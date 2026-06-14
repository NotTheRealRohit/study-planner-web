# KT bench — credibility tracker (living record)

> **What this is.** A single, always-current record of which KT `(model, dataset)` cells are
> trustworthy. The implementing agent **updates this file as it works** — flipping gate boxes,
> pasting evidence, setting cell status. Anyone (human or a fresh agent) can read this file alone to
> know exactly what has been accomplished and what is still smoke/degenerate.
>
> **The bar for each gate is defined in** [`2026-06-14-kt-credibility-and-validation-guidelines.md`](2026-06-14-kt-credibility-and-validation-guidelines.md).
> A cell is `✅ credible` **only when G1–G8 all pass**.
>
> **Location note:** this tracker lives in `research/doc/` (tracked by git). The results it describes
> live in `research/results/kt/` (gitignored), so this file is the durable, committable record of
> what those results actually are.

## How to update this tracker

1. After running/changing a cell, set each gate box: `✅` pass · `❌` fail · `⏳` not yet run · `⚠️` needs investigation.
2. Paste the evidence into the cell's row (per-fold AUC mean±std, ECE, cold-start, `epochs`/`smoke`, `n_pred`).
3. Set the **cell status**: `✅ credible` · `🟡 partial` · `❌ smoke/degenerate` · `🛑 blocked: <reason>` · `⏳ not started`.
4. Add a line to the **Changelog** with date + commit sha.
5. Commit this file together with the code/results change it describes.

## Status legend

`✅` pass/credible · `❌` fail/not-credible · `⚠️` investigate · `⏳` pending · `🛑` blocked · `n/a` not applicable

## Gate key (full definitions in the guideline)

| Gate | One-line check |
|---|---|
| **G1** | provenance `public_raw` + folds/sequences hash match |
| **G2** | full depth: `smoke==0`, `epochs>=5`, `n_pred` ≈ real test size (not 64) |
| **G3** | all 5 folds × {full,3,5,10,20} + ECE present; 0 gaps |
| **G4** | mean AUC ≥ 0.55 & reliably > chance; not the flat-0.51 degenerate signature |
| **G5** | ECE on real preds, 10 bins; ≤ 0.15 good, > 0.25 investigate |
| **G6** | cold-start AUC(k) monotone-ish, every k > 0.5 |
| **G7** | seed+config recorded; re-run reproduces AUC ±0.01 |
| **G8** | no silent model alias; pyBKT KC space sane (atomic, not `_`-joined) |

---

## Cell matrix — current state (audited 2026-06-14 @ `d04057b`; S1 relabel updated in current worktree)

