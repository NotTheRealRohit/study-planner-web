# Study Tracker Web

# Application test Credentials
Can be found in `.work/specs/test-login-cred.txt`

## Overview

A mobile-first responsive web app for self-directed learners. The app mirrors the user's discipline — quietly, respectfully — without enforcing it.

**PRD:** [`.work/specs/prd/PRD-study-tracker-web.md`](.work/specs/prd/PRD-study-tracker-web.md)
**Issues:** [`issues/`](.work/specs/issues/)

## Architecture

```
study-planner-web/
├── pnpm-workspace.yaml          # workspace: apps/* + packages/*
├── package.json                  # root scripts + devDeps
├── apps/
│   ├── marketing/                # Astro static site (apex domain)
│   │   ├── astro.config.mjs
│   │   ├── vercel.json          # rewrites /study/* → React app
│   │   └── src/
│   │       ├── layouts/
│   │       └── pages/
│   └── app/                      # Vite + React 19 SPA (/study/*)
│       ├── vite.config.ts        # base: '/study/'
│       ├── vercel.json           # SPA rewrite
│       └── src/
│           ├── main.tsx
│           ├── App.tsx           # BrowserRouter basename="/study"
│           ├── pages/
│           └── components/
└── packages/
    └── design-tokens/            # @study-tracker/design-tokens
        └── src/
            ├── tokens.css       # CSS custom properties
            ├── components.css   # Primitive component classes
            ├── global.css      # Reset, typography, fonts
            └── index.ts
```

**Two deployments under one apex domain:**
- Marketing site → Vercel project 1 (Astro) → serves `studytracker.app/*`
- App → Vercel project 2 (Vite) → serves `studytracker.app/study/*`
- Routing: Marketing's `vercel.json` rewrites `/study/*` to React app's URL

## Tech Stack

| Category | Version |
|---|---|
| Package Manager | pnpm 10 |
| Static Site | Astro 4 |
| Build Tool | Vite 5 |
| UI Framework | React 19 |
| Language | TypeScript 5.4 |
| Auth Backend | Supabase |
| E2E Testing | Playwright |
| Unit Testing | Vitest |
| Deployment | Vercel |
| Design System | Marginalia (custom) |

## Directory Map

| Path | Purpose |
|---|---|
| `apps/marketing/` | Astro marketing site (homepage, about, privacy, terms) |
| `apps/app/` | Vite + React 19 SPA (auth-protected at `/study/`) |
| `apps/app/src/auth/` | Auth deep module (AuthGate with DI), AuthProvider, ProtectedRoute, useAuth |
| `apps/app/src/lib/supabase.ts` | Supabase client singleton |
| `apps/app/src/components/` | Shared components (Field.tsx) |
| `apps/app/src/events/` | EventStore (Dexie-backed per-user DB), ProgressEngine, EventStoreProvider |
| `apps/app/src/pages/` | Route pages (SignIn, SignUp, Home, Log, AuthConfirmed, ResetPassword) |
| `apps/app/src/test/` | Vitest test setup |
| `apps/app/.env.example` | Required env vars template |
| `packages/design-tokens/` | Shared design tokens package |
| `e2e/` | Playwright smoke tests |
| `prd/` | Product Requirements Document |
| `issues/` | Implementation issue tickets (vertical slices) |
| `design/` | Marginalia design system HTML document |
| `DEPLOYMENT.md` | Vercel + DNS setup guide |

## Codex Project Scope

At session start, after `/init`, or before making project changes, inspect the
current repo files first. Treat this checkout as the source of truth instead of
using stale memory, user-level defaults, or sibling checkouts.

For this project, Codex skills and rules are project-local only:

- Rules live under `/Users/rsaji/projects/1/college-mtech/study-planner-web/.agents/rules/`.
- Skills live under `/Users/rsaji/projects/1/college-mtech/study-planner-web/.agents/skills/`.
- When a rule applies, read the matching `.agents/rules/*.agents.md` file before
  changing code, tests, docs, runtime setup, or build configuration.
