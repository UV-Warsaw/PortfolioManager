"""Summary service — business logic for portfolio dashboard."""

import logging

from sqlmodel import Session, func, select

from app.models.portfolio import Transaction
from app.repositories.portfolio import DividendRepository, TransactionRepository
from app.schemas.portfolio import (
    AssetClassValue,
    DiversificationRecommendation,
    DiversificationResponse,
    DividendSummaryResponse,
    DividendTimelineResponse,
    EmergencyFundResponse,
    RiskAssessmentResponse,
    WealthSummaryResponse,
)

_CONCENTRATION_THRESHOLD = 70.0

_ASSET_GUIDANCE: dict[str, tuple[str, str]] = {
    "Stocks": (
        "stocks",
        "Consider increasing your bonds or cash allocation to reduce equity concentration.",
    ),
    "Bonds": (
        "bonds",
        "Consider diversifying into stocks or other asset classes for better returns.",
    ),
    "Cash": (
        "cash",
        "Consider deploying excess cash into stocks or bonds for better long-term returns.",
    ),
    "Crypto": (
        "crypto",
        "Crypto is highly volatile; consider reallocating some holdings into lower-risk assets.",
    ),
    "Real Estate": (
        "real-estate",
        "Consider diversifying into liquid assets such as stocks or bonds.",
    ),
}

logger = logging.getLogger("portfolio_backend.services.summary")


