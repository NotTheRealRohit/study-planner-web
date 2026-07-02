# Scratchpad — material-session-ui-bugs

_Plan: PLAN.md (5 phases, one per bug) · Log: VERIFICATION.md (acceptance criteria pre-filled) · Updated: 2026-07-02T15:06_

Post-ship UI bug triage and plan-clarity review for the **material ↔ session decoupling** implementation
(`.work/plans/active/2026-06-30-material-session-decoupling/`, all 7 phases marked ✅ Verified 2026-07-02).
This session finds and documents defects surfaced by Rohit against the running app. Reviewer role is
diagnose + document only. Fixes are handed to the coding agents (Codex/Sonnet), not applied here.

## Now
Plan clarity review complete.
Applied the plan amendments Rohit requested after the review.
Main amendments now in `PLAN.md`: Phase 2 requires hiding the bottom-sheet grip, Phase 3 makes the compact-mode test mock configurable, Phase 4 pins helper placement/date semantics and onboarding swatch CSS, and Phase 5 uses concrete booking-capacity semantics with testable chart-domain/tick helpers.

## Alignment
On track with Rohit's review request.
Scope is plan hardening only: identify amendments needed so all five bugs can be implemented without guesswork, and raise only unresolved questions that cannot be settled from local artifacts.

## Bugs (this session)

### BUG-1 — Booking sheets render as bottom-stuck / clipped drawer instead of centered modal
- **Status:** Diagnosed · fix specified · NOT applied (hand to coding agent)
- **Reported:** desktop screenshot (booking editor for Thu Jul 2); Rohit confirms same behaviour on mobile.
- **Affected UI:** all four roadmap booking sheets — they share `.bk-sheet`:
  `apps/app/src/roadmap/booking/{BookingEditorSheet,AddSessionSheet,MaterialPickerSheet,MaterialProgressSheet}.tsx`
- **Issue:** The sheet is pinned to the bottom of the viewport with only top corners rounded, so it
  reads as clipped/cut-off. Backdrop greys and scrolls correctly (overlay is genuinely viewport-fixed
  — structural clip via a transformed ancestor ruled out). It is bottom-anchored on **every** viewport,
  not just desktop.
- **Root cause:** The booking sheets use a bespoke bottom-sheet pair in
  `apps/app/src/roadmap/roadmap.css` instead of the app's standard modal:
  - `.bk-overlay` (line ~773) hardcodes `align-items: flex-end` with **no `.center` modifier and no
    responsive breakpoint** → bottom drawer at all widths.
  - `.bk-sheet` (line ~784) uses `border-radius: var(--radius-xl) var(--radius-xl) 0 0` (top-only) →
    the "clipped" look.
  - The visual-contract mock (`mocks/proposed/roadmap.html:154`) had
    `@media (min-width:1024px){ .bk-sheet { align-self:center; border-radius:var(--radius-lg) } }` — the
    Phase-5 port **dropped that breakpoint entirely**.
  - Divergence from convention: the sibling `SessionDetailModal` on the same page already uses the
    design-system centered modal `.modal-overlay center` + `.modal-card`
    (`packages/design-tokens/src/components.css:866–871`, `.modal-overlay.center { align-items:center }`).
    The booking sheets never adopted it.
- **Fix (centered on all viewports, per Rohit):** in `apps/app/src/roadmap/roadmap.css`:
  ```css
  .bk-overlay { align-items: center; }          /* was: flex-end */
  .bk-sheet {
    border-radius: var(--radius-lg);            /* was: --radius-xl --radius-xl 0 0 */
    max-height: calc(100dvh - var(--space-6));  /* tall sheet scrolls, no top+bottom clip */
    overflow-y: auto;
  }
  .bk-grip { display: none; }                  /* drag handle is a bottom-sheet affordance */
  ```
  `max-height` + `overflow-y` is required: once centered, a sheet taller than a small phone would clip
  at both ends; the old bottom-anchor masked that. One shared `.bk-sheet` fixes all four sheets.
