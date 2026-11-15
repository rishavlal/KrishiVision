"""
KrishiVision Core Application Configuration
===========================================
"""

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value.")


class Settings:
    PROJECT_NAME: str = "कृषिVision AI"
    PROJECT_TITLE: str = "कृषिVision – Intelligent Crop Recommendation and Plant Disease Detection System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    APP_ENV: str = os.getenv("APP_ENV", "development").strip().lower()

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "").strip()
    if not SECRET_KEY:
        if APP_ENV != "development":
            raise RuntimeError("SECRET_KEY must be configured outside development.")
        SECRET_KEY = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Demo user seeding is opt-in and limited to development.
    DEMO_USER_ENABLED: bool = _env_bool("DEMO_USER_ENABLED")
    DEMO_USER_USERNAME: str = os.getenv("DEMO_USER_USERNAME", "").strip()
    DEMO_USER_EMAIL: str = os.getenv("DEMO_USER_EMAIL", "").strip()
    DEMO_USER_PASSWORD: str = os.getenv("DEMO_USER_PASSWORD", "")
    DEMO_USER_NAME: str = os.getenv("DEMO_USER_NAME", "").strip()
    DEMO_USER_LOCATION: str = os.getenv("DEMO_USER_LOCATION", "").strip()
    DEMO_USER_FARM_SIZE: float = float(os.getenv("DEMO_USER_FARM_SIZE", "3.5"))

    if DEMO_USER_ENABLED:
        if APP_ENV != "development":
            raise RuntimeError("Demo user seeding can only be enabled in development.")
        if not DEMO_USER_USERNAME or not DEMO_USER_EMAIL or not DEMO_USER_PASSWORD:
            raise RuntimeError(
                "DEMO_USER_USERNAME, DEMO_USER_EMAIL, and DEMO_USER_PASSWORD "
                "must be configured when DEMO_USER_ENABLED is true."
            )


settings = Settings()
