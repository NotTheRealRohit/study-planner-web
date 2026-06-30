---
title: "VERIFICATION — research ETA model selection + Pillar-A re-validation"
companion: ./PLAN.md
status: p0-complete-p0b-frozen-baseline-snapshotted · R1-ready
legend: "☐ not started · 🟡 implemented, awaiting reviewer · ✅ reviewer-verified · ❌ failed/blocked"
---

# Verification log

> **Protocol.** The executor fills the *Developer* block of each phase (what was done, files, commit SHA,
> deviations, evidence) and flips the phase marker ☐→🟡. The **reviewer** reads the spec + the actual diff
> + the stamped result JSONs, fills the *Reviewer* block, and flips 🟡→✅ (or ❌ with reasons). **A phase
> is not done until the reviewer signs it.** Record real numbers and real run-vs-authored-only status — no
> fabrication (PLAN §0.3).

---

## P0 — Baseline, environment, commit-the-plan  ✅ (P0b frozen baseline on disk and snapshotted — R1 ready)
**Acceptance criteria**
- [x] Planning docs committed before any code (Step-0). SHA: `17bb1af4b2ca8b85430aa94bfd50fe1e79e277d1`
- [x] Harness test status recorded (ran: `92/94` pass; or blocked with reason): `2 failed in research/comparison/tests/test_closed_loop.py; both fail because closed-loop regeneration passes RoadmapInput(materials=[]) into py_roadmap_engine, which raises ValueError("at least one material required"). Initial sandbox run was blocked by uv cache permission at /Users/rsaji/.cache/uv; escalated uv run completed.`
- [x] A-series projection provenance recorded from `research/results/projection/projection_results.json`:
      `dataset_id=synthetic-reality-3b404c903563-seed0-n3600`, `seeds=200`, `bands=small,medium,max`, `n_learners=3600`, `scored_split=held_out`.
- [x] Baseline headline numbers snapshotted: calibration winner/Holm survivors; detection robust-null;
      projection coverage/MAE/sharpness per band.
- [x] P0b corrective frozen A-series baseline regenerated on `research/datasets/synthetic-21c2cdabfa91-seed0-n5400` and snapshotted; D-08 superseded by D-09.
- [x] Refreshed calibration result contains `enriched_shrink` and current-code dual-prior candidate `enriched_dual_prior`.

**Developer notes:** P0 implemented by Codex on 2026-06-30. Step-0 planning-doc commit:
`17bb1af4b2ca8b85430aa94bfd50fe1e79e277d1`. P0 evidence commit:
`5a3eec91bdb05de177428f597543869c113d110f`.

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

**Reviewer findings (2026-06-30 · Cowork/planner):** Execution **ACCEPTED**; parity target **REJECTED**
(D-08). P0 stays **🟡** pending one corrective run (**P0b** below). **R1 is UNBLOCKED — start it now in
parallel.** All claims independently re-verified against the repo.

*Verified ✅:*
- Commits scoped correctly: `17bb1af` added the plan docs (PLAN/SCRATCHPAD/VERIFICATION + a saved
  `prompt.txt`); `5a3eec9` touched **only** SCRATCHPAD + VERIFICATION → **no code changed**, so the two
  `test_closed_loop` failures are **pre-existing**, not introduced.
- Test status real (92 passed / 2 failed). The 2 failures live in the **closed-loop** track
  (`py_roadmap_engine` rejecting `RoadmapInput(materials=[])`), which is part of the **retired
  scheduling/closed-loop area — OUT of scope** (§5c drops scheduling). **Not a blocker;** leave as-is.
- Provenance faithfully reported, and — credit to the executor — **both** real problems were *flagged*
  rather than buried.

*Critical finding — why P0 is not ✅ (parity anchor is the wrong dataset):* all three on-disk result JSONs
(`projection`, `calibration`, `detection`) were generated from
`synthetic-reality-3b404c903563-seed0-n3600` — the **reality-matched, 6-archetype (3 train / 3 held),
n3600** lineage (`generator_regime=reality_matched`), **not** an A-series frozen baseline. Two
consequences make it unusable as the headline parity anchor:
  1. The on-disk **calibration** baseline contains legacy candidates only
     (`covariate_bayes, eb_partial_pool, ewma, hierarchical_bayes, kalman, pooled_bayes, sma`) —
     **no `enriched_shrink` / `dual_prior`**. R2's entire purpose is to re-confirm those two transfer;
     there is nothing to compare them against. (The live code *does* register them —
     `baselines/calibration.py:932-933` — so a fresh run will include them.)
  2. R5 requires dissertation-grade parity with the **A-series** (9 archetypes, 5 train / 4 held). The
     reality 6-archetype run is a different experiment (PA+.7 reality-matching), not the A-series baseline.

