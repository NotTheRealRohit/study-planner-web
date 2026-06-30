---
title: "VERIFICATION — research ETA model selection + Pillar-A re-validation"
companion: ./PLAN.md
status: p0-implemented-awaiting-review
legend: "☐ not started · 🟡 implemented, awaiting reviewer · ✅ reviewer-verified · ❌ failed/blocked"
---

# Verification log

> **Protocol.** The executor fills the *Developer* block of each phase (what was done, files, commit SHA,
> deviations, evidence) and flips the phase marker ☐→🟡. The **reviewer** reads the spec + the actual diff
> + the stamped result JSONs, fills the *Reviewer* block, and flips 🟡→✅ (or ❌ with reasons). **A phase
> is not done until the reviewer signs it.** Record real numbers and real run-vs-authored-only status — no
> fabrication (PLAN §0.3).

---

## P0 — Baseline, environment, commit-the-plan  🟡
**Acceptance criteria**
- [x] Planning docs committed before any code (Step-0). SHA: `17bb1af4b2ca8b85430aa94bfd50fe1e79e277d1`
- [x] Harness test status recorded (ran: `92/94` pass; or blocked with reason): `2 failed in research/comparison/tests/test_closed_loop.py; both fail because closed-loop regeneration passes RoadmapInput(materials=[]) into py_roadmap_engine, which raises ValueError("at least one material required"). Initial sandbox run was blocked by uv cache permission at /Users/rsaji/.cache/uv; escalated uv run completed.`
- [x] A-series projection provenance recorded from `research/results/projection/projection_results.json`:
      `dataset_id=synthetic-reality-3b404c903563-seed0-n3600`, `seeds=200`, `bands=small,medium,max`, `n_learners=3600`, `scored_split=held_out`.
- [x] Baseline headline numbers snapshotted: calibration winner/Holm survivors; detection robust-null;
      projection coverage/MAE/sharpness per band.

**Developer notes:** P0 implemented by Codex on 2026-06-30. Step-0 planning-doc commit:
`17bb1af4b2ca8b85430aa94bfd50fe1e79e277d1`. P0 evidence commit:
`21a08de5eb71e0108a062b30166cb5b06234868d`.

Files changed for P0 evidence: `SCRATCHPAD.md`, `VERIFICATION.md` only.

Commands run:
- `uv run --package research-comparison pytest research/comparison/tests -q`
  - sandbox attempt failed before tests: `Failed to initialize cache at /Users/rsaji/.cache/uv`.
  - escalated rerun completed: `92 passed, 2 failed in 81.80s`.
  - failing tests: `test_closed_loop_run_regenerates_when_shift_is_detected` and
    `test_closed_vs_open_metrics_include_adherence_and_finish_drift`.
  - failure root at baseline: `packages/py-roadmap-engine/src/py_roadmap_engine/engine.py:294`
    raises `ValueError("at least one material required")` after
    `research_comparison.runners.closed_loop.run_closed_loop_for_scenario(...)` calls
    `regenerate_roadmap(...)` with `RoadmapInput(materials=[])`.
- `jq` extraction commands over:
  - `research/results/projection/projection_results.json`
  - `research/results/calibration/calibration_results.json`
  - `research/results/detection/detection_results.json`

Projection provenance actually on disk:
`dataset_id=synthetic-reality-3b404c903563-seed0-n3600`; `seed_count=200`;
`bands=[small, medium, max]`; `n_learners=3600`; formula `6 archetypes x 3 bands x 200 seeds`;
`scored_split=held_out`; `generator_version=0.1.0`; `params_version_hash=3b404c903563`;
train archetypes `marathon_runner,morning_lark,steady`; held-out archetypes
`deadline_sprinter,fading_flame,weekend_warrior`.

