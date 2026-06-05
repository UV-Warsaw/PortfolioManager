"""Repository layer for Bond database operations."""

from sqlmodel import Session, select

from app.models.bonds import Bond
from app.repositories.base import BaseRepository


class BondRepository(BaseRepository[Bond]):
    """Repository for managing Bond database operations."""

    def __init__(self, session: Session) -> None:
        """Initialize bond repository with session.

        Args:
            session: Active database session.
        """
        super().__init__(Bond, session)

    def get_by_name(self, name: str, user_id: int) -> Bond | None:
        """
        Get a bond by its name scoped to the given user.
        """
        stmt = select(Bond).where(Bond.name == name, Bond.user_id == user_id)
        return self.session.exec(stmt).first()

    def list_all(self, user_id: int) -> list[Bond]:
        """Get all bonds for the given user ordered by purchase date (newest first)."""
        stmt = select(Bond).where(Bond.user_id == user_id).order_by(Bond.purchase_date.desc())
        return self.session.exec(stmt).all()

    def get_total_value(self, user_id: int) -> float:
        """Calculate total market value of bonds for the given user."""
        bonds = self.list_all(user_id)
        total = 0.0
        for bond in bonds:
            price = bond.redemption_price if bond.redemption_price else bond.principal
            total += price * bond.quantity
        return round(total, 2)

    def get_by_id_for_user(self, bond_id: int, user_id: int) -> Bond | None:
        """Get a bond by ID scoped to the given user."""
        bond = self.session.get(Bond, bond_id)
        if bond is None or bond.user_id != user_id:
            return None
        return bond
