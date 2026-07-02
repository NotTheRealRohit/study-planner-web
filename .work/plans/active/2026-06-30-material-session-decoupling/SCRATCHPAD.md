# Scratchpad - 2026-06-30-material-session-decoupling
_Plan: .work/plans/active/2026-06-30-material-session-decoupling/PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-02T08:25_

## Now
Phase 7 review returned `Changes requested`; F1-F3 rework is implemented, verified, and committed at `6d4cc89`. Awaiting Cowork reviewer re-check.

## Alignment
Aligned with PLAN.md Phase 7 / D-09 / D22 and the review. Slot-regeneration remains retired; `RoadmapReplanned` remains a capacity/deadline/material snapshot plus booking events, with no slots or `/v1/roadmap/regenerate` call.

## Open
- Cowork reviewer re-check of Phase 7 rework.

## Blockers
- — none

## Deferrals
- `replanRoadmap.ts` / `mapToRegenerateRequest.ts` kept but no longer called from Replan.tsx (retired from live path).
- `/v1/roadmap/regenerate` removed from replan path per D-09.
- E2E specs are not the first verification target for this rework; focus on app unit tests + typecheck unless the changed surface needs browser confirmation.

## Checklist
- [x] Trace current Replan.tsx, commitReplan.ts, mapEvents/material ledger, and related tests.
- [x] Fix lever state initialization from async `replanData` without clobbering user edits.
- [x] Make live projection capacity-aware and shorten/drop-aware.
- [x] Consume `materialDurationOverrides` on read for roadmap ETA/directory/remaining.
- [x] Compute `weeks` from replan start-to-deadline span in `commitReplan`.
- [x] Add/update unit tests for F1-F3.
- [x] Run focused tests, typecheck, lint, and diff-check.
- [x] Append VERIFICATION.md rework report and update STATUS.md/PLAN.md.

## In-flight edits
— none expected after commit `6d4cc89`; verify with `git status --short --branch` before resuming.

## Decisions in force
- Commit order: RoadmapReplanned → BookingCleared × N → SessionBooked × M
- Live re-projection may stay analytic/fast, but must be capacity-aware and visibly respond to hours/day, study days, shorten, and drop.
- Single hoursPerDay stepper applies to both weekday/weekend unless code inspection shows the mock/plan requires split controls.
- Replan.test.tsx mocks commitReplan; commitReplan.test.ts covers the full emit sequence
- Verification passed: `pnpm --filter app test -- Replan mapEvents roadmapProgress commitReplan` (58 files / 509), `pnpm --filter app typecheck`, `pnpm lint` (0 errors, 4 pre-existing warnings), `git diff --check`.
- Commit: `6d4cc89` (`fix(replan): close phase 7 review gaps`).

## Resolved (recent)
- Phase 5/6 deviations rectified + E2E run green; both ✅ Verified.
- D6 pace-first recommendation implemented and verified (Phase 6 resolution).
- Phase 7 initial implementation committed at `31feaa2`; review found F1-F3 requiring rework.
- F1 fixed: async capacity hydration + capacity-aware finish preview.
- F2 fixed: `materialDurationOverrides` consumed/preserved on read/apply.
- F3 fixed: replanned `weeks` recomputed from start→deadline span.
