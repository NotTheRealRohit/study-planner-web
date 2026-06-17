from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path

from py_progress import gp_regression
from research_comparison.baselines.projection import (
    conformal_abs_residual_quantile,
    forecast_gp_finish,
    forecast_linear_finish,
)
from research_comparison.metrics.projection import projection_metrics
from research_comparison.runners.projection import projection_candidates, run_projection_for_learner

REPO_ROOT = Path(__file__).resolve().parents[3]


def _sessions(minutes: list[float], start: date = date(2026, 3, 1)) -> list[dict]:
    return [
        {
            "date": (start + timedelta(days=index)).isoformat(),
            "source": "active",
            "plannedMinutes": 50.0,
            "activeMinutes": minutes_value,
            "duration": minutes_value,
            "materialRole": "foundation",
            "startedAt": f"{(start + timedelta(days=index)).isoformat()}T08:00:00Z",
            "sessionId": f"projection-{index}",
        }
        for index, minutes_value in enumerate(minutes)
    ]


def test_gp_forecast_contains_true_finish_date_on_low_noise_learner():
    sessions = _sessions([50.0] * 10)
    forecast = forecast_gp_finish(
        sessions[:5],
        total_minutes=500.0,
        start_date="2026-03-01",
        horizon_end_date="2026-03-18",
    )
    metrics = projection_metrics([forecast], true_finish_date="2026-03-10")

    assert metrics["coverage"] == 1.0
    assert metrics["mean_abs_error_days"] <= 2.0
    assert metrics["mean_sharpness_days"] > 0.0


def test_linear_baseline_interval_is_discriminating_not_fixed_to_nominal():
    sessions = _sessions([35.0, 45.0, 50.0, 65.0, 85.0, 110.0])
    forecasts = [
        forecast_linear_finish(sessions[:t], total_minutes=390.0)
        for t in [3, 4, 5, 6]
    ]
    metrics = projection_metrics(forecasts, true_finish_date="2026-03-06")

    assert 0.0 <= metrics["coverage"] <= 1.0
    assert abs(metrics["coverage"] - 0.95) > 0.01


def test_projection_runner_reports_coverage_sharpness_and_error():
    sessions = _sessions([50.0] * 12)
    learner = {
        "learner_id": "projection-fixture",
        "band": "small",
        "archetype": "steady",
        "seed": 9,
        "sessions": sessions,
    }
    truth = {
        "true_finish_date": "2026-03-10",
        "r_star": [1.0] * len(sessions),
    }

    rows, forecasts = run_projection_for_learner(learner, truth, t_grid=[5, 8])

    assert rows
    assert forecasts
    assert all(0.0 <= row["coverage"] <= 1.0 for row in rows)
    assert all(row["mean_sharpness_days"] > 0.0 for row in rows)
    assert all(row["mean_abs_error_days"] >= 0.0 for row in rows)


def test_a1_projection_candidates_are_registered_without_removing_gp_incumbent():
    names = {candidate.name for candidate in projection_candidates()}

    assert {"gp_ard", "conformal", "gp_hetero_t"}.issubset(names)


def test_conformal_quantile_math_matches_finite_sample_rank():
    assert conformal_abs_residual_quantile([1.0, 2.0, 3.0, 4.0], alpha=0.25) == 4.0
    assert conformal_abs_residual_quantile([1.0, 2.0, 3.0, 4.0], alpha=0.40) == 3.0


def test_default_gp_path_matches_explicit_gaussian_no_ar1():
    train_x = [0.0, 1.0, 2.0, 3.0]
    train_y = [0.0, 50.0, 103.0, 151.0]
    test_x = [4.0, 5.0]

    assert gp_regression(train_x, train_y, test_x) == gp_regression(
        train_x,
        train_y,
        test_x,
        likelihood="gaussian",
        ar1=False,
    )


def test_a1_projection_results_show_conformal_coverage_on_medium_and_max_bands():
    results_path = REPO_ROOT / "research/results/projection/projection_results.json"
    payload = json.loads(results_path.read_text(encoding="utf-8"))

    coverage_by_band = {
        band: values["candidates"]["conformal"]["coverage"]
        for band, values in payload["winner_by_band"].items()
        if band in {"medium", "max"}
    }

    assert set(coverage_by_band) == {"medium", "max"}
    assert all(0.90 <= coverage <= 0.97 for coverage in coverage_by_band.values())
