from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_database
from app.api.router import api_router
from app.core.config import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = get_database()
    app.state.database_ready = database.create_all()
    yield

app = FastAPI(
    title="Voice AI Workspace Agent API",
    version="0.1.0",
    summary="Voice-first workspace agent backend powered by Composio and Supabase.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {
        "name": "voice-agent-api",
        "status": "ok",
        "environment": settings.app_env,
        "database_ready": str(getattr(app.state, "database_ready", False)).lower(),
    }
