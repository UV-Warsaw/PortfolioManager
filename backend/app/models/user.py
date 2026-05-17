"""SQLModel User table model."""

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User account for portfolio access."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    risk_level: str = Field(default="moderate", max_length=50)
    monthly_expenses: float = Field(default=0.0)
    created_at: str | None = Field(default=None)
