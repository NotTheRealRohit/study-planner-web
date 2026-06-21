# VERIFICATION — dev production-readiness (auth · resilience · hardening)

Companion to [`PLAN.md`](./PLAN.md). The **review round-trip** artifact for the build → test → review loop.

**How this file is used (each phase):**

1. **Cowork** pre-fills *Acceptance criteria* (below) from the plan. *(done — checkboxes start unchecked.)*
2. **Codex/Sonnet** fills *Implementer report* after building the phase: files changed, commit SHA, what was done, deviations + why, self-check vs criteria. Then **STOP for review**.
3. **Cowork** fills *Reviewer findings*: diff the committed SHA (`git show <sha>`), give a per-criterion verdict + required changes; set `✅ Verified` or `🔁 Changes requested`.
4. **Codex** fills *Resolution* on redo. Loop until `✅ Verified`.

**Step 0 (before any code):** commit these planning docs verbatim — `docs(plan): add dev-production-readiness plan + verification`. Cowork cannot commit (it bricks `.git` locks in the sandbox); the native side establishes the baseline so later diffs are meaningful. If a reviewer leaves edits here, the next Step 0 commits the review before acting on it.

**Global rules every phase is checked against:** Dexie schema bumps re-declare all tables and add a new version (`dexie-schema-migration`); Dexie tests use fake-indexeddb + unique DB names (`dexie-test-setup`); auth tests use hand-written fakes, never `jest.mock` (`auth-testing-fakes`); never include `/study` in router `to` (`react-router-v7-basename`); no secrets committed (use `.env.example` placeholders); E2E is written, **not run** (`CLAUDE.md`); the `CalibrationState` contract and CUSUM/GP/scheduling stay untouched (carried from the prior plan's D-03/D-04).

---

## Phase 1 — Real Supabase-JWT auth on all `/v1` endpoints

### Acceptance criteria (Cowork pre-filled)

- [ ] `pyjwt` added to `services/intelligence/pyproject.toml`.
- [ ] `app/security.py` `require_user` verifies the bearer token via `SUPABASE_JWT_SECRET` (HS256, `audience="authenticated"`), returns the `sub`; 401 on missing/malformed/invalid/expired/no-sub; 500 (loud) if the secret is unset.
- [ ] All three `/v1` routers mounted with `dependencies=[Depends(require_user)]`; `/health` stays open (no token).
- [ ] `intelligenceClient.ts` attaches `Authorization: Bearer <supabase access_token>` from `supabase.auth.getSession()`.
- [ ] `services/intelligence/.env.example` created (`SUPABASE_JWT_SECRET`, `CORS_ORIGINS`); `apps/app/.env.example` notes the service-side secret. No real secret committed.
- [ ] `test_auth.py`: 401 (no/!valid/expired/wrong-secret), 200 (valid), `/health` open. `uv run --package intelligence pytest services/intelligence/tests -q` passes.

### Implementer report (Codex/Sonnet fills)
_Files changed:_ `services/intelligence/pyproject.toml`, `uv.lock`, `services/intelligence/app/security.py`, `services/intelligence/app/main.py`, `services/intelligence/tests/test_auth.py`, `services/intelligence/tests/test_v1_integration.py`, `services/intelligence/.env.example`, `apps/app/src/lib/intelligenceClient.ts`, `apps/app/.env.example`, `plans/2026-06-20-dev-production-readiness/PLAN.md`, `plans/2026-06-20-dev-production-readiness/VERIFICATION.md`.
_Commit SHA:_ `b71d962`
_What was done:_ Added PyJWT, a service-side `require_user` dependency that verifies Supabase HS256 bearer tokens with `audience="authenticated"` and returns `sub`, protected all `/v1` routers while leaving `/health` open, and attached the current Supabase session access token from the app client. Added service env documentation and auth coverage for missing/malformed/invalid/expired/no-sub/unconfigured/valid token cases.
_Deviations + why:_ Updated existing service golden-test helper to mint a valid JWT because the suite exercises protected `/v1` endpoints and would otherwise fail after the planned router dependency. The app `.env.example` uses a comment-only note for `SUPABASE_JWT_SECRET` because this Vite app exposes `SUPABASE_*` env vars.
_Self-check vs criteria:_ All Phase 1 criteria satisfied. Verified with `uv run --package intelligence pytest services/intelligence/tests -q` (`46 passed, 1 warning`), manual unauthenticated `/v1/calibration` probe (`401`), manual `/health` probe (`{"status":"ok"}`), and `pnpm --filter @study-tracker/app typecheck`.

### Reviewer findings (Cowork fills)
_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 2 — Resilient calibration client

### Acceptance criteria (Cowork pre-filled)

- [ ] `postCalibration` uses an `AbortController` timeout (~8s), bounded retry/backoff (≤2 retries) on transient 5xx/network only.
- [ ] **Never retries 401** — throws `CalibrationAuthError` immediately; 5xx/other → `CalibrationServiceError`.
- [ ] Bearer token attached on every attempt; one `console.warn` on final failure (no silent swallow).
- [ ] `intelligenceClient.test.ts`: token attached; retry-then-succeed on 500 (2 calls); no-retry on 401 (1 call); timeout aborts. `pnpm --filter app test` + `typecheck` pass.

### Implementer report (Codex/Sonnet fills)
_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)
_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 3 — Resilient UI + Dexie stale cache

