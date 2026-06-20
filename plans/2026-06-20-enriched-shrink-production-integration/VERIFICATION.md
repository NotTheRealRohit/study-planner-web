# VERIFICATION — enriched_shrink production integration (py_progress → FastAPI → UI)

Companion to [`PLAN.md`](./PLAN.md). This is the **review round-trip** artifact for the build → test → review loop.

**How this file is used (each phase):**

1. **Cowork** pre-fills *Acceptance criteria* (below) from the plan. *(done — checkboxes start unchecked.)*
2. **Codex/Sonnet** fills *Implementer report* after building the phase: files changed, commit SHA, what was done, deviations + why, and a self-check against each criterion. Then **STOP for review**.
3. **Cowork** fills *Reviewer findings*: read the committed diff at the reported SHA (`git show <sha>`) and any `evidence.json`/`SUMMARY.md`; give a per-criterion verdict + required changes; set status `✅ Verified` or `🔁 Changes requested`.
4. **Codex** fills *Resolution* on redo. Loop until `✅ Verified`.

**Step 0 (before any code):** commit these planning docs verbatim — `docs(plan): add enriched-shrink-production-integration plan + verification`. Cowork cannot commit (it bricks `.git` locks in the sandbox); the native side establishes the baseline so later diffs are meaningful. If a reviewer leaves edits in this file, the next Step 0 commits the review before acting on it.

**Global rules every phase is also checked against:**
- Phase 0 (research) follows the brief's research rules: no generator-truth import in `baselines/`; observable next-context only in `predict_next`; prior weights / temperature tuned on **held-out-TRAIN** archetypes only and recorded in provenance; only Holm-surviving held-out wins count; emit `ProgressLogger` + `run_with_heartbeat`.
- Phases 1–3 (production): the `CalibrationState` contract stays backward-compatible (`nextSessionForecast` additive + optional); CUSUM / GP projection / scheduling untouched (PLAN D-03); the TS `computeCalibration` implementation is **not** changed (PLAN D-01); no secrets committed.

---

## Phase 0 — Validate the dual-prior weighting in the research harness (go/no-go)

### Acceptance criteria (Cowork pre-filled)

- [ ] `DualPriorWeightedCalibrator` added to `baselines/calibration.py`; composes two `EnrichedShrinkageCalibrator` members (reality + frozen prior); `_weights` returns the reality-favoured static fallback (`≈[0.6,0.4]`) when <2 active sessions; **no generator-truth import**.
- [ ] Candidate registered in `runners/calibration.py` with both regimes' TRAIN-fit priors; a `dual_prior_audit` block (both vectors + static weights + per-band weight summary) emitted next to `population_prior`.
- [ ] Scored on **reality** under the rigour protocol (200 seeds, held-out archetypes, Holm), reference baseline = `enriched_shrink` (reality-alone); `evidence.json` + `SUMMARY.md` written to `research/doc/verification-runs/2026-06-20-enriched-dualprior/`.
- [ ] **GO/NO-GO recorded:** GO iff `enriched_dual_prior` is a Holm-surviving win over `enriched_shrink` on `context_pred_mae` (reality); else NO-GO → production ships reality-alone (note added to PLAN D-02 in the same commit).
- [ ] `test_calibration_track.py` updated (candidate present + cold-start fallback weights); `uv run --package research-comparison pytest research/comparison/tests -q` passes.
- [ ] Zero changes outside `research/`.

### Implementer report (Codex/Sonnet fills)

_Files changed:_ `research/comparison/src/research_comparison/baselines/calibration.py`;
`research/comparison/src/research_comparison/runners/calibration.py`;
`research/comparison/tests/test_calibration_track.py`;
`research/doc/verification-runs/2026-06-20-enriched-dualprior/evidence.json`;
`research/doc/verification-runs/2026-06-20-enriched-dualprior/SUMMARY.md`.

_Commit SHA:_ `bd9eafafc33ec399ee8fec5f49ad7d0b982b3498`.

_What was done:_ Added `DualPriorWeightedCalibrator` to the research calibration
baselines, registered it in the calibration runner, and emitted
`dual_prior_audit` with the reality/frozen TRAIN-fit prior vectors, static
weights, and per-band weight summaries. Updated calibration tests for candidate
registration, cold-start fallback weights, scored runner output, and the audit
block. Ran the plan-required 200-seed reality calibration harness and captured
`evidence.json` plus `SUMMARY.md`.

_Deviations + why:_ The first prereq test run failed before Phase 0 because two
existing detector-sim entrypoints used a local `Progress` class name that the
repo-wide progress-logging gate did not recognize; fixed and committed that
separately as `acee4e9` before starting Phase 0. The runner resolves the
counterpart frozen/reality prior from the canonical 200-seed reference datasets
when the canonical datasets are scored; non-canonical test fixtures fall back to
the current dataset prior so tests stay hermetic.

_GO / NO-GO:_ **GO by the plan's stated criterion.** In `SUMMARY.md`, reference
baseline `enriched_shrink` / `context_pred_mae` on reality reports
`enriched_dual_prior` as a Holm-surviving winner in 7 cells. Held-out means:
max `0.137036` vs `0.138436`, medium `0.138572` vs `0.139730`, small
`0.143258` vs `0.142129`. Caveat: the result is mixed; the same reference block
also reports 2 Holm-significant not-win cells for `enriched_dual_prior` in
small-band archetypes.

