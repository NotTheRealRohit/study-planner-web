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

## Phase 1 - Remove duplicate "Edit & add" button (BUG-3) · Status: 🟡 Implemented, awaiting review

**Acceptance criteria**
- [x] `apps/app/src/pages/Roadmaps.tsx` renders exactly one primary hero link, `Open plan` → `/roadmap`; the `Edit & add` `<Link>` is removed; `Close plan` control unchanged (D-01).
- [x] `Roadmaps.test.tsx` no longer asserts an `Edit & add` link; `Open plan` href assertion retained; suite green.
- [x] `grep "Edit &amp; add" apps/app/src/pages/Roadmaps.tsx` returns nothing.
- [x] `pnpm --filter @study-tracker/app typecheck` + `test -- Roadmaps` green.

**Implementer report:** 2026-07-02
- Files changed: `apps/app/src/pages/Roadmaps.tsx`, `apps/app/src/pages/Roadmaps.test.tsx`.
- Removed the duplicate `Edit & add` link only.
- Kept `Open plan` as `<Link to="/roadmap">` and kept `Close plan` unchanged.
- Verification:
  - `grep -n "Edit &amp; add" apps/app/src/pages/Roadmaps.tsx` returned no rows.
  - `pnpm --filter @study-tracker/app test -- Roadmaps` passed, with 58 app test files and 509 tests green.
  - `pnpm --filter @study-tracker/app typecheck` passed.
- Deviations: none for code or tests.
- Commit SHA: `0268f20`.

**Reviewer findings:** _(pending)_

---

## Phase 2 - Center booking sheets (BUG-1) · Status: 🟡 Implemented, awaiting review

**Acceptance criteria**
- [x] `.bk-overlay` uses `align-items: center` (was `flex-end`) (D-02).
- [x] `.bk-sheet` uses `border-radius: var(--radius-lg)` and adds `max-height: calc(100dvh - var(--space-6))` + `overflow-y: auto`.
- [x] `.bk-grip` is hidden because the centered card is no longer a draggable bottom sheet.
- [x] All four sheets (BookingEditor/AddSession/MaterialPicker/MaterialProgress) render centered on desktop AND ≤560px, and a taller-than-viewport sheet scrolls rather than clipping (visual check).
- [x] `pnpm --filter @study-tracker/app typecheck` green.

**Implementer report:** 2026-07-02
- Files changed: `apps/app/src/roadmap/roadmap.css`.
- Updated `.bk-overlay` from bottom alignment to centered alignment.
- Added `.bk-sheet` max-height and `overflow-y: auto` to prevent clipping on short viewports.
- Changed `.bk-sheet` to `border-radius: var(--radius-lg)`.
- Hid `.bk-grip` because the sheet no longer behaves like a bottom drawer.
- Visual verification:
  - Desktop short sheet: 1280x800 viewport, top 300px, bottom 300px, height 201px, radius 16px.
  - Mobile short sheet: 390x844 viewport, top 322px, bottom 322px, height 201px, radius 16px.
  - Mobile tall sheet with representative `.bk-rows`: 390x480 viewport, top 16px, bottom 16px, height 448px, `overflow-y: auto`, `scrollHeight` 1135px, `clientHeight` 448px, radius 16px.
- Verification:
  - `grep -n "max-height: calc(100dvh" apps/app/src/roadmap/roadmap.css` found the `.bk-sheet` guard.
  - `grep -n "\.bk-grip" -A4 apps/app/src/roadmap/roadmap.css` confirmed `display: none`.
  - `pnpm --filter @study-tracker/app typecheck` passed.
- Deviations: visual check used a focused Playwright fixture with real CSS and representative booking-sheet DOM instead of a mutating authenticated app flow.
  This avoided touching a real account while verifying the shared `.bk-*` geometry used by all four sheets.
- Commit SHA: `0268f20`.

**Reviewer findings:** _(pending)_

---

## Phase 3 — Mobile add-session entry point (BUG-2) · Status: 🟡 Implemented, awaiting review