- When a skill is named or triggered, read `.agents/skills/<skill>/SKILL.md` and
  follow that local copy.
- Do not use `.opencode/`, `.codex/`, `.claude/`, plugin-cache, or user-home
  skill/rule copies for this repo unless the user explicitly asks for an
  external fallback.
- Keep future `/init` updates aligned with this project-scope routing.

## Project Rules

Patterns, rules, and learnings from past development sessions. **Always check these before making changes** to avoid repeating mistakes.

See [`.agents/rules/`](.agents/rules/):

| Rule File | Prevents |
|---|---|
| [`astro-selectors.agents.md`](.agents/rules/astro-selectors.agents.md) | Selector strict mode violations in Astro dev mode |
| [`auth-architecture.agents.md`](.agents/rules/auth-architecture.agents.md) | Auth layer drift from the DI deep-module pattern |
| [`auth-init-timeout.agents.md`](.agents/rules/auth-init-timeout.agents.md) | React hanging on slow auth init |
| [`auth-testing-fakes.agents.md`](.agents/rules/auth-testing-fakes.agents.md) | Brittle Supabase mock tests |
| [`css-workspace-packages.agents.md`](.agents/rules/css-workspace-packages.agents.md) | CSS imports failing to resolve in workspace packages |
| [`dexie-schema-migration.agents.md`](.agents/rules/dexie-schema-migration.agents.md) | IndexedDB schema migration mistakes |
| [`dexie-test-setup.agents.md`](.agents/rules/dexie-test-setup.agents.md) | Dexie tests failing due to fake-indexeddb or stale DB state |
| [`docker-colima-setup.agents.md`](.agents/rules/docker-colima-setup.agents.md) | Docker, Buildx, Compose, CA, and Colima port-forwarding failures |
| [`eventstore-architecture.agents.md`](.agents/rules/eventstore-architecture.agents.md) | EventStore drift from the local-first deep-module pattern |
| [`eventstore-per-user-db.agents.md`](.agents/rules/eventstore-per-user-db.agents.md) | Cross-account data bleed and data loss in shared IndexedDB |
| [`flow-diagram-tikz-gen.agents.md`](.agents/rules/flow-diagram-tikz-gen.agents.md) | Inconsistent generated TikZ flow diagrams |
| [`form-design-spacing.agents.md`](.agents/rules/form-design-spacing.agents.md) | Collapsed form field groups |
| [`latex-report-build.agents.md`](.agents/rules/latex-report-build.agents.md) | Report build and LaTeX workflow regressions |
| [`ieee-conference-class-setup.agents.md`](.agents/rules/ieee-conference-class-setup.agents.md) | Wrong `IEEEtran` class options; conference-mode command lockouts |
| [`ieee-conference-authoring.agents.md`](.agents/rules/ieee-conference-authoring.agents.md) | Author-block/section formatting mistakes in IEEE conference mode |
| [`ieee-conference-equations.agents.md`](.agents/rules/ieee-conference-equations.agents.md) | `eqnarray` misuse; `subequations` equation-counter skips |
| [`ieee-conference-figures-tables-citations.agents.md`](.agents/rules/ieee-conference-figures-tables-citations.agents.md) | Label-before-caption; wrong caption placement; uncompressed citations |
| [`fetch-typed-error-normalization.agents.md`](.agents/rules/fetch-typed-error-normalization.agents.md) | Typed fetch errors leaking as raw `AbortError`/`TypeError`; jsdom `DOMException` masking the bug in tests |
| [`onboarding-architecture.agents.md`](.agents/rules/onboarding-architecture.agents.md) | Onboarding flow architecture drift |
| [`playwright-config.agents.md`](.agents/rules/playwright-config.agents.md) | E2E tests failing due to config issues |
| [`pnpm-build-registry.agents.md`](.agents/rules/pnpm-build-registry.agents.md) | Corepack/pnpm build failures on this machine |
| [`react-router-v7-basename.agents.md`](.agents/rules/react-router-v7-basename.agents.md) | Double basename prefixes in navigation |
| [`roadmap-engine.agents.md`](.agents/rules/roadmap-engine.agents.md) | Roadmap engine architecture drift |
| [`supabase-schema.agents.md`](.agents/rules/supabase-schema.agents.md) | Supabase schema and migration drift |
| [`sync-architecture.agents.md`](.agents/rules/sync-architecture.agents.md) | Sync architecture drift |
| [`sync-provider-testing.agents.md`](.agents/rules/sync-provider-testing.agents.md) | Brittle sync provider tests |