### Acceptance criteria (Cowork pre-filled)

- [ ] Dexie `version(5)` added re-declaring all existing tables (`events`, `sync_queue`, `sync_meta`, `onboardingDraft`, `activeSession`) plus `calibrationCache: 'key'`; v4 data preserved on upgrade.
- [ ] `useCalibrationState` returns `{ calibration, status }` (`loading|ready|stale|error`); writes last-good to `calibrationCache`; on failure serves cached value as `stale`, or `error` with `calibration:null` when no cache. **No** in-browser recompute fallback (D-03). No null-flicker (previous value kept during refetch).
- [ ] `ErrorBoundary` created and wraps `AppRoutes` in `App.tsx`; `ServiceStatusBanner` shows stale/error affordance.
- [ ] `Home.tsx`/`Week.tsx` destructure `{ calibration, status }` (downstream `useProgressSnapshot`/`usePromptDetail` unchanged); skeleton on first load.
- [ ] Tests: hook ready/stale/error transitions + cache write; v4→v5 migration preserves events; ErrorBoundary fallback. `pnpm --filter app test` + `typecheck` pass.

### Implementer report (Codex/Sonnet fills)
_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)
_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 4 — Service hardening

### Acceptance criteria (Cowork pre-filled)

- [ ] Middleware sets/propagates `X-Request-ID`, logs one structured JSON line/request (request_id, method, path, status, latency_ms), and stamps `X-Model-Version` (= `PRODUCTION_PRIOR_STRATEGY`) on responses.
- [ ] Uncaught-exception handler returns `{error, code, request_id}` 500 (no stack leak); `HTTPException` 401/422 detail still flows.
- [ ] `sessions` length-bounded (`max_length`) → oversized payload returns 422; applied to `CalibrationRequest` (+ `ProgressRequest`).
- [ ] `/readiness` (open) returns `{status:"ready", model:...}` after a trivial `production_calibrator().fit_global([])`.
- [ ] In-memory per-user rate-limit stub (keyed on JWT `sub`) returns 429 past threshold; labelled as a dev stub.
- [ ] `docker-compose.yml` has a `/health` healthcheck. `test_hardening.py` covers request-id, 422, `/readiness`, version, rate-limit; service suite passes.

### Implementer report (Codex/Sonnet fills)
_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)
_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Phase 5 — One-command dev stack

### Acceptance criteria (Cowork pre-filled)

- [ ] Root `package.json` gains `dev:full` (runs Vite + uvicorn via `concurrently`) and devDeps `concurrently` + `wait-on`.
- [ ] README (root and/or `apps/app`) documents: service required for calibration, `pnpm dev:full`, `SUPABASE_JWT_SECRET` in env, `docker compose up` alternative.
- [ ] Manual: `pnpm dev:full` brings up :5173 and :8000; `/health` 200; Home shows live pace. (No automated test; script + docs only.)

### Implementer report (Codex/Sonnet fills)
_Files changed:_
_Commit SHA:_
_What was done:_
_Deviations + why:_
_Self-check vs criteria:_

### Reviewer findings (Cowork fills)
_Per-criterion verdict:_
_Issues / required changes:_
_Status:_ ☐ ✅ Verified / 🔁 Changes requested

### Resolution (implementer fills on redo)

---

## Sign-off

- [ ] All five phases `✅ Verified` by Cowork review.
- [ ] `MASTER_TRACKER.md` updated (new dev-readiness row/note; OQ-02 of the prior plan resolved here); `last_updated` bumped if a new day.
- [ ] Carry-forward: production hosting/secrets (OQ-03 of prior plan) still deferred; rate-limit thresholds (OQ-01) and toast system (OQ-02) noted.
