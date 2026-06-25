---
title: study-planner-web — STATUS (read-first index)
status: active living document
last_updated: 2026-06-25
location_note: >
  This is .work/STATUS.md — the single read-first index, living at the root of .work/ (inside the
  repo, tracked on purpose so git clean can't delete it). Paths below are relative to .work/ (non-.work
  targets use ../). Reshaped 2026-06-25 from the former MASTER_TRACKER.md into the scannable
  Active/Queued/Done/Reference/Gotchas model; the full long-form detail is preserved in
  master-tracker-detail.md.
tags:
  "[APP]": product web app
  "[RESEARCH]": research tier (synthetic generator → metrics → validation → report)
  "[PILLAR-A]": Pillar-A rigour / calibration / change-detection
  "[KT]": Pillar-B knowledge-tracing bench
  "[DISSERTATION]": M.Tech dissertation & review deliverables
  "[INFRA]": repo infra / housekeeping
update_protocol: >
  Update the affected row in the same session work changes state; bump last_updated. Push detail
  into the spec/plan/VERIFICATION/handover and link it. The linked canonical file wins over this
  index on any conflict — fix the row, don't paper over it. Code is ground truth.
---

# study-planner-web — STATUS

> **Read first.** The whole project at a glance — a study-plan web app **plus** the M.Tech research
> behind its algorithms. One row per item, tagged by workstream. Full long-form detail (markers,
> SHAs, findings) lives in [`master-tracker-detail.md`](master-tracker-detail.md); folder map in
> [`README.md`](README.md). Keep this short — push depth down and link it.

## Active

- **[PILLAR-A] A6 Phase 6 — change-detection decision.** Probe → **robust null** (no candidate beats CUSUM/CSD). Open call to Rohit: write Phase 6 around the null, or ship calibration as the headline. → [`plans/active/2026-06-18-pillar-a-custom-calibration-detection/`](plans/active/2026-06-18-pillar-a-custom-calibration-detection/PLAN.md)
- **[APP] enriched_shrink production integration.** ✅ Cowork-verified. Immediate: record the Phase-0 dual-prior small-band caveat in the claims ledger. → [`plans/active/2026-06-20-enriched-shrink-production-integration/`](plans/active/2026-06-20-enriched-shrink-production-integration/PLAN.md)
- **[RESEARCH] Phase 5 — N=1 real-data validation.** Log own sessions → export → harness → face-validity overlay + case study (circularity guard).
- **[RESEARCH] Phase 6 — report wiring.** `make figs` → `\input` generated tables/figures into `main.tex`; provenance stamps; reproducibility gate.

## Queued

- **[APP] PWA install** (manifest + service worker) — issue 013.
- **[APP] Plausible analytics** (017, confirm/finish) + **Week streaming narrative** (011).
- **[PILLAR-A] Deferred OQs:** OQ-01 projection wiring (drive burn-up/ETA), OQ-03 Intelligence Service deploy + auth + CORS for production.
- **[DISSERTATION] Review 2** (intermediate results) — gated on research Phases 0–3 (done) → assemble.
- **[DISSERTATION] Review 3** (full comparison + demo + journal draft) — gated on Phases 4–6.
- **[DISSERTATION] Phase II** closed-loop demo — research Phase 7 built, revealed here.

## Done

