"""Portfolio service — business logic for holdings calculation."""

import logging

from sqlmodel import Session

from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.schemas.portfolio import (
    HoldingRead,
    PortfolioValueResponse,
    TopHoldingItem,
    TopHoldingsResponse,
)

logger = logging.getLogger("portfolio_backend.services.portfolio")


def get_active_holdings(
    session: Session, account: str | None = None, user_id: int | None = None
) -> list[HoldingRead]:
    """Return active holdings for the given user."""
    repo = TransactionRepository(session)
    raw = repo.get_holdings(account=account, user_id=user_id)
    holdings = [
        HoldingRead(ticker=r["ticker"], account=r["account"], quantity=r["quantity"])
        for r in raw
    ]
    return sorted(holdings, key=lambda h: (h.account, h.ticker))


def get_portfolio_value(session: Session, user_id: int | None = None) -> PortfolioValueResponse:
    """Return current market value per account for the given user."""
    repo = TransactionRepository(session)
    accounts = repo.get_account_values(user_id=user_id)
    total = round(sum(accounts.values()), 2)

    cost_basis = repo.get_cost_basis(user_id=user_id)
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


def get_top_holdings(session: Session, limit: int = 10, user_id: int | None = None) -> TopHoldingsResponse:
    """Return the top holdings by current market value for the given user."""
    repo = TransactionRepository(session)
    rows = repo.get_top_holdings(limit=limit, user_id=user_id)
    items = [
        TopHoldingItem(ticker=ticker, cost_basis=cost_basis)
        for ticker, cost_basis in rows
    ]
    return TopHoldingsResponse(items=items)


def get_dividend_summary(session: Session, account: str | None = None, user_id: int | None = None) -> list[dict]:
    """Get dividend summary grouped by year for the given user."""
    repo = DividendRepository(session)
    return repo.get_yearly_summary(account=account, user_id=user_id)


def get_dividend_timeline(
    session: Session, year: int | None = None, account: str | None = None, user_id: int | None = None
) -> list[dict]:
    """Get dividend timeline by month for the given user."""
    repo = DividendRepository(session)
    return repo.get_monthly_timeline(year=year, account=account, user_id=user_id)
