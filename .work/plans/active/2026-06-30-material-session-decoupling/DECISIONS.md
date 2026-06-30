# Material ↔ Session decoupling — decisions scratchpad

> **Status:** active design discussion (grilling). Living document — **append every new
> decision here as we make it.** Not yet an implementation plan; this is the decision log
> the eventual `PLAN.md` will be built from.
> **Started:** 2026-06-30 · **Owner:** Rohit (design) + Cowork (planner)
> **Companion:** [`SessionDial.jsx`](./SessionDial.jsx) — the live dial prototype.

## Legend

`✅` locked (agreed) · `🟡` proposed / awaiting confirmation · `☐` open (not yet discussed/resolved) · `🛑` blocked

---

## 1. Why this work exists

- **Trigger:** the roadmap engine is buggy at `study/onboarding/3?new=1`. Root cause is the
  *prescriptive* packing: it force-fits each Material onto a specific calendar day as a
  `Slot`, and the boundary "tie" slots (`candidateMaterialIds = [...ids, '__rest__']`,
  `plannedMinutes = 0`) plus tie-resolution / `addMaterialToRoadmap` mishandle session-title
  counts and role inference.
- **Goal:** stop assigning materials to fixed days. Make **materials a browsable directory**;
  the user **picks a material at session start** and runs the existing timer. The engine no
  longer dictates a per-day grid — it **estimates completion time vs the deadline** from
  material lengths + planned capacity, and **recommends** (not dictates) session length.

## 2. Current-state facts (ground truth, verified in code)

These are what the redesign changes — recorded so the plan is grounded, not from memory.

- **Slot = a material pinned to a day.** `Slot { weekIndex, dayOfWeek, date, capacityMinutes,
  plannedMinutes, candidateMaterialIds, role, sessionTitle }` (`packages/roadmap-engine/src/roadmap-engine.ts`).
- **Start-session is pre-bound today.** `Home` reads the next `Slot`, builds `SessionSlotData`,
  hands it to `/session`. The user does not choose what to study.
- **`SessionLogged` payload** carries `materialId, slotDate, weekIndex, plannedMinutes,
  activeMinutes, duration, date, source, resolution` (`apps/app/src/session/types.ts`).
- **Attribution today** = `deriveSlotStatuses` (`packages/progress/src/deriveSlotStatuses.ts`):
  match a session to a slot by **exact `date` + `materialId ∈ candidateMaterialIds`**, FCFS;
  unmatched → "unplanned". Emits done / pending / skipped / unplanned.
- **Calibration reads `plannedMinutes` straight off the event** (`packages/progress/src/calibration.ts:57–100`),
  not from a slot. Pace ratio today = `activeMinutes / plannedMinutes`, filtered to
  `source==='active' && plannedMinutes>0 && activeMinutes>0`. **→ calibration is already
  decoupled from the dated grid.**
- **Pillar A as actually implemented** (the architecture diagram is STALE):
  - Pace Calibration — hierarchical **Bayesian** (`bayesian.ts`); research winner that overturned
    the null is **`enriched_shrink`** (log-linear + context features, `dual_prior`) in the Python
    `py-progress` tier; TS `bayesian.ts` is the shipped fallback.
  - Change Detection — **CUSUM** (`cusum.ts`); literature verdict was a **robust null** (nothing beat it).
  - **Kalman per-phase trend** (`kalman.ts` via `trend.ts`) — segments the pace series at CUSUM
    breakpoints; **this box is missing from the stale diagram.**
  - Progress Projection — **GP burn-up** (`gp.ts` / `progress.ts`); honest interval story is
    across-learner split-conformal in the research tier.
  - **Schedule Generator** = the roadmap-engine greedy interleaving packer — **the one box this
    redesign retires.**

---

## 3. Locked decisions ✅

