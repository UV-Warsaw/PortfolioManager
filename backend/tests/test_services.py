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


# ---------------------------------------------------------------------------
# Password-reset service unit tests
# ---------------------------------------------------------------------------


def test_request_password_reset_issues_token_for_registered_email(
    db_session: Session,
) -> None:
    """
    request_password_reset creates a PasswordResetToken row for a valid email.
    """
    from unittest.mock import patch

    from app.services.password_reset import request_password_reset

    register_user(email="pr@example.com", password="securepass", session=db_session)

    with patch("app.services.password_reset.send_password_reset_email"):
        request_password_reset(email="pr@example.com", session=db_session)

    from sqlmodel import select

    from app.models.password_reset import PasswordResetToken

    records = db_session.exec(
        select(PasswordResetToken).where(PasswordResetToken.email == "pr@example.com")
    ).all()
    assert len(records) == 1
    assert records[0].used_at is None


def test_request_password_reset_silent_for_unknown_email(
    db_session: Session,
) -> None:
    """
    request_password_reset returns silently for an unregistered address.
    """
    from unittest.mock import patch

    from app.services.password_reset import request_password_reset

    with patch("app.services.password_reset.send_password_reset_email") as mock_send:
        request_password_reset(email="ghost@example.com", session=db_session)
        mock_send.assert_not_called()


def test_confirm_password_reset_updates_password(db_session: Session) -> None:
    """
    confirm_password_reset changes the user's password and marks token used.
    """
    import secrets
    from datetime import UTC, datetime, timedelta

    from app.repositories.password_reset import PasswordResetTokenRepository
    from app.services.auth import login_user
    from app.services.password_reset import confirm_password_reset

    register_user(email="cpw@example.com", password="oldpassword", session=db_session)

    raw_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    repo = PasswordResetTokenRepository(db_session)
    repo.create(raw_token=raw_token, email="cpw@example.com", expires_at=expires_at)

    confirm_password_reset(
        raw_token=raw_token, new_password="newpassword1", session=db_session
    )

    result = login_user(
        email="cpw@example.com", password="newpassword1", session=db_session
    )
    assert result["email"] == "cpw@example.com"


def test_confirm_password_reset_invalid_token_raises(db_session: Session) -> None:
    """
    confirm_password_reset with a bad token raises ValueError.
    """
    from app.services.password_reset import confirm_password_reset

    with pytest.raises(ValueError, match="Invalid or expired"):
        confirm_password_reset(
            raw_token="bogus-token",
            new_password="newpassword1",
            session=db_session,
        )


def test_confirm_password_reset_token_cannot_be_reused(db_session: Session) -> None:
    """
    confirm_password_reset marks the token as used; a second attempt raises ValueError.
    """
    import secrets
    from datetime import UTC, datetime, timedelta

    from app.repositories.password_reset import PasswordResetTokenRepository
    from app.services.password_reset import confirm_password_reset

    register_user(email="reuse@example.com", password="oldpassword", session=db_session)

    raw_token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    repo = PasswordResetTokenRepository(db_session)
    repo.create(raw_token=raw_token, email="reuse@example.com", expires_at=expires_at)

    confirm_password_reset(
        raw_token=raw_token, new_password="firstnewpass", session=db_session
    )

    with pytest.raises(ValueError, match="Invalid or expired"):
        confirm_password_reset(
            raw_token=raw_token, new_password="secondnewpass", session=db_session
        )
