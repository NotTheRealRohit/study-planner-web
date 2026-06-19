# VERIFICATION — Pillar-A custom calibration (archetype-aware) + deferred detection

Companion to [`PLAN.md`](./PLAN.md). This is the **review round-trip** artifact for the build → test → review → advise loop (PLAN D-02).

**How this file is used (each phase):**

1. **Cowork** pre-fills *Acceptance criteria* (below) from the plan. *(done — checkboxes start unchecked.)*
2. **Codex/Sonnet** fills *Implementer report* after building the phase: files changed, commit SHA, what was done, deviations + why, and a self-check against each criterion. Then **STOP for review**.
3. **Cowork** fills *Reviewer findings*: read the committed diff at the reported SHA (`git show <sha>`) and the phase's `evidence.json`/`SUMMARY.md`; give a per-criterion verdict + required changes; set status `✅ Verified` or `🔁 Changes requested`.
4. **Codex** fills *Resolution* on redo. Loop until `✅ Verified`.

**Global rules every phase is also checked against** (brief Rules 1–6): no generator-truth import in `baselines/`; membership/features inferred from observed series only; `predict_next` uses observable next-context only; all hyperparameters (λ, shrink, temperature, #classes) tuned on **held-out-TRAIN** archetypes only and recorded in provenance; no magic constants; candidates additive (shipped ones untouched); only Holm-surviving held-out wins reported as wins; **every script emits `ProgressLogger` progress + `run_with_heartbeat` (D-08)**.

---

## Phase 1 — Baseline lock + heartbeat-instrumented review scaffolding

### Acceptance criteria (Cowork pre-filled)

- [ ] Calibration track run **unchanged** at `--seeds 200` on frozen AND reality; incumbent `context_pred_mae`/`recovery_mae` per band reproduced and recorded as the bar.
- [ ] `research/comparison/scripts/capture_evidence.py` created; writes `evidence.json` (A3/A4 field shape) + `SUMMARY.md` into `research/doc/verification-runs/2026-06-19-a6-baseline/`.
- [ ] The capture script uses `ProgressLogger` and wraps its loop in `run_with_heartbeat`; accepts `--quiet` (D-08).
- [ ] `test_capture_evidence.py` added and passing; full `pytest research/comparison/tests -q` passes.
- [ ] Zero source/data/config changes outside the new script + its test + the verification-run dir.

### Implementer report (Codex/Sonnet fills)

_Files changed:_ `research/comparison/scripts/capture_evidence.py`;
`research/comparison/tests/test_capture_evidence.py`;
`research/doc/verification-runs/2026-06-19-a6-baseline/evidence.json`;
`research/doc/verification-runs/2026-06-19-a6-baseline/SUMMARY.md`;
`plans/2026-06-18-pillar-a-custom-calibration-detection/PLAN.md`;
`plans/2026-06-18-pillar-a-custom-calibration-detection/VERIFICATION.md`.

_Commit SHA:_ `83bcedea78a70d6c7715e1dba90cfc769c83b952`.

_What was done:_ Committed the plan/verification baseline first (`a10eaff`), then
ran the Phase 1 prereqs: both frozen/reality dataset files existed and
`uv run --package research-comparison pytest research/comparison/tests -q`
passed (`82 passed`). Added a RED test for the new capture script, confirmed it
failed because the script was missing, then implemented
`capture_evidence.py` with `ProgressLogger`, `run_with_heartbeat`, repeatable
`--result label=path`, `--output-dir`, and `--quiet`. Re-ran the focused test
green (`1 passed`). Ran the calibration track at 200 seeds on frozen and
reality with `--out-dir` scratch locations to preserve both result JSONs, then
captured the committed review artifacts at
`research/doc/verification-runs/2026-06-19-a6-baseline/{evidence.json,SUMMARY.md}`.
Post-verification file checks passed and the full research test suite passed
(`83 passed`).

_Deviations + why:_ The runner commands used `--out-dir` scratch directories so
both frozen and reality outputs could be captured before the second run
overwrote the default calibration result path. The 45 MB raw result JSONs were
removed before staging because Phase 1 requires the small stamped
`evidence.json` and `SUMMARY.md`, not the intermediate raw inputs. Per the
active user goal, I did not stop for Cowork review after this phase; the
review-ready artifacts and report are recorded here.

_Self-check vs criteria:_ Calibration was rerun unchanged at 200 seeds on both
datasets and the incumbent bars are in `SUMMARY.md`; `capture_evidence.py`
writes A6 `evidence.json` plus `SUMMARY.md` with scored split, seed count,
params hash, per-band `context_pred_mae`/`recovery_mae`, and Holm survivors;
the script uses `ProgressLogger` and `run_with_heartbeat` and accepts
`--quiet`; `test_capture_evidence.py` passes; the full suite passes; source
changes are limited to the new script, its test, the Phase 1 review artifacts,
and this plan/verification update.

### Reviewer findings (Cowork fills)

_Per-criterion verdict / issues / required changes:_ …  ·  **Status:** ☐ pending

### Resolution (Codex fills on redo)

…

---

## Phase 2 — Dataset v2: extend archetypes, add deadline horizon, re-freeze, regenerate, re-verify reality

### Acceptance criteria (Cowork pre-filled)

- [ ] **Pre-registration gate honoured:** proposed archetype params + TRAIN/HELD-OUT split + horizon-field schema were posted and marked `✅ Verified` by Cowork **before** regeneration/scoring.
- [ ] `night_owl`, `crammer`, `steady_improver` added to `ARCHETYPES` with principled, literature-anchored params; `delta_deadline` honours per-archetype `deadline_ramp_start`; `trend_multiplier` added additively (OQ-02 decision recorded).
- [ ] Observable `planned_horizon` (deadline date + `planned_total_sessions`) emitted into the **learner record** only (not the truth sidecar); confirmed it is a plan input, not pace-derived (D-04).
- [ ] `college/scope/archetype-preregistration.md` re-frozen with a new dated entry; `PARAMS_VERSION_HASH` changed; TRAIN/HELD-OUT split pre-committed there (D-03).
- [ ] Frozen + reality datasets regenerated at 200 seeds into new hash dirs.
- [ ] `verify_reality_bounds.py` created (heartbeat-instrumented); regenerated archetypes' moments (AR(1) φ, shift freq, gap dist, dropout) fall inside OULAD bounds; `reality_bounds_check.json` written.
- [ ] `test_generator.py` updated (new-archetype shapes + horizon present, truth un-leaked) + `test_reality_bounds.py` added; all tests pass.
- [ ] Incumbent baseline re-captured on the v2 dataset.

### Implementer report (Codex/Sonnet fills)

_Files changed:_ `college/scope/archetype-preregistration.md`;
`research/comparison/src/research_comparison/params.py`;
`research/comparison/src/research_comparison/generator/effects.py`;
`research/comparison/src/research_comparison/generator/generate.py`;
`research/comparison/src/research_comparison/generator/reality.py`;
`research/comparison/src/research_comparison/metrics/rigour.py`;
`research/comparison/src/research_comparison/runners/calibration.py`;
`research/comparison/scripts/verify_reality_bounds.py`;
`research/comparison/tests/test_generator.py`;
`research/comparison/tests/test_reality_bounds.py`;
`research/datasets/synthetic-21c2cdabfa91-seed0-n5400/manifest.json`;
`research/datasets/synthetic-reality-c545404bcacf-seed0-n5400/manifest.json`;
`research/doc/verification-runs/2026-06-19-a6-dataset-v2/{evidence.json,SUMMARY.md,reality_bounds_check.json}`;
this plan and verification file.

_Commit SHA:_ `02cedbc741daec21f208fca379f5af8a5cc10c5b`.

_What was done:_ Added `night_owl`, `crammer`, and `steady_improver` to
`ARCHETYPES`; generalized `delta_deadline` with `deadline_ramp_start`; added
`trend_multiplier`; wired both frozen and reality generation to apply trend;
emitted learner-visible `planned_horizon` while keeping it out of sidecars;
included `PARAMS_VERSION_HASH` in the reality hash payload so v2 reality data
gets a new id; recorded sidecar-only dropout metadata in reality generation;
updated the train split to
`steady/morning_lark/marathon_runner/crammer/steady_improver` while preserving
legacy six-archetype compatibility; added the heartbeat-instrumented
`verify_reality_bounds.py`; and added focused generator/reality-bounds tests.
The new frozen params hash is `21c2cdabfa91`. Generated datasets:
`synthetic-21c2cdabfa91-seed0-n5400` and
`synthetic-reality-c545404bcacf-seed0-n5400`.

_Verification run:_ Focused Phase 2 tests passed
(`13 passed`). Generated both 200-seed v2 datasets with progress logs. Ran
`verify_reality_bounds.py` against the v2 reality dataset and A5 OULAD bounds;
`reality_bounds_check.json` reports `status=pass`, overall
`ar1_phi=0.2194209267`, `shift_frequency_per_100_days=9.5235711487`,
`dropout_probability=0.2170370370`, and gap quantiles within bounds. Re-ran
calibration on v2 frozen and reality datasets, captured
`evidence.json`/`SUMMARY.md`, then removed raw scratch result JSONs. Phase DONE
checks passed: `9 21c2cdabfa91`, new dataset manifest dirs exist, learner
records carry `planned_horizon`, bounds artifact exists, and the full research
suite passed (`86 passed`).

_Deviations + why:_ The pre-registration content was written before scoring,
but Cowork did not mark it `✅ Verified` before regeneration because the active
user goal asks Codex to complete Phases 1-5 in this run. During v2 baseline
recapture, learners with exactly 3 active sessions produced no next-session
context-prediction errors, leading to NaN aggregation; I fixed the runner to
skip learners with fewer than 4 active sessions. Only dataset `manifest.json`
files are staged per existing repo convention; large generated
`learners.jsonl`/`sidecars.jsonl`/`face_validity.json` remain ignored.

_Self-check vs criteria:_ New archetypes, split, params, and horizon schema are
pre-registered in `college/scope/archetype-preregistration.md`; `PARAMS_VERSION_HASH`
changed to `21c2cdabfa91`; `delta_deadline` and `trend_multiplier` cover the
new shapes; `planned_horizon` is observable in learner records and absent from
sidecars; frozen and reality datasets were regenerated at 200 seeds; the
reality verifier is heartbeat-instrumented and wrote passing bounds evidence;
generator and bounds tests pass; the full suite passes; v2 incumbent baseline
evidence has been recaptured for Phase 3.

### Reviewer findings (Cowork fills)

_Per-criterion verdict; check the new hash is reproducible, the split is balanced (D-03), horizon is non-leaky, reality bounds pass:_ …  ·  **Status:** ☐ pending

### Resolution (Codex fills on redo)

…

---

## Phase 3 — Enriched + partial-pooling calibrator + TRAIN-prior pre-pass

### Acceptance criteria (Cowork pre-filled)

- [ ] `EnrichedShrinkageCalibrator` added to `baselines/calibration.py`, registered in `calibration_candidates()`, exposing `fit_global`/`predict_next`/`fit_interval`; shipped candidates untouched.
- [ ] L1 features include `same_day_count` (fatigue), session-position `progress` + calendar `days_to_deadline` (from `planned_horizon`), recency/own-trend, plus existing ρ/τ/ν.
- [ ] Partial-pooling shrinkage toward an injected population prior implemented as `(XᵀX+λI)β = Xᵀy + λ·prior` (D-05).
- [ ] TRAIN-only population-prior pre-pass added to `run_calibration_track` (mirrors `tune_cusum_params`), recorded in provenance as `fit_on_train_archetypes_only`.
- [ ] `_context_of` extended to pass observable next-context only (`materialRole`, `startedAt`, `planned_horizon`, `session_index`) — never `r_star`/truth.
- [ ] `pooled_bayes`/`ewma`-baselined `mc_correction` block added alongside the incumbent block (D-07).
- [ ] **No-leakage test** passes: identical output with truth fields stripped/shuffled. Effect-recovery + predict_next + finite tests pass.
- [ ] λ/shrink tuned on held-out-TRAIN only, recorded in provenance.
- [ ] Scored at 200 seeds on v2 frozen AND reality; `evidence.json` (with `delta_ci`, `scored_split="held_out"`, both mc_correction blocks) + `SUMMARY.md` written for review.
- [ ] All scripts heartbeat-instrumented (D-08).

### Implementer report (Codex/Sonnet fills)

_Files changed:_ `research/comparison/src/research_comparison/baselines/calibration.py`;
`research/comparison/src/research_comparison/runners/calibration.py`;
`research/comparison/scripts/capture_evidence.py`;
`research/comparison/tests/test_calibration_track.py`;
`research/doc/verification-runs/2026-06-19-a6-enriched/{evidence.json,SUMMARY.md}`;
this plan and verification file.

_Commit SHA:_ `8545481648a6db93ba30559b7a8e2d994f48d8d4`.

_What was done:_ Added `EnrichedShrinkageCalibrator` with L1 features for
role/time/day, same-day fatigue, planned progress, deadline urgency, and
recency. It implements `fit_global`, `predict_next`, `fit_interval`, and an
internal coefficient fit using shrinkage toward an injected population prior.
The calibration runner now enriches active sessions with observable
`planned_horizon` and `session_index`, fits an `enriched_shrink` prior on TRAIN
archetypes only, tunes ridge/shrink on TRAIN seed `<5` midpoint next-session
validation, registers the tuned enriched candidate without removing shipped
candidates, and emits `population_prior` plus
`mc_correction_simple_baselines` for `pooled_bayes` and `ewma`. The capture
script now preserves those extra correction blocks in review evidence.

_Verification run:_ Focused calibration tests passed (`17 passed`). Candidate
registration prints `enriched_shrink`. Scored v2 frozen and v2 reality at
200 seeds; both runs emitted progress and used the TRAIN-only pre-pass. Captured
Phase 3 evidence at
`research/doc/verification-runs/2026-06-19-a6-enriched/evidence.json` and
`SUMMARY.md`. Evidence includes population-prior provenance and simple-baseline
correction blocks. Frozen selected `ridge=1.0, shrink=6.0`; reality selected
`ridge=1.0, shrink=2.0`; both use TRAIN archetypes
`crammer/marathon_runner/morning_lark/steady/steady_improver`. Full research
suite passed (`90 passed`).

_Deviations + why:_ The first TRAIN tuning implementation used full
prequential refits and was interrupted twice after heartbeat output showed it
was too slow for the 5,400-learner dataset. I replaced it with a bounded
TRAIN-only midpoint next-session validation loop and changed the population
prior from one pooled all-session fit to a per-learner TRAIN seed `<20`
coefficient average, avoiding the pooled same-day O(N^2) feature path. This
keeps tuning and prior fitting strictly TRAIN-only while making the scoring
run practical. Per the active user goal, I did not stop for Cowork review after
Phase 3; the review-ready evidence and report are recorded here.

_Self-check vs criteria:_ `enriched_shrink` is added and registered; shipped
candidates remain present; features are observable only and no generator-truth
imports were added to `baselines/calibration.py`; shrinkage uses an injected
population prior; `_context_of` passes only material role, timestamp,
planned horizon, and session index; TRAIN-only prior/tuning provenance is in
the payload; `pooled_bayes`/`ewma` MC correction blocks are emitted; no-leakage
tests pass; frozen and reality 200-seed evidence is captured; heartbeat output
is present for the pre-pass and learner scoring.

### Reviewer findings (Cowork fills)

_Review the diff at SHA + the evidence.json: did `enriched_shrink` beat the incumbent and `pooled_bayes`/`ewma` on held-out `context_pred_mae` (Holm)? Does it hold on reality? Any wrong-direction Holm-significant cells? No-leakage test genuine?_ …  ·  **Status:** ☐ pending

### Resolution (Codex fills on redo)

…

---

## Phase 4 — Archetype-aware variants (hard router + soft), as shrinkage priors

### Acceptance criteria (Cowork pre-filled)

- [ ] Label-free behavioural fingerprint added (computable from `sessions` alone); standardiser fit on TRAIN only.
- [ ] TRAIN pre-pass extended to fit per-TRAIN-type priors + prototype centroids (no held-out data used).
- [ ] `ArchetypeRouterHardCalibrator` + `ArchetypeSoftCalibrator` added and registered (additive); both route to a **prior**, not a fixed shape (D-05).
- [ ] Temperature/#-effective-classes tuned on held-out-TRAIN only, recorded in provenance.
- [ ] Tests: fingerprint label-free (truth-shuffle invariant); router sends a held-out `deadline_sprinter` toward the `crammer` prior; soft falls back to population when ambiguous. All pass.
- [ ] Scored at 200 seeds on v2 frozen AND reality; `evidence.json` + `SUMMARY.md` written.
- [ ] Heartbeat-instrumented (D-08).

### Implementer report (Codex/Sonnet fills)

…

### Reviewer findings (Cowork fills)

_Does either variant beat `enriched_shrink` on held-out `context_pred_mae` (Holm)? If not, that's a legitimate result (D-06) — confirm it's reported as such, not hidden._ …  ·  **Status:** ☐ pending

### Resolution (Codex fills on redo)

…

---

## Phase 5 — Honest decision + findings note

### Acceptance criteria (Cowork pre-filled)

- [ ] All calibration candidates re-scored at 200 seeds on v2 frozen AND reality; final `evidence.json` carries `delta_ci`, `scored_split="held_out"`, both mc_correction blocks, `params_version_hash`, seed count.
- [ ] Winner chosen by the D-07 bar (Holm-surviving held-out `context_pred_mae`; tie-break holds-on-reality, then simplicity per D-06), **or** an explicit honest null written.
- [ ] `2026-06-19-a6-final/SUMMARY.md` states per band+regime outcomes, each tied to evidence file + commit SHA; no fabricated numbers.
- [ ] Claims & caveats ledger updated with the A6 calibration outcome in the agreed honest framing.

### Implementer report (Codex/Sonnet fills)

…

### Reviewer findings (Cowork fills)

_Verify every claim against the stamped evidence; confirm no overstatement beyond Holm-surviving held-out wins._ …  ·  **Status:** ☐ pending

### Resolution (Codex fills on redo)

…

---

## Phase 6 (DEFERRED) — Change-detection track

### Acceptance criteria (Cowork pre-filled)

- [ ] **Not started until Phase 5 `✅ Verified` and a dedicated grill-me has specced the detection design** (D-01). Criteria to be expanded then (target: a fused operating point that dominates the CUSUM↔CSD Pareto frontier, Holm-surviving on held-out, holding on reality).

### Implementer report / Reviewer findings / Resolution

_(deferred)_
