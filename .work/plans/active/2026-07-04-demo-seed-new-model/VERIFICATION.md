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

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

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

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

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
