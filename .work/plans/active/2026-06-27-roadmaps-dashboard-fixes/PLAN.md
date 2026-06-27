<!--
  Operating-manual preamble (condensed). The full verbatim preamble lives in the parent
  plan: ../2026-06-26-roadmaps-dashboard/PLAN.md. Read this header in full before coding.
-->

# How to use this plan (condensed)

> **You are the implementing agent.** This is a focused bug-fix runbook for three defects found
> in manual testing of the Roadmaps dashboard. Each phase is a vertical slice that leaves the app
> working. Pick the first phase whose `Status:` is `☐ Not started` and whose `Depends on:` are all
> `✅`. Implement that phase only. If reality doesn't match a step, STOP and surface — do not improvise.

> **Step 0, before writing any code:** commit these planning docs verbatim —
> `docs(plan): add roadmaps-dashboard-fixes plan + verification`. Cowork cannot commit (the sandbox
> bricks on git lock files), so the native side must establish this baseline first; otherwise later
> phase diffs have nothing to diff against. After each phase, fill your section of
> [`VERIFICATION.md`](./VERIFICATION.md) (files changed, commit SHA, what you did, deviations + why)
> and expect review. **A phase is not done until the reviewer marks it `✅ Verified`; change requests
> may follow.**

Status vocabulary: `☐ Not started` · `🟡 In progress` · `🛑 Blocked: <reason>` · `✅ Complete — <sha>`.

---

# Roadmaps dashboard: post-ship bug fixes (re-entrant onboarding, history detail URL, layout)

**Slug:** `2026-06-27-roadmaps-dashboard-fixes`
**Date written:** 2026-06-27
**Author:** Claude (planner) + Rohit
**Plan status:** Draft
**Parent:** [`plans/active/2026-06-26-roadmaps-dashboard/PLAN.md`](../2026-06-26-roadmaps-dashboard/PLAN.md) (Phases 1–7 implemented; P7 awaiting review). These are defects found while manually testing that work.

## TL;DR

Three bugs surfaced in manual testing of the shipped dashboard, ranked by how hard they block further
verification:

1. **[P0 — blocks everything] New-roadmap onboarding can't start.** "Plan your next roadmap" → `/onboarding/1?new=1` opens correctly, but clicking **Continue** lands the user on `/home` and the wizard never advances. **Root cause:** the `?new=1` search param (the only signal that puts `OnboardingGate` into new-roadmap mode for a returning user) is **dropped by every intra-onboarding `navigate()` call**. The first `navigate('/onboarding/2')` produces a URL with no `?new=1`; `OnboardingGate` recomputes `newRoadmapMode = false`, sees an existing `OnboardingCompleted` event, and redirects to `/home`. Fix = make new-roadmap mode survive every step navigation. (Phase A — **do this first**.)
2. **[P1 — blocks history verification] Historical roadmap detail has no way to close.** Clicking a History row sets a component-state `selectedCreatedAt` and renders a read-only `RoadmapCalendar` inline under the list, with no back/close affordance and no URL change — the only escape is a full page refresh. Fix = open the historical roadmap as a real route view at `/roadmap?roadmap=<createdAt>` (read-only, with the existing "← Roadmaps" back link), so the browser back button and the back link both close it. (Phase B.)
3. **[P2 — cosmetic, needs input] "Bad dashboard layout."** Under-specified; gated on clarification from Rohit (see Open Questions OQ-01). Not scoped here yet.

Phase A unblocks the user's stated priority ("so onboarding and new roadmap can at least start so I can
verify the rest"). Phase B unblocks history verification. Phase C is a placeholder pending OQ-01.

## Context & grounding

Constraints (unchanged): mobile-first React 19 SPA, event-sourced Dexie store, `BrowserRouter
basename="/study"` — **never put `/study` in `to`/`navigate` paths** (rule
[`react-router-v7-basename.md`](../../../.claude/rules/react-router-v7-basename.md)). E2E tests are
authored but **not run** in this environment (see [`../../../CLAUDE.md`](../../../CLAUDE.md)); Vitest
unit tests should still be authored and the app suite must be run under **Node ≥ 20** (default shell
Node v18 cannot run the app Vitest suite — see parent plan Phase 1 notes; use the project's
`v22.17.1`).

Ground-truth observed during diagnosis (verify still true before editing):

- `apps/app/src/onboarding/OnboardingGate.tsx` — `newRoadmapMode` is derived **only** from
  `location.search` `?new=1` or `location.state.newRoadmap`. It is the parent route element for
  `/onboarding`, so it **stays mounted across step changes** (children swap via `<Outlet/>`).
