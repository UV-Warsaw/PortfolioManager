from sqlmodel import Field, SQLModel


class UserSettings(SQLModel, table=True):
    """User settings database model."""

    __tablename__ = "user_settings"

    id: int | None = Field(default=None, primary_key=True)
    monthly_expenses: float = Field(default=0.0)
    risk_profile: str = Field(default="moderate")
    usd_to_pln_rate: float = Field(default=4.0)
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)
