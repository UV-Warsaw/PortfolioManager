"""Service layer for CashAccount business logic."""

from datetime import datetime

from sqlmodel import Session

from app.models.cash import CashAccount
from app.repositories.cash import CashRepository
from app.schemas.cash import (
    CashAnalysisResponse,
    CashCreate,
    CashPortfolioSummaryResponse,
    CashResponse,
    CashUpdate,
)


class CashService:
    """Service for CashAccount business operations."""

    _TAX_RATE: float = 0.19

    def __init__(self, session: Session) -> None:
        """Initialize CashService.

        Args:
            session: SQLModel database session.
        """
        self.repo = CashRepository(session)

    @staticmethod
    def _calculate_interest(
        balance: float, annual_rate: float | None
    ) -> dict[str, float]:
        """Calculate interest earnings for annual, monthly, and daily periods.

        Args:
            balance: Account balance.
            annual_rate: Annual interest rate as percentage (e.g. 5.0 for 5%).

        Returns:
            Dict with annual_interest, monthly_interest, daily_interest.
        """
        rate = annual_rate or 0.0
        if rate <= 0 or balance <= 0:
            return {
                "annual_interest": 0.0,
                "monthly_interest": 0.0,
                "daily_interest": 0.0,
                "annual_interest_after_tax": 0.0,
                "monthly_interest_after_tax": 0.0,
                "daily_interest_after_tax": 0.0,
            }
        net = 1 - CashService._TAX_RATE
        annual = balance * rate / 100
        return {
            "annual_interest": round(annual, 2),
            "monthly_interest": round(annual / 12, 2),
            "daily_interest": round(annual / 365.25, 4),
            "annual_interest_after_tax": round(annual * net, 2),
            "monthly_interest_after_tax": round(annual / 12 * net, 2),
            "daily_interest_after_tax": round(annual / 365.25 * net, 4),
        }

    def create(self, data: CashCreate) -> CashResponse:
        """Create a new cash account.

        Args:
            data: Cash account creation data.

        Returns:
            The created account as CashResponse.

        Raises:
            ValueError: If an account with the same name already exists.
        """
        if self.repo.get_by_name(data.name):
            raise ValueError(f"Cash account '{data.name}' already exists")

        account = CashAccount(
            name=data.name,
            account_type=data.account_type,
            balance=data.balance,
            interest_rate=data.interest_rate,
            bank_name=data.bank_name,
            currency=data.currency,
        )
        self.repo.create(account)
        return CashResponse.model_validate(account)

    def get(self, account_id: int) -> CashResponse | None:
        """Get a single cash account by ID.

        Args:
            account_id: The account ID.

        Returns:
            CashResponse or None if not found.
        """
        account = self.repo.get_by_id(account_id)
        return CashResponse.model_validate(account) if account else None

    def list_all(self) -> list[CashResponse]:
        """Get all cash accounts.

        Returns:
            List of all cash accounts as CashResponse objects.
        """
        return [CashResponse.model_validate(a) for a in self.repo.list_all()]

    def update(self, account_id: int, data: CashUpdate) -> CashResponse | None:
        """Update an existing cash account.

        Args:
            account_id: The account ID to update.
            data: Partial account data to update.

        Returns:
            Updated CashResponse or None if not found.

        Raises:
            ValueError: If updating name to one that already exists.
        """
        account = self.repo.get_by_id(account_id)
        if not account:
            return None

        if data.name is not None and data.name != account.name:
            if self.repo.get_by_name(data.name):
                raise ValueError(f"Cash account '{data.name}' already exists")

        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(account, field, val)

        account.updated_at = datetime.now()
        self.repo.update(account)
        return CashResponse.model_validate(account)

    def delete(self, account_id: int) -> bool:
        """Delete a cash account by ID.

        Args:
            account_id: The account ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        account = self.repo.get_by_id(account_id)
        if not account:
            return False
        self.repo.delete(account)
        return True

    def analyze(self, account_id: int) -> CashAnalysisResponse | None:
        """Get interest analysis for a cash account.

        Args:
            account_id: The account ID.

        Returns:
            CashAnalysisResponse or None if not found.
        """
        account = self.repo.get_by_id(account_id)
        if not account:
            return None
        interest = self._calculate_interest(account.balance, account.interest_rate)
        return CashAnalysisResponse(
            account_id=account.id,
            name=account.name,
            balance=account.balance,
            **interest,
        )

    def portfolio_summary(self) -> CashPortfolioSummaryResponse:
        """Get aggregated summary of all cash accounts.

        Returns:
            CashPortfolioSummaryResponse with totals and per-type breakdown.
        """
        accounts = self.repo.list_all()
        if not accounts:
            return CashPortfolioSummaryResponse(
                total_balance=0.0,
                total_annual_interest=0.0,
                total_monthly_interest=0.0,
                total_annual_interest_after_tax=0.0,
                total_monthly_interest_after_tax=0.0,
                weighted_avg_interest_rate=0.0,
                weighted_avg_interest_rate_after_tax=0.0,
                accounts_count=0,
                accounts_by_type={},
            )

        total_balance = 0.0
        total_annual = 0.0
        total_monthly = 0.0
        weighted_sum = 0.0
        by_type: dict[str, dict] = {}

        for a in accounts:
            total_balance += a.balance
            interest = self._calculate_interest(a.balance, a.interest_rate)
            total_annual += interest["annual_interest"]
            total_monthly += interest["monthly_interest"]
            if a.interest_rate:
                weighted_sum += a.balance * a.interest_rate

            key = a.account_type.value
            if key not in by_type:
                by_type[key] = {"count": 0, "total_balance": 0.0}
            by_type[key]["count"] += 1
            by_type[key]["total_balance"] += a.balance

        net = 1 - CashService._TAX_RATE
        avg_rate = weighted_sum / total_balance if total_balance > 0 else 0.0
        return CashPortfolioSummaryResponse(
            total_balance=round(total_balance, 2),
            total_annual_interest=round(total_annual, 2),
            total_monthly_interest=round(total_monthly, 2),
            total_annual_interest_after_tax=round(total_annual * net, 2),
            total_monthly_interest_after_tax=round(total_monthly * net, 2),
            weighted_avg_interest_rate=round(avg_rate, 4),
            weighted_avg_interest_rate_after_tax=round(avg_rate * net, 4),
            accounts_count=len(accounts),
            accounts_by_type=by_type,
        )
