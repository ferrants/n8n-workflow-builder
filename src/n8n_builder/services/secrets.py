"""Secrets service for managing environment variables and API keys."""

import os
from typing import Optional
from dotenv import load_dotenv


class SecretsService:
    """Service for loading and managing secrets from environment variables."""

    def __init__(self, env_file: Optional[str] = None) -> None:
        """Initialize the secrets service.

        Args:
            env_file: Path to the .env file. If None, uses default .env file.
        """
        self._loaded = False
        self._env_file = env_file or ".env"
        self._load_secrets()

    def _load_secrets(self) -> None:
        """Load secrets from the .env file."""
        if os.path.exists(self._env_file):
            load_dotenv(self._env_file)
            self._loaded = True
        else:
            print(f"Warning: .env file not found at {self._env_file}")

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value by key.

        Args:
            key: The environment variable key
            default: Default value if key is not found

        Returns:
            The secret value or default if not found
        """
        return os.getenv(key, default)

    def get_required_secret(self, key: str) -> str:
        """Get a required secret value by key.

        Args:
            key: The environment variable key

        Returns:
            The secret value

        Raises:
            ValueError: If the secret is not found
        """
        value = self.get_secret(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found in environment")
        return value

    def is_loaded(self) -> bool:
        """Check if secrets were successfully loaded."""
        return self._loaded
