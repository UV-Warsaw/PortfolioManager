"""Password-reset service: request and confirm flows."""

import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from ..core.config import settings
from ..repositories.password_reset import PasswordResetTokenRepository
from ..repositories.user import UserRepository
from ..services.auth import _hash_password  # reuse bcrypt helper
from ..services.email import send_password_reset_email

logger = logging.getLogger(__name__)

_RESET_PATH = "/reset-password"


def request_password_reset(email: str, session: Session) -> None:
    """
    Initiate a password-reset flow for the given email address.

    Generates a secure one-time token, persists its hash, and dispatches a
    reset email.  If the address is not registered the function returns
    silently — the response is identical to the success case to prevent
    account enumeration.

    Args:
        email: Email address submitted by the user.
        session: Active database session.
    """
    user_repo = UserRepository(session)
    user = user_repo.get_by_email(email)

    if user is None:
        logger.debug("Password reset requested for unknown email: %s", email)
        return

    raw_token = secrets.token_urlsafe(32)
    expires_at = (
        datetime.now(UTC) + timedelta(hours=settings.password_reset_expire_hours)
    ).isoformat()

    repo = PasswordResetTokenRepository(session)
    repo.create(raw_token=raw_token, email=email, expires_at=expires_at)

    reset_url = f"{settings.frontend_url}{_RESET_PATH}?token={raw_token}"
    send_password_reset_email(email=email, reset_url=reset_url)

    logger.info("Password reset token issued for %s", email)


def confirm_password_reset(raw_token: str, new_password: str, session: Session) -> None:
    """
    Complete the password-reset flow by validating the token and updating the password.

    Args:
        raw_token: Token from the reset link query parameter.
        new_password: New plain-text password supplied by the user.
        session: Active database session.

    Raises:
        ValueError: If the token is invalid, expired, or already used.
    """
    repo = PasswordResetTokenRepository(session)
    record = repo.get_valid(raw_token)

    if record is None:
        raise ValueError("Invalid or expired password reset token")

    user_repo = UserRepository(session)
    user = user_repo.get_by_email(record.email)

    if user is None:
        raise ValueError("User account no longer exists")

    user.password_hash = _hash_password(new_password)
    session.add(user)
    session.commit()

    repo.mark_used(record)
    logger.info("Password reset completed for %s", record.email)
