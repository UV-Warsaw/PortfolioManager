"""Repository for user data access."""

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
