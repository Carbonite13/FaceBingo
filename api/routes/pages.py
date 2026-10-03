"""
Page routes — GET endpoints that render Jinja2 templates.
"""

from __future__ import annotations

import logging
import string

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND

from api.auth import require_admin
from api.dependencies import get_participant_profile, get_supabase
from api.state import state
from core.template import templates
from core.domain import ParticipantProfile

logger = logging.getLogger("facebingo.pages")

router = APIRouter(tags=["pages"])

_ALPHABET_LIST = list(string.ascii_uppercase)   # ordered, for template rendering
_ALPHABET_SET  = set(string.ascii_uppercase)    # O(1) membership check


@router.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request) -> HTMLResponse:
    """Page 1 — alphabet grid."""
    logger.info("Rendering alphabet index page")
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"alphabets": _ALPHABET_LIST},
    )


@router.get("/encounter/{letter}", response_class=HTMLResponse, name="encounter")
async def encounter(
    request: Request, 
    letter: str,
    profile: ParticipantProfile | None = Depends(get_participant_profile)
) -> HTMLResponse:
    """Page 2 — encounter form for a specific starting letter."""
    letter = letter.upper()
    if letter not in _ALPHABET_SET:
        logger.warning("Invalid letter requested: %s", letter)
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Invalid letter.")

    if not state.submissions_active:
        return RedirectResponse(url="/timed-out")

    logger.info("Rendering encounter form for letter '%s'", letter)
    return templates.TemplateResponse(
        request=request,
        name="encounter.html",
        context={"letter": letter},
    )


@router.get("/public", response_class=HTMLResponse, name="public")
async def public(request: Request) -> HTMLResponse:
    """Page 4 — public statistics and feed dashboard."""
    logger.info("Rendering public dashboard")
    return templates.TemplateResponse(request=request, name="public.html", context={})


@router.get("/users", response_class=HTMLResponse, name="users")
async def users_page(request: Request) -> HTMLResponse:
    """View all registered users."""
    db = get_supabase()
    users_result = db.table("users").select("*").order("created_at", desc=True).execute()
    return templates.TemplateResponse(
        request=request, 
        name="users.html", 
        context={"users": users_result.data or []}
    )



@router.get("/timed-out", response_class=HTMLResponse, name="timed_out")
async def timed_out(request: Request) -> HTMLResponse:
    """Page for timed out / paused state."""
    return templates.TemplateResponse(request=request, name="timed_out.html", context={})


@router.get("/admin", response_class=HTMLResponse, name="admin")
async def admin(
    request: Request,
    _: str = Depends(require_admin),
) -> HTMLResponse:
    """Page 3 — admin statistics dashboard (requires HTTP Basic Auth)."""
    logger.info("Rendering admin dashboard")
    return templates.TemplateResponse(request=request, name="admin.html", context={})
