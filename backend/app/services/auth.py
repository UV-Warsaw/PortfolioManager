"""Authentication service: registration and JWT token creation."""

from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session

from ..core.config import settings
from ..repositories.user import UserRepository

_ALGORITHM = "HS256"
_TOKEN_EXPIRE_DAYS = 30

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    """
    Hash a plain-text password with bcrypt.

    Args:
        password: Plain-text password.

    Returns:
        Bcrypt hash string.
    """
    return _pwd_context.hash(password)


def _create_access_token(email: str) -> str:
    """
    Create a signed JWT access token for the given email.

    Args:
        email: User email to embed as the token subject.

    Returns:
        Encoded JWT string.
    """
    expire = datetime.now(UTC) + timedelta(days=_TOKEN_EXPIRE_DAYS)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def register_user(email: str, password: str, session: Session) -> dict:
    """
    Register a new user account.

    Hashes the password, creates the user row with default settings,
    and returns a JWT access token so the caller is immediately authenticated.

    Args:
        email: Unique email address for the new account.
        password: Plain-text password (minimum 8 characters enforced by schema).
        session: Active database session.

    Returns:
        dict with id, email, access_token, token_type.

    Raises:
        ValueError: If an account with the given email already exists.
    """
    repo = UserRepository(session)

    if repo.get_by_email(email) is not None:
        raise ValueError("Account with this email already exists")

    password_hash = _hash_password(password)
    created_at = datetime.now(UTC).isoformat()
    user = repo.create(email=email, password_hash=password_hash, created_at=created_at)

    access_token = _create_access_token(email)

    return {
        "id": user.id,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }
