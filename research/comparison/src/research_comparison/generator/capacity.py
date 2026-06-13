from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

import numpy as np

from research_comparison.generator.materials import Material, sample_chunk_minutes
from research_comparison.generator.types import MaterialRole


@dataclass(frozen=True)
class PlannedSlot:
    date: date
    day_of_week: str
    planned_minutes: float
    material_role: MaterialRole
    material_type: str
    material_id: str
    time_of_day: str
    started_at: str
    same_day_count: int


_TIME_BY_SLOT = ["morning", "afternoon", "evening"]
_HOUR_BY_TIME = {"morning": 8, "afternoon": 14, "evening": 19}


def _iso_started_at(day: date, time_of_day: str) -> str:
    started = datetime.combine(day, time(_HOUR_BY_TIME[time_of_day], 0), tzinfo=UTC)
    return started.isoformat().replace("+00:00", "Z")


def build_capacity_plan(
    materials: list[Material],
    slots_needed: int,
    rng: np.random.Generator,
    start_date: date | None = None,
) -> list[PlannedSlot]:
    start = start_date or date(2026, 1, 5)
    slots: list[PlannedSlot] = []
    day_offset = 0
    material_index = 0
    while len(slots) < slots_needed:
        day = start + timedelta(days=day_offset)
        weekday = day.weekday()
        slots_today = 2 if weekday >= 5 else 1
        for same_day_count in range(1, slots_today + 1):
            if len(slots) >= slots_needed:
                break
            material = materials[material_index % len(materials)]
            material_index += 1
            time_of_day = _TIME_BY_SLOT[(same_day_count - 1 + day_offset) % len(_TIME_BY_SLOT)]
            slots.append(
                PlannedSlot(
                    date=day,
                    day_of_week=day.strftime("%A").lower(),
                    planned_minutes=round(sample_chunk_minutes(material.material_type, rng), 6),
                    material_role=material.role,
                    material_type=material.material_type,
                    material_id=material.material_id,
                    time_of_day=time_of_day,
                    started_at=_iso_started_at(day, time_of_day),
                    same_day_count=same_day_count,
                )
            )
        day_offset += 1
    return slots
