---
title: "VERIFICATION — research ETA model selection + Pillar-A re-validation"
companion: ./PLAN.md
status: awaiting-execution
legend: "☐ not started · 🟡 implemented, awaiting reviewer · ✅ reviewer-verified · ❌ failed/blocked"
---

# Verification log

> **Protocol.** The executor fills the *Developer* block of each phase (what was done, files, commit SHA,
> deviations, evidence) and flips the phase marker ☐→🟡. The **reviewer** reads the spec + the actual diff
> + the stamped result JSONs, fills the *Reviewer* block, and flips 🟡→✅ (or ❌ with reasons). **A phase
> is not done until the reviewer signs it.** Record real numbers and real run-vs-authored-only status — no
> fabrication (PLAN §0.3).

---

## P0 — Baseline, environment, commit-the-plan  ☐
**Acceptance criteria**
- [ ] Planning docs committed before any code (Step-0). SHA: `__________`
- [ ] Harness test status recorded (ran: `__/__` pass; or blocked with reason): `__________`
- [ ] A-series projection provenance recorded from `research/results/projection/projection_results.json`:
      `dataset_id=____`, `seeds=____`, `bands=____`, `n_learners=____`, `scored_split=____`.
- [ ] Baseline headline numbers snapshotted: calibration winner/Holm survivors; detection robust-null;
      projection coverage/MAE/sharpness per band.

**Developer notes:** _(files, SHA, what ran vs authored-only, deviations)_

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
