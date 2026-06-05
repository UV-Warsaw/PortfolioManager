from datetime import datetime

from sqlmodel import Field, SQLModel


class Asset(SQLModel, table=True):
    """Asset database model representing a financial instrument."""

    id: int | None = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    name: str | None = Field(default=None)


class Transaction(SQLModel, table=True):
    """Transaction database model representing a buy or sell operation."""

    id: int | None = Field(default=None, primary_key=True)
    date: datetime | None = Field(default=None)
    ticker: str | None = Field(default=None, index=True)
    type: str | None = Field(default=None)
    quantity: float | None = Field(default=None)
    price: float | None = Field(default=None)
    market_price: float | None = Field(default=None)
    amount: float | None = Field(default=None)
    raw: str | None = Field(default=None)
    account: str | None = Field(default=None, index=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)


class Dividend(SQLModel, table=True):
    """Dividend database model representing a dividend payment."""

    id: int | None = Field(default=None, primary_key=True)
    date: datetime | None = Field(default=None)
    ticker: str | None = Field(default=None, index=True)
    amount: float | None = Field(default=None)
    currency: str | None = Field(default=None)
    raw: str | None = Field(default=None)
    account: str | None = Field(default=None, index=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
