from __future__ import annotations

import os

import jwt
from fastapi import Header, HTTPException

_ALGS = ["HS256"]


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
