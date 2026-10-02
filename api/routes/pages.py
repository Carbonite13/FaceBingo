"""
Page routes — GET endpoints that render Jinja2 templates.
"""

from __future__ import annotations

import logging
import string

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.status import HTTP_404_NOT_FOUND

from api.auth import require_admin
from core.template import templates

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
async def encounter(request: Request, letter: str) -> HTMLResponse:
    """Page 2 — encounter form for a specific starting letter."""
    letter = letter.upper()
    if letter not in _ALPHABET_SET:
        logger.warning("Invalid letter requested: %s", letter)
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Invalid letter.")

    logger.info("Rendering encounter form for letter '%s'", letter)
    return templates.TemplateResponse(
        request=request,
        name="encounter.html",
        context={"letter": letter},
    )


@router.get("/admin", response_class=HTMLResponse, name="admin")
async def admin(
    request: Request,
    _: str = Depends(require_admin),
) -> HTMLResponse:
    """Page 3 — admin statistics dashboard (requires HTTP Basic Auth)."""
    logger.info("Rendering admin dashboard")
    return templates.TemplateResponse(request=request, name="admin.html", context={})
