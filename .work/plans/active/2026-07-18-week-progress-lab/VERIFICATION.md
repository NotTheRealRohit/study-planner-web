# Week Progress Lab verification

**Plan:** `.work/plans/active/2026-07-18-week-progress-lab/PLAN.md`
**Overall status:** Planning baseline ready
**Last updated:** 2026-07-18

## Phase 1 - Chart refactor and deterministic axes

### Acceptance criteria

- [ ] The default Week card remains visually equivalent to the existing burn-up card.
- [ ] Existing empty-state and minimum-data behavior remains unchanged.
- [ ] The entire meaningful-data card is a semantic dialog opener with the quiet hover and focus cue.
- [ ] The plot is reusable by both the card and modal.
- [ ] Every visible actual point has an aligned X-axis tick.
- [ ] Wide views label visible actual dates with deterministic staggering when needed.
- [ ] Compact long-range views retain first and last labels plus intermediate minor ticks.
- [ ] This week labels every visible checkpoint date.
- [ ] The complete cumulative-hours Y axis retains its computed upper bound.
- [ ] Non-interactive SVG paths do not intercept pointer events.
- [ ] Pure helpers cover domains, ticks, interpolation, gaps, summaries, and layer visibility.

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
- Next: commit the planning baseline before source changes, mark implementation active, and begin Phase 1 with focused regression tests.
