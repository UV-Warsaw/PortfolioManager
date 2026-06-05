from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class CashAccountType(StrEnum):
    """Cash account type."""

    SAVINGS = "Savings"
    CHECKING = "Checking"
    HIGH_YIELD_SAVINGS = "High-Yield Savings"
    MONEY_MARKET = "Money Market"
    CASH = "Cash"
    OTHER = "Other"


class CashAccount(SQLModel, table=True):
    """Cash account database model."""

    __tablename__ = "cash_accounts"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    account_type: CashAccountType = Field()
    balance: float = Field()
    interest_rate: float | None = Field(default=None)
    bank_name: str | None = Field(default=None)
    currency: str = Field(default="PLN")
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None)
