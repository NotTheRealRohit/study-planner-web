# VERIFICATION — material-session UI bug fixes

Round-trip review log for [`PLAN.md`](./PLAN.md). **Planner pre-fills acceptance criteria** (below).
**Implementer (Codex/Sonnet)** fills the *Implementer report* per phase (files, commit SHA, deviations,
self-check). **Reviewer (Cowork)** fills *Reviewer findings* by reading the actual diff (`git show <sha>`),
not the report alone. A phase is **not done** until it's `✅ Verified`.

Legend: `[ ]` unmet · `[x]` met · `[~]` partial. Status: ☐ Not started · 🟡 In progress · ✅ Verified · 🔁 Changes requested.

Cross-cutting invariants (must hold at every phase):
- No event-model or intelligence-math changes; booking events + per-user Dexie isolation untouched.
- No new source files outside the phase's stated scope; Marginalia design tokens used (no hard-coded colors except where BurnUpChart already hard-codes them with the documented reason).
- E2E specs authored, not run (env constraint); Vitest unit tests run green.

---

## Phase 1 — Remove duplicate "Edit & add" button (BUG-3) · Status: ☐ Not started

**Acceptance criteria**
- [ ] `apps/app/src/pages/Roadmaps.tsx` renders exactly one primary hero link, `Open plan` → `/roadmap`; the `Edit & add` `<Link>` is removed; `Close plan` control unchanged (D-01).
- [ ] `Roadmaps.test.tsx` no longer asserts an `Edit & add` link; `Open plan` href assertion retained; suite green.
- [ ] `grep "Edit &amp; add" apps/app/src/pages/Roadmaps.tsx` returns nothing.
- [ ] `pnpm --filter @study-tracker/app typecheck` + `test -- Roadmaps` green.

**Implementer report:** _(pending)_

**Reviewer findings:** _(pending)_

---

## Phase 2 — Center booking sheets (BUG-1) · Status: ☐ Not started

**Acceptance criteria**
- [ ] `.bk-overlay` uses `align-items: center` (was `flex-end`) (D-02).
- [ ] `.bk-sheet` uses `border-radius: var(--radius-lg)` and adds `max-height: calc(100dvh - var(--space-6))` + `overflow-y: auto`.
- [ ] `.bk-grip` is hidden because the centered card is no longer a draggable bottom sheet.
- [ ] All four sheets (BookingEditor/AddSession/MaterialPicker/MaterialProgress) render centered on desktop AND ≤560px, and a taller-than-viewport sheet scrolls rather than clipping (visual check).
- [ ] `pnpm --filter @study-tracker/app typecheck` green.

**Implementer report:** _(pending)_

**Reviewer findings:** _(pending)_

---

## Phase 3 — Mobile add-session entry point (BUG-2) · Status: ☐ Not started

**Acceptance criteria**
- [ ] `CalendarCell` `canOpenDay` no longer requires `bubbles.length > 0`, so empty in-month days are tappable at ≤560px (D-03).
- [ ] `DaySheet` gains `onAddSession?`/`canAddSession?`, renders an empty-state line when no bubbles, and a `+ Add session` button that calls `onAddSession(day.date)`; hidden when `!canAddSession` (readOnly).
- [ ] `RoadmapCalendar` passes `onAddSession` (closes DaySheet, opens AddSessionSheet with that date) + `canAddSession={!readOnly}`; the existing `handleCreateBooking` still emits `SessionBooked`.
- [ ] `RoadmapCalendar.test.tsx` has a configurable `useMatchMedia` mock and proves the compact add path (open empty day → Add → AddSessionSheet → create) plus readOnly hides Add. Playwright authored (not run).
- [ ] `pnpm --filter @study-tracker/app typecheck` + `test -- RoadmapCalendar DaySheet` green.

**Implementer report:** _(pending)_

**Reviewer findings:** _(pending)_

---

## Phase 4 — Study-day indicator + onboarding preview legibility (BUG-4) · Status: ☐ Not started

**Acceptance criteria** (visual contract `mocks/proposed/study-day-indicator.html`)
- [ ] Shared `.roadmap-day-studyday` moss-8% tint added; today/current-week overrides keep their fills on overlap (D-04).
- [ ] Study-day tint applied to in-month cells in **both** `RoadmapCalendar` (via `isStudyDay(date, roadmap.selectedStudyDays)`) and `Step3Preview` (via `state.selectedStudyDays`); study-day weekday headers emphasized; a "Study day" legend entry added to both legends.
- [ ] `isStudyDay` weekday mapping is unit-tested (correct `DayOfWeek` for known dates).
- [ ] Onboarding session bubble recolored `roadmap-chip-done` → `roadmap-chip-booked` with `title` + `aria-label`.
- [ ] Hover-lift (`.roadmap-day-in-month:hover`) scoped OFF inside `.onboarding-mini-calendar`; cursor default there.
- [ ] Matches the approved mock; `pnpm --filter @study-tracker/app typecheck` + `test -- CalendarCell RoadmapCalendar Step3Preview calendarModel` green.

**Implementer report:** _(pending)_

**Reviewer findings:** _(pending)_

---

## Phase 5 — Burn-up chart fix (BUG-5) · Status: ☐ Not started

**Acceptance criteria**
- [ ] `progress.ts` builds `burnUp.planned` from **booking-capacity semantics** over `startDate..deadline`, not `roadmap.slots`: each selected Mon-Fri adds `weekdayHours * 60`, each selected Sat-Sun adds `weekendHours * 60`; `deficit` recomputed off it; missing capacity fields or empty `selectedStudyDays` fall back without crashing (D-05).
- [ ] `BurnUpData` carries optional `startDate`/`deadline` domain hints populated by `computeProgress`; app mocks are not forced to update unless needed.
- [ ] `BurnUpChart.minutesToLabel` shows h+m (`45m`, `1h 30m`, `2h`), and explicit tick values prevent duplicate y-axis labels.
- [ ] Degenerate/empty data renders an empty state; x-domain spans at least `[startDate, deadline]` or the derived `today/dayNumber/totalDays` fallback so x-ticks are distinct dates.
- [ ] GP band/mean use `curveMonotoneX` (no overshoot); y-domain is based on planned/actual/GP mean with only bounded GP-upper headroom.
- [ ] `progress.test.ts` covers the booking-capacity planned baseline + fallback; `BurnUpChart.test.tsx` covers labels/ticks/empty state; `pnpm --filter @study-tracker/progress test` + app typecheck green.

**Implementer report:** _(pending)_

**Reviewer findings:** _(pending)_

---

## Final gate (after all phases ✅ Verified)
- [ ] `pnpm lint && pnpm typecheck` clean across touched packages.
- [ ] `pnpm --filter @study-tracker/app test` + `pnpm --filter @study-tracker/progress test` green.
- [ ] Visual confirmation of BUG-1/BUG-2/BUG-4 on desktop + ≤560px; BUG-5 burn-up renders sensibly with real data.
- [ ] E2E authored for BUG-2/BUG-4 (run on a capable machine before calling the whole plan done).
- [ ] OQ-01 (4d back-exit) still open, tracked.
