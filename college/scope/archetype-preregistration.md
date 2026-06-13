---
title: Archetype Parameter Pre-Registration (Synthetic Generator)
purpose: Freeze the exact numeric parameters of the synthetic learner generator BEFORE any algorithm comparison is run, with provenance for each value, so the Monte-Carlo study cannot be accused of post-hoc tuning toward a winner.
audience: candidate (***REMOVED***), examiners, future agents
status: PRE-REGISTERED / FROZEN (2026-06-13)
last_updated: 2026-06-13
related:
  - ./research-build-plan.md
  - ./asOfReview1/phase1-research-plan.md
  - ./asOfReview1/pillars-and-algorithms.md
---

## Pre-registration statement

These parameters are **frozen before any candidate comparison is executed.** No value here
may be changed after seeing comparison results in order to favour a candidate. Permitted
changes are limited to (a) fixing an internal-consistency bug, (b) widening a *sensitivity
sweep* range, or (c) an amendment recorded in §10 with a dated reason. The generator stamps
this file's version hash into every dataset manifest, so any result traces back to the exact
parameters that produced it.

**Provenance tags:** `[anchored: ref]` = grounded in a surveyed paper or the shipped prior;
`[default→sweep]` = no external source, a stated default that is varied in the sensitivity
sweep (§8) so the ranking's robustness to it is reported.

## 1 · Convention and units

- The generated quantity is the **pace ratio** `r = activeMinutes / plannedMinutes`, exactly
  as the engines consume it (`bayesian.py` L89, `cusum.py` L84).
- **`r > 1.0` ⇒ sessions over-run the planned slot** (more active minutes than budgeted);
  **`r < 1.0` ⇒ finish under budget.** This convention is fixed for the whole study.
- Latent (noise-free) pace: `r*[t] = m_global · ρ(role) · τ(time_of_day) · ν(day_of_week)
  · g_regime(t) · φ_fatigue(t) · δ_deadline(t)`; emitted `active = planned · r*[t] · ε[t]`.
- **Clip:** `r*·ε` is clipped to **[0.55, 1.60]** to keep emitted sessions physically
  plausible (a slot is never <55% or >160% of plan). Clip rate is logged per run; if any
  archetype clips >2% of sessions, that is a consistency bug to fix, not tune.

## 2 · Noise (ε) — lognormal, multiplicative, AR(1)

`ε[t] = exp(η[t])`, `η[t] = φ·η[t-1] + √(1-φ²)·N(0, σ_log²)` (stationary AR(1), mean 1).

| Parameter | Value | Provenance |
|---|---|---|
| `σ_log` (per archetype, see §4) | 0.15 – 0.25 | `[anchored: py-progress prior var=0.1 ⇒ sd≈0.32 is the upper plausible bound; Chen 2024]` |
| AR(1) coefficient `φ` | 0.30 | `[default→sweep]` |

CV mapping (verified): `σ_log` 0.15 → ±15%, 0.18 → ±18%, 0.25 → ±25% typical session swing.

## 3 · Structural effects (shared across archetypes unless overridden)

**Role multiplier `ρ`** (multiplicative on `m_global`) — `[anchored: role taxonomy in
py-progress / roadmap-engine; magnitudes default→sweep]`:

| Role | ρ | Rationale |
|---|---|---|
| anchor | 1.10 | heavy new material over-runs slots |
| foundation | 1.00 | reference |
| practice | 0.92 | exercises run shorter/faster |

**Time-of-day `τ`** (generic; Morning-Lark overrides in §4) — `[default→sweep]`:
morning 0.97 · afternoon 1.00 · evening 1.05 (mild evening fatigue).

**Day-of-week `ν`** — 1.00 all days (weekend behaviour is modelled via *adherence*, not
pace), except Weekend-Warrior weekend 1.02. `[default→sweep]`

**Fatigue `φ_fatigue`** — `+0.04` per *additional* same-day session (usually 1/day, so ≈1.0
in practice). `[default→sweep]`

**Deadline `δ_deadline`** — 1.00 except Deadline-Sprinter (§4). `[default→sweep]`

## 4 · Per-archetype parameters (FROZEN)

`m_global` is the central pace ratio; `σ_log` the noise scale; shift behaviour and adherence
are archetype-defining. Shift *counts* per length band follow §5.

