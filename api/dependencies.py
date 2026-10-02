"""
Shared FastAPI dependencies: rate limiter, Supabase client.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from config import config
from core.db import get_supabase

# Single limiter instance — key = client IP
limiter = Limiter(key_func=get_remote_address, default_limits=[config.rate_limit])

__all__ = ["limiter", "get_supabase"]
