from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_comparison.writers.tables import write_scheduling_metrics_table


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def latest_scheduling_results(root: Path | None = None) -> Path:
    results_root = root or _repo_root() / "research/results/scheduling"
    path = results_root / "scheduling_results.json"
    if not path.exists():
        raise FileNotFoundError("No scheduling results found; run make compare-scheduling first")
    return path


def write_scheduling_artifacts(results_path: Path | None = None) -> list[Path]:
    root = _repo_root()
    source = results_path or latest_scheduling_results()
    payload = json.loads(source.read_text(encoding="utf-8"))
    generated_dir = root / "college/mydeliverables/1st-Review/report/generated"
    table = write_scheduling_metrics_table(
        payload["winner_by_material_mix"],
        generated_dir / "scheduling_metrics.tex",
    )
    provenance = generated_dir / "scheduling_metrics_provenance.txt"
    provenance.write_text(
        "Scheduling metrics generated from "
        f"{payload['dataset_id']} with params hash "
        f"{payload['_provenance']['params_version_hash']}.\n",
        encoding="utf-8",
    )
    return [table, provenance]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-path", default=None)
    args = parser.parse_args()
    source = Path(args.results_path) if args.results_path else None
    for path in write_scheduling_artifacts(source):
        print(path)


if __name__ == "__main__":
    main()
