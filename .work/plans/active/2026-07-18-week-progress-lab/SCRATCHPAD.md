# Scratchpad - 2026-07-18-week-progress-lab

_Plan: `.work/plans/active/2026-07-18-week-progress-lab/PLAN.md` · Log: `VERIFICATION.md` · Updated: 2026-07-18T15:12+05:30_

## Now

Phase 2 is verified and ready for its scoped implementation commit.
The immediate next task is to record that SHA, mark Phase 3 in progress, and add failing shared-capacity tests.

## Alignment

The work matches the approved four-phase plan and visual mock.
The required planning baseline was committed before any source change as `845499b`.

## Open

- Confirm the portal and responsive SVG geometry with the required browser viewports in Phase 4.

## Blockers

- None.

## Deferrals

- Browser screenshots and full E2E verification are deferred to Phase 4 after all interactions are wired.

## Checklist

- [x] Read `.work/README.md`, `.work/STATUS.md`, the approved mock, and the relevant project rules.
- [x] Create and commit canonical `PLAN.md` and `VERIFICATION.md` before source changes.
- [x] Mark Phase 1 and `.work/STATUS.md` in progress.
- [x] Run Phase 1 prerequisite tests.
- [x] Add failing helper and opener behavior tests.
- [x] Refactor the reusable plot and card opener.
- [x] Run focused Phase 1 verification.
- [x] Capture and inspect the default card with zero X-label collisions.
- [x] Record the Phase 1 commit SHA.
- [x] Mark Phase 2 in progress.
- [x] Add failing modal interaction tests.
- [x] Implement the portal dialog and responsive CSS.
- [x] Verify focus, dismissal, checkpoint selection, and range behavior.
- [x] Capture and inspect all three required Phase 2 viewports.
- [ ] Record the Phase 2 commit SHA.
- [ ] Mark Phase 3 in progress.

## In-flight edits

- `BurnUpChart.tsx` now exports the reusable plot and pure chart helpers.
- `BurnUpChart.test.tsx` has 13 passing focused tests.
- Phase 1 `.work` evidence records implementation SHA `eeaee51`.
- `ProgressLabModal.tsx`, its scoped CSS, and five behavior tests are complete.
- Phase 2 `.work` evidence is complete but the implementation SHA is pending.

## Decisions in force

- Preserve the current Marginalia card at rest.
- Use deterministic observed-date ticks and retain the complete Y-axis upper bound.
- Keep actual progress and the reference marker always visible.
- Use fixed Full plan, 30 days, and This week ranges.
- Use the shared Replan capacity model for current-week scenarios only.
- Do not change progress-package types, database schemas, event shapes, or synchronization behavior.

## Resolved (recent)

- The missing root `MASTER_TRACKER.md` is not a blocker because `.work/README.md` confirms it was consolidated into `.work/STATUS.md` and `.work/master-tracker-detail.md` on 2026-06-25.
- Existing unrelated dirty work can be preserved with narrowly scoped staging.
- Phase 1 browser geometry initially exposed crowded labels.
  A greedy four-row label placement pass removed every detected collision without hiding observed ticks.
- Phase 1 was committed as `eeaee51` with only this task's source, tests, screenshot, and `.work` files staged.
- Phase 2 browser inspection found a 6px inline-SVG scroll-height artifact in the chart stage.
  Setting the chart SVG to `display: block` removed it, and all measured regions now report zero overflow.
