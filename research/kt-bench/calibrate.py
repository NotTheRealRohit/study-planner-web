from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def result_path(results_dir: Path, dataset: str, model: str, fold: int) -> Path:
    return results_dir / f"{dataset}__{model}__fold{fold}__ece.json"


def expected_calibration_error(
    *,
    y_true: Iterable[int],
    y_score: Iterable[float],
    n_bins: int = 10,
) -> tuple[float, list[dict[str, float | int]]]:
    truth = [int(value) for value in y_true]
    scores = [float(value) for value in y_score]
    if len(truth) != len(scores):
        raise ValueError("y_true and y_score must have the same length")
    if not truth:
        raise ValueError("ECE requires at least one prediction")

    bins = []
    ece = 0.0
    for index in range(n_bins):
        lower = index / n_bins
        upper = (index + 1) / n_bins
        selected = [
            (actual, score)
            for actual, score in zip(truth, scores)
            if score >= lower and (score < upper or index == n_bins - 1)
        ]
        if selected:
            count = len(selected)
            accuracy = sum(actual for actual, _ in selected) / count
            confidence = sum(score for _, score in selected) / count
            ece += (count / len(truth)) * abs(accuracy - confidence)
        else:
            count = 0
            accuracy = 0.0
            confidence = 0.0
        bins.append(
            {
                "lower": round(lower, 6),
                "upper": round(upper, 6),
                "count": count,
                "accuracy": round(accuracy, 6),
                "confidence": round(confidence, 6),
            }
        )
    return ece, bins


def calibrate_dataset(dataset: str, results_dir: Path, models: list[str]) -> list[Path]:
    outputs = []
    for source in sorted(results_dir.glob(f"{dataset}__*__fold*__kfull.json")):
        payload = json.loads(source.read_text(encoding="utf-8"))
        model = str(payload["model"])
        if model not in models:
            continue
        ece, bins = expected_calibration_error(
            y_true=payload["y_true"],
            y_score=payload["y_score"],
        )
        out_payload = {
            "dataset": dataset,
            "model": model,
            "fold": int(payload["fold"]),
            "k": "ece",
            "ece": ece,
            "reliability_bins": bins,
            "n_predictions": int(payload["n_predictions"]),
            "_provenance": payload.get("_provenance", {}),
        }
        out_path = result_path(results_dir, dataset, model, int(payload["fold"]))
        out_path.write_text(json.dumps(out_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        outputs.append(out_path)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--models", default="dkt,akt,deep_irt,sakt,clst")
    parser.add_argument("--results-dir", type=Path, default=repo_root() / "research/results/kt")
    args = parser.parse_args()
    models = [item.strip() for item in args.models.split(",") if item.strip()]
    for path in calibrate_dataset(args.dataset, args.results_dir, models):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