| # | Model | Dataset | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | Status | Evidence (full-seq AUC / ECE / depth) |
|---|---|---|----|----|----|----|----|----|----|----|--------|----------------------------------------|
| 1 | dkt | nips2020 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ credible | AUC 0.743 (folds .758/.732/.748/.733/.743); ECE 0.037; epochs 5, smoke 0, n_pred ~1.5k/fold; cold-start .71→.71→.75→.74. G7 rerun into `/private/tmp/kt-g7-dkt-nips2020/results` reproduced full-seq fold AUCs exactly (mean Δ=0.000000; max fold Δ=0.000000). |
| 2 | akt | nips2020 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ credible | AUC .768/.756/.755/.756/.780 (mean .7629, std .0097, 95% lower .754); ECE mean .0359; epochs 5, smoke 0, n_pred 1503/1537/1481/1497/1528; cold-start means k3=.753, k5=.738, k10=.779, k20=.789. G7 rerun into `/private/tmp/kt-g7-nips-deep/results` reproduced full-seq fold AUCs exactly (mean Δ=0.000000; max fold Δ=0.000000). |
| 3 | deep_irt | nips2020 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ credible | AUC .758/.717/.735/.730/.731 (mean .7341, std .0132, 95% lower .723); ECE mean .0382; epochs 5, smoke 0, n_pred 1503/1537/1481/1497/1528; cold-start means k3=.662, k5=.691, k10=.726, k20=.711. G7 rerun into `/private/tmp/kt-g7-nips-deep/results` reproduced full-seq fold AUCs exactly (mean Δ=0.000000; max fold Δ=0.000000). |
| 4 | sakt | nips2020 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ credible | AUC .730/.703/.715/.715/.714 (mean .7154, std .0085, 95% lower .708); ECE mean .0355; epochs 5, smoke 0, n_pred 1503/1537/1481/1497/1528; cold-start means k3=.668, k5=.701, k10=.731, k20=.716. G7 rerun into `/private/tmp/kt-g7-nips-deep/results` reproduced full-seq fold AUCs exactly (mean Δ=0.000000; max fold Δ=0.000000). |
| 5 | dkt_clst_config | nips2020 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ credible: relabeled config | AUC .759/.732/.748/.733/.743 (mean .7429, std .0100, 95% lower .734); ECE mean .0370; epochs 5, smoke 0, n_pred 1503/1537/1481/1497/1528; cold-start means k3=.707, k5=.714, k10=.752, k20=.741. G7 rerun into `/private/tmp/kt-g7-nips-deep/results` reproduced full-seq fold AUCs exactly (mean Δ=0.000000; max fold Δ=0.000000). This is DKT-backed `dkt_clst_config`, not a distinct CLST method. |
| 6 | pybkt | nips2020 | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ⏳ | ⚠️ | 🛑 blocked: zero-mass pyBKT predictions | AUC 0.508–0.509 flat (mean 0.5087, std 0.0004) on ~224k preds/fold; ECE 0.485. S2/S4 audit found active artifacts hash-match a sane sidecar (57 skills, no `_` keys, no singleton skills) and every test-fold skill is present in train. Degeneration comes from trained pyBKT output: ~90% exact-zero `correct_predictions` on NIPS, not unseen-skill fallback. Exclude unless the pyBKT formulation/runner is changed and rerun. |
| 7 | dkt | accoding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 partial: pending S6 subsample stability | Full-depth rerun 2026-06-14: AUC .695/.672/.749/.723/.722 (mean .7122); ECE mean .0547; epochs 5, smoke 0, n_pred 575/575/634/604/620; cold-start means k3=.700, k5=.705, k10=.693, k20=.668; G7 scratch rerun reproduced all folds exactly (max Δ=0.000000). Not creditable until ACcoding S6 stability passes. |
| 8 | akt | accoding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 partial: pending S6 subsample stability | Full-depth rerun 2026-06-14: AUC .690/.678/.753/.722/.748 (mean .7183); ECE mean .0494; epochs 5, smoke 0, n_pred 575/575/634/604/620; cold-start means k3=.694, k5=.696, k10=.679, k20=.676; G7 scratch rerun reproduced all folds exactly (max Δ=0.000000). Not creditable until ACcoding S6 stability passes. |
| 9 | deep_irt | accoding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 partial: pending S6 subsample stability | Full-depth rerun 2026-06-14: AUC .649/.609/.630/.665/.618 (mean .6344); ECE mean .0422; epochs 5, smoke 0, n_pred 575/575/634/604/620; cold-start means k3=.603, k5=.610, k10=.589, k20=.644; G7 scratch rerun reproduced all folds exactly (max Δ=0.000000). Not creditable until ACcoding S6 stability passes. |
| 10 | sakt | accoding | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ not credible (genuine G6 cold-start failure) | Full-depth rerun 2026-06-14: AUC .612/.593/.676/.659/.663 (mean .6407); ECE mean .0402; epochs 5, smoke 0, n_pred 575/575/634/604/620; cold-start means k3=.635, k5=.631, k10=.612, k20=.545, with k20 below chance on folds 1 (.470) and 3 (.486); G7 scratch rerun reproduced all folds exactly (max Δ=0.000000). |
| 11 | dkt_clst_config | accoding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🟡 partial: pending S6 subsample stability | Full-depth rerun 2026-06-14: AUC .694/.670/.750/.721/.722 (mean .7115); ECE mean .0546; epochs 5, smoke 0, n_pred 575/575/634/604/620; cold-start means k3=.700, k5=.705, k10=.694, k20=.667; G7 scratch rerun reproduced all folds exactly (max Δ=0.000000). Explicit DKT-backed relabel, not a distinct CLST claim; not creditable until ACcoding S6 stability passes. |
| 12 | pybkt | accoding | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ⏳ | ✅ | 🟡 partial | AUC 0.606 (folds .608/.601/.608/.611/.604), n_pred matches test sidecar exactly; ECE 0.272 (>0.25 investigation threshold), 10/10 bins populated; cold-start means k3=.659, k5=.663, k10=.655, k20=.654; problem-id KC space sane (3,817 skills, no `_` keys). Active sample is `max_learners=3000` only, so OQ-K2 stability still pending. |

