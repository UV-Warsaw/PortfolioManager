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


class RiskAssessmentResponse(BaseModel):
    """Portfolio risk level compared against the user's declared risk preference."""

    portfolio_risk: str
    """Computed portfolio risk: 'conservative' | 'moderate' | 'aggressive'."""

    user_preference: str
    """User's declared risk preference from their profile."""

    is_aligned: bool
    """True when portfolio_risk matches user_preference."""

    high_pct: float
    """Share of high-risk assets (Stocks + Crypto), 0–100."""

    medium_pct: float
    """Share of medium-risk assets (Real Estate), 0–100."""

    low_pct: float
    """Share of low-risk assets (Bonds + Cash), 0–100."""

    has_data: bool
    """False when the portfolio is empty (no assets)."""


class DiversificationRecommendation(BaseModel):
    """A single concentration-based diversification recommendation."""

    asset_class: str
    """Asset class name, e.g. 'Stocks'."""

    percentage: float
    """Current share of this asset class in the portfolio (0–100)."""

    problem: str
    """Human-readable description of the concentration issue."""

    action: str
    """Suggested action to reduce concentration."""

    link_to: str
    """Frontend tab key the user can navigate to, e.g. 'stocks'."""


class DiversificationResponse(BaseModel):
    """Concentration analysis and diversification recommendations."""

    recommendations: list[DiversificationRecommendation]
    """Up to three recommendations, ordered by concentration severity."""

    is_diversified: bool
    """True when no asset class exceeds the concentration threshold."""

    has_data: bool
    """False when the portfolio is empty (no assets)."""


class EmergencyFundResponse(BaseModel):
    """Emergency fund adequacy — cash + bonds vs monthly expenses."""

    cash_value: float
    """Current cash holdings value in PLN."""

    bonds_value: float
    """Current bonds holdings value in PLN."""

    emergency_fund: float
    """Total emergency fund (cash + bonds) in PLN."""

    monthly_expenses: float
    """User's declared monthly living expenses in PLN."""

    months_covered: float
    """How many months of expenses the emergency fund covers (0 if expenses unknown)."""

    status: str
    """'critical' (<3 months) | 'good' (3–6 months) | 'excellent' (>6 months)."""

    has_data: bool
    """False when the portfolio is empty (no assets)."""
