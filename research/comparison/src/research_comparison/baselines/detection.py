from __future__ import annotations

import math
import statistics


def _mean(values: list[float]) -> float:
    return float(statistics.fmean(values)) if values else math.nan


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.05
    value = float(statistics.stdev(values))
    return value if value > 1e-6 else 0.05


def _lag1_autocorrelation(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    mean = _mean(values)
    numerator = sum((left - mean) * (right - mean) for left, right in zip(values, values[1:]))
    denominator = sum((value - mean) ** 2 for value in values)
    return 0.0 if denominator <= 1e-12 else float(numerator / denominator)


def detect_ewma(
    pace_ratios: list[float],
    reference_mean: float | None = None,
    std: float | None = None,
    alpha: float = 0.30,
    threshold: float = 2.5,
    min_gap: int = 4,
) -> list[int]:
    """EWMA control chart over pace ratios; returns breakpoint indices."""
    if len(pace_ratios) < 3:
        return []
    baseline_window = pace_ratios[: min(8, len(pace_ratios))]
    reference = _mean(baseline_window) if reference_mean is None else float(reference_mean)
    sigma = _std(baseline_window) if std is None else max(float(std), 0.05)
    sigma_ewma = sigma * math.sqrt(alpha / (2.0 - alpha))

    statistic = reference
    breakpoints: list[int] = []
    last_breakpoint = -min_gap
    for index, ratio in enumerate(pace_ratios):
        statistic = alpha * float(ratio) + (1.0 - alpha) * statistic
        if index - last_breakpoint < min_gap:
            continue
        if abs(statistic - reference) > threshold * sigma_ewma:
            breakpoints.append(index)
            last_breakpoint = index
            recent = pace_ratios[max(0, index - 5) : index + 1]
            reference = _mean(recent)
            statistic = reference
    return breakpoints


def detect_csd(
    pace_ratios: list[float],
    window: int = 8,
    threshold: float = 0.08,
    min_gap: int | None = None,
) -> list[int]:
    """Critical-slowing-down proxy using rising local mean/variance/autocorrelation."""
    if len(pace_ratios) < window * 2:
        return []
    gap = min_gap or window
    breakpoints: list[int] = []
    last_breakpoint = -gap
    for end in range(window * 2, len(pace_ratios) + 1):
        index = end - 1
        if index - last_breakpoint < gap:
            continue
        previous = pace_ratios[end - (window * 2) : end - window]
        current = pace_ratios[end - window : end]
        mean_delta = abs(_mean(current) - _mean(previous))
        previous_var = statistics.pvariance(previous)
        current_var = statistics.pvariance(current)
        variance_ratio = current_var / max(previous_var, 1e-6)
        autocorr_delta = _lag1_autocorrelation(current) - _lag1_autocorrelation(previous)
        if mean_delta >= threshold or variance_ratio >= 1.75 or autocorr_delta >= 0.25:
            breakpoints.append(index)
            last_breakpoint = index
    return breakpoints
