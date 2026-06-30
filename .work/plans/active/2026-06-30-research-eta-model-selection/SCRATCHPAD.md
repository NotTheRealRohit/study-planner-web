---
title: "SCRATCHPAD — research ETA model selection (executor working memory)"
companion_spec: ./PLAN.md            # the contract — read-only to the executor
companion_gate: ./VERIFICATION.md    # formal per-phase acceptance + reviewer sign-off
maintained_by: executor (Codex)
purpose: >-
  Continuous, append-only working memory so a multi-session implementation survives context loss and
  the reviewer can reconstruct exactly what happened. Update at the START of every work session
  (set "Next actions") and at the END (append a Session-log entry). NEVER delete history — append.
legend: "☐ not started · 🟡 implemented, awaiting reviewer · ✅ reviewer-verified · ❌ failed/blocked"
last_updated: "2026-06-30 12:45 IST — Codex"
---

# Scratchpad

> Relationship to the other docs (do not blur): **PLAN.md** is the spec you follow.
> **VERIFICATION.md** is the formal gate (Developer notes you fill + Reviewer sign-off).
> **This file** is your running brain: every decision, number, deviation, blocker, and the immediate
> next step — enough that a fresh session (or the reviewer) can resume with zero extra context.

## 1. Current status (one-liner + phase board)
- **Now:** P0b frozen A-series baseline has been regenerated, snapshotted, and documented; per reviewer instruction P0 is ✅. Stop here before R1.
- **Branch / latest phase evidence commit:** `project/phase-1` @ `7c66d89` (previous P0 evidence `5a3eec91bdb05de177428f597543869c113d110f`)
- **Phase board:** P0 ✅ · R1 ☐ · R2 ☐ · R3 ☐ · R4 ☐ · R5 ☐ · R6 ☐

## 2. Next actions (the immediate queue — keep this current)
1. Commit the scoped P0b work: `SCRATCHPAD.md`, `VERIFICATION.md`, projection overflow guard, and regression test only.
2. Start R1 anchor verification and generator tests after this stop point.

## 3. Environment / run notes
- What runs in this sandbox vs authored-only (record the arm64/dep status the first time you hit it): the full research comparison pytest suite runs with escalated permissions for uv cache access; baseline result is `92 passed, 2 failed`.
- Exact commands that worked (copy the ones that ran clean):
  - `uv run --package research-comparison pytest research/comparison/tests -q` (required escalation because sandbox cannot open `/Users/rsaji/.cache/uv`; completed with 2 failing closed-loop tests).
  - `uv run --package research-comparison python -m research_comparison.runners.calibration --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet` (P0b frozen baseline; wrote `research/results/calibration/calibration_results.json`).
  - `uv run --package research-comparison python -m research_comparison.runners.detection --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet` (P0b frozen baseline; wrote `research/results/detection/detection_results.json`).
  - `uv run --package research-comparison python -m research_comparison.runners.projection --dataset-dir research/datasets/synthetic-21c2cdabfa91-seed0-n5400 --seeds 200 --quiet` (first failed on projection date overflow; passed after the overflow guard).
  - `uv run --package research-comparison pytest research/comparison/tests/test_projection_track.py -q -k linear_forecast_caps_pathological_far_future_dates` → `1 passed, 9 deselected`.
  - `uv run --package research-comparison pytest research/comparison/tests/test_projection_track.py -q -k 'linear or kalman or projection_runner'` → `4 passed, 6 deselected`.
  - `jq` extraction commands over `research/results/{calibration,detection,projection}/*_results.json`.
- New decoupled dataset id once generated: `synthetic-decoupled-<hash>-seed0-n<count>` → `<path>`

## 4. Decisions made during execution (continue PLAN §2's D-xx numbering)
> Record every choice you make that the PLAN left open or that deviates from it, with the why.
- **D-08 — OQ-4 parity source = the on-disk projection result, even though it is reality n3600 not frozen n5400.** `research/results/projection/projection_results.json` currently stamps `dataset_id=synthetic-reality-3b404c903563-seed0-n3600`, `seed_count=200`, `bands=small,medium,max`, `n_learners=3600`, `scored_split=held_out`, 6 archetypes (`3 train + 3 held_out`). PLAN D-05 explicitly says parity means matching the current on-disk A-series projection result if it differs from the expected n5400 lineage. — *why:* no fabrication; current stamped JSON is the authoritative P0 evidence. — *date:* 2026-06-30
- **D-09 — P0b supersedes D-08: authoritative parity anchor is frozen n5400.** D-08 is rejected for R2/R4/R5 parity. The authoritative P0 baseline is now the regenerated default-outdir frozen A-series run on `synthetic-21c2cdabfa91-seed0-n5400` with 9 archetypes × 3 bands × 200 seeds, `generator_version=0.1.0`, and `params_version_hash=21c2cdabfa91`. Calibration includes `enriched_shrink` and `enriched_dual_prior` (the current-code dual-prior candidate name). — *why:* R2/R4/R5 require dissertation-grade A-series parity and dual-prior/enriched-shrink visibility. — *date:* 2026-06-30
- **D-10 — Projection date overflow guard is part of P0b baseline hygiene.** The reviewer-specified frozen projection command exposed a deterministic `OverflowError: date value out of range` in the linear baseline when pathological low progress forecasted an impossible far-future date. `_index_to_date()` now clamps non-finite/out-of-range day offsets to Python's supported `date` bounds before serialization. — *why:* this preserves result generation for extreme but observed baseline paths without changing normal forecast currency or candidate registration. — *date:* 2026-06-30
- (OQ resolutions go here too: OQ-1 partial inclusion policy, OQ-2 cadence params, OQ-3 COLD_START_N +
  interval recipe, OQ-4 A-series parity config.)

