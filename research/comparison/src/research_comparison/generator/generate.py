from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np

from research_comparison.generator.adherence import attempt_probability, choose_source
from research_comparison.generator.archetypes import archetype_config
from research_comparison.generator.capacity import PlannedSlot, build_capacity_plan
from research_comparison.generator.effects import delta_deadline, phi_fatigue
from research_comparison.generator.materials import Material, sample_material_mix
from research_comparison.generator.noise import apply_lognormal_ar1
from research_comparison.generator.pace import latent_base
from research_comparison.generator.reality import (
    REALITY_REGIME,
    build_reality_regime_series,
    collect_reality_slots,
    draw_reality_logged_ratios,
    normalise_moment_bounds,
    reality_params_hash,
    sample_continuous_config,
)
from research_comparison.generator.regimes import build_regime_series
from research_comparison.generator.types import GroundTruth, SessionEvent
from research_comparison.manifest import build_manifest, stamp
from research_comparison.params import (
    AR1_PHI,
    BANDS,
    CLIP_HIGH,
    CLIP_LOW,
    MANUAL_FRACTION,
    PARAMS_VERSION_HASH,
    ROLE_RHO,
)
from research_comparison.progress_log import ProgressLogger

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
FROZEN_REGIME = "frozen"


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
    manual_fraction: float,
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
                emitted.append((slot, choose_source(rng, manual_fraction=manual_fraction)))
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
    ar1_phi: float,
) -> tuple[list[float], float]:
    active_indices = [
        index for index, (_slot, source) in enumerate(emitted_slots) if source == "active"
    ]
    best_ratios: list[float] = []
    best_clip_rate = 1.0

    for _attempt in range(20):
        emitted_ratios, _clip_rate = apply_lognormal_ar1(r_star, sigma_log, rng, phi=ar1_phi)
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
    overrides: dict[str, float] | None = None,
) -> tuple[list[SessionEvent], GroundTruth]:
    selected_overrides = overrides or {}
    rng = np.random.default_rng(seed)
    config = archetype_config(archetype)
    if "sigma_log" in selected_overrides:
        config["sigma_log"] = float(selected_overrides["sigma_log"])
    target_sessions = _target_sessions(band, rng)
    materials = sample_material_mix(band, rng)
    emitted_slots = _collect_attempted_slots(
        archetype,
        config,
        materials,
        target_sessions,
        rng,
        manual_fraction=float(selected_overrides.get("manual_fraction", MANUAL_FRACTION)),
    )
    regime, shifts = build_regime_series(
        archetype,
        band,
        len(emitted_slots),
        rng,
        step_magnitude=selected_overrides.get("step_mag"),
        drift_total=selected_overrides.get("drift_total"),
    )

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
        r_star,
        emitted_slots,
        float(config["sigma_log"]),
        rng,
        ar1_phi=float(selected_overrides.get("ar1_phi", AR1_PHI)),
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


def generate_reality_matched_learner(
    archetype: str,
    band: str,
    seed: int,
    moment_bounds: dict[str, Any] | None = None,
    overrides: dict[str, float] | None = None,
) -> tuple[list[SessionEvent], GroundTruth, dict[str, Any]]:
    selected_overrides = overrides or {}
    bounds = normalise_moment_bounds(moment_bounds)
    rng = np.random.default_rng(seed)
    base_config = archetype_config(archetype)
    config, continuous_traits = sample_continuous_config(base_config, bounds, rng)
    if "sigma_log" in selected_overrides:
        config["sigma_log"] = float(selected_overrides["sigma_log"])
    target_sessions = _target_sessions(band, rng)
    materials = sample_material_mix(band, rng)
    emitted_slots, missingness = collect_reality_slots(
        archetype,
        config,
        materials,
        target_sessions,
        rng,
        bounds,
        manual_fraction=float(selected_overrides.get("manual_fraction", MANUAL_FRACTION)),
    )
    regime, shifts, annotations = build_reality_regime_series(len(emitted_slots), rng, bounds)

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

    logged_ratios, true_ratios, clip_rate, misreport_factors = draw_reality_logged_ratios(
        r_star,
        emitted_slots,
        float(config["sigma_log"]),
        rng,
        ar1_phi=float(selected_overrides.get("ar1_phi", config["ar1_phi"])),
    )
    events = [
        _event_for_slot(archetype, band, seed, index, slot, source, logged_ratios[index])
        for index, (slot, source) in enumerate(emitted_slots)
    ]
    truth = GroundTruth(
        m_global=float(config["m_global"]),
        role_multipliers=dict(config.get("role_rho", ROLE_RHO)),
        context_multipliers=_context_multipliers(config),
        regime_schedule=shifts,
        r_star=r_star,
        true_finish_date=_true_finish_date(emitted_slots, materials, r_star),
        is_faker=False,
        clip_rate=round(float(clip_rate), 6),
    )
    misreporting = []
    for index, (event, (slot, source)) in enumerate(zip(events, emitted_slots, strict=True)):
        if source != "active":
            continue
        misreporting.append(
            {
                "sessionId": event["sessionId"],
                "true_active_minutes": round(slot.planned_minutes * true_ratios[index], 6),
                "reported_active_minutes": event["activeMinutes"],
                "misreport_factor": misreport_factors[index],
            }
        )
    metadata = {
        "generator_regime": REALITY_REGIME,
        "continuous_traits": continuous_traits,
        "reality_params_hash": reality_params_hash(bounds),
        "moment_bounds_hash": bounds.get("moment_bounds_hash", reality_params_hash(bounds)),
        "moment_bounds_source": {
            "bounds_version": bounds.get("bounds_version"),
            "proxy_mapping": bounds.get("proxy_mapping"),
        },
        "reality_annotations": [
            *annotations,
            {
                "label": "illness_holiday_gap",
                "hiatus_start": missingness.get("hiatus_start"),
                "hiatus_end": missingness.get("hiatus_end"),
                "hiatus_days": missingness.get("hiatus_days"),
            },
        ],
        "missingness": missingness,
        "logged_time_misreporting": {
            "hidden_from_candidate_inputs": True,
            "entries": misreporting,
        },
        "noise_model": "heavy_tailed_session_length_dependent_ar1",
    }
    return events, truth, metadata


