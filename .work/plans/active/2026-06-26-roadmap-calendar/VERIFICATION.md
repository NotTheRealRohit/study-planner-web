# Verification — roadmap-calendar

Round-trip log between implementer (Codex/Sonnet) and reviewer (Cowork). One section per phase.
Per phase: implementer fills **Implementer report**; reviewer fills **Reviewer findings** after diffing the reported commit SHA against the acceptance criteria. A phase is done only at `✅ Verified`.

**Plan:** [`PLAN.md`](PLAN.md) · **Step 0 reminder:** commit the planning docs verbatim before any code, and commit each phase's status flip together with its code.

---

## Phase 1 — Pure per-slot status derivation (`packages/progress`)

### Acceptance criteria
- [ ] `deriveSlotStatuses(roadmap, sessions, today)` exists in `packages/progress/src/deriveSlotStatuses.ts`, exported from `index.ts`.
- [ ] Match rule is `session.date === slot.date && slot.candidateMaterialIds.includes(session.materialId)`; each session attributes to at most one slot.
- [ ] `done` = ≥1 attributed (with summed `loggedMinutes`); `pending` = future slot, no match; `skipped` = past slot, no match.
- [ ] Unattributed sessions are returned as `unplanned` (not dropped).
- [ ] `today` is passed in as an ISO string — no `new Date()` inside the pure function.
- [ ] Tests cover: single match, duplicate-same-day overflow→unplanned, past-no-match (skipped), future-no-match (pending), off-plan material, empty roadmap.
- [ ] fast-check property: every session appears exactly once across `slots[].sessionIds ∪ unplanned`.
- [ ] `pnpm --filter progress test` and typecheck pass.

### Implementer report
Status: ✅ Implemented, awaiting review. Commit: `c50ff53`.

Files changed:
- `packages/progress/src/deriveSlotStatuses.ts`
- `packages/progress/src/index.ts`
- `packages/progress/src/types.ts`
- `packages/progress/test/deriveSlotStatuses.test.ts`

What was done:
- Added pure `deriveSlotStatuses(roadmap, sessions, today)` with `done` / `pending` / `skipped` slot derivation and `unplanned` return for unattributed sessions.
- Implemented the date + material match rule, first available matching slot attribution, and one-time accounting for every session.
- Exported the helper and public types from `@study-tracker/progress`.
- Added unit coverage for single match, duplicate overflow to unplanned, skipped, pending, off-plan material, empty roadmap, all-done week, and a fast-check accounting property.

Deviation:
- Added `materialId?: string` to `SessionEvent`; existing app `SessionLogged` payloads already include `materialId`, but the progress package type did not expose it. The Phase 1 match rule requires this field.

Self-check vs criteria:
- `deriveSlotStatuses` exists and is exported.
- Match rule is date + candidate material id; sessions are assigned to at most one slot.
- Done / pending / skipped are derived from attribution and caller-provided ISO `today`.
- Unattributed sessions return as `unplanned`.
- No `new Date()` usage in the helper.
- Required examples and fast-check property are covered.
- `pnpm --filter progress test` and `pnpm --filter progress typecheck` pass. Both emitted the existing Node engine warning (`wanted >=20`, current `v18.19.0`) but completed successfully.

### Reviewer findings
_(per-criterion verdict · issues · required changes · status: ✅ Verified / 🔁 Changes requested)_

### Resolution
_(implementer fills on redo — loop until ✅ Verified)_

---

## Phase 2 — Read-only month calendar on `/roadmap` (desktop)

### Acceptance criteria
- [ ] `/study/roadmap` renders a month calendar grid for the month containing today, replacing the stub.
- [ ] Cells show status-colored chips (done/pending/skipped/unplanned) per the **D-14 contract**, using design tokens only (no raw hex).
- [ ] D-14 elevation applied: current-week row uses `--cal-week-band`; today's cell uses `--cal-today-fill` + a "Today" pill; out-of-month cells dimmed. No terracotta ring on today/this-week; rust appears only on `skipped`.
- [ ] New tokens `--cal-today-fill` + `--cal-week-band` added to `packages/design-tokens/src/tokens.css`.
- [ ] Each status chip pairs an icon with its color (ti-check / ti-clock / ti-x / ti-plus) — not color-only.
- [ ] Per-cell cap of 3 bubbles, then a `+N more` affordance (D-07).
- [ ] Header progress card shows logged / to-go / % from `useProgressSnapshot`.
- [ ] Legend is present with icon/shape redundancy (not color-only).
- [ ] Empty state renders when `findRoadmap` returns `null` (D-13), with a CTA to onboarding — no crash.
- [ ] Footer Mark-complete / Abandon and Edit / Replan render as disabled placeholders.
- [ ] `calendarModel.ts` is pure and unit-tested (grid boundaries + cell binding + material-title join).
- [ ] `e2e/roadmap.spec.ts` visual walkthrough started (D-15, written not run): screenshots `01-grid`, `02-status-colors` (asserts D-14), `03-empty`.
- [ ] `pnpm --filter app test`, typecheck, lint pass.

