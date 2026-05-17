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
