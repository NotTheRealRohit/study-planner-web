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
last_updated: "2026-06-30 10:41 IST — Codex"
---

# Scratchpad

> Relationship to the other docs (do not blur): **PLAN.md** is the spec you follow.
> **VERIFICATION.md** is the formal gate (Developer notes you fill + Reviewer sign-off).
> **This file** is your running brain: every decision, number, deviation, blocker, and the immediate
> next step — enough that a fresh session (or the reviewer) can resume with zero extra context.

## 1. Current status (one-liner + phase board)
- **Now:** P0 baseline evidence is implemented and awaiting reviewer sign-off.
- **Branch / latest phase evidence commit:** `project/phase-1` @ `5a3eec91bdb05de177428f597543869c113d110f`
- **Phase board:** P0 🟡 · R1 ☐ · R2 ☐ · R3 ☐ · R4 ☐ · R5 ☐ · R6 ☐

## 2. Next actions (the immediate queue — keep this current)
1. Reviewer to inspect P0 evidence in `VERIFICATION.md` and either flip P0 🟡→✅ or return findings.
2. After P0 reviewer sign-off, start R1 by verifying the generator anchors against live code before editing.
3. R1 first edits: author `college/scope/decoupled-session-preregistration.md`, add decoupled params/hash, and add generator tests before production code.

## 3. Environment / run notes
- What runs in this sandbox vs authored-only (record the arm64/dep status the first time you hit it): the full research comparison pytest suite runs with escalated permissions for uv cache access; baseline result is `92 passed, 2 failed`.
- Exact commands that worked (copy the ones that ran clean):
  - `uv run --package research-comparison pytest research/comparison/tests -q` (required escalation because sandbox cannot open `/Users/rsaji/.cache/uv`; completed with 2 failing closed-loop tests).
  - `jq` extraction commands over `research/results/{calibration,detection,projection}/*_results.json`.
- New decoupled dataset id once generated: `synthetic-decoupled-<hash>-seed0-n<count>` → `<path>`

## 4. Decisions made during execution (continue PLAN §2's D-xx numbering)
> Record every choice you make that the PLAN left open or that deviates from it, with the why.
- **D-08 — OQ-4 parity source = the on-disk projection result, even though it is reality n3600 not frozen n5400.** `research/results/projection/projection_results.json` currently stamps `dataset_id=synthetic-reality-3b404c903563-seed0-n3600`, `seed_count=200`, `bands=small,medium,max`, `n_learners=3600`, `scored_split=held_out`, 6 archetypes (`3 train + 3 held_out`). PLAN D-05 explicitly says parity means matching the current on-disk A-series projection result if it differs from the expected n5400 lineage. — *why:* no fabrication; current stamped JSON is the authoritative P0 evidence. — *date:* 2026-06-30
- (OQ resolutions go here too: OQ-1 partial inclusion policy, OQ-2 cadence params, OQ-3 COLD_START_N +
  interval recipe, OQ-4 A-series parity config.)

## 5. Results ledger (numbers as they land — the stuff the reviewer + dissertation cite)
> Paste the real headline numbers from the stamped result JSONs. No rounding-to-make-it-look-good.
- **P0 baseline (current on-disk stamped results, reality lineage not frozen):** provenance for calibration/detection/projection is `dataset_id=synthetic-reality-3b404c903563-seed0-n3600`, `seed_count=200`, `bands=small,medium,max`, `n_learners=3600`, `scored_split=held_out`, `generator_version=0.1.0`, `params_version_hash=3b404c903563`. Calibration candidate set is legacy only (`covariate_bayes, eb_partial_pool, ewma, hierarchical_bayes, kalman, oracle_calibration, pooled_bayes, sma`); no `enriched_shrink`/`dual_prior` in the P0 JSON. m_global winners by band are all `oracle_calibration`; non-oracle `hierarchical_bayes` MAE = max `0.1529828211272382`, medium `0.11212833534127313`, small `0.11001981825580294`. Context-pred Holm survivors vs `hierarchical_bayes`: `ewma`, `sma`, and `oracle_calibration`; recovery-mae Holm survivor: `oracle_calibration` only. Detection robust-null baseline: `cusum` wins both shift types; drift latency `4.13731380394727`, false alarm `0.18408558783043402`, missed `168.0`; step latency `2.5582565598190596`, false alarm `0.20726369989319746`, missed `285.0`; no non-oracle detector has `survives_holm_win=true`. Projection gp_ard baseline by band: max coverage `0.13083333333333333`, MAE `30.236875`, sharpness `9.068541666666667`; medium coverage `0.2674206349206349`, MAE `13.002420634920634`, sharpness `8.738333333333333`; small coverage `0.31152777777777774`, MAE `6.320277777777777`, sharpness `7.710277777777779`. Projection Holm survivors vs `gp_ard`: `conformal` 9 cells, `gp_hetero_t` 9 cells, `kalman` 3 cells, `linear` 3 cells, `oracle_projection` 9 cells; oracle remains an upper bound only.
- **R2 calibration (decoupled):** enriched_shrink / dual_prior held-out Holm verdict = …
- **R3 detection (decoupled):** robust-null holds? = … (deviations: …)
- **R4 ETA (decoupled) — HEADLINE:** per band, gp_ard vs analytic_required_rate vs gp_plus_analytic
  (coverage / MAE-days / sharpness); **paired-Holm vs gp_ard survives?** = … ; cold-start (R4a) = … ;
  reference-line (R4b) = done/deferred.
- **R6 N=1:** partial-throughput in-family? = … ; ETA-on-real descriptive error = …

## 6. Deviations from PLAN (what + why + reviewer-flagged?)
- P0 baseline provenance differs from the PLAN's expected frozen `synthetic-21c2cdabfa91-seed0-n5400` / 9-archetype target: the only on-disk projection result is `synthetic-reality-3b404c903563-seed0-n3600` / 6 archetypes. Logged as D-08 and flagged for reviewer.
- The on-disk calibration baseline does not contain `enriched_shrink` or `dual_prior`; R2 may need either a regenerated baseline or an honest comparison against the available P0 baseline plus the decoupled run.

## 7. Blockers / open risks
- P0 cannot be reviewer-✅ until the reviewer accepts the current on-disk-result parity target or asks for a regenerated A-series baseline.
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
