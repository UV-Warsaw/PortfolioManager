"""Profile router: get, update email, password, and investment settings."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.database import get_db
from ..schemas.profile import (
    ProfileResponse,
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UpdateProfileSettingsRequest,
    UpdateSettingsResponse,
)
from ..services.auth import get_current_user
from ..services.profile import (
    get_profile,
    update_email,
    update_password,
    update_profile_settings,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse)
def get_my_profile(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ProfileResponse:
    """
    Return the full profile for the currently authenticated user.

    Args:
        current_user: User info dict from JWT dependency.
        session: Database session injected via dependency.

    Returns:
        ProfileResponse: Current profile data including risk level and expenses.

    Raises:
        HTTPException 404: If the user record no longer exists.
    """
    try:
        return get_profile(user_id=current_user["id"], session=session)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/email", response_model=ProfileResponse)
def change_email(
    request: UpdateEmailRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> ProfileResponse:
    """
    Change the account email address after verifying the current password.

    Args:
        request: Payload with current_password and new_email.
        current_user: User info dict from JWT dependency.
        session: Database session injected via dependency.

    Returns:
        ProfileResponse: Updated profile with new email.

    Raises:
        HTTPException 400: If current password is wrong or email is taken.
    """
    try:
        return update_email(
            user_id=current_user["id"],
            current_password=request.current_password,
            new_email=str(request.new_email),
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    request: UpdatePasswordRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> None:
    """
    Change the account password after verifying the current password.

    Args:
        request: Payload with current_password, new_password, confirm_password.
        current_user: User info dict from JWT dependency.
        session: Database session injected via dependency.

    Returns:
        None — 204 No Content on success.

    Raises:
        HTTPException 400: If current password is wrong or passwords do not match.
    """
    try:
        update_password(
            user_id=current_user["id"],
            current_password=request.current_password,
            new_password=request.new_password,
            confirm_password=request.confirm_password,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.put("/settings", response_model=UpdateSettingsResponse)
def change_settings(
    request: UpdateProfileSettingsRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> UpdateSettingsResponse:
    """
    Update risk level and/or monthly expenses for the current user.

    Args:
        request: Payload with optional risk_level and monthly_expenses.
        current_user: User info dict from JWT dependency.
        session: Database session injected via dependency.

    Returns:
        UpdateSettingsResponse: Confirmation message and updated profile.

    Raises:
        HTTPException 400: If no fields are provided or user not found.
    """
    try:
        profile = update_profile_settings(
            user_id=current_user["id"],
            risk_level=request.risk_level,
            monthly_expenses=request.monthly_expenses,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UpdateSettingsResponse(profile=profile)
