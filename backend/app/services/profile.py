"""Profile service: get, update email, update password, update settings."""

from passlib.context import CryptContext
from sqlmodel import Session

from ..repositories.user import UserRepository
from ..schemas.profile import ProfileResponse

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    """
    Hash a plain-text password with bcrypt.

    Args:
        password: Plain-text password string.

    Returns:
        Bcrypt hash string.
    """
    return _pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its bcrypt hash.

    Args:
        plain_password: Plain-text password to verify.
        hashed_password: Bcrypt hash to compare against.

    Returns:
        True if password matches, False otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)


def _user_to_profile(user: object) -> ProfileResponse:
    """
    Convert a User ORM instance to a ProfileResponse schema.

    Args:
        user: User ORM instance with id, email, risk_level,
              monthly_expenses, and created_at fields.

    Returns:
        ProfileResponse: Serialisable profile data.
    """
    return ProfileResponse(
        id=user.id,  # type: ignore[attr-defined]
        email=user.email,  # type: ignore[attr-defined]
        risk_level=user.risk_level,  # type: ignore[attr-defined]
        monthly_expenses=user.monthly_expenses,  # type: ignore[attr-defined]
        created_at=user.created_at,  # type: ignore[attr-defined]
    )


def get_profile(user_id: int, session: Session) -> ProfileResponse:
    """
    Return the full profile for the authenticated user.

    Args:
        user_id: Primary key of the user.
        session: Active database session.

    Returns:
        ProfileResponse: Current profile data.

    Raises:
        ValueError: If the user does not exist.
    """
    repo = UserRepository(session)
    user = repo.get_by_id(user_id)
    if user is None:
        raise ValueError("User not found")
    return _user_to_profile(user)


def update_email(
    user_id: int,
    current_password: str,
    new_email: str,
    session: Session,
) -> ProfileResponse:
    """
    Change the email address after verifying the current password.

    Args:
        user_id: Primary key of the user.
        current_password: Plain-text password to authenticate the request.
        new_email: New email address to set.
        session: Active database session.

    Returns:
        ProfileResponse: Updated profile data.

    Raises:
        ValueError: If the user does not exist, current password is wrong,
                    or the new email is already taken.
    """
    repo = UserRepository(session)
    user = repo.get_by_id(user_id)
    if user is None:
        raise ValueError("User not found")

    if not _verify_password(current_password, user.password_hash):
        raise ValueError("Current password is incorrect")

    existing = repo.get_by_email(new_email)
    if existing is not None and existing.id != user_id:
        raise ValueError("Email address is already in use")

    updated = repo.update_email(user_id, new_email)
    if updated is None:
        raise ValueError("User not found")
    return _user_to_profile(updated)


def update_password(
    user_id: int,
    current_password: str,
    new_password: str,
    confirm_password: str,
    session: Session,
) -> None:
    """
    Change the account password after verifying the current password.

    Args:
        user_id: Primary key of the user.
        current_password: Plain-text current password to authenticate the request.
        new_password: New plain-text password.
        confirm_password: Must match new_password exactly.
        session: Active database session.

    Raises:
        ValueError: If the user does not exist, current password is wrong,
                    or new_password and confirm_password do not match.
    """
    if new_password != confirm_password:
        raise ValueError("New password and confirmation do not match")

    repo = UserRepository(session)
    user = repo.get_by_id(user_id)
    if user is None:
        raise ValueError("User not found")

    if not _verify_password(current_password, user.password_hash):
        raise ValueError("Current password is incorrect")

    new_hash = _hash_password(new_password)
    repo.update_password(user_id, new_hash)


def update_profile_settings(
    user_id: int,
    risk_level: str | None,
    monthly_expenses: float | None,
    session: Session,
) -> ProfileResponse:
    """
    Update risk level and/or monthly expenses for the authenticated user.

    Only fields that are not None are applied.

    Args:
        user_id: Primary key of the user.
        risk_level: New risk level, or None to leave unchanged.
        monthly_expenses: New monthly expenses in PLN, or None to leave unchanged.
        session: Active database session.

    Returns:
        ProfileResponse: Updated profile data.

    Raises:
        ValueError: If the user does not exist or no fields are provided.
    """
    if risk_level is None and monthly_expenses is None:
        raise ValueError("At least one field must be provided")

    repo = UserRepository(session)
    updated = repo.update_profile_settings(
        user_id=user_id,
        risk_level=risk_level,
        monthly_expenses=monthly_expenses,
    )
    if updated is None:
        raise ValueError("User not found")
    return _user_to_profile(updated)