- **Cleaner alternative (follow-up):** retire `.bk-overlay`/`.bk-sheet` and reuse
  `.modal-overlay center` + `.modal-card` like `SessionDetailModal` — one modal convention for the
  roadmap page. Bigger diff (4 components + CSS); kills the divergence permanently.

### BUG-2 — No way to add/book a session from the calendar below 560px wide
- **Status:** Diagnosed · UX + fix specified · NOT applied (hand to coding agent)
- **Reported:** Rohit — "screen < 560px wide, there is no way to add/book session from calendar. Need a UI/UX for it."
- **Affected UI:** mobile calendar path in
  `apps/app/src/roadmap/CalendarCell.tsx` + `apps/app/src/roadmap/DaySheet.tsx`
  (both gate on `useMatchMedia('(max-width: 560px)')`).
- **Issue:** On a phone-width viewport the calendar switches to the compact dot view. There is no
  reachable control to add a booking on an empty day — the "+ add session" affordance simply does not
  exist in this layout, and the empty-day cell isn't even tappable.
- **Root cause (exact):**
  - `CalendarCell` (line 70) computes `isCompact = useMatchMedia('(max-width: 560px)')`. In the compact
    branch (lines 105–131) it renders **only** the dot-stack day button; the `+ add session` button
    (`showAddSession`, lines 165–173) lives **only in the non-compact `else` branch** → never rendered
    on mobile.
  - That mobile day button is `disabled={!canOpenDay}` where
    `canOpenDay = isCompact && day.isInMonth && day.bubbles.length > 0` (line 74). So an **empty** day
    is a disabled button — you can't even open it.
  - The `DaySheet` that a populated day opens (`DaySheet.tsx`) is **view-only**: it lists existing
    bubbles and selects them (lines 53–72); it has **no add-session action** and no empty-state.
  - Net: empty day → disabled, can't open; populated day → opens a sheet with no "add" → **no add path
    at all < 560px.** `handleCreateBooking`/`AddSessionSheet` exist and work; only the mobile *entry
    point* is missing.
- **Fix — make `DaySheet` the mobile day hub (recommended):**
  1. `CalendarCell`: allow opening empty in-month days in compact mode —
     `canOpenDay = isCompact && day.isInMonth` (drop the `bubbles.length > 0` gate) so every in-month
     day is tappable.
  2. `DaySheet`: accept `onAddSession?: (date) => void` + `canAddSession?: boolean`; render a primary
     **"+ Add session"** button (footer or header) that calls `onAddSession(day.date)`, and an
     empty-state line ("No sessions booked — add one") when `day.bubbles.length === 0`.
  3. `RoadmapCalendar`: pass `onAddSession={(date) => { setSelectedSheetDay(null); setAddSessionDate(date) }}`
     and `canAddSession={!readOnly}` into `DaySheet`. This reuses the existing `AddSessionSheet` +
     `handleCreateBooking` (`SessionBooked`) unchanged — the sheet already has a Day/Length control and
     material "Attach", so the date arrives pre-set to the tapped day.
  - Interaction: tapping Add closes the DaySheet and opens AddSessionSheet (avoid stacked sheets).
    Respect `readOnly` (history view shows no Add).
- **Alternative (lighter):** a single floating "+" FAB on the compact calendar → opens AddSessionSheet
  defaulting to today (user can change day). Less precise than per-day tap; use only if the DaySheet
  route is too big for now.
- **Cross-link:** the AddSessionSheet is a `.bk-sheet`, so **BUG-1's centering fix also applies here** —
  fix BUG-1 or this new sheet will pop up bottom-stuck too.

### BUG-3 — "Open plan" and "Edit & add" are duplicate links to the same page
- **Status:** DECIDED (Option A — collapse) · fix specified · NOT applied (hand to coding agent)
- **Decision (Rohit, 2026-07-02):** Remove the "Edit & add" button entirely; keep a single **"Open plan"**
  button. No add-material flow now.
- **Fix (decided):**
  - `apps/app/src/pages/Roadmaps.tsx` — delete the `Edit & add` `<Link>` (lines ~175–177); keep only
    `Open plan` (`btn-accent` → `/roadmap`) and the existing `Close plan` control.
  - `apps/app/src/pages/Roadmaps.test.tsx` — remove the assertion for the `Edit & add` link
    (line ~134); keep the `Open plan` href assertion.
  - Intent 2 (Adjust plan) is still reachable via the `Replan` button already in the roadmap footer;
    Intent 3 (add material to a live roadmap) remains not-built — noted as a separate future feature,
    not part of this fix.
