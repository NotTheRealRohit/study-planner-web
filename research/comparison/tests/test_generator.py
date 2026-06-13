from __future__ import annotations

import json
from dataclasses import asdict

from py_progress import MIN_SESSIONS_PER_BUCKET, compute_hierarchical_model
from research_comparison.generator.generate import generate_dataset, generate_learner
from research_comparison.params import ARCHETYPES, BANDS, PARAMS_VERSION_HASH


def _canonical(events, truth) -> str:
    return json.dumps({"events": events, "truth": asdict(truth)}, sort_keys=True)


def test_generate_learner_emits_session_event_shape():
    events, truth = generate_learner("steady", "small", 101)

    assert events
    assert len(truth.r_star) == len(events)
    for event in events:
        assert {"date", "source", "duration", "materialRole", "startedAt", "sessionId"} <= set(
            event
        )
        assert event["materialRole"] in {"anchor", "foundation", "practice"}
        if event["source"] == "active":
            assert event["plannedMinutes"] > 0
            assert event["activeMinutes"] > 0
        else:
            assert event["source"] == "manual"
            assert event.get("plannedMinutes") is None
            assert event.get("activeMinutes") is None


def test_generate_learner_is_deterministic_by_seed():
    first = generate_learner("steady", "medium", 42)
    second = generate_learner("steady", "medium", 42)

    assert _canonical(*first) == _canonical(*second)


def test_oracle_recovers_planted_pace_for_steady_learner():
    events, truth = generate_learner("steady", "medium", 7)
    active = [event for event in events if event["source"] == "active"]

    result = compute_hierarchical_model(active, set())

    assert abs(result.globalPosterior.mean - truth.m_global) < 0.12
    for role, multiplier in truth.role_multipliers.items():
        role_count = sum(1 for event in active if event["materialRole"] == role)
        if role_count >= MIN_SESSIONS_PER_BUCKET:
            assert role in result.roleMultipliers
            assert abs(result.roleMultipliers[role].multiplier - truth.m_global * multiplier) < 0.18


def test_shift_labels_match_band_schedule():
    for band, band_config in BANDS.items():
        _, truth = generate_learner("marathon_runner", band, 11)
        assert band_config["shifts"][0] <= len(truth.regime_schedule) <= band_config["shifts"][1]
        for shift in truth.regime_schedule:
            assert shift.type in {"step", "drift"}
            assert shift.onset_index >= 4
            assert shift.onset_index <= len(truth.r_star) - 4
            assert 0.20 <= shift.onset_index / len(truth.r_star) <= 0.80


def test_clip_rate_under_two_percent_for_each_archetype():
    for index, archetype in enumerate(ARCHETYPES):
        _, truth = generate_learner(archetype, "medium", 900 + index)
        assert truth.clip_rate < 0.02


def test_generate_dataset_writes_manifest_sidecar_and_face_validity(tmp_path):
    dataset_dir = generate_dataset(
        archetype_mix={"steady": 1, "morning_lark": 1},
        bands=["small"],
        seeds=[1],
        out_dir=str(tmp_path),
    )

    dataset_path = tmp_path / dataset_dir
    manifest = json.loads((dataset_path / "manifest.json").read_text())
    learner_lines = (dataset_path / "learners.jsonl").read_text().splitlines()
    sidecar_lines = (dataset_path / "sidecars.jsonl").read_text().splitlines()
    face_validity = json.loads((dataset_path / "face_validity.json").read_text())

    assert manifest["params_version_hash"] == PARAMS_VERSION_HASH
    assert manifest["n_learners"] == 2
    assert len(learner_lines) == 2
    assert len(sidecar_lines) == 2
    assert face_validity["pace_ratio"]
