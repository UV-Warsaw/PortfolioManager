"""FastAPI router for Other Asset (manual valuation) endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from app.core.database import get_db
from app.schemas.assets import (
    OtherAssetAnalysisResponse,
    OtherAssetCreate,
    OtherAssetResponse,
    OtherAssetsPortfolioSummaryResponse,
    OtherAssetUpdate,
)
from app.services.assets import OtherAssetService
from app.services.auth import get_current_user

router = APIRouter(prefix="/portfolio/assets", tags=["assets"])
_bearer = HTTPBearer()


@router.post("", response_model=OtherAssetResponse, status_code=201)
def create_asset(
    data: OtherAssetCreate,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> OtherAssetResponse:
    """Create a new manually-valued asset.

    Raises:
        400: If an asset with the same name already exists.
    """
    current_user = get_current_user(credentials, session)
    try:
        return OtherAssetService(session, current_user["id"]).create(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[OtherAssetResponse])
def list_assets(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> list[OtherAssetResponse]:
    """Get all manually-valued assets."""
    current_user = get_current_user(credentials, session)
    return OtherAssetService(session, current_user["id"]).list_all()


@router.get("/summary", response_model=OtherAssetsPortfolioSummaryResponse)
def get_portfolio_summary(
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> OtherAssetsPortfolioSummaryResponse:
    """Get aggregated manually-valued assets portfolio summary."""
    current_user = get_current_user(credentials, session)
    return OtherAssetService(session, current_user["id"]).portfolio_summary()


@router.get("/{asset_id}", response_model=OtherAssetResponse)
def get_asset(
    asset_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> OtherAssetResponse:
    """Get a single manually-valued asset by ID.

    Raises:
        404: If asset not found.
    """
    current_user = get_current_user(credentials, session)
    asset = OtherAssetService(session, current_user["id"]).get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return asset


@router.get("/{asset_id}/analysis", response_model=OtherAssetAnalysisResponse)
def get_asset_analysis(
    asset_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> OtherAssetAnalysisResponse:
    """Get P&L analysis for a manually-valued asset.

    Raises:
        404: If asset not found.
    """
    current_user = get_current_user(credentials, session)
    analysis = OtherAssetService(session, current_user["id"]).analyze(asset_id)
    if not analysis:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    return analysis


@router.put("/{asset_id}", response_model=OtherAssetResponse)
def update_asset(
    asset_id: int,
    data: OtherAssetUpdate,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> OtherAssetResponse:
    """Update a manually-valued asset.

    Raises:
        400: If updating name to one that already exists.
        404: If asset not found.
    """
    current_user = get_current_user(credentials, session)
    try:
        asset = OtherAssetService(session, current_user["id"]).update(asset_id, data)
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
        return asset
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{asset_id}", status_code=204)
def delete_asset(
    asset_id: int,
    session: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> None:
    """Delete a manually-valued asset.

    Raises:
        404: If asset not found.
    """
    current_user = get_current_user(credentials, session)
    if not OtherAssetService(session, current_user["id"]).delete(asset_id):
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