- **Reported:** Rohit — both buttons on the active-roadmap hero go to the same page; what's the
  difference? Wants a UX differentiation.
- **Affected UI:** `apps/app/src/pages/Roadmaps.tsx:171–177` (active-roadmap hero actions).
- **Issue:** `Open plan` (btn-accent) and `Edit & add` (btn-secondary) are **both** `<Link to="/roadmap">`
  — identical destination, no query param, no router state. Two affordances, one outcome → redundant
  and confusing (a distinct button must produce a distinct result).
- **Root cause (exact):**
  - Both links are literally `to="/roadmap"` (lines 172 & 175); the test even asserts both hrefs equal
    `/roadmap` (`Roadmaps.test.tsx:133–134`) — the redundancy was codified, not caught.
  - `/roadmap` with no param is already the **single view+edit surface**: inline booking add/edit/remove
    (`canAddSession`, editable bubbles) **and** a `Replan` button in its own footer
    (`RoadmapCalendar.tsx:611`). The only mode switch on `/roadmap` is `?roadmap=<createdAt>` →
    read-only history (`Roadmap.tsx:5–9`). There is no "edit mode" for `Edit & add` to open.
  - **"add" is a phantom action:** `MaterialAdded` is emitted **only** from onboarding
    (`Step3Preview.tsx:187`). There is **no** flow to add a material to an *existing* roadmap anywhere.
    So "Edit & add" promises something the app can't do.
