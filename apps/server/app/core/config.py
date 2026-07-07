from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[4]
SERVER_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            ROOT_DIR / ".env",
            SERVER_DIR / ".env",
            ROOT_DIR / ".env.local",
            SERVER_DIR / ".env.local",
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_base_url: str = "http://localhost:8000"
    web_base_url: str | None = None
    cors_allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8081"]
    )
    log_level: str = "info"

    database_url: str | None = None
    supabase_url: str | None = None
    supabase_anon_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_ANON_KEY", "SUPABASE_PUBLISHABLE_KEY"),
    )
    supabase_service_role_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SECRET_KEY"),
    )
    supabase_db_schema: str = "public"
    supabase_storage_bucket: str = "voice-agent"
    supabase_jwt_secret: str | None = None

    encryption_key: str | None = None

    composio_api_key: str | None = None
    composio_webhook_secret: str | None = None
    composio_base_url: str = "https://backend.composio.dev"
    composio_default_entity_prefix: str = "voice-agent"
    composio_google_auth_config_id: str | None = None
    composio_gmail_auth_config_id: str | None = None
    composio_googlecalendar_auth_config_id: str | None = None
    composio_microsoft_auth_config_id: str | None = None

    llm_provider: str = "openai"
    llm_model: str = "gpt-4.1-mini"
    openai_api_key: str | None = None
    google_api_key: str | None = None

    stt_provider: str = "groq"
    stt_model: str = "whisper-large-v3-turbo"
    groq_api_key: str | None = None
    deepgram_api_key: str | None = None

    tts_provider: str = "openai"
    tts_model: str = "gpt-4o-mini-tts"
    tts_voice: str = "alloy"
    elevenlabs_api_key: str | None = None

    expo_public_api_url: str | None = None
    expo_public_ws_url: str | None = None

    sentry_dsn: str | None = None
    otel_exporter_otlp_endpoint: str | None = None

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return stripped
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
