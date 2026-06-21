from __future__ import annotations

import os
import time
from dataclasses import dataclass

import jwt
from fastapi import Depends, Header, HTTPException

_ALGS = ["HS256"]
_RATE_LIMIT_WINDOW_SECONDS = 60


@dataclass
class _RateBucket:
    window_started_at: float
    count: int


_RATE_LIMITS: dict[str, _RateBucket] = {}


def require_user(authorization: str | None = Header(default=None)) -> str:
    """Verify the Supabase access JWT (HS256) and return the user id (sub)."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        # Misconfiguration, not an auth failure — make it loud.
        raise HTTPException(status_code=500, detail="auth not configured")
    token = authorization.split(" ", 1)[1]
    try:
        claims = jwt.decode(token, secret, algorithms=_ALGS, audience="authenticated")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="invalid token") from None
    sub = str(claims.get("sub") or "")
    if not sub:
        raise HTTPException(status_code=401, detail="token missing subject")
    return sub


def rate_limit_user(user_id: str = Depends(require_user)) -> None:
    """Dev-only in-memory per-user rate-limit stub."""
    raw_limit = os.getenv("INTELLIGENCE_RATE_LIMIT_PER_MINUTE", "120")
    try:
        limit = int(raw_limit)
    except ValueError:
        limit = 120
    if limit <= 0:
        return

    now = time.monotonic()
    bucket = _RATE_LIMITS.get(user_id)
    if bucket is None or now - bucket.window_started_at >= _RATE_LIMIT_WINDOW_SECONDS:
        _RATE_LIMITS[user_id] = _RateBucket(window_started_at=now, count=1)
        return

    if bucket.count >= limit:
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    bucket.count += 1
