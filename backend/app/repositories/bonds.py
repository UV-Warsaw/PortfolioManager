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

    def get_by_name(self, name: str) -> Bond | None:
        """Get a bond by its name.

        Args:
            name: The bond name to search for.

        Returns:
            The Bond if found, None otherwise.
        """
        stmt = select(Bond).where(Bond.name == name)
        return self.session.exec(stmt).first()

    def list_all(self) -> list[Bond]:
        """Get all bonds ordered by purchase date (newest first).

        Returns:
            List of all bonds in descending purchase date order.
        """
        stmt = select(Bond).order_by(Bond.purchase_date.desc())
        return self.session.exec(stmt).all()

    def get_total_value(self) -> float:
        """Calculate total market value of all bonds.

        Returns:
            Sum of current_price * quantity for all bonds,
            or purchase_price if current_price is NULL.
        """
        bonds = self.list_all()
        total = 0.0
        for bond in bonds:
            price = bond.current_price if bond.current_price else bond.purchase_price
            total += price * bond.quantity
        return round(total, 2)

    def get_by_id_for_user(self, bond_id: int) -> Bond | None:
        """Get a bond by ID (basic retrieval).

        Args:
            bond_id: The bond ID.

        Returns:
            The Bond if found, None otherwise.
        """
        return self.session.get(Bond, bond_id)
