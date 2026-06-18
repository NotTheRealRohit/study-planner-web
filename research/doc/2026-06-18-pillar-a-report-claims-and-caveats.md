# Pillar A — report claims & caveats (for the Phase 6 write-up)

> **What this is.** A durable ledger of the *honest framings* the Phase-6 report and journal
> must use for Pillar A — established during the A0–A5 rigour work and its reviews. When you
> wire the report (tracker Phase 6 / `research-tasklist.md`), the claims below are the agreed
> language; do not overstate beyond them. Source of truth for every entry: the per-phase
> **Reviewer findings** in [`plans/2026-06-14-pillar-a-rigour-VERIFICATION.md`](../../plans/2026-06-14-pillar-a-rigour-VERIFICATION.md)
> and the stamped result JSONs under `research/results/`.
>
> Add a row as each phase closes. Keep claims tied to evidence (file/commit), not memory.

## ⚠️ Priority caveat — calibration (A2): do NOT claim a clean covariate/EB win

**Tempting overstatement to avoid:** "modelling time-of-day/day-of-week/role structure (covariate_bayes / eb_partial_pool) beats pooling."

**What the evidence actually supports (A2 `4445701` + A3 `2b8e23c`):**

- On **m_global recovery**, pooling is near-optimal; `covariate_bayes`/`eb_partial_pool` are *worse* on every band. (The hierarchy "does no work" on this target — by design, not defect.)
- On **context-aware next-session prediction** (A2/D-A7), `covariate_bayes` beat pooled on the **medium/max bands by aggregate** (e.g. max Δ−0.0115, CI excl 0) at 40 seeds — a real signal where the data is rich.
- **But under A3's rigorous protocol** (200 seeds, held-out archetypes, Holm correction, per cell), those wins **do not survive**: `covariate_bayes`/`eb_partial_pool` have **no surviving Holm wins** vs the incumbent on held-out context-prediction cells, and several are significantly *worse*. Only the oracle shows consistent surviving wins.

**Agreed framing for the report:** "Context-aware modelling helps next-session pace prediction on **data-rich, seen** archetypes, but the advantage **does not generalise to held-out archetypes under multiple-comparison correction**. We therefore report it as a qualified, non-generalising effect, not a headline win. On global-pace recovery, simple pooling is near-optimal and the hierarchy adds no value — a finding in itself." Report Holm-surviving wins only as "wins."

**Evidence:** `research/results/calibration/calibration_results.json` → `mc_correction` (`survives_holm_win`); VERIFICATION A2 + A3 reviewer findings.

## Projection (A1 + A3.7): the red→green is real and earned — state it correctly

- `gp_ard` (incumbent) **under-covers badly**: held-out 95% interval coverage ≈ 0.40 / 0.264 / 0.165 (small/medium/max) vs nominal 0.95.
- The honest **within-learner** conformal (A1) only reached 0.50/0.67/0.85 — report A1 as "candidates shipped + honest under-coverage," not as the fix.
- The fix is **across-learner split-conformal** (A3.7, D-A6): held-out coverage **0.956 / 0.991 / 0.906**, ≈ nominal **by construction** (residual quantile over train-archetype learners, no tuned constant). This is the defensible "calibrated finish-date intervals" result.
- `gp_hetero_t` improves on `gp_ard` but does not reach nominal — report as the principled-but-insufficient variant.

**Caveat to keep:** A1's earlier interval used a hand-tuned `×4.20` multiplier that was **removed** in review — do not resurrect any "tuned to 0.95" phrasing. Coverage is by construction.

**Evidence:** `research/results/projection/projection_results.json` (`scored_split="held_out"`, `conformal_calibration`); VERIFICATION A1 + A3.7 reviewer findings.

## Cross-cutting (all Pillar-A claims)

- All headline numbers are under **200 seeds (3,600 learners)**, **held-out-archetype scoring**, **bootstrap CIs on Δ**, and **Holm (primary) + BH (reported)** correction. Frozen regime: params hash `e716cd12dddc`, seed 0. State this in the methods section.
- **Report only Holm-surviving wins as "wins."** A statistically significant difference in the wrong direction is not a win (the result JSONs separate `holm_significant` from `survives_holm_win`).
- **Oracles are upper bounds, not deployable candidates** — never present an oracle win as a method win. Same for any `ruptures`/CP-SAT `upper_bound` candidates added in A4.
- The synthetic generator is **neutral / literature-anchored**; no candidate is seeded with generator truth and no hyperparameter is tuned on scoring cells (the held-out split is the guard). If A5 reality-matches the generator, report ranking-hold honestly.

## Detection / scheduling — pending A4 (placeholder)

The A3 protocol already surfaced per-cell structure to characterise once A4 lands the new candidates + Pareto frontier: detection `csd`/`ewma_control_chart` beat `cusum` on some held-out cells (latency↔false-alarm trade-off); scheduling `dp_capacity`/`rule_based` beat `greedy_incumbent` on several cells. Finalise the detection Pareto-frontier framing and the scheduling winner story from the A4 results + their `mc_correction` blocks. Update this section when A4 is verified.

## Changelog

| Date | Entry | Source |
|---|---|---|
| 2026-06-18 | Created. A2 priority caveat + A1/A3.7 projection framing + cross-cutting rules recorded. | VERIFICATION A1–A3 reviewer findings; result JSONs. |
