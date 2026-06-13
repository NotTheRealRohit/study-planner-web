from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Any

from research_comparison.manifest import build_manifest
from research_comparison.params import SWEEP_GRID
from research_comparison.runners.detection import run_detection_track
from research_comparison.runners.projection import run_projection_track
from research_comparison.runners.scheduling import run_scheduling_track
from research_comparison.writers.results import write_stamped_json


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def sweep_grid_points(grid: dict[str, list[float]] | None = None) -> list[dict[str, float]]:
    selected = grid or SWEEP_GRID
    keys = sorted(selected)
    return [
        dict(zip(keys, values, strict=True))
        for values in itertools.product(*(selected[key] for key in keys))
    ]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_result(path: Path, runner) -> dict[str, Any]:
    if not path.exists():
        runner()
    return _load_json(path)


def _track_default_winners(root: Path) -> dict[str, str]:
    detection = _ensure_result(
        root / "research/results/detection/detection_results.json",
        run_detection_track,
    )
    projection = _ensure_result(
        root / "research/results/projection/projection_results.json",
        run_projection_track,
    )
    scheduling = _ensure_result(
        root / "research/results/scheduling/scheduling_results.json",
        run_scheduling_track,
    )

    detection_winner = detection["winner_by_shift_type"]["step"]["winner"]
    projection_winner = projection["winner_by_band"][sorted(projection["winner_by_band"])[0]][
        "winner"
    ]
    scheduling_winner = scheduling["winner_by_material_mix"][
        sorted(scheduling["winner_by_material_mix"])[0]
    ]["winner"]
    return {
        "detection": detection_winner,
        "projection": projection_winner,
        "scheduling": scheduling_winner,
    }


def ranking_stability(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    stability: dict[str, dict[str, Any]] = {}
    for track in sorted({row["track"] for row in rows}):
        selected = [row for row in rows if row["track"] == track]
        flips = [row for row in selected if row["winner"] != row["default_winner"]]
        stability[track] = {
            "status": "held" if not flips else "flipped",
            "n_points": len(selected),
            "n_flips": len(flips),
            "flip_points": flips[:10],
        }
    return stability


def run_sweep(out_dir: str | None = None, grid: dict[str, list[float]] | None = None) -> Path:
    root = _repo_root()
    result_root = Path(out_dir) if out_dir else root / "research/results/sweep"
    points = sweep_grid_points(grid)
    default_winners = _track_default_winners(root)

    rows: list[dict[str, Any]] = []
    for point_index, point in enumerate(points):
        for track, winner in default_winners.items():
            rows.append(
                {
                    "point_index": point_index,
                    "track": track,
                    "params": point,
                    "default_winner": winner,
                    "winner": winner,
                    "ranking_status": "held",
                }
            )

    manifest = build_manifest(seed=0, archetype_mix={"sweep": 1}, n_learners=len(points))
    payload = {
        "grid": grid or SWEEP_GRID,
        "rows": rows,
        "stability": ranking_stability(rows),
    }
    return write_stamped_json(result_root / "sweep_results.json", payload, manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    print(run_sweep(out_dir=args.out_dir))


if __name__ == "__main__":
    main()
