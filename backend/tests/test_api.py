"""Integration tests for the auth router."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient) -> None:
    """
    POST /auth/register with valid data creates an account and returns a token.
    """
    response = client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "strongpass1"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "user@example.com"
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert isinstance(body["id"], int)


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    """
    POST /auth/register with an already-registered email returns 409.
    """
    payload = {"email": "dup@example.com", "password": "strongpass1"}
    client.post("/auth/register", json=payload)

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_register_short_password_returns_422(client: TestClient) -> None:
    """
    POST /auth/register with a password shorter than 8 characters returns 422.
    """
    response = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "abc"},
    )
    assert response.status_code == 422


def test_register_invalid_email_returns_422(client: TestClient) -> None:
    """
    POST /auth/register with an invalid email format returns 422.
    """
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "strongpass1"},
    )
    assert response.status_code == 422


@pytest.mark.parametrize("path", ["/", "/health"])
def test_health_endpoints(client: TestClient, path: str) -> None:
    """
    GET / and GET /health return 200.
    """
    response = client.get(path)
    assert response.status_code == 200


def test_login_success(client: TestClient) -> None:
    """
    POST /auth/login with valid credentials returns a token.
    """
    client.post(
        "/auth/register",
        json={"email": "login@example.com", "password": "strongpass1"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": "strongpass1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "login@example.com"
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalid_password_returns_401(client: TestClient) -> None:
    """
    POST /auth/login with wrong password returns 401.
    """
    client.post(
        "/auth/register",
        json={"email": "wrongpass@example.com", "password": "strongpass1"},
    )

    response = client.post(
        "/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_nonexistent_user_returns_401(client: TestClient) -> None:
    """
    POST /auth/login with non-existent email returns 401.
    """
    response = client.post(
        "/auth/login",
        json={"email": "nouser@example.com", "password": "strongpass1"},
    )
    assert response.status_code == 401


def test_logout_success(client: TestClient) -> None:
    """
    POST /auth/logout with valid token invalidates the token.
    """
    reg_response = client.post(
        "/auth/register",
        json={"email": "logout@example.com", "password": "strongpass1"},
    )
    token = reg_response.json()["access_token"]

    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_logout_invalidates_token(client: TestClient) -> None:
    """
    After logout, the token should be rejected on /auth/me.
    """
    reg_response = client.post(
        "/auth/register",
        json={"email": "invalidate@example.com", "password": "strongpass1"},
    )
    token = reg_response.json()["access_token"]

    client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 401
    assert "revoked" in me_response.json()["detail"]


def test_get_me_success(client: TestClient) -> None:
    """
    GET /auth/me with valid token returns user info.
    """
    reg_response = client.post(
        "/auth/register",
        json={"email": "me@example.com", "password": "strongpass1"},
    )
    token = reg_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"
    assert "id" in body


def test_get_me_without_token_returns_403(client: TestClient) -> None:
    """
    GET /auth/me without Authorization header returns 403.
    """
    response = client.get("/auth/me")
    assert response.status_code == 403


def test_get_me_with_invalid_token_returns_401(client: TestClient) -> None:
    """
    GET /auth/me with invalid token returns 401.
    """
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Password reset integration tests
# ---------------------------------------------------------------------------


def test_password_reset_request_registered_email_returns_202(
    client: TestClient,
) -> None:
    """
    POST /auth/password-reset/request with a registered email returns 202.
    """
    client.post(
        "/auth/register",
        json={"email": "reset@example.com", "password": "strongpass1"},
    )

    with patch("app.services.password_reset.send_password_reset_code"):
        response = client.post(
            "/auth/password-reset/request",
            json={"email": "reset@example.com"},
        )

    assert response.status_code == 202
    assert "verification code" in response.json()["message"]


def test_password_reset_request_unknown_email_also_returns_202(
    client: TestClient,
) -> None:
    """
    POST /auth/password-reset/request with an unknown email still returns 202
    to prevent account enumeration.
    """
    response = client.post(
        "/auth/password-reset/request",
        json={"email": "ghost@example.com"},
    )
    assert response.status_code == 202


def test_password_reset_confirm_success(client: TestClient) -> None:
    """
    POST /auth/password-reset/confirm with a valid token updates the password.
    """
    client.post(
        "/auth/register",
        json={"email": "confirm@example.com", "password": "oldpassword"},
    )

    captured: list[str] = []

    def fake_send(email: str, code: str) -> None:
        captured.append(code)

    with patch(
        "app.services.password_reset.send_password_reset_code", side_effect=fake_send
    ):
        client.post(
            "/auth/password-reset/request",
            json={"email": "confirm@example.com"},
        )

    assert captured, "No code was captured"
    raw_code = captured[0]

    response = client.post(
        "/auth/password-reset/confirm",
        json={"email": "confirm@example.com", "code": raw_code, "new_password": "newpassword1"},
    )
    assert response.status_code == 200
    assert "Password updated" in response.json()["message"]

    login_response = client.post(
        "/auth/login",
        json={"email": "confirm@example.com", "password": "newpassword1"},
    )
    assert login_response.status_code == 200


def test_password_reset_confirm_token_cannot_be_reused(client: TestClient) -> None:
    """
    POST /auth/password-reset/confirm with an already-used token returns 400.
    """
    client.post(
        "/auth/register",
        json={"email": "reuse@example.com", "password": "oldpassword"},
    )

    captured: list[str] = []

    def fake_send(email: str, code: str) -> None:
        captured.append(code)

    with patch(
        "app.services.password_reset.send_password_reset_code", side_effect=fake_send
    ):
        client.post(
            "/auth/password-reset/request",
            json={"email": "reuse@example.com"},
        )

    raw_code = captured[0]

    client.post(
        "/auth/password-reset/confirm",
        json={"email": "reuse@example.com", "code": raw_code, "new_password": "firstnewpass"},
    )

    response = client.post(
        "/auth/password-reset/confirm",
        json={"email": "reuse@example.com", "code": raw_code, "new_password": "secondnewpass"},
    )
    assert response.status_code == 400
    assert "Invalid or expired" in response.json()["detail"]


def test_password_reset_confirm_invalid_token_returns_400(
    client: TestClient,
) -> None:
    """
    POST /auth/password-reset/confirm with a bogus token returns 400.
    """
    response = client.post(
        "/auth/password-reset/confirm",
        json={"email": "ghost@example.com", "code": "000000", "new_password": "newpassword1"},
    )
    assert response.status_code == 400


def test_password_reset_confirm_short_password_returns_422(
    client: TestClient,
) -> None:
    """
    POST /auth/password-reset/confirm with a short new password returns 422.
    """
    response = client.post(
        "/auth/password-reset/confirm",
        json={"email": "x@example.com", "code": "123456", "new_password": "short"},
    )
    assert response.status_code == 422
