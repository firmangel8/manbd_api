"""
Application configuration.

Reads settings from environment variables (or a `.env` file) so the same
code can run on a laptop, in CI, or in production without changes.

Students: notice we never hard-code passwords inside the source code.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app settings live here, loaded from the `.env` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    APP_NAME: str = "Library API Starter Kit"
    DEBUG: bool = True

    # --- Database ---
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "db_library"

    @property
    def database_url(self) -> str:
        """Build the SQLAlchemy connection URL from the individual settings."""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    """Cache the settings object so the `.env` file is read only once."""
    return Settings()
