# VERIFICATION — roadmaps-dashboard-fixes

Round-trips between planner (Cowork), implementer (Codex/Sonnet), and reviewer (Cowork).
Acceptance criteria are pre-filled by the planner. Implementer fills its report per phase; reviewer
fills findings. A phase is done only at `✅ Verified`.

---

## Phase A — New-roadmap mode survives the whole wizard (P0)

### Acceptance criteria (planner pre-fill)

- [ ] `apps/app/src/onboarding/useOnboardingNavigate.ts` exists and preserves `location.search` + `location.state` for string destinations.
- [ ] As a user with an existing `OnboardingCompleted` event: `/onboarding/1?new=1` → fill deadline + purpose → **Continue** advances to `/onboarding/2` with `?new=1` still in the URL (NOT redirected to `/home`).
- [ ] The full wizard (steps 1→2→3→preview) keeps `?new=1` at every step for a returning user.
- [ ] `OnboardingGate` latches new-roadmap mode in a ref; a single missed nav path does not bounce the user to `/home` mid-wizard.
- [ ] `Step3Preview` finish branches correctly for a returning user (its own `newRoadmapMode` is true): active plan present → saves draft, returns to `/roadmaps`; no active plan → emits `RoadmapCreated` (no duplicate `OnboardingCompleted`), returns to `/roadmaps`.
- [ ] Exit navigations are unchanged: `/roadmaps`, `/onboarding/4`, `/home` do NOT carry `?new=1`.
- [ ] `CheckpointGate` back-redirect preserves `location.search` + `state`.
- [ ] First-run (no `OnboardingCompleted`) onboarding still works end-to-end and lands on `/onboarding/4`.
- [ ] Direct/refresh entry to `/onboarding/2` with no param and no latch still redirects a completed user to `/home`.
- [ ] New Vitest tests cover param survival and the gate's no-redirect-in-new-mode case; suite green under Node ≥ 20.
- [ ] `pnpm --filter app typecheck` clean.

### Implementer report (Codex/Sonnet fills)

- Files changed:
  - `apps/app/src/onboarding/useOnboardingNavigate.ts`
  - `apps/app/src/onboarding/useOnboardingNavigate.test.tsx`
  - `apps/app/src/onboarding/OnboardingGate.tsx`
  - `apps/app/src/onboarding/OnboardingGate.test.tsx`
  - `apps/app/src/onboarding/CheckpointGate.tsx`
  - `apps/app/src/onboarding/components/CapacityPrompt.tsx`
  - `apps/app/src/onboarding/steps/Step1Deadline.tsx`
  - `apps/app/src/onboarding/steps/Step2Hours.tsx`
  - `apps/app/src/onboarding/steps/Step3Materials.tsx`
  - `apps/app/src/onboarding/steps/Step3Preview.tsx`
- Commit SHA: `03f7386331c56c193ed49ea32fb73ed79d6ae5a8`
- What was done:
  - Added `useOnboardingNavigate()` to preserve `location.search` and `location.state` while navigating between onboarding steps.
  - Converted the Phase A intra-onboarding navigations to the helper, while leaving `/roadmaps`, `/onboarding/4`, and `/home` exits on plain `useNavigate()`.
  - Latched new-roadmap mode in `OnboardingGate` and preserved search/state in `CheckpointGate` redirects.
  - Added Vitest coverage for helper preservation and a returning user staying inside new-roadmap mode after step navigation.
- Deviations + why:
  - None.
- Self-check vs criteria:
  - `pnpm --filter app test -- onboarding OnboardingGate useOnboardingNavigate` passed under Node v22.17.1 (49 files, 452 tests).
  - `pnpm --filter app typecheck` passed under Node v22.17.1.
  - Grep confirmed `Step1Deadline` imports/uses `useOnboardingNavigate`, and exit navigations remain unconverted.

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues / required changes:
- Status: ☐ `✅ Verified` / ☐ `🔁 Changes requested`

### Resolution (implementer fills on redo)

---

## Phase B — Historical roadmap opens as a closable route view (P1)

### Acceptance criteria (planner pre-fill)

- [ ] Clicking a History row navigates to `/roadmap?roadmap=<encodeURIComponent(createdAt)>` (URL changes; not component state).
- [ ] `pages/Roadmap.tsx` reads the `roadmap` param: present → read-only calendar for that entry; absent → active plan (unchanged).
- [ ] The read-only historical route view shows a "← Roadmaps" back link; the link and the browser Back button both return to `/roadmaps` without a page refresh.
- [ ] The inline `selectedCreatedAt` read-only calendar is removed from `Roadmaps.tsx` (no dead state / unused import).
- [ ] No `/study` prefix appears in any `to`/`navigate` path (router rule).
- [ ] Active `/roadmap` (no param) view is unchanged.
- [ ] Vitest covers: history click → URL navigation; no inline detail panel in the dashboard. Suite green under Node ≥ 20.
- [ ] `pnpm --filter app typecheck` and `pnpm lint` clean.

### Implementer report (Codex/Sonnet fills)

- Files changed:
  - `apps/app/src/pages/Roadmap.tsx`
  - `apps/app/src/pages/Roadmap.test.tsx`
  - `apps/app/src/pages/Roadmaps.tsx`
  - `apps/app/src/pages/Roadmaps.test.tsx`
  - `apps/app/src/roadmap/RoadmapCalendar.tsx`
  - `apps/app/src/roadmap/RoadmapCalendar.test.tsx`
  - `apps/app/src/onboarding/OnboardingGate.test.tsx`
- Commit SHA: pending
- What was done:
  - Changed history rows from component-state buttons to `<Link>` rows targeting `/roadmap?roadmap=${encodeURIComponent(createdAt)}`.
  - Removed `selectedCreatedAt`, `selectedEntry`, the inline `roadmaps-readonly` calendar panel, and the unused `RoadmapCalendar` import from `Roadmaps.tsx`.
  - Updated `Roadmap.tsx` to read the `roadmap` search param and render the selected entry in read-only mode when present.
  - Updated `RoadmapCalendar` so historical read-only route views still show the existing `← Roadmaps` back link.
  - Added tests for history link navigation/no inline panel, `Roadmap` query-param handoff, and the historical back link.
- Deviations + why:
  - Also replaced explicit `any` casts in the touched `OnboardingGate.test.tsx` with typed `EventStore` casts after `pnpm lint` surfaced warnings in that file. No behavior changed.
- Self-check vs criteria:
  - `pnpm --filter app test -- Roadmaps Roadmap` passed under Node v22.17.1 (50 files, 455 tests).
  - `pnpm --filter app test -- OnboardingGate useOnboardingNavigate Roadmaps Roadmap` passed after the touched-test lint cleanup (50 files, 455 tests).
  - `pnpm --filter app typecheck` passed.
  - `pnpm lint` exited 0; it reports four warning-only `no-explicit-any` findings in unrelated session files.
  - Grep found no `selectedCreatedAt`, `roadmaps-readonly`, or `RoadmapCalendar` references left in `Roadmaps.tsx`.
  - Grep found no `/study` paths in the touched route/calendar files.

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues / required changes:
- Status: ☐ `✅ Verified` / ☐ `🔁 Changes requested`

### Resolution (implementer fills on redo)

---

## Phase C — Dashboard layout polish

🛑 Blocked on OQ-01 (what is wrong with the layout). Acceptance criteria to be pre-filled once scoped.
