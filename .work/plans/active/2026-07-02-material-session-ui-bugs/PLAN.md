<!--
  This is the verbatim operating-manual preamble. It is pasted as the first content
  of every plan written by the write-implementation-plan skill. Do NOT modify it
  per-plan — keeping it identical across plans means implementing agents learn
  the protocol once and recognize it everywhere.
-->

# How to use this plan

> **You are the implementing agent.** This document is your runbook for one cohesive change to this codebase. It was written collaboratively by Claude and a human after a planning discussion, and it is the source of truth for this work. Read this preamble in full before doing anything else.

## What you're holding

A phase-by-phase implementation plan. Each phase is a **vertical slice** — an end-to-end working increment that leaves the codebase in a working state. Phases are designed so any one of them can be implemented by a fresh agent in a new context window, with only this document and the codebase as input.

## Your job

1. **Read the document header in full first.** TL;DR, Context, Decisions log, Architecture overview, and Files-touched index. These give you the *why* behind every step. The Decisions log especially — those decisions were made deliberately and explain choices that may otherwise look arbitrary or wrong. Reference IDs (D-NN) appear inside phase steps so you can look up rationale.

2. **Find your starting phase.** Scan the phase list. Pick the first phase whose status is `☐ Not started` AND whose `Depends on:` phases are all `✅ Complete`. Implement that phase only. **Do not skip ahead. Do not implement multiple phases in one go unless the human explicitly asks.**

3. **Run the prereq verification.** Each phase has a "Verification (run BEFORE starting)" block. Run those commands. **If any fail, STOP** — the codebase isn't in the state this phase expects. Surface to the human: "Phase N's prereqs failed: `<command>` returned `<result>`. Want me to investigate or hand back?"

4. **Follow the steps in order.** Code blocks in steps are the actual code, not pseudocode or sketches. Apply them as written.

5. **If reality doesn't match the step — STOP.** If the plan says "modify line 47 of `auth.py`" and line 47 is something different, do not improvise. Surface the discrepancy: "Plan expected `<X>` at `auth.py:47`, found `<Y>`. Possible causes: plan is stale, file was edited since planning, plan was wrong. How should I proceed?"

6. **Run the tests and post-verification.** Each phase specifies what tests to add or update and the bash command to run. All must pass before the phase is considered done.

7. **Update status and commit.** When the phase is complete:
   - Edit this document: change the phase's `Status:` line to `✅ Complete — <commit-sha-here>`.
   - `git add` the code changes AND this plan file.
   - Commit them together. Suggested message: `Phase N: <phase title>` (with longer body referencing the plan file).
   - The status update and the code change live in the same commit so the doc and the code never drift.

## What you must NOT do

- **Do not skip phases.** Order matters; later phases assume earlier ones completed.
- **Do not modify the Decisions log, the Operating manual preamble, the TL;DR, the Architecture overview, the Files-touched index, the Open questions, the Out-of-scope list, or the References.** Those are immutable above-the-phases content. If you discover a decision is wrong, surface to the human — don't silently revise.
- **Do not re-plan or re-architect.** If the plan seems wrong, that's a signal to stop and surface, not to improvise.
- **Do not implement multiple phases without surfacing for human review** between them, unless the user explicitly asked for batch execution upfront.

## If you get stuck

- Update the phase's `Status:` to `🛑 Blocked: <one-line reason>`.
- Fill in the phase's `Notes (filled in during implementation)` block with what you tried, what's blocking, and what you'd want to know to unblock.
- Hand back to the human.

## Status vocabulary

- `☐ Not started`
- `🟡 In progress`
- `🛑 Blocked: <reason>`
- `✅ Complete — <commit-sha>`

## When status markers and reality drift

The status markers are a fast read, but they are not the source of truth. The phase's `Verification (DONE)` commands are the truth — if you suspect a marker is wrong (someone forgot to update, branches diverged, partial commits, etc.), run the verification commands for the phases marked complete. Trust the commands over the markers, and surface the drift to the human so the markers can be corrected.

---

## Cowork operating notes for THIS plan (repo-specific)

- **Step 0 — before writing any code:** commit these planning docs verbatim so later diffs are meaningful:
  `docs(plan): add material-session-ui-bugs PLAN + VERIFICATION`. (Cowork cannot commit — the native side establishes the baseline.)
