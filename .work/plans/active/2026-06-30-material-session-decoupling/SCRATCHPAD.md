# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-01T11:31_

## Now
Phases 1 and 2 are implemented, locally verified, and recorded in `PLAN.md`, `VERIFICATION.md`, and `.work/STATUS.md`. Awaiting reviewer sign-off.

## Alignment
Aligned with `.work/STATUS.md` and `PLAN.md`. Planning baseline already exists as `8c65b07 docs: prepare material-session decoupling implementation`. Implementation intentionally leaves Phases 1/2 awaiting reviewer verification rather than self-marking them verified.

## Open
- Commit boundary still pending. If committing is required, stage only Phase 1/2 code + plan/log/scratchpad/status changes and leave pre-existing `.work/.../archive/SCRATCHPAD.md` untracked.
- Reviewer should check the deviations recorded in `VERIFICATION.md`: retained deprecated slot tests; `BookingLike` structural type in progress package.

## Blockers
- None active.

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

## In-flight edits
- Implemented booking API/tests in `packages/roadmap-engine/src/roadmap-engine.ts`, `index.ts`, and `roadmap-engine.test.ts`.
- Added booking/session/material-progress payload fields in `apps/app/src/sync/types.ts` and `apps/app/src/session/types.ts`.
- Added progress derivations/tests: `deriveBookingStatuses`, `materialLedger`, `dailyActivity`, and `calibrationDenominator`.
- Updated app mapper/lifecycle/progress bridge for optional-slot roadmaps and booking events.
- Updated `PLAN.md` phase statuses and `VERIFICATION.md` implementer reports for Phases 1–2; updated `.work/STATUS.md`.
- Restored active `SCRATCHPAD.md`; archived copy remains untouched.

## Decisions in force
- Use project-local skills/rules only for this repo.
- `.work/plans/active/2026-06-30-material-session-decoupling/` is the active task unit; `VERIFICATION.md` is the running log.
- Preserve pre-existing dirty/untracked `.work` state unless it directly blocks this task.
- Roadmap engine generated booking IDs must be deterministic; no random IDs in `@study-tracker/roadmap-engine`.
- Legacy slot APIs stay present and deprecated during Phases 1/2; no destructive event migration.
- Calibration denominator for decoupled material throughput is `materialConsumedMinutes ?? plannedMinutes`, not the pre-session dial target alone.

## Resolved (recent)
- Active scratchpad deletion at session start resolved by recreating the task-local `SCRATCHPAD.md`; archived copy left untouched.
- Phase 1 app typecheck failure from optional `slots` resolved by Phase 2 no-slot bridge and minimal legacy compatibility guards.
