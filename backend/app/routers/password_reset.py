"""Router for password-reset endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.database import get_db
from ..schemas.password_reset import (
    PasswordResetConfirmSchema,
    PasswordResetRequestSchema,
    PasswordResetResponseSchema,
)
from ..services.password_reset import confirm_password_reset, request_password_reset

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/password-reset/request",
    response_model=PasswordResetResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def password_reset_request(
    payload: PasswordResetRequestSchema,
    session: Session = Depends(get_db),
) -> PasswordResetResponseSchema:
    """
    Initiate a password-reset flow for the submitted email address.

    Always returns 202 regardless of whether the email is registered, to
    prevent account enumeration.

    Args:
        payload: Request body containing the user email.
        session: Database session injected via dependency.

    Returns:
        PasswordResetResponseSchema: Confirmation message.
    """
    request_password_reset(email=str(payload.email), session=session)
    return PasswordResetResponseSchema(
        message="If that address is registered you will receive a reset link shortly."
    )


@router.post(
    "/password-reset/confirm",
    response_model=PasswordResetResponseSchema,
)
def password_reset_confirm(
    payload: PasswordResetConfirmSchema,
    session: Session = Depends(get_db),
) -> PasswordResetResponseSchema:
    """
    Complete the password-reset flow using the one-time token.

    Args:
        payload: Request body with token and new password.
        session: Database session injected via dependency.

    Returns:
        PasswordResetResponseSchema: Confirmation message.

    Raises:
        HTTPException 400: If the token is invalid, expired, or already used.
    """
    try:
        confirm_password_reset(
            raw_token=payload.token,
            new_password=payload.new_password,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return PasswordResetResponseSchema(message="Password updated successfully.")
