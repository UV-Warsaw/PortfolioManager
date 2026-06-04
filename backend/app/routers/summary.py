"""Summary router — handles portfolio dashboard endpoints."""

import logging

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.schemas.portfolio import (
    DividendSummaryResponse,
    DividendTimelineResponse,
    PortfolioSummaryResponse,
    WealthSummaryResponse,
)
from app.services.auth import get_current_user
from app.services.summary import SummaryService

logger = logging.getLogger("portfolio_backend.routers.summary")

router = APIRouter(prefix="/summary", tags=["summary"])
_bearer = HTTPBearer()


@router.get("/dashboard", response_model=PortfolioSummaryResponse)
def get_dashboard(
    account: str | None = Query(
        default=None, description="Filter by account: IKE, PLN, USD"
    ),
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> PortfolioSummaryResponse:
    """Return portfolio summary for dashboard display.

    Includes total portfolio value, total invested, profit, and top 10 holdings.

    Args:
        account: Optional account filter.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        PortfolioSummaryResponse with portfolio metrics and top holdings.

    Raises:
        HTTPException 401: Missing or invalid token.
        HTTPException 400: Invalid account value.
    """
    from app.models.user import User

    _current_user: User = get_current_user(credentials, session)
    service = SummaryService(session)
    return PortfolioSummaryResponse(**service.get_portfolio_summary(account=account))


@router.get("/dividends/yearly", response_model=list[DividendSummaryResponse])
def get_dividend_yearly_summary(
    account: str | None = Query(
        default=None, description="Filter by account: IKE, PLN, USD"
    ),
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> list[DividendSummaryResponse]:
    """Return yearly dividend summary.

    Args:
        account: Optional account filter.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        List of DividendSummaryResponse ordered by year.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    from app.models.user import User

    _current_user: User = get_current_user(credentials, session)
    service = SummaryService(session)
    return service.get_dividend_yearly_summary(account=account)


@router.get("/dividends/timeline", response_model=list[DividendTimelineResponse])
def get_dividend_timeline(
    year: int | None = Query(default=None, description="Filter by year (optional)"),
    account: str | None = Query(
        default=None, description="Filter by account: IKE, PLN, USD"
    ),
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> list[DividendTimelineResponse]:
    """Return monthly dividend timeline.

    Args:
        year: Optional year filter — returns 12 months for that year.
        account: Optional account filter.
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        List of DividendTimelineResponse ordered by month.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    from app.models.user import User

    _current_user: User = get_current_user(credentials, session)
    service = SummaryService(session)
    return service.get_dividend_monthly_timeline(year=year, account=account)


@router.get("/wealth", response_model=WealthSummaryResponse)
def get_wealth_summary(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> WealthSummaryResponse:
    """Return total portfolio wealth aggregated across all asset classes.

    Combines stocks, bonds, cash, crypto, and real estate (net equity).

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        WealthSummaryResponse with total value and per-class breakdown.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    from app.models.user import User

    _current_user: User = get_current_user(credentials, session)
    service = SummaryService(session)
    return service.get_wealth_summary()