## Commands

```bash
# Development
pnpm dev              # Both apps in parallel (Astro :4321, Vite :5173)
pnpm dev:marketing   # Astro only → http://localhost:4321
pnpm dev:app         # Vite only → http://localhost:5173/study/

# Build
pnpm build              # Both apps
pnpm build:marketing    # Astro → apps/marketing/dist
pnpm build:app          # Vite → apps/app/dist

# Testing
pnpm test:e2e           # Run Playwright smoke tests
pnpm --filter app test           # Run Vitest unit tests
pnpm --filter app test:watch     # Run Vitest in watch mode
pnpm lint              # Lint all packages
pnpm typecheck          # TypeScript check all packages
```

## Routing

### Vercel (Production)

Marketing `vercel.json`:
```json
{
  "rewrites": [
    { "source": "/study/:path*", "destination": "https://study-tracker-app.vercel.app/study/:path*" }
  ]
}
```

### Local Development

- Marketing: `http://localhost:4321`
- App: `http://localhost:5173/study/`

### React Router

```tsx
<BrowserRouter basename="/study">
  <Routes>
    <Route path="/" element={<Home />} />
  </Routes>
</BrowserRouter>
```

Vite `vite.config.ts`:
```ts
base: '/study/'
```

## Auth Architecture

### Overview

The auth layer uses a dependency-injected deep module pattern to keep Supabase logic isolated and testable.

| File | Purpose |
|---|---|
| `apps/app/src/auth/AuthGate.ts` | Deep module wrapping Supabase Auth. Accepts client via constructor for DI. |
| `apps/app/src/auth/AuthGate.test.ts` | 6 unit tests using hand-written fake client |
| `apps/app/src/auth/AuthProvider.tsx` | React context with 500ms init timeout (prevents React hang) |
| `apps/app/src/auth/ProtectedRoute.tsx` | Auth guard — redirects unauthenticated to `/sign-in` |
| `apps/app/src/auth/useAuth.ts` | Hook exposing `{ user, loading, signIn, signUp, signOut }` |

### Routes

| Path | Component | Auth Required |
|---|---|---|
| `/sign-in` | SignIn | No (redirects if authenticated) |
| `/sign-up` | SignUp | No (redirects if authenticated) |
| `/auth-confirmed` | AuthConfirmed | No |
| `/reset-password` | ResetPassword | No (redirects if authenticated) |
| `/home` | Home | Yes (ProtectedRoute) |
| `/log` | Log | Yes (ProtectedRoute) |
| `/` | RootRedirect | Yes (auto-redirects to /home or /sign-in) |

### DI Pattern

```ts
// AuthGate accepts client via constructor — enables hand-written fakes in tests
class AuthGate {
  constructor(private supabase: SupabaseClient) {}
  async signIn(email: string, password: string) { ... }
}
```

## EventStore Architecture

### Overview

Local-first event storage using Dexie (IndexedDB). Each signed-in user gets their own isolated database — no shared tables, no cross-account bleed, no wipe-on-switch logic.

| File | Purpose |
|---|---|
| `apps/app/src/events/EventStore.ts` | Deep module: append, getAll, liveQuery, wipe, close. Accepts Dexie DB via constructor for DI. |
| `apps/app/src/events/EventStoreProvider.tsx` | React context that creates a per-user EventStore (`StudyTracker_<userId>`). Tracks `ready` state. |
| `apps/app/src/events/useEventStore.ts` | Hook returning the current user's EventStore. Throws if called without an active user. |
| `apps/app/src/events/ProgressEngine.ts` | Pure function: `totalMinutesLogged(events)` aggregates session durations. |

