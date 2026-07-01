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

## Phase 1 — engine bookings + event shapes · Status: ☐

**Acceptance criteria**
- [ ] `Booking { id, date, estimatedDuration, materialId?, status }` + `BookingStatus` exported from `packages/roadmap-engine/src/index.ts`.
- [ ] `generateBookings(BookingLayoutInput)` returns bookings by **book-to-exhaustion + buffer**: count = `ceil(totalMaterialMinutes / per-day capacity)` laid on selected study-days from `startDate`; bookings are **blank** (`materialId` undefined); weekend/weekday capacity honored; days past exhaustion unbooked; generated IDs are deterministic (`planned:<ordinal>:<date>` or equivalent), not `uuid()` (D-01).
- [ ] `suggestMaterialForBooking` prefers a started-but-not-done material, else foundation→anchor→practice interleave; skips done (D9a #2).
- [ ] Packer removed: no `candidateMaterialIds`/`__rest__`/tie-resolution/`tagRoleCandidates`/`assignMaterialsToSlots` in the live path (present only inside a `@deprecated generateRoadmap` if kept). `inferRole`/`ROLE_TO_LABEL`/`LABEL_TO_ROLE` retained.
- [ ] `sync/types.ts`: `SessionBookedPayload`, `BookingEditedPayload` (with `materialId?: string|null` detach), `BookingClearedPayload`, and `MaterialProgressMarkedPayload` added; `RoadmapCreatedPayload.materialIds?` and `materialDurationOverrides?` added; `RoadmapCreatedPayload.slots` made optional/legacy-only (not deleted).
- [ ] `SessionLoggedPayload`: `bookingId?`, `resolution?: 'completed'|'trimmed'|'interrupted'`, `materialPosition?`, `plannedSessionMinutes?`, and `materialConsumedMinutes?` added. `ActiveSessionRecord`/`SessionSlotData` carry `bookingId`, `materialEstimatedMinutes`, and `materialStartPosition` without breaking older records.
- [ ] `pnpm --filter @study-tracker/roadmap-engine test` green; `pnpm --filter app typecheck` green (deprecated `generateRoadmap` kept if any caller not yet migrated).
- [ ] Booking-layout tests added; tie/packing tests removed.

**Implementer report:** _(files changed · commit SHA · what was done · deviations + why · self-check)_

**Reviewer findings:** _(per-criterion verdict · issues · required changes · status)_

**Resolution (on redo):** _(loop until ✅ Verified)_

---

## Phase 2 — derivations + read-time adapter · Status: ☐

**Acceptance criteria**
- [ ] `deriveBookingStatuses(bookings, sessions, today)` → per-booking `done|booked|missed|unplanned` by **exact `bookingId`**; interrupted session does **not** mark `done`; unplanned = logged w/o matching bookingId grouped by date (D-03).
- [ ] `buildMaterialLedger` returns per-material `{estimatedMinutes, activeMinutesLogged, estimatedConsumedMinutes, remainingEstimatedMinutes, done, started, lastPosition}` and folds both `SessionLogged` partials and `MaterialProgressMarked`; `buildDailyActivity` returns per-day minutes. Both exported from `packages/progress/src/index.ts`.
- [ ] Shared calibration denominator helper uses `materialConsumedMinutes ?? plannedMinutes`; Bayesian/CUSUM/trend/calibration tests cover a partial session where `activeMinutes/plannedMinutes` would be wrong.
- [ ] `SessionEvent` gains `bookingId`/`materialPosition`/`materialConsumedMinutes`; `mapSessions` maps them.
- [ ] `mapBookings` folds `SessionBooked`/`BookingEdited`/`BookingCleared` by `bookingId` in event order (detach via `materialId:null`); scoped to active roadmap.
- [ ] **Legacy adapter** `deriveBookingsForRoadmap`: legacy `RoadmapCreated.slots` (future) → bookings (`date + plannedMinutes||capacity + candidateMaterialIds[0]`), then booking events applied on top; new roadmaps derive purely from booking events (D-02/D11).
- [ ] `mapEvents.findActiveRoadmap`, `roadmapLifecycle.ts`, and `roadmapProgress.ts` tolerate `RoadmapCreated.slots === undefined`; new material sets come from `materialIds`, legacy material sets from slots.
- [ ] `deriveSlotStatuses` marked `@deprecated` but still present (call sites migrate in Phase 5).
- [ ] Capacity weekly-target helper available for Week (D-08).
- [ ] `pnpm --filter @study-tracker/progress test` + `pnpm --filter app test -- mapEvents` green; new tests cover legacy-adapter + booking-fold + status derivation.

**Implementer report:** _( … )_
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Phase 3 — Onboarding page 3 · Status: ☐

**Acceptance criteria** (visual contract `mocks/proposed/onboarding-3.html`)
- [ ] `SchedulePreview`, `SwapFab`, tie-resolution, `previewEdits`, `generateRoadmap` slot path removed from `Step3Preview.tsx`.
- [ ] Preview = capacity **summary** (projected-finish verdict w/ **provisional** eyebrow, backlog-fits-capacity bar, sessions/total/buffer stats, material directory) + **expandable multi-month calendar** (toggle on the finish card; `‹ ›` month arrows; booked study-days marked) — matches the mock (D13/D13a).
- [ ] `Step3Materials.tsx` materials **grouped by type** (Videos/Playlists/Links/Manual, collapsible, count+total) with compact expand-on-edit rows (D14).
- [ ] Playlist row opens the **existing `PlaylistPickerPopup`** modal — not an inline checklist (D14a).
- [ ] `handleCommit` emits events in order: `MaterialAdded` per material → `RoadmapCreated` with capacity+deadline+`materialIds` and **no `slots`** → `SessionBooked` per generated deterministic booking → `OnboardingCompleted`.
- [ ] **`/study/onboarding/3?new=1` renders without the packer bug** (no tie warnings, no crash).
- [ ] `pnpm --filter app typecheck` + `pnpm --filter app test -- onboarding` green; Playwright authored (not run).

**Implementer report:** _( … )_
**Reviewer findings:** _( … )_
**Resolution:** _( … )_

---

## Phase 4 — Session flow (Home → pre-session → running end-sheet) · Status: ☐

**Acceptance criteria** (contracts `home.html`, `session-presession.html`, `session-running.html`)
- [ ] Home booking card reads "Study session · ~Nmin" + **"Suggested material: <title>"**; Start passes `SessionSlotData{bookingId, materialId, plannedMinutes, …}` to `/session` (D15). Continue card preserved.
- [ ] `Session.tsx` renders **`PreSessionSetup`** when `idle && no active record` instead of auto-starting; direct `/session` without location state derives today's booking or enters ad-hoc mode; running layout renders directly when a record exists (Continue bypasses setup — D-06).
- [ ] `PreSessionSetup` matches V1 mock: suggested material as title + `material-strip` + "Change" (picker), **`SessionDial`** for planned length (cap-aware, pace-first recommended), "Start" → `lc.start({…, materialId, plannedMinutes, bookingId})`. Dial **not** on the running screen (D-05).
- [ ] `PreSessionSetup` ad-hoc start emits `SessionBooked` first, then starts with that `bookingId`.
- [ ] `SessionLifecycle.interrupt(materialPosition?)` emits `SessionLogged{resolution:'interrupted', bookingId, materialPosition, plannedSessionMinutes, materialConsumedMinutes}`, material left open; `end()` (complete) carries `bookingId` plus complete-position denominator. `stale_midnight` now auto-interrupts (logs partial) instead of `SessionAbandoned` (D-04).
- [ ] `EndSessionSheet`: single primary **End session** opens it; position capture (presets + % slider; YouTube auto); complete-vs-keep-open smart default from position; Pause·come-back-later stays ghost (D-04/D18). Running numeric timer/frame unchanged (D-05).
- [ ] Calibration feed intact — an interrupted active session still flows into `calibration.ts` filter (G1 partials INCLUDED).
- [ ] `pnpm --filter app typecheck` + `pnpm --filter app test -- session` green; Playwright authored (not run).

**Implementer report:** _( … )_
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
