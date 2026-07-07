from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

from app.core.config import Settings
from app.schemas.integrations import ConnectedAccount


class ComposioService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._client = None

    @property
    def configured(self) -> bool:
        return bool(self.settings.composio_api_key)

    def _get_client(self):
        if not self.configured:
            return None
        if self._client is not None:
            return self._client
        try:
            from composio import Composio
            self._client = Composio(api_key=self.settings.composio_api_key)
        except Exception:
            return None
        return self._client

    def _auth_config_id_for(self, suite: str, app: str) -> str | None:
        normalized_app = app.strip().lower()

        if suite == "google":
            if normalized_app == "gmail":
                return (
                    self.settings.composio_gmail_auth_config_id
                    or self.settings.composio_google_auth_config_id
                )
            if normalized_app == "googlecalendar":
                return (
                    self.settings.composio_googlecalendar_auth_config_id
                    or self.settings.composio_google_auth_config_id
                )
            return self.settings.composio_google_auth_config_id
        if suite == "microsoft":
            return self.settings.composio_microsoft_auth_config_id
        return None

    def _normalize_status(self, raw_status: object) -> str:
        value = getattr(raw_status, "value", raw_status)
        normalized = str(value or "ready").split(".")[-1].strip().lower().replace("_", "-")
        status_aliases = {
            "active": "ready",
            "connected": "ready",
            "completed": "ready",
            "initializing": "connecting",
            "initiated": "connecting",
            "pending": "connecting",
            "in-progress": "connecting",
            "failed": "error",
            "inactive": "disconnected",
        }
        return status_aliases.get(normalized, normalized)

    def _extract_toolkit_slug(self, account: object) -> str:
        toolkit = getattr(account, "toolkit", None)
        nested_slug = getattr(toolkit, "slug", None)
        if nested_slug:
            return str(nested_slug)

        for attr in ("toolkit_slug", "app_unique_id", "appName", "app_name"):
            value = getattr(account, attr, None)
            if value:
                return str(value)

        return "unknown"

    def _toolkit_slug_from_tool_name(self, tool_name: str) -> str | None:
        normalized = tool_name.strip().upper()
        if normalized.startswith("GMAIL_"):
            return "gmail"
        if normalized.startswith("GOOGLECALENDAR_"):
            return "googlecalendar"
        if normalized.startswith("GOOGLEDRIVE_"):
            return "googledrive"
        if normalized.startswith("OUTLOOK_"):
            return "outlook"
        if normalized.startswith("MICROSOFTTEAMS_"):
            return "teams"
        if normalized.startswith("MICROSOFTONEDRIVE_"):
            return "onedrive"
        return None

    async def create_connection(self, user_id: str, suite: str, app: str) -> dict:
        if suite not in {"google", "microsoft"}:
            raise ValueError(f"Suite `{suite}` is not supported for direct connection yet")

        auth_config_id = self._auth_config_id_for(suite, app)
        client = self._get_client()
        fallback_integration_id = f"pending::{suite}::{app}::{user_id}"
        callback_url = self._build_callback_url(user_id=user_id, suite=suite, app=app)
        fallback_connection_url = (
            f"{self.settings.composio_base_url.rstrip('/')}/connect/{suite}/{app}?entity_id="
            f"{self.settings.composio_default_entity_prefix}:{user_id}"
        )
        if client is not None and auth_config_id:
            try:
                request = client.connected_accounts.link(
                    user_id=user_id,
                    auth_config_id=auth_config_id,
                    callback_url=callback_url,
                )
                return {
                    "connection_url": getattr(request, "redirect_url", None) or fallback_connection_url,
                    "integration_id": str(getattr(request, "id", fallback_integration_id)),
                    "expires_at": datetime.now(UTC).isoformat(),
                }
            except Exception:
                pass

        expires_at = datetime.now(UTC) + timedelta(minutes=15)
        return {
            "connection_url": fallback_connection_url,
            "integration_id": fallback_integration_id,
            "expires_at": expires_at.isoformat(),
        }

    def _build_callback_url(self, *, user_id: str, suite: str, app: str) -> str:
        base_url = (self.settings.web_base_url or self.settings.app_base_url).rstrip("/")
        query = urlencode({"user_id": user_id, "suite": suite, "app": app})
        return f"{base_url}/api/v1/integrations/composio/callback?{query}"

    async def list_connected_accounts(self, user_id: str) -> list[ConnectedAccount] | None:
        client = self._get_client()
        if client is None:
            return None

        try:
            accounts = client.connected_accounts.list(user_ids=[user_id])
        except Exception:
            return None

        items = getattr(accounts, "items", None)
        if items is None:
            items = accounts if isinstance(accounts, list) else []

        result: list[ConnectedAccount] = []
        for account in items:
            toolkit = self._extract_toolkit_slug(account)
            lowered_toolkit = toolkit.lower()
            suite = (
                "google"
                if lowered_toolkit in {"gmail", "googlecalendar", "googledrive"}
                or "google" in lowered_toolkit
                else "microsoft"
                if "microsoft" in lowered_toolkit or lowered_toolkit in {"onedrive", "outlook", "teams"}
                else lowered_toolkit
            )
            result.append(
                ConnectedAccount(
                    suite=suite,
                    app=lowered_toolkit,
                    status=self._normalize_status(getattr(account, "status", "ready")),
                    connected_account_id=str(getattr(account, "id", f"{toolkit}::{user_id}")),
                )
            )
        return result

    async def execute_tool(
        self,
        tool_name: str,
        arguments: dict,
        *,
        user_id: str | None = None,
        connected_account_id: str | None = None,
    ) -> dict:
        if not self.configured:
            return {
                "success": True,
                "dry_run": True,
                "tool_name": tool_name,
                "arguments": arguments,
                "provider": "composio",
                "message": "Composio is not configured yet. This action was simulated in dry-run mode.",
            }

        client = self._get_client()
        if client is None:
            return {
                "success": False,
                "tool_name": tool_name,
                "arguments": arguments,
                "provider": "composio",
                "message": "Composio is configured, but the SDK client could not be initialized.",
            }

        if user_id:
            toolkit_slug = self._toolkit_slug_from_tool_name(tool_name)
            accounts = await self.list_connected_accounts(user_id)
            if toolkit_slug and accounts is not None:
                matching_accounts = [account for account in accounts if account.app == toolkit_slug]
                if not matching_accounts:
                    return {
                        "success": False,
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "provider": "composio",
                        "message": (
                            f"No connected {toolkit_slug} account is available for this user yet. "
                            "Open Integrations and connect the account first."
                        ),
                    }
                ready_account = next((account for account in matching_accounts if account.status == "ready"), None)
                if ready_account is None:
                    statuses = ", ".join(sorted({account.status for account in matching_accounts}))
                    return {
                        "success": False,
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "provider": "composio",
                        "message": (
                            f"The connected {toolkit_slug} account is not ready yet ({statuses}). "
                            "Reconnect it from Integrations before retrying."
                        ),
                    }
                connected_account_id = connected_account_id or ready_account.connected_account_id

        try:
            result = client.tools.execute(
                slug=tool_name,
                arguments=arguments,
                user_id=user_id,
                connected_account_id=connected_account_id,
            )
            return {
                "success": True,
                "tool_name": tool_name,
                "arguments": arguments,
                "provider": "composio",
                "message": "Tool executed against Composio.",
                "data": result,
            }
        except Exception as exc:
            return {
                "success": False,
                "tool_name": tool_name,
                "arguments": arguments,
                "provider": "composio",
                "message": f"Composio execution failed: {exc}",
            }
