"""Summary service — business logic for portfolio dashboard."""

import logging

from sqlmodel import Session, func, select

from app.models.portfolio import Transaction
from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.schemas.portfolio import (
    AssetClassValue,
    DividendSummaryResponse,
    DividendTimelineResponse,
    WealthSummaryResponse,
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
                Transaction.type.in_(["BUY", "Stock purchase"]),
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
            DividendSummaryResponse(year=s["year"], total=s["total"]) for s in summaries
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

    def get_wealth_summary(self) -> WealthSummaryResponse:
        """Aggregate total portfolio wealth across all asset classes.

        Returns:
            WealthSummaryResponse with total value and per-class breakdown.
        """
        from app.services.assets import OtherAssetService
        from app.services.bonds import BondService
        from app.services.cash import CashService

        # Stocks
        accounts = self.tx_repo.get_account_values()
        stocks_value = round(sum(accounts.values()), 2)

        # Bonds
        bond_svc = BondService(self.session)
        bonds_value = round(bond_svc.get_total_value(), 2)

        # Cash
        cash_svc = CashService(self.session)
        cash_summary = cash_svc.portfolio_summary()
        cash_value = round(cash_summary.total_balance, 2)

        # Crypto & Real Estate (from other assets)
        asset_svc = OtherAssetService(self.session)
        other_summary = asset_svc.portfolio_summary()
        by_class = other_summary.assets_by_class

        crypto_value = round(by_class.get("Crypto", {}).get("total_value", 0.0), 2)
        re_gross = round(by_class.get("Real Estate", {}).get("total_value", 0.0), 2)
        re_net = round(re_gross - other_summary.total_mortgage, 2)
        real_estate_value = max(re_net, 0.0)  # net equity (value minus mortgage)

        total = (
            stocks_value + bonds_value + cash_value + crypto_value + real_estate_value
        )

        def pct(v: float) -> float:
            return round((v / total * 100), 2) if total > 0 else 0.0

        breakdown = [
            AssetClassValue(
                name="Stocks", value=stocks_value, percentage=pct(stocks_value)
            ),
            AssetClassValue(
                name="Bonds", value=bonds_value, percentage=pct(bonds_value)
            ),
            AssetClassValue(name="Cash", value=cash_value, percentage=pct(cash_value)),
            AssetClassValue(
                name="Crypto", value=crypto_value, percentage=pct(crypto_value)
            ),
            AssetClassValue(
                name="Real Estate",
                value=real_estate_value,
                percentage=pct(real_estate_value),
            ),
        ]

        return WealthSummaryResponse(
            total_value=round(total, 2),
            breakdown=breakdown,
            has_data=total > 0,
        )
