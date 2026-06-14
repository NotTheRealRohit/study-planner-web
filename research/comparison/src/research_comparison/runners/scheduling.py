from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from py_roadmap_engine import Material, RoadmapInput, RoadmapOutput, generate_roadmap

from research_comparison.baselines.scheduling import schedule_dp, schedule_rule_based
from research_comparison.metrics.scheduling import (
    scheduling_metric_row,
    winner_by_material_mix,
)
from research_comparison.progress_log import ProgressLogger
from research_comparison.runners.calibration import latest_dataset_dir
from research_comparison.writers.results import manifest_from_dataset, write_stamped_json

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
ROLE_ORDER = {"anchor": 0, "foundation": 1, "practice": 2}


@dataclass(frozen=True)
class SchedulingCandidate:
    name: str
    schedule: Callable[[RoadmapInput], RoadmapOutput]


@dataclass(frozen=True)
class SchedulingScenario:
    scenario_id: str
    material_mix: str
    input_data: RoadmapInput
    deadline: str


def schedule_greedy(input_data: RoadmapInput) -> RoadmapOutput:
    return generate_roadmap(input_data)


def scheduling_candidates() -> list[SchedulingCandidate]:
    return [
        SchedulingCandidate("greedy_incumbent", schedule_greedy),
        SchedulingCandidate("dp_capacity", schedule_dp),
        SchedulingCandidate("rule_based", schedule_rule_based),
    ]


def run_scheduling_for_scenario(
    scenario_id: str,
    material_mix: str,
    input_data: RoadmapInput,
    deadline: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in scheduling_candidates():
        started = time.perf_counter()
        output = candidate.schedule(input_data)
        gen_time_ms = (time.perf_counter() - started) * 1000.0
        rows.append(
            {
                "scenario_id": scenario_id,
                "candidate": candidate.name,
                "material_mix": material_mix,
                **scheduling_metric_row(output, deadline, gen_time_ms),
            }
        )
    return rows


def _day_name(day: str) -> str:
    return DAY_NAMES[date.fromisoformat(day).weekday()]


def _material_mix(roles: list[str]) -> str:
    return "+".join(sorted(set(roles), key=lambda role: ROLE_ORDER.get(role, 99)))


def scenario_from_learner(
    learner: dict[str, Any],
    truth: dict[str, Any],
) -> SchedulingScenario:
    sessions = learner["sessions"]
    totals_by_role: dict[str, float] = defaultdict(float)
    selected_days: list[str] = []
    for session in sessions:
        role = str(session.get("materialRole") or "foundation")
        planned = session.get("plannedMinutes")
        totals_by_role[role] += float(planned if planned is not None else session.get("duration") or 0.0)
        day = _day_name(str(session["date"]))
        if day not in selected_days:
            selected_days.append(day)

    roles = sorted(totals_by_role, key=lambda role: ROLE_ORDER.get(role, 99))
    if "anchor" not in totals_by_role:
        first_role = roles[0] if roles else "foundation"
        totals_by_role["anchor"] = max(30.0, totals_by_role.get(first_role, 60.0) * 0.20)
        roles = sorted(totals_by_role, key=lambda role: ROLE_ORDER.get(role, 99))

    materials = [
        Material(
            id=f"{learner['learner_id']}-{role}",
            title=f"{role.title()} material",
            totalMinutes=round(max(30.0, totals_by_role[role]), 3),
            role=role,  # type: ignore[arg-type]
            additionOrder=index,
        )
        for index, role in enumerate(roles)
    ]

    start = date.fromisoformat(str(sessions[0]["date"]))
    deadline = str(truth["true_finish_date"])
    deadline_date = date.fromisoformat(deadline)
    weeks = max(1, ((deadline_date - start).days // 7) + 1)
    selected = selected_days or ["Mon", "Wed", "Sat"]
    total_minutes = sum(float(material.totalMinutes) for material in materials)
    hours_per_week = max(total_minutes / weeks / 60.0 * 1.10, 1.0)
    weekday_days = [day for day in selected if day not in {"Sat", "Sun"}]
    weekend_days = [day for day in selected if day in {"Sat", "Sun"}]
    weekday_hours = hours_per_week * (len(weekday_days) / max(1, len(selected)))
    weekend_hours = hours_per_week * (len(weekend_days) / max(1, len(selected)))

    return SchedulingScenario(
        scenario_id=str(learner["learner_id"]),
        material_mix=_material_mix(roles),
        input_data=RoadmapInput(
            materials=materials,
            weeks=weeks,
            startDate=start.isoformat(),
            selectedStudyDays=selected,  # type: ignore[arg-type]
            weekdayHours=round(max(0.5, weekday_hours), 3),
            weekendHours=round(max(0.5, weekend_hours), 3),
        ),
        deadline=deadline,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def run_scheduling_track(
    dataset_dir: str | None = None,
    out_dir: str | None = None,
    progress: ProgressLogger | None = None,
) -> Path:
    root = _repo_root()
    dataset_path = Path(dataset_dir) if dataset_dir else latest_dataset_dir()
    result_root = Path(out_dir) if out_dir else root / "research/results/scheduling"
    if progress:
        progress.log(0, "scheduling.start", f"dataset={dataset_path}")
    raw_manifest = json.loads((dataset_path / "manifest.json").read_text(encoding="utf-8"))
    manifest = manifest_from_dataset(raw_manifest)
    sidecars = {
        row["learner_id"]: row["ground_truth"]
        for row in _read_jsonl(dataset_path / "sidecars.jsonl")
    }

    rows: list[dict[str, Any]] = []
    learners = _read_jsonl(dataset_path / "learners.jsonl")
    total_learners = len(learners)
    if progress:
        progress.log(10, "scheduling.loaded", f"learners={total_learners}")
    for learner_index, learner in enumerate(learners, start=1):
        scenario = scenario_from_learner(learner, sidecars[learner["learner_id"]])
        rows.extend(
            {
                **row,
                "band": learner["band"],
                "archetype": learner["archetype"],
                "seed": learner["seed"],
            }
            for row in run_scheduling_for_scenario(
                scenario.scenario_id,
                scenario.material_mix,
                scenario.input_data,
                scenario.deadline,
            )
        )
        if progress and (
            learner_index == 1
            or learner_index == total_learners
            or learner_index % max(1, total_learners // 20) == 0
        ):
            progress.log(
                10 + (learner_index / max(1, total_learners)) * 80,
                "scheduling.scenarios",
                f"processed={learner_index}/{total_learners} rows={len(rows)}",
            )

    payload = {
        "dataset_id": raw_manifest["dataset_id"],
        "rows": rows,
        "winner_by_material_mix": winner_by_material_mix(rows),
    }
    if progress:
        progress.log(95, "scheduling.write", f"rows={len(rows)}")
    out_path = write_stamped_json(result_root / "scheduling_results.json", payload, manifest)
    if progress:
        progress.log(100, "scheduling.complete", str(out_path))
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-dir", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--quiet", action="store_true", help="suppress progress output on stderr")
    args = parser.parse_args()
    logger = ProgressLogger(label="research-scheduling", enabled=not args.quiet)
    print(run_scheduling_track(dataset_dir=args.dataset_dir, out_dir=args.out_dir, progress=logger))


if __name__ == "__main__":
    main()