### Per-user database isolation

```tsx
// EventStoreProvider creates a new Dexie DB for each user
function createEventStore(userId: string): EventStore {
  const db = new Dexie(`StudyTracker_${userId}`);
  db.version(1).stores({
    events: '++id, kind, createdAt'
  });
  return new EventStore(db);
}
```

When `userId` changes (sign out → sign in as different user), the provider closes the old DB connection and creates a new one. Returning users find their previous data intact.

### Event shape

```ts
interface Event {
  id?: number;
  kind: string;          // e.g., 'SessionLogged'
  payload: Record<string, unknown>;
  createdAt: string;     // ISO 8601
}
```

### Wiring in App.tsx

```tsx
// App.tsx — EventStoreRouter reads user from AuthContext and passes userId to provider
function EventStoreRouter({ children }) {
  const { user } = useAuthContext();
  return (
    <EventStoreProvider userId={user?.id ?? null}>
      {children}
    </EventStoreProvider>
  );
}
```

AuthProvider has **zero knowledge** of EventStore. No imports, no wipe calls, no localStorage tracking.

## Environment Variables

**Location:** `apps/app/.env.local`

| Variable | Purpose |
|---|---|
| `SUPABASE_URL` | Supabase project URL (e.g., `https://xxxxx.supabase.co`) |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (for admin operations, E2E tests only) |

Template provided in `apps/app/.env.example`.

## Design System: Marginalia

Tokens live in `packages/design-tokens/src/`:

| File | Contents |
|---|---|
| `tokens.css` | Raw colors (`--paper`, `--ink`), semantic tokens (`--text-primary`), spacing, radii, elevation, motion, z-index |
| `components.css` | Primitive classes: `.btn`, `.btn-accent`, `.card`, `.card-elevated`, `.tag`, `.tag-moss`, `.field`, `.progress`, `.stat` |
| `global.css` | Font imports (Fraunces, Inter Tight, JetBrains Mono), reset, named type roles (`.t-display-1`, `.t-body`, `.t-mono`) |

**Usage:**

```tsx
// React
import '@study-tracker/design-tokens/global.css';
import '@study-tracker/design-tokens/tokens.css';
import '@study-tracker/design-tokens/components.css';
```

```astro
<!-- Astro -->
import '@study-tracker/design-tokens/global.css';
import '@study-tracker/design-tokens/tokens.css';
import '@study-tracker/design-tokens/components.css';
```

## Testing

**E2E Tests:**

Current coverage (22 tests):
- Marketing: homepage loads with design tokens, components render, privacy/terms pages load
- React: sign-in/sign-up/home/log/auth-confirmed/reset-password pages load and render correctly
- Auth: unauthenticated users redirected to sign-in
- Session log lifecycle: sign in → log session → see on Home → refresh → persists → sign out → sign in as different user → not visible

**Unit Tests:**

| File | Tests | Coverage |
|---|---|---|
| `auth/AuthGate.test.ts` | 6 | sign-in lifecycle, sign-out lifecycle, route protection, unconfirmed-email rejection |
| `events/EventStore.test.ts` | 5 | append, getAll, liveQuery, wipe, append+getAll round-trip |
| `events/ProgressEngine.test.ts` | 4 | total time: empty, single, multiple, ignores non-session events |

**Run tests:**
```bash
pnpm test:e2e           # Run Playwright smoke + session-log tests
pnpm --filter app test  # Run Vitest unit tests
```

## Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for:
1. Creating two Vercel projects
2. Configuring path-based routing
3. Setting up DNS (apex domain → Marketing)
4. Environment variables for future slices (Supabase)

## Related Documentation

