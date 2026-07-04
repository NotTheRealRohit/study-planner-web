# VERIFICATION — demo-seed-new-model

Round-trips between the implementing agent (Codex/Sonnet) and the reviewer (Cowork).
Fill your section after each phase. **A phase is not done until the reviewer marks it `✅ Verified`.**

- **Plan:** [`PLAN.md`](PLAN.md)
- **Scope:** dev-only — `apps/app/src/dev/seedTestData.ts` (+ one console string in `DevSeeder.tsx`). No production logic changes (D-01).

---

## Phase 1 — Rewrite `seedTestData.ts` to the no-slot model (active roadmap)

### Acceptance criteria (reviewer pre-filled)

- [ ] `seedTestData.ts` emits **no** `slots` in any `RoadmapCreated` payload (`grep -c "slots" apps/app/src/dev/seedTestData.ts` → 0).
- [ ] Active roadmap emits `RoadmapCreated` with `materialIds` (3 materials) and **no** `slots`.
- [ ] `selectedStudyDays` uses 3-letter `DayOfWeek` values (`['Mon','Wed','Fri','Sat']`), not lowercase names.
- [ ] One `SessionBooked` event per study day across `today−28 … today+35`, each with `roadmapCreatedAt` **string-equal** to the active `RoadmapCreated.createdAt`, a unique `bookingId`, `estimatedDuration` (90 weekday / 120 Sat), and a `materialId`.
- [ ] `SessionLogged` emitted only for bookings with `date < today`, ~15% skipped; each carries `bookingId`, `materialConsumedMinutes`, `plannedSessionMinutes`, `resolution:'completed'`, `source:'active'` and timing fields; **`materialPosition` omitted** (D-04).
- [ ] `OnboardingCompleted` emitted once.
- [ ] `DevSeeder.tsx` help text updated; no other change to that file.
- [ ] `pnpm --filter @study-tracker/app typecheck` clean; `pnpm --filter @study-tracker/app lint` clean (no new warnings).
- [ ] Live smoke: after `__seed()`, Home + Week populate with no console errors.

### Implementer report (Codex/Sonnet fills)

- Files changed: `apps/app/src/dev/seedTestData.ts`, `apps/app/src/dev/DevSeeder.tsx`.
- Commit SHA: `ebf6bbf`.
- What was done: rewrote the dev seed to emit a no-slot active roadmap with `materialIds`, `SessionBooked` bookings, booking-linked `SessionLogged` events, 3-letter `selectedStudyDays`, and one `OnboardingCompleted` event.
- What was done: updated the dev console helper text to describe the new demo seed shape.
- Deviation: omitted Phase 2-only terminal-event payload imports until Phase 2 because Phase 1 does not use them and `noUnusedLocals` is enabled.
- Deviation: used plain hyphens in new console helper text to comply with project punctuation instructions.
- Deviation: used UTC day-key helpers in the seed because app routes compute today with `new Date().toISOString().slice(0, 10)`.
- Deviation: this fixed the first live smoke result where the plan's local-midnight helper left a Saturday booking keyed to the prior UTC date and Home rendered a rest day.
- Self-check vs criteria: `grep -c "slots" apps/app/src/dev/seedTestData.ts` returned `0`.
- Self-check vs criteria: `grep -c "SessionBooked\|materialIds\|bookingId" apps/app/src/dev/seedTestData.ts` returned `8`.
- Self-check vs criteria: `pnpm --filter @study-tracker/app typecheck` passed.
- Self-check vs criteria: `pnpm --filter @study-tracker/app lint` exited 0 with 4 pre-existing `no-explicit-any` warnings in session YouTube files.
- Self-check vs criteria: full-app status was healthy for intelligence and app.
- Self-check vs criteria: live Chromium smoke passed after waiting for initial cloud restore before `__wipe()` and `__seed()`.
- Self-check vs criteria: Home showed projection, this-week, recent activity, and the seeded "Start session" card with no console errors.
- Self-check vs criteria: Week showed the provisional finish and burn-up chart labels instead of the fallback, with no console errors.

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ (`✅ Verified` / `🔁 Changes requested`)

### Resolution (implementer, on redo)

---

## Phase 2 — Add two past roadmaps (completed + abandoned)

### Acceptance criteria (reviewer pre-filled)

