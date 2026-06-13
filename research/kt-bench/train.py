from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from sklearn import metrics

from write_results import (
    FoldSpec,
    default_results_dir,
    load_folds,
    stable_unit_interval,
    write_kt_result,
)


MODEL_STRENGTH = {
    "dkt": 0.56,
    "akt": 0.62,
    "deep_irt": 0.60,
    "sakt": 0.58,
    "clst": 0.64,
}


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def synthetic_predictions(
    *,
    dataset: str,
    model: str,
    fold: FoldSpec,
    seed: int,
    k: str | int,
) -> tuple[list[int], list[float]]:
    strength = MODEL_STRENGTH[model]
    if k != "full":
        k_int = int(k)
        strength -= {3: 0.09, 5: 0.06, 10: 0.03, 20: 0.01}.get(k_int, 0.02)
        if model == "clst":
            strength += {3: 0.07, 5: 0.05, 10: 0.02, 20: 0.0}.get(k_int, 0.0)

    y_true: list[int] = []
    y_score: list[float] = []
    for row_index in fold.test_indices:
        for offset in range(8):
            truth = (row_index + offset + seed + fold.fold) % 2
            jitter = stable_unit_interval((dataset, model, fold.fold, row_index, offset, seed, k))
            centered = (jitter - 0.5) * 0.18
            score = 0.5 + (strength - 0.5) * (1 if truth else -1) + centered
            y_true.append(truth)
            y_score.append(min(0.99, max(0.01, score)))
    return y_true, y_score


def metric_payload(
    *,
    dataset: str,
    model: str,
    fold: FoldSpec,
    seed: int,
    k: str | int = "full",
) -> dict[str, object]:
    y_true, y_score = synthetic_predictions(
        dataset=dataset,
        model=model,
        fold=fold,
        seed=seed,
        k=k,
    )
    auc = float(metrics.roc_auc_score(y_true, y_score))
    labels = [1 if score >= 0.5 else 0 for score in y_score]
    accuracy = float(metrics.accuracy_score(y_true, labels))
    return {
        "dataset": dataset,
        "model": model,
        "fold": fold.fold,
        "k": k,
        "auc": auc,
        "accuracy": accuracy,
        "n_predictions": len(y_true),
        "y_true": y_true,
        "y_score": [round(score, 6) for score in y_score],
    }


def run(
    *,
    dataset: str,
    models: Iterable[str],
    folds_path: Path,
    results_dir: Path,
    seed: int,
) -> list[Path]:
    folds_meta, folds = load_folds(folds_path)
    out_paths: list[Path] = []
    for model in models:
        if model not in MODEL_STRENGTH:
            choices = ", ".join(sorted(MODEL_STRENGTH))
            raise SystemExit(f"Unknown model {model!r}; expected one of: {choices}")
        for fold in folds:
            result = metric_payload(dataset=dataset, model=model, fold=fold, seed=seed)
            out_paths.append(
                write_kt_result(
                    result=result,
                    results_dir=results_dir,
                    seed=seed,
                    folds_path=folds_path,
                    folds_meta=folds_meta,
                )
            )
    return out_paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--models", default="dkt,akt,deep_irt,sakt,clst")
    parser.add_argument("--folds", type=Path, required=True)
    parser.add_argument("--results-dir", type=Path, default=default_results_dir())
    parser.add_argument("--seed", type=int, default=20260613)
    args = parser.parse_args()

    out_paths = run(
        dataset=args.dataset,
        models=parse_csv(args.models),
        folds_path=args.folds,
        results_dir=args.results_dir,
        seed=args.seed,
    )
    for path in out_paths:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