**Snapshot tally:** 5 fully credible NIPS cells · 5 partial ACcoding cells pending S6 or calibration/stability · 1 genuine not-credible ACcoding cell (`sakt`, G6 cold-start failure) · 1 blocked pyBKT/NIPS cell. Reportable allow-list = **DKT, AKT, Deep-IRT, SAKT, and DKT-compatible CLST config × nips2020**. Generated KT report artifacts cite only these green NIPS cells; the relabeled config is not a distinct CLST method claim.

---

## Cross-cutting gates (apply once, not per cell)

| Item | Status | Evidence / note |
|---|---|---|
| Folds flipped to `public_raw` | ✅ | nips2020 (3,935 seqs), accoding (1,944 seqs); poj retired as smoke (D-18) |
| `kt_summary.json` gaps == 0 | ✅ | Regenerated in `reportable_allowlist` mode after G7: `gaps=[]`, `result_count=150`, allow-list = five green NIPS cells. Full-grid gaps are still expected until the non-credible Accoding cells are rerun or blocked. |
| `kt_summary` raw_sources == `[public_raw]` | ✅ | `research/results/kt_summary.json` reports `folds_raw_sources=["public_raw"]` for the reportable allow-list. |
| Report artifacts regenerated | ✅ | `kt_auc.tex`, `kt_ece.tex`, `kt_coldstart.pdf`, `kt_reliability.pdf`, `kt_provenance.txt` regenerated from the credible allow-list only. Tables now cite only the five green NIPS cells; smoke/blocked/partial Accoding cells are excluded. |
| `kt_provenance.txt` no longer says `smoke_fixture` | ✅ | "Fold raw sources: public_raw." |
| Guard tests added (5, see guideline) | ✅ | `test_kt_join.py` now covers reportable allow-list provenance/hash, G2 `test_no_smoke_in_reportable`, G7 seed/config metadata for pyKT and future pyBKT reportable cells, AUC floor/degenerate band, cold-start sanity, model registry/no silent aliases, pyBKT skill-space policy, Accoding sampling provenance, and reportable-only artifact generation. `test_progress_logging.py` guards visible Python entrypoints against missing progress logs. Verified: `uv run --package research-comparison pytest research/comparison/tests/test_kt_join.py -q` → 18 passed; full `uv run --package research-comparison pytest research/comparison/tests -q` → 51 passed. |
| Reportable allow-list | ✅ | `research/kt-bench/model_registry.json` lists only the five G1–G8-green NIPS cells as `credible`: `dkt`, `akt`, `deep_irt`, `sakt`, and `dkt_clst_config`. Do not add any Accoding cell until its G1–G8 row is green. |
| Raw public archives restored and usable | ✅ | `research/datasets/NeurIPS 2020.zip` and `research/datasets/ACcoding.zip` are present and not gitignored. NIPS zip contains the required train/metadata members; `preprocess.py` can fill missing NIPS landing files from the zip without overwriting existing files. `accoding_to_poj.py` now discovers root-level `ACcoding.zip` by default and still supports the old nested path; verified a 1,000-row adapter smoke into `/private/tmp/study-planner-web/kt-verify/poj_log.csv` (`87/1000` kept rows). |
| ACcoding `max_learners` subsample recorded | ✅ | `research/kt-bench/data/poj/poj_log.provenance.json`: `max_learners=3000`, seed `20260614`, `max_rows=0`, kept 445,837 rows across 2,523 learners from 4,046,652 submissions. This records the active sample only; S6 stability still requires ≥2 `max_learners` reruns. |

