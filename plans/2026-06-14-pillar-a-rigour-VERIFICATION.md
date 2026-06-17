# VERIFICATION — Pillar-A rigour & extensions

**Plan:** [`plans/2026-06-14-pillar-a-rigour.md`](2026-06-14-pillar-a-rigour.md)
**Slug:** `pillar-a-rigour` · **Tracker tasks:** `PA+.1–PA+.8` (`college/scope/research-tasklist.md`)
**Created:** 2026-06-17 by the Cowork planning/review agent
**Baseline at creation:** HEAD `26c31b2`, branch `project/phase-1`, clean working tree. None of A0–A5 started (verified: no `metrics/rigour.py`; projection candidates are only `gp_ard/kalman/linear/oracle`; no `infer_day_of_week`/`CovariateBayes`/`EBPartialPool`; no `ortools` dep).

> **This file round-trips between the implementer (Codex/Sonnet) and the reviewer (Cowork).**
> For each phase: the **Acceptance criteria** are pre-filled from the plan. The **implementer**
> fills its report block (files changed, commit SHA, what was done, deviations + why, self-check).
> The **reviewer** then runs the evidence commands against that SHA (`git show <sha>` / read-only
> JSON + test inspection) and fills the findings block with a per-criterion verdict and a status of
> `✅ Verified` or `🔁 Changes requested`. A phase is **not done** until it reads `✅ Verified`.

> **Reviewer ground rule (repo policy).** Trust the **diff**, corroborated by the report — not the
> report alone. All review is read-only git (`git show`/`diff`/`log`); never mutating git in this
> sandbox.

## Status board

| Phase | Title | Tracker | Implementer status | Reviewer status |
|---|---|---|---|---|
| A0 | Lock findings + rigour scaffolding | PA+.8, PA+.3(utils) | ✅ Complete — e1c6455 | — |
| A1 | Projection coverage fix (red→green) | PA+.1 | ☐ Not started | — |
| A2 | Calibration covariates + EB pooling | PA+.2 | ☐ Not started | — |
| A3 | Statistical rigour (seeds/CIs/held-out/MC) | PA+.3 | ☐ Not started | — |
| A4 | New candidates + winner tweaks + sweep | PA+.4–.6 | ☐ Not started | — |
| A5 | Reality-matched generator + external validity | PA+.7 | ☐ Not started | — |

Status vocab: `☐ Not started` · `🟡 In progress` · `🛑 Blocked: <reason>` · `✅ Complete — <sha>` (implementer) · `✅ Verified` / `🔁 Changes requested` (reviewer).

---

## Phase A0 — Lock findings + rigour scaffolding (PA+.8 + PA+.3 utils)

### Acceptance criteria

- [ ] **A0.1** `research/comparison/src/research_comparison/metrics/rigour.py` exists and exposes `bootstrap_delta_ci(deltas, *, n_boot=10000, alpha=0.05, seed=0) -> (lo, hi, point)`, `holm_bonferroni(pvalues) -> list[bool]`, `benjamini_hochberg(pvalues, q=0.05) -> list[bool]`, `heldout_archetype_split(archetypes, *, train, seed=0) -> (train_set, test_set)`.
- [ ] **A0.2** The resolved open-code-question findings (GP homoscedastic/no-AR(1); incumbent collapses to global mean; nothing currently tuned) are recorded with **file:line evidence** in a docstring/README note — this closes PA+.8.
- [ ] **A0.3** `research/comparison/tests/test_rigour.py` passes: bootstrap CI brackets a known mean; Holm/BH match hand-computed reject sets on a small p-vector; the held-out split is deterministic and disjoint.
- [ ] **A0.4** No track re-run and no change to shipped track results in this phase (pure, additive util only).

### Reviewer evidence commands (read-only)

