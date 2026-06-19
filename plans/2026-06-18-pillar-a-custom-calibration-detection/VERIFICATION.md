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

_Commit SHA:_ `26d296f099c6f66c538b541fc06691ea6cc378ca`.

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

_Files changed / SHA / what / deviations / self-check:_ …

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

…

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
