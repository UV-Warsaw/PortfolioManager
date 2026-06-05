"""Repository layer for OtherAsset database operations."""

from sqlmodel import Session, select

from app.models.assets import OtherAsset
from app.repositories.base import BaseRepository


class OtherAssetRepository(BaseRepository[OtherAsset]):
    """Repository for managing OtherAsset database operations."""

    def __init__(self, session: Session) -> None:
        """Initialize other asset repository with session.

        Args:
            session: Active database session.
        """
        super().__init__(OtherAsset, session)

    def list_all(self, user_id: int) -> list[OtherAsset]:
        """Get all assets for the given user ordered by creation date."""
        stmt = (
            select(OtherAsset)
            .where(OtherAsset.user_id == user_id)
            .order_by(OtherAsset.created_at.desc())
        )
        return list(self.session.exec(stmt).all())

    def get_by_name(self, name: str, user_id: int) -> OtherAsset | None:
        """Get an asset by name scoped to the given user."""
        stmt = select(OtherAsset).where(
            OtherAsset.name == name, OtherAsset.user_id == user_id
        )
        return self.session.exec(stmt).first()
