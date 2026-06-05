"""FastAPI router for Cash Account endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.schemas.cash import (
    CashAnalysisResponse,
    CashCreate,
    CashPortfolioSummaryResponse,
    CashResponse,
    CashUpdate,
)
from app.services.auth import get_current_user
from app.services.cash import CashService

router = APIRouter(prefix="/portfolio/cash", tags=["cash"])
_bearer = HTTPBearer()


@router.post("", response_model=CashResponse, status_code=201)
def create_cash_account(
    data: CashCreate,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CashResponse:
    """Create a new cash account.

    Raises:
        400: If an account with the same name already exists.
    """
    current_user = get_current_user(credentials, session)
    try:
        return CashService(session, current_user["id"]).create(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[CashResponse])
def list_cash_accounts(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> list[CashResponse]:
    """Get all cash accounts."""
    current_user = get_current_user(credentials, session)
    return CashService(session, current_user["id"]).list_all()


@router.get("/summary", response_model=CashPortfolioSummaryResponse)
def get_portfolio_summary(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CashPortfolioSummaryResponse:
    """Get aggregated cash portfolio summary."""
    current_user = get_current_user(credentials, session)
    return CashService(session, current_user["id"]).portfolio_summary()


@router.get("/{account_id}", response_model=CashResponse)
def get_cash_account(
    account_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CashResponse:
    """Get a single cash account by ID.

    Raises:
        404: If account not found.
    """
    current_user = get_current_user(credentials, session)
    account = CashService(session, current_user["id"]).get(account_id)
    if not account:
        raise HTTPException(
            status_code=404, detail=f"Cash account {account_id} not found"
        )
    return account


@router.get("/{account_id}/analysis", response_model=CashAnalysisResponse)
def get_cash_account_analysis(
    account_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CashAnalysisResponse:
    """Get interest analysis for a cash account.

    Raises:
        404: If account not found.
    """
    current_user = get_current_user(credentials, session)
    analysis = CashService(session, current_user["id"]).analyze(account_id)
    if not analysis:
        raise HTTPException(
            status_code=404, detail=f"Cash account {account_id} not found"
        )
    return analysis


@router.put("/{account_id}", response_model=CashResponse)
def update_cash_account(
    account_id: int,
    data: CashUpdate,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CashResponse:
    """Update a cash account.

    Raises:
        400: If updating name to one that already exists.
        404: If account not found.
    """
    current_user = get_current_user(credentials, session)
    try:
        account = CashService(session, current_user["id"]).update(account_id, data)
        if not account:
            raise HTTPException(
                status_code=404, detail=f"Cash account {account_id} not found"
            )
        return account
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{account_id}", status_code=204)
def delete_cash_account(
    account_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> None:
    """Delete a cash account.

    Raises:
        404: If account not found.
    """
    current_user = get_current_user(credentials, session)
    if not CashService(session, current_user["id"]).delete(account_id):
        raise HTTPException(
            status_code=404, detail=f"Cash account {account_id} not found"
        )
