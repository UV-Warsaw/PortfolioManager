"""Schemas for portfolio import operations."""

from datetime import datetime

from pydantic import BaseModel


class TransactionRead(BaseModel):
    id: int
    date: datetime | None
    ticker: str | None
    type: str | None
    quantity: float | None
    price: float | None
    amount: float | None
    account: str | None

    model_config = {"from_attributes": True}


class DividendRead(BaseModel):
    id: int
    date: datetime | None
    ticker: str | None
    amount: float | None
    currency: str | None
    account: str | None

    model_config = {"from_attributes": True}


class ImportResponse(BaseModel):
    imported_transactions: int
    imported_dividends: int
    account: str
