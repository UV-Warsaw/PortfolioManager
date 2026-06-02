"""Routers package."""

from app.routers.auth import router as auth_router
from app.routers.bonds import router as bonds_router
from app.routers.password_reset import router as password_reset_router
from app.routers.portfolio import router as portfolio_router
from app.routers.profile import router as profile_router

__all__ = ["auth_router", "bonds_router", "password_reset_router", "portfolio_router", "profile_router"]
