from __future__ import annotations

from research_comparison.baselines.calibration import CalibrationCandidate


def prequential_absolute_errors(
    sessions: list[dict],
    candidate: CalibrationCandidate,
    targets: list[float],
    t_grid: list[int],
) -> list[float]:
    errors: list[float] = []
    for t in t_grid:
        if t >= len(sessions):
            continue
        estimate = candidate.fit_global(sessions[:t])
        errors.append(abs(estimate - targets[t]))
    return errors
