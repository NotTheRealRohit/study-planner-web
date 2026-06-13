from __future__ import annotations

from typing import Any

from research_comparison.params import FATIGUE_PER_EXTRA_SESSION


def phi_fatigue(same_day_count: int) -> float:
    return 1.0 + FATIGUE_PER_EXTRA_SESSION * max(0, same_day_count - 1)


def delta_deadline(session_index: int, total_sessions: int, archetype_config: dict[str, Any]) -> float:
    ramp_target = archetype_config.get("deadline_ramp")
    if not ramp_target or total_sessions <= 1:
        return 1.0
    progress = session_index / (total_sessions - 1)
    if progress < 0.80:
        return 1.0
    ramp_progress = (progress - 0.80) / 0.20
    return float(1.0 + (ramp_target - 1.0) * ramp_progress**2)
