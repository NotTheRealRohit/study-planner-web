# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-01T20:35_

## Now
Phase 7 (replan levers) implemented and committed at `31feaa2`. Awaiting Cowork review. All 7 phases are now implemented — Phase 7 is the only one not yet Cowork-verified.

## Alignment
Aligned. Phase 7 built per plan + mock. Three intentional deviations documented in VERIFICATION.md Phase 7 implementer report (analytic-only re-projection, single hoursPerDay stepper, clear-all+regen commit strategy).

## Open
- Cowork review of Phase 7.

## Blockers
- — none

## Deferrals
- `replanRoadmap.ts` / `mapToRegenerateRequest.ts` kept but no longer called from Replan.tsx (retired from live path).
- `/v1/roadmap/regenerate` removed from replan path per D-09.
- E2E specs authored (not run) per project constraint.

## Checklist
- [x] Add new CSS classes to roadmap.css
- [x] Rewrite commitReplan.ts + test
- [x] Rewrite Replan.tsx with levers + live outcome
- [x] New Replan.test.tsx (8 tests) + updated pages/Replan.test.tsx (2 tests)
- [x] Author E2E Playwright specs (2 new replan specs)
- [x] pnpm --filter app typecheck clean
- [x] pnpm --filter app test green (58 files / 504 tests)
- [x] pnpm lint clean (0 errors)
- [x] PLAN.md Phase 7 status updated
- [x] VERIFICATION.md Phase 7 implementer report filled
- [x] STATUS.md updated
- [x] git commit `31feaa2`

## In-flight edits
— none; all committed.

## Decisions in force
- Commit order: RoadmapReplanned → BookingCleared × N → SessionBooked × M
- Live re-projection: analytic-only (empty gpCurve) — fast, no calibration needed
- Single hoursPerDay stepper applies to both weekday/weekend
- Replan.test.tsx mocks commitReplan; commitReplan.test.ts covers the full emit sequence

## Resolved (recent)
- Phase 5/6 deviations rectified + E2E run green; both ✅ Verified.
- D6 pace-first recommendation implemented and verified (Phase 6 resolution).
- Phase 7 implemented at 31feaa2; awaiting review.
