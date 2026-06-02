"""Summary service — business logic for portfolio dashboard."""

import logging
from datetime import datetime

from sqlmodel import Session, func, select

from app.models.portfolio import Dividend, Transaction
from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.schemas.portfolio import (
    DividendSummaryResponse,
    DividendTimelineResponse,
)

logger = logging.getLogger("portfolio_backend.services.summary")


class SummaryService:
    """Service for portfolio summary and dashboard data."""

    def __init__(self, session: Session) -> None:
        """Initialize summary service with a database session."""
        self.session = session
        self.tx_repo = TransactionRepository(session)
        self.div_repo = DividendRepository(session)

    def get_portfolio_summary(self, account: str | None = None) -> dict:
        """Get complete portfolio summary for dashboard.

        Returns total value, total invested, total profit, and top holdings.

        Args:
            account: Optional account filter (IKE, PLN, USD).

        Returns:
            Dict with portfolio_value, total_invested, profit, and top_holdings.
        """
        accounts = self.tx_repo.get_account_values()
        top_holdings = self.tx_repo.get_top_holdings(limit=10)
        holdings = self.tx_repo.get_holdings(account=account)

        portfolio_value = sum(accounts.values())

        total_invested = 0.0
        for holding in holdings:
            stmt = select(func.sum(Transaction.amount)).where(
                Transaction.ticker == holding["ticker"],
                Transaction.type == "BUY",
                Transaction.account == holding["account"],
            )
            if account:
                stmt = stmt.where(Transaction.account == account)
            result = self.session.exec(stmt).first()
            total_invested += float(result) if result else 0.0

        profit = portfolio_value - total_invested

        return {
            "portfolio_value": round(portfolio_value, 2),
            "total_invested": round(total_invested, 2),
            "profit": round(profit, 2),
            "profit_percentage": round(
                (profit / total_invested * 100) if total_invested > 0 else 0, 2
            ),
            "top_holdings": [
                {"ticker": ticker, "value": round(value, 2)}
                for ticker, value in top_holdings[:10]
            ],
        }

    def get_dividend_yearly_summary(
        self, account: str | None = None
    ) -> list[DividendSummaryResponse]:
        """Get yearly dividend summary.

        Args:
            account: Optional account filter (IKE, PLN, USD).

        Returns:
            List of DividendSummaryResponse ordered by year.
        """
        summaries = self.div_repo.get_yearly_summary(account=account)
        return [
            DividendSummaryResponse(year=s["year"], total=s["total"])
            for s in summaries
        ]

    def get_dividend_monthly_timeline(
        self, year: int | None = None, account: str | None = None
    ) -> list[DividendTimelineResponse]:
        """Get monthly dividend timeline.

        Args:
            year: Optional year filter — returns 12 months for that year.
            account: Optional account filter (IKE, PLN, USD).

        Returns:
            List of DividendTimelineResponse ordered by month.
        """
        timelines = self.div_repo.get_monthly_timeline(year=year, account=account)
        return [
            DividendTimelineResponse(month=t["month"], total=t["total"])
            for t in timelines
        ]
