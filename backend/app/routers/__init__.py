"""Routers package."""

from app.routers.assets import router as assets_router
from app.routers.auth import router as auth_router
from app.routers.bonds import router as bonds_router
from app.routers.cash import router as cash_router
from app.routers.password_reset import router as password_reset_router
from app.routers.portfolio import router as portfolio_router
from app.routers.profile import router as profile_router
from app.routers.summary import router as summary_router

__all__ = [
    "assets_router",
    "auth_router",
    "bonds_router",
    "cash_router",
    "password_reset_router",
    "portfolio_router",
    "profile_router",
    "summary_router",
]
