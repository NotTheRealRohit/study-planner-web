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
uv run --package intelligence uvicorn app.main:app --reload --port 8000
```

Set `CORS_ORIGINS` to a comma-separated list when the caller is not the default
local Vite app:

```bash
CORS_ORIGINS=http://localhost:5173,https://studytracker.app \
  uv run --package intelligence uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl -s http://localhost:8000/health
```

## Run with Docker Compose

From the repository root:

```bash
docker compose up --build -d
```

The service listens on `http://localhost:8000`. Stop it with:

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

Health:

```bash
curl -s http://localhost:8000/health
```

Calibration:

```bash
curl -s -X POST http://localhost:8000/v1/calibration \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/pillar-a/progress/compute-calibration-empty.input.json
```

Calibration prompt detail:

```bash
curl -s -X POST http://localhost:8000/v1/calibration/prompt-detail \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/pillar-a/progress/get-prompt-detail-empty.input.json
```

Progress:

```bash
curl -s -X POST http://localhost:8000/v1/progress \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/pillar-a/progress/compute-progress-full-snapshot.input.json
```

Roadmap generation:

```bash
curl -s -X POST http://localhost:8000/v1/roadmap/generate \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/pillar-a/roadmap/generate-roadmap-ddia-600-min.input.json
```

Roadmap regeneration:

```bash
curl -s -X POST http://localhost:8000/v1/roadmap/regenerate \
  -H 'Content-Type: application/json' \
  -d @tests/fixtures/pillar-a/roadmap/regenerate-preserves-pins.input.json
```

## Test

```bash
uv run --package intelligence pytest services/intelligence/tests -q
```
