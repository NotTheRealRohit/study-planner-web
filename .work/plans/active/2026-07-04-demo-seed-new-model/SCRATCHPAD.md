# Scratchpad - 2026-07-04-demo-seed-new-model
_Plan: `.work/plans/active/2026-07-04-demo-seed-new-model/PLAN.md` | Log: `VERIFICATION.md` | Updated: 2026-07-04T07:45_

## Now
Phase 1 is implemented in `ebf6bbf` and awaiting reviewer verification.
The plan, verification log, scratchpad, and STATUS row record the implementation SHA and verification evidence.
Step 0 planning docs are already committed in `1532a5c chore(workspace): capture active updates`, so no empty baseline commit is needed.

## Alignment
Work is aligned with the plan with three implementation deviations recorded for verification.
Implement Phase 1 only unless the user explicitly broadens the request.
Keep edits scoped to `apps/app/src/dev/seedTestData.ts`, `apps/app/src/dev/DevSeeder.tsx`, `PLAN.md`, `VERIFICATION.md`, `SCRATCHPAD.md`, and any required `.work/STATUS.md` journal update.

## Open
- Reviewer needs to verify Phase 1 before Phase 2 starts.

## Blockers
- none

## Deferrals
- OQ-01 remains deferred: active-roadmap progress is not scoped away from prior `SessionLogged` events.
- OQ-02 remains deferred: past roadmap logged progress should wait for OQ-01.
- Phase 2 and Phase 3 remain pending until Phase 1 is reviewer-verified.

## Checklist
- [x] Read `.work/README.md`, `.work/STATUS.md`, `PLAN.md`, and `VERIFICATION.md`.
- [x] Read project-local scratchpad and work-journal skills.
- [x] Read applicable project rules for full-app verification, Playwright config, pnpm build registry, and roadmap-engine context.
- [x] Confirm Step 0 planning docs are already committed.
- [x] Run Phase 1 prereq verification.
- [x] Rewrite `seedTestData.ts` to the no-slot active roadmap model.
- [x] Update `DevSeeder.tsx` help text.
- [x] Run Phase 1 verification commands.
- [x] Commit Phase 1 code changes with scoped commit `ebf6bbf`.
- [x] Update `PLAN.md`, `VERIFICATION.md`, `SCRATCHPAD.md`, and `.work/STATUS.md` as needed.
- [x] Commit `.work` records for Phase 1.

## In-flight edits
- none

## Decisions in force
- D-01: dev-only seed scope; do not change production progress, roadmap, chart, or page logic.
- D-02: past roadmaps will carry no `SessionLogged` when Phase 2 runs.
- D-03: all seed dates are relative to the run date.
- D-04: seeded active `SessionLogged` events omit `materialPosition`.
- D-05: leave today and future bookings unlogged.
- D-06: booking material assignment is sequential in curriculum order.
- D-07: chart and projection issues require live verification before any production change.
- Phase 1 implementation omits Phase 2-only terminal-event imports until Phase 2 to satisfy `noUnusedLocals`.
- New console help text uses plain hyphens to follow project punctuation instructions.
- Seed date keys use UTC day helpers to match the app's `todayISO()` convention.

## Resolved (recent)
- Step 0 planning baseline resolved: `PLAN.md` and `VERIFICATION.md` are already tracked in `1532a5c`.
- Phase 1 prereqs resolved: legacy `slots` present, `materialIds` and `SessionBookedPayload` exist, and `DayOfWeek` is exported.
- Punctuation decision resolved: new text uses plain hyphens, not em dashes.
- Phase 1 implementation commit resolved: `ebf6bbf`.
- Phase 1 verification resolved: grep guards, typecheck, lint, and live Chromium smoke passed.
