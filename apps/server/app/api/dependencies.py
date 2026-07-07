from functools import lru_cache

from app.agents.runtime import DemoAgentRuntime
from app.core.config import Settings, get_settings
from app.db import Database
from app.services.composio import ComposioService
from app.services.store import AppStore
from app.services.supabase import SupabaseService
from app.services.voice import VoiceService


@lru_cache(maxsize=1)
def get_database() -> Database:
    return Database(get_settings())


@lru_cache(maxsize=1)
def get_composio_service() -> ComposioService:
    return ComposioService(get_settings())


@lru_cache(maxsize=1)
def get_supabase_service() -> SupabaseService:
    return SupabaseService(get_settings())


@lru_cache(maxsize=1)
def get_voice_service() -> VoiceService:
    return VoiceService(get_settings())


@lru_cache(maxsize=1)
def get_store() -> AppStore:
    return AppStore(get_database())


@lru_cache(maxsize=1)
def get_agent_runtime() -> DemoAgentRuntime:
    return DemoAgentRuntime(get_store(), get_composio_service())


def settings_dependency() -> Settings:
    return get_settings()
