from __future__ import annotations

import json
from pathlib import Path


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
