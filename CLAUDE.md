# Study Tracker Web

A mobile-first responsive web app for self-directed learners. Two Vercel deployments under one apex domain: Astro marketing site (`studytracker.app/*`) + Vite React 19 SPA (`studytracker.app/study/*`).

**PRD:** [`prd/PRD-study-tracker-web.md`](prd/PRD-study-tracker-web.md) | **Issues:** [`issues/`](issues/)

## Tech Stack

pnpm 10, Astro 4, Vite 5, React 19, TypeScript 5.4, Supabase (auth + DB + storage), Dexie (IndexedDB), date-fns 4, Playwright, Vitest, Vercel, Marginalia design system.

## Commands

```bash
export FNM_PATH="$HOME/.local/share/fnm" && export PATH="$FNM_PATH:$PATH" && eval "$(fnm env --shell bash)" && fnm use 22
export PNPM_HOME="$HOME/.local/share/pnpm" && export PATH="$PNPM_HOME:$PATH"

pnpm dev                               # Both apps (Astro :4321, Vite :5173)
pnpm dev:app                           # Vite only → http://localhost:5173/study/
pnpm build                             # Both apps
pnpm test:e2e                          # Playwright (4 suites)
pnpm --filter app test                 # Vitest unit tests (app)
pnpm --filter roadmap-engine test       # Vitest unit tests (roadmap-engine)
pnpm --filter progress test             # Vitest unit tests (progress)
pnpm lint && pnpm typecheck            # Lint + typecheck all packages
```

## Directory Map

| Path | Purpose |
|---|---|
| `apps/marketing/` | Astro marketing site; `vercel.json` rewrites `/study/*` → React app |
| `apps/app/src/auth/` | Auth deep module (AuthGate with DI), AuthProvider, ProtectedRoute |
| `apps/app/src/events/` | EventStore (Dexie per-user DB, v3 schema), ProgressEngine (deprecated) |
| `apps/app/src/progress/` | Progress hooks (useCalibrationState, useProgressSnapshot, usePromptDetail) |
| `apps/app/src/onboarding/` | 4-step onboarding wizard with draft persistence |
| `apps/app/src/sync/` | Cloud sync engine (write-ahead queue, snapshots, restore) |
| `apps/app/src/components/` | AppShell, NavBar, SyncIndicator, Field, Button, Card, Tag |
| `apps/app/src/lib/` | Supabase client, useMatchMedia hook |
| `apps/app/src/pages/` | SignIn, SignUp, Home, Log, Week, Roadmap, Roadmaps, Settings |
| `apps/app/supabase/migrations/` | SQL migrations (events table, storage buckets) |
| `packages/design-tokens/` | CSS tokens, component classes, reset/typography |
| `packages/progress/` | Pure progress tracking — Bayesian calibration, GP regression, streak, burn-up |
| `packages/roadmap-engine/` | Pure roadmap generation algorithm (no framework deps) |
| `e2e/` | Playwright: smoke, session-log, sync, onboarding specs |

## Routing

`BrowserRouter basename="/study"` — never include `/study` in `to` props. Vite `base: '/study/'`.

Provider nesting: `AuthProvider → EventStoreRouter → SyncRouter → AppRoutes`.

App routes wrapped in `ProtectedRoute + RequireOnboarding`. Onboarding routes wrapped in `ProtectedRoute + OnboardingGate`.

## Architecture References

Deep-dive docs live in `.cursor/rules/` (Cursor project rules):

| Rule | Topic |
|---|---|
| [`auth-architecture.mdc`](.cursor/rules/auth-architecture.mdc) | Auth module, DI pattern, routes |
| [`eventstore-architecture.mdc`](.cursor/rules/eventstore-architecture.mdc) | Dexie schema (v3), tables, event shape, per-user isolation |
| [`onboarding-architecture.mdc`](.cursor/rules/onboarding-architecture.mdc) | 4-step wizard, state persistence, completion events |
| [`sync-architecture.mdc`](.cursor/rules/sync-architecture.mdc) | Write-ahead queue, snapshots, browser lifecycle, retry |
| [`roadmap-engine.mdc`](.cursor/rules/roadmap-engine.mdc) | Roadmap generation API, types, role inference |
| [`supabase-schema.mdc`](.cursor/rules/supabase-schema.mdc) | Events table, RLS policies, storage buckets |

## Project Rules

| Rule | Prevents |
|---|---|
| [`css-workspace-packages.mdc`](.cursor/rules/css-workspace-packages.mdc) | CSS imports failing to resolve |
| [`playwright-config.mdc`](.cursor/rules/playwright-config.mdc) | E2E config issues |
| [`astro-selectors.mdc`](.cursor/rules/astro-selectors.mdc) | Selector strict mode violations |
| [`react-router-v7-basename.mdc`](.cursor/rules/react-router-v7-basename.mdc) | Double basename prefixes |
| [`auth-testing-fakes.mdc`](.cursor/rules/auth-testing-fakes.mdc) | Brittle Supabase mocks |
| [`form-design-spacing.mdc`](.cursor/rules/form-design-spacing.mdc) | Collapsed form field groups |
| [`auth-init-timeout.mdc`](.cursor/rules/auth-init-timeout.mdc) | React hanging on slow auth |
| [`eventstore-per-user-db.mdc`](.cursor/rules/eventstore-per-user-db.mdc) | Cross-account data bleed |
| [`dexie-test-setup.mdc`](.cursor/rules/dexie-test-setup.mdc) | Dexie test failures |
| [`dexie-schema-migration.mdc`](.cursor/rules/dexie-schema-migration.mdc) | Data loss on schema changes |
| [`sync-provider-testing.mdc`](.cursor/rules/sync-provider-testing.mdc) | Lifecycle hook test failures |
| [`latex-report-build.mdc`](.cursor/rules/latex-report-build.mdc) | "latexmk not found"; broken dissertation builds |

## Environment Variables

`apps/app/.env.local` — template at `.env.example`: `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.

## Related Docs

[`DEPLOYMENT.md`](DEPLOYMENT.md) | [`design/marginalia.html`](design/marginalia.html) | [`design/algo/ROADMAP_ENGINE_GUIDE.md`](design/algo/ROADMAP_ENGINE_GUIDE.md) | [`design/2026-04-29-onboarding-ui-ux-guide.md`](design/2026-04-29-onboarding-ui-ux-guide.md)

## Codebase Index Maintenance

Memory contains a codebase index (14 module files tracking 162+ source files). At session start, check for staleness:

1. Read `index-metadata.md` from memory for the last-indexed commit hash
2. Run: `git diff --name-only <hash>..HEAD -- 'apps/' 'packages/' 'e2e/'`
3. If output is non-empty, invoke `/update-index` to update affected module indexes
4. If the metadata file is missing, invoke `/update-index --full` for a full rescan

## E2E test

E2E test cannot be performed due to Environment issues, So only write the test dont try to run.