from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Asset(SQLModel, table=True):
    """Asset database model representing a financial instrument."""

    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    name: Optional[str] = Field(default=None)


class Transaction(SQLModel, table=True):
    """Transaction database model representing a buy or sell operation."""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: Optional[datetime] = Field(default=None)
    ticker: Optional[str] = Field(default=None, index=True)
    type: Optional[str] = Field(default=None)
    quantity: Optional[float] = Field(default=None)
    price: Optional[float] = Field(default=None)
    market_price: Optional[float] = Field(default=None)
    amount: Optional[float] = Field(default=None)
    raw: Optional[str] = Field(default=None)
    account: Optional[str] = Field(default=None, index=True)


class Dividend(SQLModel, table=True):
    """Dividend database model representing a dividend payment."""

    id: Optional[int] = Field(default=None, primary_key=True)
    date: Optional[datetime] = Field(default=None)
    ticker: Optional[str] = Field(default=None, index=True)
    amount: Optional[float] = Field(default=None)
    currency: Optional[str] = Field(default=None)
    raw: Optional[str] = Field(default=None)
    account: Optional[str] = Field(default=None, index=True)