- **[APP] Dev production-readiness** ✅ — auth (Supabase JWT, HS256 + ES256/JWKS) on all `/v1`, resilient calibration client (timeout/retry/typed errors), Dexie-persisted stale cache + ErrorBoundary, service hardening (request-id, logging, bounds, `/readiness`, rate-limit stub, healthcheck), one-command `pnpm dev:full`. All 5 phases Cowork-verified 2026-06-25 (Phase 2 fixed in `abbac65`). → [`plans/archive/2026-06-20-dev-production-readiness/`](plans/archive/2026-06-20-dev-production-readiness/PLAN.md)
- **[APP] Web app v1 core** — slices 1a–12, 14–16 shipped (auth, session log + per-user isolation, cloud sync/restore, 4-step onboarding, active sessions, URL/YouTube materials, ProgressEngine + pace calibration, replan flow, Google OAuth, marketing site, settings, password reset). → [`specs/issues/`](specs/issues/README.md)
- **[PILLAR-A] A-series rigour A0–A5** ✅ verified (`e1c6455`…`68f4a12`). Pace calibration was an honest null under rigour. → [`plans/active/2026-06-14-pillar-a-rigour.md`](plans/active/2026-06-14-pillar-a-rigour.md)
- **[PILLAR-A] A6 calibration** ✅ — `enriched_shrink` overturns the null (Holm-surviving held-out win); archetype layer not recommended. → [`plans/active/2026-06-18-pillar-a-custom-calibration-detection/`](plans/active/2026-06-18-pillar-a-custom-calibration-detection/PLAN.md)
- **[PILLAR-A] Change-detection probe → robust NULL** (no candidate dominates the CUSUM/CSD frontier). → [`../research/doc/2026-06-20-change-detection-literature-survey.md`](../research/doc/2026-06-20-change-detection-literature-survey.md) · [`archive/unified_detector_summary.md`](archive/unified_detector_summary.md)
- **[RESEARCH] Research tier Phases 0–4, 7** ✅. → [`../college/scope/research-tasklist.md`](../college/scope/research-tasklist.md)
- **[KT] Pillar-B KT-bench Phase 4** ✅ credibility-gated — 9 pyKT cells reportable (5 NIPS2020 + 4 ACcoding). → [`../research/doc/2026-06-14-kt-credibility-tracker.md`](../research/doc/2026-06-14-kt-credibility-tracker.md)
- **[DISSERTATION] Phase I delivered** ✅ — 1st Review report/deck; 1st & 2nd Guidance calls done. → [`../college/mydeliverables/`](../college/mydeliverables/)

## Reference

- **Full workstream detail** (markers, SHAs, findings, caveats, NEXT rollup): [`master-tracker-detail.md`](master-tracker-detail.md)
- **PRD:** [`specs/prd/PRD-study-tracker-web.md`](specs/prd/PRD-study-tracker-web.md) · **Issues:** [`specs/issues/README.md`](specs/issues/README.md)
- **Research KB:** [`../research/doc/`](../research/doc/) · **Research tasklist:** [`../college/scope/research-tasklist.md`](../college/scope/research-tasklist.md)
- **Pillar-A claims ledger:** [`../research/doc/2026-06-18-pillar-a-report-claims-and-caveats.md`](../research/doc/2026-06-18-pillar-a-report-claims-and-caveats.md)
- **Dissertation:** [`../college/mydeliverables/`](../college/mydeliverables/) · **Deploy:** [`../DEPLOYMENT.md`](../DEPLOYMENT.md) · **Folder map:** [`README.md`](README.md)

## Gotchas

- **E2E tests are written but NOT run** (environment constraint — see [`../CLAUDE.md`](../CLAUDE.md)).
- **pnpm build needs the internal registry:** set `COREPACK_NPM_REGISTRY` (see [`../.claude/rules/pnpm-build-registry.md`](../.claude/rules/pnpm-build-registry.md)).
- **LaTeX** builds via TinyTeX on PATH ([`../.claude/rules/latex-report-build.md`](../.claude/rules/latex-report-build.md)).
- **Dexie schema changes must version-up** ([`../.claude/rules/dexie-schema-migration.md`](../.claude/rules/dexie-schema-migration.md)).
- **React Router** `basename="/study"` — never include `/study` in `to` ([`../.claude/rules/react-router-v7-basename.md`](../.claude/rules/react-router-v7-basename.md)).
- **A6 calibration loose ends:** OQ-03 ledger caveat not yet added; restore the pre-registration stop-gate before any Phase 6 dataset change.
- **Git in the Cowork sandbox bricks on lock files** — Cowork never runs mutating git; the native side commits. Never gitignore `.work/`; never `git clean -fdx` at the repo root.
