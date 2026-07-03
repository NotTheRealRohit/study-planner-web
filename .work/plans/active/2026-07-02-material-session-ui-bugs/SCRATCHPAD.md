# Scratchpad - material-session-ui-bugs

_Plan: PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-03T16:20 (D-09 resolved, Phase 8 fully spec'd, ready to implement)_

## Now
**D-09 is resolved (✅ Agreed) and PLAN.md's Phase 8 is fully rewritten and ready to implement — nothing left blocking it.**
Via `/grill-me`, Rohit picked **Option C1 ("Notebook mark")** outright, confirmed the long-wait secondary copy
(~3s swap), and agreed the safety timeout stays **8000ms** but becomes a configurable `SyncProvider` prop
(`initialRestoreSafetyTimeoutMs`, defaulted from a new `VITE_INITIAL_RESTORE_TIMEOUT_MS` env var, same pattern as
`VITE_INTELLIGENCE_URL`) rather than a hardcoded literal — his ask was "make this timeout easily editable, like a
plugin." Wrote the full decision + implementation detail into `PLAN.md`'s D-09 entry (same rigor as D-10) and
rewrote Phase 8's Steps 5-7, added Steps 8-9 (new CSS in `packages/design-tokens/src/components.css`; env-var docs
in `CLAUDE.md`/`apps/app/.env.example`), updated the Files-touched index, Tests, and Verification sections, and
closed OQ-03. Phase 8 is now self-contained and implementable by a fresh agent with no outstanding design questions.