---

## Step checklist — getting all cells to credible (R4 acceptance)

> Order: fixes first (so the re-run produces credible numbers), then the full grid, then regenerate + gate.

- [x] **S1 — CLST fidelity (G8).** Relabeled the silent `clst` alias to `dkt_clst_config`, added `research/kt-bench/model_registry.json`, and added the clean-env model-registry/reportable-allow-list guard. True distinct CLST implementation is deferred to a later research plan.
- [x] **S2 — pyBKT KC keying audit (G8/G4).** Current active `pybkt × nips2020` artifacts hash-match `folds/nips2020_sequences.csv`, which has 57 numeric skills, no `_` compound keys, no singleton skills, and min skill count 21. The old compound-keying explanation is not supported by current evidence. Cell 6 remains ❌ under G4/G5; investigate pyBKT fit/prediction behavior before crediting.
- [x] **S3 — Full-depth deep re-run (G2).** NIPS side is full-depth and G7-verified for `akt,deep_irt,sakt,dkt_clst_config`; together with already-credible `dkt`, all five NIPS pyKT cells are reportable. ACcoding `dkt,akt,deep_irt,sakt,dkt_clst_config` full-depth train/coldstart/calibrate completed on 2026-06-14: all five pass G2/G4/G5/G7, four pass G6, and `sakt × accoding` is a genuine G6 cold-start failure. ACcoding cells remain non-reportable until S6 subsample stability is resolved.
- [ ] **S4 — pyBKT real fit on shared folds (G2/G4).** Cell 6 (`pybkt × nips2020`) is blocked/excluded on current evidence: fit artifacts use sane shared folds but trained pyBKT outputs ~90% exact-zero scores and remains flat at chance. Cell 12 (`pybkt × accoding`) passes G4/G6/G8 on current artifacts but fails G5 calibration (`ECE≈0.272`) and still needs S6 subsample stability.
- [x] **S5 — Guard tests (auto gates).** Added clean-env guards for the reportable allow-list: G2 `test_no_smoke_in_reportable`, public provenance + matching folds hash, G7 seed/config metadata, AUC floor/degenerate band, cold-start sanity, model registry/no silent aliases, pyBKT skill-space policy, Accoding sampling provenance, and reportable-only artifact generation. Verified 18 passing tests.
- [ ] **S6 — ACcoding subsample stability (OQ-K2).** Current active Accoding artifacts use a single deterministic `max_learners=3000` sample. The raw ACcoding zip is restored and adapter-readable, so the stability work is unblocked; re-run accoding cells at ≥2 `max_learners` values, confirm AUC stable, and record before any Accoding cell is creditable.
- [x] **S7 — Re-join + regenerate report.** `join.py` now writes reportable-only artifacts by default from the credible registry allow-list. Regenerated `kt_*` artifacts and `kt_summary.json`; confirmed `gaps=[]`, `folds_raw_sources=["public_raw"]`, and tables cite only the five green NIPS cells.
- [x] **S8 — Update this tracker + tracker allow-list.** Current reached cells are updated: five NIPS pyKT cells are credible, `pybkt × nips2020` is blocked, `pybkt × accoding` remains partial, Accoding pyKT cells remain non-reportable, and the reportable allow-list is exactly the green NIPS set.
- [ ] **S9 — Flip tracker in `research-tasklist.md`** Phase 4 → "✅ complete (real public-benchmark numbers, all cells credible)" once S1–S8 are genuinely done. Interim state has been reconciled there as partial: real data wired, five NIPS pyKT cells are currently reportable, and Accoding/pyBKT cells remain unresolved.

