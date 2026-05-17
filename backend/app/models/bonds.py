from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class CapitalizationType(str, Enum):
    """Bond interest capitalization type."""

    ANNUAL = "Annual"
    MONTHLY = "Monthly"


class Bond(SQLModel, table=True):
    """Bond database model."""

    __tablename__ = "bonds"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    interest_rate: float = Field()
    interest_period_years: float = Field()
    capitalization: CapitalizationType = Field()
    purchase_price: float = Field()
    current_price: float | None = Field(default=None)
    quantity: int = Field(default=1)
    purchase_date: datetime = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None)
