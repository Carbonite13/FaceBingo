"""
FaceBingo — application entry point.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.cors import CORSMiddleware

from api.dependencies import limiter
from api.routes.debug import debugRouter
from api.routes.pages import router as pages_router
from api.routes.submissions import router as submissions_router
from config import config
from core.errors import register_error_handlers
from core.logging import RequestLoggingMiddleware, setup_logging

# Logging 
setup_logging()

# App 
app = FastAPI(
    title=config.app_title,
    version=config.app_version,
    # Disable auto-generated docs in production to reduce attack surface
    docs_url="/docs" if config.app_env != "production" else None,
    redoc_url="/redoc" if config.app_env != "production" else None,
)

# Rate limiter state 
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware 
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# Error handlers
register_error_handlers(app)

#  Static files 
_STATIC_DIR = Path(__file__).parent / "UI" / "static/"
_SCRIPT_DIR = Path(__file__).parent / "UI" / "scripts"
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
app.mount("/scripts", StaticFiles(directory=str(_SCRIPT_DIR)), name="scripts")

#  Routers 
app.include_router(pages_router)         # GET /  · /encounter/{letter} · /admin
app.include_router(submissions_router)   # POST /submit · GET /admin/stats
app.include_router(debugRouter)          # GET /debug/* (admin-auth protected)


#  Health check 
@app.get("/health", tags=["health"], include_in_schema=False)
async def health() -> dict[str, str]:
    """Liveness probe — no auth, no rate limit."""
    return {"status": "ok", "version": config.app_version}
