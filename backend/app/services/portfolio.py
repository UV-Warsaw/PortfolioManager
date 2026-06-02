"""Portfolio service — business logic for holdings calculation."""

import logging

from sqlmodel import Session

from app.repositories.portfolio import TransactionRepository
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
    
    # Also calculate cost basis and profit %
    cost_basis = repo.get_cost_basis()
    profit_data = {}
    for account, market_value in accounts.items():
        cost = cost_basis.get(account, 0)
        profit = round(market_value - cost, 2)
        profit_pct = round((profit / cost * 100) if cost > 0 else 0, 2)
        profit_data[account] = {
            "market_value": market_value,
            "cost_basis": cost,
            "profit": profit,
            "profit_percentage": profit_pct,
        }
    
    # For backward compatibility, return simple accounts dict, but add profit data
    response = PortfolioValueResponse(accounts=accounts, total=total)
    response.profit_data = profit_data  # type: ignore
    return response


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
