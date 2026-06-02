"""Portfolio service — business logic for holdings calculation."""

import logging

from sqlmodel import Session

from app.repositories.portfolio import TransactionRepository, DividendRepository
from app.schemas.portfolio import (
    HoldingRead,
    PortfolioValueResponse,
    TopHoldingItem,
    TopHoldingsResponse,
)

logger = logging.getLogger("portfolio_backend.services.portfolio")


def get_active_holdings(
    session: Session, account: str | None = None
) -> list[HoldingRead]:
    """Return active holdings for a given account, or all accounts if none specified.

    Holdings with net quantity <= 0 (fully sold positions) are excluded.

    Args:
        session: Database session.
        account: Optional account filter — IKE, PLN, or USD.

    Returns:
        Sorted list of HoldingRead objects with positive net quantities.
    """
    repo = TransactionRepository(session)
    raw = repo.get_holdings(account=account)
    holdings = [
        HoldingRead(ticker=r["ticker"], account=r["account"], quantity=r["quantity"])
        for r in raw
    ]
    return sorted(holdings, key=lambda h: (h.account, h.ticker))


def get_portfolio_value(session: Session) -> PortfolioValueResponse:
    """Return current market value per account and aggregate total.

    Values represent sum(market_price * quantity) per account for open BUY
    positions. All prices are stored in PLN — USD transactions are converted
    at import time.

    Args:
        session: Database session.

    Returns:
        PortfolioValueResponse with per-account market values and aggregate total.
    """
    repo = TransactionRepository(session)
    accounts = repo.get_account_values()
    total = round(sum(accounts.values()), 2)
    return PortfolioValueResponse(accounts=accounts, total=total)


def get_top_holdings(session: Session, limit: int = 10) -> TopHoldingsResponse:
    """Return the top holdings by current market value.

    Args:
        session: Database session.
        limit: Maximum number of holdings to return (default 10).

    Returns:
        TopHoldingsResponse with items ordered by market value descending.
    """
    repo = TransactionRepository(session)
    rows = repo.get_top_holdings(limit=limit)
    items = [
        TopHoldingItem(ticker=ticker, cost_basis=cost_basis)
        for ticker, cost_basis in rows
    ]
    return TopHoldingsResponse(items=items)


def get_dividend_summary(
    session: Session, account: str | None = None
) -> list[dict]:
    """Get dividend summary grouped by year.

    Args:
        session: Database session.
        account: Optional account filter (IKE, PLN, USD).

    Returns:
        List of dicts with 'year' and 'total' keys.
    """
    repo = DividendRepository(session)
    return repo.get_yearly_summary(account=account)


def get_dividend_timeline(
    session: Session, year: int | None = None, account: str | None = None
) -> list[dict]:
    """Get dividend timeline by month.

    Args:
        session: Database session.
        year: Optional year filter — returns 12 months for that year.
        account: Optional account filter (IKE, PLN, USD).

    Returns:
        List of dicts with 'month' and 'total' keys.
    """
    repo = DividendRepository(session)
    return repo.get_monthly_timeline(year=year, account=account)
