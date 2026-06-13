from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

import numpy as np

from research_comparison.generator.adherence import attempt_probability, choose_source
from research_comparison.generator.archetypes import archetype_config
from research_comparison.generator.capacity import PlannedSlot, build_capacity_plan
from research_comparison.generator.effects import delta_deadline, phi_fatigue
from research_comparison.generator.materials import Material, sample_material_mix
from research_comparison.generator.noise import apply_lognormal_ar1
from research_comparison.generator.pace import latent_base
from research_comparison.generator.regimes import build_regime_series
from research_comparison.generator.types import GroundTruth, SessionEvent
from research_comparison.manifest import build_manifest, stamp
from research_comparison.params import BANDS, CLIP_HIGH, CLIP_LOW, PARAMS_VERSION_HASH, ROLE_RHO

DEFAULT_ARCHETYPE_MIX = {
    "steady": 1,
    "morning_lark": 1,
    "fading_flame": 1,
    "weekend_warrior": 1,
    "deadline_sprinter": 1,
    "marathon_runner": 1,
}
DEFAULT_BANDS = ["small", "medium", "max"]
DEFAULT_SEEDS = list(range(40))


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[5]


def _json_default(value):
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _target_sessions(band: str, rng: np.random.Generator) -> int:
    low, high = BANDS[band]["sessions"]
    return int(rng.integers(low, high + 1))


def _collect_attempted_slots(
    archetype: str,
    config: dict,
    materials: list[Material],
    target_sessions: int,
    rng: np.random.Generator,
) -> list[tuple[PlannedSlot, str]]:
    slots_needed = max(target_sessions * 4, target_sessions + 12)
    emitted: list[tuple[PlannedSlot, str]] = []
    while len(emitted) < target_sessions:
        slots = build_capacity_plan(materials, slots_needed, rng, start_date=date(2026, 1, 5))
        for slot in slots:
            if len(emitted) >= target_sessions:
                break
            prob = attempt_probability(archetype, config, slot, len(emitted), target_sessions)
            if float(rng.random()) <= prob:
                emitted.append((slot, choose_source(rng)))
        slots_needed *= 2
    return emitted[:target_sessions]


def _context_multipliers(config: dict) -> dict[str, float]:
    return {
        "morning": float(config["tau"].get("morning", 1.0)),
        "afternoon": float(config["tau"].get("afternoon", 1.0)),
        "evening": float(config["tau"].get("evening", 1.0)),
        "weekday": 1.0,
        "weekend": float(config.get("nu_weekend", 1.0)),
    }


def _true_finish_date(
    emitted_slots: list[tuple[PlannedSlot, str]],
    materials: list[Material],
    r_star: list[float],
) -> str:
    target_minutes = sum(material.total_minutes for material in materials)
    cumulative = 0.0
    for (slot, _source), latent in zip(emitted_slots, r_star, strict=True):
        cumulative += slot.planned_minutes * latent
        if cumulative >= target_minutes:
            return slot.date.isoformat()
    return emitted_slots[-1][0].date.isoformat()


def _event_for_slot(
    archetype: str,
    band: str,
    seed: int,
    index: int,
    slot: PlannedSlot,
    source: str,
    ratio: float,
) -> SessionEvent:
    base: SessionEvent = {
        "date": slot.date.isoformat(),
        "source": source,  # type: ignore[typeddict-item]
        "duration": round(
            slot.planned_minutes if source == "manual" else slot.planned_minutes * ratio,
            6,
        ),
        "materialRole": slot.material_role,
        "startedAt": slot.started_at,
        "sessionId": f"{archetype}-{band}-{seed}-{index:04d}",
    }
    if source == "active":
        base["plannedMinutes"] = round(slot.planned_minutes, 6)
        base["activeMinutes"] = round(slot.planned_minutes * ratio, 6)
    return base


def _draw_emitted_ratios_under_clip_guard(
    r_star: list[float],
    emitted_slots: list[tuple[PlannedSlot, str]],
    sigma_log: float,
    rng: np.random.Generator,
) -> tuple[list[float], float]:
    active_indices = [
        index for index, (_slot, source) in enumerate(emitted_slots) if source == "active"
    ]
    best_ratios: list[float] = []
    best_clip_rate = 1.0

    for _attempt in range(20):
        emitted_ratios, _clip_rate = apply_lognormal_ar1(r_star, sigma_log, rng)
        active_clip_count = sum(
            1
            for index in active_indices
            if emitted_ratios[index] <= CLIP_LOW or emitted_ratios[index] >= CLIP_HIGH
        )
        clip_rate = active_clip_count / max(1, len(active_indices))
        if clip_rate < best_clip_rate:
            best_ratios = emitted_ratios
            best_clip_rate = clip_rate
        if clip_rate < 0.02:
            return emitted_ratios, clip_rate

    return best_ratios, best_clip_rate


