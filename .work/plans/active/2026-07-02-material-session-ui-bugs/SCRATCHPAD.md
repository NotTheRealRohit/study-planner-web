# Scratchpad - material-session-ui-bugs

_Plan: PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-02T20:39_

## Now
Phase 1 and Phase 2 are implemented and awaiting reviewer pass.
The current work is final hygiene: commit the scoped files and report the result.

## Alignment
Still aligned with the plan.
The planning bundle is already committed in `754efa9`, satisfying the plan's Step 0 baseline.
The phase prereq greps matched current source before editing.
All plan-scoped Phase 1 and Phase 2 verification checks passed.
No event model, intelligence math, routing basename, or Python code is in scope.

## Open
- Commit recording detail: final commit SHA is not known until after commit creation.
  `VERIFICATION.md` currently records this as pending session commit.

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
- [ ] Commit scoped Phase 1 and Phase 2 files.

## In-flight edits
- `apps/app/src/pages/Roadmaps.tsx`: duplicate `Edit & add` link removed and verified.
- `apps/app/src/pages/Roadmaps.test.tsx`: duplicate-link assertion removed and suite verified.
- `apps/app/src/roadmap/roadmap.css`: `.bk-overlay` centered, `.bk-sheet` made rounded and scroll-guarded, `.bk-grip` hidden and visually checked.
- `.work/plans/active/2026-07-02-material-session-ui-bugs/PLAN.md`: Phase 1 and Phase 2 status and notes updated.
- `.work/plans/active/2026-07-02-material-session-ui-bugs/VERIFICATION.md`: Phase 1 and Phase 2 reports filled, reviewer findings pending.
- `.work/STATUS.md`: active row updated through work-journal.

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
