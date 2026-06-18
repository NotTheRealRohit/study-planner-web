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
from research_comparison.metrics.prequential import (
    context_prediction_absolute_errors,
    prequential_absolute_errors,
)
from research_comparison.metrics.recovery import recovery_mae, recovery_rmse
from research_comparison.oracles.calibration import calibration_oracle_estimate
from research_comparison.progress_log import ProgressLogger
from research_comparison.runners.rigour import (
    DEFAULT_SEED_COUNT,
    annotate_archetype_split,
    attach_rigour_provenance,
    mc_correction_block,
    paired_by_group,
    paired_metric_result,
    read_jsonl,
    reporting_rows,
    resolve_dataset_dir,
)
from research_comparison.runners.rigour import (
    latest_dataset_dir as _latest_dataset_dir,
)
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
    repo_root = _repo_root()
    if root is None:
        return _latest_dataset_dir(repo_root)
    candidates = [path for path in root.iterdir() if (path / "learners.jsonl").exists()]
    if not candidates:
        raise FileNotFoundError("No generated dataset found under research/datasets")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path)


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


def _context_of(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "materialRole": session.get("materialRole") or "foundation",
        "startedAt": session.get("startedAt") or session.get("date"),
    }


def _paired_metric_result(
    challenger: list[float],
    baseline: list[float],
) -> dict[str, float]:
    return paired_metric_result(challenger, baseline)


def _prefixed_metric_result(
    metric: str,
    result: dict[str, float],
) -> dict[str, float]:
    return {f"{metric}_{key}": value for key, value in result.items()}


def _paired_by_candidate(
    rows: list[dict[str, Any]],
    baseline_candidate: str = "hierarchical_bayes",
) -> dict[str, dict[str, dict[str, float]]]:
    metrics = ["recovery_mae", "context_pred_mae"]
    by_band_seed_candidate_metric: dict[tuple[str, int, str, str], list[float]] = {}
    for row in rows:
        for metric in metrics:
            if metric not in row:
                continue
            key = (row["band"], int(row["seed"]), row["candidate"], metric)
            by_band_seed_candidate_metric.setdefault(key, []).append(float(row[metric]))

    bands = sorted({row["band"] for row in rows})
    candidates = sorted(
        {row["candidate"] for row in rows if row["candidate"] != baseline_candidate}
    )
    paired: dict[str, dict[str, dict[str, float]]] = {}
    for band in bands:
        paired[band] = {}
        seeds = sorted({int(row["seed"]) for row in rows if row["band"] == band})
        for candidate in candidates:
            result: dict[str, float] = {}
            for metric in metrics:
                baseline = [
                    _mean(
                        by_band_seed_candidate_metric[
                            (band, seed, baseline_candidate, metric)
                        ]
                    )
                    for seed in seeds
                    if (band, seed, baseline_candidate, metric)
                    in by_band_seed_candidate_metric
                ]
                challenger = [
                    _mean(by_band_seed_candidate_metric[(band, seed, candidate, metric)])
                    for seed in seeds
                    if (band, seed, candidate, metric) in by_band_seed_candidate_metric
                ]
                if len(challenger) != len(baseline):
                    continue
                metric_result = _paired_metric_result(challenger, baseline)
                if metric == "recovery_mae":
                    result.update(metric_result)
                result.update(_prefixed_metric_result(metric, metric_result))
            if result:
                paired[band][candidate] = result
    return paired


def run_calibration_track(
    dataset_dir: str | None = None,
    out_dir: str | None = None,
    seed_count: int | None = DEFAULT_SEED_COUNT,
    progress: ProgressLogger | None = None,
) -> Path:
    root = _repo_root()
    dataset_path = resolve_dataset_dir(root, dataset_dir, seed_count, progress=progress)
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
        progress.log(
            10,
            "calibration.loaded",
            f"learners={total_learners} candidates={len(candidates) + 1}",
        )
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
                "context_pred_mae": 0.0,
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
            next_contexts = [_context_of(session) for session in active_sessions]
            prequential_errors = prequential_absolute_errors(
                active_sessions, candidate, active_targets, t_grid
            )
            context_prediction_errors = context_prediction_absolute_errors(
                active_sessions,
                candidate,
                active_targets,
                t_grid,
                next_contexts=next_contexts,
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
                "context_pred_mae": _mean(context_prediction_errors),
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

    dataset_archetypes = {str(learner["archetype"]) for learner in learners}
    annotate_archetype_split(rows, archetypes=dataset_archetypes)
    scored_rows, scored_split = reporting_rows(rows)
    recovery_cells = paired_by_group(
        scored_rows,
        metric="recovery_mae",
        baseline_candidate="hierarchical_bayes",
        group_fields=["band", "archetype"],
    )
    context_cells = paired_by_group(
        scored_rows,
        metric="context_pred_mae",
        baseline_candidate="hierarchical_bayes",
        group_fields=["band", "archetype"],
    )
    manifest = attach_rigour_provenance(
        manifest,
        raw_manifest,
        rows,
        archetypes=dataset_archetypes,
    )
    payload = {
        "dataset_id": raw_manifest["dataset_id"],
        "scored_split": scored_split,
        "rows": rows,
        "convergence": convergence,
        "cell_summary": cell_summary(scored_rows),
        "winner_per_band": winner_per_band(scored_rows),
        "context_pred_cell_summary": cell_summary(scored_rows, metric="context_pred_mae"),
        "context_pred_winner_per_band": winner_per_band(scored_rows, metric="context_pred_mae"),
        "paired_vs_incumbent": _paired_by_candidate(scored_rows),
        "paired_vs_pooled_bayes": _paired_by_candidate(
            scored_rows,
            baseline_candidate="pooled_bayes",
        ),
        "paired_by_cell": {
            "recovery_mae": recovery_cells,
            "context_pred_mae": context_cells,
        },
        "mc_correction": {
            "recovery_mae": mc_correction_block(
                recovery_cells,
                metric="recovery_mae",
                baseline_candidate="hierarchical_bayes",
            ),
            "context_pred_mae": mc_correction_block(
                context_cells,
                metric="context_pred_mae",
                baseline_candidate="hierarchical_bayes",
            ),
        },
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
    parser.add_argument("--seeds", type=int, default=DEFAULT_SEED_COUNT)
    parser.add_argument("--quiet", action="store_true", help="suppress progress output on stderr")
    args = parser.parse_args()
    logger = ProgressLogger(label="research-calibration", enabled=not args.quiet)
    if args.stub:
        logger.log(0, "calibration.stub_start")
        path = write_stub()
        logger.log(100, "calibration.stub_complete", str(path))
        print(path)
        return
    print(
        run_calibration_track(
            dataset_dir=args.dataset_dir,
            out_dir=args.out_dir,
            seed_count=args.seeds,
            progress=logger,
        )
    )


if __name__ == "__main__":
    main()