→ **D-08 is rejected.** The correct anchor is already on disk and free to use:
`synthetic-21c2cdabfa91-seed0-n5400` — **frozen** regime, **9 archetypes × 3 bands × 200 = 5400**, which
is exactly what the live `PARAMS_VERSION_HASH` and the dual-prior `FROZEN_REFERENCE_DATASET_ID` resolve to.
(Note: the older `e716cd12dddc`/n3600 frozen lineage the claims-ledger cites also exists on disk — in the
R5 ledger note, record which lineage each number comes from; do **not** silently mix lineages.)

*REQUIRED — P0b (does NOT block R1; must land before R2/R4/R5 comparisons):* regenerate the frozen
A-series baseline with the **current** code, all three tracks, on the 9-archetype frozen dataset, to the
**default** out-dirs (this IS the legitimate A-series baseline — default out-dirs are correct here; the
"separate --out-dir" rule applies only to the *decoupled* runs):
```
uv run --package research-comparison python -m research_comparison.runners.calibration \
  --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet
uv run --package research-comparison python -m research_comparison.runners.detection  \
  --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet
uv run --package research-comparison python -m research_comparison.runners.projection \
  --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet
```
Then: confirm the calibration result now contains `enriched_shrink` + `dual_prior`; re-snapshot the three
headline blocks into SCRATCHPAD §5 as the **authoritative** P0 baseline; mark D-08 superseded by a new
decision recording the frozen 9-archetype anchor. Flip P0 → ✅ once P0b's baseline is on disk and
snapshotted.

*Out of scope / no action:* the 2 closed-loop test failures (retired track). *Open for Rohit (optional):*
whether to also refresh the reality lineage — not needed for this workstream.

**Developer P0b follow-up (2026-06-30 · Codex):** Completed the reviewer-required corrective baseline.
D-08 is superseded; the authoritative P0 parity anchor for R2/R4/R5 is now the frozen A-series dataset
`synthetic-21c2cdabfa91-seed0-n5400` (9 archetypes × 3 bands × 200 seeds = 5400 learners).

Commands run:
```
uv run --package research-comparison python -m research_comparison.runners.calibration \
  --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet
uv run --package research-comparison python -m research_comparison.runners.detection \
  --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet
uv run --package research-comparison python -m research_comparison.runners.projection \
  --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet
```

Result files verified on disk:
- `research/results/calibration/calibration_results.json` — `102M`, mtime `2026-06-30 11:48`.
- `research/results/detection/detection_results.json` — `13M`, mtime `2026-06-30 11:48`.
- `research/results/projection/projection_results.json` — `74M`, mtime `2026-06-30 12:28`.

Shared P0b provenance from all three result JSONs:
`dataset_id=synthetic-21c2cdabfa91-seed0-n5400`; `seed_count=200`; `bands=[small, medium, max]`;
`n_learners=5400`; `scored_split=held_out`; `generator_version=0.1.0`;
`params_version_hash=21c2cdabfa91`; train archetypes
`crammer,marathon_runner,morning_lark,steady,steady_improver`; held-out archetypes
`deadline_sprinter,fading_flame,night_owl,weekend_warrior`.

P0b calibration snapshot:
- Candidate set is now `archetype_router_hard, archetype_soft, covariate_bayes, eb_partial_pool,
  enriched_dual_prior, enriched_shrink, ewma, hierarchical_bayes, kalman, oracle_calibration,
  pooled_bayes, sma`. This satisfies the reviewer requirement for `enriched_shrink` plus dual-prior
  visibility; the actual current-code candidate name is `enriched_dual_prior`.
