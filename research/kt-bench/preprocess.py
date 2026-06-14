from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Iterable

import pandas as pd
from pykt.preprocess.data_proprocess import process_raw_data
from pykt.preprocess.split_datasets import main as split_concept


@dataclass(frozen=True)
class DatasetSpec:
    public_name: str
    pykt_name: str
    raw_file: str


DATASETS = {
    "nips2020": DatasetSpec(
        public_name="nips2020",
        pykt_name="nips_task34",
        raw_file="train_task_3_4.csv",
    ),
    "poj": DatasetSpec(
        public_name="poj",
        pykt_name="poj",
        raw_file="poj_log.csv",
    ),
    "accoding": DatasetSpec(
        public_name="accoding",
        pykt_name="poj",
        raw_file="poj_log.csv",
    ),
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_datasets(raw: str) -> list[DatasetSpec]:
    specs = []
    for name in [item.strip() for item in raw.split(",") if item.strip()]:
        if name not in DATASETS:
            choices = ", ".join(sorted(DATASETS))
            raise SystemExit(f"Unknown dataset {name!r}; expected one of: {choices}")
        specs.append(DATASETS[name])
    return specs


def raw_dataset_path(raw_root: Path, spec: DatasetSpec) -> Path:
    candidates = [
        raw_root / spec.pykt_name / spec.raw_file,
        raw_root / spec.public_name / spec.raw_file,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def write_smoke_sequences(path: Path, spec: DatasetSpec) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: list[list[str]] = []
    for learner in range(12):
        seq_len = 6 + (learner % 4)
        uid = f"{spec.public_name}_smoke_{learner:02d}"
        questions = [f"q{(learner + offset) % 9}" for offset in range(seq_len)]
        concepts = [f"c{(learner + offset) % 5}" for offset in range(seq_len)]
        responses = [str((learner + offset + (offset // 3)) % 2) for offset in range(seq_len)]
        timestamps = [str(1_700_000_000 + learner * 1_000 + offset * 60) for offset in range(seq_len)]
        usetimes = [str(30 + (offset % 5) * 5) for offset in range(seq_len)]

        if spec.public_name == "poj":
            questions_line = "NA"
        else:
            questions_line = ",".join(questions)

        rows.extend(
            [
                f"{uid},{seq_len}",
                questions_line,
                ",".join(concepts),
                ",".join(responses),
                ",".join(timestamps),
                ",".join(usetimes),
            ]
        )
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def ensure_config(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")


def ensure_dataset_config(path: Path, dataset_name: str) -> None:
    ensure_config(path)
    raw = path.read_text(encoding="utf-8").strip()
    data = json.loads(raw) if raw else {}
    if dataset_name not in data:
        data[dataset_name] = {}
        path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def preprocess_raw(spec: DatasetSpec, raw_root: Path, config_path: Path) -> tuple[Path, Path, str]:
    raw_path = raw_dataset_path(raw_root, spec)
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Missing raw {spec.public_name} file at {raw_path}. "
            "Use --mode smoke for a local smoke export, or place the public dataset under --raw-root."
        )

    ensure_dataset_config(config_path, spec.pykt_name)
    dname, data_txt = process_raw_data(spec.pykt_name, {spec.pykt_name: str(raw_path)})
    if spec.pykt_name == "poj":
        normalize_poj_uid_lines(Path(data_txt))
    split_concept(dname, data_txt, spec.pykt_name, str(config_path), 3, 200, 5)
    return Path(dname), Path(data_txt), "public_raw"


def normalize_poj_uid_lines(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    normalized: list[str] = []
    for index, line in enumerate(lines):
        if index % 6 == 0 and line.startswith("("):
            prefix, _, rest = line.partition("),")
            uid = prefix.strip("()").rstrip(",")
            normalized.append(f"{uid},{rest}")
        else:
            normalized.append(line)
    path.write_text("\n".join(normalized) + "\n", encoding="utf-8")


def preprocess_smoke(spec: DatasetSpec, work_dir: Path, config_path: Path) -> tuple[Path, Path, str]:
    dataset_dir = work_dir / spec.pykt_name
    data_txt = dataset_dir / "data.txt"
    write_smoke_sequences(data_txt, spec)
    ensure_dataset_config(config_path, spec.pykt_name)
    split_concept(str(dataset_dir), str(data_txt), spec.pykt_name, str(config_path), 3, 200, 5)
    return dataset_dir, data_txt, "smoke_fixture"


def export_folds(
    *,
    spec: DatasetSpec,
    dataset_dir: Path,
    data_txt: Path,
    raw_source: str,
    folds_dir: Path,
) -> Path:
    train_valid_path = dataset_dir / "train_valid.csv"
    frame = pd.read_csv(train_valid_path)
    if "fold" not in frame.columns:
        raise ValueError(f"{train_valid_path} has no fold column")

    folds = []
    all_indices = set(range(len(frame)))
    for fold in range(5):
        test_indices = set(frame.index[frame["fold"] == fold].astype(int).tolist())
        train_indices = all_indices - test_indices
        folds.append(
            {
                "fold": fold,
                "train_indices": sorted(train_indices),
                "test_indices": sorted(test_indices),
            }
        )

    payload = {
        "dataset": spec.public_name,
        "pykt_dataset": spec.pykt_name,
        "source": "pykt.preprocess.split_datasets.KFold_split",
        "raw_source": raw_source,
        "kfold": 5,
        "python_version": platform.python_version(),
        "pykt_version": version("pykt-toolkit"),
        "train_valid_rows": len(frame),
        "train_valid_sha256": sha256_file(train_valid_path),
        "source_sequences_sha256": sha256_file(data_txt),
        "folds": folds,
    }

    folds_dir.mkdir(parents=True, exist_ok=True)
    out_path = folds_dir / f"{spec.public_name}_folds.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def _split_sequence(raw: object) -> list[str]:
    return [item.strip() for item in str(raw).split(",") if item.strip() and item.strip() != "-1"]


def export_sequence_sidecar(
    *,
    spec: DatasetSpec,
    dataset_dir: Path,
    folds_dir: Path,
) -> Path:
    train_valid_path = dataset_dir / "train_valid.csv"
    frame = pd.read_csv(train_valid_path)
    required = {"concepts", "responses"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{train_valid_path} is missing required sequence columns: {sorted(missing)}")

    folds_dir.mkdir(parents=True, exist_ok=True)
    out_path = folds_dir / f"{spec.public_name}_sequences.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["row_index", "order", "skill", "correct"])
        for row_index, row in frame.iterrows():
            concepts = _split_sequence(row["concepts"])
            responses = _split_sequence(row["responses"])
            if len(concepts) != len(responses):
                raise ValueError(
                    f"{train_valid_path} row {row_index} has {len(concepts)} concepts "
                    f"but {len(responses)} responses"
                )
            for order, (skill, correct) in enumerate(zip(concepts, responses)):
                if correct not in {"0", "1"}:
                    raise ValueError(f"{train_valid_path} row {row_index} has non-binary response {correct!r}")
                writer.writerow([row_index, order, skill, correct])
    return out_path


def preprocess_dataset(
    *,
    spec: DatasetSpec,
    mode: str,
    raw_root: Path,
    work_dir: Path,
    config_path: Path,
    folds_dir: Path,
) -> Path:
    if mode == "raw":
        dataset_dir, data_txt, raw_source = preprocess_raw(spec, raw_root, config_path)
    elif mode == "smoke":
        dataset_dir, data_txt, raw_source = preprocess_smoke(spec, work_dir, config_path)
    else:
        raw_path = raw_dataset_path(raw_root, spec)
        if raw_path.exists():
            dataset_dir, data_txt, raw_source = preprocess_raw(spec, raw_root, config_path)
        else:
            dataset_dir, data_txt, raw_source = preprocess_smoke(spec, work_dir, config_path)

    folds_path = export_folds(
        spec=spec,
        dataset_dir=dataset_dir,
        data_txt=data_txt,
        raw_source=raw_source,
        folds_dir=folds_dir,
    )
    sidecar_path = export_sequence_sidecar(spec=spec, dataset_dir=dataset_dir, folds_dir=folds_dir)
    print(f"wrote {sidecar_path}")
    return folds_path


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets", default="nips2020,accoding")
    parser.add_argument("--mode", choices=("auto", "raw", "smoke"), default="auto")
    parser.add_argument("--raw-root", type=Path, default=Path("data"))
    parser.add_argument("--work-dir", type=Path, default=Path(".work"))
    parser.add_argument("--folds-dir", type=Path, default=Path("folds"))
    args = parser.parse_args(argv)

    config_path = args.work_dir / "data_config.json"
    ensure_config(config_path)

    for spec in parse_datasets(args.datasets):
        out_path = preprocess_dataset(
            spec=spec,
            mode=args.mode,
            raw_root=args.raw_root,
            work_dir=args.work_dir,
            config_path=config_path,
            folds_dir=args.folds_dir,
        )
        print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
