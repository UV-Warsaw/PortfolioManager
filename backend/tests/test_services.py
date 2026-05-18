"""Unit tests for the auth service."""

import pytest
from sqlmodel import Session

from app.services.auth import login_user, logout_user, register_user


def test_register_user_creates_account(db_session: Session) -> None:
    """
    register_user creates a new account and returns a token dict.
    """
    result = register_user(
        email="test@example.com",
        password="securepassword",
        session=db_session,
    )
    assert result["email"] == "test@example.com"
    assert "access_token" in result
    assert result["token_type"] == "bearer"
    assert isinstance(result["id"], int)


def test_register_user_hashes_password(db_session: Session) -> None:
    """
    register_user stores a bcrypt hash, not the plain-text password.
    """
    from app.repositories.user import UserRepository

    register_user(email="hash@example.com", password="mypassword", session=db_session)
    repo = UserRepository(db_session)
    user = repo.get_by_email("hash@example.com")
    assert user is not None
    assert user.password_hash != "mypassword"
    assert user.password_hash.startswith("$2b$")


def test_register_user_sets_defaults(db_session: Session) -> None:
    """
    register_user assigns default risk_level and monthly_expenses.
    """
    from app.repositories.user import UserRepository

    register_user(
        email="defaults@example.com", password="mypassword", session=db_session
    )
    repo = UserRepository(db_session)
    user = repo.get_by_email("defaults@example.com")
    assert user is not None
    assert user.risk_level == "moderate"
    assert user.monthly_expenses == 0.0


def test_register_user_duplicate_raises(db_session: Session) -> None:
    """
    register_user raises ValueError when the email is already taken.
    """
    register_user(email="dup@example.com", password="securepass", session=db_session)
    with pytest.raises(ValueError, match="already exists"):
        register_user(email="dup@example.com", password="otherpass", session=db_session)


def test_login_user_success(db_session: Session) -> None:
    """
    login_user with valid credentials returns a token dict.
    """
    register_user(
        email="logintest@example.com",
        password="securepassword",
        session=db_session,
    )
    result = login_user(
        email="logintest@example.com",
        password="securepassword",
        session=db_session,
    )
    assert result["email"] == "logintest@example.com"
    assert "access_token" in result
    assert result["token_type"] == "bearer"


def test_login_user_wrong_password_raises(db_session: Session) -> None:
    """
    login_user with wrong password raises ValueError.
    """
    register_user(
        email="wrongpass@example.com",
        password="securepassword",
        session=db_session,
    )
    with pytest.raises(ValueError, match="Invalid email or password"):
        login_user(
            email="wrongpass@example.com",
            password="wrongpassword",
            session=db_session,
        )


def test_login_user_nonexistent_raises(db_session: Session) -> None:
    """
    login_user with non-existent email raises ValueError.
    """
    with pytest.raises(ValueError, match="Invalid email or password"):
        login_user(
            email="nouser@example.com",
            password="anypassword",
            session=db_session,
        )


def test_logout_user_blacklists_token(db_session: Session) -> None:
    """
    logout_user adds the token to the blacklist.
    """
    from app.repositories.token_blacklist import TokenBlacklistRepository

    result = register_user(
        email="logouttest@example.com",
        password="securepassword",
        session=db_session,
    )
    token = result["access_token"]

    logout_user(token=token, session=db_session)

    blacklist_repo = TokenBlacklistRepository(db_session)
    assert blacklist_repo.is_blacklisted(token) is True


def test_logout_user_invalid_token_raises(db_session: Session) -> None:
    """
    logout_user with invalid token raises ValueError.
    """
    with pytest.raises(ValueError, match="Invalid token"):
        logout_user(token="invalid-token", session=db_session)
