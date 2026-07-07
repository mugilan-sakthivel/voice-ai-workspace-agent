from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_thread_creation_and_fetch() -> None:
    created = client.post("/api/v1/threads", json={"user_id": "demo-user", "title": "My thread"})
    assert created.status_code == 200
    thread = created.json()

    fetched = client.get(f"/api/v1/threads/{thread['id']}")
    assert fetched.status_code == 200
    payload = fetched.json()
    assert payload["id"] == thread["id"]
    assert payload["messages"] == []

    missing = client.get("/api/v1/threads/thread_missing?user_id=demo-user")
    assert missing.status_code == 404


def test_chat_requires_approval_for_write_actions() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_test_write",
            "message": "Send an email to user@example.com saying hello from the voice agent",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "approval_required"
    assert payload["approval"]["tool_name"] == "GMAIL_SEND_EMAIL"
    assert payload["message_id"].startswith("msg_")
    assert payload["approval"]["arguments"]["recipient_email"] == "user@example.com"


def test_chat_read_only_flow() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_test_read",
            "message": "Show my calendar today",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["proposed_tools"][0]["tool_name"] == "GOOGLECALENDAR_FIND_EVENT"
    assert payload["message_id"].startswith("msg_")


def test_onedrive_prompt_routes_to_onedrive_tool() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_test_onedrive",
            "message": "List my OneDrive files",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert "Gmail and Google Calendar" in payload["reply"]


def test_send_email_requires_recipient_address() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_missing_recipient",
            "message": "Send an email to the team",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert "recipient email address" in payload["reply"]


def test_schedule_requires_specific_time() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_missing_time",
            "message": "Schedule a meeting with Alex",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert "give me an exact time" in payload["reply"]


def test_thread_access_is_scoped_to_user() -> None:
    created = client.post("/api/v1/threads", json={"user_id": "owner-user", "title": "Private"})
    assert created.status_code == 200
    thread_id = created.json()["id"]

    forbidden_fetch = client.get(f"/api/v1/threads/{thread_id}?user_id=other-user")
    assert forbidden_fetch.status_code == 404

    forbidden_chat = client.post(
        "/api/v1/chat",
        json={
            "user_id": "other-user",
            "thread_id": thread_id,
            "message": "Show my calendar",
            "input_mode": "text",
        },
    )
    assert forbidden_chat.status_code == 403
