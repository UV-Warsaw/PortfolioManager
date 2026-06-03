"""Pydantic schemas for Cash Account API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.cash import CashAccountType


class CashCreate(BaseModel):
    """Request schema for creating a new cash account."""

    name: str = Field(..., min_length=1, max_length=255)
    account_type: CashAccountType
    balance: float = Field(..., ge=0, description="Current balance")
    interest_rate: float | None = Field(
        None, ge=0, le=100, description="Annual interest rate %"
    )
    bank_name: str | None = Field(None, max_length=255)
    currency: str = Field(default="PLN", max_length=10)


class CashUpdate(BaseModel):
    """Request schema for updating a cash account."""

    name: str | None = Field(None, min_length=1, max_length=255)
    account_type: CashAccountType | None = None
    balance: float | None = Field(None, ge=0)
    interest_rate: float | None = Field(None, ge=0, le=100)
    bank_name: str | None = Field(None, max_length=255)
    currency: str | None = Field(None, max_length=10)


class CashResponse(BaseModel):
    """Response schema for a single cash account."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    account_type: CashAccountType
    balance: float
    interest_rate: float | None
    bank_name: str | None
    currency: str
    created_at: datetime
    updated_at: datetime | None


class CashAnalysisResponse(BaseModel):
    """Response schema for cash account interest analysis."""

    account_id: int
    name: str
    balance: float
    annual_interest: float = Field(..., description="Annual interest earnings (gross)")
    monthly_interest: float = Field(
        ..., description="Monthly interest earnings (~annual/12, gross)"
    )
    daily_interest: float = Field(
        ..., description="Daily interest earnings (~annual/365.25, gross)"
    )
    annual_interest_after_tax: float = Field(
        ..., description="Annual interest after 19% capital gains tax"
    )
    monthly_interest_after_tax: float = Field(
        ..., description="Monthly interest after 19% capital gains tax"
    )
    daily_interest_after_tax: float = Field(
        ..., description="Daily interest after 19% capital gains tax"
    )


class CashPortfolioSummaryResponse(BaseModel):
    """Response schema for full cash portfolio summary."""

    total_balance: float
    total_annual_interest: float
    total_monthly_interest: float
    total_annual_interest_after_tax: float
    total_monthly_interest_after_tax: float
    weighted_avg_interest_rate: float
    weighted_avg_interest_rate_after_tax: float
    accounts_count: int
    accounts_by_type: dict[str, dict]
