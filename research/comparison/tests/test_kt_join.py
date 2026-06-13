from __future__ import annotations

import json
import importlib
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
FOLDS_DIR = REPO_ROOT / "research" / "kt-bench" / "folds"


def test_folds_schema() -> None:
    for dataset in ("nips2020", "poj"):
        path = FOLDS_DIR / f"{dataset}_folds.json"
        raw = json.loads(path.read_text(encoding="utf-8"))

        assert raw["dataset"] == dataset
        assert raw["source"] == "pykt.preprocess.split_datasets.KFold_split"
        assert len(raw["folds"]) == 5

        for expected_fold, fold in enumerate(raw["folds"]):
            train_indices = set(fold["train_indices"])
            test_indices = set(fold["test_indices"])

            assert fold["fold"] == expected_fold
            assert train_indices
            assert test_indices
            assert train_indices.isdisjoint(test_indices)


def _write_result(
    results_dir: Path,
    *,
    dataset: str = "nips2020",
    model: str = "dkt",
    fold: int = 0,
    k: str | int = "full",
    auc: float = 0.75,
    ece: float | None = None,
) -> None:
    suffix = "ece" if k == "ece" else f"k{k}"
    path = results_dir / f"{dataset}__{model}__fold{fold}__{suffix}.json"
    payload = {
        "dataset": dataset,
        "model": model,
        "fold": fold,
        "k": k,
        "auc": auc,
        "y_true": [1, 0, 1, 0],
        "y_score": [0.9, 0.8, 0.4, 0.1],
        "_provenance": {"seed": 1, "folds_hash": "fixture"},
    }
    if ece is not None:
        payload["ece"] = ece
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_join_reports_missing_cells_as_gaps(tmp_path: Path) -> None:
    from research_comparison.kt.join import join_kt_results

    results_dir = tmp_path / "kt"
    _write_result(results_dir, dataset="nips2020", model="dkt", fold=0, k="full", auc=0.75)
    _write_result(results_dir, dataset="nips2020", model="dkt", fold=0, k=3, auc=0.70)
    _write_result(results_dir, dataset="nips2020", model="dkt", fold=0, k="ece", ece=0.2)

    summary = join_kt_results(
        results_dir,
        expected_datasets=["nips2020"],
        expected_models=["dkt", "akt"],
        expected_folds=[0],
        expected_k_values=["full", 3],
    )

    assert summary["full_seq_auc"]["nips2020"]["dkt"] == pytest.approx(0.75)
    assert summary["coldstart_auc"][0]["auc"] == pytest.approx(0.70)
    assert summary["ece"]["nips2020"]["dkt"] == pytest.approx(0.2)
    assert {
        "dataset": "nips2020",
        "model": "akt",
        "fold": 0,
        "k": "full",
    } in summary["gaps"]


def test_join_boundary_does_not_import_torch_or_pykt() -> None:
    sys.modules.pop("research_comparison.kt.join", None)
    sys.modules.pop("torch", None)
    sys.modules.pop("pykt", None)

    importlib.import_module("research_comparison.kt.join")

    assert "torch" not in sys.modules
    assert "pykt" not in sys.modules


def test_expected_calibration_error_matches_hand_computed_value() -> None:
    from research_comparison.kt.join import expected_calibration_error

    ece, bins = expected_calibration_error(
        y_true=[1, 0, 1, 0],
        y_score=[0.9, 0.8, 0.4, 0.1],
        n_bins=2,
    )

    assert ece == pytest.approx(0.3)
    assert bins == [
        {"lower": 0.0, "upper": 0.5, "count": 2, "accuracy": 0.5, "confidence": 0.25},
        {"lower": 0.5, "upper": 1.0, "count": 2, "accuracy": 0.5, "confidence": 0.85},
    ]
