"""Pydantic schemas for Other Asset (manual valuation) API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.assets import OtherAssetClass


class OtherAssetCreate(BaseModel):
    """Request schema for creating a manually-valued asset."""

    name: str = Field(..., min_length=1, max_length=255)
    asset_class: OtherAssetClass
    current_value: float = Field(..., ge=0, description="Current market value")
    currency: str = Field(default="PLN", max_length=10)
    quantity: float | None = Field(None, gt=0, description="Number of units (crypto)")
    purchase_price: float | None = Field(
        None, ge=0, description="Purchase price per unit (for P&L)"
    )
    mortgage_remaining: float | None = Field(
        None, ge=0, description="Capital remaining on mortgage (real estate)"
    )
    notes: str | None = Field(None, max_length=1000)


class OtherAssetUpdate(BaseModel):
    """Request schema for updating a manually-valued asset."""

    name: str | None = Field(None, min_length=1, max_length=255)
    asset_class: OtherAssetClass | None = None
    current_value: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    quantity: float | None = Field(None, gt=0)
    purchase_price: float | None = Field(None, ge=0)
    mortgage_remaining: float | None = Field(None, ge=0)
    notes: str | None = Field(None, max_length=1000)


class OtherAssetResponse(BaseModel):
    """Response schema for a single manually-valued asset."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    asset_class: OtherAssetClass
    current_value: float
    currency: str
    quantity: float | None
    purchase_price: float | None
    mortgage_remaining: float | None
    notes: str | None
    created_at: datetime
    updated_at: datetime | None


class OtherAssetAnalysisResponse(BaseModel):
    """Response schema for asset P&L analysis."""

    asset_id: int
    name: str
    asset_class: OtherAssetClass
    current_value: float
    currency: str
    total_cost: float | None = Field(
        None, description="Total purchase cost (quantity × purchase_price)"
    )
    profit: float | None = Field(
        None, description="Profit (current_value − total_cost)"
    )
    profit_pct: float | None = Field(None, description="Profit as percentage of cost")
    # Real estate equity
    net_equity: float | None = Field(
        None, description="Net equity (current_value − mortgage_remaining)"
    )


class OtherAssetsPortfolioSummaryResponse(BaseModel):
    """Response schema for the full manually-valued assets portfolio summary."""

    total_value: float
    total_cost: float
    total_profit: float
    total_mortgage: float
    total_net_equity: float
    assets_count: int
    assets_by_class: dict[str, dict]