### Implementer report
Status: ✅ Implemented, awaiting review. Commit: pending.

Files changed:
- `apps/app/src/roadmap/calendarModel.ts`
- `apps/app/src/roadmap/calendarModel.test.ts`
- `apps/app/src/roadmap/statusStyles.ts`
- `apps/app/src/roadmap/CalendarCell.tsx`
- `apps/app/src/roadmap/RoadmapCalendar.tsx`
- `apps/app/src/roadmap/roadmap.css`
- `apps/app/src/pages/Roadmap.tsx`
- `apps/app/src/progress/mapEvents.ts`
- `packages/design-tokens/src/tokens.css`
- `e2e/roadmap.spec.ts`
- `packages/progress/eslint.config.js`
- `apps/app/src/components/BurnUpChart.tsx`
- `apps/app/supabase/functions/materials-metadata/handler.test.ts`

What was done:
- Replaced `/roadmap` stub with a read-only current-month calendar fed by the event log.
- Added pure `calendarModel` helpers for Monday-start month grids and binding derived slots/unplanned sessions to day cells.
- Added D-14 calendar tokens `--cal-today-fill` and `--cal-week-band`.
- Added status style mapping and icon-paired chips for done/planned/skipped/unplanned; rust is only used by skipped chips in the new roadmap UI.
- Added current-week band, filled today cell + Today pill, dimmed out-of-month cells, per-cell cap of 3 bubbles, `+N more`, legend, progress card, empty state, and disabled footer placeholders for Mark complete / Abandon / Edit / Replan.
- Added the Phase 2 Playwright visual walkthrough steps `01-grid`, `02-status-colors`, and `03-empty`; authored only, not executed.

Deviations:
- Added `apps/app/src/roadmap/roadmap.css` even though the file index did not list a CSS file; this keeps hover/media-query styling auditable and avoids inline CSS bloat.
- Updated `mapSessions` to include `materialId`; without this, real app sessions could not satisfy Phase 1's match rule.
- Fixed narrow pre-existing lint-gate blockers so `pnpm lint` can pass: added `packages/progress/eslint.config.js`, removed two stale disables for an uninstalled React-hooks rule, and removed one unused Deno-test type import.

Self-check vs criteria:
- `/study/roadmap` renders a month calendar instead of the stub.
- D-14 tokens and status chip classes are in place; source audit found no raw color literals in new roadmap UI files.
- Current-week, today, and out-of-month states are styled through tokens/classes.
- Status chips and legend pair color with `ti-*` icon metadata and inline SVG icons.
- Bubbles cap at 3 per cell with `+N more`.
- Progress card calls `useProgressSnapshot`; it falls back to event-derived totals while calibration is unavailable.
- Empty state renders for post-onboarding/no-roadmap state with an onboarding CTA.
- Footer placeholders render disabled.
- `calendarModel.ts` is pure and unit-tested.
- `e2e/roadmap.spec.ts` contains the required write-only walkthrough screenshots.
- Verification passed under Node `v22.17.1`: `pnpm --filter app test`, `pnpm --filter app typecheck`, `pnpm --filter progress test`, `pnpm --filter progress typecheck`, and `pnpm lint`. Running the app tests under the default Node `v18.19.0` failed before tests due jsdom/html-encoding-sniffer ESM compatibility, matching the repo's `node >=20` engine requirement.

### Reviewer findings

### Resolution

---

## Phase 3 — Month navigation (prev/next/today, clamp, slide)

### Acceptance criteria
- [ ] Prev/next + Today controls change the visible month; default is the month containing today.
- [ ] Prev/next are clamped to the roadmap's start/end months (no empty paging).
- [ ] Month change animates with a horizontal slide (~180ms); `prefers-reduced-motion` respected.
- [ ] Deadline day is visually marked.
- [ ] Clamp bounds unit-tested; walkthrough extended (write only) with screenshots `04-next-month`, `05-prev-month`, `06-today-reset`; deadline-day marker asserted.
- [ ] `pnpm --filter app test` + typecheck pass.

### Implementer report

### Reviewer findings

### Resolution

---

## Phase 4 — Session-detail modal + day modal (desktop)

### Acceptance criteria
- [ ] `SessionDetailModal` reuses the onboarding/Recalibration modal structure.
- [ ] Modal renders eyebrow (date), title, status pill, body (logged vs planned, material link), and a status-dependent action label (done/pending/skipped/unplanned).
- [ ] Clicking a bubble opens the modal for that session; `+N more` opens the day list.
- [ ] Modal close works; component unit-tested for status→pill/action mapping.
- [ ] Walkthrough extended (write only): screenshots `07-hover-expand`, `08-modal-done`, `09-modal-pending`, `10-day-modal`; modal open/close asserted at each step.
- [ ] `pnpm --filter app test` + typecheck pass.

