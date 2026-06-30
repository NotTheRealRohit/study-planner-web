# Tracker — Research model selection (parallel workstream)

**Purpose:** a control/tracking baton so a parallel session can **drive and track the model-selection
decisions** that come out of the research re-run — distinct from the *implementation* plan (that lives in
`PLAN.md`/`VERIFICATION.md`). This doc owns the **"which model wins"** calls and the feedback loop back
into the design decisions.

**Update this doc** as runs complete: flip the gate statuses, log results, and when a gate resolves, push
the decision into `DECISIONS.md` (and the claims ledger).

---

## Companion docs (read these first)

- **Planning handoff (for Opus, the implementation plan):** `.work/handovers/2026-06-30-research-eta-model-selection.md`
  — contains the full harness map (generator, evaluators, candidate registries, run entrypoints) and the
  R1–R6 charter. Don't duplicate it here; this tracker references it.
- **Design SoT:** `.work/plans/active/2026-06-30-material-session-decoupling/DECISIONS.md` (esp. **§5c** =
  the research workstream; **#3** = the ETA design this research proves).
- **Plan + log (once Opus writes them):** `.work/plans/active/2026-06-30-research-eta-model-selection/PLAN.md`
  + `VERIFICATION.md` — implementation phase tracking lives there; **decision tracking lives here.**
- **Claims ledger (where proven results get written for the dissertation):**
  `research/doc/2026-06-18-pillar-a-report-claims-and-caveats.md`.
- **Harness:** `research/comparison/` (Makefile targets `make dataset | compare | compare-detection |
  compare-projection | sweep`; results → `research/results/{calibration,detection,projection,sweep}/*.json`,
  stamped by `generator_version`/`params_version_hash`).

## Current status (update me)

| Step | What | Status | Owner / where |
|---|---|---|---|
| Plan | Opus authors the R1–R6 implementation plan | ⏳ in progress | `plans/active/2026-06-30-research-eta-model-selection/` |
| R1 | Extend generator (planned-vs-chunk split; interrupted partials; ad-hoc cadence; bump `generator_version`) | ☐ | implementer |
| R2 | Calibration regression (does `enriched_shrink`/`dual_prior` still win?) | ☐ | implementer → **gate G1** |
| R3 | Detection regression (does CUSUM null hold under new cadence?) | ☐ | implementer → **gate G2** |
| R4 | **ETA benchmark** (gp_ard vs analytic vs gp+analytic composite) | ☐ | implementer → **gate G3 (headline)** |
| R5 | Rigour parity (200 seeds / 9 archetypes / 3 bands / Holm / held-out) | ☐ | implementer |
| R6 | Phase-5 N=1 real-data circularity guard | ☐ | Rohit (real logs) → **gate G4** |

Status keys: ☐ not started · 🟡 running/partial · ✅ resolved · 🛑 blocked.

## The model-selection gates (the decisions this workstream exists to make)

Each gate has an explicit **win criterion** and an explicit **feedback action**. A result only becomes a
dissertation claim once it passes the criterion under R5 rigour.

**G1 — Calibrator.** *Question:* under the new event mix (incl. partial-chunk throughput points, D8a), does
`enriched_shrink` (+ `dual_prior`) still beat baselines on `m_global` / `context_pred_mae`?
- **Win criterion:** Holm-significant **and** improved delta **and** holds on held-out archetypes + reality.
- **Feedback:** if yes → calibration transfers (note it). If it degrades → down-weight/exclude partials
  (revisit D8a) and re-run; record the chosen calibrator in `DECISIONS.md`.

**G2 — Detector.** *Question:* does the CUSUM **robust-null** still hold when interrupted partials + ad-hoc
arrivals add noise (latency / false-alarm-rate frontier)?
- **Win criterion:** no candidate dominates CUSUM on the latency↔FAR frontier under rigour.
- **Feedback:** if null holds → keep CUSUM. If a candidate now dominates → adopt it + update the change-
  detection survey doc + claims ledger.

**G3 — ETA / projection (headline; unblocks #3).** *Question:* which projection minimizes finish-date error
while hitting coverage — `gp_ard` (incumbent), `analytic_required_rate`, or the `gp+analytic` composite?
- **Win criterion:** best on `mean_abs_error_days` with `coverage ≈ 0.95` and acceptable sharpness,
  **paired-Holm significant vs `gp_ard`**, holding on held-out. Also decide: linear vs capacity-shaped
  reference line; cold-start fallback behaviour.
- **Feedback:** **flip #3 in `DECISIONS.md` from 🟡 to ✅** with the winning method; record the result in the
  claims ledger. This is the gate the UI's ETA visuals are waiting on.

**G4 — Real-data sanity (circularity guard).** *Question:* do partial-chunk throughput + the chosen ETA
behave sanely on Rohit's own N=1 logged sessions (synthetic scoring is model-dependent)?
- **Win criterion:** face-validity overlay holds; no gross divergence from synthetic.
- **Feedback:** add the external-validity note to the claims ledger; if it diverges, caveat or revisit G3.

## How to read a run

- Results JSON per stage carries `rows` (per-learner), `paired_vs_incumbent` (delta, p_value, CI),
  `mc_correction` (Holm), `winners`, and a `_provenance` manifest. Trust **held-out + Holm-surviving**
  numbers; treat train-only or non-Holm wins as suggestive, not claimable (this is the A-series standard).
- Confirm the run's `generator_version`/`params_version_hash` matches the **extended** generator (R1), not a
  frozen A-series dataset — otherwise you're scoring the old world.

## Feedback loop (close it explicitly)

When a gate resolves: (1) log the result + dataset hash in this tracker; (2) update the matching
`DECISIONS.md` entry (esp. **flip #3 on G3**); (3) write the claim/caveat into the claims ledger; (4) flip the
`STATUS.md` research row. Leave doc edits in the working tree for the native side to commit.

## Running log (append dated entries)

- **2026-06-30** — Tracker created. Opus authoring the R1–R6 plan in parallel. No runs yet; all gates open.
  #3 remains 🟡 pending **G3 (R4)**.
