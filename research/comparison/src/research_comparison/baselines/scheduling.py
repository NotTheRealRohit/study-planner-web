from __future__ import annotations

import math
from dataclasses import replace
from datetime import date, timedelta

from py_roadmap_engine import CapacityCheck, RoadmapInput, RoadmapOutput, RoadmapWeek, Slot, Warning
from py_roadmap_engine.types import Material

DAY_OFFSETS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
ROLE_ORDER = {"anchor": 0, "foundation": 1, "practice": 2}


def _capacity_for_day(input_data: RoadmapInput, day: str) -> int:
    selected_weekdays = [d for d in input_data.selectedStudyDays if d not in {"Sat", "Sun"}]
    selected_weekends = [d for d in input_data.selectedStudyDays if d in {"Sat", "Sun"}]
    if day in {"Sat", "Sun"}:
        return round((input_data.weekendHours * 60) / max(1, len(selected_weekends)))
    return round((input_data.weekdayHours * 60) / max(1, len(selected_weekdays)))


def _slot_grid(input_data: RoadmapInput) -> list[Slot]:
    start = date.fromisoformat(input_data.startDate)
    slots: list[Slot] = []
    for week in range(input_data.weeks):
        for day in input_data.selectedStudyDays:
            slots.append(
                Slot(
                    weekIndex=week,
                    dayOfWeek=day,
                    date=(start + timedelta(days=week * 7 + DAY_OFFSETS[day])).isoformat(),
                    capacityMinutes=_capacity_for_day(input_data, day),
                    role=None,
                    candidateMaterialIds=[],
                    plannedMinutes=0,
                    sessionTitle=None,
                )
            )
    return slots


def _capacity_check(input_data: RoadmapInput, slots: list[Slot]) -> CapacityCheck:
    total_capacity = sum(slot.capacityMinutes for slot in slots)
    total_material = sum(material.totalMinutes for material in input_data.materials)
    if total_material > total_capacity:
        return CapacityCheck(total_capacity, total_material, "over-capacity")
    return CapacityCheck(total_capacity, total_material, "fits")


def _weeks_from_slots(slots: list[Slot], input_data: RoadmapInput, warnings: list[Warning]) -> RoadmapOutput:
    weeks: list[RoadmapWeek] = []
    start = date.fromisoformat(input_data.startDate)
    for week_index in range(input_data.weeks):
        week_slots = [slot for slot in slots if slot.weekIndex == week_index]
        weeks.append(
            RoadmapWeek(
                weekIndex=week_index,
                startDate=(start + timedelta(days=week_index * 7)).isoformat(),
                slots=week_slots,
            )
        )
    return RoadmapOutput(
        weeks=weeks,
        warnings=warnings,
        capacityCheck=_capacity_check(input_data, slots),
    )


def _allocate(
    input_data: RoadmapInput,
    materials: list[Material],
    *,
    overflow_last_slot: bool,
) -> RoadmapOutput:
    slots = _slot_grid(input_data)
    warnings: list[Warning] = []
    slot_index = 0
    for material in materials:
        remaining = float(material.totalMinutes)
        session = 1
        while remaining > 1e-6 and slot_index < len(slots):
            slot = slots[slot_index]
            available = float(slot.capacityMinutes)
            if available <= 0:
                slot_index += 1
                continue
            planned = min(available, remaining)
            slot.role = material.role
            slot.candidateMaterialIds = [material.id]
            slot.plannedMinutes = round(planned, 3)
            slot.sessionTitle = f"{material.title} · session {session}"
            remaining -= planned
            session += 1
            slot_index += 1
        if remaining > 1e-6:
            warnings.append(
                Warning(
                    "over-capacity",
                    {"materialId": material.id, "overflowMinutes": round(remaining, 3)},
                )
            )
            if overflow_last_slot and slots:
                slot = slots[-1]
                slot.role = material.role
                slot.candidateMaterialIds = [material.id]
                slot.plannedMinutes = round(float(slot.plannedMinutes) + remaining, 3)
                slot.sessionTitle = f"{material.title} · overflow"
    return _weeks_from_slots(slots, input_data, warnings)


def schedule_dp(input_data: RoadmapInput) -> RoadmapOutput:
    """Capacity-respecting DP-style baseline: role order, then smaller jobs first."""
    materials = sorted(
        input_data.materials,
        key=lambda material: (ROLE_ORDER[material.role], material.totalMinutes, material.additionOrder),
    )
    return _allocate(replace(input_data, materials=materials), materials, overflow_last_slot=False)


def schedule_rule_based(input_data: RoadmapInput) -> RoadmapOutput:
    """Fixed heuristic baseline: anchor, foundation, practice, original addition order."""
    materials = sorted(
        input_data.materials,
        key=lambda material: (ROLE_ORDER[material.role], material.additionOrder),
    )
    return _allocate(replace(input_data, materials=materials), materials, overflow_last_slot=True)
