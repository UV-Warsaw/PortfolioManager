"""Pydantic schemas for Bond API endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.bonds import CapitalizationType


class BondCreate(BaseModel):
    """Request schema for creating a new bond."""

    name: str = Field(..., min_length=1, max_length=255)
    interest_rate: float = Field(..., ge=0, le=100)
    interest_period_years: float = Field(..., gt=0)
    capitalization: CapitalizationType
    purchase_price: float = Field(..., gt=0)
    current_price: float | None = Field(None, gt=0)
    quantity: int = Field(default=1, ge=1)
    purchase_date: datetime


class BondUpdate(BaseModel):
    """Request schema for updating an existing bond."""

    name: str | None = Field(None, min_length=1, max_length=255)
    interest_rate: float | None = Field(None, ge=0, le=100)
    interest_period_years: float | None = Field(None, gt=0)
    capitalization: CapitalizationType | None = None
    purchase_price: float | None = Field(None, gt=0)
    current_price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=1)
    purchase_date: datetime | None = None


class BondResponse(BaseModel):
    """Response schema for a single bond."""

    id: int
    name: str
    interest_rate: float
    interest_period_years: float
    capitalization: CapitalizationType
    purchase_price: float
    current_price: float | None
    quantity: int
    purchase_date: datetime
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
