# Scratchpad - 2026-07-04-demo-seed-new-model
_Plan: `.work/plans/active/2026-07-04-demo-seed-new-model/PLAN.md` | Log: `VERIFICATION.md` | Updated: 2026-07-04T07:59_

## Now
Phase 2 is complete in `edd31ba` and awaiting reviewer verification.
`seedTestData.ts` now inserts one completed past roadmap and one abandoned past roadmap before the active roadmap.
Phase 1 remains recorded as implemented in `ebf6bbf`, with the reviewer section still blank.

## Alignment
Work remains aligned with D-01 dev-only scope.
Phase 2 should touch only `apps/app/src/dev/seedTestData.ts` plus `PLAN.md`, `VERIFICATION.md`, `SCRATCHPAD.md`, and `.work/STATUS.md` journal updates.
Do not change production roadmap, progress, chart, or page logic.

## Open
- none

## Blockers
- none

## Deferrals
- OQ-01 remains deferred: active-roadmap progress is not scoped away from prior `SessionLogged` events.
- OQ-02 remains deferred: past roadmap logged progress should wait for OQ-01.
- Phase 3 remains pending until Phase 2 is implemented and verified.

## Checklist
- [x] Read `.work/README.md`, `.work/STATUS.md`, `PLAN.md`, and `VERIFICATION.md`.
- [x] Read project-local scratchpad and work-journal skills.
- [x] Read project-local plan-implementor and code-memory skills.
- [x] Read applicable project rules for full-app verification, Playwright config, pnpm build registry, and roadmap-engine context.
- [x] Confirm Step 0 planning docs are already committed.
- [x] Check git status before Phase 2.
- [x] Run Phase 2 prereq verification.
- [x] Record Phase 2 start in `PLAN.md` and `SCRATCHPAD.md`.
- [x] Commit Phase 2 start marker.
- [x] Add completed and abandoned past roadmaps to `seedTestData.ts`.
- [x] Update seed console summary.
- [x] Run Phase 2 verification commands.
- [x] Run live `/study/roadmaps` smoke for history rows.
- [x] Fill Phase 2 implementer report in `VERIFICATION.md`.
- [x] Update `.work/STATUS.md`.
- [x] Commit Phase 2 implementation and journal records.

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
- Phase 2 proceeds by explicit user request even though Phase 1's reviewer block is still blank.
- Phase 2 terminal payload objects stay unannotated so the plan's grep guard counts only emitted terminal event kinds.

## Resolved (recent)
- Step 0 planning baseline resolved: `PLAN.md` and `VERIFICATION.md` are already tracked in `1532a5c`.
- Phase 1 prereqs resolved: legacy `slots` present, `materialIds` and `SessionBookedPayload` exist, and `DayOfWeek` is exported.
- Punctuation decision resolved: new text uses plain hyphens, not em dashes.
- Phase 1 implementation commit resolved: `ebf6bbf`.
- Phase 1 verification resolved: grep guards, typecheck, lint, and live Chromium smoke passed.
- Phase 2 helper prereq resolved: `bookingsForWindow`, `roadmapEvent`, and `bookingEvent` are present.
- Phase 2 prereq drift resolved: the semantic placeholder was present despite exact grep case and punctuation drift, and the user had explicitly requested Phase 2.
- Phase 2 static verification resolved: grep guard returned `2`, typecheck passed, and lint exited 0 with the same four pre-existing warnings.
- Phase 2 live smoke resolved: `/study/roadmaps` showed exactly two history rows, one abandoned and one completed, with zero browser console errors.
- Phase 2 commit resolved: `edd31ba`.
