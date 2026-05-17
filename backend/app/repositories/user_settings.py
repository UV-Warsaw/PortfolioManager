"""Repository for user settings data access."""

from datetime import datetime

from sqlmodel import Session, select

from ..models.user_settings import UserSettings
from .base import BaseRepository


class UserSettingsRepository(BaseRepository[UserSettings]):
    """Repository for user settings database operations."""

    def __init__(self, session: Session) -> None:
        """
        Initialise with the UserSettings model.

        Args:
            session: Active database session.
        """
        super().__init__(UserSettings, session)

    def get_user_settings(self) -> UserSettings | None:
        """
        Return the single user settings record (single-user system).

        Returns:
            UserSettings instance or None.
        """
        statement = select(UserSettings).limit(1)
        return self.session.exec(statement).first()

    def create_or_update_settings(self, monthly_expenses: float) -> UserSettings:
        """
        Create a new settings record or update the existing one.

        Args:
            monthly_expenses: Monthly living expenses amount in PLN.

        Returns:
            UserSettings: Persisted settings instance.
        """
        existing = self.get_user_settings()
        now = datetime.now().isoformat()

        if existing:
            existing.monthly_expenses = monthly_expenses
            existing.updated_at = now
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing

        new_settings = UserSettings(
            monthly_expenses=monthly_expenses,
            created_at=now,
            updated_at=None,
        )
        self.session.add(new_settings)
        self.session.commit()
        self.session.refresh(new_settings)
        return new_settings