## 5. Results ledger (numbers as they land — the stuff the reviewer + dissertation cite)
> Paste the real headline numbers from the stamped result JSONs. No rounding-to-make-it-look-good.
- **P0 baseline (authoritative P0b frozen A-series snapshot):** provenance for calibration/detection/projection is `dataset_id=synthetic-21c2cdabfa91-seed0-n5400`, `seed_count=200`, `bands=small,medium,max`, `n_learners=5400`, `scored_split=held_out`, `generator_version=0.1.0`, `params_version_hash=21c2cdabfa91`, formula `9 archetypes x 3 bands x 200 seeds`; train archetypes `crammer,marathon_runner,morning_lark,steady,steady_improver`; held-out archetypes `deadline_sprinter,fading_flame,night_owl,weekend_warrior`. Result files refreshed on 2026-06-30: calibration `102M` at 11:48, detection `13M` at 11:48, projection `74M` at 12:28. The previous reality-lineage n3600 snapshot is superseded for R2/R4/R5 parity.
  - Calibration candidates: `archetype_router_hard, archetype_soft, covariate_bayes, eb_partial_pool, enriched_dual_prior, enriched_shrink, ewma, hierarchical_bayes, kalman, oracle_calibration, pooled_bayes, sma`. `enriched_shrink` and current-code `enriched_dual_prior` are present.
  - Calibration `m_global` winners by band are all `oracle_calibration`. Non-oracle baselines: max `hierarchical_bayes=0.026354900745805085`, `enriched_shrink=0.056212252802336035`, `enriched_dual_prior=0.062103710154268625`; medium `hierarchical_bayes=0.04562505437289908`, `enriched_shrink=0.049223212296770055`, `enriched_dual_prior=0.06371362073990708`; small `hierarchical_bayes=0.07906760923042382`, `enriched_shrink=0.04944408506263499`, `enriched_dual_prior=0.07521373672819062`.
  - Calibration `context_pred_mae` winners are all `oracle_calibration`. Non-oracle baselines: max `hierarchical_bayes=0.10440349677245025`, `enriched_shrink=0.0743644361853051`, `enriched_dual_prior=0.07964693330557786`; medium `hierarchical_bayes=0.1075614799189899`, `enriched_shrink=0.08132948740137101`, `enriched_dual_prior=0.08712631181875113`; small `hierarchical_bayes=0.11106906535728693`, `enriched_shrink=0.09635347023180586`, `enriched_dual_prior=0.1004458991381396`. Holm survivors vs `hierarchical_bayes`: context-pred `archetype_router_hard, archetype_soft, covariate_bayes, eb_partial_pool, enriched_dual_prior, enriched_shrink, ewma, oracle_calibration`; recovery `archetype_router_hard, archetype_soft, enriched_dual_prior, enriched_shrink, oracle_calibration`.
  - Detection: current-code frozen baseline is **not** the old pure robust-null story. `cusum` wins `drift` overall (latency `1.3606837606837607`, false alarm `0.2960410840918919`, missed `15.0`, score `1508.761710862981`); `page_hinkley` wins `step` overall (latency `3.03`, false alarm `0.14928175554741097`, missed `0.0`, score `6.762043888685274`). For `step`, `cusum` has latency `1.425`, false alarm `0.3117871322402778`, missed `0.0`, score `9.219678306006946`, while `csd` has latency `5.155`, false alarm `0.08346613127896195`, missed `0.0`, score `7.241653281974049`. Holm survivors vs `cusum`: `csd` 3 cells and `page_hinkley` 3 cells, all in fading_flame (`max/drift`, `max/step`, `medium/drift`) with negative deltas; no small-band fading_flame drift win survives because deltas are positive there.
  - Projection: winners by band are all `oracle_projection` (upper bound only). `gp_ard` baseline by band: max coverage `0.186875`, MAE `20.1709375`, sharpness `6.610625`; medium coverage `0.29080357142857144`, MAE `9.4475`, sharpness `4.98110119047619`; small coverage `0.43822916666666667`, MAE `2.1460416666666666`, sharpness `1.9139583333333334`. `conformal`: max coverage `0.93734375`, MAE `20.1709375`, sharpness `92.0`; medium coverage `0.9899702380952381`, MAE `9.4475`, sharpness `85.9946130952381`; small coverage `0.9689583333333333`, MAE `2.1460416666666666`, sharpness `15.7884375`. `kalman`: max coverage `0.1065625`, MAE `34.07828125`, sharpness `1.958125`; medium coverage `0.1799702380952381`, MAE `12.8925`, sharpness `1.915327380952381`; small coverage `0.5084375`, MAE `2.5221875`, sharpness `1.82875`. Holm survivors vs `gp_ard`: `conformal` 12 cells, `gp_hetero_t` 12 cells, `linear` 4 cells, `oracle_projection` 12 cells.
