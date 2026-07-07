import os
import sys
from pathlib import Path


SERVER_ROOT = Path(__file__).resolve().parents[1]
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))


for env_name in (
    "DATABASE_URL",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_SECRET_KEY",
    "COMPOSIO_API_KEY",
    "COMPOSIO_GMAIL_AUTH_CONFIG_ID",
    "COMPOSIO_GOOGLECALENDAR_AUTH_CONFIG_ID",
    "COMPOSIO_GOOGLE_AUTH_CONFIG_ID",
    "COMPOSIO_MICROSOFT_AUTH_CONFIG_ID",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "OPENAI_API_KEY",
):
    os.environ[env_name] = ""
