"""Auth router: account registration."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..core.database import get_db
from ..schemas.auth import RegisterRequest, RegisterResponse
from ..services.auth import register_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    session: Session = Depends(get_db),
) -> RegisterResponse:
    """
    Create a new user account and return an access token.

    Args:
        request: Registration payload with email and password.
        session: Database session injected via dependency.

    Returns:
        RegisterResponse: Account details and JWT access token.

    Raises:
        HTTPException 409: If the email is already registered.
    """
    try:
        result = register_user(
            email=request.email,
            password=request.password,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return RegisterResponse(**result)
