from __future__ import annotations

import argparse
import json
import statistics
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from py_progress import run_cusum

from research_comparison.baselines.detection import detect_csd, detect_ewma
from research_comparison.metrics.detection import (
    SHIFT_TYPES,
    roc_points,
    score_detections,
    winner_by_shift_type,
)
from research_comparison.oracles.detection import detection_oracle_breakpoints
from research_comparison.progress_log import ProgressLogger
from research_comparison.runners.calibration import latest_dataset_dir
from research_comparison.writers.results import manifest_from_dataset, write_stamped_json


@dataclass(frozen=True)
class DetectionCandidate:
    name: str
    detector: Callable[[list[float]], list[int]]


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.05
    value = float(statistics.stdev(values))
    return value if value > 1e-6 else 0.05


def detect_cusum(
    pace_ratios: list[float],
    reference_mean: float,
    std: float,
) -> list[int]:
    return list(run_cusum(pace_ratios, reference_mean, std).breakpoints)


def detection_candidates(pace_ratios: list[float]) -> list[DetectionCandidate]:
    baseline = pace_ratios[: min(8, len(pace_ratios))]
    reference_mean = float(statistics.fmean(baseline)) if baseline else 1.0
    std = _std(baseline)
    return [
        DetectionCandidate(
            "cusum",
            lambda series: detect_cusum(series, reference_mean=reference_mean, std=std),
        ),
        DetectionCandidate(
            "ewma_control_chart",
            lambda series: detect_ewma(
                series,
                reference_mean=reference_mean,
                std=std,
                threshold=2.4,
            ),
        ),
        DetectionCandidate("csd", lambda series: detect_csd(series, window=8, threshold=0.07)),
    ]


def _active_series_with_indices(sessions: list[dict[str, Any]]) -> tuple[list[float], list[int]]:
    pace_ratios: list[float] = []
    original_indices: list[int] = []
    for index, session in enumerate(sessions):
        planned = session.get("plannedMinutes")
        active = session.get("activeMinutes")
        if session.get("source") != "active" or planned is None or active is None:
            continue
        planned_value = float(planned)
        if planned_value <= 0:
            continue
        pace_ratios.append(float(active) / planned_value)
        original_indices.append(index)
    return pace_ratios, original_indices


def _shifts_on_active_axis(
    raw_shifts: list[dict[str, Any]],
    active_original_indices: list[int],
) -> list[dict[str, Any]]:
    active_shifts: list[dict[str, Any]] = []
    for shift in raw_shifts:
        onset = int(shift["onset_index"])
        active_index = next(
            (
                active_position
                for active_position, original_index in enumerate(active_original_indices)
                if original_index >= onset
            ),
            None,
        )
        if active_index is None:
            continue
        active_shifts.append({**shift, "onset_index": active_index})
    return active_shifts


