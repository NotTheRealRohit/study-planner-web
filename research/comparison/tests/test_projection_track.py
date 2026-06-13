from __future__ import annotations

from datetime import date, timedelta

from research_comparison.baselines.projection import forecast_gp_finish, forecast_linear_finish
from research_comparison.metrics.projection import projection_metrics
from research_comparison.runners.projection import run_projection_for_learner


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
