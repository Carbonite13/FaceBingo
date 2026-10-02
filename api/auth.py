"""
HTTP Basic Authentication dependency.

Inject `require_admin` into any route or router that must be
protected by admin credentials configured in .env.
"""

from __future__ import annotations

import logging
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from config import config

logger = logging.getLogger("facebingo.auth")

_security = HTTPBasic()


def require_admin(credentials: HTTPBasicCredentials = Depends(_security)) -> str:
    """
    FastAPI dependency — validates HTTP Basic Auth credentials against the
    values stored in ``ADMIN_USERNAME`` / ``ADMIN_PASSWORD`` from .env.

    Uses :func:`secrets.compare_digest` for constant-time comparison to
    prevent timing-based username/password enumeration attacks.

    Returns the verified username on success.
    Raises HTTP 401 on invalid credentials.
    """
    valid_user = secrets.compare_digest(
        credentials.username.encode("utf-8"),
        config.admin_username.encode("utf-8"),
    )
    valid_pass = secrets.compare_digest(
        credentials.password.encode("utf-8"),
        config.admin_password.encode("utf-8"),
    )

    if not (valid_user and valid_pass):
        logger.warning(
            "Failed admin auth attempt — supplied username: '%s'",
            credentials.username,
        )
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Basic"},
        )

    logger.info("Admin access granted to '%s'", credentials.username)
    return credentials.username
