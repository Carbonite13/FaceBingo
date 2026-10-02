"""
Supabase client factory — thread-safe singleton.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from supabase import Client, create_client

from config import config

logger = logging.getLogger("facebingo.db")


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    logger.info("Initialising Supabase client (url=%s)", config.supabase_url)
    return create_client(config.supabase_url, config.supabase_anon_key)
