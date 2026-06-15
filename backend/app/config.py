"""Application configuration.

Settings are loaded from environment variables (and an optional ``.env`` file)
via ``pydantic-settings``. Importing :data:`settings` anywhere in the app yields
a single, validated, cached configuration object.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings."""

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application ----
    app_name: str = "Repository Analyzer"
    environment: str = "development"
    log_level: str = "INFO"

    # ---- Server ----
    host: str = "0.0.0.0"
    port: int = 8000

    # ---- Database ----
    database_url: str = "sqlite:///./data/analyzer.db"

    # ---- CORS ----
    # ``NoDecode`` disables pydantic-settings' default JSON parsing for these
    # list fields so the comma-separated validator below handles raw strings
    # like ``a,b,c`` (otherwise a non-JSON env value would raise on load).
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ---- Scanning ----
    ignored_dirs: Annotated[list[str], NoDecode] = [
        ".git", "node_modules", "venv", ".venv", "dist", "build",
        "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        ".idea", ".vscode",
    ]
    max_file_size: int = 1_048_576  # 1 MiB

    # ---- AI provider ----
    ai_provider: str = "none"  # openai | gemini | none
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    ai_max_tokens: int = 600
    ai_temperature: float = 0.2

    @field_validator("cors_origins", "ignored_dirs", mode="before")
    @classmethod
    def _split_comma_separated(cls, value: object) -> object:
        """Allow comma-separated strings for list-typed settings.

        Environment variables are always strings, so ``CORS_ORIGINS=a,b`` is
        normalised into ``["a", "b"]`` here.
        """
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def ai_enabled(self) -> bool:
        """True when a provider is selected and its API key is present."""
        provider = self.ai_provider.lower()
        if provider == "openai":
            return bool(self.openai_api_key)
        if provider == "gemini":
            return bool(self.gemini_api_key)
        return False


@lru_cache
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()


settings = get_settings()