- **After each phase**, fill your section of [`VERIFICATION.md`](./VERIFICATION.md) (files changed, commit SHA, what you did, deviations + why, self-check vs. the phase's acceptance criteria) and expect review. **A phase is not done until the reviewer marks it `✅ Verified`**; change requests may follow.
- **Phase 4's visual contract is the approved mock** [`mocks/proposed/study-day-indicator.html`](./mocks/proposed/study-day-indicator.html) (renders with **real** app CSS copied into `mocks/real-css/`). Build the study-day indicator to it.
- **Project rules** live in `.agents/rules/*.agents.md` (Codex) / `.claude/rules/*.md` (Sonnet); cite the relevant one per phase.
- **E2E tests: author only, do not run** (environment constraint — see repo `CLAUDE.md`). Vitest unit tests DO run.
- **These are five independent bug fixes.** Phases have **no cross-dependencies** — each can be picked up and shipped on its own. Ordered easiest→most-involved, not by dependency.

---

# Material-session UI bug fixes (roadmap + onboarding + burn-up)

**Slug:** `material-session-ui-bugs`
**Date written:** 2026-07-02
**Author:** Claude + Rohit
**Plan status:** Draft
**Upstream:** post-ship review of [`2026-06-30-material-session-decoupling`](../2026-06-30-material-session-decoupling/PLAN.md); triage log [`SCRATCHPAD.md`](./SCRATCHPAD.md)

## TL;DR

Five independent UI defects surfaced during hands-on review of the material↔session decoupling work. Fix them as five standalone vertical slices: (1) remove the duplicate **"Edit & add"** roadmap-hero button; (2) **center the booking sheets** (they're stuck bottom-clipped on all viewports); (3) give the **<560px calendar a way to add/book a session** (none exists today); (4) add a **study-day indicator** (tinted cells) across all calendars plus onboarding-preview legibility fixes (recolor booked chip, tooltip, kill false hover-lift) — built to an approved mock; (5) fix the **burn-up chart** (broken "planned" baseline from retired slots, duplicated axis labels, degenerate domain, blobby curve). All fixes are client-side TS/CSS; no Python service or event-model changes.

## Context & background

The material↔session decoupling shipped (all 7 phases verified, `.work/plans/active/2026-06-30-material-session-decoupling/`). Using the running app, Rohit found five UI issues. Two are regressions tied to that change (BUG-4's onboarding preview, BUG-5's "planned" baseline which still reads the now-retired `roadmap.slots`); three are latent gaps (BUG-1 modal centering, BUG-2 mobile add-session, BUG-3 duplicate button). Each was diagnosed against real code during the review; this plan consolidates the agreed fixes.

Constraints: keep the event model and intelligence math untouched; keep rendering client-side (Rohit chose to fix the burn-up chart in-place rather than move to Python rendering — see D-05); match the Marginalia design system; per-user Dexie isolation and the booking event model from the decoupling work are unaffected.

**Support docs:**

- Triage / root-cause log: [`SCRATCHPAD.md`](./SCRATCHPAD.md)
- Phase-4 visual contract (approved): [`mocks/proposed/study-day-indicator.html`](./mocks/proposed/study-day-indicator.html)
- Upstream plan: [`../2026-06-30-material-session-decoupling/PLAN.md`](../2026-06-30-material-session-decoupling/PLAN.md)
- Rules: `.agents/rules/{css-workspace-packages,form-design-spacing,react-router-v7-basename,roadmap-engine}.agents.md`

## Decisions log

### D-01: BUG-3 — collapse to one roadmap-hero button

**Status:** ✅ Agreed
**Context:** `Open plan` and `Edit & add` on the active-roadmap hero both `<Link to="/roadmap">` — same page, no difference; "add material to an existing roadmap" isn't implemented anywhere (`MaterialAdded` only emitted from onboarding).
**Decision:** Remove `Edit & add` entirely; keep a single `Open plan`. Editing (inline booking edits) and `Replan` already live on the opened page.
**Rationale:** Two affordances must not produce one identical outcome; the second promised a capability that doesn't exist.
**Alternatives considered:** repoint secondary → `/replan` → rejected by Rohit (wants one button); build add-material flow → deferred (separate future feature).
**User pushback:** Rohit: "Remove the button Edit & Plan entirely. Let there be one Open Plan button."
**Reversibility:** easy.

### D-02: BUG-1 — center the booking sheets on all viewports

**Status:** ✅ Agreed
**Context:** `.bk-overlay`/`.bk-sheet` are a bespoke bottom-sheet (`align-items:flex-end`, top-only radius) with no responsive rule; they read as clipped/stuck on both desktop and mobile.
**Decision:** Center on all viewports: `.bk-overlay { align-items:center }`, `.bk-sheet { border-radius: var(--radius-lg); max-height: calc(100dvh - var(--space-6)); overflow-y:auto }`. Fixes all four sheets (shared class).
**Rationale:** Rohit confirmed the same behaviour on mobile and wants it centered; `max-height`+`overflow-y` prevents a tall centered sheet clipping on short screens.
**Alternatives considered:** desktop-only `@media(min-width:1024px)` centering (mock's original) → rejected (Rohit wants centered on mobile too); consolidate onto the design-system `.modal-overlay center`/`.modal-card` used by `SessionDetailModal` → deferred as a follow-up (bigger diff).
**Reversibility:** easy.

### D-03: BUG-2 — DaySheet becomes the mobile day hub (empty days tappable + add-session)

**Status:** ✅ Agreed
**Context:** Below 560px the calendar is dot-view; the `+ add session` affordance only exists in the desktop branch, and the empty-day mobile button is `disabled`, so there is no path to add a booking. The `DaySheet` it opens is view-only.
**Decision:** Make empty in-month days tappable in compact mode; add a `+ Add session` action + empty-state to `DaySheet`; wire it to the existing `AddSessionSheet`/`handleCreateBooking`.
**Rationale:** Reuses the existing add flow; per-day tap pre-sets the date. Cleaner than a floating "+" FAB (which needs a separate date picker).
**Alternatives considered:** floating "+" FAB → rejected (less precise, extra UI).
**Reversibility:** easy.

### D-04: BUG-4 — study-day tint across all calendars + onboarding preview legibility

**Status:** ✅ Agreed (mock approved)
**Context:** Onboarding preview shows a green (done-styled) session bubble for a *future* booking, clipped label, false hover-lift, and no cue for why sessions land on their dates.
**Decision:** (a) shared `.roadmap-day-studyday` moss-8% tint on every in-month cell whose weekday ∈ selected study days, applied to **both** the roadmap calendar and the onboarding preview, + "Study day" legend entry + study-day weekday-header emphasis; (b) recolor the onboarding session bubble `roadmap-chip-done` → `roadmap-chip-booked` with a `title`+`aria-label`; (c) scope the `.roadmap-day-in-month:hover` lift so it does NOT apply inside `.onboarding-mini-calendar` (read-only). Built to the approved mock.
**Rationale:** The tint answers "why this day" visually; green must stay reserved for completed; the preview is read-only so it must not imply clicks.
**Alternatives considered:** dot marker / header-only emphasis → rejected (tint reads best with bubbles inside); onboarding-only scope → rejected (Rohit: "all calendars").
**User pushback:** Rohit approved the real-CSS mock after v1 (mock-CSS copies) looked wrong.
**Reversibility:** easy.

### D-05: BUG-5 — fix the burn-up chart client-side; rebuild "planned" from capacity

**Status:** ✅ Agreed
**Context:** `buildPlannedCumulative(roadmap.slots)` now reads booking-synthesized slots (few, sparse) → a near-flat "planned" baseline; plus coarse y-axis formatter, degenerate x-domain on empty data, and `curveBasis` overshoot.
**Decision:** Keep the chart client-side (@visx); do NOT move rendering to Python.
Rebuild "planned" as a capacity-shaped cumulative over `startDate..deadline` using the live booking-capacity semantics: on each selected study day, add `weekdayHours * 60` for Mon-Fri and `weekendHours * 60` for Sat-Sun.
Do not use the legacy slot-grid split (`weekdayHours / weekdayCount`, `weekendHours / weekendCount`) for this burn-up fix.
Fix the axis formatter (h+m, dedupe), guard degenerate/empty domains (+ empty state), swap `curveBasis`→`curveMonotoneX`, and base the y-domain on the data not the inflated GP upper.
This plan intentionally resolves the upstream target-line OQ for the product burn-up chart: the Week chart reference line is capacity-shaped, not linear-to-deadline.
**Rationale:** The mess is data + config bugs, not a rendering-library limit; Python rendering adds a round-trip, loses interactivity/theming, and couples a view to an undeployed service. Python plotting stays the tool for research/dissertation figures only.
**Alternatives considered:** matplotlib PNG/SVG from `/v1/progress` → rejected (static, latency, theming, service gating); Plotly.js → rejected (heavy, still client render).
**User pushback:** Rohit floated Python; accepted Option A ("Sure A then").
**Reversibility:** moderate (planned-baseline change alters the "vs plan" semantics — intended).

### D-06: BUG-4 4d (back-to-/roadmaps exit) is out of scope here

**Status:** ⚠️ Deferred
**Context:** Re-entrant onboarding (via "Resume setup") has no exit to `/roadmaps` except browser-back.
**Decision:** Not fixed in this plan (Rohit: "move on"). Tracked as OQ-01.
**Reversibility:** easy.

## Architecture overview

Five isolated client-side fixes, no shared runtime coupling:

```
BUG-3  apps/app/src/pages/Roadmaps.tsx            — delete one <Link>
BUG-1  apps/app/src/roadmap/roadmap.css           — .bk-overlay / .bk-sheet centering (4 sheets share it)
BUG-2  CalendarCell.tsx + DaySheet.tsx + RoadmapCalendar.tsx  — mobile add-session entry point
BUG-4  roadmap.css (+ shared class) + RoadmapCalendar.tsx + CalendarCell.tsx + Step3Preview.tsx  — study-day tint + preview fixes
BUG-5  packages/progress/src/progress.ts (planned baseline) + apps/app/src/components/BurnUpChart.tsx (axes/domain/curve)
```

Data facts to rely on (verified in code, do not re-derive):
- `@study-tracker/progress` `RoadmapInput` exposes `startDate, deadline, selectedStudyDays?, weekdayHours?, weekendHours?`.
  The fields are optional in the progress package for legacy compatibility, so Phase 5 must fall back to the old slot-based series when any capacity field is missing or `selectedStudyDays` is empty.
- The live booking path does **not** split weekday/weekend hours across the selected days.
  `generateBookings` uses `capacityForBookingDay(day, input) = (isWeekend(day) ? weekendHours : weekdayHours) * 60`.
  The Phase 5 burn-up planned baseline must mirror that booking-capacity semantics.
- Do not import `apps/app/src/session/sessionPlanning.ts` from `packages/progress`.
  The app-layer `dailyCapacityForDate` can be read as a reference only; `packages/progress` needs its own small pure helper.
- Booking sheets `BookingEditorSheet`/`AddSessionSheet`/`MaterialPickerSheet`/`MaterialProgressSheet` all render `.bk-overlay > .bk-sheet` (`apps/app/src/roadmap/booking/*.tsx`).
- `AddSessionSheet` props: `{ date, materials, capMinutes, onClose, onCreate }`; wired in `RoadmapCalendar` via `addSessionDate` state + `handleCreateBooking` (emits `SessionBooked`).

## Files touched (index)

| Path | Change | Phase | Purpose |
|------|--------|-------|---------|
| `apps/app/src/pages/Roadmaps.tsx` | modify | 1 | Remove the `Edit & add` link |
| `apps/app/src/pages/Roadmaps.test.tsx` | modify | 1 | Drop the `Edit & add` assertion |
| `apps/app/src/roadmap/roadmap.css` | modify | 2,4 | Center booking sheets (2); study-day tint + onboarding no-lift (4) |
| `apps/app/src/roadmap/CalendarCell.tsx` | modify | 2,4 | Empty-day tappable in compact (2); study-day class (4) |
| `apps/app/src/roadmap/DaySheet.tsx` | modify | 2 | Add-session action + empty state |
| `apps/app/src/roadmap/RoadmapCalendar.tsx` | modify | 2,4 | Wire DaySheet add (2); study-day set + legend (4) |
| `apps/app/src/onboarding/steps/Step3Preview.tsx` | modify | 4 | Recolor session chip, tooltip, study-day tint, legend |
| `apps/app/src/onboarding/onboarding.css` | modify | 4 | Study-day legend swatch |
| `packages/progress/src/progress.ts` | modify | 5 | Capacity-based `planned` baseline |
| `packages/progress/src/types.ts` | modify | 5 | Add optional `burnUp.startDate` / `burnUp.deadline` domain hints |
| `apps/app/src/components/BurnUpChart.tsx` | modify | 5 | Axis formatter, domain guard, curve, y-domain, empty state |
| `packages/progress/src/progress.test.ts` | modify | 5 | Planned-baseline tests |
| test files per phase | modify | 1,3,4,5 | Cover behavior and rendering changes |

## Phases

---

### Phase 1: Remove the duplicate "Edit & add" roadmap-hero button (BUG-3)

**Status:** ☐ Not started
**Depends on:** none — can start immediately
**Estimated scope:** ~2 files, ~6 lines

#### Codebase state assumed at start
- `apps/app/src/pages/Roadmaps.tsx` renders two links in `.rmd-actions`: `Open plan` and `Edit &amp; add`, both `to="/roadmap"` (~lines 172–177).
- `apps/app/src/pages/Roadmaps.test.tsx` asserts both links' hrefs (~lines 133–134).

#### Verification (run BEFORE starting)
```bash
grep -n "Edit &amp; add\|Open plan" apps/app/src/pages/Roadmaps.tsx      # both present
grep -n "Edit & add" apps/app/src/pages/Roadmaps.test.tsx               # assertion present
```

#### Steps
1. **Modify `apps/app/src/pages/Roadmaps.tsx`, `.rmd-actions` block (currently ~lines 171–185):** delete the second link only. Implements D-01.
   ```tsx
   <div className="rmd-actions">
     <Link className="btn btn-accent" to="/roadmap">
       Open plan
     </Link>
     <button
       className="btn btn-ghost"
       type="button"
       onClick={() => setShowCloseControls((shown) => !shown)}
     >
       Close plan
     </button>
   </div>
   ```
   (Removes the `<Link className="btn btn-secondary" to="/roadmap">Edit &amp; add</Link>`.)
2. **Modify `apps/app/src/pages/Roadmaps.test.tsx` (~line 134):** delete the `Edit & add` assertion; keep the `Open plan` href assertion.

#### Tests
- Update `Roadmaps.test.tsx` — remove the `Edit & add` link assertion; keep `Open plan` → `/roadmap`.
- Run: `pnpm --filter @study-tracker/app test -- Roadmaps`

#### Verification (DONE)
```bash
grep -n "Edit &amp; add" apps/app/src/pages/Roadmaps.tsx     # returns nothing
pnpm --filter @study-tracker/app typecheck && pnpm --filter @study-tracker/app test -- Roadmaps
```

#### Rollback
Re-add the removed `<Link>` and the test assertion.

#### Notes (filled in during implementation)
*(empty)*

---

### Phase 2: Center the booking sheets on all viewports (BUG-1)

**Status:** ☐ Not started
**Depends on:** none — can start immediately
**Estimated scope:** ~1 file, ~6 lines CSS

#### Codebase state assumed at start
- `apps/app/src/roadmap/roadmap.css` has `.bk-overlay` (~line 773, `align-items: flex-end`), `.bk-sheet` (~line 784, `border-radius: var(--radius-xl) var(--radius-xl) 0 0`), `.bk-grip` (~line 793). No `@media` desktop centering exists for `.bk-sheet`.
- Four sheets share these classes: `BookingEditorSheet`, `AddSessionSheet`, `MaterialPickerSheet`, `MaterialProgressSheet`.

#### Verification (run BEFORE starting)
```bash
grep -n "align-items: flex-end" apps/app/src/roadmap/roadmap.css   # in .bk-overlay
grep -n "\.bk-sheet" apps/app/src/roadmap/roadmap.css              # ~784
```

#### Steps
1. **Modify `apps/app/src/roadmap/roadmap.css`, `.bk-overlay` (~line 773):** center vertically. Implements D-02.
   ```css
   .bk-overlay {
     position: fixed;
     inset: 0;
     z-index: var(--z-modal);
     display: flex;
     align-items: center;            /* was: flex-end */
     justify-content: center;
     padding: var(--space-4);
     background: rgba(42, 31, 24, 0.4);
   }
   ```
2. **Modify `.bk-sheet` (~line 784):** full radius + scroll guard.
   ```css
   .bk-sheet {
     width: 100%;
     max-width: 460px;
     max-height: calc(100dvh - var(--space-6));   /* new: tall sheet scrolls, no clip */
     overflow-y: auto;                            /* new */
     padding: var(--space-5) var(--space-5) var(--space-6);
     border-radius: var(--radius-lg);             /* was: --radius-xl --radius-xl 0 0 */
     background: var(--surface-card);
     box-shadow: var(--shadow-modal);
   }
   ```
3. **Modify `.bk-grip` (~line 793):** hide the drag handle because it is a bottom-sheet affordance, not a centered modal affordance.
   ```css
   .bk-grip {
     display: none;
   }
   ```

#### Tests
- No unit test asserts sheet geometry; verify visually. If you run the app, open any booking sheet on desktop and a ≤560px viewport and confirm it's centered and scrolls when tall.
- Run: `pnpm --filter @study-tracker/app typecheck`

#### Verification (DONE)
```bash
grep -n "align-items: center" apps/app/src/roadmap/roadmap.css     # in .bk-overlay
grep -n "max-height: calc(100dvh" apps/app/src/roadmap/roadmap.css # in .bk-sheet
grep -n "\.bk-grip" -A4 apps/app/src/roadmap/roadmap.css           # display:none present
pnpm --filter @study-tracker/app typecheck
```

#### Rollback
Restore the three original rule bodies.

#### Notes (filled in during implementation)
*(empty)*

---

### Phase 3: Add-session entry point on the <560px calendar (BUG-2)

**Status:** ☐ Not started
**Depends on:** none — can start immediately
**Estimated scope:** ~3 files, ~40 lines

#### Codebase state assumed at start
- `apps/app/src/roadmap/CalendarCell.tsx`: `isCompact = useMatchMedia('(max-width: 560px)')` (~line 70); `canOpenDay = isCompact && day.isInMonth && day.bubbles.length > 0` (~line 74); the mobile day button is `disabled={!canOpenDay}`; the `+ add session` button (`showAddSession`) renders ONLY in the non-compact branch (~lines 165–173).
- `apps/app/src/roadmap/DaySheet.tsx`: view-only; props `{ day, onClose, onSelectBubble }`; maps `day.bubbles` only.
- `apps/app/src/roadmap/RoadmapCalendar.tsx`: renders `<DaySheet day={selectedSheetDay} .../>` (~line 625); has `setAddSessionDate` + `handleCreateBooking` + `<AddSessionSheet .../>` (~line 642); `readOnly` prop exists.

#### Verification (run BEFORE starting)
```bash
grep -n "canOpenDay" apps/app/src/roadmap/CalendarCell.tsx          # ~74
grep -n "onSelectBubble\|day.bubbles.map" apps/app/src/roadmap/DaySheet.tsx
grep -n "setAddSessionDate\|<DaySheet" apps/app/src/roadmap/RoadmapCalendar.tsx
```

#### Steps
1. **`CalendarCell.tsx` (~line 74):** let empty in-month days open in compact mode. Implements D-03.
   ```tsx
   const canOpenDay = isCompact && day.isInMonth
   ```
   (Drops `&& day.bubbles.length > 0`. The dot-stack renders empty for 0 bubbles, which is fine — the tap now opens the DaySheet where Add lives.)
   Also update the compact button's `aria-label` so empty days do not claim they already have sessions:
   ```tsx
   aria-label={day.bubbles.length > 0 ? `Open ${day.date} sessions` : `Open ${day.date} day options`}
   ```
2. **`DaySheet.tsx`:** add props and an add-session action + empty state.
   ```tsx
   interface DaySheetProps {
     day: BoundCalendarDay | null
     onClose: () => void
     onSelectBubble: (bubble: CalendarBubble) => void
     onAddSession?: (date: string) => void
     canAddSession?: boolean
   }
   ```
   In the body, after the list, render the empty state + add button (only when `canAddSession`):
   ```tsx
   {day.bubbles.length === 0 && (
     <p className="roadmap-day-sheet-empty">No sessions booked for this day.</p>
   )}
   {canAddSession && onAddSession && (
     <button
       type="button"
       className="btn btn-accent btn-block roadmap-day-sheet-add"
       onClick={() => onAddSession(day.date)}
     >
       + Add session
     </button>
   )}
   ```
   Destructure the new props in the component signature.
3. **`RoadmapCalendar.tsx`, `<DaySheet .../>` (~line 625):** wire add → existing AddSessionSheet, closing the day sheet first.
   ```tsx
   <DaySheet
     day={selectedSheetDay}
     onClose={() => setSelectedSheetDay(null)}
     onSelectBubble={handleDayBubbleSelect}
     canAddSession={!readOnly}
     onAddSession={(date) => { setSelectedSheetDay(null); setAddSessionDate(date) }}
   />
   ```
4. **`roadmap.css`:** add minimal styles for `.roadmap-day-sheet-empty` (muted, `var(--text-tertiary)`, small) and `.roadmap-day-sheet-add` (top margin `var(--space-3)`), matching the sheet's existing spacing.

#### Tests
- Update `apps/app/src/roadmap/RoadmapCalendar.test.tsx`.
  The file currently mocks `../lib/useMatchMedia` as always `false`, so first make the mock configurable:
  ```tsx
  const mockViewport = vi.hoisted(() => ({ isCompact: false }))

  vi.mock('../lib/useMatchMedia', () => ({
    useMatchMedia: () => mockViewport.isCompact,
  }))
  ```
  Reset `mockViewport.isCompact = false` in `beforeEach`.
  In the compact-path test, set `mockViewport.isCompact = true`, open an empty in-month day, assert the `+ Add session` action appears in the `DaySheet`, click it, assert the day sheet closes, assert `AddSessionSheet` opens with that date, then create the booking and assert `SessionBooked`.
- Add or update a read-only compact test.
  Render a historical/read-only calendar with `mockViewport.isCompact = true`, open a day, and assert `+ Add session` is absent.
  Follow `.agents/rules/dexie-test-setup.agents.md` if any test starts using a real Dexie store.
- Author (do not run) a Playwright case in `e2e/material-session-decoupling.spec.ts`: at ≤560px, open an empty day → Add session → booking appears.
  The test must set a viewport below 560px, for example `page.setViewportSize({ width: 390, height: 844 })`, before visiting `/study/roadmap`.
  This is required because the existing desktop booking E2E coverage never exercises the compact `DaySheet` path.
- Run: `pnpm --filter @study-tracker/app test -- RoadmapCalendar DaySheet`

#### Verification (DONE)
```bash
grep -n "onAddSession" apps/app/src/roadmap/DaySheet.tsx apps/app/src/roadmap/RoadmapCalendar.tsx   # present in both
pnpm --filter @study-tracker/app typecheck && pnpm --filter @study-tracker/app test -- RoadmapCalendar
```

#### Rollback
Revert the four edits; the mobile empty-day button returns to disabled.

#### Notes (filled in during implementation)
*(empty)*

---

### Phase 4: Study-day indicator across all calendars + onboarding preview legibility (BUG-4)

**Status:** ☐ Not started
**Depends on:** none — can start immediately
**Estimated scope:** ~5 files, ~80 lines. **Visual contract:** [`mocks/proposed/study-day-indicator.html`](./mocks/proposed/study-day-indicator.html).

#### Codebase state assumed at start
- `roadmap.css` has `.roadmap-day`, `.roadmap-day-today` (`--cal-today-fill`), `.roadmap-day-current-week` (`--cal-week-band`), and `@media (pointer: fine) { .roadmap-day-in-month:hover { transform… } }` (the lift).
- `RoadmapCalendar.tsx` has `roadmap.selectedStudyDays` available; renders `<CalendarCell>` per day and the legend via `LEGEND_ITEMS` (`statusStyles.ts`).
- `CalendarCell.tsx` builds the cell class list (~lines 76–84).
- `Step3Preview.tsx` renders the onboarding mini-calendar (`.roadmap-calendar-shell onboarding-mini-calendar`), a session bubble as `roadmap-bubble roadmap-chip-done` (~lines 348–360), `state.selectedStudyDays` available, and a `.cal-legend` (~lines 370–374).

#### Verification (run BEFORE starting)
```bash
grep -n "roadmap-day-in-month:hover" apps/app/src/roadmap/roadmap.css
grep -n "selectedStudyDays" apps/app/src/roadmap/RoadmapCalendar.tsx apps/app/src/onboarding/steps/Step3Preview.tsx
grep -n "roadmap-chip-done" apps/app/src/onboarding/steps/Step3Preview.tsx
```

#### Steps
1. **`roadmap.css` — add the shared indicator** (implements D-04). Place near the other `.roadmap-day-*` rules:
   ```css
   .roadmap-day-studyday { background: color-mix(in srgb, var(--moss) 8%, var(--surface-card)); }
   .roadmap-day-current-week.roadmap-day-studyday { background: color-mix(in srgb, var(--moss) 8%, var(--cal-week-band)); }
   .roadmap-day-today.roadmap-day-studyday,
   .roadmap-day-today.roadmap-day-current-week.roadmap-day-studyday {
     background: var(--cal-today-fill);
   }
   .roadmap-weekday.roadmap-weekday-studyday { color: var(--moss); font-weight: 600; }
   .roadmap-legend-swatch.roadmap-studyday-swatch {
     background: color-mix(in srgb, var(--moss) 8%, var(--surface-card));
     border: 1px solid color-mix(in srgb, var(--moss) 32%, var(--surface-card));
   }
   ```
   The order and combined today selector matter: if a date is both today and in the current week, today keeps `--cal-today-fill`.
   And **scope the hover-lift off the onboarding mini-calendar** (read-only):
   ```css
   .onboarding-mini-calendar .roadmap-day-in-month:hover { transform: none; box-shadow: none; z-index: auto; }
   .onboarding-mini-calendar .roadmap-day { cursor: default; }
   ```
2. **Add the shared weekday helper in `apps/app/src/roadmap/calendarModel.ts`:** keep it beside the existing month-grid helpers so both `RoadmapCalendar` and `Step3Preview` import one source of truth.
   Use the repo's UTC ISO-date weekday convention, matching `sessionPlanning.ts`, `mapEvents.ts`, and `packages/progress/src/progress.ts`.
   Do **not** use `parseISO(dateISO).getDay()` here, because that introduces a local-time weekday convention for study-day matching.
   Do **not** use `new Date(`${dateISO}T00:00:00`)`; that also depends on local timezone.
   ```ts
   const STUDY_DAY_BY_INDEX = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as const

   export function dayOfWeekForISODate(dateISO: string): string {
     return STUDY_DAY_BY_INDEX[new Date(`${dateISO}T00:00:00.000Z`).getUTCDay()]
   }

   export function isStudyDay(dateISO: string, studyDays: readonly string[] | undefined): boolean {
     if (!studyDays?.length) return false
     return studyDays.includes(dayOfWeekForISODate(dateISO))
   }
   ```
   Add `calendarModel.test.ts` coverage for known dates, including `2026-07-06` → `Mon`, `2026-07-07` → `Tue`, and `2026-07-12` → `Sun`.
3. **`CalendarCell.tsx`:** accept `isStudyDay?: boolean` and add `'roadmap-day-studyday'` to the class list when true.
   `RoadmapCalendar.tsx`: pass `isStudyDay={day.isInMonth && isStudyDay(day.date, roadmap.selectedStudyDays)}` when rendering each `<CalendarCell>`.
   Do not tint outside-month filler cells.
   Add the study-day weekday-header class to the header cells whose weekday is a study day.
   Add a **"Study day"** legend entry (static span with `roadmap-legend-swatch roadmap-studyday-swatch`) alongside the status legend.
4. **`Step3Preview.tsx` + `onboarding.css`:** (a) add `roadmap-day-studyday` to each mini-calendar in-month cell where `day.isInMonth && isStudyDay(day.date, state.selectedStudyDays)`; (b) recolor the session bubble from `roadmap-chip-done` → `roadmap-chip-booked` and add `title` + `aria-label` (e.g. ``Booked study session · ${formatMinutes(booking.estimatedDuration)} · ${format(parseISO(booking.date),'EEE, MMM d')}``); (c) add a "study day" entry to `.cal-legend`; (d) add `.cal-swatch.studyday` in `apps/app/src/onboarding/onboarding.css` with the same moss tint as `.roadmap-studyday-swatch`; (e) update `.cal-swatch.booked` so the legend no longer presents a moss/green booked session swatch after the booked bubble moves to the outline style; (f) the mini-calendar already has `onboarding-mini-calendar` so the Step-1 hover override applies.
   Keep the buffer caption; the tint replaces the "why the 7th" prose.
5. Honour rules: `.agents/rules/css-workspace-packages.agents.md`, `.agents/rules/form-design-spacing.agents.md`. Match the approved mock.

#### Tests
- `CalendarCell.test.tsx` / `RoadmapCalendar.test.tsx`: a study-day in-month cell gets `roadmap-day-studyday`; a non-study day does not; legend shows "Study day".
  Also assert an outside-month filler cell is not tinted even when its weekday is selected.
- New `calendarModel`/util test for `isStudyDay` (weekday mapping correctness — the load-bearing bit).
- `Step3Preview.test.tsx`: session bubble uses `roadmap-chip-booked` (not `-done`) and has a `title`; study-day cells tinted; the legend still includes booked session and now includes study day.
- Author (not run) Playwright: `/onboarding/3?new=1` shows tinted study-day columns and a booked-style session chip.
- Run: `pnpm --filter @study-tracker/app test -- CalendarCell RoadmapCalendar Step3Preview calendarModel`

#### Verification (DONE)
```bash
grep -n "roadmap-day-studyday" apps/app/src/roadmap/roadmap.css apps/app/src/roadmap/CalendarCell.tsx apps/app/src/onboarding/steps/Step3Preview.tsx
grep -n "roadmap-chip-booked" apps/app/src/onboarding/steps/Step3Preview.tsx   # session recolored
pnpm --filter @study-tracker/app typecheck && pnpm --filter @study-tracker/app test -- CalendarCell RoadmapCalendar Step3Preview
```

#### Rollback
Revert the CSS additions + the `isStudyDay` wiring + the Step3Preview chip recolor.

#### Notes (filled in during implementation)
*(empty)*

---

### Phase 5: Fix the burn-up chart — planned baseline + axes/domain/curve (BUG-5)

**Status:** ☐ Not started
**Depends on:** none — can start immediately
**Estimated scope:** ~4 files, ~130 lines

#### Codebase state assumed at start
- `packages/progress/src/progress.ts`: `buildPlannedCumulative(slots)` (~line 30) + `computeProgress` builds `burnUp.planned = buildPlannedCumulative(roadmap.slots)` (~line 216) and `deficit = lastActual - lastPlanned`. `roadmap` (RoadmapInput) has `startDate, deadline, selectedStudyDays, weekdayHours, weekendHours`.
- `apps/app/src/components/BurnUpChart.tsx`: `minutesToLabel(m)=Math.floor(m/60)+'h'` (~line 34); x-domain from min/max of planned+gp dates (~lines 87–109); GP band/mean use `curveBasis`; y-domain `Math.max(...allMinutes)*1.08` where `allMinutes` includes `gp.upper`.

#### Verification (run BEFORE starting)
```bash
grep -n "buildPlannedCumulative\|burnUp\b\|deficit" packages/progress/src/progress.ts | head
grep -n "minutesToLabel\|curveBasis\|allMinutes\|allDates" apps/app/src/components/BurnUpChart.tsx
pnpm --filter @study-tracker/progress test   # baseline green
```

#### Steps
1. **`packages/progress/src/types.ts` — add optional domain hints to `BurnUpData`:**
   ```ts
   export interface BurnUpData {
     planned: CumulativePoint[]
     actual: CumulativePoint[]
     gpCurve: Array<{ date: string; mean: number; lower: number; upper: number }>
     today: string
     startDate?: string
     deadline?: string
     deficit: number
     dayNumber: number
     totalDays: number
   }
   ```
   Keep `startDate` and `deadline` optional so existing tests and mocks that construct `BurnUpData` directly do not all have to change in this phase.
2. **`packages/progress/src/progress.ts` — capacity-based planned baseline** (implements D-05). Add a package-local helper that builds cumulative *planned* minutes over every selected study day from `startDate` to `deadline`, then use it instead of `buildPlannedCumulative(roadmap.slots)`.
   The helper must mirror the live booking path, not the legacy slot-grid path:
   ```ts
   const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] as const

   function hasCapacityFields(roadmap: RoadmapInput): roadmap is RoadmapInput & {
     selectedStudyDays: string[]
     weekdayHours: number
     weekendHours: number
   } {
     return Array.isArray(roadmap.selectedStudyDays) &&
       roadmap.selectedStudyDays.length > 0 &&
       typeof roadmap.weekdayHours === 'number' &&
       typeof roadmap.weekendHours === 'number'
   }

   function capacityForStudyDay(day: string, roadmap: { weekdayHours: number; weekendHours: number }): number {
     const hours = day === 'Sat' || day === 'Sun' ? roadmap.weekendHours : roadmap.weekdayHours
     return Math.round(Math.max(0, hours) * 60)
   }

   function buildPlannedCumulativeFromCapacity(roadmap: RoadmapInput): CumulativePoint[] {
     if (!hasCapacityFields(roadmap)) return buildPlannedCumulative(roadmap.slots)

     let cumulative = 0
     const planned: CumulativePoint[] = []
     for (let date = roadmap.startDate; date <= roadmap.deadline; date = addDaysISO(date, 1)) {
       const day = DAY_NAMES[new Date(`${date}T00:00:00.000Z`).getUTCDay()]
       if (!roadmap.selectedStudyDays.includes(day)) continue

       cumulative += capacityForStudyDay(day, roadmap)
       planned.push({ date, minutes: cumulative })
     }

     return planned.length > 0 ? planned : buildPlannedCumulative(roadmap.slots)
   }
   ```
   Replace `const plannedCumulative = buildPlannedCumulative(roadmap.slots)` with `buildPlannedCumulativeFromCapacity(roadmap)`.
   Keep `buildPlannedCumulative` as the legacy fallback.
   Recompute `lastPlanned`, `deficit`, and `verdict` from the new series.
   Populate `burnUp.startDate = roadmap.startDate` and `burnUp.deadline = roadmap.deadline`.
   Do not import from `apps/app/src/session/sessionPlanning.ts` or from `@study-tracker/roadmap-engine`.
3. **`BurnUpChart.tsx` — axis formatter and deterministic ticks** (~line 34): export small pure helpers so this behavior is unit-testable.
   ```ts
   export function minutesToLabel(minutes: number): string {
     const safe = Math.max(0, Math.round(minutes))
     const h = Math.floor(safe / 60)
     const min = safe % 60
     if (h === 0) return `${min}m`
     return min === 0 ? `${h}h` : `${h}h ${min}m`
   }

   export function buildMinuteTickValues(maxMinutes: number): number[] {
     const max = Math.max(60, Math.ceil(maxMinutes / 30) * 30)
     const step = max <= 120 ? 30 : max <= 360 ? 60 : 120
     const ticks: number[] = []
     for (let value = 0; value <= max; value += step) ticks.push(value)
     if (ticks[ticks.length - 1] !== max) ticks.push(max)
     return [...new Set(ticks)]
   }
   ```
   Use `tickValues={buildMinuteTickValues(yDomainMax)}` on `AxisLeft` instead of relying only on `numTicks={5}`.
4. **`BurnUpChart.tsx` — degenerate/empty domain guard** (~lines 87–120): include planned, actual, GP, and explicit roadmap-domain dates in the x-domain calculation.
   Export the pure helper so jsdom unit tests do not depend on SVG layout:
   ```ts
   export function buildBurnUpDateDomain(
     hints: Pick<BurnUpData, 'startDate' | 'deadline' | 'today' | 'dayNumber' | 'totalDays'>,
     candidateDates: Date[],
   ): [Date, Date]
   ```
   Build `domainStart` and `domainEnd` from `data.startDate` / `data.deadline` when present.
   If either is missing, derive a fallback from `today`, `dayNumber`, and `totalDays`.
   The x-domain must always include `[domainStart, domainEnd]`, even when planned or GP arrays are sparse.
   Export and use a second pure helper for the empty-state decision:
   ```tsx
   export function hasMeaningfulBurnUpData(
     planned: BurnUpData['planned'],
     actual: BurnUpData['actual'],
   ): boolean {
     const hasMeaningfulPlan = planned.length > 1 || planned.some((point) => point.minutes > 0)
     return actual.length > 0 || hasMeaningfulPlan
   }
   ```
   In the public `BurnUpChart` component, return the empty state before rendering `ParentSize` when `hasMeaningfulBurnUpData(data.planned, data.actual)` is false.
   The empty state copy is: "Log a session to see your burn-up".
5. **`BurnUpChart.tsx` — curves + y-domain:** change the GP band and mean `curve={curveBasis}` → `curve={curveMonotoneX}`.
   Base the primary y-domain on `max(planned, actual, gp.mean)`.
   Include GP upper only as bounded headroom, for example `Math.min(maxGpUpper, primaryMax * 1.25)`, so a wide confidence band cannot flatten the actual and planned lines.
   Apply normal headroom after that bounded max.
   Export this as a pure helper too, for example:
   ```ts
   export function buildBurnUpYDomainMax(series: {
     planned: number[]
     actual: number[]
     gpMean: number[]
     gpUpper: number[]
   }): number
   ```
6. `Week.tsx` needs no behavioral change because it consumes `progress.burnUp` and already gates chart rendering until there are at least three actual points.
   Do not remove that gate in this phase unless Rohit explicitly widens scope.
   The chart's own empty-state tests should render `BurnUpChart` directly, not through `Week`.
   Update any test fixture that fails typechecking only if you made `startDate` / `deadline` required by mistake; they should remain optional.
   Confirm the "N ahead/behind" footer now reflects the corrected `deficit`.

#### Tests
- `progress.test.ts`: new test proving the planned cumulative uses booking-capacity semantics.
  Example: `selectedStudyDays=['Mon','Wed','Sat']`, `weekdayHours=2`, `weekendHours=3`, `startDate='2026-07-06'`, `deadline='2026-07-12'` should yield `Mon 120`, `Wed 240`, `Sat 420`.
  Add a fallback test where capacity fields are missing or `selectedStudyDays=[]`; it must not crash and should use the old slot-based series.
  Add a `deficit` test that uses the new capacity baseline.
- Add `apps/app/src/components/BurnUpChart.test.tsx` for exported helpers and empty state.
  Cover `minutesToLabel`: `45`→`45m`, `90`→`1h 30m`, `120`→`2h`.
  Cover `buildMinuteTickValues` returns unique labels for a low range where the old formatter collapsed.
  Cover `buildBurnUpDateDomain` with sparse/empty chart data and explicit `startDate` / `deadline`.
  Cover `buildBurnUpYDomainMax` so an inflated GP upper cannot flatten the chart beyond the bounded headroom.
  Cover empty-data renders "Log a session to see your burn-up".
- Author (not run) a visual Playwright check of the Week burn-up if practical.
  If it goes through `/study/week`, seed at least three actual data points so the existing Week gate renders `BurnUpChart`.
- Run: `pnpm --filter @study-tracker/progress test && pnpm --filter @study-tracker/app test -- BurnUpChart Week`

#### Verification (DONE)
```bash
grep -n "buildPlannedCumulativeFromCapacity\|startDate" packages/progress/src/progress.ts packages/progress/src/types.ts
grep -n "curveMonotoneX\|buildMinuteTickValues" apps/app/src/components/BurnUpChart.tsx
pnpm --filter @study-tracker/progress test && pnpm --filter @study-tracker/app typecheck && pnpm --filter @study-tracker/app test -- BurnUpChart Week
```

#### Rollback
Revert `progress.ts` to `buildPlannedCumulative(roadmap.slots)` and restore the original `BurnUpChart` formatter/curve/domain.

#### Notes (filled in during implementation)
*(empty)*

---

## Open questions

### OQ-01: Back-to-/roadmaps exit from re-entrant onboarding (BUG-4 4d)
**Why deferred:** Rohit said "move on"; not blocking the tint/legibility fixes.
**Triggers needing resolution:** any re-entrant-onboarding UX work, or user complaints about being stuck in setup.
**Owner / resolution path:** product decision + a small nav affordance in the onboarding preview/layout.
**Cross-ref:** D-06.

## Out of scope

- **Add-material-to-existing-roadmap flow** — not built anywhere today; a separate feature, not part of BUG-3's button removal (D-01).
- **Consolidating `.bk-*` onto the design-system `.modal-overlay`/`.modal-card`** — deferred follow-up to D-02; this plan does the minimal centering fix.
- **Moving any chart rendering to the Python service** — explicitly rejected (D-05); Python plotting stays for research/dissertation figures.
- **Server-side ETA/`/v1/progress` parity** — unchanged; still OQ in the upstream plan.

## References

- Triage log + root causes: [`SCRATCHPAD.md`](./SCRATCHPAD.md)
- Approved visual contract (Phase 4): [`mocks/proposed/study-day-indicator.html`](./mocks/proposed/study-day-indicator.html)
- Upstream decoupling plan: [`../2026-06-30-material-session-decoupling/PLAN.md`](../2026-06-30-material-session-decoupling/PLAN.md)
- Verification log: [`VERIFICATION.md`](./VERIFICATION.md)
- Rules: `.agents/rules/{css-workspace-packages,form-design-spacing,react-router-v7-basename,roadmap-engine,dexie-test-setup}.agents.md`