Mock is built and visually verified (this is what grounded the grill-me discussion and is now Phase 8's cited visual contract):
[`mocks/proposed/bug6-branded-loading.html`](./mocks/proposed/bug6-branded-loading.html) — baseline (byte-accurate
to today's shipped, uncentered plain "Loading..." card) plus three candidate options, each real CSS (tokens/global/
components templates refreshed-and-confirmed-identical to source) + real DOM (inline SVG built from the actual
`favicon.svg` mark geometry, split into 3 separately-animatable ruled lines + dot), rendered live in both a 390×660
phone iframe and a 640×420 desktop iframe:
- **C1 — Notebook mark (recommended):** full-bleed paper background, the mark draws itself in line-by-line then the
  dot settles into a quiet pulse, wordmark + plain-language caption cascade in underneath. Warmest/calmest.
- **C2 — Ink curtain:** full-bleed `--surface-inverted` takeover (reusing the same inverted-surface token
  `.card-inverted` already uses elsewhere, not a new dark mode), mark rendered directly on a soft terracotta glow,
  sparse copy. Boldest/most ceremonial.
- **C3 — Quiet caption:** same `.card.card-elevated` footprint/position as today's placeholder, small static mark +
  one sentence of real status copy + "This only happens once." Smallest departure, safest/least memorable.

A "Show long-wait state" toggle swaps each option's copy to a reassuring "still working" variant, to help ground
the still-fully-open safety-timeout-duration question in something concrete rather than an abstract number.
Verified via a throwaway Playwright script (screenshots of all 4 states × both viewports + the long-wait toggle,
zero console/page errors) — not committed anywhere, just a local render check.

**Next: implement Phases 6, 7, and 8** — all three are independent (no cross-dependencies) and fully spec'd with no
open design questions. Order doesn't matter; pick whichever fits the next session's context budget.

## Alignment
Still aligned with the plan.
Phases 1-4 are implemented and awaiting reviewer pass.
Rohit explicitly asked to start Phases 5 and 6, so this session proceeds into Phase 5 despite the previous scratchpad's reviewer-pass next action.
`PLAN.md` has only Phases 1-5 plus a final gate.
The requested Phase 6 is interpreted as the final gate after Phase 5 unless a separate Phase 6 plan appears.
Phase 5 prereq greps matched the expected legacy burn-up implementation.
`pnpm --filter @study-tracker/progress test` passed before Phase 5 edits.
The Phase 5 red tests failed for the intended reasons, then passed after the implementation.
Focused verification passed: progress test suite, app typecheck, and `BurnUpChart Week` app tests.
The pre-review final gate passed: lint exits 0 with pre-existing warnings, full typecheck passed, app tests passed, and progress tests passed.
Browser visual inspection found and fixed an overly dense y-axis tick design from the plan's sample helper.
The final browser probe of `/study/chart-test` showed sparse unique visible y labels and a nonblank 798x280 chart.
No event model, intelligence math, routing basename, or Python code is in scope.
Unrelated dirty rule/doc files and `_perm_test.txt` are present before this session and must not be touched or staged.

## Open
- Phases 6, 7, and 8 are all fully spec'd with no open design questions — ready to implement whenever, in any order,
  independently of each other.
- Run the authored hermetic E2E specs (`e2e/material-session-decoupling.spec.ts`'s two new BUG-2/BUG-4 cases) on a machine with `SUPABASE_SERVICE_ROLE_KEY` set — the reviewer replicated their assertions manually against the real test account instead, since the key is unset here. (Pre-existing item from the Phase 1-5 review, still open.)
- Phase 8's Verification (DONE) step now also asks the implementer to record the *actual observed* cold-start restore duration during the live re-check (there's no production telemetry for this yet — D-09 leaned on an existing app-wide timeout convention, `intelligenceClient.ts`'s `TIMEOUT_MS=8000`, rather than a measurement). Worth surfacing if that number turns out to be way off from 8000ms.

## Blockers
- none

## Deferrals
- BUG-4d: back-to-`/roadmaps` exit for re-entrant onboarding remains deferred.
  Trigger: picking up re-entrant onboarding UX work.
- Cleaner `.modal-overlay` and `.modal-card` consolidation remains deferred.
  Trigger: a follow-up modal consistency pass after the targeted `.bk-*` fix.
- Full Phase-5-port responsive-rule sweep remains deferred.
  Trigger: broader roadmap CSS audit, not this targeted burn-up fix.

## Checklist
- [x] Read the 2026-07-03 handover, `PLAN.md`, and this scratchpad at session start.
- [x] Diff `mocks/real-css/*.css` against live source — confirmed byte-identical, no refresh needed.
- [x] Invoke `/frontend-design` for aesthetic direction on the branded-loading moment.
- [x] Design 3 candidate treatments (C1 Notebook mark, C2 Ink curtain, C3 Quiet caption) spanning minimal→bold.
- [x] Build `mocks/proposed/bug6-branded-loading.html` (baseline + 3 options × 2 viewports + long-wait toggle).
- [x] Visually verify the mock via a throwaway Playwright screenshot script — no console/page errors.
- [x] Run `/grill-me` with Rohit — picked C1, confirmed long-wait copy, agreed 8000ms made configurable.
- [x] Used `/write-implementation-plan` (adapted to update the existing living plan, not scaffold a new file) to
      write D-09 ✅ Agreed, rewrite Phase 8 Steps 5-7 and add Steps 8-9, update Files-touched/Tests/Verification, close OQ-03.
- [ ] `work-journal` the outcome (this scratchpad + `.work/STATUS.md`).
- [ ] Implement Phases 6, 7, 8 (next session or later this session, per Rohit's call).

## In-flight edits
- none.
  Phase 5 implementation is committed in `256616b`.
  The `.work` SHA recording is committed in the current docs follow-up.

## Decisions in force
- D-05: keep burn-up rendering client-side.
- D-05: planned burn-up baseline mirrors booking capacity by selected study day, using full weekday/weekend hours per selected day.
- D-05: do not use legacy slot-grid splitting for the fixed product burn-up chart.
- `BurnUpData.startDate` and `BurnUpData.deadline` remain optional.
- Week's low-data gate stays in place.
- E2E specs may be authored but not run (though this environment can run them — see `CLAUDE.md`; Phases 6-8 lean toward actually running visual/Playwright checks where practical).
- Reuse existing Marginalia palette and chart restraint; spend the UI change on clarity, not a new visual identity.
- Design deviation in force: high-range tick values target roughly six readable intervals rather than the plan's literal 2h step for large domains.
- Do not touch unrelated dirty rule/doc files or `_perm_test.txt`.
- D-07: BUG-6's fix is centralized in `SyncProvider`; `RequireOnboarding.tsx`/`OnboardingGate.tsx` are not modified.
- D-08: `initialRestorePending` clears immediately on the fast (already-hydrated) path; only the genuine cold-start slow path blocks — never add a visible delay to ordinary page reloads for returning users.
- D-09: Phase 8 ships **Option C1 ("Notebook mark")** — resolved, no longer open. The old plain `ProtectedRoute`-style "Loading..." placeholder is fully superseded; do not implement it. Safety timeout stays 8000ms but ships as a configurable `initialRestoreSafetyTimeoutMs` prop (env-var-backed default via `VITE_INITIAL_RESTORE_TIMEOUT_MS`), not a hardcoded literal.
- D-10: Phase 7 ships Option C (icon + duration, drop "Session" label) — resolved, no longer open.

## Resolved (recent)
- D-09 (Phase 8's loading-state visual + safety-timeout duration) — resolved via `/frontend-design` mock + `/grill-me`: Option C1, long-wait copy at ~3s, 8000ms timeout made configurable. OQ-03 closed. PLAN.md's Phase 8 fully rewritten (Steps 5-9) and ready to implement.
- Phase 5's full implementation checklist (prereqs → tests → implementation → verification → commits) completed; see the previous scratchpad revision or `VERIFICATION.md` for the itemized list.
- Planning handoff state superseded by implementation state for Phase 1 and Phase 2.
- Phase 1 verification passed and commit `0268f20` exists.
- Phase 2 verification passed and commit `0268f20` exists.
- Phase 3 verification passed and commit `3c8d869` exists.
- Phase 4 verification passed and commit `3c8d869` exists.
- Phase 5 prereq verification passed before edits.
- Phase 5 focused verification passed after implementation.
- Final-gate probe passed after the tick-density visual fix.
- Scoped Phase 5 implementation commit created: `256616b`.
- Scoped `.work` docs follow-up committed after recording `256616b`.
