# VERIFICATION — Roadmaps dashboard

Round-trips between agents. **Planner** pre-fills acceptance criteria. **Developer (Codex/Sonnet)** fills the implementer report per phase. **Reviewer (Cowork)** fills findings by diffing the reported commit SHA against the criteria. A phase is done only when the reviewer marks it `✅ Verified`.

- Plan: [`PLAN.md`](./PLAN.md)
- Slug: `2026-06-26-roadmaps-dashboard`
- Step 0 baseline commit (planning docs): `4d3bca9` (native side fills after `docs(plan): add roadmaps-dashboard plan + verification`)

Status legend: `☐` pending · `✅` met · `❌` failed · `➖` n/a.

---

## Phase 1 — Typed events + in-place lifecycle identity

### Acceptance criteria (pre-filled)

- [ ] `RoadmapReplannedPayload` (extends created shape + `roadmapCreatedAt`) and `RoadmapEditedPayload` added to `sync/types.ts`; `pnpm --filter app typecheck` clean.
- [ ] `deriveRoadmapLifecycle` groups roadmap events by stable identity (`RoadmapCreated.createdAt`; `RoadmapReplanned.payload.roadmapCreatedAt` points back) and surfaces the **latest snapshot per identity**.
- [ ] A replan chain (`Created(A)` + `Replanned(roadmapCreatedAt=A)` ×2) collapses to **one** `active` entry whose `roadmapCreatedAt === A` and whose `payload` is the latest snapshot.
- [ ] Terminal event on the original identity (`MarkedComplete(roadmapCreatedAt=A)`) moves the collapsed entry to `completed`, not `active`.
- [ ] `superseded` no longer appears in the active/history derivation (removed or unused).
- [ ] New tests in `roadmapLifecycle.test.ts` green: chain collapse, terminal-on-original, two-distinct-roadmaps.
- [ ] No `SessionLogged` payload change; no Dexie schema bump.

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)

---

## Phase 2 — Session attribution by date window

### Acceptance criteria (pre-filled)

- [ ] `completedSlotCount` filters `SessionLogged` to those whose `date` is within the roadmap's `[startDate, deadline]` (inclusive, ISO-string compare).
- [ ] A session dated outside a roadmap's window does NOT count toward its `completedSlots`/`percentComplete`.
- [ ] Two historical roadmaps each count only their own window's sessions (frozen history).
- [ ] Active roadmap still shows live progress; `findRoadmap` semantics (latest = active) unchanged.
- [ ] Gap-sessions (outside any window) documented as global-stats-only (comment present).
- [ ] New window tests in `roadmapLifecycle.test.ts` green; typecheck clean.

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)

---

## Phase 3 — Re-entrant onboarding + nav/routing reshape

### Acceptance criteria (pre-filled)

- [ ] NavBar item points at `/roadmaps`, label "Roadmaps"; both `/roadmaps` and `/roadmap` highlight it (prefix match verified).
- [ ] `OnboardingGate` does NOT redirect to `/home` when in new-roadmap mode (`?new=1` or `state.newRoadmap`), even though `OnboardingCompleted` exists.
- [ ] First-run gating preserved: with no `OnboardingCompleted`, the gate behaves exactly as before.
- [ ] `Step3Preview.handleCommit` branches: new-mode + active → save draft, no `RoadmapCreated`/no second `OnboardingCompleted`, `navigate('/roadmaps')`.
- [ ] new-mode + no active → emit `RoadmapCreated` (no duplicate `OnboardingCompleted`), clear draft, `navigate('/roadmaps')`.
- [ ] first-run → unchanged emits + `navigate('/onboarding/4')`.
- [ ] `RoadmapCalendar` (non-readOnly) shows a "← Roadmaps" back link to `/roadmaps` (no `/study` in `to`).
- [ ] Onboarding/gate tests green for: new-mode opens despite completion, first-run still redirects, draft-vs-start branch behavior.

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)

---

## Phase 4 — Roadmaps dashboard

### Acceptance criteria (pre-filled)

