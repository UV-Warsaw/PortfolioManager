"""Bond calculation and analysis service."""

from datetime import datetime, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta
from sqlmodel import Session

from app.models.bonds import Bond, CapitalizationType
from app.schemas.bonds import BondAnalysisResponse, BondValuePoint, BondsPortfolioSummaryResponse


class BondCalculationService:
    """Service for bond value calculations and analysis."""

    CAPITAL_GAINS_TAX_RATE = 0.19  # 19% capital gains tax

    @staticmethod
    def calculate_compound_interest(
        principal: float,
        annual_rate: float,
        years: float,
        capitalization: CapitalizationType,
    ) -> float:
        """
        Calculate compound interest.

        Args:
            principal: Initial principal amount
            annual_rate: Annual interest rate as percentage (e.g., 5.5 for 5.5%)
            years: Number of years
            capitalization: Capitalization frequency

        Returns:
            Final amount with compound interest
        """
        rate_decimal = annual_rate / 100

        if capitalization == CapitalizationType.ANNUAL:
            # A = P(1 + r)^t
            return principal * ((1 + rate_decimal) ** years)

        elif capitalization == CapitalizationType.MONTHLY:
            # A = P(1 + r/12)^(12*t)
            monthly_rate = rate_decimal / 12
            months = years * 12
            return principal * ((1 + monthly_rate) ** months)

        else:
            raise ValueError(f"Unsupported capitalization type: {capitalization}")

    @staticmethod
    def calculate_value_at_date(bond: Bond, target_date: datetime) -> float:
        """
        Calculate bond value at specific date.

        Args:
            bond: Bond instance
            target_date: Target date for calculation

        Returns:
            Bond value at target date
        """
        if target_date < bond.purchase_date:
            return 0.0

        years_held = (target_date - bond.purchase_date).days / 365.25

        # Don't calculate beyond the bond's interest period
        years_to_calculate = min(years_held, bond.years)

        return BondCalculationService.calculate_compound_interest(
            principal=bond.principal,
            annual_rate=bond.annual_rate,
            years=years_to_calculate,
            capitalization=bond.capitalization,
        )

    @staticmethod
    def generate_value_projection(
        bond: Bond,
        end_date: datetime | None = None,
        data_points: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Generate value projection over time.

        Args:
            bond: Bond instance
            end_date: End date for projection (defaults to bond maturity)
            data_points: Number of data points to generate

        Returns:
            List of value projection points
        """
        if end_date is None:
            end_date = bond.purchase_date + relativedelta(years=bond.years)

        # Generate evenly spaced dates
        start_date = bond.purchase_date
        total_days = (end_date - start_date).days

        projections = []

        for i in range(data_points + 1):
            days_offset = (total_days * i) // data_points
            current_date = start_date + timedelta(days=days_offset)

            principal_value = BondCalculationService.calculate_value_at_date(bond, current_date)
            total_value = principal_value * bond.quantity

            projections.append(
                {
                    "date": current_date,
                    "principal_value": round(principal_value, 2),
                    "total_value": round(total_value, 2),
                }
            )

        return projections

    @staticmethod
    def calculate_sale_value_after_tax(
        bond: Bond, current_bond_value: float
    ) -> float:
        """
        Calculate value per bond if redeemed today after 19% capital gains tax.

        Redemption amount = max(stored redemption_price, current compound value).
        Tax is 19% on profit above principal (if any).

        Args:
            bond: Bond instance
            current_bond_value: Current compound-interest value per bond

        Returns:
            After-tax cash per bond if redeemed now
        """
        stored_redemption = bond.redemption_price if bond.redemption_price is not None else 0.0
        redemption_amount = max(stored_redemption, current_bond_value)

        profit = redemption_amount - bond.principal
        if profit <= 0:
            return round(redemption_amount, 2)

        tax = profit * BondCalculationService.CAPITAL_GAINS_TAX_RATE
        return round(redemption_amount - tax, 2)

    @staticmethod
    def analyze_bond(bond: Bond) -> BondAnalysisResponse:
        """
        Analyze a single bond.

        Args:
            bond: Bond instance

        Returns:
            Bond analysis response
        """
        current_date = datetime.now()
        current_value_per_bond = BondCalculationService.calculate_value_at_date(
            bond, current_date
        )
        current_total_value = current_value_per_bond * bond.quantity
        total_invested = bond.principal * bond.quantity

        redemption_per_bond = BondCalculationService.calculate_sale_value_after_tax(
            bond, current_value_per_bond
        )
        redemption_value_after_tax = round(redemption_per_bond * bond.quantity, 2)

        # Gross profit before tax: current compound value minus what was paid
        profit = current_total_value - total_invested
        profit_percentage = (
            (profit / total_invested) * 100
            if total_invested > 0
            else 0
        )

        value_projection = BondCalculationService.generate_value_projection(bond)

        return BondAnalysisResponse(
            bond_id=bond.id or 0,
            name=bond.name,
            current_value_per_bond=round(current_value_per_bond, 2),
            current_total_value=round(current_total_value, 2),
            sale_value_after_tax=redemption_value_after_tax,
            redemption_value_after_tax=redemption_value_after_tax,
            profit=round(profit, 2),
            profit_percentage=round(profit_percentage, 2),
            value_projection=[
                BondValuePoint(
                    date=point["date"].isoformat(),
                    principal_value=point["principal_value"],
                    total_value=point["total_value"],
                )
                for point in value_projection
            ],
        )

    @staticmethod
    def calculate_portfolio_summary(bonds: list[Bond]) -> BondsPortfolioSummaryResponse:
        """
        Calculate summary statistics for bond portfolio.

        Args:
            bonds: List of bond instances

        Returns:
            Portfolio summary response
        """
        current_date = datetime.now()
        total_invested = 0.0
        current_total_value = 0.0
        total_redemption_value_after_tax = 0.0

        for bond in bonds:
            invested = bond.principal * bond.quantity
            current_value_per_bond = BondCalculationService.calculate_value_at_date(
                bond, current_date
            )
            total_value = current_value_per_bond * bond.quantity
            redemption_per_bond = BondCalculationService.calculate_sale_value_after_tax(
                bond, current_value_per_bond
            )

            total_invested += invested
            current_total_value += total_value
            total_redemption_value_after_tax += redemption_per_bond * bond.quantity

        total_profit = current_total_value - total_invested
        total_profit_percentage = (
            (total_profit / total_invested) * 100 if total_invested > 0 else 0
        )

        return BondsPortfolioSummaryResponse(
            total_invested=round(total_invested, 2),
            current_total_value=round(current_total_value, 2),
            total_profit=round(total_profit, 2),
            total_profit_percentage=round(total_profit_percentage, 2),
            total_sale_value_after_tax=round(total_redemption_value_after_tax, 2),
            total_redemption_value_after_tax=round(total_redemption_value_after_tax, 2),
            bonds_count=len(bonds),
        )
