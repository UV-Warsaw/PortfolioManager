"""Repository tests for UserRepository profile update methods."""

import pytest
from sqlmodel import Session

from app.repositories.user import UserRepository
from app.services.auth import register_user


def _create_user(session: Session, email: str = "repo@example.com") -> int:
    """
    Register a user and return its id.

    Args:
        session: Active database session.
        email: Email address for the new user.

    Returns:
        int: Primary key of the created user.
    """
    result = register_user(email=email, password="securepass1", session=session)
    return int(result["id"])


def test_update_email_changes_email(db_session: Session) -> None:
    """
    update_email persists the new email address.
    """
    user_id = _create_user(db_session)
    repo = UserRepository(db_session)

    updated = repo.update_email(user_id, "new@example.com")

    assert updated is not None
    assert updated.email == "new@example.com"


def test_update_email_returns_none_for_missing_user(db_session: Session) -> None:
    """
    update_email returns None when the user id does not exist.
    """
    repo = UserRepository(db_session)
    result = repo.update_email(999, "ghost@example.com")
    assert result is None


def test_update_password_changes_hash(db_session: Session) -> None:
    """
    update_password replaces the stored password hash.
    """
    user_id = _create_user(db_session)
    repo = UserRepository(db_session)
    original_hash = repo.get_by_id(user_id).password_hash  # type: ignore[union-attr]

    repo.update_password(user_id, "newhash_bcrypt_placeholder")

    updated = repo.get_by_id(user_id)
    assert updated is not None
    assert updated.password_hash == "newhash_bcrypt_placeholder"
    assert updated.password_hash != original_hash


def test_update_password_returns_none_for_missing_user(db_session: Session) -> None:
    """
    update_password returns None when the user id does not exist.
    """
    repo = UserRepository(db_session)
    result = repo.update_password(999, "somehash")
    assert result is None


def test_update_profile_settings_risk_level(db_session: Session) -> None:
    """
    update_profile_settings changes risk_level when provided.
    """
    user_id = _create_user(db_session)
    repo = UserRepository(db_session)

    updated = repo.update_profile_settings(
        user_id=user_id, risk_level="aggressive", monthly_expenses=None
    )

    assert updated is not None
    assert updated.risk_level == "aggressive"
    assert updated.monthly_expenses == 0.0


def test_update_profile_settings_monthly_expenses(db_session: Session) -> None:
    """
    update_profile_settings changes monthly_expenses when provided.
    """
    user_id = _create_user(db_session)
    repo = UserRepository(db_session)

    updated = repo.update_profile_settings(
        user_id=user_id, risk_level=None, monthly_expenses=5000.0
    )

    assert updated is not None
    assert updated.monthly_expenses == 5000.0
    assert updated.risk_level == "moderate"


def test_update_profile_settings_both_fields(db_session: Session) -> None:
    """
    update_profile_settings applies both fields when both are provided.
    """
    user_id = _create_user(db_session)
    repo = UserRepository(db_session)

    updated = repo.update_profile_settings(
        user_id=user_id, risk_level="conservative", monthly_expenses=1200.0
    )

    assert updated is not None
    assert updated.risk_level == "conservative"
    assert updated.monthly_expenses == 1200.0


def test_update_profile_settings_returns_none_for_missing_user(
    db_session: Session,
) -> None:
    """
    update_profile_settings returns None when the user id does not exist.
    """
    repo = UserRepository(db_session)
    result = repo.update_profile_settings(
        user_id=999, risk_level="moderate", monthly_expenses=None
    )
    assert result is None
