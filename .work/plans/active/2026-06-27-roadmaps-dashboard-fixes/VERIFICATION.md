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
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

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
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues / required changes:
- Status: ☐ `✅ Verified` / ☐ `🔁 Changes requested`

### Resolution (implementer fills on redo)

---

## Phase C — Dashboard layout polish

🛑 Blocked on OQ-01 (what is wrong with the layout). Acceptance criteria to be pre-filled once scoped.
