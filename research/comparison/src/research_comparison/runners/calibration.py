from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from research_comparison.baselines.calibration import (
    CalibrationCandidate,
    calibration_candidates,
)
from research_comparison.metrics.aggregate import cell_summary, winner_per_band
from research_comparison.metrics.coverage import credible_interval_coverage
from research_comparison.metrics.paired import paired_difference
from research_comparison.metrics.prequential import prequential_absolute_errors
from research_comparison.metrics.recovery import recovery_mae, recovery_rmse
from research_comparison.oracles.calibration import calibration_oracle_estimate
from research_comparison.progress_log import ProgressLogger
from research_comparison.writers.results import manifest_from_dataset, write_stamped_json


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def write_stub() -> Path:
    from research_comparison.manifest import build_manifest, stamp

    manifest = build_manifest(seed=0, archetype_mix={"stub": 1}, n_learners=1)
    output = stamp({"status": "stub", "stage": "compare"}, manifest)
    out_path = _repo_root() / "research/results/compare_stub.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def prequential_calibration(
    sessions: list[dict],
    candidate: CalibrationCandidate,
    t_grid: list[int],
) -> list[tuple[int, float]]:
    """Return list of (t, estimate) where estimate is the global pace multiplier at history 1..t."""
    out = []
    for t in t_grid:
        hist = sessions[:t]
        out.append((t, candidate.fit_global(hist)))
    return out


def default_t_grid(n_sessions: int) -> list[int]:
    base = [3, 5, 8, 13, 21, 34, 55, 89, 144, n_sessions]
    return sorted({value for value in base if 1 <= value <= n_sessions})


def latest_dataset_dir(root: Path | None = None) -> Path:
    datasets_root = root or _repo_root() / "research/datasets"
    candidates = [path for path in datasets_root.iterdir() if (path / "learners.jsonl").exists()]
    if not candidates:
        raise FileNotFoundError("No generated dataset found under research/datasets")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _active_sessions_with_targets(
    sessions: list[dict[str, Any]],
    r_star: list[float],
) -> tuple[list[dict[str, Any]], list[float]]:
    active_sessions: list[dict[str, Any]] = []
    active_targets: list[float] = []
    for session, target in zip(sessions, r_star, strict=True):
        if session["source"] == "active":
            active_sessions.append(session)
            active_targets.append(float(target))
    return active_sessions, active_targets


def _mean(values: list[float]) -> float:
    return float(sum(values) / len(values)) if values else math.nan


def _paired_by_candidate(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float]]]:
    by_band_seed_candidate: dict[tuple[str, int, str], list[float]] = {}
    for row in rows:
        key = (row["band"], int(row["seed"]), row["candidate"])
        by_band_seed_candidate.setdefault(key, []).append(float(row["recovery_mae"]))

    bands = sorted({row["band"] for row in rows})
    candidates = sorted(
        {row["candidate"] for row in rows if row["candidate"] != "hierarchical_bayes"}
    )
    paired: dict[str, dict[str, dict[str, float]]] = {}
    for band in bands:
        paired[band] = {}
        seeds = sorted({int(row["seed"]) for row in rows if row["band"] == band})
        incumbent = [
            _mean(by_band_seed_candidate[(band, seed, "hierarchical_bayes")])
            for seed in seeds
            if (band, seed, "hierarchical_bayes") in by_band_seed_candidate
        ]
        for candidate in candidates:
            challenger = [
                _mean(by_band_seed_candidate[(band, seed, candidate)])
                for seed in seeds
                if (band, seed, candidate) in by_band_seed_candidate
            ]
            if len(challenger) == len(incumbent):
                paired[band][candidate] = paired_difference(challenger, incumbent)
    return paired


