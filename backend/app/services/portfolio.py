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
    """Return net cost basis per account and aggregate total.

    Values represent the net capital invested per account (BUY amounts minus
    SELL amounts). All amounts are stored in PLN — USD transactions are
    converted at import time.

    Args:
        session: Database session.

    Returns:
        PortfolioValueResponse with per-account values and aggregate total.
    """
    repo = TransactionRepository(session)
    accounts = repo.get_account_values()
    total = round(sum(accounts.values()), 2)
    return PortfolioValueResponse(accounts=accounts, total=total)


def get_top_holdings(session: Session, limit: int = 10) -> TopHoldingsResponse:
    """Return the top holdings by net cost basis.

    Args:
        session: Database session.
        limit: Maximum number of holdings to return (default 10).

    Returns:
        TopHoldingsResponse with items ordered by cost_basis descending.
    """
    repo = TransactionRepository(session)
    rows = repo.get_top_holdings(limit=limit)
    items = [
        TopHoldingItem(ticker=ticker, cost_basis=cost_basis)
        for ticker, cost_basis in rows
    ]
    return TopHoldingsResponse(items=items)