- [ ] `roadmapDraft.ts::deriveRoadmapDraft` returns `null` when no `OnboardingCompleted`, or `stepReached <= 1`, or no `deadline`; returns a summary (title fallback "Untitled plan", correct `stepLabel`) otherwise.
- [ ] Dashboard renders three zones: Active hero (title, range, weeks, progress, actions Open / Edit & add / Close), Next-up draft, History (completed + abandoned rows → read-only calendar).
- [ ] Active hero shows progress and at least sessions + percent (richer stats per OQ-01 or follow-up filed).
- [ ] Draft card appears only after step 1 (D-12); shows "paused at step N · <label>"; lock note present when a plan is active.
- [ ] **Start plan** disabled while a plan is active; enabled only when none active (non-overlap, D-01/D-04); promotion routes through `/onboarding/<step>?new=1`, NOT a direct `RoadmapCreated` from the dashboard.
- [ ] Close (Complete/Abandon) goes through the shared resolve helper (same path as the calendar); on close with a draft, an inline "Ready to start <draft>?" prompt appears.
- [ ] Empty state ("Plan your next roadmap" → `/onboarding?new=1`) when no active plan and no draft.
- [ ] Read-only history detail unchanged (clicking a row opens `RoadmapCalendar readOnly`).
- [ ] Tests green: `roadmapDraft` thresholds, dashboard Start-disabled-while-active, draft-after-step-1, close→prompt; typecheck + lint clean.

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)

---

## Phase 5 — Deadline-passed banner

### Acceptance criteria (pre-filled)

- [ ] `useRoadmapEndedState` returns `ended === true` only for an active entry whose `deadline < today` with no terminal event; `false` for future-deadline or terminated plans.
- [ ] `RoadmapEndedBanner` is a non-dismissible (no close control) inline banner with exactly three actions: Mark complete, Extend deadline (→ `/replan`), Abandon.
- [ ] Banner mounted as the first child on Home (independent of `RecalibrationBanner`), only when ended.
- [ ] Dashboard active hero flips its pill to "● Ended — needs review" and surfaces the three actions when ended.
- [ ] Calendar (non-readOnly) shows the banner strip atop when ended.
- [ ] Mark complete / Abandon route through the shared resolve helper (same terminal events).
- [ ] Tests green: hook truth table (past/future/terminated), banner renders three actions + no dismiss; typecheck clean.

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)

---

## Phase 6 — Add-session quick-log + inline light edits

### Acceptance criteria (pre-filled)

- [ ] `logRoadmapEdit.ts` emits a `RoadmapEdited` event keyed to the active roadmap identity (`roadmapCreatedAt`) with the slot fields.
- [ ] Calendar day-tap (non-readOnly) opens a log action pre-filled with that day's date + slot material/title; emits `SessionLogged` that attributes by date window (D-06).
- [ ] Inline light edits (rename, move material, mark done, nudge minutes) emit `RoadmapEdited`; they are future-only (past/locked days not editable).
- [ ] Emitted `RoadmapEdited` is consumed as a `user-edited` pin by `mapToRegenerateRequest` (integration assertion).
- [ ] `readOnly` (history) mode renders NONE of the new edit/log affordances.
- [ ] No structural reflow happens here (that's `/replan`, Phase 7).
- [ ] Tests green: `logRoadmapEdit`, calendar log + rename, readOnly gating; typecheck clean.

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)

---

## Phase 7 — `/replan` preview-and-confirm + in-place commit

### Acceptance criteria (pre-filled)

- [ ] `parseRoadmapOutput` runtime-validates the regenerate response (shape check on `weeks[]`/`warnings`) and throws a typed error on malformed input instead of casting; no bad `RoadmapReplanned` is committed.
- [ ] `commitReplan.ts` emits exactly one `RoadmapReplanned` whose `roadmapCreatedAt === original active identity` and whose slots are the regenerated set.
- [ ] After commit, `deriveRoadmapLifecycle` shows ONE active entry with the new slots (in place, D-07) — not a new/superseded sibling.
- [ ] `/replan` renders a preview of the regenerated rest-of-plan (reusing Step3Preview presentation) + a pin summary ("N locked, M re-planned").
- [ ] Actions: Apply → commit + `navigate('/roadmap')`; Keep current → no commit.
- [ ] `ReplanStub` removed; `/replan` mounts `<Replan />`; the three existing entry points (calendar, Week, Home modal) all land on it.
- [ ] Extend-deadline intent (from Phase 5 banner) pre-fills a later deadline (per OQ-02 mechanism).
- [ ] Tests green: malformed→typed error/no commit, well-formed parse, `commitReplan` identity + one-active-after, `Replan` preview/apply/keep; typecheck + lint clean.
- [ ] Three-option scope picker explicitly NOT built here (remains issue 010).

### Implementer report (Developer fills)

- Files changed:
- Commit SHA:
- What was done:
- Deviations + why:
- Self-check vs criteria:

### Reviewer findings (Cowork fills)

- Per-criterion verdict:
- Issues:
- Required changes:
- **Status:** ☐ awaiting implementation

### Resolution (Developer fills on redo)