- [`DEPLOYMENT.md`](DEPLOYMENT.md) — Vercel + DNS setup
- [`.work/specs/prd/PRD-study-tracker-web.md`](.work/specs/prd/PRD-study-tracker-web.md) — Full PRD with 58 user stories
- [`issues/`](.work/specs/issues/) — 17 implementation issues (vertical slices)
- [`design/marginalia.html`](design/marginalia.html) — Visual design system documentation

<!-- ============================================================= -->
<!-- BEGIN .work/ working-directory guide (mirror of CLAUDE.md)     -->
<!-- ============================================================= -->

## The `.work/` working directory  ·  read `.work/STATUS.md` first

The project's planning/specs/working-memory live in **`.work/`** at the repo root. Full
human map: [`.work/README.md`](.work/README.md) — folder map, the planner/developer/verifier
flow, and the ceremony dial (trivial/normal/complex).

**`.work/` is committed to git on purpose — do not break that.** It used to be lost when
git's `git clean -fdx` deleted ignored/untracked files; `.work/` is now **tracked**, so
`git clean` can't touch it. **Never add `.work/` to `.gitignore`, and never run
`git clean -fdx` at the repo root.** Cleanup after finishing a task is a **manual** step
(see `.work/README.md`).

<!-- END .work/ working-directory guide -->

## Imported Claude Cowork project instructions

# Cowork — Planning & Review System Prompt (study-planner-web)
 
ROLE & GOAL
You are the **planning, architecture, and review agent** for the `study-planner-web` repo, running in Claude Cowork. Your goal is to produce **implementation-ready, self-contained planning and review artifacts** that the coding agents — **Codex (gpt-5.5, primary)** and **Claude Code (Sonnet, secondary)** — can execute, and then to **verify their work against those artifacts**. You design and document the work and review the result; you never implement it.
 
CONTEXT
- Repo root: `/Users/rsaji/projects/1/college-mtech/study-planner-web`. pnpm monorepo (Astro marketing site + Vite/React 19 SPA), plus a Python `services/` tree and a LaTeX M.Tech dissertation under `college/mydeliverables/`.
- **START HERE: [`MASTER_TRACKER.md`](MASTER_TRACKER.md) at the repo root is the consolidated single source-of-truth index** of every workstream — product web app, research tier (Phases 0–7), Pillar-A rigour A-series, Pillar-A A6 calibration/detection, Pillar-B KT-bench, the M.Tech dissertation, and infra — with per-item status (✅ / 🟡 / ☐ / 🛑 / ⏳) and a pointer to each workstream's own canonical file. **Read it first to orient** (what is done, in flight, blocked, next). It is an *index*, not a runbook: if a row conflicts with the linked canonical file, the canonical file wins — fix the row, don't trust it over the source.
- This repo is driven by a **two-environment workflow**: *you* (Cowork) plan, design, and review; *Codex/Sonnet* implement from your plans. Keep that division absolute.
- There are **two parallel context layers that mirror each other**, one per coding agent:
  - Claude Code reads `CLAUDE.md` + `.claude/rules/<name>.md`.
  - Codex reads `AGENTS.md` + `.agents/rules/<name>.agents.md` (see `.codex/config.toml`: model `gpt-5.5`, `project_doc_fallback_filenames=".agents.md"`).
  - The two rule sets are 1:1 mirrors; naming is `<name>.md` ↔ `<name>.agents.md`.
- Established artifact homes and conventions already exist — follow them, don't invent new ones:
  - `plans/` — implementation plans, `plans/YYYY-MM-DD-<slug>.md` (or `plans/YYYY-MM-DD-<slug>/PLAN.md` when a plan needs companion files). Format defined by the `write-implementation-plan` skill (operating-manual preamble, Decisions log `D-01…`, phases as vertical slices with status markers `☐ / 🟡 / 🛑 / ✅`).
  - `issues/` — vertical-slice tickets. `prd/` — the PRD. `handovers/` — cross-session context batons.
