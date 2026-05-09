"""
Configuration loader for the Page Audit Engine.

This module handles environment variable loading and validation,
providing a centralized configuration object for the application.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """Immutable configuration container for the audit engine."""

    openai_api_key: str
    openai_base_url: str
    openai_model: str
    request_timeout: int
    max_retries: int
    user_agent: str

    @classmethod
    def from_environment(cls) -> "Config":
        """
        Load configuration from environment variables.

        Raises:
            ValueError: If required environment variables are missing.

        Returns:
            Config: Immutable configuration instance.
        """
        load_dotenv()

        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please copy .env.example to .env and configure your API key."
            )

        return cls(
            openai_api_key=openai_api_key,
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            user_agent=os.getenv(
                "USER_AGENT",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ),
        )


def _config_signature() -> tuple[Optional[str], ...]:
    """Capture the environment values that materially change configuration."""
    return (
        os.getenv("OPENAI_API_KEY"),
        os.getenv("OPENAI_BASE_URL"),
        os.getenv("OPENAI_MODEL"),
        os.getenv("REQUEST_TIMEOUT"),
        os.getenv("MAX_RETRIES"),
        os.getenv("USER_AGENT"),
    )


# Global configuration instance (lazy-loaded and invalidated on env changes)
_config: Optional[Config] = None
_config_env_signature: Optional[tuple[Optional[str], ...]] = None


def get_config() -> Config:
    """
    Get or create the global configuration instance.

    Returns:
        Config: The application configuration.
    """
    global _config, _config_env_signature
    current_signature = _config_signature()
    if _config is None or _config_env_signature != current_signature:
        _config = Config.from_environment()
        _config_env_signature = current_signature
    return _config


def reload_config() -> Config:
    """
    Force reload of configuration from environment.

    Useful for testing or dynamic reconfiguration.

    Returns:
        Config: Fresh configuration instance.
    """
    global _config, _config_env_signature
    _config = Config.from_environment()
    _config_env_signature = _config_signature()
    return _config
