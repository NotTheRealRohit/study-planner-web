from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

import numpy as np
from py_progress import (
    BAYESIAN_PRIOR_MEAN,
    BAYESIAN_PRIOR_VARIANCE,
    compute_hierarchical_model,
    infer_day_of_week,
    infer_time_of_day,
)


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
class CalibrationObservation:
    ratio: float
    role: str
    time_of_day: str
    day_of_week: str


@dataclass(frozen=True)
class CovariateEffectFit:
    global_multiplier: float
    role_multipliers: dict[str, float]
    time_multipliers: dict[str, float]
    day_multipliers: dict[str, float]
    residual_variance: float
    session_count: int


def _active_observations(sessions: list[dict]) -> list[CalibrationObservation]:
    observations: list[CalibrationObservation] = []
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
            started_at = session.get("startedAt") or session.get("date")
            observations.append(
                CalibrationObservation(
                    ratio=float(active) / float(planned),
                    role=str(session.get("materialRole") or "foundation"),
                    time_of_day=infer_time_of_day(started_at),
                    day_of_week=infer_day_of_week(started_at),
                )
            )
    return observations


def _safe_log(value: float) -> float:
    return math.log(max(value, 1e-9))


def _posterior_interval(
    center: float,
    residual_variance: float,
    n: int,
) -> tuple[float, float] | None:
    if n < 1:
        return None
    se = math.sqrt(max(residual_variance, 0.001) / max(1, n))
    log_center = _safe_log(center)
    return (
        float(math.exp(log_center - 1.96 * se)),
        float(math.exp(log_center + 1.96 * se)),
    )


