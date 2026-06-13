from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from research_comparison.manifest import build_manifest
from research_comparison.params import SWEEP_GRID
from research_comparison.generator.generate import generate_learner
from research_comparison.runners.detection import run_detection_for_learner
from research_comparison.runners.projection import run_projection_for_learner
from research_comparison.runners.scheduling import (
    run_scheduling_for_scenario,
    scenario_from_learner,
)
from research_comparison.writers.results import write_stamped_json


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def sweep_grid_points(grid: dict[str, list[float]] | None = None) -> list[dict[str, float]]:
    selected = grid or SWEEP_GRID
    keys = sorted(selected)
    return [
        dict(zip(keys, values, strict=True))
        for values in itertools.product(*(selected[key] for key in keys))
    ]


def ranking_stability(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stability: dict[str, dict[str, Any]] = {}
    for track in sorted({row["track"] for row in rows}):
        selected = [row for row in rows if row["track"] == track]
        flips = [row for row in selected if row["winner"] != row["default_winner"]]
        stability[track] = {
            "status": "held" if not flips else "flipped",
            "n_points": len(selected),
            "n_flips": len(flips),
            "flip_points": flips[:10],
        }
    return stability


def _truth_dict(truth: Any) -> dict[str, Any]:
    return {**asdict(truth), "regime_schedule": [asdict(shift) for shift in truth.regime_schedule]}


def _learner_dict(
    archetype: str,
    band: str,
    seed: int,
    sessions: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "learner_id": f"sweep-{archetype}-{band}-{seed}",
        "archetype": archetype,
        "band": band,
        "seed": seed,
        "sessions": sessions,
    }


def _fixture_learners(point: dict[str, float], point_index: int) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    fixtures = []
    for offset, archetype in enumerate(["marathon_runner", "fading_flame"]):
        seed = point_index * 1000 + offset + 17
        sessions, truth = generate_learner(archetype, "medium", seed, overrides=point)
        truth_row = _truth_dict(truth)
        learner = _learner_dict(archetype, "medium", seed, sessions)
        fixtures.append((learner, truth_row))
    return fixtures


def _winner_from_scores(scores: dict[str, list[float]]) -> str:
    means = {
        candidate: sum(values) / len(values)
        for candidate, values in scores.items()
        if values and not candidate.startswith("oracle")
    }
    return min(means, key=means.__getitem__) if means else "none"


def _detection_winner(fixtures: list[tuple[dict[str, Any], dict[str, Any]]]) -> str:
    scores: dict[str, list[float]] = {}
    for learner, truth in fixtures:
        rows, _roc = run_detection_for_learner(learner, truth)
        for row in rows:
            candidate = str(row["candidate"])
            if candidate.startswith("oracle"):
                continue
            score = (
                float(row["mean_latency"])
                + float(row["missed"]) * 100.0
                + float(row["false_alarm_rate"]) * 25.0
            )
            scores.setdefault(candidate, []).append(score)
    return _winner_from_scores(scores)


def _projection_winner(fixtures: list[tuple[dict[str, Any], dict[str, Any]]]) -> str:
    scores: dict[str, list[float]] = {}
    for learner, truth in fixtures:
        rows, _forecasts = run_projection_for_learner(learner, truth, t_grid=[5, 8, 13])
        for row in rows:
            candidate = str(row["candidate"])
            if candidate.startswith("oracle"):
                continue
            score = (
                float(row["mean_abs_error_days"])
                + abs(0.95 - float(row["coverage"])) * 10.0
                + float(row["mean_sharpness_days"]) * 0.01
            )
            scores.setdefault(candidate, []).append(score)
    return _winner_from_scores(scores)


def _scheduling_winner(fixtures: list[tuple[dict[str, Any], dict[str, Any]]]) -> str:
    scores: dict[str, list[float]] = {}
    for learner, truth in fixtures:
        scenario = scenario_from_learner(learner, truth)
        rows = run_scheduling_for_scenario(
            scenario.scenario_id,
            scenario.material_mix,
            scenario.input_data,
            scenario.deadline,
        )
        for row in rows:
            score = (
                abs(float(row["deadline_drift_days"]))
                + float(row["capacity_violation_rate"]) * 25.0
                + (1.0 - float(row["prereq_order_correctness"])) * 25.0
            )
            scores.setdefault(str(row["candidate"]), []).append(score)
    return _winner_from_scores(scores)


def _default_winners() -> dict[str, str]:
    fixtures = _fixture_learners(
        {
            "ar1_phi": 0.30,
            "drift_total": 0.20,
            "manual_fraction": 0.15,
            "sigma_log": 0.18,
            "step_mag": 0.15,
        },
        point_index=0,
    )
    return {
        "detection": _detection_winner(fixtures),
        "projection": _projection_winner(fixtures),
        "scheduling": _scheduling_winner(fixtures),
    }


def run_sweep(out_dir: str | None = None, grid: dict[str, list[float]] | None = None) -> Path:
    root = _repo_root()
    result_root = Path(out_dir) if out_dir else root / "research/results/sweep"
    points = sweep_grid_points(grid)
    default_winners = _default_winners()

    rows: list[dict[str, Any]] = []
    for point_index, point in enumerate(points):
        fixtures = _fixture_learners(point, point_index)
        winners = {
            "detection": _detection_winner(fixtures),
            "projection": _projection_winner(fixtures),
            "scheduling": _scheduling_winner(fixtures),
        }
        for track, winner in winners.items():
            default_winner = default_winners[track]
            rows.append(
                {
                    "point_index": point_index,
                    "track": track,
                    "params": point,
                    "default_winner": default_winner,
                    "winner": winner,
                    "ranking_status": "held" if winner == default_winner else "flipped",
                }
            )

    manifest = build_manifest(seed=0, archetype_mix={"sweep": 2}, n_learners=len(points) * 2)
    payload = {
        "grid": grid or SWEEP_GRID,
        "rows": rows,
        "stability": ranking_stability(rows),
    }
    return write_stamped_json(result_root / "sweep_results.json", payload, manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    print(run_sweep(out_dir=args.out_dir))


if __name__ == "__main__":
    main()
