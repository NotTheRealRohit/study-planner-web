# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-01T11:59_

## Now
Phase 2 redo is implemented locally and verified by focused tests. Added the missing no-slots app-level tests for `roadmapLifecycle.ts` and `roadmapProgress.ts`, updated `PLAN.md`, `VERIFICATION.md`, and `.work/STATUS.md`; awaiting Cowork reviewer re-check.

## Alignment
Aligned with `PLAN.md` and the Cowork Phase 2 review in `VERIFICATION.md`. Phase 1 is now marked complete/verified. Phase 2 remains in-progress because the redo is not reviewer-verified yet; do not mark it ✅ from implementer-side tests alone.

## Open
- Await Cowork re-check of Phase 2 redo. The missing-test checklist is now implemented and logged in `VERIFICATION.md`.
- Commit boundary is pending for the redo unless the user asks to commit.

## Blockers
- Phase 2 cannot be marked verified by the implementer; leave it awaiting reviewer redo/sign-off.

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

## In-flight edits
- Modified `apps/app/src/roadmap/roadmapLifecycle.test.ts` with a no-slots booking-count case.
- Added `apps/app/src/roadmap/roadmapProgress.test.ts` covering ledger-backed no-slots progress summary.
- Updated `PLAN.md`, `VERIFICATION.md`, `.work/STATUS.md`, and this scratchpad for the Phase 2 redo.

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
