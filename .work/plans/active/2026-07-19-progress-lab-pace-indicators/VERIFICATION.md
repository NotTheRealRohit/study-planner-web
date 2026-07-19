# Progress Lab pace-indicators verification

**Plan:** `.work/plans/active/2026-07-19-progress-lab-pace-indicators/PLAN.md`
**Overall status:** -˜ Not started
**Last updated:** 2026-07-19

> Reviewer pre-fills acceptance criteria from the plan. Implementer (Codex/Sonnet) fills the
> report section per phase; reviewer fills findings. A phase is done only at `-œ… Verified`.
> **Option-X invariant, checked every phase:** `git diff` on
> `apps/app/src/roadmap/replan/capacityScenario.ts` and `apps/app/src/pages/Replan.tsx` is empty,
> and their test suites pass unmodified.

## Phase 1 --- End dates: goal line, finish flags, domain, clipping

### Acceptance criteria
- [ ] `BurnUpPlot` accepts optional `deadlineISO`, `forecastFinishISO`, `forecastBasis`, `scenarioFinishISO`, `totalPlannedMinutes`.
- [ ] Full-range domain includes every supplied finish date; right edge -‰¥ the latest finish (month/week ranges unchanged).
- [ ] Planned staircase and scenario line are clipped at the total (no point/segment beyond the finish x).
- [ ] Goal line renders at `totalPlannedMinutes` with the `PLAN COMPLETE Â· <total>` label and a done-zone tint above it.
- [ ] Dated finish flags render for Plan (deadline), Forecast (when present), Your pace (when a scenario is active); absent when the prop is absent.
- [ ] Dotted connector links the GP line end to the Forecast pin.
- [ ] Scenario line visibly starts at the actual endpoint and reads as a clean line; only drawn when `paceDeltaMinutes > 0`.
- [ ] Legend gains GP forecast + Your pace entries.
- [ ] New decorative SVG paths keep `pointerEvents="none"`; default Week card appearance unchanged.
- [ ] `capacityScenario.ts` / `Replan.tsx` diffs empty; their suites green.

### Implementer report
- Status: -˜ Â· Files changed: Â· Commit SHA: Â· Commands + results: Â· Deviations + why: Â· Self-check:

### Reviewer findings
- Status: -˜ (`-œ… Verified` / `ğŸ- Changes requested`) Â· Per-criterion verdict: Â· Issues / required changes:

### Resolution
- (implementer fills on redo -†’ loop until Verified)

## Phase 2 --- Coordinate crosshair (variation B)

### Acceptance criteria
- [ ] Hovering anywhere on the plot shows vertical + horizontal guides.
- [ ] A date pill renders on the X axis (date under cursor) and an hours pill on the Y axis (hours at cursor Y).
- [ ] A coloured dot sits on each visible line at the hovered date; a readout box lists each series' value.
- [ ] Actual value is absent for dates after today; scenario value absent at Current pace.
- [ ] Crosshair clears on `mouseleave`; existing checkpoint keyboard selection still works.
- [ ] Overlay hit-rect uses explicit `pointerEvents:all`; series paths remain non-interactive.
- [ ] `capacityScenario.ts` / `Replan.tsx` diffs empty; their suites green.

### Implementer report
- Status: -˜ Â· Files changed: Â· Commit SHA: Â· Commands + results: Â· Deviations + why: Â· Self-check:

### Reviewer findings
- Status: -˜ Â· Per-criterion verdict: Â· Issues / required changes:

### Resolution
-

## Phase 3 --- Narrative three-finish panel + wiring

### Acceptance criteria
- [ ] Rail narrative shows Plan (deadline), Forecast (`projection.finishDate`), and --- at +N --- the pace scenario date + delta vs deadline.
- [ ] `forecastBasis==='analytic'` shows the "estimate" tag; `'gp'` does not.
- [ ] At Current pace: no scenario line; narrative reads "current trajectory -†’ forecast" (no misleading capacity date).
- [ ] Pace slider + `Replan with this pace` link unchanged (still `/replan?paceDeltaMinutes=N`, no `/study` prefix).
- [ ] Week passes `forecastFinishISO`/`forecastBasis`/`deadlineISO`/`totalPlannedMinutes` for the current week, `undefined` when `isPastWeek`.
- [ ] Historical mode hides slider + forecast/scenario narrative + scenario/forecast flags; keeps goal line, Plan flag, crosshair.
- [ ] Narrative + legend styles use design tokens (`form-design-spacing`).
- [ ] `capacityScenario.ts` / `Replan.tsx` diffs empty; their suites green.

### Implementer report
- Status: -˜ Â· Files changed: Â· Commit SHA: Â· Commands + results: Â· Deviations + why: Â· Self-check:

### Reviewer findings
- Status: -˜ Â· Per-criterion verdict: Â· Issues / required changes:

### Resolution
-

## Phase 4 --- Integration, regression proof, visual verification

### Acceptance criteria
- [ ] `e2e/week-progress-lab.spec.ts` covers: goal line + Plan/Forecast flags, crosshair readout on hover, slider -†’ scenario line + Your-pace flag + narrative date.
- [ ] `capacityScenario` + `Replan` suites pass with **no edits** to those files (diff-stat empty --- recorded here).
- [ ] Screenshots at 1440Ã—900, 1024Ã—600, 390Ã—844: no modal/rail/chart overflow, flags + axis labels in-bounds, no console/page errors.
- [ ] `pnpm typecheck` + `pnpm lint` (repo-wide) clean; app suites green.

### Implementer report
- Status: -˜ Â· Files changed: Â· Commit SHA: Â· Commands + results: Â· Screenshot evidence: Â· Deviations + why: Â· Self-check:

### Reviewer findings
- Status: -˜ Â· Per-criterion verdict: Â· Issues / required changes:

### Resolution
-
