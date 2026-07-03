# Scratchpad - material-session-ui-bugs

_Plan: PLAN.md · Log: VERIFICATION.md · Updated: 2026-07-03T21:44 (Phase 6 implemented, commit pending)_

## Now
**Phase 6 is implemented and awaiting the scoped commit plus reviewer verification.**
`DaySheet.tsx` now keeps `useRef`/`useEffect` before the early return, attaches the ref to the root section, and calls `scrollIntoView({ behavior: 'smooth', block: 'start' })` when a day opens.
`RoadmapCalendar.test.tsx` covers the existing compact empty-day path with a jsdom `Element.prototype.scrollIntoView` stub.
Required verification passed: grep found the new effect, app typecheck passed, and `pnpm --filter @study-tracker/app test -- RoadmapCalendar` passed with 59 files and 523 tests.
Live browser verification also passed against the real app at 390px: tapping `Open 2026-07-01 day options` scrolled from `0` to max scroll `758`, and the DaySheet was fully visible with the empty state present.

## Alignment
Still aligned with the plan.
Phases 1-5 are implemented and reviewer-verified.
The live plan now has added Phases 6-8, and the user asked to start from Phase 6.
Per the plan preamble, this turn is implementing Phase 6 only.
No event model, intelligence math, routing basename, Python code, onboarding gate, or sync code is in scope for Phase 6.
An unrelated deleted file is present before this session: `.work/plans/active/2026-07-03 third-review-report-work/research/SCRATCHPAD-research-2.md`.
An unrelated untracked file also appeared outside this work: `.work/plans/active/2026-07-03 third-review-report-work/research/SCRATCHPAD-research-3.md`.
Do not stage or restore that unrelated deletion.

## Open
- Phase 6 needs a scoped code/docs commit, then reviewer verification.
- Phases 7 and 8 remain fully spec'd with no open design questions and are not being edited in this slice.
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
- [x] Read `.work/README.md`, `.work/STATUS.md`, `PLAN.md`, `VERIFICATION.md`, and this scratchpad.
- [x] Read project-local `project-rules`, `code-memory`, `scratchpad`, and `work-journal` skills.
- [x] Read applicable rules: `playwright-config`, `playwright-full-app-lifecycle`, `css-workspace-packages`, `form-design-spacing`, and `roadmap-engine`.
- [x] Run Phase 6 prereq greps.
- [x] Run baseline `pnpm --filter @study-tracker/app test -- RoadmapCalendar`.
- [x] Implement Phase 6 `DaySheet.tsx` scroll effect.
- [x] Add `RoadmapCalendar.test.tsx` coverage for `scrollIntoView`.
- [x] Run Phase 6 verification: grep, app typecheck, and focused RoadmapCalendar test.
- [x] Run real-app 390px browser check through the managed full-app lifecycle.
- [x] Fill Phase 6 `VERIFICATION.md` implementer report with pending commit SHA.
- [x] Update `SCRATCHPAD.md`, `.work/STATUS.md`, and Phase 6 plan status with pending commit SHA.
- [ ] Commit the scoped Phase 6 changes if verification passes.

## In-flight edits
- Source edits complete: `apps/app/src/roadmap/DaySheet.tsx` and `apps/app/src/roadmap/RoadmapCalendar.test.tsx`.
- Tracking edits complete pending commit SHA replacement: `PLAN.md`, `VERIFICATION.md`, `SCRATCHPAD.md`, `.work/STATUS.md`.
- Do not touch or stage the unrelated deleted `.work/plans/active/2026-07-03 third-review-report-work/research/SCRATCHPAD-research-2.md` or untracked sibling `SCRATCHPAD-research-3.md`.

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
- Phase 6 must keep the DaySheet hooks before the `if (!day) return null` early return for Rules of Hooks compliance.

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
- Phase 6 implementation and verification completed.
- Full-app browser check completed and services stopped.