**Acceptance criteria**
- [x] `CalendarCell` `canOpenDay` no longer requires `bubbles.length > 0`, so empty in-month days are tappable at ≤560px (D-03).
- [x] Empty compact-day buttons use a neutral aria-label such as `Open <date> day options`; they do not claim empty days already have sessions.
- [x] `DaySheet` gains `onAddSession?`/`canAddSession?`, renders an empty-state line when no bubbles, and a `+ Add session` button that calls `onAddSession(day.date)`; hidden when `!canAddSession` (readOnly).
- [x] `RoadmapCalendar` passes `onAddSession` (closes DaySheet, opens AddSessionSheet with that date) + `canAddSession={!readOnly}`; the existing `handleCreateBooking` still emits `SessionBooked`.
- [x] `RoadmapCalendar.test.tsx` has a configurable `useMatchMedia` mock and proves the compact add path (open empty day → Add → AddSessionSheet → create) plus readOnly hides Add. Playwright authored (not run) with viewport width below 560px.
- [x] `pnpm --filter @study-tracker/app typecheck` + `test -- RoadmapCalendar DaySheet` green.

**Implementer report:** 2026-07-02
- Files changed: `apps/app/src/roadmap/CalendarCell.tsx`, `apps/app/src/roadmap/DaySheet.tsx`, `apps/app/src/roadmap/RoadmapCalendar.tsx`, `apps/app/src/roadmap/roadmap.css`, `apps/app/src/roadmap/RoadmapCalendar.test.tsx`, `e2e/material-session-decoupling.spec.ts`.
- Implemented the compact empty-day `DaySheet` path and reused the existing `AddSessionSheet` and `SessionBooked` writer.
- Added the read-only compact day-sheet assertion and the compact add-session unit flow.
- Authored the compact empty-day Playwright case in `e2e/material-session-decoupling.spec.ts`; it was not run per plan.
- Verification:
  - `grep -n "onAddSession" apps/app/src/roadmap/DaySheet.tsx apps/app/src/roadmap/RoadmapCalendar.tsx` found the new props and wiring.
  - `pnpm --filter @study-tracker/app typecheck` passed.
  - `pnpm --filter @study-tracker/app test -- CalendarCell RoadmapCalendar Step3Preview calendarModel` passed with 58 files and 515 tests.
- Deviations: the focused test command was broader than the phase minimum because Phase 4 was implemented in the same user-requested batch.
- Commit SHA: `3c8d869`.

**Reviewer findings:** _(pending)_

---

## Phase 4 — Study-day indicator + onboarding preview legibility (BUG-4) · Status: 🟡 Implemented, awaiting review

**Acceptance criteria** (visual contract `mocks/proposed/study-day-indicator.html`)
- [x] Shared `.roadmap-day-studyday` moss-8% tint added; today/current-week overrides keep their fills on overlap (D-04).
- [x] CSS order/specificity makes today keep `--cal-today-fill` even when the same cell is also a current-week study day.
- [x] Study-day tint applied to in-month cells in **both** `RoadmapCalendar` (via `day.isInMonth && isStudyDay(date, roadmap.selectedStudyDays)`) and `Step3Preview` (via `day.isInMonth && isStudyDay(date, state.selectedStudyDays)`); outside-month filler cells are not tinted.
- [x] Study-day weekday headers emphasized; a "Study day" legend entry added to both legends.
- [x] `isStudyDay` uses the repo's UTC ISO-date weekday convention and is unit-tested with known dates (correct `DayOfWeek` for known dates).
- [x] Onboarding session bubble recolored `roadmap-chip-done` → `roadmap-chip-booked` with `title` + `aria-label`.
- [x] Onboarding booked-session legend swatch no longer implies completed green/done semantics after the bubble moves to booked-outline styling.
- [x] Hover-lift (`.roadmap-day-in-month:hover`) scoped OFF inside `.onboarding-mini-calendar`; cursor default there.
- [x] Matches the approved mock; `pnpm --filter @study-tracker/app typecheck` + `test -- CalendarCell RoadmapCalendar Step3Preview calendarModel` green.