```bash
git show --stat <sha>                       # only rigour.py + test_rigour.py (+ doc note) touched
test -f research/comparison/src/research_comparison/metrics/rigour.py && echo present
export PATH="$HOME/.local/bin:$PATH"
uv run --package research-comparison pytest research/comparison/tests/test_rigour.py -q
uv run --package research-comparison python -c "from research_comparison.metrics.rigour import bootstrap_delta_ci, holm_bonferroni, benjamini_hochberg, heldout_archetype_split; print('rigour ok')"
git diff <baseline-sha> <sha> -- research/results | head   # expect empty (no result drift)
```

### Implementer report (Codex/Sonnet fills)

- Commit SHA: `e1c6455`
- Files changed: `research/comparison/src/research_comparison/metrics/rigour.py`; `research/comparison/tests/test_rigour.py`; `plans/2026-06-14-pillar-a-rigour.md`; `plans/2026-06-14-pillar-a-rigour-VERIFICATION.md`
- What I did: Added the A0 rigour utility module with percentile bootstrap CIs for paired deltas, Holm and Benjamini-Hochberg rejection masks, and the declared held-out archetype split. Recorded the resolved open-code-question evidence in the module docstring with current file:line references. Added focused tests for bootstrap CI bracketing, hand-computed Holm/BH masks, and deterministic disjoint held-out splitting.
- Deviations + why: No implementation deviation. The local `uv` verification commands were run with sandbox escalation because uv needs its cache under `/Users/rsaji/.cache/uv`; the commands and code paths are otherwise the plan's commands.
- Self-check vs criteria (A0.1–A0.4): A0.1 met by `metrics/rigour.py`; A0.2 met by the module docstring evidence note; A0.3 met by `uv run --package research-comparison pytest research/comparison/tests/test_rigour.py -q` passing with 3 tests; A0.4 met by no track re-run and empty `git diff -- research/results`.

### Reviewer findings (Cowork fills)

- Per-criterion verdict: `…`
- Issues / required changes: `…`
- **Status:** `…`

### Resolution (implementer fills on redo)

`…`

---

## Phase A1 — Projection coverage fix (PA+.1)

### Acceptance criteria

- [ ] **A1.1** `forecast_conformal_finish` added to `baselines/projection.py` — split-conformal wrapper around the existing point forecast; returns the same dict shape (`candidate, predicted_finish_date, interval_low, interval_high, sharpness_days`) so runner/metrics are unchanged.
- [ ] **A1.2** `forecast_gp_hetero_t_finish` added — heteroscedastic/Student-t + AR(1) residual variant, implemented **behind a flag** in `packages/py-progress/src/py_progress/gp.py` (e.g. `gp_regression(..., likelihood="student_t", ar1=True)`) with the **default `gp_regression` path unchanged**.
- [ ] **A1.3** Both registered in the projection candidate list; `gp_ard` retained for before/after contrast.
- [ ] **A1.4** Projection track re-run (frozen params hash `e716cd12dddc`, seed 0; seed bump deferred to A3). `conformal` coverage ≈ **0.90–0.97** on at least the `medium` + `max` bands (where `gp_ard` was 0.32 / 0.20); sharpness reported and not absurdly inflated.
- [ ] **A1.5** `college/mydeliverables/1st-Review/report/generated/projection_reliability.pdf` **regenerated** (mtime newer than the run; shows conformal/gp_hetero_t near the 0.95 line vs gp_ard below it). *(File already exists from Phase 3 — verify it changed, not merely that it exists.)*
- [ ] **A1.6** `test_projection_track.py` extended and passing: conformal coverage ≥ 0.90 on medium+max; conformal quantile math hand-checked on a fixture.

### Reviewer evidence commands (read-only)

```bash
git show --stat <sha>
export PATH="$HOME/.local/bin:$PATH"
python3 -c "import json;d=json.load(open('research/results/projection/projection_results.json'));print({b:{'gp_ard':round(v['candidates']['gp_ard']['coverage'],3),'conformal':round(v['candidates'].get('conformal',{}).get('coverage',float('nan')),3)} for b,v in d['winner_by_band'].items()})"
uv run --package research-comparison pytest research/comparison/tests/test_projection_track.py -q
# default GP path untouched:
git diff <baseline-sha> <sha> -- packages/py-progress/src/py_progress/gp.py   # changes must be flag-gated, default unchanged
ls -l --time-style=+%s college/mydeliverables/1st-Review/report/generated/projection_reliability.pdf
```

