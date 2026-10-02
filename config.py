"""
Application configuration via pydantic-settings.
All values are loaded from environment variables / .env file.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    # Supabase 
    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_anon_key: str = Field(..., description="Supabase anon/public key")
    supabase_bucket: str = Field(
        default="facebingo-photos",
        description="Supabase Storage bucket name for encounter photos",
    )
    supabase_table: str = Field(
        default="encounters",
        description="Supabase table that stores encounter records",
    )

    @property
    def active_bucket(self) -> str:
        return self.supabase_bucket if self.supabase_bucket.strip() else "facebingo-photos"

    @property
    def active_table(self) -> str:
        return self.supabase_table if self.supabase_table.strip() else "encounters"

    # CORS 
    allowed_origins: list[str] = Field(
        default=["*"],
        description="List of allowed CORS origins",
    )

    # Rate limiting 
    rate_limit: str = Field(
        default="20/minute",
        description="SlowAPI rate limit string applied to write endpoints",
    )

    # Admin auth
    admin_username: str = Field(..., description="HTTP Basic Auth username for /admin and /debug routes")
    admin_password: str = Field(..., description="HTTP Basic Auth password for /admin and /debug routes")

    # App 
    app_env: str = Field(default="development", description="Runtime environment")
    log_level: str = Field(default="INFO", description="Python logging level")
    app_title: str = Field(default="FaceBingo", description="Application title")
    app_version: str = Field(default="0.1.0", description="Application version")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Singleton instance 
config = Config()