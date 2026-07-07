from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_approval_confirm_and_reject() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_test_approval",
            "message": "Send an email to leader@example.com saying please review the update",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    approval_id = response.json()["approval"]["approval_id"]

    confirmed = client.post(
        f"/api/v1/approvals/{approval_id}/confirm",
        json={"user_id": "demo-user"},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "approved"

    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "demo-user",
            "thread_id": "thread_test_reject",
            "message": "Schedule a meeting with team@example.com tomorrow 3pm for project sync",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    approval_id = response.json()["approval"]["approval_id"]

    rejected = client.post(
        f"/api/v1/approvals/{approval_id}/reject",
        json={"user_id": "demo-user"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"


def test_approval_resolution_is_user_scoped_and_idempotent() -> None:
    response = client.post(
        "/api/v1/chat",
        json={
            "user_id": "owner-user",
            "thread_id": "thread_test_guardrails",
            "message": "Send an email to team@example.com saying status update",
            "input_mode": "text",
        },
    )
    assert response.status_code == 200
    approval_id = response.json()["approval"]["approval_id"]

    forbidden = client.post(
        f"/api/v1/approvals/{approval_id}/confirm",
        json={"user_id": "other-user"},
    )
    assert forbidden.status_code == 403

    confirmed = client.post(
        f"/api/v1/approvals/{approval_id}/confirm",
        json={"user_id": "owner-user"},
    )
    assert confirmed.status_code == 200

    duplicate = client.post(
        f"/api/v1/approvals/{approval_id}/confirm",
        json={"user_id": "owner-user"},
    )
    assert duplicate.status_code == 409