---

## Per-cell evidence log (paste raw numbers here as cells are re-run)

> Template — copy a block per cell when you re-run it.

```
### <model> × <dataset>  — re-run <date> @ <sha>
depth:        epochs=__  smoke=__  n_pred/fold=[__,__,__,__,__]
full-seq AUC: folds=[__,__,__,__,__]  mean=__  std=__
ECE:          mean=__  (bins ok? __)
cold-start:   k3=__ k5=__ k10=__ k20=__  monotone-ish? __
reproduce:    seed=__  rerun_AUC=__  (Δ vs first __)
gates:        G1__ G2__ G3__ G4__ G5__ G6__ G7__ G8__
status:       <✅ credible | 🟡 partial | ❌ ... | 🛑 ...>
notes:        __
```

### pybkt × accoding — audit 2026-06-14 @ current worktree

depth:        pyBKT full shared folds; n_pred/fold=[64899,64857,76648,73235,76741]
full-seq AUC: folds=[.608155,.600790,.607649,.610874,.603661]  mean=.606226  std=.003563
ECE:          mean=.271600  std=.007403  (10/10 bins populated on every fold; fails G5 threshold)
cold-start:   k3=.659013 k5=.662772 k10=.654777 k20=.653810  monotone-ish? yes; all > .50
sampling:     adapter provenance records `max_learners=3000`, seed `20260614`, kept 445,837 rows / 2,523 learners
skill space:  356,380 sidecar rows; 1,944 fold users; 3,817 problem-id skills; 0 `_` keys; 156 singleton skills allowed by registry
gates:        G1✅ G2✅ G3✅ G4✅ G5❌ G6✅ G7⏳ G8✅
status:       🟡 partial — not creditable until calibration is addressed or justified, G7 rerun passes, and S6 stability exists

### dkt × accoding — T1 full-depth rerun 2026-06-14 @ current worktree

depth:        epochs=5  smoke=0  n_pred/fold=[575,575,634,604,620]
full-seq AUC: folds=[.694896,.671647,.749390,.723179,.722114]  mean=.712245  std=.026631
ECE:          mean=.054673  (10-bin ECE rows written for all folds)
cold-start:   k3=.699654 k5=.704898 k10=.693129 k20=.668136  monotone-ish? yes by guard rule; all folds/k > .50
reproduce:    seed=20260613  scratch=`research/kt-bench/.work/g7-accoding-dkt/results`  max fold Δ=0.000000
gates:        G1✅ G2✅ G3✅ G4✅ G5✅ G6✅ G7✅ G8✅
status:       🟡 partial — G1-G8 pass, but not creditable until S6 subsample stability exists

### akt × accoding — T1 full-depth rerun 2026-06-14 @ current worktree

depth:        epochs=5  smoke=0  n_pred/fold=[575,575,634,604,620]
full-seq AUC: folds=[.690384,.678042,.752716,.722103,.748414]  mean=.718332  std=.030019
ECE:          mean=.049386  (10-bin ECE rows written for all folds)
cold-start:   k3=.693917 k5=.695992 k10=.678787 k20=.675839  monotone-ish? yes by guard rule; all folds/k > .50
reproduce:    seed=20260613  scratch=`research/kt-bench/.work/g7-accoding-deep/results`  max fold Δ=0.000000
gates:        G1✅ G2✅ G3✅ G4✅ G5✅ G6✅ G7✅ G8✅
status:       🟡 partial — G1-G8 pass, but not creditable until S6 subsample stability exists

### deep_irt × accoding — T1 full-depth rerun 2026-06-14 @ current worktree