def generate_learner(
    archetype: str,
    band: str,
    seed: int,
) -> tuple[list[SessionEvent], GroundTruth]:
    rng = np.random.default_rng(seed)
    config = archetype_config(archetype)
    target_sessions = _target_sessions(band, rng)
    materials = sample_material_mix(band, rng)
    emitted_slots = _collect_attempted_slots(archetype, config, materials, target_sessions, rng)
    regime, shifts = build_regime_series(archetype, band, len(emitted_slots), rng)

    r_star: list[float] = []
    for index, ((slot, _source), regime_multiplier) in enumerate(
        zip(emitted_slots, regime, strict=True)
    ):
        latent = (
            latent_base(
                float(config["m_global"]),
                slot.material_role,
                slot.time_of_day,
                slot.day_of_week,
                config,
            )
            * regime_multiplier
            * phi_fatigue(slot.same_day_count)
            * delta_deadline(index, len(emitted_slots), config)
        )
        r_star.append(round(float(latent), 6))

    emitted_ratios, clip_rate = _draw_emitted_ratios_under_clip_guard(
        r_star, emitted_slots, float(config["sigma_log"]), rng
    )
    events = [
        _event_for_slot(archetype, band, seed, index, slot, source, emitted_ratios[index])
        for index, (slot, source) in enumerate(emitted_slots)
    ]
    truth = GroundTruth(
        m_global=float(config["m_global"]),
        role_multipliers=dict(ROLE_RHO),
        context_multipliers=_context_multipliers(config),
        regime_schedule=shifts,
        r_star=r_star,
        true_finish_date=_true_finish_date(emitted_slots, materials, r_star),
        is_faker=False,
        clip_rate=round(float(clip_rate), 6),
    )
    return events, truth


def generate_dataset(
    archetype_mix: dict[str, int] | None = None,
    bands: list[str] | None = None,
    seeds: list[int] | None = None,
    out_dir: str | None = None,
) -> str:
    mix = archetype_mix or DEFAULT_ARCHETYPE_MIX
    selected_bands = bands or DEFAULT_BANDS
    selected_seeds = seeds or DEFAULT_SEEDS
    out_root = Path(out_dir) if out_dir else _repo_root() / "research/datasets"
    n_learners = sum(mix.values()) * len(selected_bands) * len(selected_seeds)
    dataset_id = f"synthetic-{PARAMS_VERSION_HASH}-seed{selected_seeds[0]}-n{n_learners}"
    dataset_dir = out_root / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)

    learners_path = dataset_dir / "learners.jsonl"
    sidecars_path = dataset_dir / "sidecars.jsonl"
    with learners_path.open("w", encoding="utf-8") as learner_file, sidecars_path.open(
        "w", encoding="utf-8"
    ) as sidecar_file:
        learner_index = 0
        for seed in selected_seeds:
            for band in selected_bands:
                for archetype, count in mix.items():
                    for replicate in range(count):
                        learner_seed = int(seed * 10_000 + learner_index + replicate)
                        sessions, truth = generate_learner(archetype, band, learner_seed)
                        metadata = {
                            "learner_id": f"{archetype}-{band}-{seed}-{learner_index:05d}",
                            "archetype": archetype,
                            "band": band,
                            "seed": seed,
                        }
                        learner_file.write(
                            json.dumps(
                                {**metadata, "sessions": sessions},
                                sort_keys=True,
                                default=_json_default,
                            )
                            + "\n"
                        )
                        sidecar_file.write(
                            json.dumps(
                                {**metadata, "ground_truth": asdict(truth)},
                                sort_keys=True,
                                default=_json_default,
                            )
                            + "\n"
                        )
                        learner_index += 1

    manifest = build_manifest(seed=selected_seeds[0], archetype_mix=mix, n_learners=n_learners)
    manifest_dict = {
        **asdict(manifest),
        "dataset_id": dataset_id,
        "bands": selected_bands,
        "seeds": selected_seeds,
    }
    (dataset_dir / "manifest.json").write_text(
        json.dumps(manifest_dict, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    export_face_validity(str(dataset_dir))
    return dataset_id


def export_face_validity(dataset_dir: str) -> None:
    dataset_path = Path(dataset_dir)
    pace_ratio: list[float] = []
    duration: list[float] = []
    gaps_days: list[int] = []
    for line in (dataset_path / "learners.jsonl").read_text(encoding="utf-8").splitlines():
        learner = json.loads(line)
        previous_date: date | None = None
        for event in learner["sessions"]:
            current_date = date.fromisoformat(event["date"])
            if previous_date is not None:
                gaps_days.append((current_date - previous_date).days)
            previous_date = current_date
            duration.append(float(event["duration"]))
            if event["source"] == "active":
                pace_ratio.append(float(event["activeMinutes"]) / float(event["plannedMinutes"]))

    output = {
        "pace_ratio": pace_ratio,
        "duration": duration,
        "gaps_days": gaps_days,
    }
    (dataset_path / "face_validity.json").write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_stub() -> Path:
    manifest = build_manifest(seed=0, archetype_mix={"stub": 1}, n_learners=1)
    output = stamp({"status": "stub", "stage": "dataset"}, manifest)
    out_path = _repo_root() / "research/results/dataset_stub.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stub", action="store_true")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    if args.stub:
        print(write_stub())
        return
    print(generate_dataset(out_dir=args.out_dir))


if __name__ == "__main__":
    main()
