"""FastAPI router for Bond endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.schemas.bonds import BondCreate, BondResponse, BondUpdate
from app.services.bonds import BondService
from app.services.auth import get_current_user

router = APIRouter(prefix="/portfolio/bonds", tags=["bonds"])
_bearer = HTTPBearer()


@router.post("", response_model=BondResponse, status_code=201)
def create_bond(
    bond_data: BondCreate,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> BondResponse:
    """Create a new bond.

    Args:
        bond_data: The bond data to create.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        The created bond.

    Raises:
        400: If a bond with the same name already exists.
    """
    get_current_user(credentials, session)
    try:
        service = BondService(session)
        return service.create_bond(bond_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[BondResponse])
def list_bonds(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> list[BondResponse]:
    """Get all bonds.

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        List of all bonds.
    """
    get_current_user(credentials, session)
    service = BondService(session)
    return service.list_bonds()


@router.get("/{bond_id}", response_model=BondResponse)
def get_bond(
    bond_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> BondResponse:
    """Get a single bond by ID.

    Args:
        bond_id: The bond ID.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        The bond.

    Raises:
        404: If bond not found.
    """
    get_current_user(credentials, session)
    service = BondService(session)
    bond = service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail=f"Bond {bond_id} not found")
    return bond


@router.put("/{bond_id}", response_model=BondResponse)
def update_bond(
    bond_id: int,
    bond_data: BondUpdate,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> BondResponse:
    """Update an existing bond.

    Args:
        bond_id: The bond ID to update.
        bond_data: The updated bond data.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        The updated bond.

    Raises:
        404: If bond not found.
        400: If updating to a duplicate name.
    """
    get_current_user(credentials, session)
    try:
        service = BondService(session)
        bond = service.update_bond(bond_id, bond_data)
        if not bond:
            raise HTTPException(status_code=404, detail=f"Bond {bond_id} not found")
        return bond
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{bond_id}", status_code=204)
def delete_bond(
    bond_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> None:
    """Delete a bond by ID.

    Args:
        bond_id: The bond ID to delete.
        session: Database session.
        credentials: Bearer token credentials.

    Raises:
        404: If bond not found.
    """
    get_current_user(credentials, session)
    service = BondService(session)
    if not service.delete_bond(bond_id):
        raise HTTPException(status_code=404, detail=f"Bond {bond_id} not found")
