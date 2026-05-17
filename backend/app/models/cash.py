from datetime import datetime
from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field


class CashAccountType(str, Enum):
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

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    account_type: CashAccountType = Field()
    balance: float = Field()
    interest_rate: Optional[float] = Field(default=None)
    bank_name: Optional[str] = Field(default=None)
    currency: str = Field(default="PLN")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default=None)
