"""FastAPI router for Bond endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.schemas.bonds import (
    BondAnalysisResponse,
    BondCreate,
    BondResponse,
    BondUpdate,
    BondsPortfolioSummaryResponse,
)
from app.services.bonds import BondService
from app.services.bond_calculation import BondCalculationService
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


@router.get("/{bond_id}/analysis", response_model=BondAnalysisResponse)
def get_bond_analysis(
    bond_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> BondAnalysisResponse:
    """Get detailed analysis for a single bond.

    Args:
        bond_id: The bond ID.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        Detailed bond analysis including value projection.

    Raises:
        404: If bond not found.
    """
    get_current_user(credentials, session)
    service = BondService(session)
    bond = service.get_bond(bond_id)
    if not bond:
        raise HTTPException(status_code=404, detail=f"Bond {bond_id} not found")
    return BondCalculationService.analyze_bond(bond)


@router.get("/portfolio/summary", response_model=BondsPortfolioSummaryResponse)
def get_bonds_portfolio_summary(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> BondsPortfolioSummaryResponse:
    """Get summary statistics for the bonds portfolio.

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        Portfolio summary with aggregated statistics.
    """
    get_current_user(credentials, session)
    service = BondService(session)
    bonds = service.list_bonds()
    # Convert BondResponse to Bond for calculation service
    from app.models.bonds import Bond

    bond_models = []
    for bond_resp in bonds:
        # Reconstruct Bond model from response
        bond_models.append(
            Bond(
                id=bond_resp.id,
                name=bond_resp.name,
                annual_rate=bond_resp.annual_rate,
                years=bond_resp.years,
                capitalization=bond_resp.capitalization,
                principal=bond_resp.principal,
                redemption_price=bond_resp.redemption_price,
                quantity=bond_resp.quantity,
                purchase_date=bond_resp.purchase_date,
                created_at=bond_resp.created_at,
                updated_at=bond_resp.updated_at,
            )
        )

    return BondCalculationService.calculate_portfolio_summary(bond_models)
