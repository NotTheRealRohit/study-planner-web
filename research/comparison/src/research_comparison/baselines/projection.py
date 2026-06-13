from __future__ import annotations

import math
import statistics
from datetime import date, timedelta
from typing import Any

from py_progress import fit_burn_up_gp, run_kalman_on_phase


def _parse(day: str) -> date:
    return date.fromisoformat(day)


def _date_to_index(day: str, start_date: str) -> int:
    return (_parse(day) - _parse(start_date)).days


def _index_to_date(index: float, start_date: str) -> str:
    return (_parse(start_date) + timedelta(days=round(index))).isoformat()


def _duration_minutes(session: dict[str, Any]) -> float:
    if session.get("source") == "active" and session.get("activeMinutes") is not None:
        return float(session["activeMinutes"])
    return float(session.get("duration") or 0.0)


def cumulative_points(sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cumulative = 0.0
    points: list[dict[str, Any]] = []
    for session in sessions:
        cumulative += _duration_minutes(session)
        points.append({"date": session["date"], "minutes": cumulative})
    return points


def _linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float, list[float]]:
    if len(xs) < 2:
        return 0.0, ys[0] if ys else 0.0, []
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    slope = (
        sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys, strict=True)) / denominator
        if denominator > 0
        else 0.0
    )
    intercept = y_mean - slope * x_mean
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys, strict=True)]
    return float(slope), float(intercept), residuals


def _finish_from_rate(
    total_minutes: float,
    start_date: str,
    slope: float,
    intercept: float,
    residuals: list[float],
    min_width_days: float,
) -> dict[str, Any]:
    safe_slope = max(slope, 1e-6)
    predicted_index = max(0.0, (total_minutes - intercept) / safe_slope)
    residual_std = statistics.stdev(residuals) if len(residuals) > 1 else safe_slope
    width_days = max(min_width_days, 1.96 * residual_std / safe_slope)
    return {
        "predicted_finish_date": _index_to_date(predicted_index, start_date),
        "interval_low": _index_to_date(max(0.0, predicted_index - width_days), start_date),
        "interval_high": _index_to_date(predicted_index + width_days, start_date),
        "sharpness_days": max(1.0, round(width_days * 2.0, 3)),
    }


def forecast_linear_finish(
    sessions: list[dict[str, Any]],
    total_minutes: float,
) -> dict[str, Any]:
    points = cumulative_points(sessions)
    if not points:
        today = date.today().isoformat()
        return {
            "candidate": "linear",
            "predicted_finish_date": today,
            "interval_low": today,
            "interval_high": today,
            "sharpness_days": 0.0,
        }
    start_date = points[0]["date"]
    xs = [_date_to_index(point["date"], start_date) for point in points]
    ys = [float(point["minutes"]) for point in points]
    slope, intercept, residuals = _linear_fit(xs, ys)
    return {
        "candidate": "linear",
        **_finish_from_rate(total_minutes, start_date, slope, intercept, residuals, 1.0),
    }


def _first_crossing(curve: list[dict[str, Any]], key: str, total_minutes: float) -> str:
    for point in curve:
        if float(point[key]) >= total_minutes:
            return str(point["date"])
    return str(curve[-1]["date"])


def forecast_gp_finish(
    sessions: list[dict[str, Any]],
    total_minutes: float,
    start_date: str | None = None,
    horizon_end_date: str | None = None,
) -> dict[str, Any]:
    points = cumulative_points(sessions)
    if not points:
        today = date.today().isoformat()
        return {
            "candidate": "gp_ard",
            "predicted_finish_date": today,
            "interval_low": today,
            "interval_high": today,
            "sharpness_days": 0.0,
        }
    start = start_date or points[0]["date"]
    today = points[-1]["date"]
    end = horizon_end_date or (_parse(today) + timedelta(days=90)).isoformat()
    curve = [point.__dict__ for point in fit_burn_up_gp(points, start, end, today)]
    predicted = _first_crossing(curve, "mean", total_minutes)
    low = _first_crossing(curve, "upper", total_minutes)
    high = _first_crossing(curve, "lower", total_minutes)
    return {
        "candidate": "gp_ard",
        "predicted_finish_date": predicted,
        "interval_low": min(low, high),
        "interval_high": max(low, high),
        "sharpness_days": max(1.0, (_parse(max(low, high)) - _parse(min(low, high))).days),
    }


def forecast_kalman_finish(
    sessions: list[dict[str, Any]],
    total_minutes: float,
) -> dict[str, Any]:
    points = cumulative_points(sessions)
    if not points:
        today = date.today().isoformat()
        return {
            "candidate": "kalman",
            "predicted_finish_date": today,
            "interval_low": today,
            "interval_high": today,
            "sharpness_days": 0.0,
        }
    start_date = points[0]["date"]
    xs = [_date_to_index(point["date"], start_date) for point in points]
    ys = [float(point["minutes"]) for point in points]
    increments = [ys[0], *[right - left for left, right in zip(ys, ys[1:])]]
    initial = statistics.fmean(increments[: min(3, len(increments))])
    result = run_kalman_on_phase(increments, initial, 0.20, 0.05)
    slope = max(result.finalLevel + result.finalSlope, 1e-6)
    intercept = ys[-1] - slope * xs[-1]
    uncertainty_minutes = max(result.levelUncertainty * 20.0, 10.0)
    width_days = max(1.0, 1.96 * uncertainty_minutes / slope)
    predicted_index = max(xs[-1], (total_minutes - intercept) / slope)
    return {
        "candidate": "kalman",
        "predicted_finish_date": _index_to_date(predicted_index, start_date),
        "interval_low": _index_to_date(max(xs[-1], predicted_index - width_days), start_date),
        "interval_high": _index_to_date(predicted_index + width_days, start_date),
        "sharpness_days": max(1.0, round(width_days * 2.0, 3)),
    }
