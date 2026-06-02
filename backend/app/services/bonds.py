"""Service layer for Bond business logic."""

from datetime import datetime

from sqlmodel import Session

from app.models.bonds import Bond
from app.repositories.bonds import BondRepository
from app.schemas.bonds import BondCreate, BondResponse, BondUpdate


class BondService:
    """Service for Bond business operations."""

    def __init__(self, session: Session):
        """Initialize BondService.

        Args:
            session: SQLModel database session.
        """
        self.repo = BondRepository(session)
        self.session = session

    def create_bond(self, data: BondCreate) -> BondResponse:
        """Create a new bond.

        Args:
            data: Bond creation data.

        Returns:
            The created bond as BondResponse.

        Raises:
            ValueError: If a bond with the same name already exists.
        """
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise ValueError(f"Bond '{data.name}' already exists")

        bond = Bond(
            name=data.name,
            interest_rate=data.interest_rate,
            interest_period_years=data.interest_period_years,
            capitalization=data.capitalization,
            purchase_price=data.purchase_price,
            current_price=data.current_price,
            quantity=data.quantity,
            purchase_date=data.purchase_date,
        )
        self.repo.create(bond)
        return BondResponse.from_attributes(bond)

    def get_bond(self, bond_id: int) -> BondResponse | None:
        """Get a single bond by ID.

        Args:
            bond_id: The bond ID.

        Returns:
            The bond as BondResponse, or None if not found.
        """
        bond = self.repo.get_by_id_for_user(bond_id)
        return BondResponse.from_attributes(bond) if bond else None

    def list_bonds(self) -> list[BondResponse]:
        """Get all bonds.

        Returns:
            List of all bonds as BondResponse objects.
        """
        bonds = self.repo.list_all()
        return [BondResponse.from_attributes(b) for b in bonds]

    def update_bond(self, bond_id: int, data: BondUpdate) -> BondResponse | None:
        """Update an existing bond.

        Args:
            bond_id: The bond ID to update.
            data: Partial bond data to update.

        Returns:
            The updated bond as BondResponse, or None if not found.

        Raises:
            ValueError: If updating name to one that already exists.
        """
        bond = self.repo.get_by_id_for_user(bond_id)
        if not bond:
            return None

        # Check if updating to existing name
        if data.name and data.name != bond.name:
            existing = self.repo.get_by_name(data.name)
            if existing:
                raise ValueError(f"Bond '{data.name}' already exists")

        # Update fields
        if data.name is not None:
            bond.name = data.name
        if data.interest_rate is not None:
            bond.interest_rate = data.interest_rate
        if data.interest_period_years is not None:
            bond.interest_period_years = data.interest_period_years
        if data.capitalization is not None:
            bond.capitalization = data.capitalization
        if data.purchase_price is not None:
            bond.purchase_price = data.purchase_price
        if data.current_price is not None:
            bond.current_price = data.current_price
        if data.quantity is not None:
            bond.quantity = data.quantity
        if data.purchase_date is not None:
            bond.purchase_date = data.purchase_date

        bond.updated_at = datetime.now()
        self.repo.update(bond)
        return BondResponse.from_attributes(bond)

    def delete_bond(self, bond_id: int) -> bool:
        """Delete a bond by ID.

        Args:
            bond_id: The bond ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        bond = self.repo.get_by_id_for_user(bond_id)
        if not bond:
            return False
        self.repo.delete(bond)
        return True

    def get_total_value(self) -> float:
        """Get the total market value of all bonds.

        Returns:
            Total value (current_price * quantity for all bonds).
        """
        return self.repo.get_total_value()