- `apps/app/src/App.tsx` — `OnboardingIndexRedirect` (line ~121) already preserves `location.search`
  **and** `location.state` when redirecting `/onboarding` → `/onboarding/1`. The intra-step
  navigations do **not** follow this pattern.
- Intra-onboarding navigations that **drop** the param (grep result):
  - `steps/Step1Deadline.tsx:34` `navigate('/onboarding/2')`
  - `steps/Step2Hours.tsx:34` `navigate('/onboarding/1')`, `:45` `navigate('/onboarding/3')`
  - `steps/Step3Materials.tsx:156` `navigate('/onboarding/2')`, `:159` `navigate('/onboarding/3/preview')`
  - `steps/Step3Preview.tsx:319` `navigate('/onboarding/3')`
  - `components/CapacityPrompt.tsx:30/33/36` `navigate('/onboarding/1'|'2'|'3')`
  - `CheckpointGate.tsx:32` `<Navigate to={`/onboarding/${earliestIncomplete}`} replace/>`
- `steps/Step3Preview.tsx:33` computes its **own** `newRoadmapMode` from `location` — so it ALSO
  mis-branches when the param is lost (it would treat a returning user's new roadmap as first-run).
  Preserving the param across navigation fixes both `OnboardingGate` and `Step3Preview`.
- Navigations that **exit** onboarding must NOT carry `?new=1`: `Step3Preview.tsx:179` & `:230`
  `navigate('/roadmaps')`/`navigate('/onboarding/4')`; `Step4Confirm.tsx:52/95` `navigate('/home')`.
  (`/onboarding/4` is first-run only and must not carry `?new=1`.)
- Bug #2: `pages/Roadmap.tsx` renders `<RoadmapCalendar />` with no props (always the active plan).
  `RoadmapCalendar` already accepts `{ roadmapCreatedAt?: string | null, readOnly?: boolean }` and
  resolves the entry via `lifecycle.all.find(...)` (RoadmapCalendar.tsx:130–167). The "← Roadmaps"
  back link renders **only when `!readOnly`** (RoadmapCalendar.tsx:387).
  `pages/Roadmaps.tsx:99,328–335` selects via `useState` + inline read-only calendar (no URL, no close).

## Decisions log

### D-01: New-roadmap mode is propagated by preserving the URL search param across every intra-onboarding navigation, AND latched in `OnboardingGate` as defense-in-depth

**Status:** ✅ Agreed (planner default; reversible)

**Decision:** (a) Every navigation that stays **within** `/onboarding/*` preserves the current
`location.search` (which carries `?new=1`) and `location.state`. Centralize this in a tiny hook
`useOnboardingNavigate()` so call sites can't forget it. (b) Additionally, `OnboardingGate` **latches**
new-roadmap mode in a `useRef` the first time it sees the param/state, so the gate keeps the user in
the wizard even if some navigation path is missed. The URL remains the source of truth (refresh-safe);
the latch is a safety net within a single mount.

**Rationale:** The URL-preservation fix is the complete one (it also fixes `Step3Preview`'s independent
detection and keeps refresh/back honest). The latch alone would not fix `Step3Preview`. Doing both is
small, low-risk, and robust. Mirrors the existing `OnboardingIndexRedirect` pattern.

**Alternatives considered:** sessionStorage flag (drifts from URL, extra cleanup); `intent` event
(D-12 of parent plan explicitly chose derive-not-flag) — rejected.

**Reversibility:** easy.

### D-02: Historical roadmaps are viewed at `/roadmap?roadmap=<createdAt>` (read-only), not as inline component state

**Status:** ✅ Agreed (user explicitly asked for a URL redirect `/roadmap?someParam`)

**Decision:** A History-row click navigates to `/roadmap?roadmap=<encodeURIComponent(createdAt)>`.
`pages/Roadmap.tsx` reads the `roadmap` search param: if present, render
`<RoadmapCalendar roadmapCreatedAt={param} readOnly />`; if absent, render `<RoadmapCalendar />`
(the active plan, unchanged). The "← Roadmaps" back link must render in this read-only-via-route case
so there is always a way out (browser Back also works because it's a real navigation). Remove the
inline `selectedCreatedAt` calendar from `Roadmaps.tsx`.

**Rationale:** Makes the detail a first-class, shareable, back-button-friendly view and eliminates the
no-escape inline panel. Reuses the calendar's existing `roadmapCreatedAt`/`readOnly` support — minimal
new code.

**User pushback:** none — user proposed the URL approach.

**Reversibility:** easy.

### D-03: Bug #1 ("bad layout") is not scoped until Rohit specifies what is wrong

**Status:** 🤔 Open (OQ-01)

**Decision:** Do not guess at layout changes. Phase C is a placeholder; fill it only after OQ-01 is
answered (or after a design critique the user approves).

## Files touched (index)

| Path | Change | Phase | Purpose |
|------|--------|-------|---------|
| `apps/app/src/onboarding/useOnboardingNavigate.ts` | new | A | Hook: `navigate` that preserves `location.search` + `state` within onboarding (D-01) |
| `apps/app/src/onboarding/OnboardingGate.tsx` | modify | A | Latch new-roadmap mode in a ref (D-01) |
| `apps/app/src/onboarding/CheckpointGate.tsx` | modify | A | Preserve search on the back-redirect `<Navigate>` (D-01) |
| `apps/app/src/onboarding/steps/Step1Deadline.tsx` | modify | A | Use `useOnboardingNavigate` for `/onboarding/2` |
| `apps/app/src/onboarding/steps/Step2Hours.tsx` | modify | A | Use it for `/onboarding/1` and `/onboarding/3` |
| `apps/app/src/onboarding/steps/Step3Materials.tsx` | modify | A | Use it for `/onboarding/2` and `/onboarding/3/preview` |
| `apps/app/src/onboarding/steps/Step3Preview.tsx` | modify | A | Use it for the `/onboarding/3` back nav (NOT the `/roadmaps`/`/onboarding/4` exits) |
| `apps/app/src/onboarding/components/CapacityPrompt.tsx` | modify | A | Use it for `/onboarding/1|2|3` |
| `apps/app/src/onboarding/*.test.tsx` | new/modify | A | Cover param survival end-to-end |
| `apps/app/src/pages/Roadmap.tsx` | modify | B | Read `?roadmap=` param → read-only historical view (D-02) |
| `apps/app/src/roadmap/RoadmapCalendar.tsx` | modify | B | Render "← Roadmaps" back link in read-only-via-route mode (D-02) |
| `apps/app/src/pages/Roadmaps.tsx` | modify | B | History row → `Link to="/roadmap?roadmap=..."`; remove inline `selectedCreatedAt` calendar (D-02) |
| `apps/app/src/pages/Roadmaps.test.tsx` | modify | B | History click navigates by URL; no inline detail panel |

## Phases

### Phase A: New-roadmap mode survives the whole wizard (UNBLOCKS onboarding) — DO FIRST

**Status:** ☐ Not started
**Depends on:** none
**Estimated scope:** ~8 files, ~120 lines

#### Codebase state assumed at start

As grounded above. Confirm before editing:

```bash
cd apps/app
grep -n "navigate('/onboarding/2')" src/onboarding/steps/Step1Deadline.tsx   # expect line ~34
grep -n "newRoadmapMode" src/onboarding/OnboardingGate.tsx                   # expect derive-from-location
grep -n "newRoadmapMode" src/onboarding/steps/Step3Preview.tsx               # expect its own derive
```

If `useOnboardingNavigate` already exists, STOP and surface — the plan is stale.

#### Steps

1. **Create `apps/app/src/onboarding/useOnboardingNavigate.ts`** — a thin wrapper over `useNavigate`
   that, for **string** destinations under `/onboarding`, preserves the current `location.search` and
   `location.state`. Exits (`/home`, `/roadmaps`) call plain navigate. Implements D-01.

   ```ts
   import { useCallback } from 'react'
   import { useLocation, useNavigate, type NavigateOptions } from 'react-router-dom'

   /**
    * navigate() that keeps new-roadmap mode (?new=1 / state.newRoadmap) attached while moving
    * BETWEEN onboarding steps. Use ONLY for intra-onboarding destinations ('/onboarding/...').
    * For destinations that leave onboarding ('/home', '/roadmaps'), call useNavigate() directly. (D-01)
    */
   export function useOnboardingNavigate() {
     const navigate = useNavigate()
     const location = useLocation()
     return useCallback(
       (to: string, options?: NavigateOptions) => {
         navigate(
           { pathname: to, search: location.search },
           { state: location.state, ...options },
         )
       },
       [navigate, location.search, location.state],
     )
   }
   ```

2. **`OnboardingGate.tsx`** — latch new-roadmap mode so it survives even an un-converted nav path
   (D-01). The component stays mounted across step changes, so a ref persists for the wizard session:

   ```tsx
   import { type ReactNode, useEffect, useRef } from 'react'
   // ...
   const urlNewRoadmapMode =
     new URLSearchParams(location.search).get('new') === '1' ||
     (location.state as { newRoadmap?: boolean } | null)?.newRoadmap === true
   const latchedNewRoadmap = useRef(false)
   if (urlNewRoadmapMode) latchedNewRoadmap.current = true
   const newRoadmapMode = urlNewRoadmapMode || latchedNewRoadmap.current
   ```

   Leave the existing redirect `useEffect` and render guards as-is (they already key off
   `newRoadmapMode`). Keep `newRoadmapMode` in the effect dependency array.

3. **Convert intra-onboarding navigations** to `useOnboardingNavigate()` in: `Step1Deadline.tsx`
   (`/onboarding/2`), `Step2Hours.tsx` (`/onboarding/1`, `/onboarding/3`), `Step3Materials.tsx`
   (`/onboarding/2`, `/onboarding/3/preview`), `Step3Preview.tsx` (the `/onboarding/3` back nav at
   line ~319 only), `CapacityPrompt.tsx` (`/onboarding/1|2|3`). In each file, replace
   `const navigate = useNavigate()` with `const navigate = useOnboardingNavigate()` **only if the
   file has no exit navigations**; where a file has BOTH intra and exit navigations (`Step3Preview`),
   keep `useNavigate` for the exits and add a separately-named `const stepNavigate = useOnboardingNavigate()`
   for the intra-step back nav. **Do not** change `Step3Preview.tsx:179/:230` (`/roadmaps`,
   `/onboarding/4`) or `Step4Confirm.tsx` (`/home`).

4. **`CheckpointGate.tsx`** — preserve search on the corrective back-redirect so a returning user
   bounced to an earlier step keeps new-roadmap mode (D-01):

   ```tsx
   import { Navigate, useLocation } from 'react-router-dom'
   // ...
   const location = useLocation()
   // ...
   if (earliestIncomplete > 0) {
     return (
       <Navigate
         to={{ pathname: `/onboarding/${earliestIncomplete}`, search: location.search }}
         state={location.state}
         replace
       />
     )
   }
   ```

#### Tests

- `apps/app/src/onboarding/useOnboardingNavigate.test.tsx` (or extend an existing onboarding test):
  - mount a router at `/onboarding/1?new=1`, render a component using the hook, trigger
    `navigate('/onboarding/2')` → asserted resulting location is `/onboarding/2?new=1`.
- Extend the OnboardingGate test:
  - returning user (events include `OnboardingCompleted`) at `/onboarding/1?new=1`, advance to
    `/onboarding/2` via the hook → gate still renders children (does NOT redirect to `/home`).
  - returning user at `/onboarding/2` with **no** param and no prior latch → redirects to `/home`
    (unchanged guard for direct/refresh entry without mode).
- Run (Node ≥ 20): `pnpm --filter app test -- onboarding OnboardingGate useOnboardingNavigate`

#### Verification (DONE)

```bash
cd apps/app
pnpm --filter app test -- onboarding OnboardingGate useOnboardingNavigate   # expect green
grep -n "useOnboardingNavigate" src/onboarding/steps/Step1Deadline.tsx      # expect present
pnpm --filter app typecheck
```

Manual smoke (native side, dev server): as a user who has completed onboarding, Roadmaps →
"Plan your next roadmap" → fill deadline + purpose → **Continue** advances to step 2 (URL stays
`/onboarding/2?new=1`), through to preview, and Finish returns to `/roadmaps` (draft saved if a plan
is active, or the new plan started if none active).

#### Rollback

Revert the listed files; delete `useOnboardingNavigate.ts`. Onboarding returns to dropping the param.

#### Notes (filled in during implementation)

<empty>

---

### Phase B: Historical roadmap opens as a closable route view (`/roadmap?roadmap=...`)

**Status:** ☐ Not started
**Depends on:** none (independent of Phase A; can be done in parallel)
**Estimated scope:** ~3 files, ~60 lines

#### Codebase state assumed at start

`pages/Roadmap.tsx` renders `<RoadmapCalendar />` (no props). `RoadmapCalendar` accepts
`{ roadmapCreatedAt?, readOnly? }` and the back link is gated on `!readOnly`. `Roadmaps.tsx` selects
history via `useState selectedCreatedAt` and renders an inline read-only calendar (lines ~99, 319–336).

```bash
cd apps/app
grep -n "RoadmapCalendar" src/pages/Roadmap.tsx                 # expect props-less render
grep -n "selectedCreatedAt\|roadmaps-readonly" src/pages/Roadmaps.tsx
grep -n "&larr; Roadmaps\|!readOnly" src/roadmap/RoadmapCalendar.tsx
```

#### Steps

1. **`pages/Roadmap.tsx`** — read the `roadmap` search param and pass through (D-02):

   ```tsx
   import { useSearchParams } from 'react-router-dom'
   import { RoadmapCalendar } from '../roadmap/RoadmapCalendar'

   export function Roadmap() {
     const [params] = useSearchParams()
     const roadmapCreatedAt = params.get('roadmap')
     return roadmapCreatedAt
       ? <RoadmapCalendar roadmapCreatedAt={roadmapCreatedAt} readOnly />
       : <RoadmapCalendar />
   }
   ```

2. **`RoadmapCalendar.tsx`** — ensure a "← Roadmaps" back link is shown for the read-only historical
   route view (it currently renders only when `!readOnly`). Add a prop or render condition so the back
   link appears when `roadmapCreatedAt` is set (history detail) as well as when `!readOnly` (active).
   Simplest: render the back link when `readOnly ? roadmapCreatedAt != null : true`. Confirm the link
   is `<Link to="/roadmaps">` (no `/study`). Browser Back also closes the view since it is now a real
   navigation.

3. **`pages/Roadmaps.tsx`** — replace inline selection with navigation (D-02):
   - In `HistoryRows`, render each row as `<Link to={`/roadmap?roadmap=${encodeURIComponent(entry.roadmapCreatedAt)}`}>`
     (keep the existing row markup/classes; a `Link` styled as the row, or wrap the row). Drop the
     `onSelect`/`selectedCreatedAt`/`data-selected` plumbing.
   - Remove `selectedCreatedAt` state, `selectedEntry`, and the inline `<section className="roadmaps-readonly">`
     `RoadmapCalendar` block (lines ~328–335). Remove the now-unused `RoadmapCalendar` import if nothing
     else uses it in this file.
   - The `roadmaps-layout`/`roadmaps-groups` two-column wrapper can collapse to a single column since
     there is no inline detail anymore (adjust `roadmap.css` only if it leaves an empty column gap).

#### Tests

- `pages/Roadmaps.test.tsx`: clicking a history row navigates to `/roadmap?roadmap=<createdAt>`
  (assert via a memory router location), and no inline read-only calendar renders in the dashboard.
- Optionally a `pages/Roadmap.test.tsx`: with `?roadmap=<id>` renders the calendar in read-only mode
  for that entry and shows the "← Roadmaps" back link.
- Run (Node ≥ 20): `pnpm --filter app test -- Roadmaps Roadmap`

#### Verification (DONE)

```bash
cd apps/app
pnpm --filter app test -- Roadmaps Roadmap   # expect green
pnpm --filter app typecheck && pnpm lint
```

Manual smoke: click a History entry → URL becomes `/study/roadmap?roadmap=...`, read-only calendar
shows, "← Roadmaps" link and browser Back both return to `/roadmaps` (no refresh needed).

#### Rollback

Revert the three files; the inline-selection behavior returns.

#### Notes (filled in during implementation)

<empty>

---

### Phase C: Dashboard layout polish — DEFERRED (UI handled holistically later)

**Status:** 🛑 Deferred by Rohit (2026-06-27): "whole thing feels plain — we will tackle UI as a whole later, focus on bugs."
**Depends on:** a future dedicated UI/design pass (out of this fix plan's scope)
**Estimated scope:** TBD

Not part of this plan's execution. The dashboard layout (and likely other screens) will get a single
holistic design pass later — a `design-critique` → restyle effort rather than a one-off patch here.
Do NOT make piecemeal layout edits while fixing Phases A/B.

---

## Open questions

- **OQ-01 (Phase C):** ✅ Resolved 2026-06-27 — Rohit: the dashboard "feels plain" overall; UI will
  be tackled holistically in a later dedicated design pass, not in this bug-fix plan. Phase C deferred.

## Out of scope

- The richer three-option replan scope-picker UI (issue 010).
- Any Dexie schema change (none needed).
- Hero stat-strip enrichment beyond what already ships.
