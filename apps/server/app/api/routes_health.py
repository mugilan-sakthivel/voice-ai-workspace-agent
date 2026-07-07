from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_composio_service,
    get_supabase_service,
    settings_dependency,
)
from app.core.config import Settings
from app.schemas.common import HealthResponse
from app.services.composio import ComposioService
from app.services.supabase import SupabaseService


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    settings: Settings = Depends(settings_dependency),
    composio: ComposioService = Depends(get_composio_service),
    supabase: SupabaseService = Depends(get_supabase_service),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        composio_configured=composio.configured,
        supabase_configured=supabase.configured,
    )

