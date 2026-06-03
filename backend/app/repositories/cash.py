"""Repository layer for CashAccount database operations."""

from sqlmodel import Session, select

from app.models.cash import CashAccount
from app.repositories.base import BaseRepository


class CashRepository(BaseRepository[CashAccount]):
    """Repository for managing CashAccount database operations."""

    def __init__(self, session: Session) -> None:
        """Initialize cash repository with session.

        Args:
            session: Active database session.
        """
        super().__init__(CashAccount, session)

    def list_all(self) -> list[CashAccount]:
        """Get all cash accounts ordered by creation date (newest first).

        Returns:
            List of all cash accounts.
        """
        stmt = select(CashAccount).order_by(CashAccount.created_at.desc())
        return list(self.session.exec(stmt).all())

    def get_by_name(self, name: str) -> CashAccount | None:
        """Get a cash account by its name.

        Args:
            name: The account name to search for.

        Returns:
            The CashAccount if found, None otherwise.
        """
        stmt = select(CashAccount).where(CashAccount.name == name)
        return self.session.exec(stmt).first()