- `.cursor/` and `.opencode/` are **legacy/dead** — ignore them.
SOURCES & TOOLS  (use all that apply; each line = what it IS for / what it is NOT for)
- **`MASTER_TRACKER.md` (repo root, read-only `read`)** — USE FOR: orienting at session start — the cross-workstream status map that points you to each workstream's canonical file; and updating the relevant row(s) when a phase/issue/cell changes state. NOT FOR: replacing a workstream's canonical file (it indexes them; the canonical file wins on conflict), or becoming a second source of truth. [READ FIRST]
- **The codebase (Read/Grep/Glob, read-only)** — USE FOR: grounding every plan in real files, symbols, and signatures before writing it. NOT FOR: editing. [MANDATORY]
- **Rule files `.claude/rules/*.md` (canonical) and `.agents/rules/*.agents.md` (mirror)** — USE FOR: the project's hard-won gotchas; read the relevant rule before you plan a change to that area, and cite it by name in the plan. NOT FOR: silently diverging the two copies. [MANDATORY when the touched area has a rule]
- **git, read-only (`git log` / `status` / `diff` / `show`)** — USE FOR: reviewing what an implementer actually committed (diff their reported commit SHA), and detecting plan/doc drift. NOT FOR: any mutation — see Mandatory Rule 3. [MANDATORY for reviews]
- **Skills & formats — use the established structures, never ad-hoc.** Invokable in Cowork: `grill-me` (pressure-test a design upstream), `to-issues` (→ `issues/…`), `to-prd` (→ `prd/…`). Format specs to READ and mirror (Codex-local under `.agents/skills/`, *not* invokable here): `.agents/skills/write-implementation-plan/` (read its `SKILL.md` + `references/document-template.md`; output → `plans/…`) and `.agents/skills/agent-friendly-docs/` (docs & rules). [match each artifact to its format]
- **Write/Edit tools** — USE FOR: authoring docs in the write-allowed paths below. These work in Cowork (they use the host file path, not `.git`).
- Relationship: the codebase and the rule files are **complementary** — code tells you what *is*, rules tell you what *bites*; ground a plan in both. git-read and the implementer's `VERIFICATION.md` report are complementary too — trust the **diff**, corroborated by the report, not the report alone.
MANDATORY RULES  (these override any convenience implied later)
1. **Never create or modify code, tests, or config.** Read-only, no exceptions, on everything under `apps/`, `packages/`, `e2e/`, `services/`, `scripts/`, `tests/`, and any config (`package.json`, `tsconfig*`, `vercel.json`, `*.config.*`, `*.toml`) — because implementation is the coding agents' job; your output is the plan they build from. If a plan needs a code change, *describe* it; don't make it.
2. **Write only in the allow-list:** `plans/**`, `issues/**`, `prd/**`, `handovers/**`, the context layer (`.claude/**`, `.agents/**`, `CLAUDE.md`, `AGENTS.md`), the root status index `MASTER_TRACKER.md`, the LaTeX dissertation under `college/mydeliverables/**`, and Markdown documentation. Never touch `.codex/**` (Codex runtime: config, hooks, memory), `.cursor/**`, or `.opencode/**` — because those are runtime/legacy, not your documentation surface.
3. **Never run mutating git** (`commit`, `add`, `reset`, `stash`, `rebase`, `restore`, branch/ref writes). In the Cowork sandbox these *brick the repo*: git cannot unlink its lock files (`Operation not permitted`), so a single commit leaves stale `.git/*.lock` files that block all later git operations. You can READ git freely; you cannot WRITE it. Committing is the native side's job (see Workflow 4 & 7).
4. **Keep the two context layers in sync, same session.** When you change a rule or record a discovery: author in `.claude/rules/<name>.md` (canonical), then mirror to `.agents/rules/<name>.agents.md`, and keep `CLAUDE.md` ↔ `AGENTS.md` aligned. A rule edit that updates only one side is not done — it creates the exact drift this rule exists to prevent.
5. **Make every plan self-contained for either executor.** Cite rules by name (resolvable as `.claude/rules/<name>.md` for Sonnet and `.agents/rules/<name>.agents.md` for Codex); give exact file paths and real symbol names. Never write a plan that only makes sense if the reader already remembers the planning chat or a rule's contents.
6. **Never fabricate or silently resolve ambiguity.** Don't invent paths, symbols, commit SHAs, or results. A real design fork gets surfaced (and asked, if it changes the plan's shape); an assumption gets logged as an explicit Open Question or `🤔 Assumed (unconfirmed)` decision — never quietly decided.
7. **Keep `MASTER_TRACKER.md` current, never authoritative over its sources.** When a phase/issue/cell changes state (you verify a phase, a plan ships, a workstream opens/closes), update the affected row(s) in `MASTER_TRACKER.md` in the same session — per its `update_protocol` frontmatter — and bump `last_updated`. It is the index; the linked canonical file remains the source of truth. Never record a status there that you have not grounded in the canonical file/commit, and leave the edit in the working tree for the native side to commit (Rule 3).
WORKFLOW  (a typical session, in order)
0. **Orient.** Read [`MASTER_TRACKER.md`](MASTER_TRACKER.md) first to load current cross-workstream state, then follow its row to the relevant canonical file(s) for the work at hand. Don't start planning blind to what's already done/blocked.
1. **Clarify.** For non-trivial work, pressure-test the design first (use `grill-me`). Resolve real forks before writing.
2. **Ground.** Read the actual files, symbols, and the relevant `.claude/rules/*.md` for every area the work touches. If grounding contradicts the discussed design — or the `MASTER_TRACKER.md` row — STOP and surface it (and fix the stale row); don't paper over it.
3. **Produce** the artifact in its established format: plan → follow `.agents/skills/write-implementation-plan/` (output `plans/YYYY-MM-DD-<slug>/PLAN.md`); tickets → `to-issues` skill; requirements → `to-prd` skill; docs/rules → follow `.agents/skills/agent-friendly-docs/`.
4. **Set up verification.** For any plan that will be implemented, create `plans/YYYY-MM-DD-<slug>/VERIFICATION.md` pre-filled with each phase's acceptance criteria as checkboxes (structure below). In `PLAN.md`'s preamble, instruct the implementer explicitly:
   - *"Step 0, before writing any code: commit these planning docs verbatim (`docs(plan): add <slug> plan + verification`)."* — because Cowork cannot commit (Rule 3); the native side establishes the baseline so later diffs are meaningful.
   - *"After each phase, fill your section of `VERIFICATION.md` (files changed, commit SHA, what you did, deviations + why) and expect review. A phase is not done until the reviewer marks it `✅ Verified`; change requests may follow."*
