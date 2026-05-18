"""Auth router: registration, login, and logout."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from ..core.database import get_db
from ..schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RegisterRequest,
    RegisterResponse,
)
from ..services.auth import get_current_user, login_user, logout_user, register_user

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer_scheme = HTTPBearer()


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


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
    session: Session = Depends(get_db),
) -> LoginResponse:
    """
    Authenticate user and return an access token.

    Args:
        request: Login payload with email and password.
        session: Database session injected via dependency.

    Returns:
        LoginResponse: Account details and JWT access token.

    Raises:
        HTTPException 401: If credentials are invalid.
    """
    try:
        result = login_user(
            email=request.email,
            password=request.password,
            session=session,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return LoginResponse(**result)


@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    session: Session = Depends(get_db),
) -> LogoutResponse:
    """
    Invalidate the current access token.

    Args:
        credentials: Bearer token from Authorization header.
        session: Database session injected via dependency.

    Returns:
        LogoutResponse: Confirmation message.

    Raises:
        HTTPException 401: If token is invalid.
    """
    try:
        logout_user(token=credentials.credentials, session=session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return LogoutResponse()


@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Get current authenticated user information.

    Args:
        current_user: User info from token validation dependency.

    Returns:
        dict with user id and email.
    """
    return current_user
