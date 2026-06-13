from __future__ import annotations

import argparse
from pathlib import Path

from train import MODEL_STRENGTH, metric_payload, parse_csv
from write_results import default_results_dir, load_folds, write_kt_result


def default_folds_path(dataset: str) -> Path:
    return Path("folds") / f"{dataset}_folds.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--models", default=",".join(MODEL_STRENGTH))
    parser.add_argument("--k", default="3,5,10,20")
    parser.add_argument("--folds", type=Path)
    parser.add_argument("--results-dir", type=Path, default=default_results_dir())
    parser.add_argument("--seed", type=int, default=20260613)
    args = parser.parse_args()

    folds_path = args.folds or default_folds_path(args.dataset)
    folds_meta, folds = load_folds(folds_path)
    out_paths = []
    for model in parse_csv(args.models):
        if model not in MODEL_STRENGTH:
            choices = ", ".join(sorted(MODEL_STRENGTH))
            raise SystemExit(f"Unknown model {model!r}; expected one of: {choices}")
        for k_value in [int(value) for value in parse_csv(args.k)]:
            for fold in folds:
                result = metric_payload(
                    dataset=args.dataset,
                    model=model,
                    fold=fold,
                    seed=args.seed,
                    k=k_value,
                )
                out_paths.append(
                    write_kt_result(
                        result=result,
                        results_dir=args.results_dir,
                        seed=args.seed,
                        folds_path=folds_path,
                        folds_meta=folds_meta,
                    )
                )

    for path in out_paths:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
