from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.testclient import TestClient

from app.main import app

SECRET = "test-supabase-jwt-secret-32-bytes-min"
WRONG_SECRET = "wrong-supabase-jwt-secret-32-bytes"


def _calibration_body() -> dict[str, Any]:
    return {
        "sessions": [],
        "exceptionalTags": [],
        "resolutions": [],
    }


def _token(secret: str = SECRET, **overrides: Any) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "aud": "authenticated",
        "exp": now + timedelta(minutes=5),
        "iat": now,
        "sub": "user-123",
        "role": "authenticated",
    }
    claims.update(overrides)
    return jwt.encode(claims, secret, algorithm="HS256")


def test_health_stays_open_without_token() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_v1_rejects_missing_token(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    client = TestClient(app)

    response = client.post("/v1/calibration", json=_calibration_body())

    assert response.status_code == 401


def test_v1_rejects_malformed_authorization_header(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    client = TestClient(app)

    response = client.post(
        "/v1/calibration",
        headers={"Authorization": "Basic definitely-not-a-bearer-token"},
        json=_calibration_body(),
    )

    assert response.status_code == 401


def test_v1_rejects_wrong_secret(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    client = TestClient(app)

    response = client.post(
        "/v1/calibration",
        headers={"Authorization": f"Bearer {_token(secret=WRONG_SECRET)}"},
        json=_calibration_body(),
    )

    assert response.status_code == 401


def test_v1_rejects_expired_token(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    client = TestClient(app)

    response = client.post(
        "/v1/calibration",
        headers={
            "Authorization": f"Bearer {_token(exp=datetime.now(UTC) - timedelta(minutes=1))}"
        },
        json=_calibration_body(),
    )

    assert response.status_code == 401


def test_v1_rejects_token_missing_subject(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    client = TestClient(app)

    response = client.post(
        "/v1/calibration",
        headers={"Authorization": f"Bearer {_token(sub='')}"},
        json=_calibration_body(),
    )

    assert response.status_code == 401


def test_v1_rejects_when_auth_secret_is_unset(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    client = TestClient(app)

    response = client.post(
        "/v1/calibration",
        headers={"Authorization": f"Bearer {_token()}"},
        json=_calibration_body(),
    )

    assert response.status_code == 500


def test_v1_accepts_valid_supabase_jwt(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", SECRET)
    client = TestClient(app)

    response = client.post(
        "/v1/calibration",
        headers={"Authorization": f"Bearer {_token()}"},
        json=_calibration_body(),
    )

    assert response.status_code == 200