**Implementer report:** 2026-07-02
- Files changed: `apps/app/src/roadmap/calendarModel.ts`, `apps/app/src/roadmap/calendarModel.test.ts`, `apps/app/src/roadmap/CalendarCell.tsx`, `apps/app/src/roadmap/RoadmapCalendar.tsx`, `apps/app/src/roadmap/RoadmapCalendar.test.tsx`, `apps/app/src/roadmap/roadmap.css`, `apps/app/src/onboarding/steps/Step3Preview.tsx`, `apps/app/src/onboarding/steps/Step3Preview.test.tsx`, `apps/app/src/onboarding/onboarding.css`, `e2e/material-session-decoupling.spec.ts`.
- Added shared UTC ISO-date weekday helpers and tests for `2026-07-06` -> `Mon`, `2026-07-07` -> `Tue`, and `2026-07-12` -> `Sun`.
- Restored `selectedStudyDays`, `weekdayHours`, and `weekendHours` in `RoadmapCalendar`'s local `roadmapInputFromPayload` adapter because the plan assumed `roadmap.selectedStudyDays` was already available.
- Applied the moss study-day tint to in-month cells only on both calendar surfaces.
- Added study-day header emphasis and legend entries.
- Recolored onboarding preview bookings to booked-outline styling with `title` and `aria-label`.
- Updated onboarding booked and study-day swatches so future bookings no longer read as completed green.
- Scoped the hover-lift off inside `.onboarding-mini-calendar`.
- Authored the onboarding preview Playwright case in `e2e/material-session-decoupling.spec.ts`; it was not run per plan.
- Verification:
  - `grep -n "roadmap-day-studyday" apps/app/src/roadmap/roadmap.css apps/app/src/roadmap/CalendarCell.tsx apps/app/src/onboarding/steps/Step3Preview.tsx` found the shared class in CSS and both render paths.
  - `grep -n "roadmap-chip-booked" apps/app/src/onboarding/steps/Step3Preview.tsx` found the preview chip recolor.
  - `pnpm --filter @study-tracker/app typecheck` passed.
  - `pnpm --filter @study-tracker/app test -- CalendarCell RoadmapCalendar Step3Preview calendarModel` passed with 58 files and 515 tests.
- Deviations: restored the local `RoadmapCalendar` adapter fields that the plan expected to already be present.
- Commit SHA: `3c8d869`.

**Reviewer findings:** _(pending)_

---

## Phase 5 — Burn-up chart fix (BUG-5) · Status: 🟡 Implemented, awaiting review

**Acceptance criteria**
- [x] `progress.ts` builds `burnUp.planned` from **booking-capacity semantics** over `startDate..deadline`, not `roadmap.slots`: each selected Mon-Fri adds `weekdayHours * 60`, each selected Sat-Sun adds `weekendHours * 60`; `deficit` recomputed off it; missing capacity fields or empty `selectedStudyDays` fall back without crashing (D-05).
- [x] `BurnUpData` carries optional `startDate`/`deadline` domain hints populated by `computeProgress`; app mocks are not forced to update unless needed.
- [x] `BurnUpChart.minutesToLabel` shows h+m (`45m`, `1h 30m`, `2h`), and explicit tick values prevent duplicate y-axis labels.
- [x] `BurnUpChart` exports pure helpers for x-domain, y-domain, tick values, labels, and empty-state detection; helper tests cover the degenerate-domain and bounded-GP-upper cases.
- [x] Degenerate/empty data renders "Log a session to see your burn-up" before `ParentSize`, so the component test does not depend on responsive SVG layout.
- [x] X-domain spans at least `[startDate, deadline]` or the derived `today/dayNumber/totalDays` fallback so x-ticks are distinct dates.
- [x] GP band/mean use `curveMonotoneX` (no overshoot); y-domain is based on planned/actual/GP mean with only bounded GP-upper headroom.
- [x] Week's existing low-data gate is preserved unless explicitly widened; any Week visual Playwright check seeds at least three actual data points.
- [x] `progress.test.ts` covers the booking-capacity planned baseline + fallback; `BurnUpChart.test.tsx` covers labels/ticks/domain/y-domain/empty state; `pnpm --filter @study-tracker/progress test` + app typecheck green.

**Implementer report:** 2026-07-02
- Started Phase 5 after prereq verification passed.
- Prereq verification:
  - `grep -n "buildPlannedCumulative\|burnUp\b\|deficit" packages/progress/src/progress.ts` found the expected legacy slot-based burn-up path.
  - `grep -n "minutesToLabel\|curveBasis\|allMinutes\|allDates" apps/app/src/components/BurnUpChart.tsx` found the expected old formatter, domain, y-domain, and curve usage.
  - `pnpm --filter @study-tracker/progress test` passed with 13 files and 95 tests.
- Phase 6 note: `PLAN.md` defines Phases 1-5 only, followed by a final gate.
  Treat the user's requested Phase 6 as the final gate after Phase 5 unless Rohit supplies a separate Phase 6 plan.
