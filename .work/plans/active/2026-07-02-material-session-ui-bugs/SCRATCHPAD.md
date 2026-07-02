# Scratchpad - material-session-ui-bugs

_Plan: PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-02T21:33_

## Now
Phase 5 is implemented and awaiting review.
The plan has no Phase 6, so the requested Phase 6 was handled as a pre-review final-gate probe.
Current work for this session is complete.

## Alignment
Still aligned with the plan.
Phases 1-4 are implemented and awaiting reviewer pass.
Rohit explicitly asked to start Phases 5 and 6, so this session proceeds into Phase 5 despite the previous scratchpad's reviewer-pass next action.
`PLAN.md` has only Phases 1-5 plus a final gate.
The requested Phase 6 is interpreted as the final gate after Phase 5 unless a separate Phase 6 plan appears.
Phase 5 prereq greps matched the expected legacy burn-up implementation.
`pnpm --filter @study-tracker/progress test` passed before Phase 5 edits.
The Phase 5 red tests failed for the intended reasons, then passed after the implementation.
Focused verification passed: progress test suite, app typecheck, and `BurnUpChart Week` app tests.
The pre-review final gate passed: lint exits 0 with pre-existing warnings, full typecheck passed, app tests passed, and progress tests passed.
Browser visual inspection found and fixed an overly dense y-axis tick design from the plan's sample helper.
The final browser probe of `/study/chart-test` showed sparse unique visible y labels and a nonblank 798x280 chart.
No event model, intelligence math, routing basename, or Python code is in scope.
Unrelated dirty rule/doc files and `_perm_test.txt` are present before this session and must not be touched or staged.

## Open
- Reviewer still needs to pass Phases 1-5.
- Authenticated Week real-data visual confirmation remains for reviewer or a capable E2E pass.

## Blockers
- none

## Deferrals
- BUG-4d: back-to-`/roadmaps` exit for re-entrant onboarding remains deferred.
  Trigger: picking up re-entrant onboarding UX work.
- Cleaner `.modal-overlay` and `.modal-card` consolidation remains deferred.
  Trigger: a follow-up modal consistency pass after the targeted `.bk-*` fix.
- Full Phase-5-port responsive-rule sweep remains deferred.
  Trigger: broader roadmap CSS audit, not this targeted burn-up fix.

## Checklist
- [x] Read `.work/README.md` and `.work/STATUS.md`.
- [x] Read `PLAN.md`, `VERIFICATION.md`, and this scratchpad.
- [x] Read applicable local rules: `css-workspace-packages`, `form-design-spacing`, `roadmap-engine`, `playwright-config`, `playwright-full-app-lifecycle`, and `dexie-test-setup`.
- [x] Consult code memory and global memory for the material-session workflow.
- [x] Confirm the plan has no Phase 6 section.
- [x] Run Phase 5 prereq greps.
- [x] Run Phase 5 baseline `pnpm --filter @study-tracker/progress test`.
- [x] Mark Phase 5 in progress in `PLAN.md` and `VERIFICATION.md`.
- [x] Add progress-package tests for capacity-based planned baseline, fallback, and deficit.
- [x] Implement capacity-based planned baseline and burn-up domain hints.
- [x] Add app chart helper tests and empty-state coverage.
- [x] Implement BurnUpChart helper exports, deterministic ticks, guarded domains, y-domain bounding, monotone GP curves, and empty state.
- [x] Run Phase 5 verification commands.
- [x] Fill Phase 5 implementer report.
- [x] Run final gate checks as the Phase-6-like step requested by Rohit.
- [x] Update `.work/STATUS.md` through work-journal.
- [x] Commit scoped Phase 5 code and `.work` updates.
- [x] Commit scoped docs follow-up with the recorded Phase 5 SHA.

## In-flight edits
- none.
  Phase 5 implementation is committed in `256616b`.
  The `.work` SHA recording is committed in the current docs follow-up.

## Decisions in force
- D-05: keep burn-up rendering client-side.
- D-05: planned burn-up baseline mirrors booking capacity by selected study day, using full weekday/weekend hours per selected day.
- D-05: do not use legacy slot-grid splitting for the fixed product burn-up chart.
- `BurnUpData.startDate` and `BurnUpData.deadline` remain optional.
- Week's low-data gate stays in place.
- E2E specs may be authored but not run.
- Reuse existing Marginalia palette and chart restraint; spend the UI change on clarity, not a new visual identity.
- Design deviation in force: high-range tick values target roughly six readable intervals rather than the plan's literal 2h step for large domains.
- Do not touch unrelated dirty rule/doc files or `_perm_test.txt`.

## Resolved (recent)
- Planning handoff state superseded by implementation state for Phase 1 and Phase 2.
- Phase 1 verification passed and commit `0268f20` exists.
- Phase 2 verification passed and commit `0268f20` exists.
- Phase 3 verification passed and commit `3c8d869` exists.
- Phase 4 verification passed and commit `3c8d869` exists.
- Phase 5 prereq verification passed before edits.
- Phase 5 focused verification passed after implementation.
- Final-gate probe passed after the tick-density visual fix.
- Scoped Phase 5 implementation commit created: `256616b`.
- Scoped `.work` docs follow-up committed after recording `256616b`.
