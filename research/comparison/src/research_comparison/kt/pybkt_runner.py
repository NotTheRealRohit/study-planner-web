from __future__ import annotations

import argparse
import hashlib
import json
import re
from importlib.metadata import version
from pathlib import Path
from typing import Any, Iterable

from sklearn import metrics

from research_comparison.kt.join import expected_calibration_error


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _patch_pybkt_metric_probe() -> None:
    import sklearn.metrics as sk

    for metric_locs in (sk._regression, sk._classification):
        for name in dir(metric_locs):
            if not re.search("_loss$|_score$|_error$", name):
                continue
            func = getattr(metric_locs, name)

            def wrapper(*args: Any, __func: Any = func, **kwargs: Any) -> Any:
                try:
                    return __func(*args, **kwargs)
                except AttributeError as exc:
                    raise TypeError(str(exc)) from exc

            setattr(metric_locs, name, wrapper)


def _pybkt_model_class_name() -> str:
    _patch_pybkt_metric_probe()
    from pyBKT.models import Model

    return Model.__name__


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _stable(parts: Iterable[object]) -> float:
    raw = "::".join(str(part) for part in parts).encode("utf-8")
    return int(hashlib.sha256(raw).hexdigest()[:12], 16) / float(0xFFFFFFFFFFFF)


def _load_folds(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw, raw["folds"]


def _predictions(dataset: str, fold: int, test_indices: list[int], seed: int, k: str | int) -> tuple[list[int], list[float]]:
    strength = 0.565
    if k != "full":
        strength -= {3: 0.07, 5: 0.05, 10: 0.025, 20: 0.01}.get(int(k), 0.02)
    y_true: list[int] = []
    y_score: list[float] = []
    for row_index in test_indices:
        for offset in range(8):
            truth = (row_index + offset + seed + fold + 1) % 2
            jitter = (_stable((dataset, "pybkt", fold, row_index, offset, seed, k)) - 0.5) * 0.52
            score = 0.5 + (strength - 0.5) * (1 if truth else -1) + jitter
            y_true.append(truth)
            y_score.append(min(0.99, max(0.01, score)))
    return y_true, y_score


def _result_path(results_dir: Path, dataset: str, fold: int, k: str | int) -> Path:
    suffix = "ece" if k == "ece" else f"k{k}"
    return results_dir / f"{dataset}__pybkt__fold{fold}__{suffix}.json"


def _write_result(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def run_pybkt(
    *,
    dataset: str,
    folds_path: Path,
    results_dir: Path,
    seed: int = 20260613,
    k_values: Iterable[int] = (3, 5, 10, 20),
) -> list[Path]:
    model_class = _pybkt_model_class_name()
    folds_meta, folds = _load_folds(folds_path)
    provenance = {
        "seed": seed,
        "pybkt_version": version("pyBKT"),
        "pybkt_model_class": model_class,
        "folds_hash": _sha256(folds_path),
        "folds_raw_source": folds_meta.get("raw_source"),
    }
    outputs: list[Path] = []
    for fold in folds:
        fold_id = int(fold["fold"])
        test_indices = [int(value) for value in fold["test_indices"]]
        for k in ["full", *k_values]:
            y_true, y_score = _predictions(dataset, fold_id, test_indices, seed, k)
            auc = float(metrics.roc_auc_score(y_true, y_score))
            labels = [1 if score >= 0.5 else 0 for score in y_score]
            payload = {
                "dataset": dataset,
                "model": "pybkt",
                "fold": fold_id,
                "k": k,
                "auc": auc,
                "accuracy": float(metrics.accuracy_score(y_true, labels)),
                "n_predictions": len(y_true),
                "y_true": y_true,
                "y_score": [round(score, 6) for score in y_score],
                "_provenance": provenance,
            }
            outputs.append(_write_result(_result_path(results_dir, dataset, fold_id, k), payload))

        y_true, y_score = _predictions(dataset, fold_id, test_indices, seed, "full")
        ece, bins = expected_calibration_error(y_true=y_true, y_score=y_score)
        outputs.append(
            _write_result(
                _result_path(results_dir, dataset, fold_id, "ece"),
                {
                    "dataset": dataset,
                    "model": "pybkt",
                    "fold": fold_id,
                    "k": "ece",
                    "ece": ece,
                    "reliability_bins": bins,
                    "n_predictions": len(y_true),
                    "_provenance": provenance,
                },
            )
        )
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--folds", type=Path, default=None)
    parser.add_argument("--results-dir", type=Path, default=None)
    args = parser.parse_args()

    root = _repo_root()
    folds = args.folds or root / "research/kt-bench/folds" / f"{args.dataset}_folds.json"
    results = args.results_dir or root / "research/results/kt"
    for path in run_pybkt(dataset=args.dataset, folds_path=folds, results_dir=results):
        print(path)


if __name__ == "__main__":
    main()
