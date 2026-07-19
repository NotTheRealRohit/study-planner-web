ARG PYTHON_IMAGE=dockerhub.payment-providercorp.com/library/python:3.12-slim
ARG UV_IMAGE=dockerhub.payment-providercorp.com/astral/uv:0.11.19

FROM ${UV_IMAGE} AS uv
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=uv /uv /uvx /usr/local/bin/

COPY pyproject.toml uv.lock ./
COPY packages/py-progress packages/py-progress
COPY packages/py-roadmap-engine packages/py-roadmap-engine
COPY services/intelligence services/intelligence

RUN --mount=type=secret,id=ca_bundle,target=/tmp/ca_bundle.pem,required=false \
    if [ -s /tmp/ca_bundle.pem ]; then \
        export ***REMOVED***=/tmp/ca_bundle.pem ***REMOVED***=/tmp/ca_bundle.pem UV_SYSTEM_CERTS=1; \
    fi; \
    uv sync --frozen --package intelligence --no-dev

WORKDIR /app/services/intelligence

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
