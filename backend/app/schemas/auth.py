"""Pydantic schemas for authentication."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    email: EmailStr
    password: str = Field(min_length=8)


class RegisterResponse(BaseModel):
    """Schema for registration response with access token."""

    id: int
    email: str
    access_token: str
    token_type: str = "bearer"