depth:        epochs=5  smoke=0  n_pred/fold=[575,575,634,604,620]
full-seq AUC: folds=[.649452,.608992,.630177,.664881,.618292]  mean=.634359  std=.020389
ECE:          mean=.042229  (10-bin ECE rows written for all folds)
cold-start:   k3=.602919 k5=.610021 k10=.589152 k20=.643616  monotone-ish? yes by guard rule; all folds/k > .50
reproduce:    seed=20260613  scratch=`research/kt-bench/.work/g7-accoding-deep/results`  max fold Δ=0.000000
gates:        G1✅ G2✅ G3✅ G4✅ G5✅ G6✅ G7✅ G8✅
status:       🟡 partial — G1-G8 pass, but not creditable until S6 subsample stability exists

### sakt × accoding — T1 full-depth rerun 2026-06-14 @ current worktree

depth:        epochs=5  smoke=0  n_pred/fold=[575,575,634,604,620]
full-seq AUC: folds=[.612388,.593357,.676042,.659070,.662696]  mean=.640711  std=.031979
ECE:          mean=.040192  (10-bin ECE rows written for all folds)
cold-start:   k3=.635444 k5=.630843 k10=.611546 k20=.544611  monotone-ish? no; k20 folds 1=.470323 and 3=.486230 are below chance
reproduce:    seed=20260613  scratch=`research/kt-bench/.work/g7-accoding-deep/results`  max fold Δ=0.000000
gates:        G1✅ G2✅ G3✅ G4✅ G5✅ G6❌ G7✅ G8✅
status:       ❌ not credible (genuine full-depth G6 cold-start failure)

### dkt_clst_config × accoding — T1 full-depth rerun 2026-06-14 @ current worktree

depth:        epochs=5  smoke=0  n_pred/fold=[575,575,634,604,620]
full-seq AUC: folds=[.693850,.670446,.749728,.721197,.722286]  mean=.711501  std=.027088
ECE:          mean=.054610  (10-bin ECE rows written for all folds)
cold-start:   k3=.699557 k5=.704623 k10=.693551 k20=.666821  monotone-ish? yes by guard rule; all folds/k > .50
reproduce:    seed=20260613  scratch=`research/kt-bench/.work/g7-accoding-deep/results`  max fold Δ=0.000000
gates:        G1✅ G2✅ G3✅ G4✅ G5✅ G6✅ G7✅ G8✅
status:       🟡 partial — explicit DKT-backed relabel; G1-G8 pass, but not creditable until S6 subsample stability exists

---

## Changelog