_Self-check vs criteria:_ `DualPriorWeightedCalibrator` composes reality/frozen
`EnrichedShrinkageCalibrator` members and returns `[0.6, 0.4]` for cold-start
histories; no generator-truth imports or fields are used in `baselines/`.
Runner output includes `dual_prior_audit` with both prior vectors, static
weights, and per-band summaries. Evidence was scored on
`synthetic-reality-c545404bcacf-seed0-n5400` with 200 seeds, held-out
archetypes, Holm correction, and reference baseline `enriched_shrink`. Tests:
`uv run --package research-comparison pytest research/comparison/tests -q`
passed (`94 passed`). Implementation/evidence changes in the phase commit are
under `research/`; this follow-up docs commit records the SHA and GO result.

### Reviewer findings (Cowork fills)

_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 1 — Promote the enriched calibrator into `py_progress`

### Acceptance criteria (Cowork pre-filled)

- [ ] `packages/py-progress/src/py_progress/enriched.py` created; `EnrichedShrinkageCalibrator` (+ required helpers, `EnrichedShrinkageFit`, `ENRICHED_FEATURE_NAMES`, `_safe_log`, `_posterior_interval`) lifted **verbatim except the import line** from research baselines; archetype/fingerprint code and unused imports **not** copied.
- [ ] `REALITY_POPULATION_PRIOR` + `FROZEN_POPULATION_PRIOR` constants present with the exact evidence.json vectors and a provenance comment; `PRODUCTION_PRIOR_STRATEGY` matches Phase 0's GO/NO-GO; `production_calibrator()` returns dual-prior (GO) or reality-alone (NO-GO).
- [ ] Symbols exported from `py_progress/__init__.py` (`__all__` updated).
- [ ] `test_enriched.py` added: empty → `≈BAYESIAN_PRIOR_MEAN`; deterministic finite positive `predict_next` with `planned_horizon`; **parity** with the research class (within 1e-9) on a fixed fixture; (GO only) cold-start weights `≈[0.6,0.4]`.
- [ ] `uv run --package py-progress pytest packages/py-progress/tests -q` passes; **`compute_calibration` unchanged this phase** (production behaviour identical).

### Implementer report (Codex/Sonnet fills)

_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)

_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 2 — Wire enriched pace + `nextSessionForecast` through `compute_calibration` and the FastAPI endpoint

### Acceptance criteria (Cowork pre-filled)

- [ ] `CalibrationState` gains `nextSessionForecast: float | None = None` (Python dataclass, last field); TS `types.ts` gains `nextSessionForecast?: number | null`; pydantic `CalibrationStatePayload` gains `nextSessionForecast`.
- [ ] `compute_calibration` keeps the hierarchical + CUSUM + trend pipeline; `globalMultiplier`/`globalPosterior.mean` now come from `production_calibrator().fit_global`; `nextSessionForecast` = `predict_next(visible, next_context)` when `next_context` is supplied, else `None`. `roleMultipliers`/`promptNeeded`/`insights`/`trend` unchanged in source.
- [ ] `CalibrationRequest` gains optional `nextContext` (with `planned_horizon{deadline, planned_total_sessions}` + role/date/session_index); router passes it through.
- [ ] `test_v1_integration.py` updated (inline payloads, no missing fixtures): `globalMultiplier` equals the enriched pace; `nextSessionForecast` non-null with `nextContext` and null without; `/v1/progress` + `/v1/roadmap/*` still pass.
- [ ] `uv run --package intelligence pytest services/intelligence/tests -q` and `uv run --package py-progress pytest packages/py-progress/tests -q` pass; TS `computeCalibration` implementation untouched (D-01).

### Implementer report (Codex/Sonnet fills)

_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)

_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 3 — Switch the app's `useCalibrationState` to call the FastAPI service

### Acceptance criteria (Cowork pre-filled)

- [ ] `apps/app/src/lib/intelligenceClient.ts` created; reads `import.meta.env.VITE_INTELLIGENCE_URL` (default `http://localhost:8000`); `postCalibration` throws on non-2xx.
- [ ] `useCalibration.ts` builds the request from mapped events + derives `nextContext` (deadline + `planned_total_sessions = slots.length` + up-next slot via the same logic as `ProgressEngine.getUpNextSlot`); POSTs to the service; returns `CalibrationState` on success and `null` while loading / on error (so `Home`/`Week` null-guards hold). TS `computeCalibration` no longer imported by the app.
- [ ] `VITE_INTELLIGENCE_URL` documented in `apps/app/.env.example`.
- [ ] `useCalibration.test.ts` added (request carries `planned_horizon`; success maps state; rejection → null), using the Dexie test setup; `pnpm --filter app test` + `pnpm --filter app typecheck` pass.
- [ ] Playwright spec for the Home pace/forecast path is **written** (mocked `/v1/calibration`) but **not run** (per `CLAUDE.md` E2E constraint).

### Implementer report (Codex/Sonnet fills)

_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)

_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Sign-off

- [ ] All four phases `✅ Verified`.
- [ ] MASTER_TRACKER §4 + §8 rows reflect production integration state; `last_updated` bumped.
- [ ] OQ-01 (projection wiring), OQ-02 (offline caching), OQ-03 (prod auth/deploy) carried forward or resolved.
