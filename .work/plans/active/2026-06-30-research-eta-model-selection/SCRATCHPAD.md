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
last_updated: "<YYYY-MM-DD HH:MM> — <who>"
---

# Scratchpad

> Relationship to the other docs (do not blur): **PLAN.md** is the spec you follow.
> **VERIFICATION.md** is the formal gate (Developer notes you fill + Reviewer sign-off).
> **This file** is your running brain: every decision, number, deviation, blocker, and the immediate
> next step — enough that a fresh session (or the reviewer) can resume with zero extra context.

## 1. Current status (one-liner + phase board)
- **Now:** <one sentence: what is in flight right now>
- **Branch / last commit:** `<branch>` @ `<sha>`
- **Phase board:** P0 ☐ · R1 ☐ · R2 ☐ · R3 ☐ · R4 ☐ · R5 ☐ · R6 ☐

## 2. Next actions (the immediate queue — keep this current)
1. <next concrete step>
2. <after that>

## 3. Environment / run notes
- What runs in this sandbox vs authored-only (record the arm64/dep status the first time you hit it):
- Exact commands that worked (copy the ones that ran clean):
- New decoupled dataset id once generated: `synthetic-decoupled-<hash>-seed0-n<count>` → `<path>`

## 4. Decisions made during execution (continue PLAN §2's D-xx numbering)
> Record every choice you make that the PLAN left open or that deviates from it, with the why.
- **D-08 —** <decision> — *why:* <reason> — *date:*
- (OQ resolutions go here too: OQ-1 partial inclusion policy, OQ-2 cadence params, OQ-3 COLD_START_N +
  interval recipe, OQ-4 A-series parity config.)

## 5. Results ledger (numbers as they land — the stuff the reviewer + dissertation cite)
> Paste the real headline numbers from the stamped result JSONs. No rounding-to-make-it-look-good.
- **P0 baseline (frozen A-series):** calibration winner/Holm survivors = … ; detection robust-null = … ;
  projection coverage/MAE/sharpness per band (gp_ard) = …
- **R2 calibration (decoupled):** enriched_shrink / dual_prior held-out Holm verdict = …
- **R3 detection (decoupled):** robust-null holds? = … (deviations: …)
- **R4 ETA (decoupled) — HEADLINE:** per band, gp_ard vs analytic_required_rate vs gp_plus_analytic
  (coverage / MAE-days / sharpness); **paired-Holm vs gp_ard survives?** = … ; cold-start (R4a) = … ;
  reference-line (R4b) = done/deferred.
- **R6 N=1:** partial-throughput in-family? = … ; ETA-on-real descriptive error = …

## 6. Deviations from PLAN (what + why + reviewer-flagged?)
- <none yet>

## 7. Blockers / open risks
- <none yet>

---

## 8. Session log (append-only — newest at the bottom)

### <YYYY-MM-DD HH:MM> — session 1 — <who>
- **Goal this session:**
- **Did:**
- **Files changed:**
- **Commit SHA:**
- **Results / numbers:**
- **Deviations / decisions:** (cross-ref §4/§6)
- **Left off at / next:** (mirror into §2)
