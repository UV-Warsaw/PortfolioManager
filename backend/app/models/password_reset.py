"""SQLModel PasswordResetToken table model."""

from sqlmodel import Field, SQLModel


class PasswordResetToken(SQLModel, table=True):
    """One-time token for resetting a user password.

    The raw token is never stored — only its SHA-256 hash is persisted so that
    a database leak cannot be used to trigger resets directly.
    """

    __tablename__ = "password_reset_tokens"

    id: int | None = Field(default=None, primary_key=True)
    token_hash: str = Field(index=True, unique=True, max_length=64)
    email: str = Field(index=True, max_length=255)
    created_at: str = Field(max_length=50)
    expires_at: str = Field(max_length=50)
    used_at: str | None = Field(default=None, max_length=50)
