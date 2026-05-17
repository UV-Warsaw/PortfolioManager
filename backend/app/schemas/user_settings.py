"""Pydantic schemas for user settings."""

from pydantic import BaseModel, Field


class UserSettingsCreate(BaseModel):
    """Schema for creating user settings."""

    monthly_expenses: float = Field(ge=0, description="Monthly living expenses in PLN")


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""

    monthly_expenses: float | None = Field(
        default=None, ge=0, description="Monthly living expenses in PLN"
    )


class UserSettingsResponse(BaseModel):
    """Schema for user settings response."""

    id: int
    monthly_expenses: float
    created_at: str | None
    updated_at: str | None