def _sample_variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return float(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def _eb_effects(
    values_by_group: dict[str, list[float]],
    global_mean: float,
    fallback_variance: float,
) -> dict[str, float]:
    if not values_by_group:
        return {}
    group_means = {
        group: sum(values) / len(values)
        for group, values in values_by_group.items()
    }
    tau_sq = _sample_variance(list(group_means.values()))
    effects: dict[str, float] = {}
    for group, values in values_by_group.items():
        n = len(values)
        sigma_sq = _sample_variance(values) if n > 1 else fallback_variance
        denominator = tau_sq + sigma_sq / max(1, n)
        weight = tau_sq / denominator if denominator > 0 else 0.0
        effects[group] = float(weight * (group_means[group] - global_mean))
    return effects


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


@dataclass(frozen=True)
class CovariateBayesCalibrator:
    ridge: float = 1.0
    name: str = "covariate_bayes"

    def fit_effects(self, sessions: list[dict]) -> CovariateEffectFit:
        observations = _active_observations(sessions)
        if not observations:
            return CovariateEffectFit(
                global_multiplier=BAYESIAN_PRIOR_MEAN,
                role_multipliers={},
                time_multipliers={},
                day_multipliers={},
                residual_variance=BAYESIAN_PRIOR_VARIANCE,
                session_count=0,
            )

        rows: list[list[float]] = []
        targets: list[float] = []
        for observation in observations:
            rows.append(
                [
                    1.0,
                    1.0 if observation.role == "anchor" else 0.0,
                    1.0 if observation.role == "practice" else 0.0,
                    1.0 if observation.time_of_day == "morning" else 0.0,
                    1.0 if observation.time_of_day == "evening" else 0.0,
                    1.0 if observation.day_of_week == "weekend" else 0.0,
                ]
            )
            targets.append(_safe_log(observation.ratio))

        x = np.asarray(rows, dtype=float)
        y = np.asarray(targets, dtype=float)
        penalty = np.diag(
            [0.0, self.ridge, self.ridge, self.ridge, self.ridge, self.ridge]
        )
        beta = np.linalg.solve(x.T @ x + penalty, x.T @ y)
        residuals = y - x @ beta
        residual_variance = (
            float(np.var(residuals, ddof=1))
            if len(residuals) > 1
            else BAYESIAN_PRIOR_VARIANCE
        )
        return CovariateEffectFit(
            global_multiplier=float(math.exp(beta[0])),
            role_multipliers={
                "foundation": 1.0,
                "anchor": float(math.exp(beta[1])),
                "practice": float(math.exp(beta[2])),
            },
            time_multipliers={
                "afternoon": 1.0,
                "morning": float(math.exp(beta[3])),
                "evening": float(math.exp(beta[4])),
            },
            day_multipliers={
                "weekday": 1.0,
                "weekend": float(math.exp(beta[5])),
            },
            residual_variance=max(residual_variance, 0.001),
            session_count=len(observations),
        )

    def fit_global(self, sessions: list[dict]) -> float:
        return self.fit_effects(sessions).global_multiplier

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None:
        fit = self.fit_effects(sessions)
        return _posterior_interval(
            fit.global_multiplier,
            fit.residual_variance,
            fit.session_count,
        )


@dataclass(frozen=True)
class EBPartialPoolCalibrator:
    name: str = "eb_partial_pool"

    def fit_effects(self, sessions: list[dict]) -> CovariateEffectFit:
        observations = _active_observations(sessions)
        if not observations:
            return CovariateEffectFit(
                global_multiplier=BAYESIAN_PRIOR_MEAN,
                role_multipliers={},
                time_multipliers={},
                day_multipliers={},
                residual_variance=BAYESIAN_PRIOR_VARIANCE,
                session_count=0,
            )

        log_ratios = [_safe_log(observation.ratio) for observation in observations]
        global_log = sum(log_ratios) / len(log_ratios)
        fallback_variance = max(_sample_variance(log_ratios), 0.001)

        role_values: dict[str, list[float]] = {}
        for observation, log_ratio in zip(observations, log_ratios, strict=True):
            role_values.setdefault(observation.role, []).append(log_ratio)
        role_effects = _eb_effects(role_values, global_log, fallback_variance)

        role_adjusted = [
            log_ratio - role_effects.get(observation.role, 0.0)
            for observation, log_ratio in zip(observations, log_ratios, strict=True)
        ]
        role_adjusted_mean = sum(role_adjusted) / len(role_adjusted)
        time_values: dict[str, list[float]] = {}
        for observation, adjusted in zip(observations, role_adjusted, strict=True):
            time_values.setdefault(observation.time_of_day, []).append(adjusted)
        time_effects = _eb_effects(time_values, role_adjusted_mean, fallback_variance)

        time_adjusted = [
            adjusted - time_effects.get(observation.time_of_day, 0.0)
            for observation, adjusted in zip(observations, role_adjusted, strict=True)
        ]
        time_adjusted_mean = sum(time_adjusted) / len(time_adjusted)
        day_values: dict[str, list[float]] = {}
        for observation, adjusted in zip(observations, time_adjusted, strict=True):
            day_values.setdefault(observation.day_of_week, []).append(adjusted)
        day_effects = _eb_effects(day_values, time_adjusted_mean, fallback_variance)

        decontextualized = [
            log_ratio
            - role_effects.get(observation.role, 0.0)
            - time_effects.get(observation.time_of_day, 0.0)
            - day_effects.get(observation.day_of_week, 0.0)
            for observation, log_ratio in zip(observations, log_ratios, strict=True)
        ]
        global_estimate = sum(decontextualized) / len(decontextualized)
        residuals = [
            log_ratio
            - global_estimate
            - role_effects.get(observation.role, 0.0)
            - time_effects.get(observation.time_of_day, 0.0)
            - day_effects.get(observation.day_of_week, 0.0)
            for observation, log_ratio in zip(observations, log_ratios, strict=True)
        ]
        residual_variance = max(_sample_variance(residuals), 0.001)
        return CovariateEffectFit(
            global_multiplier=float(math.exp(global_estimate)),
            role_multipliers={
                role: float(math.exp(effect)) for role, effect in role_effects.items()
            },
            time_multipliers={
                time: float(math.exp(effect)) for time, effect in time_effects.items()
            },
            day_multipliers={
                day: float(math.exp(effect)) for day, effect in day_effects.items()
            },
            residual_variance=residual_variance,
            session_count=len(observations),
        )

    def fit_global(self, sessions: list[dict]) -> float:
        return self.fit_effects(sessions).global_multiplier

    def fit_interval(self, sessions: list[dict]) -> tuple[float, float] | None:
        fit = self.fit_effects(sessions)
        return _posterior_interval(
            fit.global_multiplier,
            fit.residual_variance,
            fit.session_count,
        )


def calibration_candidates() -> list[CalibrationCandidate]:
    return [
        IncumbentCalibration(),
        CovariateBayesCalibrator(),
        EBPartialPoolCalibrator(),
        SMACalibrator(),
        EWMACalibrator(),
        PooledBayesianCalibrator(),
    ]
