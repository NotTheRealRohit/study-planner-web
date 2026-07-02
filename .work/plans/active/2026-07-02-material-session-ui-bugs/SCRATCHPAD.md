# Scratchpad - material-session-ui-bugs

_Plan: PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-02T21:18_

## Now
Phase 3 and Phase 4 are implemented in code commit `3c8d869` and documented for reviewer pass.
Current work is complete for this handoff.
Next action is reviewer pass on Phases 1-4, then Phase 5.

## Alignment
Still aligned with the plan.
The planning bundle is already committed in `754efa9`, satisfying the plan's Step 0 baseline.
Phase 3 prereq greps matched current source.
Phase 4 prereq greps found the expected CSS and onboarding chip state, and confirmed `selectedStudyDays` in `Step3Preview`.
`RoadmapCalendar.tsx` currently omits `selectedStudyDays` from its local `roadmapInputFromPayload` adapter even though `RoadmapCreatedPayload` and `RoadmapInput` both carry the field.
Restoring that adapter field is treated as the planned `roadmap.selectedStudyDays` availability, not a design change.
No event model, intelligence math, routing basename, or Python code is in scope.

## Open
- Reviewer still needs to pass Phases 1-4.

## Blockers
- none

## Deferrals
- BUG-4d: back-to-`/roadmaps` exit for re-entrant onboarding remains deferred.
  Trigger: picking up Phase 4 or any re-entrant onboarding work.
- Cleaner `.modal-overlay` and `.modal-card` consolidation remains deferred.
  Trigger: a follow-up modal consistency pass after the targeted `.bk-*` fix.
- Full Phase-5-port responsive-rule sweep remains deferred.
  Trigger: broader roadmap CSS audit, not Phase 1 or Phase 2.

## Checklist
- [x] Read `.work/README.md` and `.work/STATUS.md`.
- [x] Read `PLAN.md`, `VERIFICATION.md`, and this scratchpad.
- [x] Read applicable local rules: `css-workspace-packages`, `form-design-spacing`, `roadmap-engine`, `playwright-config`, and `playwright-full-app-lifecycle`.
- [x] Consult code memory and global memory for the material-session workflow.
- [x] Run Phase 3 prereq greps.
- [x] Run Phase 4 prereq greps and inspect the `RoadmapCalendar` adapter drift.
- [x] Mark Phase 3 and Phase 4 in progress in `VERIFICATION.md`.
- [x] Implement Phase 3 mobile empty-day DaySheet add flow.
- [x] Implement Phase 4 study-day tint, legends, weekday headers, and onboarding booked chip.
- [x] Add or update unit tests for Phase 3 and Phase 4.
- [x] Author required Playwright cases without running E2E.
- [x] Run plan-required Vitest/typecheck commands.
- [x] Fill Phase 3 and Phase 4 implementer reports.
- [x] Update `.work/STATUS.md` through work-journal.
- [x] Commit `.work` journal updates.

## In-flight edits
- none.
  Code/test/E2E changes are committed in `3c8d869`.
  `.work` journal updates are committed in the current docs commit.

## Decisions in force
- D-03: compact calendar empty in-month days open `DaySheet`, and `DaySheet` owns the mobile add-session action.
- D-04: study-day tint applies to all calendars, but only in-month cells get tinted.
- D-04: onboarding preview uses booked styling, tooltips, a study-day legend, and no read-only hover lift.
- Reuse existing Marginalia tokens and local CSS conventions.
- Do not implement Phase 5 in this pass.
- Do not touch `_perm_test.txt`; it is unrelated dirty work.

## Resolved (recent)
- Planning handoff state superseded by implementation state for Phase 1 and Phase 2.
- Phase prereqs confirmed: both duplicate links were present, and `.bk-overlay` used `align-items: flex-end`.
- Phase 1 verification passed: duplicate link removed, focused test command passed, app typecheck passed.
- Phase 2 verification passed: CSS guards present, focused browser geometry check passed, app typecheck passed.
- Scoped implementation commit created: `0268f20`.
- Phase 3 prereqs confirmed: compact cell gating, view-only DaySheet, and existing AddSessionSheet state are present.
- Phase 4 adapter drift resolved as an implementation note: payload/type support exists, but `RoadmapCalendar` currently drops the fields locally.
- Phase 3 verification passed: `onAddSession` greps, app typecheck, and focused app test command.
- Phase 4 verification passed: `roadmap-day-studyday` greps, `roadmap-chip-booked` grep, app typecheck, and focused app test command.
