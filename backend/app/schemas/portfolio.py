"""Schemas for portfolio import and holdings operations."""

from datetime import datetime

from pydantic import BaseModel


class TransactionRead(BaseModel):
    """Read schema for a single transaction record."""

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
    """Read schema for a single dividend record."""

    id: int
    date: datetime | None
    ticker: str | None
    amount: float | None
    currency: str | None
    account: str | None

    model_config = {"from_attributes": True}


class HoldingRead(BaseModel):
    """Read schema for an aggregated current holding position."""

    ticker: str
    account: str
    quantity: float


class PortfolioValueResponse(BaseModel):
    """Read schema for portfolio cost basis grouped by account."""

    accounts: dict[str, float]
    total: float


class TopHoldingItem(BaseModel):
    """Read schema for a single holding ranked by cost basis."""

    ticker: str
    cost_basis: float


class TopHoldingsResponse(BaseModel):
    """Read schema for the top-N holdings by cost basis."""

    items: list[TopHoldingItem]


class ImportResponse(BaseModel):
    """Response schema for the portfolio upload endpoint."""

    imported_transactions: int
    imported_dividends: int
    account: str
