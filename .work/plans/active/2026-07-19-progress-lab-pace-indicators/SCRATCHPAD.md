# Scratchpad - 2026-07-19-progress-lab-pace-indicators

_Plan: `.work/plans/active/2026-07-19-progress-lab-pace-indicators/PLAN.md` | Log: `VERIFICATION.md` | Updated: 2026-07-19T08:33+0530_

## Now

Phase 1 is implemented and self-verified.
Phase 2 is next, beginning with pure step and linear interpolation helpers before the mouse-only chart overlay.

## Alignment

The user-authorized batch sequence overrides the handoff's pause-for-review cadence.
All four implementation phases remain in plan order, with reviewer sections left unclaimed.

## Open

- None.

## Blockers

- None.

## Deferrals

- The projection-inconsistency task has dangling PLAN, VERIFICATION, and DIAGNOSIS references.
  It is explicitly non-blocking and must not be modified by this task.
- Independent reviewer verification and archiving remain after self-verification.

## Checklist

- [x] Commit initial task documentation and completed mock.
- [x] Make the Home projected-finish test deterministic and prove the complete app suite is green.
- [x] Implement and self-verify Phase 1 finish markers and goal line.
  - [x] Extend only the full-plan domain for supplied finishes with right-edge padding.
  - [x] Clip planned and scenario trajectories at completion.
  - [x] Render the goal line, done zone, flags, and GP connector safely.
  - [x] Add GP forecast and Your pace legend entries.
- [ ] Implement and self-verify Phase 2 crosshair.
- [ ] Implement and self-verify Phase 3 finish narrative and Week wiring.
- [ ] Implement and self-verify Phase 4 E2E coverage and screenshots.
- [ ] Run final full verification and protected-file checks.

## In-flight edits

- Phase 1 chart source, tests, dev harness, and journal updates are ready for the feature commit.
- `college/mydeliverables/phase1-ESA/design/phase1-esa-deck.html` is an unrelated user change and must remain unstaged.

## Decisions in force

- Option X is authoritative.
  The existing GP projection owns the forecast while capacity scenario finish math stays unchanged.
- `forecastBasis` belongs in the modal narrative only, not in `BurnUpPlot`.
- Historical mode receives deadline and total so the goal line and Plan flag remain visible.
  Forecast and scenario data remain withheld.
- Focused Vitest checks use direct file paths.
- Phase 4 screenshots live in this task's `screenshots/` directory.
- Do not modify protected capacity scenario, Replan, or package files.

## Resolved (recent)

- The expected dirty tree was confirmed.
  Task documentation is the intended initial commit, and the dissertation deck remains unrelated.
- Documentation baseline committed at `959ccb9`.
- The Home test failure was reproduced on 2026-07-19 because the projected finish rendered as `Tomorrow`.
  A local frozen clock restored the intended `Jul 20` assertion, and the complete app suite passed 555 tests.
- Phase 1 passed 33 focused tests across the chart and protected Replan surfaces, plus app typecheck.
  Protected source and test diffs remained empty.
