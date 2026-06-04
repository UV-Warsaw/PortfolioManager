"""Service layer for OtherAsset (manual valuation) business logic."""

from datetime import datetime

from sqlmodel import Session

from app.models.assets import OtherAsset
from app.repositories.assets import OtherAssetRepository
from app.schemas.assets import (
    OtherAssetAnalysisResponse,
    OtherAssetCreate,
    OtherAssetResponse,
    OtherAssetsPortfolioSummaryResponse,
    OtherAssetUpdate,
)


class OtherAssetService:
    """Service for OtherAsset business operations."""

    def __init__(self, session: Session) -> None:
        """Initialize OtherAssetService.

        Args:
            session: SQLModel database session.
        """
        self.repo = OtherAssetRepository(session)

    @staticmethod
    def _calculate_pnl(
        current_value: float,
        quantity: float | None,
        purchase_price: float | None,
    ) -> dict:
        """Calculate P&L for an asset when cost basis is known.

        Args:
            current_value: Current total market value.
            quantity: Number of units held.
            purchase_price: Purchase price per unit.

        Returns:
            Dict with total_cost, profit, profit_pct (all None if data missing).
        """
        if quantity is None or purchase_price is None:
            return {"total_cost": None, "profit": None, "profit_pct": None}
        total_cost = round(quantity * purchase_price, 2)
        profit = round(current_value - total_cost, 2)
        profit_pct = round((profit / total_cost * 100), 2) if total_cost > 0 else None
        return {"total_cost": total_cost, "profit": profit, "profit_pct": profit_pct}

    def create(self, data: OtherAssetCreate) -> OtherAssetResponse:
        """Create a new manually-valued asset.

        Args:
            data: Asset creation data.

        Returns:
            The created asset as OtherAssetResponse.

        Raises:
            ValueError: If an asset with the same name already exists.
        """
        if self.repo.get_by_name(data.name):
            raise ValueError(f"Asset '{data.name}' already exists")
        asset = OtherAsset(
            name=data.name,
            asset_class=data.asset_class,
            current_value=data.current_value,
            currency=data.currency,
            quantity=data.quantity,
            purchase_price=data.purchase_price,
            notes=data.notes,
        )
        self.repo.create(asset)
        return OtherAssetResponse.model_validate(asset)

    def get(self, asset_id: int) -> OtherAssetResponse | None:
        """Get a single asset by ID.

        Args:
            asset_id: The asset ID.

        Returns:
            OtherAssetResponse or None if not found.
        """
        asset = self.repo.get_by_id(asset_id)
        return OtherAssetResponse.model_validate(asset) if asset else None

    def list_all(self) -> list[OtherAssetResponse]:
        """Get all manually-valued assets.

        Returns:
            List of all assets as OtherAssetResponse objects.
        """
        return [OtherAssetResponse.model_validate(a) for a in self.repo.list_all()]

    def update(
        self, asset_id: int, data: OtherAssetUpdate
    ) -> OtherAssetResponse | None:
        """Update an existing asset.

        Args:
            asset_id: The asset ID to update.
            data: Partial asset data to update.

        Returns:
            Updated OtherAssetResponse or None if not found.

        Raises:
            ValueError: If updating name to one that already exists.
        """
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            return None
        if data.name is not None and data.name != asset.name:
            if self.repo.get_by_name(data.name):
                raise ValueError(f"Asset '{data.name}' already exists")
        for field, val in data.model_dump(exclude_unset=True).items():
            setattr(asset, field, val)
        asset.updated_at = datetime.now()
        self.repo.update(asset)
        return OtherAssetResponse.model_validate(asset)

    def delete(self, asset_id: int) -> bool:
        """Delete an asset by ID.

        Args:
            asset_id: The asset ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            return False
        self.repo.delete(asset)
        return True

    def analyze(self, asset_id: int) -> OtherAssetAnalysisResponse | None:
        """Get P&L analysis for a single asset.

        Args:
            asset_id: The asset ID.

        Returns:
            OtherAssetAnalysisResponse or None if not found.
        """
        asset = self.repo.get_by_id(asset_id)
        if not asset:
            return None
        pnl = self._calculate_pnl(
            asset.current_value, asset.quantity, asset.purchase_price
        )
        return OtherAssetAnalysisResponse(
            asset_id=asset.id,
            name=asset.name,
            asset_class=asset.asset_class,
            current_value=asset.current_value,
            currency=asset.currency,
            **pnl,
        )

    def portfolio_summary(self) -> OtherAssetsPortfolioSummaryResponse:
        """Get aggregated summary of all manually-valued assets.

        Returns:
            OtherAssetsPortfolioSummaryResponse with totals and per-class breakdown.
        """
        assets = self.repo.list_all()
        if not assets:
            return OtherAssetsPortfolioSummaryResponse(
                total_value=0.0,
                total_cost=0.0,
                total_profit=0.0,
                assets_count=0,
                assets_by_class={},
            )

        total_value = 0.0
        total_cost = 0.0
        by_class: dict[str, dict] = {}

        for a in assets:
            total_value += a.current_value
            pnl = self._calculate_pnl(a.current_value, a.quantity, a.purchase_price)
            if pnl["total_cost"] is not None:
                total_cost += pnl["total_cost"]

            key = a.asset_class.value
            if key not in by_class:
                by_class[key] = {"count": 0, "total_value": 0.0}
            by_class[key]["count"] += 1
            by_class[key]["total_value"] = round(
                by_class[key]["total_value"] + a.current_value, 2
            )

        total_profit = round(total_value - total_cost, 2)

        return OtherAssetsPortfolioSummaryResponse(
            total_value=round(total_value, 2),
            total_cost=round(total_cost, 2),
            total_profit=total_profit,
            assets_count=len(assets),
            assets_by_class=by_class,
        )
