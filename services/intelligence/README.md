# Intelligence Service

FastAPI service exposing Pillar A engines (calibration, progress, roadmap).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

From the repository root:

```bash
uv sync
```

## Run locally

```bash
SUPABASE_URL=https://<project>.supabase.co \
SUPABASE_JWT_SECRET=<project JWT secret> \
  uv run --package intelligence uvicorn app.main:app --reload --port 8000
```

From the repository root, `pnpm dev:intelligence` and `pnpm dev:full` also load
`services/intelligence/.env` before starting uvicorn.

`SUPABASE_JWT_SECRET` must be the Supabase project JWT secret from the dashboard,
not the publishable/anon key or service role key. For Supabase projects using
asymmetric signing keys (`ES256`/`RS256`), `SUPABASE_URL` is also required so the
service can fetch the project's public JWKS verification keys. `pnpm
dev:intelligence` will reuse `SUPABASE_URL` from `apps/app/.env.local` when the
service env file does not set it.

Set `CORS_ORIGINS` to a comma-separated list when the caller is not the default
local Vite app:

```bash
CORS_ORIGINS=http://localhost:5173,https://studytracker.app \
SUPABASE_URL=https://<project>.supabase.co \
SUPABASE_JWT_SECRET=<project JWT secret> \
  uv run --package intelligence uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl -s http://127.0.0.1:8000/health
```

For full-stack browser testing, start the Vite app with the intelligence service:

```bash
pnpm dev:full
```

This binds the intelligence service to `127.0.0.1:8000` and starts the app at
`http://localhost:5173/study/`. If the app does not start, first check that port
`8000` is not already occupied by another local dev server:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

## Run with Docker Compose

From the repository root:

```bash
SUPABASE_URL=https://<project>.supabase.co \
SUPABASE_JWT_SECRET=<project JWT secret> \
  docker compose up --build -d
```

The service listens on `http://127.0.0.1:8000`. Stop it with:

```bash
docker compose down
```

The Dockerfile defaults to the internal Docker image mirror available to local
Colima. Compose also passes the local CA bundle at
`/usr/local/etc/openssl/certs/combined_cacerts.pem` as a build secret so `uv`
can verify Python package downloads through the corporate proxy. Override
`DOCKER_CA_BUNDLE` if your CA bundle lives elsewhere.

On a host that can pull public images directly, override the build args:

```bash
PYTHON_IMAGE=python:3.12-slim UV_IMAGE=ghcr.io/astral-sh/uv:0.11.19 \
  docker compose up --build -d
```

## Curl examples

The examples below use the golden fixtures under
`tests/fixtures/pillar-a/`. Fixture request bodies include a `fn` field used by
the parity tests; the API ignores that extra field.

`/v1/*` endpoints require a Supabase access token from the configured project.
Legacy `HS256` tokens are verified with `SUPABASE_JWT_SECRET`; `ES256`/`RS256`
tokens are verified with the public JWKS endpoint under `SUPABASE_URL`:

```bash
AUTH_HEADER="Authorization: Bearer <supabase access token>"
```

Health:

```bash
curl -s http://127.0.0.1:8000/health
```

Calibration:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/calibration \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d @tests/fixtures/pillar-a/progress/compute-calibration-empty.input.json
```

Calibration prompt detail:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/calibration/prompt-detail \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d @tests/fixtures/pillar-a/progress/get-prompt-detail-empty.input.json
```

Progress:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/progress \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d @tests/fixtures/pillar-a/progress/compute-progress-full-snapshot.input.json
```

Roadmap generation:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/roadmap/generate \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d @tests/fixtures/pillar-a/roadmap/generate-roadmap-ddia-600-min.input.json
```

Roadmap regeneration:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/roadmap/regenerate \
  -H 'Content-Type: application/json' \
  -H "$AUTH_HEADER" \
  -d @tests/fixtures/pillar-a/roadmap/regenerate-preserves-pins.input.json
```

## Test

```bash
uv run --package intelligence pytest services/intelligence/tests -q
```