### Implementer report (Codex/Sonnet fills)

- Commit SHA: `…` · Files changed: `…`
- Coverage before/after by band: `…`
- Deviations + why (e.g. OQ-A1 jackknife+ for short small-band seqs): `…`
- Self-check vs criteria (A1.1–A1.6): `…`

### Reviewer findings (Cowork fills)

- Per-criterion verdict: `…` · Issues / required changes: `…` · **Status:** `…`

### Resolution (implementer fills on redo)

`…`

---

## Phase A2 — Calibration covariates + empirical-Bayes pooling (PA+.2)

### Acceptance criteria

- [ ] **A2.1** `infer_day_of_week` added to `packages/py-progress/src/py_progress/bayesian.py` — pure helper mirroring `infer_time_of_day`, returning at least `weekend`/`weekday`; deterministic; **no change to existing call sites**.
- [ ] **A2.2** `CovariateBayesCalibrator` added — models pace as `m_global · ρ̂(role) · τ̂(time_of_day) · ν̂(day_of_week)` with shrinkage toward 1.0, reusing the role/context grouping in `compute_hierarchical_model`.
- [ ] **A2.3** `EBPartialPoolCalibrator` added — James–Stein-style EB shrinkage with weight `τ²/(τ²+σ²/n)` estimated from between/within-group variance.
- [ ] **A2.4** Both registered in `calibration_candidates()`; the incumbent (`IncumbentCalibration`) left **as-is** so the "ties pooled" contrast stays honest.
- [ ] **A2.5** Calibration track re-run; bootstrap CIs on Δ (A0 util) reported per band.
- [ ] **A2.6 (success criterion, D-A2)** On the **small** band, `eb_partial_pool` (and/or `covariate_bayes`) has Δ-vs-incumbent with a **bootstrap CI excluding 0 in its favour**.
- [ ] **A2.7** `test_calibration_track.py` extended and passing: `covariate_bayes` recovers planted per-bucket multipliers within tolerance; `eb_partial_pool` recovery MAE < `pooled_bayes`; `infer_day_of_week` deterministic for known timestamps.

### Reviewer evidence commands (read-only)

```bash
git show --stat <sha>
export PATH="$HOME/.local/bin:$PATH"
python3 -c "import json;d=json.load(open('research/results/calibration/calibration_results.json'));print('small candidates:', list(d['winner_per_band']['small']['candidates']))"
python3 -c "import json;d=json.load(open('research/results/calibration/calibration_results.json'));print({k:{m:d['paired_vs_incumbent'][k].get(m,{}) for m in ('eb_partial_pool','covariate_bayes')} for k in ['small']})"
uv run --package research-comparison pytest research/comparison/tests/test_calibration_track.py -q
git diff <baseline-sha> <sha> -- packages/py-progress/src/py_progress/bayesian.py   # only adds infer_day_of_week + helpers; existing call sites intact
```

### Implementer report / Reviewer findings / Resolution

- Implementer — SHA / files / small-band Δ + CI / deviations / self-check (A2.1–A2.7): `…`
- Reviewer — per-criterion verdict / issues / **Status**: `…`
- Resolution (on redo): `…`

---

## Phase A3 — Statistical rigour: seeds, bootstrap CIs, held-out archetypes, MC correction (PA+.3)

### Acceptance criteria

