from app.core.config import Settings


class SupabaseService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    @property
    def configured(self) -> bool:
        return bool(
            self.settings.supabase_url
            and self.settings.supabase_anon_key
            and self.settings.supabase_service_role_key
        )

    def get_client(self):
        if not self.configured:
            return None
        if self._client is not None:
            return self._client
        try:
            from supabase import ClientOptions, create_client
            self._client = create_client(
                self.settings.supabase_url,
                self.settings.supabase_service_role_key,
                options=ClientOptions(auto_refresh_token=False, persist_session=False),
            )
        except Exception:
            return None
        return self._client

    async def health_summary(self) -> dict:
        return {
            "configured": self.configured,
            "url": self.settings.supabase_url,
            "schema": self.settings.supabase_db_schema,
            "bucket": self.settings.supabase_storage_bucket,
            "client_ready": self.get_client() is not None,
        }