- **R2 calibration (decoupled):** enriched_shrink / dual_prior held-out Holm verdict = …
- **R3 detection (decoupled):** robust-null holds? = … (deviations: …)
- **R4 ETA (decoupled) — HEADLINE:** per band, gp_ard vs analytic_required_rate vs gp_plus_analytic
  (coverage / MAE-days / sharpness); **paired-Holm vs gp_ard survives?** = … ; cold-start (R4a) = … ;
  reference-line (R4b) = done/deferred.
- **R6 N=1:** partial-throughput in-family? = … ; ETA-on-real descriptive error = …

## 6. Deviations from PLAN (what + why + reviewer-flagged?)
- Superseded: initial P0 baseline provenance used the reality `synthetic-reality-3b404c903563-seed0-n3600` / 6-archetype result because it was the current on-disk stamped result. Reviewer rejected that as the parity anchor. D-09 replaces it with the regenerated frozen `synthetic-21c2cdabfa91-seed0-n5400` / 9-archetype baseline.
- Projection P0b required a small code fix: the linear baseline could forecast dates outside Python's supported date range under pathological low-progress histories. The fix is limited to date-index clamping in `research/comparison/src/research_comparison/baselines/projection.py`, with regression coverage in `research/comparison/tests/test_projection_track.py`.

## 7. Blockers / open risks
- R1 has not started. P0b is complete; next session should begin R1.
- Baseline test suite has 2 pre-existing failures in `research/comparison/tests/test_closed_loop.py`, both from `py_roadmap_engine` rejecting `RoadmapInput(materials=[])` during closed-loop regeneration.

---

## 8. Session log (append-only — newest at the bottom)

### 2026-06-30 10:34 IST — session 1 — Codex
- **Goal this session:** Execute P0: Step-0 commit, harness baseline, provenance/headline extraction, and verification maintenance.
- **Did:** Committed the four plan docs verbatim as Step 0; ran the full research comparison pytest suite with uv cache escalation; extracted projection/calibration/detection provenance and headline baselines from stamped result JSONs.
- **Files changed:** `.work/plans/active/2026-06-30-research-eta-model-selection/SCRATCHPAD.md`; `.work/plans/active/2026-06-30-research-eta-model-selection/VERIFICATION.md`.
- **Commit SHA:** Step-0 plan commit `17bb1af4b2ca8b85430aa94bfd50fe1e79e277d1`; P0 evidence commit `5a3eec91bdb05de177428f597543869c113d110f`.
- **Results / numbers:** Harness baseline `92 passed, 2 failed`; projection provenance `synthetic-reality-3b404c903563-seed0-n3600`, `seed_count=200`, `n_learners=3600`, `scored_split=held_out`; headline numbers copied into §5.
- **Deviations / decisions:** D-08 resolves OQ-4 against the current on-disk projection result; deviations logged in §6.
- **Left off at / next:** P0 is 🟡 awaiting reviewer sign-off. Do not start dependent R1 until reviewer accepts P0 or gives the requested correction.

### 2026-06-30 11:00 IST — session 2 — Codex
- **Goal this session:** Execute reviewer-requested P0b frozen-baseline correction, then prepare to begin R1.
- **Did:** Read reviewer findings in `VERIFICATION.md`; accepted that D-08 is rejected and R1 is unblocked, with P0b required before R2/R4/R5.
- **Files changed:** `SCRATCHPAD.md` session-start update; `VERIFICATION.md` already has uncommitted reviewer notes from the user.
- **Commit SHA:** pending.
- **Results / numbers:** pending P0b runs.
- **Deviations / decisions:** D-09 created as pending correction/supersession of D-08.
- **Left off at / next:** Run the three P0b baseline commands exactly as specified by the reviewer.

### 2026-06-30 12:45 IST — session 2 closeout — Codex
- **Goal this session:** Document and commit the completed P0b frozen-baseline correction, then stop before R1.
- **Did:** Regenerated and snapshotted the frozen n5400 calibration, detection, and projection baselines; confirmed calibration includes `enriched_shrink` and `enriched_dual_prior`; recorded projection overflow bug/fix evidence.
- **Files changed:** `SCRATCHPAD.md`, `VERIFICATION.md`, `research/comparison/src/research_comparison/baselines/projection.py`, `research/comparison/tests/test_projection_track.py`.
- **Commit SHA:** `7c66d89` (`fix(research): refresh frozen eta P0 baseline`).
- **Results / numbers:** frozen baseline provenance and headline metrics copied into §5.
- **Deviations / decisions:** D-09 supersedes D-08; D-10 records the projection date-overflow guard. Full `test_projection_track.py` run was attempted after focused passes but interrupted by user, so it is not counted as completed verification.
- **Left off at / next:** Commit scoped P0b work only; start R1 in a later step.
