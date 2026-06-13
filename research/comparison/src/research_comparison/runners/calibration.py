from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_comparison.manifest import build_manifest, stamp


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def write_stub() -> Path:
    manifest = build_manifest(seed=0, archetype_mix={"stub": 1}, n_learners=1)
    output = stamp({"status": "stub", "stage": "compare"}, manifest)
    out_path = _repo_root() / "research/results/compare_stub.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stub", action="store_true")
    args = parser.parse_args()
    if args.stub:
        print(write_stub())
        return
    raise SystemExit("Phase 2 will replace the calibration runner stub.")


if __name__ == "__main__":
    main()