Baseline headline snapshot:
- Calibration: on-disk candidate set is legacy-only
  (`covariate_bayes, eb_partial_pool, ewma, hierarchical_bayes, kalman, oracle_calibration,
  pooled_bayes, sma`); `enriched_shrink` and `dual_prior` are not present in this P0 JSON.
  m_global winners are `oracle_calibration` for max/medium/small; non-oracle
  `hierarchical_bayes` MAE is max `0.1529828211272382`, medium `0.11212833534127313`,
  small `0.11001981825580294`. Context-pred Holm survivors vs `hierarchical_bayes` are
  `ewma`, `sma`, and `oracle_calibration`; recovery-mae Holm survivor is `oracle_calibration` only.
- Detection: robust-null holds in this baseline. `cusum` wins drift and step; no non-oracle detector has
  `survives_holm_win=true`. Drift: latency `4.13731380394727`, false alarm `0.18408558783043402`,
  missed `168.0`, score `16808.73945349971`. Step: latency `2.5582565598190596`, false alarm
  `0.20726369989319746`, missed `285.0`, score `28507.73984905715`.
- Projection: `gp_ard` by band: max coverage `0.13083333333333333`, MAE `30.236875`,
  sharpness `9.068541666666667`; medium coverage `0.2674206349206349`, MAE `13.002420634920634`,
  sharpness `8.738333333333333`; small coverage `0.31152777777777774`, MAE `6.320277777777777`,
  sharpness `7.710277777777779`. Holm survivors vs `gp_ard`: `conformal` 9 cells,
  `gp_hetero_t` 9 cells, `kalman` 3 cells, `linear` 3 cells, `oracle_projection` 9 cells. Treat oracle
  as an upper bound only.

Deviation/reviewer flag: PLAN expected the D-05 parity target may be the frozen
`synthetic-21c2cdabfa91-seed0-n5400` / 9-archetype lineage, but the only on-disk projection result is
`synthetic-reality-3b404c903563-seed0-n3600` / 6 archetypes. PLAN D-05 says to match the current on-disk
projection result rather than guessing, so SCRATCHPAD D-08 resolves OQ-4 to the current stamped JSON.
Reviewer should either accept this parity target or request a regenerated A-series baseline before R1/R5
parity is relied on.

**Reviewer findings:** _(verdict, ✅/❌, date)_

---

## R1 — `decoupled` generator regime  ☐
**Acceptance criteria**
- [ ] New dataset `synthetic-decoupled-<hash>-seed0-n5400` created; **A-series + reality datasets
      untouched** (list `research/datasets/` before/after — both unchanged).
- [ ] `GENERATOR_VERSION == "0.2.0"`; manifest stamps base `params_version_hash` **AND** new
      `decoupled_params_hash`; `PARAMS_VERSION_HASH` and `calibration.py:49-50` reference ids **unchanged** (D-01).
- [ ] New pre-reg doc `college/scope/decoupled-session-preregistration.md` committed; cadence/partial/dial
      params frozen there with brief justification (OQ-2).
- [ ] `SessionEvent` extended (`plannedSessionMinutes, resolution, materialPosition, bookingId, isAdHoc`);
      `GroundTruth` extended (`study_days, adherence_bias, interruption_rate, adhoc_rate`).
- [ ] Tests assert (D-02/D-03): `len(r_star)==len(sessions)`; `all(duration>0)`; for every active event
      `abs(active/planned − r_star_i) < 1e-6` **including partials**; partials `resolution=="interrupted"`
      with `0<plannedMinutes<chunk`; ad-hoc sessions off study-days; `face_validity.json` has the new dists.
- [ ] Latent-pace core unchanged (no edits to `pace.py` constants / regimes / `m_global`).

**Developer notes:**

**Reviewer findings:**

---

## R2 — Calibration regression (transfer → re-confirm)  ☐
**Acceptance criteria**
- [ ] Ran on the decoupled dataset with a **separate `--out-dir`** (A-series `research/results/calibration/`
      not clobbered). Out path: `__________`
- [ ] Held-out + Holm verdict for `enriched_shrink` / `dual_prior` vs `hierarchical_bayes` recorded
      (`survives_holm_win`), compared to the P0 baseline.