- **UX options (differentiate by intent — three real, separate intents exist):**
  - Intent 1 **Track/view + tweak bookings** → the calendar (today's `/roadmap`).
  - Intent 2 **Adjust plan shape** (deadline / capacity / shorten-drop) → `/replan` (exists).
  - Intent 3 **Add material to this roadmap** → does not exist yet (would emit `MaterialAdded` + book).
  - **Option A (recommended, honest, smallest): collapse to one.** Keep primary **"Open plan"** →
    `/roadmap`; delete **"Edit & add"** (editing + Replan already live on that page). If add-material is
    wanted, surface an **"Add material"** button *inside* the roadmap Materials-directory panel — a real
    small feature, not a hero twin.
  - **Option B: repoint the secondary to a different real page.** "Open plan" → `/roadmap`; relabel
    "Edit & add" → **"Adjust plan"/"Replan"** → `/replan`. Zero new features, immediately differentiated.
  - **Option C: build the add-material flow** and make "Edit & add" → deep-link
    (`/roadmap?panel=materials` opening the directory with an "Add material" CTA, or the re-entrant
    onboarding materials step scoped to the active roadmap). Biggest scope; delivers the missing Intent 3.
  - Recommendation: **B now** (instant clarity, no new surface) + **A's inline "Add material"** or **C**
    as a follow-up if adding materials to a live roadmap is a real need.
- **Note:** whichever option, drop the test assertion that both hrefs equal `/roadmap`.

### BUG-4 — Onboarding step-3 preview calendar: unreadable/mis-signalling session bubble + no exit
- **Status:** DECIDED (4a/4b/4c) + mock APPROVED by Rohit 2026-07-02 · 4d deferred · NOT applied (hand to coding agent)
- **Reported:** Rohit on `/onboarding/3?new=1` after adding materials — (a) green bubble on Jul 7 has no
  explanation, isn't clickable, text is clipped ("S. 2h"); (b) hovering any cell lifts it, implying
  clickability; (c) today is Jul 2 but the session sits on Jul 7 — unclear why, and "2h" vs the 1h 24m
  backlog is confusing; (d) arrived via "Resume setup" with no button back to `/roadmaps` (only browser back).
- **Affected UI:** `apps/app/src/onboarding/steps/Step3Preview.tsx` (mini-calendar, lines ~317–374,
  back button ~411–417) + shared `apps/app/src/roadmap/roadmap.css` hover rule (line ~1720).
- **Root causes (grounded):**
  - Bubble uses `roadmap-bubble roadmap-chip-done` (line ~351) — the **done/green** style — for a
    **future booked** session → wrong semantics (looks completed). Label "Session {mins}" clips to
    "S. 2h" in the narrow mini-cell. It's a `<div>` (non-interactive) but styled like the interactive
    roadmap bubbles.
  - "2h" = the day's **capacity** (`weekdayHours`/`weekendHours`×60), because `generateBookings` is
    book-to-exhaustion: each session = that day's full capacity, stop once material total (1h 24m) is
    covered. Bubble shows session length, not material minutes.
  - Jul 7 (not 2–6): bookings only land on **selected study days**; the 7th is the first study day
    on/after today. No copy explains this.
  - Hover-lift: onboarding cells reuse `.roadmap-day-in-month`; `roadmap.css:1720`
    (`@media (pointer:fine)`) lifts that class on hover — an affordance meant for the interactive
    roadmap page, inherited here (false affordance).
  - No exit: back button → `/onboarding/3` (materials); nothing routes to `/roadmaps` for re-entrant
    ("Resume setup") users.
- **Decisions so far (Rohit, 2026-07-02):**
  - Preview calendar is **read-only** (no interactivity mid-setup; editing lives on `/roadmap` post-commit).
  - **Tooltip** on the session cell/bubble (native `title` + `aria-label`), e.g.
    "Booked study session · 2h · Tue, Jul 7" — recovers the clipped label.
  - **Recolor** the bubble from `roadmap-chip-done` (green/done) to the **booked/outlined** style; green
    stays reserved for completed.
  - **Remove the hover-lift** (`.roadmap-day-in-month:hover`) for the onboarding mini-calendar (scope it
    to the interactive roadmap page only).
  - **Add a visual indicator for selected study days** on the calendar — mark every in-month cell whose
    weekday ∈ `state.selectedStudyDays` (and likely the weekday column headers), so the study-day pattern
    is visible even on unbooked days. This directly answers "why the 7th." Add a "study day" legend entry.
    → Supersedes the standalone "why the 7th" caption; keep only the short buffer note.
  - **Study-day indicator treatment = subtle moss tint** on in-month study-day cells
    (`color-mix(in srgb, var(--moss) 8%, var(--surface-card))`), new shared class `.roadmap-day-studyday`
    + study-day weekday-header emphasis + "Study day" legend entry. **Applies to ALL calendars**
    (roadmap + onboarding preview) via one shared class. today/deadline/current-week still win on overlap.
- **Mock built (visual contract):** `mocks/proposed/study-day-indicator.html`.
  - v1 used the stale **mock-CSS copies** + an invented layout → Rohit: "looks different from current
    pages, not interactive." Rebuilt v2 against the **REAL app CSS** (`mocks/real-css/` = verbatim copies
    of `packages/design-tokens/src/{tokens,global,components}.css` + `apps/app/src/roadmap/roadmap.css` +
    `apps/app/src/onboarding/onboarding.css`) and the **real component DOM** (RoadmapCalendar +
    Step3Preview), so it matches the running pages. (Real roadmap.css=1939 lines vs mock copy 1343 — the
    stale copies were the mismatch source.)
  - Interactive: a top toggle flips `body.studyday-on` to compare **baseline ↔ proposed**; the onboarding
    finish card expands/collapses the calendar; bubbles carry native tooltips.
  - Proposed layer (gated on the toggle): `.roadmap-day-studyday` moss tint on study-day cells + weekday
    header emphasis + "Study day" legend; onboarding session recolored done→booked; onboarding hover-lift
    removed (read-only). Real booked chip class is `roadmap-chip-booked` (not the mock's `chip-pending`).
  - Orphan `mocks/css/` (v1 copies) left in tree — sandbox `rm` blocked (Operation not permitted); harmless.
- **Locked fix set for the coding agent (4a/4b/4c):**
  1. Add shared `.roadmap-day-studyday` (moss 8% tint) + apply to every in-month cell whose weekday ∈
     `state.selectedStudyDays` (`RoadmapCalendar.tsx` cell build + `Step3Preview.tsx` mini-calendar);
     study-day weekday-header emphasis; add "Study day" legend entry to both legends. All calendars.
  2. `Step3Preview.tsx` session bubble: `roadmap-chip-done` → `roadmap-chip-booked`; add `title` +
     `aria-label` "Booked study session · {mins} · {EEE, MMM d}".
  3. Scope the `.roadmap-day-in-month:hover` lift (`roadmap.css:1720`) so it does NOT apply inside
     `.onboarding-mini-calendar` (read-only preview); default cursor there.
  4. Keep the buffer caption; the study-day tint replaces the "why the 7th" prose.
- **4d — back-to-`/roadmaps` exit from re-entrant onboarding: DEFERRED (Rohit "move on").** Not decided.
  Re-entrant users (via "Resume setup") have no exit to the dashboard except browser-back; Step3Preview
  back btn goes to `/onboarding/3`. Revisit when picking BUG-4 fixes up for implementation.

### BUG-5 — "Hours studied vs plan" burn-up chart is a mess
- **Status:** DECIDED — Option A (fix client-side visx chart), 2026-07-02 · NOT applied (hand to coding agent)
- **Decision (Rohit):** Option A — keep the chart client-side (@visx) and fix it; do **not** move rendering to
  Python. Scope includes the "planned" baseline rebuild **and** the visual fixes (defaulted in; the chart is
  misleading without the data fix — flag if Rohit wants visual-only).
- **Reported:** Rohit — burn-up chart on Week page looks broken (dup y-axis labels, repeated x-axis dates,
  blobby band, flat/low planned line); suggested using the Python service + python graphing libs.
- **Data pipeline (how it's built):**
  `Week.tsx` → `useProgressSnapshot()` → `computeProgress()` (`packages/progress/src/progress.ts`) →
  `ProgressSnapshot.burnUp: BurnUpData { planned, actual, gpCurve, today, deficit, dayNumber, totalDays }`.
  - `planned` = `buildPlannedCumulative(roadmap.slots)` (cumulative daily planned minutes).
  - `actual` = `buildActualCumulative(sessions)` (cumulative logged minutes).
  - `gpCurve` = `fitBurnUpGP(actualCumulative, startDate, deadline, today)` (GP mean/lower/upper, extrapolated).
  - Rendered client-side by `apps/app/src/components/BurnUpChart.tsx` using **@visx** (scaleTime/scaleLinear,
    AreaClosed, LinePath, AxisLeft/Bottom) inside a `ParentSize`.
- **Root causes (grounded):**
  1. **Decoupling-related "planned" regression.** `roadmap.slots` is retired; `findActiveRoadmap`/`toRoadmapInput`
     (`mapEvents.ts:98`) synthesize slots from bookings via `slotFromBooking` (`plannedMinutes = booking.estimatedDuration`).
     Book-to-exhaustion emits only a *few* bookings (enough to cover the backlog), so the "planned" cumulative
     is now sparse/low/flat — not the old prescriptive daily-to-deadline curve. "vs plan" now compares against a
     near-flat tiny baseline → distorted `deficit` and framing. **This is the tie to the material-session change.**
  2. **Y-axis label formatter too coarse.** `minutesToLabel(m)=Math.floor(m/60)+'h'` (BurnUpChart:34) drops minutes;
     on a small domain 5 ticks collapse to "0h,0h,0h,1h,1h" → the duplicated "1h/1h/0h/0h/0h" seen.
  3. **Degenerate x-domain on no/low data.** x-domain = min/max of planned+gp dates. Day 1 with nothing logged →
     `fitBurnUpGP` returns `[]` (actualPoints empty) and planned sparse → domain collapses to ~1 day →
     `format 'MMM dd'` repeats "Jun 27". No empty/degenerate guard, no empty state.
  4. **Curve overshoot + y-scale domination.** GP band/mean use `curveBasis` (doesn't pass through points, overshoots →
     blobby band); y-domain driven by `gp.upper*1.08` so actual/planned look flat and low.
- **Fix options:**
  - **A (recommended): fix the client-side visx chart.** (i) rebuild "planned" from capacity/bookings with a real
    daily-planned-to-deadline baseline (not just booked-session steps) so "vs plan" is meaningful again; (ii)
    `minutesToLabel` → h+m and dedupe ticks (or scale to hours); (iii) guard degenerate/empty domains (min 1-day →
    full startDate..deadline span; empty state "Log a session to see your burn-up"); (iv) swap `curveBasis`→
    `curveMonotoneX`/linear; base y-domain on data not inflated GP upper. Keeps interactivity, live theming
    (Marginalia tokens), responsiveness; no round-trip.
  - **B: Python-rendered graph (Rohit's idea).** Either (b1) `/v1/progress` returns a matplotlib PNG/SVG — static
    (loses hover/responsive), needs theming to match Marginalia, adds auth+latency+network dependence, couples a
    view concern to the service (currently unused by app; prod gated on OQ-02/OQ-03); or (b2) service returns
    Plotly JSON rendered by Plotly.js client-side (heavy dep, still client render). Note: matplotlib is already the
    right tool for the **dissertation/research figures** (`research/comparison`, `make figs`) and any PDF/report export.
  - **Assessment:** the mess is data + config bugs, not a limitation of the rendering library — so A fixes the actual
    problem with the least architectural cost; reserve Python plotting for research/report/server-side figures.
    If server-side parity is wanted later, mirror the *data shaping* in `/v1/progress` (OQ-01) but keep rendering client-side.

## Open
- Interaction note (Rohit): ask clarifying questions in chat only for now. Do not use the multiple-choice question tool.

## Blockers
— none

## Deferrals
- **BUG-4d** — back-to-`/roadmaps` exit for re-entrant onboarding. Deferred (Rohit "move on"); revisit at
  BUG-4 implementation. Trigger: picking up BUG-4 fixes / any re-entrant-onboarding work.
- Cleaner `.modal-overlay`/`.modal-card` consolidation deferred to a follow-up (BUG-1 alternative above).
- Full P5-port responsive-rule sweep (other dropped `@media(min-width:1024px)` rules from
  `roadmap.html`) — offered, not yet run.

## Checklist
- [x] Read `.work/README.md` and `.work/STATUS.md` to resolve active task layout.
- [x] Read existing `SCRATCHPAD.md`, `PLAN.md`, and `VERIFICATION.md`.
- [x] Read applicable local rules: Playwright config/lifecycle, form spacing, CSS workspace packages, React Router basename, roadmap engine, Dexie test setup, onboarding architecture.
- [x] Consult local memory for prior material-session plan-hardening expectations.
- [x] Verify exact current code for all plan-sensitive claims.
- [x] Produce amendment list with resolved findings and any true unresolved questions.
- [x] Apply approved amendments to `PLAN.md`.
- [x] Tighten `VERIFICATION.md` acceptance criteria to match amended plan.

## In-flight edits
- Updated this scratchpad for the plan-clarity review session.
- Edited `PLAN.md` and `VERIFICATION.md`.
- No app source or CSS fixes applied.

## Decisions in force
- Reviewer validates the plan before implementation. Do not implement the bug fixes in this session unless Rohit explicitly changes scope.
- Apply the prior workflow bar: hollow or ambiguous plan steps must be tightened into executable contracts before coding starts.
- `VERIFICATION.md` is the acceptance record; if it is stricter than `PLAN.md`, the plan should be amended to match it.

## Resolved (recent)
- Phase 1 source/test assumptions match current `Roadmaps.tsx` and `Roadmaps.test.tsx`.
- Phase 2 source assumptions match current `.bk-overlay`/`.bk-sheet`; plan now requires `.bk-grip { display: none; }`.
- Phase 3 source assumptions match current compact-day and DaySheet code; plan now makes the `useMatchMedia` test mock configurable.
- Phase 4 source assumptions match current preview/calendar code; plan now pins `isStudyDay` into `calendarModel.ts` with date-fns parsing and optional string-array input.
- Phase 5 is now implementation-ready: package progress uses live booking-capacity semantics, keeps the slot-grid helper only as fallback, and gives concrete chart helper/domain tests.
