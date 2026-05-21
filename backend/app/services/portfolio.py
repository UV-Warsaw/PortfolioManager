"""Portfolio service — business logic for holdings calculation."""

import logging

from sqlmodel import Session

from app.repositories.portfolio import TransactionRepository
from app.schemas.portfolio import HoldingRead

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
