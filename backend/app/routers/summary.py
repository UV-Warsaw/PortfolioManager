"""Summary router — handles portfolio dashboard endpoints."""

import logging

from fastapi import APIRouter, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.repositories.user import UserRepository
from app.schemas.portfolio import (
    CryptoPricesResponse,
    DiversificationResponse,
    DividendSummaryResponse,
    DividendTimelineResponse,
    EmergencyFundResponse,
    PortfolioSummaryResponse,
    RiskAssessmentResponse,
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


@router.get("/risk", response_model=RiskAssessmentResponse)
def get_risk_assessment(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> RiskAssessmentResponse:
    """Return portfolio risk level compared against the user's declared preference.

    Classifies portfolio risk from asset-class weights:
      - Stocks + Crypto  → high risk
      - Real Estate      → medium risk
      - Bonds + Cash     → low risk

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        RiskAssessmentResponse with computed risk, preference, and alignment flag.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    current_user_info: dict = get_current_user(credentials, session)
    user = UserRepository(session).get_by_id(current_user_info["id"])
    user_preference: str = getattr(user, "risk_level", None) or "moderate"
    service = SummaryService(session)
    return service.get_risk_assessment(user_preference)


@router.get("/diversification", response_model=DiversificationResponse)
def get_diversification(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> DiversificationResponse:
    """Return concentration alerts and diversification recommendations.

    Flags any asset class exceeding 70% of total portfolio value. Returns at
    most three recommendations sorted by concentration severity.

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        DiversificationResponse with up to three recommendations and an
        ``is_diversified`` flag.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    from app.models.user import User

    _current_user: User = get_current_user(credentials, session)
    service = SummaryService(session)
    return service.get_diversification_recommendations()


@router.get("/emergency-fund", response_model=EmergencyFundResponse)
def get_emergency_fund(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> EmergencyFundResponse:
    """Return emergency fund adequacy based on cash + bonds vs monthly expenses.

    Thresholds: <3 months → critical, 3–6 months → good, >6 months → excellent.

    Args:
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        EmergencyFundResponse with months covered and status.

    Raises:
        HTTPException 401: Missing or invalid token.
    """
    current_user_info: dict = get_current_user(credentials, session)
    user = UserRepository(session).get_by_id(current_user_info["id"])
    monthly_expenses: float = getattr(user, "monthly_expenses", None) or 0.0
    service = SummaryService(session)
    return service.get_emergency_fund(monthly_expenses)


@router.get("/crypto-prices", response_model=CryptoPricesResponse)
def get_crypto_prices(
    currency: str = Query(default="PLN", max_length=10),
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> CryptoPricesResponse:
    """Return live BTC and ETH prices from CoinGecko.

    Args:
        currency: Target currency code (default PLN).
        session: Database session.
        credentials: Bearer token credentials.

    Returns:
        CryptoPricesResponse with BTC and ETH prices.

    Raises:
        HTTPException 401: Missing or invalid token.
        HTTPException 502: CoinGecko upstream request failed.
    """
    from fastapi import HTTPException, status

    from app.services.crypto_prices import fetch_crypto_prices

    _current_user = get_current_user(credentials, session)
    try:
        return fetch_crypto_prices(currency)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