def run_calibration_track(
    dataset_dir: str | None = None,
    out_dir: str | None = None,
    progress: ProgressLogger | None = None,
) -> Path:
    root = _repo_root()
    dataset_path = Path(dataset_dir) if dataset_dir else latest_dataset_dir()
    result_root = Path(out_dir) if out_dir else root / "research/results/calibration"
    if progress:
        progress.log(0, "calibration.start", f"dataset={dataset_path}")
    raw_manifest = json.loads((dataset_path / "manifest.json").read_text(encoding="utf-8"))
    manifest = manifest_from_dataset(raw_manifest)
    learners = _read_jsonl(dataset_path / "learners.jsonl")
    sidecars = {
        row["learner_id"]: row["ground_truth"]
        for row in _read_jsonl(dataset_path / "sidecars.jsonl")
    }

    rows: list[dict[str, Any]] = []
    convergence: list[dict[str, Any]] = []
    candidates = calibration_candidates()
    total_learners = len(learners)
    if progress:
        progress.log(10, "calibration.loaded", f"learners={total_learners} candidates={len(candidates) + 1}")
    for learner_index, learner in enumerate(learners, start=1):
        truth = sidecars[learner["learner_id"]]
        active_sessions, active_targets = _active_sessions_with_targets(
            learner["sessions"], truth["r_star"]
        )
        if len(active_sessions) < 3:
            continue
        t_grid = default_t_grid(len(active_sessions))
        oracle_estimate = calibration_oracle_estimate(truth)
        rows.append(
            {
                "learner_id": learner["learner_id"],
                "band": learner["band"],
                "archetype": learner["archetype"],
                "seed": learner["seed"],
                "candidate": "oracle_calibration",
                "recovery_mae": recovery_mae([oracle_estimate], truth["m_global"]),
                "recovery_rmse": recovery_rmse([oracle_estimate], truth["m_global"]),
                "prequential_mae": 0.0,
                "coverage": 1.0,
                "n_active": len(active_sessions),
            }
        )
        convergence.extend(
            {
                "band": learner["band"],
                "archetype": learner["archetype"],
                "seed": learner["seed"],
                "candidate": "oracle_calibration",
                "t": t,
                "recovery_error": 0.0,
            }
            for t in t_grid
        )
        for candidate in candidates:
            estimates = prequential_calibration(active_sessions, candidate, t_grid)
            estimate_values = [estimate for _t, estimate in estimates]
            intervals = [candidate.fit_interval(active_sessions[:t]) for t in t_grid]
            prequential_errors = prequential_absolute_errors(
                active_sessions, candidate, active_targets, t_grid
            )
            row = {
                "learner_id": learner["learner_id"],
                "band": learner["band"],
                "archetype": learner["archetype"],
                "seed": learner["seed"],
                "candidate": candidate.name,
                "recovery_mae": recovery_mae([estimate_values[-1]], truth["m_global"]),
                "recovery_rmse": recovery_rmse([estimate_values[-1]], truth["m_global"]),
                "prequential_mae": _mean(prequential_errors),
                "coverage": credible_interval_coverage(intervals, truth["m_global"]),
                "n_active": len(active_sessions),
            }
            rows.append(row)
            convergence.extend(
                {
                    "band": learner["band"],
                    "archetype": learner["archetype"],
                    "seed": learner["seed"],
                    "candidate": candidate.name,
                    "t": t,
                    "recovery_error": abs(estimate - truth["m_global"]),
                }
                for t, estimate in estimates
            )
        if progress and (
            learner_index == 1
            or learner_index == total_learners
            or learner_index % max(1, total_learners // 20) == 0
        ):
            progress.log(
                10 + (learner_index / max(1, total_learners)) * 80,
                "calibration.learners",
                f"processed={learner_index}/{total_learners} rows={len(rows)}",
            )

    payload = {
        "dataset_id": raw_manifest["dataset_id"],
        "rows": rows,
        "convergence": convergence,
        "cell_summary": cell_summary(rows),
        "winner_per_band": winner_per_band(rows),
        "paired_vs_incumbent": _paired_by_candidate(rows),
    }
    if progress:
        progress.log(95, "calibration.write", f"rows={len(rows)} convergence={len(convergence)}")
    out_path = write_stamped_json(result_root / "calibration_results.json", payload, manifest)
    if progress:
        progress.log(100, "calibration.complete", str(out_path))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stub", action="store_true")
    parser.add_argument("--dataset-dir", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--quiet", action="store_true", help="suppress progress output on stderr")
    args = parser.parse_args()
    logger = ProgressLogger(label="research-calibration", enabled=not args.quiet)
    if args.stub:
        logger.log(0, "calibration.stub_start")
        path = write_stub()
        logger.log(100, "calibration.stub_complete", str(path))
        print(path)
        return
    print(run_calibration_track(dataset_dir=args.dataset_dir, out_dir=args.out_dir, progress=logger))


if __name__ == "__main__":
    main()
