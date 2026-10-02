from fastapi import APIRouter, Depends
from config import config
from api.auth import require_admin

debugRouter = APIRouter(
    prefix="/debug",
    tags=["debug"],
    dependencies=[Depends(require_admin)],  # all /debug/* endpoints require admin auth
)

@debugRouter.get("/supa")
async def handle_supabase():
    # verify supabase configurations
    return {
        "supabase_url": True if config.supabase_url else False,
        "supabase_anon_key": True if config.supabase_anon_key else False,
        "supabase_bucket": True if config.supabase_bucket else False,
        "supabase_table": True if config.supabase_table else False,
    }

@debugRouter.get("/cors")
async def handle_cors():
    # verify cors config
    return {
        "cors": config.allowed_origins,
    }

@debugRouter.get("/rate_limit")
async def handle_rate_limit():
    # verify rate limiting config
    return {
        "rate_limit": config.rate_limit,
    }

@debugRouter.get("/app")
async def handle_app():
    # verify app config
    return {
        "app_env": config.app_env,
        "log_level": config.log_level,
        "app_title": config.app_title,
        "app_version": config.app_version,
    }