- [ ] If degraded by partials: fallback run (down-weight/exclude) recorded; chosen inclusion policy +
      justification documented (OQ-1).
- [ ] Only **Holm-surviving** improvements reported as "wins."

**Developer notes:**

**Reviewer findings:**

---

## R3 — Detection regression (must re-run)  ☐
**Acceptance criteria**
- [ ] Ran on the decoupled dataset, separate `--out-dir`. Out path: `__________`
- [ ] `paired_vs_incumbent` / `mc_correction` vs `cusum` recorded; verdict stated: robust-null **holds** or
      **changed** (which detector / shift_type / band, Holm-surviving) vs A4.
- [ ] CUSUM tuning confirmed **train-archetypes-only** (no leakage); shift-onset mapping onto the active
      axis sanity-checked under the new cadence.

**Developer notes:**

**Reviewer findings:**

---

## R4 — ETA benchmark (HEADLINE)  ☐
**Acceptance criteria**
- [ ] `forecast_analytic_required_rate` + `forecast_gp_plus_analytic` added to `baselines/projection.py`
      (correct signature + return shape); both registered in `projection_candidates()` (runners/projection.py).
- [ ] No `tf` double-count (analytic implemented in actual-minutes currency per PLAN R4 note).
- [ ] Ran full decoupled dataset, separate `--out-dir`. Out path: `__________`
- [ ] Per-band coverage / MAE-days / sharpness recorded for `gp_ard`, `analytic_required_rate`,
      `gp_plus_analytic`; **paired-Holm vs `gp_ard`** with `survives_holm_win`.
- [ ] **Explicit verdict sentence:** does the composite (and/or analytic) beat `gp_ard` under held-out +
      Holm, on which bands? → `__________`
- [ ] R4a cold-start eval recorded (composite vs `gp_ard` at small `t`).
- [ ] R4b reference-line eval done **or** explicitly logged as deferred.
- [ ] Oracles still treated as upper bounds only.
- [ ] New-forecaster tests added (shape, cold-start switch, non-crossing rescue).

**Developer notes:**

**Reviewer findings:**

---

## R5 — Rigour parity + claims ledger  ☐
**Acceptance criteria**
- [ ] R2/R3/R4 protocol matches the A-series projection config recorded in P0 (D-05); provenance hashes
      stamped in each result JSON.
- [ ] `research/doc/2026-06-18-pillar-a-report-claims-and-caveats.md` appended: calibration source-change +
      transfer status; partial-inclusion caveat + policy; detection re-run verdict; ETA verdict to the
      strength Holm supports.
- [ ] Comparability doc (frozen vs decoupled headline per track) written under `research/doc/`.
- [ ] DECISIONS.md change log updated: #3 flipped to locked-claimable **or** kept 🟡 per evidence.

**Developer notes:**

**Reviewer findings:**

---

## R6 — N=1 real-data circularity guard (Research Phase 5)  ☐
**Acceptance criteria**
- [ ] Partial-session throughput `active/(position×chunk)` from real N=1 data compared to the synthetic
      partial distribution (in-family or flagged).
- [ ] ETA candidates run on the real burn-up curve; finish-date error reported **descriptively** (N=1, no
      significance / no algorithm-superiority claim).
- [ ] Descriptive bounds only — **no** synthetic parameter tuned to real data (circularity guard).
- [ ] Write-up stub under `research/doc/` (or `college/...`) with **explicit non-claims**; relevant P5
      boxes checked in `college/scope/research-tasklist.md`.

**Developer notes:**

**Reviewer findings:**

---

## Cross-cutting checks (reviewer, at wrap)
- [ ] Scheduling track **not run / not extended** (§5c dropped).
- [ ] No edits to `apps/ packages/ e2e/ services/`; only `research/`, `college/scope/` pre-reg + docs, plan docs.
- [ ] No A-series dataset/result overwritten; reference dataset ids in `calibration.py` intact.
- [ ] Every "win" in the write-up is Holm-surviving; degradations reported honestly.
- [ ] Open questions OQ-1..OQ-4 resolved here (not silently).
