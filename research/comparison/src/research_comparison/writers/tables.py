from __future__ import annotations

from pathlib import Path
from typing import Any


def _tex(value: str) -> str:
    return value.replace("_", r"\_")


def render_calibration_winners_table(winners: dict[str, dict[str, Any]]) -> str:
    lines = [
        r"\begin{tabular}{llr}",
        r"\toprule",
        r"Length band & Winner & Mean recovery MAE \\",
        r"\midrule",
    ]
    for band, row in winners.items():
        lines.append(f"{_tex(band)} & {_tex(row['winner'])} & {row['mean_error']:.4f} \\\\")
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    return "\n".join(lines)


def write_calibration_winners_table(
    winners: dict[str, dict[str, Any]],
    out_path: Path,
) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_calibration_winners_table(winners), encoding="utf-8")
    return out_path
