# VERIFICATION — material ↔ session decoupling

Round-trip review log for [`PLAN.md`](./PLAN.md). **Planner pre-fills acceptance criteria** (below).
**Implementer (Codex/Sonnet)** fills the *Implementer report* per phase (files, commit SHA, deviations,
self-check). **Reviewer (Cowork)** fills *Reviewer findings* (per-criterion verdict, status
`✅ Verified` / `🔁 Changes requested`) by reading the actual diff (`git show <sha>`), not the report alone.
A phase is **not done** until it's `✅ Verified`.

Legend: `[ ]` unmet · `[x]` met · `[~]` partial. Status: ☐ Not started · 🟡 In progress · ✅ Verified · 🔁 Changes requested.

Cross-cutting invariants (must hold at every phase):
- Zero destructive event migration; legacy `RoadmapCreated.slots` still readable (D-02/D11).
- Calibration feed intact — `interrupted`/partial `SessionLogged` still satisfy `source:'active' && activeMinutes>0` with denominator `materialConsumedMinutes ?? plannedMinutes`; research G1 "INCLUDE partials".
- No detector/calibrator model change (research G1/G2).
- Finish-date labels shown **provisional**; ETA is a cold-start fallback layered on GP, never a GP replacement (research G3 / D-07).
- Per-user Dexie isolation preserved; new event kinds need no schema version bump (events table is generic) — but any `activeSession` field additions must not break existing records.
- New roadmaps can omit `slots`; app read paths must use `materialIds` + booking events and only synthesize legacy slots for compatibility.

---

## Plan review log

- **2026-07-01** Senior ML/UI review hardened `PLAN.md` against the current code and supporting docs. Resolved hollow steps around deterministic booking IDs, no-slot roadmap reads, material-consumed calibration denominators, out-of-session material progress, direct `/session` starts, client-side ETA wiring, and replan shorten/drop payloads. No app implementation code changed in this review.

---

## Phase 1 — engine bookings + event shapes · Status: ✅ Verified

