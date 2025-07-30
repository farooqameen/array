"""
Application settings and configuration.
"""

import os
from typing import List
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application metadata
    app_name: str = "Data Parser API"
    app_version: str = "0.1.0"
    description: str = "A FastAPI application for data parsing with uv"
    debug: bool = False

    # Project root directory
    PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()

    # Upload directory for files
    UPLOAD_DIR: Path = PROJECT_ROOT / "uploads"

    # CORS settings
    allowed_origins: List[str] = ["*"]
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]

    # Frontend origin (for production CORS)
    frontend_origin: str = "http://localhost:3000"

    # API configuration
    api_v1_prefix: str = "/api/v1"

    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE: Path = PROJECT_ROOT / "logs" / "app.log"

    # Rate limiting
    rate_limit_per_minute: int = 100


# Create a global settings instance
settings = Settings()
