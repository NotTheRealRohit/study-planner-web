from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

from py_progress import BAYESIAN_PRIOR_MEAN, BAYESIAN_PRIOR_VARIANCE, compute_hierarchical_model


class CalibrationCandidate(Protocol):
    name: str

    def fit_global(self, sessions: list[dict]) -> float: ...

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None: ...


def active_ratios(sessions: list[dict]) -> list[float]:
    ratios: list[float] = []
    for session in sessions:
        planned = session.get("plannedMinutes")
        active = session.get("activeMinutes")
        if (
            session.get("source") == "active"
            and planned is not None
            and active is not None
            and planned > 0
            and active > 0
        ):
            ratios.append(float(active) / float(planned))
    return ratios


def empirical_variance(values: list[float]) -> float:
    if len(values) < 2:
        return BAYESIAN_PRIOR_VARIANCE
    mean = sum(values) / len(values)
    return max(sum((value - mean) ** 2 for value in values) / (len(values) - 1), 0.001)


@dataclass(frozen=True)
class IncumbentCalibration:
    name: str = "hierarchical_bayes"

    def fit_global(self, sessions: list[dict]) -> float:
        return float(compute_hierarchical_model(sessions, set()).globalPosterior.mean)

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None:
        posterior = compute_hierarchical_model(sessions, set()).globalPosterior
        radius = 1.96 * math.sqrt(posterior.variance)
        return (float(posterior.mean - radius), float(posterior.mean + radius))


@dataclass(frozen=True)
class SMACalibrator:
    window: int = 8
    name: str = "sma"

    def fit_global(self, sessions: list[dict]) -> float:
        ratios = active_ratios(sessions)
        if not ratios:
            return BAYESIAN_PRIOR_MEAN
        return float(sum(ratios[-self.window :]) / len(ratios[-self.window :]))

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None:
        ratios = active_ratios(sessions)
        if not ratios:
            return None
        mean = self.fit_global(sessions)
        radius = 1.96 * math.sqrt(empirical_variance(ratios[-self.window :]))
        return (mean - radius, mean + radius)


@dataclass(frozen=True)
class EWMACalibrator:
    alpha: float = 0.35
    name: str = "ewma"

    def fit_global(self, sessions: list[dict]) -> float:
        estimate = BAYESIAN_PRIOR_MEAN
        for ratio in active_ratios(sessions):
            estimate = self.alpha * ratio + (1.0 - self.alpha) * estimate
        return float(estimate)

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None:
        ratios = active_ratios(sessions)
        if not ratios:
            return None
        mean = self.fit_global(sessions)
        radius = 1.96 * math.sqrt(empirical_variance(ratios))
        return (mean - radius, mean + radius)


@dataclass(frozen=True)
class PooledBayesianCalibrator:
    name: str = "pooled_bayes"

    def fit_global(self, sessions: list[dict]) -> float:
        ratios = active_ratios(sessions)
        if not ratios:
            return BAYESIAN_PRIOR_MEAN
        variance = empirical_variance(ratios)
        precision = 1.0 / BAYESIAN_PRIOR_VARIANCE + len(ratios) / variance
        weighted = BAYESIAN_PRIOR_MEAN / BAYESIAN_PRIOR_VARIANCE + sum(ratios) / variance
        return float(weighted / precision)

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None:
        ratios = active_ratios(sessions)
        if not ratios:
            return None
        variance = empirical_variance(ratios)
        posterior_variance = 1.0 / (1.0 / BAYESIAN_PRIOR_VARIANCE + len(ratios) / variance)
        mean = self.fit_global(sessions)
        radius = 1.96 * math.sqrt(posterior_variance)
        return (mean - radius, mean + radius)


def calibration_candidates() -> list[CalibrationCandidate]:
    return [
        IncumbentCalibration(),
        SMACalibrator(),
        EWMACalibrator(),
        PooledBayesianCalibrator(),
    ]
