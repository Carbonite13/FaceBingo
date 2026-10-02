"""
Shared FastAPI dependencies: rate limiter, Supabase client.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import config
from core.db import get_supabase

import json
import urllib.parse
from fastapi import Request
from api.state import state
from core.domain import ParticipantProfile

# Single limiter instance — key = client IP
limiter = Limiter(key_func=get_remote_address, default_limits=[config.rate_limit])

class RegistrationRequiredException(Exception):
    pass

async def get_participant_profile(request: Request) -> ParticipantProfile | None:
    cookie_val = request.cookies.get("facebingo_profile")
    if cookie_val:
        try:
            data = json.loads(urllib.parse.unquote(cookie_val))
            return ParticipantProfile(**data)
        except Exception:
            pass
    if state.registration_required:
        raise RegistrationRequiredException()
    return None

__all__ = ["limiter", "get_supabase", "get_participant_profile", "RegistrationRequiredException"]
