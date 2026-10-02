"""
Generic error handlers — never expose internal details to the client.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from starlette.status import (
    HTTP_422_UNPROCESSABLE_CONTENT,
    HTTP_429_TOO_MANY_REQUESTS,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import RedirectResponse
from core.template import templates
from api.dependencies import RegistrationRequiredException

logger = logging.getLogger("facebingo.errors")

_GENERIC_MSG = "Something went wrong. Please try again."
_VALIDATION_MSG = "Invalid input. Please check your submission and try again."
_RATE_MSG = "Too many requests. Please wait a moment and try again."


def register_error_handlers(app: FastAPI) -> None:
    """Attach all global exception handlers to the FastAPI instance."""

    @app.exception_handler(RegistrationRequiredException)
    async def _registration_required_handler(request: Request, exc: RegistrationRequiredException):
        # Redirect to index to register
        return RedirectResponse(url="/", status_code=303)

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return templates.TemplateResponse(request=request, name="error.html", context={}, status_code=404)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        logger.warning("Rate limit exceeded: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": _RATE_MSG},
        )

    @app.exception_handler(ValidationError)
    async def _validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        logger.info("Validation error on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": _VALIDATION_MSG},
        )

    @app.exception_handler(HTTP_422_UNPROCESSABLE_CONTENT)
    async def _request_validation_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.info("Request validation error on %s", request.url.path)
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": _VALIDATION_MSG},
        )

    @app.exception_handler(Exception)
    async def _generic_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled exception on %s %s: %s",
            request.method,
            request.url.path,
            exc,
            exc_info=True,
        )
        return templates.TemplateResponse(request=request, name="error.html", context={}, status_code=404)