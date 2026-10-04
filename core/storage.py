"""
Supabase Storage helpers — photo upload to the configured bucket.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from supabase import Client

from config import config

logger = logging.getLogger("facebingo.storage")

# Accepted MIME types and their file extensions
_ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


def upload_photo(
    client: Client,
    image_bytes: bytes,
    content_type: str,
    submitter_name: str,
    letter: str,
) -> str:
    """
    Upload *image_bytes* to Supabase Storage and return the public URL.

    Path inside bucket: ``{LETTER}/{submitter_name}_{uuid_short}.{ext}``

    The submitter_name is used as the identification attribute as required.
    """
    ext = _ALLOWED_TYPES.get(content_type, "jpg")
    uid = uuid.uuid4().hex[:8]
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in submitter_name)
    path = f"{letter.upper()}/{safe_name}_{uid}.{ext}"

    logger.info("Uploading photo for '%s' → bucket=%s path=%s", submitter_name, config.active_bucket, path)

    client.storage.from_(config.active_bucket).upload(
        path=path,
        file=image_bytes,
        file_options={"content-type": content_type, "upsert": "false"},
    )

    public_url: str = client.storage.from_(config.active_bucket).get_public_url(path)
    logger.info("Photo uploaded successfully: %s", public_url)
    return public_url


def delete_public_photo(client: Client, photo_url: str) -> None:
    """Delete only a public URL belonging to this application's configured bucket."""
    bucket_prefix = f"/storage/v1/object/public/{config.active_bucket}/"
    if bucket_prefix not in photo_url:
        logger.warning("Refusing to delete photo outside configured bucket")
        return
    client.storage.from_(config.active_bucket).remove([photo_url.split(bucket_prefix, 1)[1]])


def delete_public_photo(client: Client, photo_url: str) -> None:
    """Remove a photo only when its URL belongs to this application's bucket."""
    bucket_prefix = f"/storage/v1/object/public/{config.active_bucket}/"
    if bucket_prefix not in photo_url:
        logger.warning("Refusing to delete a photo outside the configured bucket")
        return
    client.storage.from_(config.active_bucket).remove([photo_url.split(bucket_prefix, 1)[1]])
