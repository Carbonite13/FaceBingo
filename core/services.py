"""Application use cases, isolated from FastAPI for straightforward testing."""
from __future__ import annotations
import logging, string
from typing import Any
from supabase import Client
from core.repositories import EncounterRepository, ParticipantRepository
from core.storage import delete_public_photo, upload_photo
logger = logging.getLogger("facebingo.services")
_ALPHABET, _MAX_PHOTO_BYTES = set(string.ascii_uppercase), 5 * 1024 * 1024
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
class ValidationError(ValueError): """A safe validation failure for a participant."""
class ParticipantService:
    def __init__(self, client: Client) -> None: self.repository = ParticipantRepository(client)
    def register(self, *, name: str, bio: str) -> dict[str, Any]:
        name, bio = name.strip(), bio.strip()
        if not name: raise ValidationError("Name is required.")
        return self.repository.upsert_by_name(name=name, bio=bio)
    def list_participants(self) -> list[dict[str, Any]]: return self.repository.list_all()
    def delete_participant(self, user_id: str) -> None: self.repository.delete(user_id)
class EncounterService:
    def __init__(self, client: Client) -> None: self.client, self.repository = client, EncounterRepository(client)
    def submit(self, *, letter: str, submitter_name: str, met_name: str, thought: str, image_bytes: bytes, content_type: str | None) -> str:
        letter, submitter_name, met_name, thought = letter.upper().strip(), submitter_name.strip(), met_name.strip(), thought.strip()
        if letter not in _ALPHABET: raise ValidationError("Invalid letter. Please go back and try again.")
        if not all((submitter_name, met_name, thought)): raise ValidationError("All fields are required. Please complete the form.")
        if not image_bytes: raise ValidationError("A photo is required. Please capture or upload a photo.")
        if content_type not in _ALLOWED_TYPES: raise ValidationError("Only JPEG, PNG and WebP photos are accepted.")
        if len(image_bytes) > _MAX_PHOTO_BYTES: raise ValidationError("Photo must be under 5 MB.")
        photo_url = upload_photo(self.client, image_bytes, content_type, submitter_name, letter)
        self.repository.create({"submitter_name": submitter_name, "met_name": met_name, "thought": thought, "photo_url": photo_url, "letter": letter})
        return photo_url
    def statistics(self) -> dict[str, Any]:
        rows, counts = self.repository.list_recent(), {}
        for row in rows:
            letter = row.get("letter", "?"); counts[letter] = counts.get(letter, 0) + 1
        return {"total_encounters": len(rows), "unique_participants": len({row["submitter_name"] for row in rows}), "most_active_letter": max(counts, key=counts.get, default="—"), "letter_counts": counts, "recent": rows[:20]}
    def delete_encounter(self, encounter_id: str) -> None:
        photo_url = self.repository.photo_url(encounter_id)
        if photo_url:
            try: delete_public_photo(self.client, photo_url)
            except Exception: logger.warning("Could not remove photo for encounter %s", encounter_id, exc_info=True)
        self.repository.delete(encounter_id)
