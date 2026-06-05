from datetime import datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class OtherAssetClass(StrEnum):
    """Manual asset class type."""

    CRYPTO = "Crypto"
    REAL_ESTATE = "Real Estate"
    OTHER = "Other"


class OtherAsset(SQLModel, table=True):
    """Manually-valued asset database model (crypto, real estate, etc.)."""

    __tablename__ = "other_assets"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field()
    asset_class: OtherAssetClass = Field()
    current_value: float = Field()
    currency: str = Field(default="PLN")
    # Optional crypto P&L fields
    quantity: float | None = Field(default=None)
    purchase_price: float | None = Field(default=None)
    # Optional real estate field
    mortgage_remaining: float | None = Field(default=None)
    notes: str | None = Field(default=None)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None)
