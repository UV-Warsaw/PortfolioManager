"""Authentication service: registration, login, logout and JWT token management."""

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from ..core.config import settings
from ..core.database import get_db
from ..repositories.token_blacklist import TokenBlacklistRepository
from ..repositories.user import UserRepository

_ALGORITHM = "HS256"

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer_scheme = HTTPBearer()


def _hash_password(password: str) -> str:
    """
    Hash a plain-text password with bcrypt.

    Args:
        password: Plain-text password.

    Returns:
        Bcrypt hash string.
    """
    return _pwd_context.hash(password)


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its hash.

    Args:
        plain_password: Plain-text password to verify.
        hashed_password: Bcrypt hash to verify against.

    Returns:
        True if password matches, False otherwise.
    """
    return _pwd_context.verify(plain_password, hashed_password)


def _create_access_token(email: str) -> tuple[str, datetime]:
    """
    Create a signed JWT access token for the given email.

    Args:
        email: User email to embed as the token subject.

    Returns:
        Tuple of (encoded JWT string, expiration datetime).
    """
    expire = datetime.now(UTC) + timedelta(hours=settings.access_token_expire_hours)
    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)
    return token, expire


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string to decode.

    Returns:
        Decoded token payload.

    Raises:
        JWTError: If token is invalid or expired.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])


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

    access_token, _ = _create_access_token(email)

    return {
        "id": user.id,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }


def login_user(email: str, password: str, session: Session) -> dict:
    """
    Authenticate a user and return access token.

    Args:
        email: User email address.
        password: Plain-text password.
        session: Active database session.

    Returns:
        dict with id, email, access_token, token_type.

    Raises:
        ValueError: If credentials are invalid.
    """
    repo = UserRepository(session)
    user = repo.get_by_email(email)

    if user is None or not _verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    access_token, _ = _create_access_token(email)

    return {
        "id": user.id,
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }


def logout_user(token: str, session: Session) -> None:
    """
    Invalidate a token by adding it to the blacklist.

    Args:
        token: JWT token to invalidate.
        session: Active database session.

    Raises:
        ValueError: If token is invalid.
    """
    try:
        payload = decode_token(token)
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            expires_at = datetime.fromtimestamp(exp_timestamp, tz=UTC).isoformat()
        else:
            expires_at = datetime.now(UTC).isoformat()
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    blacklist_repo = TokenBlacklistRepository(session)
    blacklisted_at = datetime.now(UTC).isoformat()
    blacklist_repo.add(
        token=token, blacklisted_at=blacklisted_at, expires_at=expires_at
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    session: Session = Depends(get_db),
) -> dict:
    """
    FastAPI dependency to get current authenticated user from JWT token.

    Validates the token, checks it's not blacklisted, and returns user info.

    Args:
        credentials: Bearer token from Authorization header.
        session: Active database session.

    Returns:
        dict with user id and email.

    Raises:
        HTTPException 401: If token is invalid, expired, or blacklisted.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    blacklist_repo = TokenBlacklistRepository(session)
    if blacklist_repo.is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository(session)
    user = user_repo.get_by_email(email)
    if user is None:
        raise credentials_exception

    return {"id": user.id, "email": user.email}
