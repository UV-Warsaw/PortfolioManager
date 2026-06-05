from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class CapitalizationType(StrEnum):
    """Bond interest capitalization type."""

    ANNUAL = "Annual"
    MONTHLY = "Monthly"


class Bond(SQLModel, table=True):
    """Bond database model."""

    __tablename__ = "bonds"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    annual_rate: float = Field()  # Renamed from interest_rate
    years: float = Field()  # Renamed from interest_period_years
    capitalization: CapitalizationType = Field()
    principal: float = Field()  # Renamed from purchase_price
    redemption_price: float | None = Field(default=None)  # Renamed from current_price
    quantity: int = Field(default=1)
    purchase_date: datetime = Field()
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None)