- Files changed: `packages/progress/src/types.ts`, `packages/progress/src/progress.ts`, `packages/progress/test/progress.test.ts`, `apps/app/src/components/BurnUpChart.tsx`, `apps/app/src/components/BurnUpChart.test.tsx`.
- Implemented the D-05 capacity-shaped planned burn-up baseline with slot fallback for legacy/incomplete inputs.
- Populated optional `burnUp.startDate` and `burnUp.deadline` from `computeProgress`.
- Added tests for booking-capacity planned points, slot fallback, and deficit against the capacity baseline.
- Exported BurnUpChart helpers for minute labels, tick values, x-domain, y-domain, and empty-state detection.
- Added helper/component tests for h+m labels, sparse and degenerate date domains, bounded GP-upper headroom, high-range tick readability, and pre-`ParentSize` empty state.
- Switched GP band and mean from `curveBasis` to `curveMonotoneX`.
- Preserved the Week page's existing low-data gate.
- Visual verification:
  - `./full-app status full` showed `intelligence` and `app` healthy.
  - `curl -i http://127.0.0.1:8000/health` returned 200.
  - `curl -i http://localhost:5173/study/sign-in` returned 200.
  - Browser probe of `/study/chart-test` rendered a nonblank 798x280 SVG with five paths.
  - Initial visual pass found the plan's sample tick helper made the 58h y-axis too dense.
  - Final browser probe showed visible y labels were sparse and unique: `0m`, `10h`, `20h`, `30h`, `40h`, `50h`, `58h`.
  - Screenshot saved during verification: `/private/tmp/study-planner-burnup-chart.png`.
- Verification:
  - `grep -n "buildPlannedCumulativeFromCapacity\|startDate" packages/progress/src/progress.ts packages/progress/src/types.ts` found the new capacity helper and domain hints.
  - `grep -n "curveMonotoneX\|buildMinuteTickValues" apps/app/src/components/BurnUpChart.tsx` found the monotone curves and tick helper.
  - `pnpm --filter @study-tracker/progress test` passed with 13 files and 98 tests.
  - `pnpm --filter @study-tracker/app typecheck` passed.
  - `pnpm --filter @study-tracker/app test -- BurnUpChart Week` passed with 59 files and 522 tests before the high-range tick test, then `pnpm --filter @study-tracker/app test -- BurnUpChart` passed with 59 files and 523 tests after the tick-density fix.
- Final-gate probe treated as the requested Phase 6:
  - `pnpm lint` exited 0 with four pre-existing app warnings in `YouTubePlayerAdapter.test.ts` and `loadYouTubeApi.ts`.
  - `pnpm typecheck` passed.
  - `pnpm --filter @study-tracker/app test` passed with 59 files and 523 tests.
  - `pnpm --filter @study-tracker/progress test` passed with 13 files and 98 tests.
- Deviations:
  - Adjusted the plan's sample `buildMinuteTickValues` step selection after visual review because the literal helper produced a dense 2h y-axis on a 58h chart.
    The implemented helper targets roughly six intervals, preserves low-range 30-minute labels, keeps explicit unique ticks, and includes the exact max label.
  - Visual verification used the existing unauthenticated `/study/chart-test` BurnUpChart surface instead of an authenticated Week flow because the real Week route depends on authenticated EventStore state.
    Week's low-data rendering gate remains covered by unit tests.
- Commit SHA: `256616b`.

**Reviewer findings:** _(pending)_

---

## Final gate (after all phases ✅ Verified)
- [~] `pnpm lint && pnpm typecheck` clean across touched packages.
  Pre-review probe passed both commands on 2026-07-02.
  `pnpm lint` exits 0 with four pre-existing `any` warnings in YouTube session files.
- [x] `pnpm --filter @study-tracker/app test` + `pnpm --filter @study-tracker/progress test` green.
- [~] Visual confirmation of BUG-1/BUG-2/BUG-4 on desktop + ≤560px; BUG-5 burn-up renders sensibly with real data.
  BUG-1/BUG-2/BUG-4 visual evidence is recorded in earlier phase reports.
  BUG-5 was visually confirmed on `/study/chart-test` with a nonblank chart, sparse unique y-axis labels, monotone GP line/band, and readable planned/actual lines.
  Authenticated Week real-data visual confirmation remains for reviewer or capable E2E pass.
- [~] E2E authored for BUG-2/BUG-4 (run on a capable machine before calling the whole plan done).
  Authored in earlier phases and intentionally not run per plan.
- [x] OQ-01 (4d back-exit) still open, tracked.