| Date | Commit | Change |
|---|---|---|
| 2026-06-14 | `d04057b` | Initial audit snapshot recorded. 1/12 credible (DKT×nips2020). Smoke-depth on 9 cells, pyBKT degenerate (nips2020), CLST alias. Tracker created. |
| 2026-06-14 | current worktree | S1 relabel path selected: `clst` retired, `dkt_clst_config` added with model registry + reportable allow-list guard. DKT×nips2020 downgraded to partial until G7 rerun proves reproducibility. |
| 2026-06-14 | current worktree | S2/S5 update: active `pybkt × nips2020` artifacts hash-match a sane 57-skill sidecar, so compound KC keying is not the current blocker; cell remains degenerate under G4/G5. Added the lightweight guard suite; later expanded to `18 passed`. |
| 2026-06-14 | current worktree | S4 pyBKT/NIPS audit: all NIPS test-fold skills exist in train, so zero scores are not fallback. `correct_predictions` have ~90% exact zeros across folds while positive rate is ~0.53; cell 6 marked blocked/excluded unless pyBKT formulation changes. |
| 2026-06-14 | current worktree | S4/S6 Accoding audit: active pyBKT Accoding sample provenance confirmed at `max_learners=3000`; cell 12 passes AUC/cold-start/KC-space gates but fails G5 calibration (`ECE≈0.272`) and remains pending G7 plus ≥2-subsample stability. |
| 2026-06-14 | current worktree | G7 metadata prerequisite fixed for the reportable allow-list candidate: DKT×NIPS cold-start and ECE rows now preserve seed plus full training config; future pyBKT reruns will also write fit config. Guard suite later expanded to `18 passed`. |
| 2026-06-14 | current worktree | G7 completed for DKT×NIPS: same-seed rerun to `/private/tmp/kt-g7-dkt-nips2020/results` reproduced fold AUCs exactly (mean Δ=0.000000, max fold Δ=0.000000). Cell 1 marked credible and registry allow-list status changed to `credible`. |
| 2026-06-14 | current worktree | S7/S8 report regeneration: `join.py` now defaults to the credible reportable allow-list; regenerated KT tables/plots and `kt_summary.json` from only `dkt × nips2020` (`30` rows, `gaps=[]`, `public_raw`). Guard suite now `18 passed`. |
| 2026-06-14 | current worktree | Interrupted S3 before progress logging existed; killed silent training PID after it wrote AKT×NIPS full-seq all folds and Deep-IRT×NIPS folds 0-2. Tracker records these as partial/mixed only; reportable allow-list unchanged. Added percent progress logging to KT scripts before continuing heavy reruns. |
| 2026-06-14 | current worktree | S3 NIPS deep rerun completed with progress logging: AKT, Deep-IRT, SAKT, and `dkt_clst_config` now have full-depth full-seq, cold-start, and ECE rows. Gates G1-G6/G8 pass for those four cells; G7 remains pending, so reportable allow-list remains `dkt × nips2020`. |
| 2026-06-14 | current worktree | G7 completed for AKT, Deep-IRT, SAKT, and `dkt_clst_config` × NIPS: same-seed rerun to `/private/tmp/kt-g7-nips-deep/results` reproduced all 20 full-seq fold AUCs exactly (mean Δ=0.000000, max fold Δ=0.000000). Reportable allow-list expanded to the five green NIPS cells; `dkt_clst_config` remains an explicit relabel, not a distinct CLST method. |
| 2026-06-14 | current worktree | Progress logging expanded across KT, comparison CLI scripts, and visible standalone Python scripts. Added `test_progress_logging.py` so new visible Python entrypoints must include progress logs. Test cleanup narrowed so synthetic smoke tests no longer delete `research/results/kt` or raw dataset directories. Restored `pybkt × accoding` local artifacts by rerunning `python -m research_comparison.kt.pybkt_runner --dataset accoding` (30 rows, full AUC folds .608/.601/.608/.611/.604, ECE mean still >0.25); focused KT guards pass (`18 passed`) and full comparison suite passes (`51 passed`). |
| 2026-06-14 | current worktree | Restored raw archives are now usable without special paths: `.gitignore` allows `research/datasets/NeurIPS 2020.zip` and `research/datasets/ACcoding.zip`; `preprocess.py` safely fills missing NIPS landing files from the zip; `accoding_to_poj.py` defaults to the root-level ACcoding zip; `make kt` only generates `data/poj/poj_log.csv` if it is absent. Verified NIPS extraction into `/private/tmp/study-planner-web/kt-verify/nips-data`, ACcoding 1,000-row adapter smoke into `/private/tmp/study-planner-web/kt-verify/poj_log.csv`, and focused tests (`6 passed`). |
| 2026-06-14 | current worktree | T1 ACcoding deep rerun completed: `dkt,akt,deep_irt,sakt,dkt_clst_config` now have full-depth train/cold-start/ECE rows plus scratch G7 reruns with max fold Δ=0.000000. `dkt`, `akt`, `deep_irt`, and `dkt_clst_config` pass G1-G8 but remain partial pending S6 subsample stability; `sakt × accoding` is a genuine full-depth G6 cold-start failure and remains non-reportable. |
| _add as you go_ | | |
