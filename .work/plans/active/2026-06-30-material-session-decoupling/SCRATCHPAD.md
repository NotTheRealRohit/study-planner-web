# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-01T12:49_

## Now
Phase 3 and Phase 4 are implemented locally and focused verification is green. They are deliberately left awaiting reviewer sign-off in `VERIFICATION.md` / `PLAN.md`; do not self-mark them verified.

## Alignment
Aligned with the active plan. Phase 2 is now reflected as reviewer-verified in `VERIFICATION.md`; Phase 3/4 are implementation-complete pending Cowork review.

## Open
- Reviewer should inspect fidelity gaps called out in `VERIFICATION.md`: group headers not collapsible; pre-session dial is range-backed rather than full SVG radial/cap math; YouTube auto-position capture is not implemented.
- Commit boundary remains undecided in-session; preserve pre-existing dirty docs/untracked archive unless staging later.

## Blockers
- — none active.

## Deferrals
- Leave `/v1/progress` service parity deferred by the plan; this session is not implementing ETA composite/server parity.
- Leave the pre-existing untracked `.work/plans/active/2026-06-30-material-session-decoupling/archive/SCRATCHPAD.md` untouched unless the user asks for cleanup.

## Checklist
- [x] Read project-local `scratchpad`, `work-journal`, and `code-memory` skills.
- [x] Read `.work/README.md`, `.work/STATUS.md`, `PLAN.md`, `VERIFICATION.md`, `DECISIONS.md`, and the archived scratchpad.
- [x] Confirm planning baseline commit exists (`8c65b07`).
- [x] Read applicable local rules: `roadmap-engine`, `sync-architecture`, `eventstore-architecture`, `eventstore-per-user-db`, `pnpm-build-registry`.
- [x] Run Phase 1 prereq checks.
- [x] Implement Phase 1 engine bookings and event/session payload types.
- [x] Run Phase 1 focused verification.
- [x] Implement Phase 2 derivations, calibration denominator helper, and app mapping adapters.
- [x] Run Phase 2 focused verification.
- [x] Update `PLAN.md`, `VERIFICATION.md`, `.work/STATUS.md`, and this scratchpad with final state.
- [x] Commit Phase 1/2 implementation as `327ca45`.
- [x] Read Phase 2 reviewer changes-requested checklist.
- [x] Add no-slots `roadmapProgress.test.ts`.
- [x] Add no-slots `roadmapLifecycle.test.ts` coverage.
- [x] Run required Phase 2 redo verification.
- [x] Update `VERIFICATION.md`, `.work/STATUS.md`, and this scratchpad with redo result.
- [x] Read project-local plan-implementor, tdd, debug-session, frontend-design, code-memory, scratchpad, and work-journal skills.
- [x] Read `.work/README.md`, `.work/STATUS.md`, `PLAN.md`, `VERIFICATION.md`, `DECISIONS.md`, UI/research handovers, and Phase 3/4 mocks.
- [x] Read applicable local rules: onboarding architecture, form spacing, CSS workspace packages, React Router basename, sync/eventstore, Dexie tests, sync-provider tests, pnpm registry, roadmap engine, Playwright config.
- [x] Run Phase 3 prereq checks.
- [x] Implement Phase 3 onboarding page 3.
- [x] Verify Phase 3 (`pnpm --filter app typecheck`, `pnpm --filter app test -- onboarding`, authored Playwright as applicable).
- [x] Run Phase 4 prereq checks.
- [x] Implement Phase 4 Home/session flow.
- [x] Verify Phase 4 (`pnpm --filter app typecheck`, `pnpm --filter app test -- session`, authored Playwright as applicable).
- [x] Update `PLAN.md`, `VERIFICATION.md`, `.work/STATUS.md`, and this scratchpad with Phase 3/4 result.

## In-flight edits
- Phase 3 implemented: sync write path optional `createdAt`; `Step3Preview.tsx` booking summary/calendar/no-slot commit flow; `Step3Materials.tsx` grouped compact material sections with existing playlist modals; onboarding styles/tests updated.
- Phase 4 implemented: `sessionPlanning.ts`, Home suggested-material booking card, `/session` pre-session gate, `PreSessionSetup`, `EndSessionSheet`, lifecycle interrupt/material-consumed logging, stale-midnight auto-interrupt, and focused component/lifecycle tests.
- Authored Playwright coverage added in `e2e/material-session-decoupling.spec.ts`; discovery checked, not executed.
- Verification passed: `pnpm --filter app typecheck`; `pnpm --filter app test -- onboarding`; `pnpm --filter app test -- session`; `pnpm exec playwright test --config e2e/playwright.config.ts e2e/material-session-decoupling.spec.ts --list`; `git diff --check`; Phase 3/4 grep checks.
- Pre-existing tracked dirty change: `VERIFICATION.md` contains Cowork Phase 2 reviewer re-check; preserve.
- Pre-existing untracked folder: `.work/plans/active/2026-06-30-material-session-decoupling/archive/`; leave untouched unless wrapping the whole task.

## Decisions in force
- Use project-local skills/rules only for this repo.
- `.work/plans/active/2026-06-30-material-session-decoupling/` is the active task unit; `VERIFICATION.md` is the running log.
- Preserve pre-existing dirty/untracked `.work` state unless it directly blocks this task.
- Roadmap engine generated booking IDs must be deterministic; no random IDs in `@study-tracker/roadmap-engine`.
- Legacy slot APIs stay present and deprecated during Phases 1/2; no destructive event migration.
- Calibration denominator for decoupled material throughput is `materialConsumedMinutes ?? plannedMinutes`, not the pre-session dial target alone.
- The review miss was a verification-scope mistake: the package/mapEvents tests were green, but the app-level no-slots branches named in the Phase 2 Tests block were not covered.

## Resolved (recent)
- Active scratchpad deletion at session start resolved by recreating the task-local `SCRATCHPAD.md`; archived copy left untouched.
- Phase 1 app typecheck failure from optional `slots` resolved by Phase 2 no-slot bridge and minimal legacy compatibility guards.
- Implementation commit boundary resolved as `327ca45`.
- Phase 2 missing-test blocker addressed with `roadmapProgress.test.ts` and no-slots lifecycle coverage; verification passed: `pnpm --filter @study-tracker/progress test`, `pnpm --filter app test -- roadmapProgress roadmapLifecycle`, `pnpm --filter app typecheck`, `git diff --check`.
- Phase 2 reviewer re-check landed in `VERIFICATION.md`; implementation may proceed to Phase 3.
- Phase 3/4 implementation reports landed in `VERIFICATION.md`; `.work/STATUS.md` and `PLAN.md` now reflect implemented-awaiting-review state.
