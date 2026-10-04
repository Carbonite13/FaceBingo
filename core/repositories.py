"""Thin Supabase persistence adapters; no HTTP or business logic lives here."""
from __future__ import annotations
from typing import Any
from supabase import Client
from config import config
class ParticipantRepository:
    def __init__(self, client: Client) -> None: self.client = client
    def upsert_by_name(self, *, name: str, bio: str) -> dict[str, Any]:
        existing = self.client.table("users").select("id").eq("name", name).execute()
        if existing.data:
            user_id = existing.data[0]["id"]
            result = self.client.table("users").update({"additional_metadata": {"bio": bio}}).eq("id", user_id).execute()
            return result.data[0] if result.data else {"id": user_id}
        return self.client.table("users").insert({"name": name, "additional_metadata": {"bio": bio}}).execute().data[0]
    def list_all(self) -> list[dict[str, Any]]:
        return self.client.table("users").select("*").order("created_at", desc=True).execute().data or []
    def delete(self, user_id: str) -> None: self.client.table("users").delete().eq("id", user_id).execute()
class EncounterRepository:
    def __init__(self, client: Client) -> None: self.client = client
    def create(self, payload: dict[str, Any]) -> None: self.client.table(config.active_table).insert(payload).execute()
    def list_recent(self) -> list[dict[str, Any]]:
        return self.client.table(config.active_table).select("*").order("created_at", desc=True).execute().data or []
    def photo_url(self, encounter_id: str) -> str | None:
        result = self.client.table(config.active_table).select("photo_url").eq("id", encounter_id).execute()
        return result.data[0].get("photo_url") if result.data else None
    def delete(self, encounter_id: str) -> None: self.client.table(config.active_table).delete().eq("id", encounter_id).execute()
