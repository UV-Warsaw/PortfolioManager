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
    """Read schema for portfolio current market value grouped by account."""

    accounts: dict[str, float]
    total: float
    profit_data: dict[str, dict[str, float]] | None = None


class TopHoldingItem(BaseModel):
    """Read schema for a single holding ranked by market value."""

    ticker: str
    cost_basis: float


class TopHoldingsResponse(BaseModel):
    """Read schema for the top-N holdings by market value."""

    items: list[TopHoldingItem]


class ImportResponse(BaseModel):
    """Response schema for the portfolio upload endpoint."""

    imported_transactions: int
    imported_dividends: int
    account: str


class TopHoldingItemSummary(BaseModel):
    """Schema for a single top holding in portfolio summary."""

    ticker: str
    value: float


class PortfolioSummaryResponse(BaseModel):
    """Response schema for portfolio dashboard summary."""

    portfolio_value: float
    total_invested: float
    profit: float
    profit_percentage: float
    top_holdings: list[TopHoldingItemSummary]


class DividendSummaryResponse(BaseModel):
    """Schema for yearly dividend summary."""

    year: int
    total: float


class DividendTimelineResponse(BaseModel):
    """Schema for monthly dividend timeline."""

    month: int
    total: float


class AssetClassValue(BaseModel):
    """A single asset class value and its portfolio share."""

    name: str
    value: float
    percentage: float


class WealthSummaryResponse(BaseModel):
    """Total portfolio wealth broken down by asset class."""

    total_value: float
    breakdown: list[AssetClassValue]
    has_data: bool
