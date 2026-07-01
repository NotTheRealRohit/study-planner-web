# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-01T15:00_

## Now
Implementing Phase 7: Replan window — levers → live re-projection. Phases 1–6 are all ✅ Verified.

## Alignment
Aligned. Phase 7 replaces the `SchedulePreview`/`replanRoadmap`/`mapToRegenerateRequest` slot path in `Replan.tsx` with a levers + live-outcome layout per `mocks/proposed/replan.html`. Commit emits `RoadmapReplanned{materialIds, materialDurationOverrides, no slots}` + `BookingCleared` (future bookings) + `SessionBooked` (new bookings from `generateBookings`). No `/v1/roadmap/regenerate` call.

## Open
- Exact `weeklyHours` computation (using `hoursPerDay * selectedStudyDays.length` since single stepper)
- Booking commit order: `RoadmapReplanned` → `BookingCleared` × N → `SessionBooked` × M

## Blockers
- — none

## Deferrals
- `replanRoadmap.ts` and `mapToRegenerateRequest.ts` are kept (not deleted) but no longer called from `Replan.tsx`.
- `/v1/roadmap/regenerate` service call removed from replan path per D-09.

## Checklist
- [ ] Add new `.rp-*`/`.lever`/`.stepper`/`.daychip`/`.preset`/`.matline`/`.mshort`/`.mdrop`/`.provisional` CSS to `roadmap.css`
- [ ] Rewrite `commitReplan.ts` — new interface (no RoadmapOutput, no slots; takes deadline/capacity/materialIds/materialDurationOverrides/materials; clears future bookings + generates new SessionBooked events)
- [ ] Rewrite `Replan.tsx` — delete SchedulePreview/replanRoadmap/mapToRegenerateRequest; build levers + sticky outcome panel; live re-projection via projectFinish (analytic path)
- [ ] Update `commitReplan.test.ts` — test new behavior
- [ ] New `Replan.test.tsx` — levers update live finish; commit emits correct events; Keep current emits nothing
- [ ] Author (not run) E2E coverage in `e2e/material-session-decoupling.spec.ts`
- [ ] Run `pnpm --filter app typecheck && pnpm --filter app test -- Replan`
- [ ] Update `PLAN.md` Phase 7 status + fill `VERIFICATION.md` Phase 7 implementer report

## In-flight edits
- (nothing yet — starting now)

## Decisions in force
- commitReplan commit order: RoadmapReplanned → BookingCleared × N → SessionBooked × M
- Live finish projection: analytic-only (empty gpCurve) so it's fast + pure
- Single `hoursPerDay` stepper applied to both weekdayHours and weekendHours
- `materialDurationOverrides[matId]` = target remaining minutes after shorten lever
- Drop = exclude from materialIds + override = 0
- `?intent=extend` query param pre-selects +1 week extend preset (backward compat)

## Resolved (recent)
- Phase 3 and Phase 4 are reviewer-verified.
- Phase 5/6 deviations rectified + E2E run green; both ✅ Verified.
- D6 pace-first recommendation implemented and verified (Phase 6 resolution).