**Acceptance criteria**
- [x] `Booking { id, date, estimatedDuration, materialId?, status }` + `BookingStatus` exported from `packages/roadmap-engine/src/index.ts`.
- [x] `generateBookings(BookingLayoutInput)` returns bookings by **book-to-exhaustion + buffer**: count = `ceil(totalMaterialMinutes / per-day capacity)` laid on selected study-days from `startDate`; bookings are **blank** (`materialId` undefined); weekend/weekday capacity honored; days past exhaustion unbooked; generated IDs are deterministic (`planned:<ordinal>:<date>` or equivalent), not `uuid()` (D-01).
- [x] `suggestMaterialForBooking` prefers a started-but-not-done material, else foundation→anchor→practice interleave; skips done (D9a #2).
- [x] Packer removed from the new live booking path: no `candidateMaterialIds`/`__rest__`/tie-resolution/`tagRoleCandidates`/`assignMaterialsToSlots` in `generateBookings`; these remain only in deprecated legacy slot APIs. `inferRole`/`ROLE_TO_LABEL`/`LABEL_TO_ROLE` retained.
- [x] `sync/types.ts`: `SessionBookedPayload`, `BookingEditedPayload` (with `materialId?: string|null` detach), `BookingClearedPayload`, and `MaterialProgressMarkedPayload` added; `RoadmapCreatedPayload.materialIds?` and `materialDurationOverrides?` added; `RoadmapCreatedPayload.slots` made optional/legacy-only (not deleted).
- [x] `SessionLoggedPayload`: `bookingId?`, `resolution?: 'completed'|'trimmed'|'interrupted'`, `materialPosition?`, `plannedSessionMinutes?`, and `materialConsumedMinutes?` added. `ActiveSessionRecord`/`SessionSlotData` carry `bookingId`, `materialEstimatedMinutes`, and `materialStartPosition` without breaking older records.
- [x] `pnpm --filter @study-tracker/roadmap-engine test` green; `pnpm --filter app typecheck` green (deprecated `generateRoadmap` kept while current callers migrate in later phases).
- [~] Booking-layout tests added. Legacy slot/packing tests were retained as deprecated API regression coverage because old callers still compile against that path until Phases 3/5/7.

**Implementer report (2026-07-01):**
- Files changed: `packages/roadmap-engine/src/roadmap-engine.ts`, `packages/roadmap-engine/src/index.ts`, `packages/roadmap-engine/src/roadmap-engine.test.ts`, `apps/app/src/sync/types.ts`, `apps/app/src/session/types.ts`, plus minimal optional-slot guards in app callers required for typecheck.
- Commit SHA: `327ca45` (`feat(planner): add booking foundations`). Planning baseline was already committed as `8c65b07`.
- What changed: added deterministic `Booking`/`BookingLayoutInput`/`generateBookings`, `suggestMaterialForBooking`, deprecated legacy slot APIs, booking/session/material-progress event payload types, optional `materialIds`/`materialDurationOverrides`, optional legacy `slots`, and session booking/material-position fields.
- Deviations: retained legacy slot packer tests instead of deleting them because current app callers still import deprecated slot APIs. No new booking path depends on the packer.
- Self-check: `pnpm --filter @study-tracker/roadmap-engine test` passed (`36` tests); `pnpm --filter app typecheck` passed; `git diff --check` passed.

**Reviewer findings (2026-07-01, Cowork senior review — read against `git show 327ca45`):** **Status: ✅ Verified**
- [x] `Booking`/`BookingStatus`/`BookingLayoutInput` + `generateBookings` + `suggestMaterialForBooking` exported from `index.ts` (verified in diff).
- [x] `generateBookings` is book-to-exhaustion + buffer, blank bookings, deterministic `planned:<ordinal>:<date>` IDs, weekday/weekend capacity honored, no RNG. Tests assert count (`ceil` = 3 for 180min@60), buffer day unbooked, ID stability across repeated calls, mixed weekend capacity. ✅
- [x] Packer quarantined: `generateBookings` contains no `candidateMaterialIds`/`__rest__`/`tagRoleCandidates`/`assignMaterialsToSlots`; `generateRoadmap` + slot mutators kept and tagged `@deprecated`; `inferRole`/`ROLE_TO_LABEL`/`LABEL_TO_ROLE` retained. ✅
- [x] `sync/types.ts`: `SessionBookedPayload`, `BookingEditedPayload` (`materialId?: string|null` detach), `BookingClearedPayload`, `MaterialProgressMarkedPayload`; `RoadmapCreatedPayload.materialIds?`/`materialDurationOverrides?` added; `slots?` made optional (not deleted). ✅
- [x] Session payload/record fields added (`bookingId`, `resolution:'…|interrupted'`, `materialPosition`, `plannedSessionMinutes`, `materialConsumedMinutes`, `materialEstimatedMinutes`, `materialStartPosition`) — all optional, back-compat preserved. ✅
- [x] `pnpm --filter @study-tracker/roadmap-engine test` = 36 green (re-run by reviewer); `pnpm --filter app typecheck` green (re-run). Optional-slot guards in `Step4Confirm`/`RoadmapCalendar`/`mapToRegenerateRequest` are non-behavioral (`payload.slots ?? []`). ✅
- Non-blocking nits (do not gate Phase 1): (1) `suggestMaterialForBooking` applies role order **sequentially** (all foundation, then anchor, then practice) rather than a true interleave, and drops the `usedMaterialIds` guard in the second (fallback) role loop — acceptable under the plan's wording, revisit if the suggestion UX in P3/P4 needs interleave. (2) `roadmapIdentity` is now duplicated across `mapEvents.ts`, `roadmapLifecycle.ts`, `mapToRegenerateRequest.ts` — consider hoisting to one shared util in a later phase.

**Resolution (on redo):** _n/a — verified as-is._

---

## Phase 2 — derivations + read-time adapter · Status: ✅ Verified

**Acceptance criteria**
- [x] `deriveBookingStatuses(bookings, sessions, today)` → per-booking `done|booked|missed|unplanned` by **exact `bookingId`**; interrupted session does **not** mark `done`; unplanned = logged w/o matching bookingId grouped by date (D-03).
- [x] `buildMaterialLedger` returns per-material `{estimatedMinutes, activeMinutesLogged, estimatedConsumedMinutes, remainingEstimatedMinutes, done, started, lastPosition}` and folds both `SessionLogged` partials and `MaterialProgressMarked`; `buildDailyActivity` returns per-day minutes. Both exported from `packages/progress/src/index.ts`.
- [x] Shared calibration denominator helper uses `materialConsumedMinutes ?? plannedMinutes`; calibration test covers a partial session where `activeMinutes/plannedMinutes` would be wrong, and Bayesian/CUSUM/trend/calibration code paths use the helper.
- [x] `SessionEvent` gains `bookingId`/`materialPosition`/`materialConsumedMinutes`; `mapSessions` maps them.
- [x] `mapBookings` folds `SessionBooked`/`BookingEdited`/`BookingCleared` by `bookingId` in event order (detach via `materialId:null`); scoped to active roadmap.
- [x] **Legacy adapter** `deriveBookingsForRoadmap`: legacy `RoadmapCreated.slots` (future) → bookings (`date + plannedMinutes||capacity + candidateMaterialIds[0]`), then booking events applied on top; new roadmaps derive purely from booking events (D-02/D11).
- [x] `mapEvents.findActiveRoadmap`, `roadmapLifecycle.ts`, and `roadmapProgress.ts` tolerate `RoadmapCreated.slots === undefined`; new material sets come from `materialIds`, legacy material sets from slots.
- [x] `deriveSlotStatuses` marked `@deprecated` but still present (call sites migrate in Phase 5).
- [x] Capacity weekly-target helper available for Week (D-08).
- [x] `pnpm --filter @study-tracker/progress test` + `pnpm --filter app test -- mapEvents` green; new tests cover legacy-adapter + booking-fold + status derivation.

**Implementer report (2026-07-01):**
- Files changed: `packages/progress/src/{deriveBookingStatuses,materialLedger,dailyActivity,calibrationDenominator,types,index,deriveSlotStatuses,bayesian,calibration,cusum,trend}.ts`, matching progress tests, `apps/app/src/progress/mapEvents.ts`, `apps/app/src/progress/mapEvents.test.ts`, `apps/app/src/roadmap/{roadmapLifecycle,roadmapProgress}.ts`, plus minimal legacy optional-slot guards/tests in `RoadmapCalendar`, `Step4Confirm`, and `mapToRegenerateRequest`.
- Commit SHA: `327ca45` (`feat(planner): add booking foundations`).
- What changed: added booking status derivation, material ledger, daily activity, calibration denominator helper, new SessionEvent fields, booking event folding, legacy-slot-to-booking adapter, material scoping by `materialIds`, no-slot active-roadmap bridge, no-slot lifecycle/progress summaries, and capacity weekly-target helper.
- Deviations: `deriveBookingStatuses` uses a local structural `BookingLike` instead of importing `@study-tracker/roadmap-engine` because `@study-tracker/progress` does not declare that package as a dependency and app typecheck caught the boundary. This preserves structural compatibility without adding a package dependency.
- Self-check: `pnpm --filter @study-tracker/progress test` passed (`90` tests); `pnpm --filter app test -- mapEvents` passed (`52` app test files / `472` tests under the filter run); `pnpm --filter app typecheck` passed; `git diff --check` passed.
**Reviewer findings (2026-07-01, Cowork senior review — read against `git show 327ca45`):** **Status: 🔁 Changes requested**

Logic is correct and complete; the block is a **missing-test** gap that the plan explicitly requires.

- [x] `deriveBookingStatuses` — exact-`bookingId` match; interrupted session does **not** mark done (test asserts `missed`); future/past unmatched → `booked`/`missed`; unplanned grouped by date. Verified + well-tested. ✅
- [x] `buildMaterialLedger` — `estimatedConsumedMinutes = max(Σ materialConsumedMinutes, latest-position-converted)`; folds in-session + out-of-session marks; `done`/`started`/`lastPosition`/`remaining` correct. `buildDailyActivity` per-day. Both exported + tested. ✅
- [x] **Calibration denominator** helper `materialConsumedMinutes ?? plannedMinutes` wired into **all four** modules (`bayesian`, `cusum`, `trend`, `calibration`) via `isCalibrationSession`/`calibrationDenominator`; test proves a partial session yields ratio `30/20` (multiplier > 1), not `30/60`. Legacy events fall back to `plannedMinutes` → back-compat intact (G1/D8). ✅
- [x] `SessionEvent` gains `bookingId`/`materialPosition`/`materialConsumedMinutes`/`plannedSessionMinutes`/`resolution`; `mapSessions` maps them. ✅
- [x] `mapBookings` folds `SessionBooked`/`BookingEdited`/`BookingCleared` by `bookingId` in event order, scoped to roadmap; detach via `materialId:null` tested; `BookingCleared` order tested. ✅
- [x] Legacy adapter `deriveBookingsForRoadmap` maps future legacy slots → bookings then applies booking events on top; `mapMaterialsForRoadmap` scopes by `materialIds` (falls back to slot candidates for legacy) — tested (`mat-2` only, not all `MaterialAdded`). ✅
- [x] `findActiveRoadmap`/`findRoadmap`/`roadmapLifecycle.ts`/`roadmapProgress.ts` tolerate `slots === undefined`; `roadmapIdentity` correctly reroutes `RoadmapReplanned` booking scope to the original `roadmapCreatedAt`. ✅ (compiles + typecheck green)
- [x] `deriveSlotStatuses` tagged `@deprecated`, still present. `capacityWeeklyTarget` (D-08) present + exported. ✅
- [~] **`pnpm --filter @study-tracker/progress test` (90) + `mapEvents` (472) green — BUT one plan test requirement is unmet.** The Phase-2 "Tests" block requires: *"`roadmapLifecycle.test.ts` + `roadmapProgress.test.ts`: no-slots roadmap does not crash and computes active dashboard progress from bookings/sessions."*
  - `roadmapLifecycle.test.ts` received **only** mechanical `base.slots![0]` non-null fixups — **no** new test exercising the new no-slots path (`bookingIdsForRoadmap` / `completedBookingCount`).
  - **`roadmapProgress.test.ts` does not exist.** The ~90-line no-slots branch of `summarizeRoadmapProgress` (`bookingsForEntry`, `materialLedgerForEntry`, completed-booking counting, ledger-vs-booking `totalPlanned`/`toGo`) is the **largest new logic block in Phase 2 and has zero coverage.** VERIFICATION checks the "tolerate `slots===undefined`" criterion `[x]`, but that tolerance is untested for the progress summary.

**Required changes to reach ✅ Verified (Phase 2):**
1. Add `apps/app/src/roadmap/roadmapProgress.test.ts`: a no-slots `RoadmapLifecycleEntry` (payload with `materialIds`, no `slots`) + `MaterialAdded` + `SessionBooked` + `SessionLogged` (one completed, one `interrupted`) → assert `summarizeRoadmapProgress` returns correct `completedSlots`/`totalSlots`/`loggedMinutes`/`toGoMinutes`/`percentComplete`, that an `interrupted` session does **not** count as completed, and that ledger-based `totalPlanned`/`toGo` are used when `materialIds` resolve.
2. Add a no-slots case to `roadmapLifecycle.test.ts` proving `deriveRoadmapLifecycle` computes `totalSlots`/`completedSlots`/`percentComplete` from booking events (via `bookingIdsForRoadmap`/`completedBookingCount`) and does not crash when `payload.slots === undefined`.
3. Re-run `pnpm --filter @study-tracker/progress test && pnpm --filter app test -- roadmapProgress roadmapLifecycle` and update the implementer report.

No correctness defects found in the code itself — `sessionsCount === completedSlots` matches the legacy branch's own semantics, so no behavioral drift for existing consumers.

**Resolution (redo 2026-07-01):**
- Analysis: the Phase 2 logic was correct, but my first self-check over-weighted green package/mapEvents tests and missed the plan's app-level test line for `roadmapLifecycle.test.ts` + `roadmapProgress.test.ts`. That left the no-slots dashboard progress branch unguarded despite being production logic.
- Added `apps/app/src/roadmap/roadmapProgress.test.ts`: no-slots `RoadmapLifecycleEntry` with `materialIds`, `MaterialAdded`, `SessionBooked`, and `SessionLogged` events; asserts `completedSlots=1`, `totalSlots=2`, `loggedMinutes=70`, `totalPlannedMinutes=180`, `toGoMinutes=60`, and `percentComplete=50`; interrupted booked session is logged but does not count complete; material-ledger totals win over booking-duration fallback.
- Added a no-slots case to `apps/app/src/roadmap/roadmapLifecycle.test.ts`: proves `deriveRoadmapLifecycle` handles `payload.slots === undefined`, counts active booking events after `BookingCleared`, ignores interrupted sessions for completion, and returns `totalSlots=2`, `completedSlots=1`, `percentComplete=50`.
- Verification: `pnpm --filter @study-tracker/progress test` passed (`90` tests); `pnpm --filter app test -- roadmapProgress roadmapLifecycle` passed (`53` files / `474` tests under the filter run); `pnpm --filter app typecheck` passed; `git diff --check` passed.
- Status: redo implemented locally; awaiting Cowork reviewer re-check. Not self-marking Phase 2 verified.

**Reviewer re-check (2026-07-01, Cowork — read both new test files + re-ran suites):** **Status: ✅ Verified**
- [x] `apps/app/src/roadmap/roadmapProgress.test.ts` added and meaningful: no-slots entry (`materialIds:['mat-1','mat-2']`, no `slots`) + `MaterialAdded`(100/80) + 2×`SessionBooked` + `SessionLogged`(completed) + `SessionLogged`(interrupted). Asserts the exact expected summary object — `completedSlots=1` (interrupted excluded), `totalSlots=2`, `loggedMinutes=70`, ledger-driven `totalPlannedMinutes=180`/`toGoMinutes=60`, `percentComplete=50`. Exercises `bookingsForEntry` + `materialLedgerForEntry` + completed-booking counting. ✅
- [x] `roadmapLifecycle.test.ts` no-slots case added: proves `payload.slots === undefined` tolerated, `bookingIdsForRoadmap` honors a `BookingCleared` (booked 3, cleared 1 → `totalSlots=2`), interrupted session excluded from `completedBookingCount` (`completedSlots=1`, `percentComplete=50`). Goes beyond the minimum ask. ✅
- [x] Reviewer re-ran `pnpm --filter app test -- roadmapProgress roadmapLifecycle` → **53 files / 474 tests green**; `pnpm --filter app typecheck` clean. The `[~]` test-coverage criterion is now `[x]`.
- No correctness defects. **Phase 2 closed.** Both foundation phases (1 & 2) are ✅ Verified — proceed to Phase 3 (onboarding p3).

---

## Phase 3 — Onboarding page 3 · Status: 🟡 Implemented; awaiting reviewer

**Acceptance criteria** (visual contract `mocks/proposed/onboarding-3.html`)
- [x] `SchedulePreview`, `SwapFab`, tie-resolution, `previewEdits`, `generateRoadmap` slot path removed from `Step3Preview.tsx`.
- [x] Preview = capacity **summary** (projected-finish verdict w/ **provisional** eyebrow, backlog-fits-capacity bar, sessions/total/buffer stats, material directory) + **expandable multi-month calendar** (toggle on the finish card; `‹ ›` month arrows; booked study-days marked) — matches the mock (D13/D13a).
- [~] `Step3Materials.tsx` materials **grouped by type** (Videos/Playlists/Links/Manual, collapsible, count+total) with compact expand-on-edit rows (D14). Implemented grouped compact sections and expandable rows; group headers themselves are not collapsible.
- [x] Playlist row opens the **existing `PlaylistPickerPopup`** modal — not an inline checklist (D14a).
- [x] `handleCommit` emits events in order: `MaterialAdded` per material → `RoadmapCreated` with capacity+deadline+`materialIds` and **no `slots`** → `SessionBooked` per generated deterministic booking → `OnboardingCompleted`.
- [x] **`/study/onboarding/3?new=1` renders without the packer bug** (no tie warnings, no crash).
- [x] `pnpm --filter app typecheck` + `pnpm --filter app test -- onboarding` green; Playwright authored (not run).

**Implementer report (2026-07-01):**
- Files changed: `apps/app/src/onboarding/steps/Step3Preview.tsx`, `Step3Materials.tsx`, onboarding tests, `apps/app/src/onboarding/onboarding.css`, plus sync/EventStore created-at plumbing so no-slot `RoadmapCreated` and generated `SessionBooked` events share the intended roadmap identity.
- Commit SHA: uncommitted local implementation in this working tree.
- What changed: replaced the slot packer preview with a booking summary, capacity bar, stats, material directory chips, and expandable calendar; grouped material rows by type; reused `PlaylistPickerPopup`; changed commit to emit `RoadmapCreated{materialIds}` with no `slots` followed by deterministic `SessionBooked` events.
- Deviations: group headers are not collapsible; rows expand for edit/attention states. Visual behavior is aligned with the mock intent but not a pixel-identical port.
- Self-check: `pnpm --filter app typecheck` passed; `pnpm --filter app test -- onboarding` passed (`55` files / `476` tests under the filter run after Phase 4 additions); `grep -n "SchedulePreview\|SwapFab" apps/app/src/onboarding/steps/Step3Preview.tsx` returned no matches; `git diff --check` passed. Authored Playwright coverage in `e2e/material-session-decoupling.spec.ts` includes `/study/onboarding/3?new=1` summary/no-tie assertions and was discovery-checked with `pnpm exec playwright test --config e2e/playwright.config.ts e2e/material-session-decoupling.spec.ts --list` (not executed).
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Phase 4 — Session flow (Home → pre-session → running end-sheet) · Status: 🟡 Implemented; awaiting reviewer

**Acceptance criteria** (contracts `home.html`, `session-presession.html`, `session-running.html`)
- [x] Home booking card reads "Study session · ~Nmin" + **"Suggested material: <title>"**; Start passes `SessionSlotData{bookingId, materialId, plannedMinutes, …}` to `/session` (D15). Continue card preserved.
- [x] `Session.tsx` renders **`PreSessionSetup`** when `idle && no active record` instead of auto-starting; direct `/session` without location state derives today's booking or enters ad-hoc mode; running layout renders directly when a record exists (Continue bypasses setup — D-06).
- [~] `PreSessionSetup` matches V1 mock: suggested material as title + `material-strip` + "Change" (picker), **`SessionDial`** for planned length (cap-aware, pace-first recommended), "Start" → `lc.start({…, materialId, plannedMinutes, bookingId})`. Dial **not** on the running screen (D-05). Implemented a Marginalia-skinned circular readout plus range control; cap/recommendation is based on the booking target, not full hours-per-day minus done-today math.
- [x] `PreSessionSetup` ad-hoc start emits `SessionBooked` first, then starts with that `bookingId`.
- [x] `SessionLifecycle.interrupt(materialPosition?)` emits `SessionLogged{resolution:'interrupted', bookingId, materialPosition, plannedSessionMinutes, materialConsumedMinutes}`, material left open; `end()` (complete) carries `bookingId` plus complete-position denominator. `stale_midnight` now auto-interrupts (logs partial) instead of `SessionAbandoned` (D-04).
- [~] `EndSessionSheet`: single primary **End session** opens it; position capture (presets + % slider; YouTube auto); complete-vs-keep-open smart default from position; Pause·come-back-later stays ghost (D-04/D18). Running numeric timer/frame unchanged (D-05). Implemented presets/slider/smart default; YouTube-specific auto-position is not implemented yet.
- [x] Calibration feed intact — an interrupted active session still flows into `calibration.ts` filter (G1 partials INCLUDED).
- [x] `pnpm --filter app typecheck` + `pnpm --filter app test -- session` green; Playwright authored (not run).

**Implementer report (2026-07-01):**
- Files changed: `apps/app/src/pages/Home.tsx`, `Session.tsx`, `apps/app/src/session/{sessionPlanning,PreSessionSetup,SessionLifecycle,types}.ts(x)`, `apps/app/src/session/components/{EndSessionSheet,index}.ts(x)`, `apps/app/src/session/session.css`, related tests, and `e2e/material-session-decoupling.spec.ts`.
- Commit SHA: uncommitted local implementation in this working tree.
- What changed: Home now derives today's booking/material suggestion from booking events + material ledger; `/session` now renders setup instead of auto-starting when idle, derives direct-route suggestions, preserves active-record Continue bypass, logs ad-hoc `SessionBooked` before start, carries booking/material metadata into the active record, opens an end sheet for complete/interrupted logging, emits `materialPosition`/`materialConsumedMinutes`, and auto-interrupts stale-midnight sessions.
- Deviations: pre-session uses a range-backed dial rather than the full SVG radial interaction; cap math is booking-target based; YouTube auto-position capture remains manual through the percent sheet. These are UI/interaction fidelity gaps, not event-model blockers.
- Self-check: `pnpm --filter app typecheck` passed; `pnpm --filter app test -- session` passed (`55` files / `476` tests); `grep -n "interrupt\|materialPosition\|materialConsumedMinutes" apps/app/src/session/SessionLifecycle.ts` shows the Phase 4 lifecycle path; `grep -n "PreSessionSetup\|EndSessionSheet" apps/app/src/pages/Session.tsx apps/app/src/session/components/*` shows the wiring; `git diff --check` passed. Authored Playwright coverage in `e2e/material-session-decoupling.spec.ts` covers Home → pre-session → start → interrupt partial and Continue bypass; discovery checked with `pnpm exec playwright test --config e2e/playwright.config.ts e2e/material-session-decoupling.spec.ts --list` (not executed).
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Phase 5 — Roadmap page + booking interactions · Status: ☐

**Acceptance criteria** (contract `mocks/proposed/roadmap.html`)
- [ ] `RoadmapCalendar.tsx` uses `deriveBookingStatuses` (over `deriveBookingsForRoadmap`) — **no `deriveSlotStatuses`** in the live path; legend = done/booked/missed/unplanned (D9).
- [ ] Future = outlined **booking** bubbles (blank = "Session · pick at start"), past = filled **activity**; "+ add session" on empty in-month days.
- [ ] Collapsible **Materials directory panel** below calendar (from `buildMaterialLedger`, per-material progress + Mark progress).
- [ ] Header **ETA card** (finish + burn-up sparkline, **provisional**); full 5–6 row month grid (no clipping).
- [ ] Booking editor: swap/detach material (`BookingEdited`, `materialId:null`), **duration stepper** (`BookingEdited`, *not the dial*), move day (`BookingEdited`), **remove** (`BookingCleared`) (D21).
- [ ] Add-session sheet → `SessionBooked`; material picker includes "No material · pick at start".
- [ ] `RoadmapEdited`/`logRoadmapEdit` slot-coordinate path replaced by booking events; `SessionDetailModal` = read-only past-session detail.
- [ ] Materials directory **Mark progress** emits `MaterialProgressMarked{roadmapCreatedAt, materialId, markedAt, materialPosition, source:'directory'}`; it updates ledger/ETA and does not emit `SessionLogged`.
- [ ] `pnpm --filter app typecheck` + `pnpm --filter app test -- RoadmapCalendar calendarModel` green; Playwright authored (not run).

**Implementer report:** _( … )_
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Phase 6 — ETA composite + Week wiring · Status: ☐

**Acceptance criteria** (research §2 / D-07/D-08)
- [ ] `packages/progress/src/projectFinish.ts` with `COLD_START_N = 5` and switch: (1) `sessionCount<5` → analytic; (2) GP finish ≥ horizonEnd (non-crossing) → analytic; (3) else GP point + CI.
- [ ] `sessionCount === 0 || consumedActualMin <= 0` returns `finishDate:null` with `basis:'analytic'` and `provisional:true`; product does not claim an ETA before evidence even though the Python helper returns today for no sessions.
- [ ] Analytic uses **actual-minutes currency** (`consumedActual/elapsedDays` rate; `remainingActual/rate` days) with **no throughput multiplication**; mirrors `forecast_gp_plus_analytic_finish`.
- [ ] `progress.ts` uses `projectFinish`; `projection` carries `basis`/`provisional`; CI only when `basis==='gp'` (analytic CI = null — not presented as calibrated).
- [ ] This phase intentionally updates the local TS progress path consumed by the app; `/v1/progress` parity remains deferred unless the service becomes a live app dependency.
- [ ] Home / Week / Roadmap ETA render the finish with a **provisional** eyebrow.
- [ ] Week `plannedMinutesThisWeek` from **capacity** (D-08); no other Week UI change; no booked-day marker.
- [ ] `pnpm --filter @study-tracker/progress test` green; `projectFinish.test.ts` covers all three branches + actual-minutes/no-pace-multiply; a case cross-checked vs the Python reference where feasible.

**Implementer report:** _( … )_
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Phase 7 — Replan window · Status: ☐

**Acceptance criteria** (contract `mocks/proposed/replan.html` / D-09/D22)
- [ ] `Replan.tsx` no longer renders `SchedulePreview` or calls `replanRoadmap`/`mapToRegenerateRequest` (slot-regen retired).
- [ ] Levers = extend-deadline presets · hours/day stepper + study-day chips · per-material **shorten stepper + × drop** · "Keep current" = accept later finish; layout = split levers + sticky outcome (matches mock).
- [ ] Live projected finish via `projectFinish` (P6) updates as levers change (**provisional**).
- [ ] Commit emits `RoadmapReplanned` with new **capacity+deadline+`materialIds`+`materialDurationOverrides`** (no slots) + `BookingEdited`/`BookingCleared` for booking changes; dropped materials are removed from `materialIds`; "Keep current" emits nothing.
- [ ] No `/v1/roadmap/regenerate` call in the replan path.
- [ ] `pnpm --filter app typecheck` + `pnpm --filter app test -- Replan` green; Playwright authored (not run).

**Implementer report:** _( … )_
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Final gate (after all phases ✅ Verified)
- [ ] `pnpm lint && pnpm typecheck` clean across packages.
- [ ] `pnpm --filter app test && pnpm --filter @study-tracker/progress test && pnpm --filter @study-tracker/roadmap-engine test` green.
- [ ] E2E suites authored (not run — env constraint); listed for a `node>=20` run later.
- [ ] `DECISIONS.md` `#3` remains 🟡 QUALIFIED; claims-ledger external-validity caveat (OQ-04) intact.
- [ ] `.work/STATUS.md` row updated to reflect implementation state.