class SummaryService:
    """Service for portfolio summary and dashboard data."""

    def __init__(self, session: Session, user_id: int) -> None:
        """Initialize summary service with a database session and user id."""
        self.session = session
        self.user_id = user_id
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
        accounts = self.tx_repo.get_account_values(self.user_id)
        top_holdings = self.tx_repo.get_top_holdings(limit=10, user_id=self.user_id)
        holdings = self.tx_repo.get_holdings(account=account, user_id=self.user_id)

        portfolio_value = sum(accounts.values())

        total_invested = 0.0
        for holding in holdings:
            stmt = select(func.sum(Transaction.amount)).where(
                Transaction.ticker == holding["ticker"],
                Transaction.type.in_(["BUY", "Stock purchase"]),
                Transaction.account == holding["account"],
                Transaction.user_id == self.user_id,
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
        summaries = self.div_repo.get_yearly_summary(
            account=account, user_id=self.user_id
        )
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
        timelines = self.div_repo.get_monthly_timeline(
            year=year, account=account, user_id=self.user_id
        )
        return [
            DividendTimelineResponse(month=t["month"], total=t["total"])
            for t in timelines
        ]

    def get_wealth_summary(self) -> WealthSummaryResponse:
        """Aggregate total portfolio wealth across all asset classes.

        Returns:
            WealthSummaryResponse with total value and per-class breakdown.
        """
        from app.repositories.bonds import BondRepository
        from app.services.assets import OtherAssetService
        from app.services.bond_calculation import BondCalculationService
        from app.services.cash import CashService

        # Stocks
        accounts = self.tx_repo.get_account_values(self.user_id)
        stocks_value = round(sum(accounts.values()), 2)

        # Bonds — use proper compound-interest calculation
        bond_repo = BondRepository(self.session)
        bonds = bond_repo.list_all(self.user_id)
        bonds_summary = BondCalculationService.calculate_portfolio_summary(bonds)
        bonds_value = bonds_summary.current_total_value

        # Cash
        cash_svc = CashService(self.session, self.user_id)
        cash_summary = cash_svc.portfolio_summary()
        cash_value = round(cash_summary.total_balance, 2)

        # Crypto & Real Estate (from other assets)
        asset_svc = OtherAssetService(self.session, self.user_id)
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

    def get_risk_assessment(self, user_preference: str) -> RiskAssessmentResponse:
        """Assess portfolio risk level and compare against the user's declared preference.

        Risk classification:
          - Crypto                  → high risk
          - Stocks + Real Estate   → medium risk
          - Bonds + Cash           → low risk

        Portfolio risk label:
          - aggressive   : high_pct >  50 %
          - conservative : low_pct  >= 60 %
          - moderate     : otherwise

        Args:
            user_preference: The declared risk preference stored on the User record.

        Returns:
            RiskAssessmentResponse with computed risk, preference, and alignment flag.
        """
        wealth = self.get_wealth_summary()

        if not wealth.has_data:
            return RiskAssessmentResponse(
                portfolio_risk="moderate",
                user_preference=user_preference,
                is_aligned=user_preference == "moderate",
                high_pct=0.0,
                medium_pct=0.0,
                low_pct=0.0,
                has_data=False,
            )

        by_name = {item.name: item.percentage for item in wealth.breakdown}
        high_pct = round(by_name.get("Crypto", 0.0), 2)
        medium_pct = round(
            by_name.get("Stocks", 0.0) + by_name.get("Real Estate", 0.0), 2
        )
        low_pct = round(by_name.get("Bonds", 0.0) + by_name.get("Cash", 0.0), 2)

        if high_pct > 50.0:
            portfolio_risk = "aggressive"
        elif low_pct >= 60.0:
            portfolio_risk = "conservative"
        else:
            portfolio_risk = "moderate"

        return RiskAssessmentResponse(
            portfolio_risk=portfolio_risk,
            user_preference=user_preference,
            is_aligned=portfolio_risk == user_preference,
            high_pct=high_pct,
            medium_pct=medium_pct,
            low_pct=low_pct,
            has_data=True,
        )

    def get_diversification_recommendations(self) -> DiversificationResponse:
        """Detect asset-class concentration and generate diversification recommendations.

        A concentration alert is raised when a single asset class exceeds
        _CONCENTRATION_THRESHOLD (70%) of the total portfolio value. At most
        three recommendations are returned, sorted by concentration level (highest
        first).

        Returns:
            DiversificationResponse with up to three recommendations and an
            ``is_diversified`` flag.
        """
        wealth = self.get_wealth_summary()

        if not wealth.has_data:
            return DiversificationResponse(
                recommendations=[],
                is_diversified=True,
                has_data=False,
            )

        recs: list[DiversificationRecommendation] = []
        for asset in wealth.breakdown:
            if asset.percentage > _CONCENTRATION_THRESHOLD:
                link, action = _ASSET_GUIDANCE.get(
                    asset.name,
                    ("overview", "Consider diversifying your portfolio."),
                )
                recs.append(
                    DiversificationRecommendation(
                        asset_class=asset.name,
                        percentage=asset.percentage,
                        problem=(
                            f"{asset.percentage:.0f}% of your portfolio is"
                            f" concentrated in {asset.name.lower()}."
                        ),
                        action=action,
                        link_to=link,
                    )
                )

        recs.sort(key=lambda r: r.percentage, reverse=True)
        recs = recs[:3]

        return DiversificationResponse(
            recommendations=recs,
            is_diversified=len(recs) == 0,
            has_data=True,
        )

    def get_emergency_fund(self, monthly_expenses: float) -> EmergencyFundResponse:
        """Evaluate emergency fund adequacy (cash + bonds vs monthly expenses).

        Thresholds:
          - < 3 months  → 'critical'
          - 3 – 6 months → 'good'
          - > 6 months  → 'excellent'

        When monthly_expenses is 0 the months_covered cannot be determined;
        status defaults to 'good' and months_covered to 0.

        Args:
            monthly_expenses: User's declared monthly living expenses in PLN.

        Returns:
            EmergencyFundResponse with values, months covered, and status.
        """
        wealth = self.get_wealth_summary()

        if not wealth.has_data:
            return EmergencyFundResponse(
                cash_value=0.0,
                bonds_value=0.0,
                emergency_fund=0.0,
                monthly_expenses=monthly_expenses,
                months_covered=0.0,
                status="critical",
                has_data=False,
            )

        by_name = {item.name: item.value for item in wealth.breakdown}
        cash_value = round(by_name.get("Cash", 0.0), 2)
        bonds_value = round(by_name.get("Bonds", 0.0), 2)
        emergency_fund = round(cash_value + bonds_value, 2)

        if monthly_expenses > 0:
            months_covered = round(emergency_fund / monthly_expenses, 1)
            if months_covered < 3:
                status = "critical"
            elif months_covered <= 6:
                status = "good"
            else:
                status = "excellent"
        else:
            months_covered = 0.0
            status = "good"

        return EmergencyFundResponse(
            cash_value=cash_value,
            bonds_value=bonds_value,
            emergency_fund=emergency_fund,
            monthly_expenses=monthly_expenses,
            months_covered=months_covered,
            status=status,
            has_data=True,
        )