### Implementer report

### Reviewer findings

### Resolution

---

## Phase 5 — Mobile responsive (dots + day sheet + swipe)

### Acceptance criteria
- [ ] Below the width threshold, bubbles render as status dots with a count badge when >1; hover-expand disabled.
- [ ] Tapping a day opens a bottom sheet (normal-flow overlay, never `position: fixed`) listing that day's sessions.
- [ ] Sheet rows open the session-detail modal.
- [ ] Left/right swipe changes months on mobile (reuses the slide).
- [ ] Walkthrough extended (write only) with a mobile-viewport project: screenshots `11-mobile-dots`, `12-day-sheet`, `13-mobile-modal`, `14-mobile-month-change`.
- [ ] `pnpm --filter app test` + typecheck pass.

### Implementer report

### Reviewer findings

### Resolution

---

## Phase 6 — Mark complete / abandon events + `/roadmaps` history

### Acceptance criteria
- [ ] `RoadmapMarkedComplete` / `RoadmapMarkedAbandoned` payload types added to `sync/types.ts` (`{ roadmapCreatedAt, resolvedAt, reason? }`).
- [ ] Detail footer buttons emit the events via `logEvent` (abandon behind a confirm), then route to `/roadmaps`.
- [ ] `roadmapLifecycle.ts` is pure and classifies Active / Completed / Abandoned via latest matching terminal event by `roadmapCreatedAt`; replan supersedes.
- [ ] `/study/roadmaps` renders the three groups + the empty state (italic Fraunces) + "Start a new roadmap" → onboarding.
- [ ] Clicking an entry opens the detail calendar in read-only mode.
- [ ] `roadmapLifecycle.test.ts` covers active/completed/abandoned/replan-supersede/multi-roadmap.
- [ ] Walkthrough extended (write only): screenshots `15-complete-confirm`, `16-history-completed`, `17-history-abandoned`, `18-history-empty`, `19-history-readonly`.
- [ ] `pnpm --filter app test`, typecheck, lint pass.

### Implementer report

### Reviewer findings

### Resolution

---

## Phase 7 — Replan interface seam routed to Python (stubbed UI)

### Acceptance criteria
- [ ] `postRoadmapRegenerate` added to `intelligenceClient.ts`, POSTing to `${BASE}/v1/roadmap/regenerate`, mirroring `postCalibration` (auth header, AbortController timeout, retry/backoff, typed errors).
- [ ] Error normalization follows rule `fetch-typed-error-normalization` (normalize by `name`, not `instanceof Error`).
- [ ] `mapToRegenerateRequest.ts` (pure) builds the exact Python request: `materials[{id,title,totalMinutes,role,additionOrder}]`, `weeks/startDate/selectedStudyDays/weekdayHours/weekendHours`, and `pins[]` with `reason ∈ {completed,today,user-edited}`.
- [ ] `replanRoadmap(events, opts)` boundary calls map→post→parse to `RoadmapOutput`, with an internal TS `offlineReplan` fallback behind the same signature (not UI-wired).
- [ ] `/replan` route reserved in `App.tsx` (under ProtectedRoute + RequireOnboarding; no `/study` in the path) rendering a clear stub.
- [ ] Tests: `mapToRegenerateRequest` field-mapping + pin construction; `postRoadmapRegenerate` 401/≥500/timeout(real `Error` subclass named `AbortError`)/network-`TypeError` exhaustion.
- [ ] Walkthrough extended (write only): screenshot `20-replan-stub`; `/study/replan` resolves under ProtectedRoute + RequireOnboarding with no double `/study` prefix.
- [ ] `pnpm --filter app test`, typecheck, lint pass.

### Implementer report

### Reviewer findings

### Resolution

---

## Cross-cutting checks (reviewer, at plan completion)
- [ ] No `/study` prefix introduced in any `to`/route path (rule `react-router-v7-basename`).
- [ ] No raw hex colors in new UI; design tokens only, incl. the two new `--cal-*` tokens (rule `form-design-spacing`, D-14).
- [ ] D-14 visual contract honored everywhere: rust only on `skipped`; today = `--cal-today-fill`; current week = `--cal-week-band`; every status chip is icon+color.
- [ ] `e2e/roadmap.spec.ts` is one ordered visual walkthrough (steps `01`–`20`) writing screenshots to `e2e/__screens__/roadmap/`; authored but not executed (environment constraint, D-15).
- [ ] No Dexie schema change was needed (events are additive); if any table was touched, it versioned up (rule `dexie-schema-migration`).
- [ ] E2E specs written but not executed (environment constraint).
- [ ] `.work/STATUS.md` row updated to reflect the shipped state.
