"""FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables


def _setup_logging() -> None:
    """Configure application-wide logging to console and file."""
    log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format))

    file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)


_setup_logging()
logger = logging.getLogger("portfolio_backend")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manage application startup and shutdown lifecycle.

    Args:
        application: The FastAPI application instance.

    Yields:
        None
    """
    logger.info("Starting Portfolio Manager Backend API")
    logger.info("Debug mode: %s", settings.debug)
    logger.info("Database URL: %s", settings.database_url)

    create_db_and_tables()
    logger.info("Database initialised")

    yield

    logger.info("Shutting down Portfolio Manager Backend API")


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Portfolio Manager - Microservices Backend API",
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root() -> dict:
    """
    Root endpoint returning basic service information.

    Returns:
        dict: Application name, status, and version.
    """
    return {
        "application": settings.app_name,
        "status": "operational",
        "version": "0.1.0",
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Health check endpoint for container orchestration probes.

    Returns:
        dict: Detailed health status.
    """
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": "0.1.0",
        "database": "connected",
    }
