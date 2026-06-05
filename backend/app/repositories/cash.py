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

    def list_all(self, user_id: int) -> list[CashAccount]:
        """Get all cash accounts for the given user ordered by creation date."""
        stmt = select(CashAccount).where(CashAccount.user_id == user_id).order_by(CashAccount.created_at.desc())
        return list(self.session.exec(stmt).all())

    def get_by_name(self, name: str, user_id: int) -> CashAccount | None:
        """Get a cash account by name scoped to the given user."""
        stmt = select(CashAccount).where(CashAccount.name == name, CashAccount.user_id == user_id)
        return self.session.exec(stmt).first()
