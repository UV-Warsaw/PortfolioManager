"""Pydantic schemas for user profile management."""

from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    """Schema for returning full user profile data."""

    id: int
    email: str
    risk_level: str
    monthly_expenses: float
    created_at: str | None


class UpdateEmailRequest(BaseModel):
    """Schema for changing the account email address."""

    current_password: str
    new_email: EmailStr


class UpdatePasswordRequest(BaseModel):
    """Schema for changing the account password."""

    current_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class UpdateProfileSettingsRequest(BaseModel):
    """Schema for updating risk level and monthly expenses."""

    risk_level: str | None = Field(
        default=None,
        pattern="^(conservative|moderate|aggressive)$",
        description="Investment risk profile",
    )
    monthly_expenses: float | None = Field(
        default=None,
        ge=0,
        description="Monthly living expenses in PLN",
    )


class UpdateSettingsResponse(BaseModel):
    """Schema confirming a settings update."""

    message: str = "Settings updated"
    profile: ProfileResponse
