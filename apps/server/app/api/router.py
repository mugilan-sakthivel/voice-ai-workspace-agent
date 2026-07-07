from fastapi import APIRouter

from app.api.routes_approvals import router as approvals_router
from app.api.routes_chat import router as chat_router
from app.api.routes_health import router as health_router
from app.api.routes_integrations import router as integrations_router
from app.api.routes_threads import router as threads_router
from app.api.routes_voice import router as voice_router


api_router = APIRouter()
api_router.include_router(health_router, prefix="/api/v1")
api_router.include_router(chat_router, prefix="/api/v1")
api_router.include_router(voice_router, prefix="/api/v1")
api_router.include_router(integrations_router, prefix="/api/v1")
api_router.include_router(approvals_router, prefix="/api/v1")
api_router.include_router(threads_router, prefix="/api/v1")
