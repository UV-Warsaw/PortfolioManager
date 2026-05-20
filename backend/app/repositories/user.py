"""Repository for user data access."""

from datetime import UTC, datetime

from sqlmodel import Session, select

from ..models.user import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User database operations."""

    def __init__(self, session: Session) -> None:
        """
        Initialise with the User model.

        Args:
            session: Active database session.
        """
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by email address.

        Args:
            email: Email to search for.

        Returns:
            User instance or None if not found.
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def create(self, email: str, password_hash: str, created_at: str) -> User:
        """
        Insert a new user record.

        Args:
            email: Unique email address.
            password_hash: Bcrypt hash of the password.
            created_at: ISO-formatted creation timestamp.

        Returns:
            Persisted User instance.
        """
        user = User(
            email=email,
            password_hash=password_hash,
            risk_level="moderate",
            monthly_expenses=0.0,
            created_at=created_at,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_email(self, user_id: int, new_email: str) -> User | None:
        """
        Update the email address for the given user.

        Args:
            user_id: Primary key of the user to update.
            new_email: New unique email address.

        Returns:
            Updated User instance, or None if not found.
        """
        user = self.get_by_id(user_id)
        if user is None:
            return None
        user.email = new_email
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_password(self, user_id: int, new_password_hash: str) -> User | None:
        """
        Replace the stored password hash for the given user.

        Args:
            user_id: Primary key of the user to update.
            new_password_hash: Bcrypt hash of the new password.

        Returns:
            Updated User instance, or None if not found.
        """
        user = self.get_by_id(user_id)
        if user is None:
            return None
        user.password_hash = new_password_hash
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_profile_settings(
        self,
        user_id: int,
        risk_level: str | None,
        monthly_expenses: float | None,
    ) -> User | None:
        """
        Update risk level and/or monthly expenses for the given user.

        Only fields that are not None are applied.

        Args:
            user_id: Primary key of the user to update.
            risk_level: New risk level string, or None to leave unchanged.
            monthly_expenses: New monthly expenses value, or None to leave unchanged.

        Returns:
            Updated User instance, or None if not found.
        """
        user = self.get_by_id(user_id)
        if user is None:
            return None
        if risk_level is not None:
            user.risk_level = risk_level
        if monthly_expenses is not None:
            user.monthly_expenses = monthly_expenses
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
