from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.api.dependencies import get_composio_service, get_store
from app.schemas.integrations import (
    ConnectedAccount,
    IntegrationConnectRequest,
    IntegrationConnectResponse,
)
from app.services.composio import ComposioService


router = APIRouter(tags=["integrations"])


@router.post("/integrations/composio/connect", response_model=IntegrationConnectResponse)
async def connect_integration(
    payload: IntegrationConnectRequest,
    composio: ComposioService = Depends(get_composio_service),
    store=Depends(get_store),
) -> IntegrationConnectResponse:
    try:
        response = await composio.create_connection(payload.user_id, payload.suite, payload.app)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    store.upsert_connected_account(
        payload.user_id,
        payload.suite,
        payload.app,
        status="connecting",
        connected_account_id=response["integration_id"],
    )
    return IntegrationConnectResponse(**response)


@router.get("/integrations/accounts", response_model=list[ConnectedAccount])
async def list_accounts(
    user_id: str = "demo-user",
    composio: ComposioService = Depends(get_composio_service),
    store=Depends(get_store),
) -> list[ConnectedAccount]:
    accounts = await composio.list_connected_accounts(user_id)
    if accounts is not None:
        for account in accounts:
            store.upsert_connected_account(
                user_id,
                account.suite,
                account.app,
                account.status,
                connected_account_id=account.connected_account_id,
            )
        return accounts
    return store.list_connected_accounts(user_id)


@router.get("/integrations/composio/callback", response_class=HTMLResponse, include_in_schema=False)
async def composio_callback(
    suite: str = Query(default="workspace"),
    app: str = Query(default="integration"),
) -> HTMLResponse:
    title = f"{suite.title()} {app.title()} connected"
    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title}</title>
        <style>
          body {{
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5efe6;
            color: #1f2937;
            min-height: 100vh;
            display: grid;
            place-items: center;
          }}
          .card {{
            width: min(92vw, 420px);
            background: white;
            border-radius: 24px;
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.12);
            padding: 28px 24px;
          }}
          h1 {{
            font-size: 26px;
            margin: 0 0 12px;
          }}
          p {{
            margin: 0 0 16px;
            line-height: 1.5;
            color: #4b5563;
          }}
          .badge {{
            display: inline-block;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            color: #0f766e;
            background: #ccfbf1;
            border-radius: 999px;
            padding: 8px 10px;
            margin-bottom: 14px;
          }}
          .button {{
            appearance: none;
            border: 0;
            border-radius: 14px;
            background: #111827;
            color: white;
            font-weight: 600;
            padding: 12px 16px;
            width: 100%;
          }}
        </style>
      </head>
      <body>
        <main class="card">
          <div class="badge">Connection complete</div>
          <h1>{title}</h1>
          <p>Your sign-in finished successfully. Return to the app and refresh the Integrations screen to see the updated status.</p>
          <p>If the app is still open, you can now go back and continue testing Gmail or Google Calendar actions.</p>
          <button class="button" onclick="window.close()">Close this tab</button>
        </main>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
