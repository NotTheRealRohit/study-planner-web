from __future__ import annotations

import json
import math

from research_comparison.baselines.calibration import (
    EWMACalibrator,
    IncumbentCalibration,
    PooledBayesianCalibrator,
    SMACalibrator,
)
from research_comparison.generator.generate import generate_dataset
from research_comparison.generator.generate import generate_learner
from research_comparison.metrics.aggregate import winner_per_band
from research_comparison.metrics.paired import paired_difference
from research_comparison.plots.convergence import write_convergence_artifacts
from research_comparison.runners.calibration import prequential_calibration
from research_comparison.runners.calibration import run_calibration_track


def _flat_sessions(ratio: float = 1.08, n: int = 18):
    return [
        {
            "date": f"2026-01-{index + 1:02d}",
            "source": "active",
            "plannedMinutes": 50.0,
            "activeMinutes": 50.0 * ratio,
            "duration": 50.0 * ratio,
            "materialRole": "foundation",
            "startedAt": f"2026-01-{index + 1:02d}T08:00:00Z",
            "sessionId": f"flat-{index}",
        }
        for index in range(n)
    ]


def test_prequential_runner_returns_finite_estimates_for_all_candidates():
    sessions, _truth = generate_learner("steady", "medium", 44)
    active = [session for session in sessions if session["source"] == "active"]
    candidates = [
        IncumbentCalibration(),
        SMACalibrator(window=5),
        EWMACalibrator(alpha=0.35),
        PooledBayesianCalibrator(),
    ]

    for candidate in candidates:
        estimates = prequential_calibration(active, candidate, [3, 5, 8])
        assert len(estimates) == 3
        assert all(math.isfinite(estimate) for _t, estimate in estimates)


def test_baselines_return_float_and_pooled_converges_on_flat_pace():
    sessions = _flat_sessions(ratio=1.08, n=24)

    assert isinstance(SMACalibrator(window=5).fit_global(sessions), float)
    assert isinstance(EWMACalibrator(alpha=0.30).fit_global(sessions), float)
    pooled = PooledBayesianCalibrator().fit_global(sessions)
    assert abs(pooled - 1.08) < 0.04


def test_paired_difference_recovers_delta_p_value_and_effect_sign():
    result = paired_difference([0.30, 0.25, 0.20, 0.18], [0.35, 0.31, 0.29, 0.23])

    assert result["delta"] < 0
    assert 0 <= result["p_value"] <= 1
    assert result["effect_size"] < 0


def test_winner_per_band_chooses_lower_error_candidate():
    rows = [
        {"band": "small", "archetype": "steady", "candidate": "a", "recovery_mae": 0.20},
        {"band": "small", "archetype": "steady", "candidate": "b", "recovery_mae": 0.10},
        {"band": "medium", "archetype": "steady", "candidate": "a", "recovery_mae": 0.05},
        {"band": "medium", "archetype": "steady", "candidate": "b", "recovery_mae": 0.08},
    ]

    winners = winner_per_band(rows)

    assert winners["small"]["winner"] == "b"
    assert winners["medium"]["winner"] == "a"


def test_tracer_bullet_dataset_compare_figs_produces_artifacts_in_temp_workspace(tmp_path):
    workspace = tmp_path / "research-comparison-tracer"
    datasets_root = workspace / "datasets"
    results_root = workspace / "results"
    generated = workspace / "generated"

    dataset_id = generate_dataset(
        archetype_mix={"steady": 1},
        bands=["small"],
        seeds=[0],
        out_dir=str(datasets_root),
    )
    dataset_dir = datasets_root / dataset_id
    result_path = run_calibration_track(
        dataset_dir=str(dataset_dir),
        out_dir=str(results_root / "calibration"),
    )
    write_convergence_artifacts(result_path, generated_dir=generated)

    pdf = generated / "calibration_convergence.pdf"
    table = generated / "calibration_winners.tex"
    result_files = sorted((results_root / "calibration").glob("*.json"))

    assert pdf.exists() and pdf.stat().st_size > 0
    assert table.exists() and table.stat().st_size > 0
    assert result_files
    assert "_provenance" in json.loads(result_files[0].read_text())
