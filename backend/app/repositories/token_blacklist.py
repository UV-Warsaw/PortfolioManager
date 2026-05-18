"""Repository for token blacklist operations."""

from sqlmodel import Session, select

from ..models.token_blacklist import TokenBlacklist


class TokenBlacklistRepository:
    """Database access layer for token blacklist operations."""

    def __init__(self, session: Session) -> None:
        """
        Initialize repository with a database session.

        Args:
            session: SQLModel database session.
        """
        self._session = session

    def add(self, token: str, blacklisted_at: str, expires_at: str) -> TokenBlacklist:
        """
        Add a token to the blacklist.

        Args:
            token: JWT token string to blacklist.
            blacklisted_at: ISO timestamp when token was blacklisted.
            expires_at: ISO timestamp when token expires.

        Returns:
            Created TokenBlacklist record.
        """
        entry = TokenBlacklist(
            token=token,
            blacklisted_at=blacklisted_at,
            expires_at=expires_at,
        )
        self._session.add(entry)
        self._session.commit()
        self._session.refresh(entry)
        return entry

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is in the blacklist.

        Args:
            token: JWT token string to check.

        Returns:
            True if token is blacklisted, False otherwise.
        """
        stmt = select(TokenBlacklist).where(TokenBlacklist.token == token)
        result = self._session.exec(stmt).first()
        return result is not None

    def cleanup_expired(self, current_time: str) -> int:
        """
        Remove expired tokens from the blacklist.

        Args:
            current_time: Current ISO timestamp for comparison.

        Returns:
            Number of tokens removed.
        """
        stmt = select(TokenBlacklist).where(TokenBlacklist.expires_at < current_time)
        expired = self._session.exec(stmt).all()
        count = len(expired)
        for entry in expired:
            self._session.delete(entry)
        self._session.commit()
        return count
