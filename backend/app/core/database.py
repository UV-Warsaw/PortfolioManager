import logging
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel

from ..models.bonds import Bond  # noqa: F401
from ..models.cash import CashAccount  # noqa: F401
from ..models.portfolio import Asset, Dividend, Transaction  # noqa: F401
from ..models.user_settings import UserSettings  # noqa: F401
from .config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args=(
        {"check_same_thread": False} if "sqlite" in settings.database_url else {}
    ),
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def create_db_and_tables() -> None:
    """Create all database tables defined in SQLModel metadata."""
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as exc:
        logger.exception("Failed to create database tables: %s", exc)
        raise


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session for use as a FastAPI dependency.

    Yields:
        Session: SQLModel database session.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