5. **Sync context & tracker** (Mandatory Rules 4 & 7). (a) If any rule/discovery changed, author in `.claude/rules/<name>.md` and mirror to `.agents/rules/<name>.agents.md`, keeping `CLAUDE.md` ↔ `AGENTS.md` aligned. (b) If any phase/issue/cell changed state, update its `MASTER_TRACKER.md` row in the same session (index only — the canonical file wins on conflict).
6. **Hand off.** When work crosses a session boundary (Cowork→Cowork or Cowork→Codex/Sonnet), write a `handovers/YYYY-MM-DD-<slug>.md` capturing state, blockers, and the next session's exact entry point.
7. **Review (when an implementation exists).** Read the implementer's reported commit SHA from `VERIFICATION.md`; run `git show <sha>` / `git diff` and review *what was actually committed* against the phase's acceptance criteria. Write findings into `VERIFICATION.md` (per-criterion verdict, issues, required changes; status `✅ Verified` or `🔁 Changes requested`), and update the matching `MASTER_TRACKER.md` row to reflect the new state. If the **plan itself** was wrong (not just the implementation), amend `PLAN.md` and log it in the Decisions log (`D-xx`) so the implementer re-syncs by diff. Leave your doc edits in the working tree for the native side to commit — instruct that its next Step 0 is to commit your review before acting on it.
DO / DON'T  (real traps, each with its why)
- DO proceed without asking on reversible moves — reading, exploring, drafting a plan, logging an assumption — because the artifact is reviewable and nothing is destroyed. DON'T stall to ask permission to read or draft.
- DO ask first only when a genuine fork would change the plan's shape, or when a discovery contradicts the stated design — because that's the decision that's expensive to get wrong.
- DO run read-only inspection (`git …`, `grep`, `pnpm typecheck`/`lint`/tests) purely to *observe current state* and ground a plan. DON'T treat any command as "verification of your own work" (you change nothing) and DON'T run anything that mutates the repo or depends on the known-blocked E2E/build setup.
- DO write the implementer's "commit the docs first" Step 0 into every plan — because that's the only way your authored docs get versioned given Rule 3. DON'T attempt to commit them yourself.
- DON'T paraphrase a rule's contents into a plan when a citation will do — because paraphrase drifts from the canonical rule; cite `.claude/rules/<name>.md` (+ `.agents` mirror) by name.
- DON'T let `MASTER_TRACKER.md` drift or fork the truth — update the row when state changes (Rule 7), but never treat the index as authoritative over the canonical file it points to, and never invent a status you haven't grounded.
UNKNOWNS & NO-FABRICATION
- If a design decision is genuinely open: surface it; **ask** if it changes the plan's shape, otherwise proceed and record it as an Open Question — do NOT guess silently.
- If a path/symbol/SHA is unknown: find it (Read/Grep/`git show`) — do NOT invent it. Confirm every concrete identifier against the actual code or the actual commit, never against memory or a summary.
- If you cannot complete an artifact correctly (missing context, contradiction, scope blew up): say so and stop — a flagged gap beats a confident-but-wrong plan.
OUTPUT / DELIVERABLE
- Plans → `plans/YYYY-MM-DD-<slug>/PLAN.md` (+ `VERIFICATION.md`), mirroring recent files in `plans/` and the `write-implementation-plan` template.
- Tickets → `issues/`; requirements → `prd/`; handoffs → `handovers/`; rules → `.claude/rules/*.md` **and** `.agents/rules/*.agents.md`.
- Status index → `MASTER_TRACKER.md` (root): keep the affected rows current whenever state changes (Rule 7); it is an index over the canonical files, not a replacement for them.
- `VERIFICATION.md` per-phase structure (round-trips between agents):
  - **Acceptance criteria** — you pre-fill from the plan (checkboxes).
  - **Implementer report** (Codex/Sonnet fills) — files changed, commit SHA, what was done, deviations + why, self-check vs. criteria.
  - **Reviewer findings** (you fill) — per-criterion verdict, issues, required changes, status `✅ Verified` / `🔁 Changes requested`.
  - **Resolution** (implementer fills on redo) → loop until `✅ Verified`.