- `m_global` winners are all `oracle_calibration`. Non-oracle comparison values:
  max `hierarchical_bayes=0.026354900745805085`, `enriched_shrink=0.056212252802336035`,
  `enriched_dual_prior=0.062103710154268625`; medium
  `hierarchical_bayes=0.04562505437289908`, `enriched_shrink=0.049223212296770055`,
  `enriched_dual_prior=0.06371362073990708`; small
  `hierarchical_bayes=0.07906760923042382`, `enriched_shrink=0.04944408506263499`,
  `enriched_dual_prior=0.07521373672819062`.
- `context_pred_mae` non-oracle values:
  max `hierarchical_bayes=0.10440349677245025`, `enriched_shrink=0.0743644361853051`,
  `enriched_dual_prior=0.07964693330557786`; medium
  `hierarchical_bayes=0.1075614799189899`, `enriched_shrink=0.08132948740137101`,
  `enriched_dual_prior=0.08712631181875113`; small
  `hierarchical_bayes=0.11106906535728693`, `enriched_shrink=0.09635347023180586`,
  `enriched_dual_prior=0.1004458991381396`.
- Holm survivors vs `hierarchical_bayes`: `context_pred_mae` has
  `archetype_router_hard, archetype_soft, covariate_bayes, eb_partial_pool, enriched_dual_prior,
  enriched_shrink, ewma, oracle_calibration`; `recovery_mae` has
  `archetype_router_hard, archetype_soft, enriched_dual_prior, enriched_shrink, oracle_calibration`.

P0b detection snapshot:
- Overall winners: `cusum` for `drift`; `page_hinkley` for `step`.
- `drift` winner metrics (`cusum`): latency `1.3606837606837607`,
  false alarm `0.2960410840918919`, missed `15.0`, score `1508.761710862981`.
- `step` winner metrics (`page_hinkley`): latency `3.03`, false alarm `0.14928175554741097`,
  missed `0.0`, score `6.762043888685274`.
- Comparator details: `step/cusum` latency `1.425`, false alarm `0.3117871322402778`,
  missed `0.0`, score `9.219678306006946`; `step/csd` latency `5.155`,
  false alarm `0.08346613127896195`, missed `0.0`, score `7.241653281974049`;
  `drift/csd` latency `4.0988235294117645`, false alarm `0.04880510931950491`,
  missed `175.0`, score `17505.3189512624`; `drift/page_hinkley` latency
  `2.3905109489051095`, false alarm `0.13856685388266293`, missed `52.0`,
  score `5205.8546822959715`.
- Multiple-comparison correction baseline is `cusum`, primary `holm_bonferroni`.
  Holm-surviving wins: `csd` 3 cells and `page_hinkley` 3 cells. Exact survivor cells:
  `band=max|archetype=fading_flame|shift_type=drift` (`csd` delta `-3.318025024032897`,
  p `1.7966938086023196E-36`; `page_hinkley` delta `-3.0276344173216705`,
  p `1.270717319979601E-63`), `band=max|archetype=fading_flame|shift_type=step`
  (`csd` delta `-1.9780250240328965`, p `1.06794415545707E-12`; `page_hinkley`
  delta `-2.4576344173216707`, p `1.837227654076149E-40`), and
  `band=medium|archetype=fading_flame|shift_type=drift` (`csd` delta
  `-3.8151852022816963`, p `2.2289628195690317E-35`; `page_hinkley` delta
  `-3.2217753932095623`, p `8.763552967143099E-65`). This current-code frozen baseline is
  not the old pure robust-null snapshot.

P0b projection snapshot:
- Winners by band are all `oracle_projection`; oracle remains an upper bound only.
- `gp_ard` baseline: max coverage `0.186875`, MAE `20.1709375`, sharpness `6.610625`;
  medium coverage `0.29080357142857144`, MAE `9.4475`, sharpness `4.98110119047619`;
  small coverage `0.43822916666666667`, MAE `2.1460416666666666`, sharpness
  `1.9139583333333334`.
- `conformal`: max coverage `0.93734375`, MAE `20.1709375`, sharpness `92.0`;
  medium coverage `0.9899702380952381`, MAE `9.4475`, sharpness `85.9946130952381`;
  small coverage `0.9689583333333333`, MAE `2.1460416666666666`, sharpness `15.7884375`.
