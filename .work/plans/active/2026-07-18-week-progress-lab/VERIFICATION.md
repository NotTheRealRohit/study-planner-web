# Week Progress Lab verification

**Plan:** `.work/plans/active/2026-07-18-week-progress-lab/PLAN.md`
**Overall status:** Phase 1 verified, Phase 2 ready
**Last updated:** 2026-07-18

## Phase 1 - Chart refactor and deterministic axes

### Acceptance criteria

- [x] The default Week card remains visually equivalent to the existing burn-up card.
- [x] Existing empty-state and minimum-data behavior remains unchanged.
- [x] The entire meaningful-data card is a semantic dialog opener with the quiet hover and focus cue.
- [x] The plot is reusable by both the card and modal.
- [x] Every visible actual point has an aligned X-axis tick.
- [x] Wide views label visible actual dates with deterministic staggering when needed.
- [x] Compact long-range views retain first and last labels plus intermediate minor ticks.
- [x] This week labels every visible checkpoint date.
- [x] The complete cumulative-hours Y axis retains its computed upper bound.
- [x] Non-interactive SVG paths do not intercept pointer events.
- [x] Pure helpers cover domains, ticks, interpolation, gaps, summaries, and layer visibility.

### Implementer report

- Status: Verified locally, pending phase commit
- Files changed: `apps/app/src/components/BurnUpChart.tsx`, `apps/app/src/components/BurnUpChart.test.tsx`
- Commit SHA: Pending
- Commands and results: Initial `pnpm --filter @study-tracker/app test -- BurnUpChart` baseline passed 535 tests.
  The RED run `pnpm --filter @study-tracker/app exec vitest run src/components/BurnUpChart.test.tsx` failed 5 of 13 tests on the absent interfaces.
  The final focused run passed 13 of 13 tests.
  `pnpm --filter @study-tracker/app typecheck` passed.
- Screenshot evidence: `screenshots/phase1-default-card.png` captured from the live `/study/chart-test` route at 980x760.
  Automated geometry inspection reported zero label collisions, zero console or page errors, and no body overflow.
- Deviations and reason: None.
- Self-check: The exported `BurnUpPlot` is responsive and the existing `BurnUpChart` card retains its header, 280px plot, footer, empty state, palette, and complete computed Y range.

### Reviewer findings

- Status: Verified
- Criterion verdicts: All Phase 1 criteria pass by focused tests, app typecheck, live browser geometry, and manual screenshot inspection.
- Issues and required changes: None.

### Resolution

- Phase 1 accepted for the next dependent phase.

## Phase 2 - Viewport-fit inspection modal

### Acceptance criteria

- [ ] The modal renders through a `document.body` portal with an accessible title and description.
- [ ] Full plan, 30 days, and This week ranges use the locked domains.
- [ ] Planned, GP projection, and confidence controls are independent pressed-state controls.
- [ ] Actual progress and the reference marker cannot be disabled.
- [ ] Visible checkpoints work with pointer, Enter, and Space.
- [ ] Selection adds a ring and a deterministic date, actual, plan, signed-gap, and interpretation summary.
- [ ] Selection clears when a new range excludes the selected point.
- [ ] Close, backdrop, Escape, focus trap, scroll lock, and opener focus restoration work.
- [ ] Reduced-motion preferences are respected.
- [ ] Desktop, compact-width, and short-height layouts fit without document, overlay, dialog, chart-region, or rail scrolling.

### Implementer report

- Status: Not started
- Files changed:
- Commit SHA:
- Commands and results:
- Screenshot evidence:
- Deviations and reason:
- Self-check:

### Reviewer findings

- Status: Pending review
- Criterion verdicts:
- Issues and required changes:

### Resolution

- Pending.

## Phase 3 - Shared capacity scenario and Replan hydration

### Acceptance criteria

- [ ] The demonstrated-throughput and capacity-finish logic is shared from `capacityScenario.ts`.
- [ ] The shared model uses active roadmap study days, `weekdayHours`, remaining material minutes, demonstrated throughput, and the selected pace delta.
- [ ] The result includes finish date and normalized cumulative chart points.
- [ ] Zero pace shows current capacity finish without a moss scenario line.
- [ ] Supported deltas are exactly `0`, `15`, `30`, `45`, and `60`.
- [ ] The moss scenario begins at Today's actual cumulative value and reaches final planned cumulative value on the shared finish date.
- [ ] Missing capacity inputs disable the scenario UI without breaking chart inspection.
- [ ] Historical mode hides every scenario affordance.
- [ ] The modal navigates to `/replan?paceDeltaMinutes=N` without `/study`.
- [ ] Invalid Replan query values fall back to zero.
- [ ] One-time Replan hydration adds the query delta to the current per-study-day hours.
- [ ] The initial Replan finish exactly matches the modal scenario finish.
- [ ] The modal writes no roadmap events.

### Implementer report

- Status: Not started
- Files changed:
- Commit SHA:
- Commands and results:
- Screenshot evidence:
- Deviations and reason:
- Self-check:

### Reviewer findings

- Status: Pending review
- Criterion verdicts:
- Issues and required changes:

### Resolution

- Pending.

## Phase 4 - Week integration and visual acceptance

### Acceptance criteria

- [ ] `Week.tsx` owns modal state, opener focus restoration, week bounds, historical mode, and active-roadmap scenario inputs.
- [ ] Current-week component tests cover modal inspection and scenario behavior.
- [ ] Historical component tests cover Week end and inspection-only behavior.
- [ ] The focused E2E spec uses the existing authenticated dev seeder.
- [ ] 1440x900 desktop screenshot is manually inspected.
- [ ] 1024x600 short-viewport screenshot is manually inspected.
- [ ] 390x844 phone screenshot is manually inspected.
- [ ] Complete X and Y axes are readable at all required viewports.
- [ ] Pace scenario and Replan prefill finish are identical.
- [ ] Escape and backdrop dismissal restore focus to the opener.
- [ ] Document, overlay, dialog, chart region, and control rail have no overflow.
- [ ] The browser reports no console or page errors.
- [ ] All focused, app-wide, and repo-wide verification commands pass or have an explicitly documented environment blocker.

### Implementer report

- Status: Not started
- Files changed:
- Commit SHA:
- Commands and results:
- Screenshot evidence:
- Deviations and reason:
- Self-check:

### Reviewer findings

- Status: Pending review
- Criterion verdicts:
- Issues and required changes:

### Resolution

- Pending.

## Running log

- 2026-07-18: Canonical plan and prefilled verification artifact created from the approved Week Progress Lab plan.
- 2026-07-18: Phase 1 completed with reusable chart helpers, deterministic observed-date axes, whole-card opener semantics, focused tests, clean typecheck, and a collision-free live card screenshot.
- Next: commit Phase 1, record its SHA, then implement the viewport-fit portal modal in Phase 2.
