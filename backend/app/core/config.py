from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    database_url: str = "sqlite:///./data/portfolio.db"
    database_echo: bool = False

    app_name: str = "Portfolio Manager API"
    debug: bool = False

    secret_key: str = "change-me-in-production"
    access_token_expire_hours: int = 24

    password_reset_expire_hours: int = 1

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    frontend_url: str = "http://localhost:5173"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "noreply@portfoliomanager.local"

    data_dir: Path = Path(__file__).parent.parent.parent / "data"

    usd_to_pln_rate: float = 4.0

    log_level: str = "INFO"
    log_file: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

settings.data_dir.mkdir(parents=True, exist_ok=True)

if settings.log_file is None:
    settings.log_file = str(settings.data_dir / "backend.log")