- [ ] **A3.1** `--seeds` knob (default **200**) threaded through all four runners; seed 0 + params hash `e716cd12dddc` kept frozen; documented that `n_learners = 6 × 3 × seeds` and the regime is unchanged.
- [ ] **A3.2** Each track's `paired_vs_incumbent` (or equivalent) carries `delta_ci_low`/`delta_ci_high` alongside `delta`/`p_value`/`effect_size`.
- [ ] **A3.3** Held-out-archetype protocol wired via `heldout_archetype_split`: any tunable candidate (A1 conformal `m`/GP-t hyperparams; A2 shrinkage; A4 detection k/h) fitted on **train archetypes only**, scored on held-out; the partition recorded in `_provenance` (disjoint).
- [ ] **A3.4** Holm (primary) + BH (reported) correction applied across all band×archetype×shift cells; which "wins" survive correction is marked.
- [ ] **A3.5** All four tracks re-run at ≥200 seeds; winner tables/figures regenerated with CIs and corrected significance flags.
- [ ] **A3.6** Each track test asserts the result JSON now carries `delta_ci_low/high` + a `mc_correction` block + a disjoint held-out partition in provenance.

### Reviewer evidence commands (read-only)

```bash
git show --stat <sha>
python3 -c "import json;d=json.load(open('research/results/calibration/calibration_results.json'));print('n_learners:', d['_provenance']['n_learners']);b=d['paired_vs_incumbent']['small']['ewma'];print('has CI:', 'delta_ci_low' in b and 'delta_ci_high' in b);print('held-out:', d['_provenance'].get('heldout_archetypes') or d['_provenance'].get('archetype_split'))"
export PATH="$HOME/.local/bin:$PATH"
uv run --package research-comparison pytest research/comparison/tests -q
```

### Implementer report / Reviewer findings / Resolution

- Implementer — SHA / files / seeds used / held-out partition / deviations / self-check (A3.1–A3.6): `…`
- Reviewer — per-criterion verdict / issues / **Status**: `…`
- Resolution (on redo): `…`

---

## Phase A4 — New candidates + winner tweaks + wider/adversarial sweep (PA+.4–.6)

### Acceptance criteria

- [ ] **A4.1 Calibration:** `kalman` (state-space random-walk pace) added (optionally `particle`).
- [ ] **A4.2 Detection:** `bocpd`, `page_hinkley`, `adwin` added; `ruptures` PELT/BinSeg added **labelled `upper_bound`** (retrospective, excluded from deployable-winner selection). CUSUM tweaks: robust running-scale standardisation + per-shift-type k/h + Page-Hinkley drift arm. **Latency↔false-alarm Pareto frontier** reported (monotone) instead of a single operating point.
- [ ] **A4.3 Scheduling:** CP-SAT/ILP exact optimum (OR-Tools) added **labelled `upper_bound`**; topological prereq scheduler + local-search (SA/tabu) repair added; greedy tweak (one-step lookahead + prereq-aware topo pre-order). Prereq-order correctness back to **1.0** on the previously-dipping mix.
- [ ] **A4.4 Sweep:** widened to **5+ points/axis** + adversarial regimes (multi-shift, step+drift, bursty missingness); **flip cells** and **per-archetype worst case** reported (not just the mean); `robustness_heatmap.pdf` regenerated.
- [ ] **A4.5** `ortools` recorded in `research/comparison/pyproject.toml` as an **optional** extra; `import ortools` works **OR** the CP-SAT candidate is gracefully skipped so CI without it still passes (OQ-A3).
- [ ] **A4.6** Per-track tests pass: each new candidate returns the track's result-dict shape and runs on a fixture; upper-bound candidates excluded from deployable-winner selection; Pareto output monotone.

### Reviewer evidence commands (read-only)

```bash
git show --stat <sha>
export PATH="$HOME/.local/bin:$PATH"
uv run --package research-comparison python -c "import ortools; print('ortools ok')" || echo "ortools absent — CP-SAT must skip gracefully"
python3 -c "import json;d=json.load(open('research/results/detection/detection_results.json'));print('detection keys:', list(d.keys()))"
python3 -c "import json;d=json.load(open('research/results/scheduling/scheduling_results.json'));print('scheduling keys:', list(d.keys()))"
uv run --package research-comparison pytest research/comparison/tests -q
ls -l --time-style=+%s college/mydeliverables/1st-Review/report/generated/robustness_heatmap.pdf
```

