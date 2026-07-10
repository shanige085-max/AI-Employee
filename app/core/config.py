"""Configuration management and environment loading."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import API_V1_PREFIX, APP_NAME, DEFAULT_DATABASE_URL, DEFAULT_LOG_LEVEL

ENV_FILE = Path(".env")


def load_environment(env_file: Path | str = ENV_FILE) -> None:
    """Load environment variables from a .env file without overriding process values."""
    load_dotenv(dotenv_path=env_file, override=False)


class Settings(BaseSettings):
    """Typed application settings sourced from environment variables."""

    app_name: str = APP_NAME
    environment: Literal["local", "development", "staging", "production", "test"] = "local"
    debug: bool = False
    api_v1_prefix: str = API_V1_PREFIX

    database_url: str = Field(default=DEFAULT_DATABASE_URL, validation_alias="DATABASE_URL")
    database_echo: bool = False

    log_level: str = DEFAULT_LOG_LEVEL
    log_json: bool = False

    background_jobs_enabled: bool = True
    background_job_interval_seconds: float = 60.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def safe_public_settings(self) -> dict[str, object]:
        """Return non-secret settings that may be exposed by the Settings API."""
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "debug": self.debug,
            "api_v1_prefix": self.api_v1_prefix,
            "database_echo": self.database_echo,
            "log_level": self.log_level,
            "background_jobs_enabled": self.background_jobs_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings after loading the local environment file."""
    load_environment()
    return Settings()