def run_detection_for_learner(
    learner: dict[str, Any],
    truth: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pace_ratios, original_indices = _active_series_with_indices(learner["sessions"])
    shifts = _shifts_on_active_axis(truth.get("regime_schedule", []), original_indices)
    if len(pace_ratios) < 3 or not shifts:
        return [], []

    rows: list[dict[str, Any]] = []
    for candidate in detection_candidates(pace_ratios):
        breakpoints = candidate.detector(pace_ratios)
        score = score_detections(breakpoints, shifts, n_observations=len(pace_ratios))
        for shift_type in SHIFT_TYPES:
            type_score = score["by_type"][shift_type]
            if type_score["n_shifts"] == 0:
                continue
            rows.append(
                {
                    "learner_id": learner["learner_id"],
                    "band": learner["band"],
                    "archetype": learner["archetype"],
                    "seed": learner["seed"],
                    "candidate": candidate.name,
                    "shift_type": shift_type,
                    "n_shifts": type_score["n_shifts"],
                    "n_detected": type_score["n_detected"],
                    "missed": type_score["missed"],
                    "mean_latency": type_score["mean_latency"],
                    "false_alarms": score["false_alarms"],
                    "false_alarm_rate": score["false_alarm_rate"],
                    "breakpoints": breakpoints,
                }
            )

    oracle_breakpoints = detection_oracle_breakpoints(shifts)
    oracle_score = score_detections(oracle_breakpoints, shifts, n_observations=len(pace_ratios))
    for shift_type in SHIFT_TYPES:
        type_score = oracle_score["by_type"][shift_type]
        if type_score["n_shifts"] == 0:
            continue
        rows.append(
            {
                "learner_id": learner["learner_id"],
                "band": learner["band"],
                "archetype": learner["archetype"],
                "seed": learner["seed"],
                "candidate": "oracle_detection",
                "shift_type": shift_type,
                "n_shifts": type_score["n_shifts"],
                "n_detected": type_score["n_detected"],
                "missed": type_score["missed"],
                "mean_latency": type_score["mean_latency"],
                "false_alarms": oracle_score["false_alarms"],
                "false_alarm_rate": oracle_score["false_alarm_rate"],
                "breakpoints": oracle_breakpoints,
            }
        )

    baseline = pace_ratios[: min(8, len(pace_ratios))]
    reference_mean = float(statistics.fmean(baseline)) if baseline else 1.0
    std = _std(baseline)
    roc = [
        {
            "learner_id": learner["learner_id"],
            "band": learner["band"],
            "archetype": learner["archetype"],
            "candidate": "ewma_control_chart",
            **point,
        }
        for point in roc_points(
            pace_ratios,
            shifts,
            detector=lambda series, threshold: detect_ewma(
                series,
                reference_mean=reference_mean,
                std=std,
                threshold=threshold,
            ),
            thresholds=[3.0, 2.4, 1.8, 1.2],
        )
    ]
    return rows, roc


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_detection_track(
    dataset_dir: str | None = None,
    out_dir: str | None = None,
    progress: ProgressLogger | None = None,
) -> Path:
    root = _repo_root()
    dataset_path = Path(dataset_dir) if dataset_dir else latest_dataset_dir()
    result_root = Path(out_dir) if out_dir else root / "research/results/detection"
    if progress:
        progress.log(0, "detection.start", f"dataset={dataset_path}")
    raw_manifest = json.loads((dataset_path / "manifest.json").read_text(encoding="utf-8"))
    manifest = manifest_from_dataset(raw_manifest)
    sidecars = {
        row["learner_id"]: row["ground_truth"]
        for row in _read_jsonl(dataset_path / "sidecars.jsonl")
    }

    rows: list[dict[str, Any]] = []
    roc: list[dict[str, Any]] = []
    learners = _read_jsonl(dataset_path / "learners.jsonl")
    total_learners = len(learners)
    if progress:
        progress.log(10, "detection.loaded", f"learners={total_learners}")
    for learner_index, learner in enumerate(learners, start=1):
        learner_rows, learner_roc = run_detection_for_learner(
            learner,
            sidecars[learner["learner_id"]],
        )
        rows.extend(learner_rows)
        roc.extend(learner_roc)
        if progress and (
            learner_index == 1
            or learner_index == total_learners
            or learner_index % max(1, total_learners // 20) == 0
        ):
            progress.log(
                10 + (learner_index / max(1, total_learners)) * 80,
                "detection.learners",
                f"processed={learner_index}/{total_learners} rows={len(rows)} roc={len(roc)}",
            )

    payload = {
        "dataset_id": raw_manifest["dataset_id"],
        "rows": rows,
        "roc": roc,
        "winner_by_shift_type": winner_by_shift_type(rows),
    }
    if progress:
        progress.log(95, "detection.write", f"rows={len(rows)} roc={len(roc)}")
    out_path = write_stamped_json(result_root / "detection_results.json", payload, manifest)
    if progress:
        progress.log(100, "detection.complete", str(out_path))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--quiet", action="store_true", help="suppress progress output on stderr")
    args = parser.parse_args()
    logger = ProgressLogger(label="research-detection", enabled=not args.quiet)
    print(run_detection_track(dataset_dir=args.dataset_dir, out_dir=args.out_dir, progress=logger))


if __name__ == "__main__":
    main()