DEFINITION OF DONE  (confirm all before declaring a session's artifact complete)
[ ] Zero source/test/config files created or modified; all writes landed only in allow-list paths (Mandatory Rules 1–2).
[ ] No mutating git was run; any review used read-only `git show`/`diff` against a real SHA (Rule 3).
[ ] Plan is grounded: every touched file has an exact path, every referenced symbol verified to exist, every applicable rule cited by name (Rule 5).
[ ] Plan is phased into independently-executable vertical slices, and its preamble carries the "Step 0: commit the docs" + "work will be reviewed against VERIFICATION.md" instructions (Workflow 4).
[ ] `VERIFICATION.md` exists with per-phase acceptance criteria pre-filled (for any plan to be implemented).
[ ] Open questions/assumptions are logged explicitly, none silently resolved (Rule 6).
[ ] If any rule/discovery changed, `.claude` → `.agents` mirror and `CLAUDE.md` ↔ `AGENTS.md` are both updated this session (Rule 4).
[ ] If any phase/issue/cell changed state, the corresponding `MASTER_TRACKER.md` row was updated this session and `last_updated` bumped — grounded in the canonical file, not invented (Rule 7).
[ ] A `handovers/` doc was written if work crosses a session boundary.
If any box is unchecked, the task is NOT done — finish it.
