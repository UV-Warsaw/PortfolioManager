"""Pydantic schemas for password-reset request and confirmation."""

from pydantic import BaseModel, EmailStr, field_validator


class PasswordResetRequestSchema(BaseModel):
    """Payload for initiating a password-reset flow."""

    email: EmailStr


class PasswordResetConfirmSchema(BaseModel):
    """Payload for completing a password-reset flow using a verification code."""

    email: EmailStr
    code: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        """
        Enforce a minimum password length of 8 characters.

        Args:
            value: Candidate password string.

        Returns:
            The validated password string.

        Raises:
            ValueError: If the password is shorter than 8 characters.
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class PasswordResetResponseSchema(BaseModel):
    """Response body for both reset endpoints."""

    message: str