- `kalman`: max coverage `0.1065625`, MAE `34.07828125`, sharpness `1.958125`;
  medium coverage `0.1799702380952381`, MAE `12.8925`, sharpness `1.915327380952381`;
  small coverage `0.5084375`, MAE `2.5221875`, sharpness `1.82875`.
- Multiple-comparison correction baseline is `gp_ard`, primary `holm_bonferroni`.
  Holm survivors: `conformal` 12 cells, `gp_hetero_t` 12 cells, `linear` 4 cells,
  `oracle_projection` 12 cells.

Projection-run deviation and fix:
- First P0b projection run failed deterministically with `OverflowError: date value out of range`
  in `research/comparison/src/research_comparison/baselines/projection.py`, where
  `_index_to_date()` attempted to add a pathological far-future day offset emitted by the linear
  baseline.
- Fix: `_index_to_date()` now clamps non-finite/out-of-range offsets to Python's supported
  `date.min`/`date.max` range before serializing. Regression test added:
  `test_linear_forecast_caps_pathological_far_future_dates` in
  `research/comparison/tests/test_projection_track.py`.
- Verification:
  - `uv run --package research-comparison pytest research/comparison/tests/test_projection_track.py -q -k linear_forecast_caps_pathological_far_future_dates`
    → `1 passed, 9 deselected`.
  - `uv run --package research-comparison pytest research/comparison/tests/test_projection_track.py -q -k 'linear or kalman or projection_runner'`
    → `4 passed, 6 deselected`.
  - Full `test_projection_track.py` was attempted after the focused passes but interrupted by the user;
    it is not counted as completed verification.

Per reviewer instruction, P0 is flipped to ✅ because P0b's frozen baseline is on disk and snapshotted.

**Reviewer sign-off — P0b (2026-06-30 · Cowork/planner): ✅ RATIFIED. P0 is genuinely complete.**
Independently re-verified against the repo:
- All three on-disk result JSONs now stamp `synthetic-21c2cdabfa91-seed0-n5400` — **9 archetypes × 3 bands
  × 200 = 5400**, frozen hash `21c2cdabfa91`, held-out split 5-train/4-held (matches
  `DEFAULT_HELDOUT_TRAIN_ARCHETYPES`). Correct A-series anchor. ✅
- Calibration registry now includes `enriched_shrink` + `enriched_dual_prior` (+ `archetype_router_hard`,
  `archetype_soft`). The dual-prior win R2 must test **is present** on this baseline: `enriched_shrink` and
  `enriched_dual_prior` are Holm survivors vs `hierarchical_bayes` on **both** `recovery_mae` and
  `context_pred_mae`. So R2 has a genuine win to re-confirm transfers. ✅
- The "overflow fix" (`_index_to_date` clamp to `date.min/max` + non-finite guard) is **safe and
  legitimate** — it round-trips in-range dates identically and only tames pathological far-future indices
  (the frozen `max` band's long horizons trigger it; it will also matter for the R4 analytic candidate).
  Regression test added. Accepted into scope as a necessary baseline-completion fix.

Two findings to carry forward (not P0 defects — context for later phases):
1. **Detection baseline is NOT a pure robust-null on this lineage.** Current code gives `cusum` wins
   `drift` but **`page_hinkley` wins `step`**, and `csd`+`page_hinkley` Holm-survive vs `cusum` on the
   `fading_flame` cells. This matches the **A4** result, not the simpler "nothing beats CUSUM" framing.
   **R3 must state its verdict against THIS baseline** (drift→cusum, step→page_hinkley), not against a
   pure-null strawman.
2. **Name reconciliation:** the dual-prior candidate is registered as **`enriched_dual_prior`** (not
   `dual_prior` as the PLAN prose says). R2/R4/R5 must use `enriched_dual_prior` in all paired comparisons
   and write-ups.

Process note for future phases: leave the phase marker at **🟡** when you finish and let the reviewer flip
🟡→✅ (you pre-set ✅ here; substance was correct so I ratified, but keep the gate one-directional going
forward). **R1 is cleared to start.**

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
- [ ] Held-out + Holm verdict for `enriched_shrink` / `enriched_dual_prior` (the registered dual-prior
      name — see P0b sign-off) vs `hierarchical_bayes` recorded (`survives_holm_win`), compared to the P0
      baseline (both survive on the frozen baseline; goal is to confirm they still do on decoupled data).
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
