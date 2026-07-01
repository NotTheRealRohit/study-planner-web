# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-01T14:18_

## Now
Phase 5 (Roadmap booking calendar + materials directory + booking interactions) and Phase 6 (ETA composite + Week wiring) are implemented locally and awaiting Cowork review. `PLAN.md` and `VERIFICATION.md` now mark both phases as implemented locally, not verified.

## Alignment
Aligned with the active plan for Phase 5/6. Deviations are explicitly logged in `VERIFICATION.md`: booking sheets use native select/date controls instead of the full grouped directory picker; direct Python subprocess parity was not added for ETA because the product-specific TS contract differs from the research helper's no-evidence/elapsed-day convention; an unrelated random CUSUM test fixture was seeded for stable package verification.

## Open
- Cowork review still needed for Phase 5/6.
- D6 pace-first pre-session recommendation nudge remains open from the Phase 3/4 follow-up. Phase 6 wired ETA/projection and Week capacity target; `PreSessionSetup` still recommends booking target clamped to the D5 soft cap.

## Blockers
- — none active.

## Deferrals
- `/v1/progress` parity remains deferred by PLAN OQ-01; Phase 6 intentionally ships the local TS progress path only.
- E2E execution remains author-only/not-run per project rule; Playwright discovery/listing passed.
- Full Replan slot-path retirement remains Phase 7, not part of this Phase 5/6 pass.
- Grouped material picker reuse in booking sheets is deferred as UI polish; event semantics and "No material · pick at start" are implemented.

## Checklist
- [x] Read project-local `scratchpad`, `work-journal`, `frontend-design`, `code-memory`, and `plan-implementor` skills.
- [x] Read `.work/README.md`, `.work/STATUS.md`, `PLAN.md`, `VERIFICATION.md`, `DECISIONS.md`, and applicable local rules.
- [x] Confirm partial Phase 5/6 worktree state after resume.
- [x] Implement Phase 5 calendar model/status styles/RoadmapCalendar booking path.
- [x] Implement Phase 5 booking editor/add-session/material progress interactions.
- [x] Add/update Phase 5 unit tests and author Playwright coverage.
- [x] Implement Phase 6 `projectFinish` and progress projection wiring.
- [x] Wire provisional ETA labels and Week capacity target.
- [x] Run focused verification: app typecheck, RoadmapCalendar/calendarModel tests, progress tests, Home/Week tests, workspace typecheck, Playwright listing, git diff check.
- [x] Update `PLAN.md`, `VERIFICATION.md`, `.work/STATUS.md`, and this scratchpad with implementation/deviations.

## In-flight edits
- Roadmap page now uses booking statuses, booking/action sheets, material directory, and provisional ETA card.
- Progress package now has `projectFinish` and projection `basis`/`provisional`; app progress input carries material total/remaining and capacity fields.
- Home/Week/Roadmap show provisional finish copy; Week has a compact projected-finish card in the burn-up column.
- `e2e/material-session-decoupling.spec.ts` now includes author-only roadmap add/edit/remove booking coverage.

## Decisions in force
- Use project-local skills/rules only for this repo.
- `.work/plans/active/2026-06-30-material-session-decoupling/` is the active task unit; `VERIFICATION.md` is the running log.
- Preserve event sourcing: append `SessionBooked`/`BookingEdited`/`BookingCleared`/`MaterialProgressMarked`; no destructive migration.
- Material directory `Mark progress` emits `MaterialProgressMarked` only; it must not create `SessionLogged` or a calibration point.
- Phase 6 ETA is GP plus analytic fallback for cold-start/non-crossing, not a GP replacement; labels stay provisional and `/v1/progress` parity is deferred.
- Week target comes from capacity when capacity fields are available, not summed legacy slot minutes.

## Resolved (recent)
- Phase 3 and Phase 4 are reviewer-verified in `VERIFICATION.md`.
- Phase 5/6 compile/test failures from resume are resolved: `pnpm typecheck`, `pnpm --filter @study-tracker/progress test`, and focused app test filters are green.
- The unrelated flaky CUSUM stable-signal fixture is now deterministic.
