from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    composio_configured: bool
    supabase_configured: bool

