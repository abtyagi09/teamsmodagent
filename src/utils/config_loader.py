"""
Configuration loader for Teams moderation system.
"""

import json
import os
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Microsoft Foundry
    foundry_project_endpoint: str = Field(..., description="Microsoft Foundry project endpoint")
    foundry_model_deployment: str = Field(..., description="Model deployment name")
    azure_subscription_id: str | None = Field(None, description="Azure subscription ID")
    azure_resource_group: str | None = Field(None, description="Azure resource group")

    # Azure AI Content Safety
    content_safety_endpoint: str = Field(..., description="Content Safety endpoint")
    content_safety_key: str | None = Field(None, description="Content Safety API key")

    # Microsoft Teams
    teams_tenant_id: str = Field(..., description="Microsoft Entra ID tenant ID")
    teams_client_id: str = Field(..., description="App registration client ID")
    teams_client_secret: str = Field(..., description="App registration client secret")
    teams_team_id: str = Field(..., description="Teams team ID to monitor")

    # Notifications
    notification_email: str | None = Field(None, description="Email for notifications")
    notification_webhook: str | None = Field(None, description="Webhook URL for notifications")

    # Application settings
    log_level: str = Field("INFO", description="Logging level")
    moderation_mode: str = Field("monitor", description="Mode: monitor or enforce")
    polling_interval: int = Field(60, description="Polling interval in seconds")


def load_json_config(filename: str) -> dict[str, Any]:
    """
    Load JSON configuration file.

    Args:
        filename: Name of config file (e.g., 'channels.json')

    Returns:
        Parsed JSON configuration
    """
    config_path = Path(__file__).parent.parent.parent / "config" / filename

    # If main file doesn't exist, try .example.json
    if not config_path.exists():
        example_path = config_path.with_suffix(".example.json")
        if example_path.exists():
            config_path = example_path

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings object loaded from environment
    """
    return Settings()
