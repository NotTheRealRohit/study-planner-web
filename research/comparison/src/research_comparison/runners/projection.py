from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from research_comparison.baselines.projection import (
    forecast_gp_finish,
    forecast_kalman_finish,
    forecast_linear_finish,
)
from research_comparison.metrics.projection import projection_metrics, winner_by_band
from research_comparison.runners.calibration import latest_dataset_dir
from research_comparison.writers.results import manifest_from_dataset, write_stamped_json


@dataclass(frozen=True)
class ProjectionCandidate:
    name: str
    forecast: Callable[[list[dict[str, Any]], float, str, str], dict[str, Any]]


def projection_candidates() -> list[ProjectionCandidate]:
    return [
        ProjectionCandidate(
            "gp_ard",
            lambda sessions, total, start, end: forecast_gp_finish(
                sessions,
                total,
                start_date=start,
                horizon_end_date=end,
            ),
        ),
        ProjectionCandidate(
            "linear",
            lambda sessions, total, _start, _end: forecast_linear_finish(sessions, total),
        ),
        ProjectionCandidate(
            "kalman",
            lambda sessions, total, _start, _end: forecast_kalman_finish(sessions, total),
        ),
    ]


def default_t_grid(n_sessions: int) -> list[int]:
    base = [5, 8, 13, 21, 34, 55, 89, n_sessions]
    return sorted({value for value in base if 2 <= value <= n_sessions})


def _session_minutes_noise_free(session: dict[str, Any], latent_ratio: float) -> float:
    if session.get("plannedMinutes") is not None:
        return float(session["plannedMinutes"]) * latent_ratio
    return float(session.get("duration") or 0.0)


def _target_minutes_from_truth(
    sessions: list[dict[str, Any]],
    truth: dict[str, Any],
) -> float:
    true_finish = date.fromisoformat(str(truth["true_finish_date"]))
    cumulative = 0.0
    for session, latent_ratio in zip(sessions, truth["r_star"], strict=False):
        cumulative += _session_minutes_noise_free(session, float(latent_ratio))
        if date.fromisoformat(str(session["date"])) >= true_finish:
            return cumulative
    return cumulative


def _horizon_end_date(sessions: list[dict[str, Any]], true_finish_date: str) -> str:
    last = date.fromisoformat(str(sessions[-1]["date"]))
    true_date = date.fromisoformat(true_finish_date)
    return (max(last, true_date) + timedelta(days=30)).isoformat()


def run_projection_for_learner(
    learner: dict[str, Any],
    truth: dict[str, Any],
    t_grid: list[int] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sessions = [session for session in learner["sessions"] if float(session.get("duration") or 0) > 0]
    if len(sessions) < 2:
        return [], []
    total_minutes = _target_minutes_from_truth(sessions, truth)
    true_finish_date = str(truth["true_finish_date"])
    grid = t_grid or default_t_grid(len(sessions))
    start_date = str(sessions[0]["date"])
    horizon_end = _horizon_end_date(sessions, true_finish_date)

    rows: list[dict[str, Any]] = []
    forecast_rows: list[dict[str, Any]] = []
    for candidate in projection_candidates():
        forecasts: list[dict[str, Any]] = []
        for t in grid:
            forecast = candidate.forecast(sessions[:t], total_minutes, start_date, horizon_end)
            forecasts.append(forecast)
            forecast_rows.append(
                {
                    "learner_id": learner["learner_id"],
                    "band": learner["band"],
                    "archetype": learner["archetype"],
                    "seed": learner["seed"],
                    "candidate": candidate.name,
                    "t": t,
                    **forecast,
                }
            )
        metrics = projection_metrics(forecasts, true_finish_date=true_finish_date)
        rows.append(
            {
                "learner_id": learner["learner_id"],
                "band": learner["band"],
                "archetype": learner["archetype"],
                "seed": learner["seed"],
                "candidate": candidate.name,
                "coverage": metrics["coverage"],
                "mean_sharpness_days": metrics["mean_sharpness_days"],
                "mean_abs_error_days": metrics["mean_abs_error_days"],
                "n_forecasts": len(forecasts),
            }
        )
    return rows, forecast_rows


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_projection_track(dataset_dir: str | None = None, out_dir: str | None = None) -> Path:
    root = _repo_root()
    dataset_path = Path(dataset_dir) if dataset_dir else latest_dataset_dir()
    result_root = Path(out_dir) if out_dir else root / "research/results/projection"
    raw_manifest = json.loads((dataset_path / "manifest.json").read_text(encoding="utf-8"))
    manifest = manifest_from_dataset(raw_manifest)
    sidecars = {
        row["learner_id"]: row["ground_truth"]
        for row in _read_jsonl(dataset_path / "sidecars.jsonl")
    }

    rows: list[dict[str, Any]] = []
    forecasts: list[dict[str, Any]] = []
    for learner in _read_jsonl(dataset_path / "learners.jsonl"):
        learner_rows, learner_forecasts = run_projection_for_learner(
            learner,
            sidecars[learner["learner_id"]],
        )
        rows.extend(learner_rows)
        forecasts.extend(learner_forecasts)

    payload = {
        "dataset_id": raw_manifest["dataset_id"],
        "rows": rows,
        "forecasts": forecasts,
        "winner_by_band": winner_by_band(rows),
    }
    return write_stamped_json(result_root / "projection_results.json", payload, manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default=None)
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    print(run_projection_track(dataset_dir=args.dataset_dir, out_dir=args.out_dir))


if __name__ == "__main__":
    main()