### Implementer report / Reviewer findings / Resolution

- Implementer — SHA / files / new candidates per track / ortools handling / prereq-order fix / deviations / self-check (A4.1–A4.6): `…`
- Reviewer — per-criterion verdict / issues / **Status**: `…`
- Resolution (on redo): `…`

---

## Phase A5 — Reality-matched generator + external validity (PA+.7)

### Acceptance criteria

- [ ] **A5.1** Generator enriched (continuous archetype space, richer regimes, bursty dropout/return, heavy tails, a **logged-time-misreporting** layer hidden from candidate inputs), gated behind a **new `dataset_id`/params hash**; the frozen `e716cd12dddc` regime preserved and **still reproduces byte-identically**.
- [ ] **A5.2** Moments (autocorrelation φ, shift frequency, gap distribution) fitted to OULAD/EdNet/Junyi **engagement** series as **bounds/ranges only** — never point-fit then scored on the same fit (circularity guard); source + proxy mapping (clicks/interactions → "minutes toward a roadmap") recorded explicitly.
- [ ] **A5.3** Full contest re-run on the reality-matched regime under the A3 rigour protocol; the **per-track ranking-hold reported**, including where it does not hold (honest external-validity result).
- [ ] **A5.4** *(Optional)* direct external validation on real engagement series with the stated proxy mapping.
- [ ] **A5.5** Generator tests: the new regime produces the planted richer structure (multi-shift labels, bursty-gap distribution, misreporting layer present-but-hidden); the frozen regime hash `e716cd12dddc` is unchanged.

### Reviewer evidence commands (read-only)

```bash
git show --stat <sha>
export PATH="$HOME/.local/bin:$PATH"
uv run --package research-comparison pytest research/comparison/tests/test_generator.py -q
python3 -c "import json;d=json.load(open('research/results/sweep/sweep_results.json'));print('dataset_id:', d.get('dataset_id'));print('stability keys:', list(d.get('stability',{}).keys()))"
# confirm the frozen-regime artifacts still carry params_version_hash e716cd12dddc somewhere in results provenance
```

### Implementer report / Reviewer findings / Resolution

- Implementer — SHA / files / dataset_id + moment sources / ranking-hold summary / deviations / self-check (A5.1–A5.5): `…`
- Reviewer — per-criterion verdict / issues / **Status**: `…`
- Resolution (on redo): `…`

---

## Whole-plan definition of done (reviewer confirms after A5)

- [ ] A1 coverage ≈ 0.95 where gp_ard was 0.20/0.32/0.44; `projection_reliability.pdf` shows the fix; `gp_ard` retained.
- [ ] A2 a covariate/EB candidate beats `pooled_bayes` on the small band (bootstrap CI on Δ excludes 0); `infer_day_of_week` shipped; "ties pooled" puzzle resolved + documented.
- [ ] A3 all tracks at ≥200 seeds with bootstrap CIs on Δ, recorded held-out partition, Holm/BH-corrected flags.
- [ ] A4 new candidates per track (ruptures/CP-SAT as upper bounds); CUSUM Pareto frontier; scheduling prereq-order back to 1.0 on the dipping mix; sweep widened + adversarial + flip map + per-archetype worst case.
- [ ] A5 reality-matched regime (new `dataset_id`) fitted to real engagement *moments* as bounds; contest re-run + ranking-hold reported; frozen `e716cd12dddc` preserved.
- [ ] `PA+.1–PA+.8` ticked in `college/scope/research-tasklist.md`; open-code-question findings recorded with file:line evidence.
- [ ] Zero changes outside the plan's Files-touched index; no KT-bench / Pillar-B effort spent here (§0).

## Reviewer log (per round)

| Date | Phase | SHA reviewed | Verdict | Note |
|---|---|---|---|---|
| _add per review_ | | | | |
