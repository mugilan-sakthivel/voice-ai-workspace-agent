from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_connect_integration_persists_local_account_state() -> None:
    response = client.post(
        "/api/v1/integrations/composio/connect",
        json={
            "user_id": "demo-user",
            "suite": "google",
            "app": "gmail",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["connection_url"]
    assert payload["integration_id"].startswith("pending::google::gmail::demo-user")

    accounts = client.get("/api/v1/integrations/accounts?user_id=demo-user")
    assert accounts.status_code == 200
    body = accounts.json()
    google_account = next(
        (item for item in body if item["suite"] == "google" and item["app"] == "gmail"),
        None,
    )
    assert google_account is not None
    assert google_account["status"] == "connecting"


def test_connect_google_calendar_persists_toolkit_specific_state() -> None:
    response = client.post(
        "/api/v1/integrations/composio/connect",
        json={
            "user_id": "demo-user",
            "suite": "google",
            "app": "googlecalendar",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["integration_id"].startswith("pending::google::googlecalendar::demo-user")

    accounts = client.get("/api/v1/integrations/accounts?user_id=demo-user")
    assert accounts.status_code == 200
    body = accounts.json()
    calendar_account = next(
        (
            item
            for item in body
            if item["suite"] == "google" and item["app"] == "googlecalendar"
        ),
        None,
    )
    assert calendar_account is not None
    assert calendar_account["status"] == "connecting"


def test_connect_integration_rejects_unsupported_suite() -> None:
    response = client.post(
        "/api/v1/integrations/composio/connect",
        json={
            "user_id": "demo-user",
            "suite": "meta",
            "app": "ads",
        },
    )

    assert response.status_code == 400
    assert "not supported" in response.json()["detail"]
