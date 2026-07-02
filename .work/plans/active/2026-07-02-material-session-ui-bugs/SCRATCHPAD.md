# Scratchpad - material-session-ui-bugs

_Plan: PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-02T20:39_

## Now
Phase 1 and Phase 2 are implemented and awaiting reviewer pass.
Implementation commit `0268f20` and journal update commit `5c5ba44` are complete.
Next action is reviewer pass on Phases 1-2, then Phase 3.

## Alignment
Still aligned with the plan.
The planning bundle is already committed in `754efa9`, satisfying the plan's Step 0 baseline.
The phase prereq greps matched current source before editing.
All plan-scoped Phase 1 and Phase 2 verification checks passed.
No event model, intelligence math, routing basename, or Python code is in scope.

## Open
- none

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
- [x] Read applicable local rules: `css-workspace-packages`, `form-design-spacing`, `react-router-v7-basename`, `roadmap-engine`, and `pnpm-build-registry`.
- [x] Consult code memory and global memory for the material-session workflow.
- [x] Run Phase 1 prereq greps.
- [x] Run Phase 2 prereq greps.
- [x] Mark Phase 1 and Phase 2 in progress in `VERIFICATION.md`.
- [x] Remove duplicate `Edit & add` link and assertion.
- [x] Center `.bk-*` booking sheets with existing Marginalia tokens.
- [x] Run Phase 1 done greps and `Roadmaps` test.
- [x] Run Phase 2 done greps and app typecheck.
- [x] Perform focused Playwright geometry check with real CSS.
- [x] Fill Phase 1 and Phase 2 implementer reports.
- [x] Update `.work/STATUS.md` through work-journal.
- [x] Commit scoped Phase 1 and Phase 2 files.

## In-flight edits
- none.
  Phase 1 and Phase 2 code changes are committed in `0268f20`; `.work` SHA correction is committed in `5c5ba44`.

## Decisions in force
- D-01: keep one `Open plan` action in the Roadmaps hero.
- D-02: booking sheets are centered on all viewports, not just desktop.
- Reuse existing Marginalia tokens and local CSS conventions.
- Do not implement Phase 3, Phase 4, or Phase 5 in this pass.
- Do not touch `_perm_test.txt`; it is unrelated dirty work.

## Resolved (recent)
- Planning handoff state superseded by implementation state for Phase 1 and Phase 2.
- Phase prereqs confirmed: both duplicate links were present, and `.bk-overlay` used `align-items: flex-end`.
- Phase 1 verification passed: duplicate link removed, focused test command passed, app typecheck passed.
- Phase 2 verification passed: CSS guards present, focused browser geometry check passed, app typecheck passed.
- Scoped implementation commit created: `0268f20`.