| Archetype | `m_global` | `σ_log` | Distinguishing mechanism | Adherence (attempt prob.) |
|---|---|---|---|---|
| **Steady** | 1.00 | 0.15 | flat regime, no/low shifts | 0.88 uniform |
| **Morning-Lark** | 0.98 | 0.16 | τ override: morning **0.85**, afternoon 1.00, evening **1.20** | 0.85 uniform |
| **Fading-Flame** | 1.00 → **0.80** | 0.20 | one **gradual drift** (down 0.20) over middle 40% of sequence | declines **0.90 → 0.45** linearly |
| **Weekend-Warrior** | 1.02 | 0.18 | pace flat; ν(weekend)=1.02 | weekday **0.45**, weekend **0.95** |
| **Deadline-Sprinter** | 1.00 | 0.25 | `δ_deadline` ramp ×1.00→**×1.30** over final 20% of timeline (nonlinear) | early **0.45** → final-20% **0.95** |
| **Marathon-Runner** | 1.05 | 0.18 | 2–3 **abrupt steps**, magnitude ±0.12–0.18 | 0.92 uniform |

Provenance: archetype *shapes* `[anchored: phase1-research-plan archetypes; Saqr 2026 for
gradual-disengagement (Fading-Flame); Alhazbi 2024 for adherence/time-management variation]`;
exact magnitudes `[default→sweep]`.

## 5 · Shift schedule per length band (FROZEN)

| Band | Sessions | # shifts | Mix |
|---|---|---|---|
| Small | ~8–20 | 0–1 | single step **or** none |
| Medium | ~35–70 | 1–2 | ≥1 of each type when count=2 |
| Max | ~90–160 | 2–3 | both types represented |

- **Abrupt step magnitude:** ±0.15 (default), drawn U(0.10, 0.22) per shift. `[default→sweep]`
- **Gradual drift total:** 0.20 over its window (default), window = 30–45% of remaining
  sequence. `[anchored: Saqr 2026 critical-slowing-down; magnitude default→sweep]`
- **Onset:** sampled in the interior 20–80% of the sequence; never within 4 sessions of an
  edge (so detection latency is measurable). Every shift recorded in the sidecar as
  `{onset_index, type ∈ step|drift, pre_mean, post_mean, drift_window}`.

## 6 · Adherence / missingness (FROZEN)

- **Attempt probability** per archetype as in §4 (the Bernoulli that a planned slot becomes
  a logged session).
- **Manual fraction:** of *attempted* sessions, 0.15 are logged `source="manual"` (no pace,
  contribute to streak/burn-up only). `[default→sweep]`
- Skipped slots leave real calendar gaps; spacing is therefore irregular by construction.

## 7 · Capacity planner (planned-minutes source, FROZEN)

`plannedMinutes` per slot is set by a **neutral capacity planner**, not a scheduler:
weekday slot = `weekdayHours·60`, weekend = `weekendHours·60`, distributed across the study
days, chunked by material type (playlist 20–50, textbook 40–90, practice 30–75, flashcards
10–20 min). `[anchored: OpenAPI RoadmapGenerateRequest capacity model]` Material totals and
counts per band follow research-build-plan §4.

## 8 · Sensitivity sweep grid

Run after the frozen-default run; report whether the per-track **ranking** is stable across:

| Swept parameter | Grid | Purpose |
|---|---|---|
| noise `σ_log` | {0.12, 0.18, 0.25} | SNR robustness |
| step magnitude | {0.10, 0.15, 0.22} | detection difficulty |
| drift total | {0.12, 0.20, 0.30} | gradual-shift difficulty |
| manual fraction | {0.05, 0.15, 0.25} | missing-pace robustness |
| AR(1) `φ` | {0.0, 0.30, 0.50} | autocorrelation robustness |

A ranking that holds across the grid is a *robustness finding*; a ranking that flips is
reported honestly (and localised to the regime where it flips).

## 9 · Oracle upper-bound baselines (per track)

Confirm each task is discriminable *before* reading candidate results:

- **Calibration oracle** — knows true per-bucket `r*` mean (zero recovery error reference).
- **Detection oracle** — knows planted onsets (latency 0, FA 0); defines the achievable
  frontier the candidates are measured against.
- **Projection oracle** — uses noise-free `r*` (ideal CI coverage + sharpness).

If a track's oracle cannot separate from the field, the SNR is mis-set — adjust §2/§5 ranges
(a consistency fix, recorded in §10), never the candidate-favouring values.

## 10 · Amendments log

| Date | Change | Reason |
|---|---|---|
| 2026-06-13 | Initial pre-registration frozen | grill session decisions (research-build-plan §7) |

## See also

- [`research-build-plan.md`](./research-build-plan.md) — the full research-tier design (§7 generator spec).
- [`asOfReview1/phase1-research-plan.md`](./asOfReview1/phase1-research-plan.md) — archetypes and the ground-truth-model rationale.