### D1 — Decouple sessions from the dated slot grid; materials become a directory ✅
Drop the prescriptive day-by-day `Slot` assignment. Materials live in a browsable **directory**;
the user **picks a material at session start**, then sets a session length. The engine's job
shrinks to **capacity model + finish-date projection**, not per-day packing.
- **Scope = end-to-end:** onboarding (page 3), Home (start-session), Session, Roadmap. (Confirmed
  by Rohit's request to redesign all four pages.)
- **Why:** the bug, the rigid up-next, and the brittle calendar are all symptoms of slots being
  prescriptive.

### D2 — Two session inputs: planned length (dial) + actual length (timer) ✅
At start, after picking the material, the user sets a **planned length** on a dial (Input 1).
Then the **actual** timer runs and **can overrun** past planned until they close it (Input 2).
Both inputs feed the intelligence layer. *(See P1 — how `planned` relates to calibration is being
revised.)*

### D3 — Progress is material-based, with per-material completion captured ✅
The user is trying to finish **materials**, not log hours. Each material tracks `estimatedMinutes`
vs `loggedMinutes` + a completion signal. **Capture:** YouTube/playlist auto (video timer /
`videosCompleted`); articles & manual the user keys in. *(Being extended to partial position — see P1.)*

### D4 — Interrupted / partial sessions auto-log; material left open ✅
A partial session that's interrupted (incl. crossing midnight) **auto-logs its real
`activeMinutes`** with `resolution:'interrupted'` and leaves the **material open** to resume next
session. `End · complete` logs and marks the material **done**. The material (not the session) is
what "resumes" — a session stays bounded to one calendar day for clean per-day attribution.
- **Changes current behaviour:** today `stale_midnight` → `SessionAbandoned` (logs nothing). New
  behaviour logs the partial.

### D5 — Soft-cap dial driven by daily budget ✅
Soft cap = `hoursPerDay − minutesAlreadyLoggedToday`, applied on **any** day (planned or not — the
user may study any day). The dial defaults its **recommended** length within the cap; the user can
dial past it and the live timer can overrun it (visual indicator, choice stays theirs). A second
same-day session sees a reduced cap.

### D6 (Q3) — Recommendation is pace-first ✅
The recommended session length is **capped at a realistic ceiling = the user's stated remaining
daily budget (cap)**. Within that, it nudges from demonstrated pace toward the deadline-required
rate. When even the cap can't hit the deadline, the app **stops recommending an impossible number**
and surfaces the levers: **extend the deadline / drop or shorten materials / accept the later
finish**. The dial still lets the user voluntarily blow past the ceiling.
- `requiredDailyMinutes = (remaining material × throughputFactor) ÷ remaining days to deadline`,
  compared against `demonstratedDailyMinutes`.

### D7 — Dial UX (prototype direction) ✅
Real twist-to-set-timer model: **fixed 270° scale** anchored to the daily budget (printed minute
ticks, only rescales when hours/day changes). Four roles on four layers so none occludes another:
**planned** = draggable blue knob (rotate to set); **actual** = bold inner ring, colour-staged
teal (≤ plan) → amber (> plan) → red (> cap); **cap** = dashed bezel notch; **recommended** =
purple bezel triangle (flips to red "risk" flag under D6 infeasibility). Prototype: `SessionDial.jsx`.

---

### D8 — The intelligence layer calibrates THROUGHPUT (time ÷ material), not session-length adherence ✅
*Confirmed by reading the A-series synthetic generator (see verification below).*

Two signals, both using **time + material completion**:

1. **Throughput pace** = `actual minutes ÷ estimated material minutes consumed`, captured **per
   session including interrupted ones** (via **partial material position** — see below). → feeds
   **Pillar A** (Bayesian/CUSUM/Kalman, **math unchanged**) → drives the **finish-date / ETA** and
   the throughput factor in D6.
2. **Session-length adherence** = actual vs the dial's planned target. → a **lighter, separate
   signal** → drives the **recommended session length**. **Interrupted sessions are excluded here**
   (the cutoff was external, not a choice); complete-but-short sessions stay in.

- **Why this preserves Pillar A:** in the old slot model `planned` was the slot's *material chunk*
  (≈ estimated material time), so `active/planned` was *already* throughput. Feeding throughput
  keeps the **same validated signal**, just sourced from material position instead of a slot.
  Using the *dial value* as the calibration denominator (the earlier D2 reading) would have
  silently changed the signal to adherence and broken that — **this corrects D2.**
- **Requires:** completion capture (D3) extended from binary → **partial position**: free for
  video (timer position), a light "where'd you get to" for articles/manual, default-inferred from
  `logged ÷ estimated` if skipped.
- **Resolves concern #1** (interrupted 30 min is a real signal — it lives in throughput) and
  **concern #4** (throughput stays its own ratio; Pillar A machinery unchanged).

**Verification — A-series synthetic generator models a time-vs-material signal ✅**
(`research/comparison/src/research_comparison/generator/`)
- `generate.py` `PlannedSlot.planned_minutes = sample_chunk_minutes(material_type)` — `planned` is
  a **material chunk** (playlist 20–50, textbook 40–90, practice ~45, flashcards 10–20 min), not a
  time budget.
- `_event_for_slot` (gen.py:140–141): `plannedMinutes = planned_minutes`,
  `activeMinutes = planned_minutes * ratio` → `activeMinutes / plannedMinutes = ratio`.
- `ratio` ← `latent_base = m_global × role_rho × tau × weekend` (`pace.py`) — the ground-truth pace
  multiplier the calibration estimates.
- `_true_finish_date` (gen.py:110–116): `cumulative += planned_minutes * latent` until
  `sum(material.total_minutes)` — the finish date is *material consumed at pace*.
- **Conclusion:** the calibrated quantity is the multiplier on **material time** = throughput.
  Feeding the product calibration `actual ÷ estimated-material-consumed` is the **same signal shape
  → no re-validation needed.**

### D8a — Interrupted / partial-chunk throughput points ✅
*Confirmed: include them.* The generator only emits **full-chunk** sessions (no
partial-chunk events), so interrupted sessions' throughput points (`partial est ÷ actual`) use the
**same ratio definition** but weren't explicitly in the validation set.
- **Rec:** **include** them in calibration (real users get interrupted often; the ratio is in-family)
  + add a one-line external-validity note in the Pillar-A claims ledger + let Research Phase 5
  (N=1 real-data) sanity-check partial points.
- **Alternative:** complete-sessions-only in calibration (purest match to validation); interrupted
  sessions feed material progress + daily-minutes only.

### D9 — Roadmap = a session-booking model (resolves open #2's calendar fork) ✅
The roadmap keeps a **forward plan**, but as **blank session bookings**, not material-packed slots.
- **Engine = capacity layout only.** From `startDate, deadline, selectedStudyDays, weekday/weekendHours`
  it lays out **booked sessions** = `{ id, date, estimatedDuration, materialId?, status }` (dates +
  estimated durations). It does **NOT** pack materials — no `candidateMaterialIds`, no role-tie
  resolution, no `__rest__`. **This reduction is what kills the `/onboarding/3` bug.**
- **Advance booking:** on the Roadmap page the user clicks a future blank booking → attaches a
  material to it. Or leaves it blank and picks at start.
- **Non-planned days:** click an empty day cell → "no sessions planned — add one?" → same
  add-session UX → creates a booking on that day.
- **Study day (Home):** the day's booking shows with its material pre-loaded; the user confirms the
  planned length on the dial (defaults to `estimatedDuration`) + confirms the material → starts.
- **Calendar:** past = activity/done; future = bookings (with/without material). Status enum
  (done / booked / missed / unplanned) returns, keyed by **`bookingId`** (exact match, replacing the
  fuzzy date+materialId FCFS matching of `deriveSlotStatuses`).
- **Editable:** the Roadmap page allows add/move/remove bookings, change durations, attach/detach
  materials (replaces the old slot-coordinate `RoadmapEdited` events).
- **Week page target** = capacity (`hoursPerDay × study-days that week` / booked-session minutes),
  not summed slot-planned minutes.

## 4. Recently resolved (this session)

### D9a — booked-session shape & material relationship ✅
1. **Cardinality:** **one** material per booked session (matches the dial flow; a long material spans
   consecutive bookings).
2. **Soft-suggest, overridable:** the engine suggests a material per booking via spaced-practice ordering
   (foundation→anchor→practice, interleaving), **preferring a material that's already in-progress**
   (resume/continuity before opening new material). Non-binding — the user can swap or clear it.
3. **Attribution:** `SessionLogged` carries `bookingId` (exact match). A spontaneous Home start with no
   booking auto-creates a booking for today.
4. **Edit events:** booking-edit events replace slot-coordinate `RoadmapEdited`; exact shape deferred to
   the implementation plan.

### D10 — Material progress marking (extends D3) ✅
- **YouTube/playlist:** auto from the video timer / `videosCompleted`.
- **Non-YouTube (article/textbook/practice/manual):** the user marks progress as a **progress rate**
  (% / position). Available **(i)** within the session (at end; optionally adjustable during) **and**
  **(ii)** from the Roadmap material directory, any time.
- **Throughput rule:** only **session-bound** progress (paired with actual minutes) feeds the throughput
  calibration (D8). An **out-of-session** edit from the directory updates the material ledger and the
  ETA's "remaining," but does **not** produce a pace data point (no time component).

### D11 — Legacy roadmaps via read-time adapter; bookings are first-class events ✅
The app is **event-sourced** (append-only, synced to Supabase, replayed) — so **never rewrite history.**
- **Old slot-based roadmaps:** extend `mapEvents.ts` to **adapt on read** — capacity + materials come from
  the existing `RoadmapCreated` payload (`weekdayHours/weekendHours/selectedStudyDays`) + `MaterialAdded`;
  **future slots → derived bookings** (date + estimatedDuration + suggested material = `candidateMaterialIds[0]`);
  past `SessionLogged` already carry `materialId`/`date` → feed the material ledger directly.
- **New bookings = their own events:** `SessionBooked` / `BookingEdited` / `BookingCleared` (mutable —
  add/move/remove/attach/detach). `RoadmapCreated` for new roadmaps carries capacity + deadline + materials,
  **not** slots or bookings. **This also resolves D9a #4 (edit-event shape).**
- **Why:** event-sourcing-correct — no destructive migration to fight sync / risk cross-device divergence;
  one mapper, no second legacy UI. (Alternatives rejected: one-time event rewrite; legacy read-only calendar.)

---

## 5. Open questions ☐ (not yet resolved)

- ~~**#2 — Replacement for `deriveSlotStatuses`.**~~ **RESOLVED → D9** (session-booking model).
  Derivations become: per-material ledger + per-day activity + booking-status by `bookingId`.
  Sub-forks in D9a.
- **#3 — ETA / projection redefinition.** 🟡 **Proposed composite (pending R4 benchmark):** GP
  extrapolation of the material-done curve → finish-date + CI; **analytic** `remaining × tf ÷ rate` →
  the dial recommendation / required-rate; verdict = GP finish vs deadline; reference line = linear-to-
  deadline (vs capacity-shaped); cold-start → analytic fallback. Currency = **material** (D3). **Not
  locked — must be proven by R4** (see §5c). *Gates Home + Roadmap UI display.*
- **Lower-priority / plan-time:**
  - ~~Migration of existing slot-based `RoadmapCreated` events.~~ **RESOLVED → D11** (read-time adapter;
    bookings as first-class events).
  - Replan service contract (`/v1/roadmap/regenerate` currently returns slots) → becomes a
    re-projection / capacity-deadline adjust. *(Still open.)*
  - One-line note in the Pillar-A claims ledger that calibration's `planned` reference changed source.
  - Multi-roadmap lifecycle (active/queued/abandoned, date-window attribution) interaction with the
    material-set model.

---

## 5b. Deferred UI concerns (design later)

- **Material directory view on the Roadmap page** — let the user browse their materials + per-material
  progress from within the roadmap (not just attach-on-booking). UI concern, revisit during page design.
- **Progress-marking affordances** — the in-session and in-directory controls for D10 (how the
  % / position is captured per material type).

## 5c. Research / validation workstream (proof for the new design)

The refactor changes the **data-generating process** (session arrival + new event types), **not** the
**latent pace signal** (throughput; verified in D8). So validation splits three ways:
- **Transfers (re-confirm, don't redo):** calibration multiplier estimation
  (`enriched_shrink`/`dual_prior` vs baselines on `m_global`/context) — same signal, fed from material
  throughput.
- **Must re-run (cadence / new-event sensitive):** change-detection latency + false-alarm-rate, GP
  projection coverage, and the **new ETA composite** (never benchmarked).
- **Dropped:** the scheduling track (constrained packer retired; soft-suggest ordering is a lighter,
  separate KT concern).

Harness exists and is reusable (`research/comparison/`): 4 tracks, 200 seeds × 9 archetypes × 3 bands,
Holm + held-out, results stamped by `generator_version` / `params_version_hash`; adding a model = register
a candidate → auto-scored vs ground truth with paired-Holm vs incumbent. Projection candidates live in
`runners/projection.py:42-82`, scored by `metrics/projection.py` (coverage / MAE-days / sharpness vs
`GroundTruth.true_finish_date`).

- **R1 — Extend the generator** (keep the validated latent-pace core; add layers, each with ground truth):
  separate `plannedSessionMinutes` (dial choice) from the material chunk (adherence vs throughput); emit
  **interrupted / partial-chunk** sessions (D4/D8a); model **booking cadence + ad-hoc any-day** sessions.
  Bump `generator_version` (datasets coexist; nothing overwritten).
- **R2 — Calibration regression:** re-run; confirm the `enriched_shrink`/`dual_prior` win survives Holm +
  held-out with partial-chunk throughput points included. Down-weight partials if it degrades. *(Transfers
  only if reproduced.)*
- **R3 — Detection re-run:** re-score the 7 detectors under the new cadence; confirm the CUSUM robust-null
  holds when partials + irregular arrivals add noise.
- **R4 — ETA benchmark (headline new result):** register `analytic_required_rate` (B) and the
  `gp+analytic` composite (A+B) alongside `gp_ard/linear/conformal/kalman`; score vs `true_finish_date`,
  paired-Holm vs the GP incumbent. Also test cold-start fallback + linear-vs-capacity ideal line.
  **This is what proves the #3 design.**
- **R5 — Rigour parity** with the A-series (same seeds/archetypes/bands/Holm/held-out) → dissertation-grade,
  directly comparable.
- **R6 — Circularity guard (Research Phase 5, N=1 real data):** synthetic scoring is model-dependent and
  the new event types are where external validity is weakest — validate partial-chunk throughput + the ETA
  on real logged sessions before claiming.

**Consequence:** the **#3 ETA composite is a hypothesis (🟡), gated on R4** — design the UI to it, but the
dissertation only claims it once R4 (+R6) back it.

## 7. UI/UX & build-plan decisions (grill session 2 — 2026-06-30)

> Second grilling session, focused on the **UI/UX** of the four screens + how the work is
> packaged into a plan. Foundation (engine reduction, new events, mapEvents adapter, the three
> derivations) is planned **here too**, not elsewhere. Goal: one cohesive, concrete plan family
> incorporating UI + UX + logic. Append every decision below as `D12+`.

### D12 — Planning scope & packaging ✅
The whole decoupling (foundation + UI + UX + logic) is planned in **this folder**. We will
clarify the UI/UX design through grilling first, then produce a concrete `PLAN.md` (+ companion
`VERIFICATION.md`) that incorporates UI, UX, and logic together. Open sub-question (revisit after
UI/UX is clear): whether to ship as one phased `PLAN.md` with a **Phase 0 foundation** slice + per-page
slices, or split into a prerequisite foundation plan + four page plans. Leaning: one phased PLAN.md,
Phase 0 = foundation (engine reduction + new events + mapEvents adapter + three derivations), then a
vertical slice per page. *(Confirmed by Rohit: "we will plan it here… UI, UX and logic all incorporated.")*

### D13 — Onboarding page-3 preview: summary + expandable calendar ✅
The day-by-day packing preview (`Step3Preview` + `SchedulePreview`, tie-resolution, swap-FAB) is
**retired**. Replacement = **Option A (capacity summary) with an embedded, expandable calendar**
(Option C's grid), chosen by Rohit from three mocked options (A summary / B booking-list / C calendar;
the losing two kept under `mocks/proposed/onboarding-3-option{A,B,C}-*.html` for the record).
Locked mock: `mocks/proposed/onboarding-3.html`. Shape:
- **Default view = summary:** a **Projected finish** verdict card, a backlog-fits-capacity bar, a
  sessions/total/buffer stat row, and an **unordered material directory** ("what you'll study"). No
  day-by-day grid by default.
- **Projected-finish card is a toggle:** clicking it **slides a calendar panel down** (pushing the
  cards below it down) showing booked study-days + finish + deadline; clicking again collapses it.
  Closed by default.
- **Discoverability (required by Rohit):** the card carries a **persistent "Calendar ⌄" pill** + a
  chevron that rotates on open, **hover elevation** (`--shadow-md` + border darken + 1px lift), a
  hover-revealed hint line, `cursor:pointer`, and keyboard support (`role=button`, `tabindex=0`,
  Enter/Space, `aria-expanded`/`aria-controls`).
- **Calendar is multi-month with ‹ › arrows** (Rohit: must page across months); arrows disable at the
  plan's month bounds. Reuses the real `roadmap-calendar-shell` grid classes.
- Finish-date / "estimate" labels flagged **provisional pending research R4** (#3) — shown with a
  `provisional` eyebrow.

### D13a — Booking generation rule ✅
**Book-to-exhaustion + buffer:** engine books one session per selected study-day (Mon/Wed/Fri in the
mock), each sized to that day's capacity, **stopping once cumulative booked minutes ≥ total material
minutes**; remaining days to the deadline render as **buffer**. (Chosen with D13; rejects "book every
study-day to the deadline" from option B.) Generation is pure counting — `ceil(totalMaterialMin ÷
per-day capacity)` study-days laid onto the soonest study-days — **no material-to-day assignment**, so
the `/onboarding/3` packing bug cannot recur.

### D14 — Onboarding page-3 LEFT panel: organising many materials (🟡 choosing via mocks)
Problem: the current flat vertical stack of full edit-cards (`MaterialRow`) grows unbounded — many
materials = endless ugly scroll. Two mocked options (`mocks/proposed/onboarding-3-left-options.html`),
both built on a shared **compact, expand-on-edit row** (icon · title · length · role tag; click to
reveal fields; drag-grip to reorder; incomplete rows auto-open):
- **Option 1 — flat compact accordion list:** all materials in one slim scroll-capped list. Simplest;
  least chrome.
- **Option 2 — grouped by type:** collapsible sections **Videos / Playlists / Links & articles /
  Manual**, each with a count + total; same compact rows inside. Scales best for large libraries.
- **Material types to support (Rohit):** YouTube **video**, YouTube **playlist** (nested,
  selectable videos — new `pl` purple icon), **external URL/article**, **manual/book**. Playlist row
  expands to its video checklist.
- Open sub-points: reorder/drag persistence; whether grouping auto-engages only past N items (hybrid).

<!-- append D15+ here as the grill resolves them -->

## 6. Change log

- **2026-06-30** — Document created. Captured D1–D7 + Q3 (D6) as locked; P1 (throughput
  realignment) as proposed/pending; concerns #2, #3 and lower-priority items as open.
- **2026-06-30** — Verified the A-series synthetic generator models a time-vs-material signal
  (`planned_minutes` = material chunk; `active = planned × pace`). **P1 confirmed → locked as D8**
  (calibrate throughput; no re-validation needed). New sub-decision **D8a** opened (include
  interrupted/partial-chunk throughput points vs complete-only; rec = include + ledger note).
- **2026-06-30** — D8a confirmed: **include** interrupted/partial-chunk throughput points (+ claims-
  ledger note + Phase-5 check). Moved to discussing open question #2 (replace `deriveSlotStatuses`).
- **2026-06-30** — #2 resolved → **D9 (session-booking model):** engine lays out blank bookings
  (date + estimated duration, capacity-only, no material packing); user attaches material in advance or
  at start; non-planned days bookable; Home loads the day's booking → confirm dial + material → start;
  attribution by `bookingId`. Sub-forks **D9a** opened (cardinality, blank-vs-suggested, attribution,
  edit events).
- **2026-06-30** — **D9a resolved** (one material/booking; soft-suggest preferring in-progress material;
  bookingId attribution; edit-event shape deferred). **D10 added** (non-YouTube progress marking in-session
  + in-directory; out-of-session edits don't feed throughput). Deferred UI: material directory view on the
  Roadmap page. Remaining open: **#3 (ETA/projection)**.
- **2026-06-30** — #3 design drafted as a **proposed composite** (GP finish-date + analytic recommendation)
  but **not locked**: Rohit flagged it needs empirical proof. Added **§5c research workstream R1–R6** —
  extend the generator, regression-test calibration/detection, **benchmark the ETA composite (R4)** on the
  existing `research/comparison/` harness with A-series rigour, guard circularity via Phase-5 real data.
  #3 composite is now 🟡 gated on R4.
- **2026-06-30 (grill session 2)** — Mock-driven workflow set up under `mocks/` (verbatim design-system
  CSS in `mocks/css/`; frozen `baseline/`, evolving `proposed/`). Onboarding-3 baseline mocked + fidelity
  confirmed by Rohit. Three preview options rendered (A summary / B booking-list / C calendar). **D13 +
  D13a locked:** chose **Option A summary + expandable multi-month calendar** (Projected-finish card
  toggles a slide-down calendar; persistent "Calendar ⌄" pill + hover affordance + keyboard a11y;
  ‹ › month arrows) and **book-to-exhaustion + buffer** generation. Chosen mock:
  `mocks/proposed/onboarding-3.html`.
- **2026-06-30 (grill session 2)** — UI/UX grilling started. **D12** logged: plan the whole
  decoupling (foundation + UI + UX + logic) in this folder as one cohesive plan; clarify UI/UX
  first. Grounded in real components: `Step3Materials.tsx` / `Step3Preview.tsx` (the day-by-day
  packing UI to retire), `Home.tsx` (`getUpNextSlot` pre-bound start). Appending D13+ as resolved.
- **2026-06-30** — Research workstream handed off to a separate Opus session
  (`.work/handovers/2026-06-30-research-eta-model-selection.md`). Lower-priority **legacy-data** item
  resolved → **D11** (read-time adapter; new bookings as first-class `SessionBooked`/`BookingEdited`/
  `BookingCleared` events — also closes D9a #4). UI planning handed off
  (`.work/handovers/2026-06-30-ui-planning-handoff.md`). Remaining open: replan contract; claims-ledger
  note; multi-roadmap lifecycle interaction; **#3 gated on R4**.
