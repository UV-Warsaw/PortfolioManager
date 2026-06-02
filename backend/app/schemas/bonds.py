"""Pydantic schemas for Bond API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.bonds import CapitalizationType


class BondValuePoint(BaseModel):
    """Value projection data point for a bond."""

    date: str = Field(..., description="ISO format date")
    principal_value: float = Field(..., description="Principal value with interest")
    total_value: float = Field(..., description="Total value (principal_value * quantity)")


class BondCreate(BaseModel):
    """Request schema for creating a new bond."""

    name: str = Field(..., min_length=1, max_length=255)
    annual_rate: float = Field(..., ge=0, le=100, description="Annual interest rate as percentage")
    years: float = Field(..., gt=0, description="Maturity period in years")
    capitalization: CapitalizationType
    principal: float = Field(..., gt=0, description="Principal/nominal value")
    redemption_price: float | None = Field(None, gt=0, description="Redemption/sale price")
    quantity: int = Field(default=1, ge=1)
    purchase_date: datetime


class BondUpdate(BaseModel):
    """Request schema for updating an existing bond."""

    name: str | None = Field(None, min_length=1, max_length=255)
    annual_rate: float | None = Field(None, ge=0, le=100)
    years: float | None = Field(None, gt=0)
    capitalization: CapitalizationType | None = None
    principal: float | None = Field(None, gt=0)
    redemption_price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=1)
    purchase_date: datetime | None = None


class BondResponse(BaseModel):
    """Response schema for a single bond."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    annual_rate: float
    years: float
    capitalization: CapitalizationType
    principal: float
    redemption_price: float | None
    quantity: int
    purchase_date: datetime
    created_at: datetime
    updated_at: datetime | None


class BondAnalysisResponse(BaseModel):
    """Response schema for bond analysis."""

    bond_id: int
    name: str
    current_value_per_bond: float = Field(..., description="Current value per bond")
    current_total_value: float = Field(
        ..., description="Current total value (per bond * quantity)"
    )
    sale_value_after_tax: float = Field(..., description="Value after tax when selling")
    profit: float = Field(..., description="Profit/loss in absolute amount")
    profit_percentage: float = Field(..., description="Profit/loss as percentage")
    value_projection: list[BondValuePoint] = Field(
        ..., description="Value projection over time"
    )


class BondsPortfolioSummaryResponse(BaseModel):
    """Response schema for bonds portfolio summary."""

    total_invested: float = Field(..., description="Total amount invested in bonds")
    current_total_value: float = Field(..., description="Current portfolio value")
    total_profit: float = Field(..., description="Total profit/loss")
    total_profit_percentage: float = Field(..., description="Total profit/loss percentage")
    total_sale_value_after_tax: float = Field(
        ..., description="Total portfolio value after tax when selling all"
    )
    bonds_count: int = Field(..., description="Number of bonds in portfolio")

    model_config = {"from_attributes": True}
