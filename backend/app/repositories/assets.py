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

    def list_all(self) -> list[OtherAsset]:
        """Get all manually-valued assets ordered by creation date (newest first).

        Returns:
            List of all other assets.
        """
        stmt = select(OtherAsset).order_by(OtherAsset.created_at.desc())
        return list(self.session.exec(stmt).all())

    def get_by_name(self, name: str) -> OtherAsset | None:
        """Get an asset by its name.

        Args:
            name: The asset name to search for.

        Returns:
            The OtherAsset if found, None otherwise.
        """
        stmt = select(OtherAsset).where(OtherAsset.name == name)
        return self.session.exec(stmt).first()
