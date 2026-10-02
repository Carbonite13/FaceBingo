"""
Submission routes — POST /submit and GET /admin/stats.
"""

from __future__ import annotations

import logging
import string
from typing import Literal

from fastapi import APIRouter, File, Form, Request, UploadFile, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_303_SEE_OTHER

from api.auth import require_admin
from api.dependencies import get_supabase, limiter, get_participant_profile
from api.state import state
from config import config
from core.storage import upload_photo
from core.template import templates
from core.domain import ParticipantProfile

logger = logging.getLogger("facebingo.submissions")

router = APIRouter(tags=["submissions"])

_ALPHABETS = set(string.ascii_uppercase)  # O(1) membership check
_MAX_PHOTO_BYTES = 5 * 1024 * 1024  # 5 MB
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/submit", response_class=HTMLResponse, name="submit")
@limiter.limit(config.rate_limit)
async def submit(
    request: Request,
    letter: str = Form(...),
    your_name: str = Form(default=""),  # fallback but mostly ignored
    met_name: str = Form(...),
    thought: str = Form(...),
    photo: UploadFile | None = File(default=None),
    profile: ParticipantProfile | None = Depends(get_participant_profile),
) -> HTMLResponse:
    """
    Save an encounter record and upload the photo to Supabase Storage.
    Redirects back to a success page on completion.
    """
    letter = letter.upper().strip()
    your_name = profile.name if profile else (your_name.strip() or "Anonymous")
    met_name = met_name.strip()
    thought = thought.strip()

    if not state.submissions_active:
        return RedirectResponse(url="/timed-out", status_code=HTTP_303_SEE_OTHER)

    # Basic validation 
    if letter not in _ALPHABETS:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"detail": "Invalid letter. Please go back and try again."},
        )
    if not your_name or not met_name or not thought:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"detail": "All fields are required. Please complete the form."},
        )

    logger.info("Encounter submitted: '%s' met '%s' (letter=%s)", your_name, met_name, letter)

    if not photo or not photo.size or photo.size == 0:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"detail": "A photo is required. Please capture or upload a photo."},
        )

    # Photo upload 
    photo_url: str | None = None
    if photo and photo.size and photo.size > 0:
        if photo.content_type not in _ALLOWED_CONTENT_TYPES:
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"detail": "Only JPEG, PNG and WebP photos are accepted."},
            )
        if photo.size > _MAX_PHOTO_BYTES:
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"detail": "Photo must be under 5 MB."},
            )
        image_bytes = await photo.read()
        db = get_supabase()
        photo_url = upload_photo(
            client=db,
            image_bytes=image_bytes,
            content_type=photo.content_type or "image/jpeg",
            submitter_name=your_name,
            letter=letter,
        )

    # Save record to Supabase 
    db = get_supabase()
    payload = {
        "submitter_name": your_name,
        "met_name": met_name,
        "thought": thought,
        "photo_url": photo_url,
        "letter": letter,
    }
    db.table(config.active_table).insert(payload).execute()
    logger.info("Encounter record saved for '%s'", your_name)

    # Render success page 
    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={
            "your_name": your_name,
            "met_name": met_name,
            "letter": letter,
            "photo_url": photo_url,
        },
    )


@router.get("/admin/stats", name="admin_stats")
@limiter.limit(config.rate_limit)
async def admin_stats(request: Request) -> JSONResponse:
    """
    Return JSON statistics for the admin dashboard.
    Polled every 15 s by admin.js. No auth required — the page itself is protected.
    """
    logger.info("Admin stats requested")
    db = get_supabase()

    # Fetch all records (fine for event scale, not a social network)
    result = db.table(config.active_table).select("*").order("created_at", desc=True).execute()
    rows: list[dict] = result.data or []

    total = len(rows)
    unique_submitters = len({r["submitter_name"] for r in rows})

    # Count encounters per letter
    letter_counts: dict[str, int] = {}
    for row in rows:
        ltr = row.get("letter", "?")
        letter_counts[ltr] = letter_counts.get(ltr, 0) + 1

    most_active_letter = max(letter_counts, key=lambda k: letter_counts[k], default="—")

    stats = {
        "total_encounters": total,
        "unique_participants": unique_submitters,
        "most_active_letter": most_active_letter,
        "letter_counts": letter_counts,
        "recent": rows[:20],  # latest 20 for the live feed
    }

    return JSONResponse(content=stats)


@router.delete("/admin/encounters/{encounter_id}", name="admin_delete_encounter")
async def admin_delete_encounter(
    encounter_id: str,
    _: str = Depends(require_admin),
) -> JSONResponse:
    """
    Admin endpoint to delete a specific encounter and its associated photo.
    """
    logger.info("Admin deleting encounter %s", encounter_id)
    db = get_supabase()

    # Try to delete the photo from storage if it exists
    try:
        result = db.table(config.active_table).select("photo_url").eq("id", encounter_id).execute()
        if result.data and result.data[0].get("photo_url"):
            photo_url = result.data[0]["photo_url"]
            bucket_prefix = f"/storage/v1/object/public/{config.active_bucket}/"
            if bucket_prefix in photo_url:
                path = photo_url.split(bucket_prefix)[1]
                db.storage.from_(config.active_bucket).remove([path])
    except Exception as e:
        logger.warning("Failed to delete photo from storage during encounter deletion: %s", e)

    # Delete the record from the database
    db.table(config.active_table).delete().eq("id", encounter_id).execute()
    return JSONResponse(content={"status": "ok"})


@router.get("/admin/status", name="admin_get_status")
async def admin_get_status(_: str = Depends(require_admin)) -> JSONResponse:
    return JSONResponse(content={
        "active": state.submissions_active,
        "registration_required": state.registration_required
    })


@router.post("/admin/status", name="admin_set_status")
async def admin_set_status(
    request: Request,
    _: str = Depends(require_admin)
) -> JSONResponse:
    data = await request.json()
    if "active" in data:
        state.submissions_active = bool(data["active"])
        logger.info(f"Admin toggled submissions active status to {state.submissions_active}")
    if "registration_required" in data:
        state.registration_required = bool(data["registration_required"])
        logger.info(f"Admin toggled registration required to {state.registration_required}")
    return JSONResponse(content={
        "active": state.submissions_active,
        "registration_required": state.registration_required
    })
