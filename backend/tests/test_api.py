"""Integration tests for the auth router."""

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
