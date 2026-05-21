"""Password-reset service: request and confirm flows."""

import logging
import secrets
from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from ..core.config import settings
from ..repositories.password_reset import PasswordResetTokenRepository
from ..repositories.user import UserRepository
from ..services.auth import _hash_password  # reuse bcrypt helper
from ..services.email import send_password_reset_code

logger = logging.getLogger(__name__)

_CODE_DIGITS = 6


def request_password_reset(email: str, session: Session) -> None:
    """
    Initiate a password-reset flow for the given email address.

    Generates a secure 6-digit verification code, persists its hash, and
    dispatches the code via email (or logs it when SMTP is not configured).
    If the address is not registered the function returns silently to prevent
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

    raw_code = f"{secrets.randbelow(10 ** _CODE_DIGITS):0{_CODE_DIGITS}d}"
    expires_at = (
        datetime.now(UTC) + timedelta(hours=settings.password_reset_expire_hours)
    ).isoformat()

    repo = PasswordResetTokenRepository(session)
    repo.create(raw_token=raw_code, email=email, expires_at=expires_at)

    send_password_reset_code(email=email, code=raw_code)

    logger.info("Password reset code issued for %s", email)


def confirm_password_reset(
    email: str, raw_code: str, new_password: str, session: Session
) -> None:
    """
    Complete the password-reset flow by validating the 6-digit code and updating the password.

    Args:
        email: Email address the reset was requested for.
        raw_code: 6-digit verification code entered by the user.
        new_password: New plain-text password supplied by the user.
        session: Active database session.

    Raises:
        ValueError: If the code is invalid, expired, or already used.
    """
    repo = PasswordResetTokenRepository(session)
    record = repo.get_valid(raw_code=raw_code, email=email)

    if record is None:
        raise ValueError("Invalid or expired verification code")

    user_repo = UserRepository(session)
    user = user_repo.get_by_email(record.email)

    if user is None:
        raise ValueError("User account no longer exists")

    user.password_hash = _hash_password(new_password)
    session.add(user)
    session.commit()

    repo.mark_used(record)
    logger.info("Password reset completed for %s", record.email)
