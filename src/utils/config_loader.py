"""
Configuration loader for Teams moderation system.
"""

import json
import os
from pathlib import Path
from typing import Any

from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from azure.identity import DefaultAzureCredential
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
    email_connection_string: str | None = Field(None, description="Azure Communication Services connection string")
    email_sender: str | None = Field(None, description="Sender email address")

    # Application settings
    log_level: str = Field("INFO", description="Logging level")
    moderation_mode: str = Field("monitor", description="Mode: monitor or enforce")
    
    # App Configuration
    app_config_endpoint: str | None = Field(None, description="Azure App Configuration endpoint")


_app_config_client = None


def get_app_config_client() -> AzureAppConfigurationClient | None:
    """
    Get or create Azure App Configuration client.
    
    Returns:
        AzureAppConfigurationClient if endpoint is configured, None otherwise
    """
    global _app_config_client
    
    if _app_config_client is not None:
        return _app_config_client
    
    endpoint = os.getenv("APP_CONFIG_ENDPOINT")
    if not endpoint:
        print("Warning: APP_CONFIG_ENDPOINT not set. Using local config files only.")
        return None
    
    try:
        credential = DefaultAzureCredential()
        _app_config_client = AzureAppConfigurationClient(base_url=endpoint, credential=credential)
        print(f"✅ Connected to Azure App Configuration: {endpoint}")
        return _app_config_client
    except Exception as e:
        print(f"Warning: Failed to initialize App Configuration client: {e}")
        return None


def load_json_config(filename: str, use_cache: bool = True) -> dict[str, Any]:
    """
    Load JSON configuration file.
    
    First tries to load from Azure App Configuration (if available),
    then falls back to local file system.

    Args:
        filename: Name of config file (e.g., 'channels.json')
        use_cache: If False, always fetch fresh from App Configuration (default: True)

    Returns:
        Parsed JSON configuration
    """
    # Try App Configuration first
    app_config_client = get_app_config_client()
    if app_config_client:
        try:
            # Use filename without extension as the key
            key = filename.replace('.json', '')
            print(f"🔍 Loading '{key}' from App Configuration (use_cache={use_cache})...")
            config_value = app_config_client.get_configuration_setting(key=key)
            if config_value and config_value.value:
                config = json.loads(config_value.value)
                if not use_cache:
                    print(f"✅ Refreshed {filename} from App Configuration (no-cache)")
                else:
                    print(f"✅ Loaded {filename} from App Configuration")
                return config
            else:
                print(f"⚠️  Key '{key}' exists but has no value in App Configuration")
        except Exception as e:
            print(f"⚠️  Failed to load {filename} from App Configuration: {e}. Falling back to local file.")
    
    # Fall back to local file
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


def save_json_config(filename: str, config: dict[str, Any]) -> None:
    """
    Save JSON configuration.
    
    Saves to both Azure App Configuration (if available) and local file system.

    Args:
        filename: Name of config file (e.g., 'channels.json')
        config: Configuration dictionary to save
    """
    # Save to App Configuration first
    app_config_client = get_app_config_client()
    if app_config_client:
        try:
            # Use filename without extension as the key
            key = filename.replace('.json', '')
            config_value = json.dumps(config, indent=2)
            print(f"💾 Saving '{key}' to App Configuration...")
            
            # Create ConfigurationSetting object
            setting = ConfigurationSetting(key=key, value=config_value)
            app_config_client.set_configuration_setting(setting)
            
            print(f"✅ Successfully saved {filename} to App Configuration")
        except Exception as e:
            print(f"❌ Failed to save {filename} to App Configuration: {e}")
    else:
        print(f"⚠️  No App Configuration client - saving to local file only")
    
    # Also save to local file for backwards compatibility
    config_path = Path(__file__).parent.parent.parent / "config" / filename
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"💾 Saved {filename} to local file: {config_path}")


def get_settings() -> Settings:
    """
    Get application settings.

    Returns:
        Settings object loaded from environment
    """
    return Settings()