def generate_dataset(
    archetype_mix: dict[str, int] | None = None,
    bands: list[str] | None = None,
    seeds: list[int] | None = None,
    out_dir: str | None = None,
    progress: ProgressLogger | None = None,
    generator_regime: str = FROZEN_REGIME,
    moment_bounds: dict[str, Any] | None = None,
) -> str:
    mix = archetype_mix or DEFAULT_ARCHETYPE_MIX
    selected_bands = bands or DEFAULT_BANDS
    selected_seeds = seeds or DEFAULT_SEEDS
    out_root = Path(out_dir) if out_dir else _repo_root() / "research/datasets"
    n_learners = sum(mix.values()) * len(selected_bands) * len(selected_seeds)
    if generator_regime == FROZEN_REGIME:
        dataset_hash = PARAMS_VERSION_HASH
        dataset_id = f"synthetic-{PARAMS_VERSION_HASH}-seed{selected_seeds[0]}-n{n_learners}"
        selected_moment_bounds = None
    elif generator_regime == REALITY_REGIME:
        selected_moment_bounds = normalise_moment_bounds(moment_bounds)
        dataset_hash = reality_params_hash(selected_moment_bounds)
        dataset_id = f"synthetic-reality-{dataset_hash}-seed{selected_seeds[0]}-n{n_learners}"
    else:
        raise ValueError(f"Unknown generator_regime: {generator_regime}")
    dataset_dir = out_root / dataset_id
    dataset_dir.mkdir(parents=True, exist_ok=True)
    if progress:
        progress.log(0, "dataset.start", f"dataset_id={dataset_id} learners={n_learners}")

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
                        sidecar_extras: dict[str, Any] = {}
                        if generator_regime == REALITY_REGIME:
                            sessions, truth, sidecar_extras = generate_reality_matched_learner(
                                archetype,
                                band,
                                learner_seed,
                                moment_bounds=selected_moment_bounds,
                            )
                        else:
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
                                {**metadata, "ground_truth": asdict(truth), **sidecar_extras},
                                sort_keys=True,
                                default=_json_default,
                            )
                            + "\n"
                        )
                        learner_index += 1
                        if progress and (
                            learner_index == 1
                            or learner_index == n_learners
                            or learner_index % max(1, n_learners // 20) == 0
                        ):
                            percent = 5 + (learner_index / n_learners) * 75
                            progress.log(
                                percent,
                                "dataset.learners",
                                f"generated={learner_index}/{n_learners} seed={seed} "
                                f"band={band} archetype={archetype}",
                            )

    manifest = build_manifest(seed=selected_seeds[0], archetype_mix=mix, n_learners=n_learners)
    manifest_dict = {
        **asdict(manifest),
        "params_version_hash": dataset_hash,
        "base_params_version_hash": PARAMS_VERSION_HASH,
        "dataset_id": dataset_id,
        "generator_regime": generator_regime,
        "bands": selected_bands,
        "seeds": selected_seeds,
        "seed_count": len(selected_seeds),
        "n_learners_formula": (
            f"{sum(mix.values())} archetypes x {len(selected_bands)} bands x "
            f"{len(selected_seeds)} seeds"
        ),
    }
    if generator_regime == REALITY_REGIME:
        manifest_dict["moment_bounds"] = {
            "reality_params_hash": dataset_hash,
            "moment_bounds_hash": selected_moment_bounds.get("moment_bounds_hash", dataset_hash),
            "bounds_version": selected_moment_bounds.get("bounds_version"),
            "source": selected_moment_bounds.get("source"),
            "proxy_mapping": selected_moment_bounds.get("proxy_mapping"),
            "bounds": selected_moment_bounds.get("bounds"),
        }
    (dataset_dir / "manifest.json").write_text(
        json.dumps(manifest_dict, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    if progress:
        progress.log(85, "dataset.manifest_written", str(dataset_dir / "manifest.json"))
    export_face_validity(str(dataset_dir))
    if progress:
        progress.log(100, "dataset.complete", str(dataset_dir))
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
    parser.add_argument("--regime", choices=[FROZEN_REGIME, REALITY_REGIME], default=FROZEN_REGIME)
    parser.add_argument("--moment-bounds-file", default=None)
    parser.add_argument("--seeds", type=int, default=None)
    parser.add_argument("--quiet", action="store_true", help="suppress progress output on stderr")
    args = parser.parse_args()
    logger = ProgressLogger(label="research-dataset", enabled=not args.quiet)
    if args.stub:
        logger.log(0, "dataset.stub_start")
        path = write_stub()
        logger.log(100, "dataset.stub_complete", str(path))
        print(path)
        return
    moment_bounds = None
    if args.moment_bounds_file:
        moment_bounds = json.loads(Path(args.moment_bounds_file).read_text(encoding="utf-8"))
    seeds = list(range(args.seeds)) if args.seeds is not None else None
    print(
        generate_dataset(
            out_dir=args.out_dir,
            progress=logger,
            generator_regime=args.regime,
            moment_bounds=moment_bounds,
            seeds=seeds,
        )
    )


if __name__ == "__main__":
    main()
