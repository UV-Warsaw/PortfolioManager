"""SQLModel TokenBlacklist table model for invalidated JWT tokens."""

from sqlmodel import Field, SQLModel


class TokenBlacklist(SQLModel, table=True):
    """Blacklisted JWT tokens for logout functionality."""

    __tablename__ = "token_blacklist"

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(index=True, unique=True, max_length=500)
    blacklisted_at: str = Field(max_length=50)
    expires_at: str = Field(max_length=50)