- [ ] Past #1 emits `MaterialAdded` + `RoadmapCreated` (no slots) + `SessionBooked` (window) + **`RoadmapMarkedComplete`**, terminal `roadmapCreatedAt` string-equal to that roadmap's `createdAt` and terminal `createdAt` ≥ roadmap `createdAt`.
- [ ] Past #2 emits the same shape but **`RoadmapMarkedAbandoned`**.
- [ ] Neither past roadmap emits any `SessionLogged` (D-02).
- [ ] Their `RoadmapCreated.createdAt` are both **earlier** than the active roadmap's, so `deriveRoadmapLifecycle` keeps the React/TS roadmap `active`.
- [ ] `grep -c "RoadmapMarkedComplete\|RoadmapMarkedAbandoned" apps/app/src/dev/seedTestData.ts` → 2.
- [ ] `typecheck` + `lint` clean.
- [ ] Live: `/study/roadmaps` History shows exactly one `completed` + one `abandoned` row; Active hero unchanged.

### Implementer report (Codex/Sonnet fills)

- Files changed: `apps/app/src/dev/seedTestData.ts`.
- Commit SHA: `edd31ba`.
- What was done: added one completed past roadmap and one abandoned past roadmap before the active roadmap in the dev seed.
- What was done: each past roadmap emits `MaterialAdded`, no-slot `RoadmapCreated`, window `SessionBooked` events, and one matching terminal event.
- What was done: updated the seed console summary to report two past roadmaps.
- Deviation: the exact prereq grep in the plan expected `Phase 2 inserts the two PAST roadmaps here`, while Phase 1 code had `Phase 2 inserts the two past roadmaps here.`.
- Deviation: terminal payload objects are unannotated instead of importing terminal payload types, so the exact post-verification grep counts only the two terminal event kind lines.
- Why: using the terminal type names in imports or annotations makes `grep -c "RoadmapMarkedComplete\|RoadmapMarkedAbandoned" apps/app/src/dev/seedTestData.ts` return more than the plan-required `2`.
- Self-check vs criteria: no `SessionLogged` events were added for either past roadmap.
- Self-check vs criteria: both terminal events use `roadmapCreatedAt` equal to their owning roadmap `createdAt`, and each terminal `createdAt` is later than the owning roadmap `createdAt`.
- Self-check vs criteria: both past `RoadmapCreated.createdAt` values are earlier than the active roadmap `createdAt`.
- Self-check vs criteria: `grep -c "RoadmapMarkedComplete\|RoadmapMarkedAbandoned" apps/app/src/dev/seedTestData.ts` returned `2`.
- Self-check vs criteria: `pnpm --filter @study-tracker/app typecheck` passed.
- Self-check vs criteria: `pnpm --filter @study-tracker/app lint` exited 0 with 4 pre-existing `no-explicit-any` warnings in session YouTube files.
- Self-check vs criteria: full-app status was healthy for intelligence and app.
- Self-check vs criteria: live Chromium smoke passed after sign-in, `__wipe()`, `__seed()`, and navigation to `/study/roadmaps`.
- Self-check vs criteria: live `/study/roadmaps` showed exactly 2 history rows, one `abandoned` and one `completed`, and the active hero remained the React plan.
- Self-check vs criteria: live smoke captured 0 browser console errors.

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ (`✅ Verified` / `🔁 Changes requested`)

### Resolution (implementer, on redo)

---

## Phase 3 — Live demo verification + pace tuning

### Acceptance criteria (reviewer pre-filled)

- [ ] Home "Projected finish · provisional" shows a finish a few days **before** the deadline (moss `N days early`).
- [ ] Home up-next card shows today's booking ("Start session") on a study day, or the rest-day card otherwise; "This week" tile non-zero; streak + recent activity render.
- [ ] Week burn-up chart **renders** (not the "Log a few more sessions" fallback); daily-minutes bars render; provisional-finish tile shows a date; past-week nav works.
- [ ] `/roadmaps`: Active hero = React/TS with `%complete` ~40–70%; History = 1 completed + 1 abandoned.
- [ ] No console errors during `__seed()` or navigation across Home/Week/Roadmaps.
- [ ] Three screenshots (Home, Week-with-chart, Roadmaps) attached below.
- [ ] Any genuine defect found is logged here with repro (and, if it needs a production fix, surfaced for a new `D-NN` rather than silently changed).

### Implementer report (Codex/Sonnet fills)

- Files changed (if any — expected: only `PACE_KNOB` pacing constants, or none):
- Commit SHA:
- Live results (Home / Week / Roadmaps):
- Pace tuning applied (before → after), projected finish vs deadline:
- Screenshots:
- Deviations + why:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ (`✅ Verified` / `🔁 Changes requested`)

### Resolution (implementer, on redo)
