"""
Diagnostic script to test Azure App Configuration connectivity and data.

Run this script to verify that:
1. APP_CONFIG_ENDPOINT is set correctly
2. Managed Identity can authenticate
3. Configuration keys exist and have correct data
4. Read and write operations work
"""

import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import (
    get_app_config_client,
    load_json_config,
    save_json_config,
)


def main():
    """Run diagnostics."""
    print("=" * 60)
    print("Azure App Configuration Diagnostics")
    print("=" * 60)
    print()

    # Check environment variable
    print("1. Checking APP_CONFIG_ENDPOINT environment variable...")
    endpoint = os.getenv("APP_CONFIG_ENDPOINT")
    if endpoint:
        print(f"   ✅ APP_CONFIG_ENDPOINT is set: {endpoint}")
    else:
        print(f"   ❌ APP_CONFIG_ENDPOINT is NOT set")
        print(f"   Set it with: $env:APP_CONFIG_ENDPOINT='<your-endpoint>'")
        return
    print()

    # Test client initialization
    print("2. Testing Azure App Configuration client initialization...")
    client = get_app_config_client()
    if client:
        print(f"   ✅ Client initialized successfully")
    else:
        print(f"   ❌ Failed to initialize client")
        return
    print()

    # Test reading channels config
    print("3. Testing read of 'channels' configuration...")
    try:
        channels_config = load_json_config("channels.json", use_cache=False)
        print(f"   ✅ Successfully loaded channels.json")
        print(f"   Monitored channels: {channels_config.get('monitored_channels', [])}")
    except Exception as e:
        print(f"   ❌ Failed to load channels.json: {e}")
    print()

    # Test reading policies config
    print("4. Testing read of 'policies' configuration...")
    try:
        policies_config = load_json_config("policies.json", use_cache=False)
        print(f"   ✅ Successfully loaded policies.json")
        enabled_categories = [
            cat for cat, details in policies_config.items() 
            if isinstance(details, dict) and details.get("enabled", False)
        ]
        print(f"   Enabled policy categories: {enabled_categories}")
    except Exception as e:
        print(f"   ❌ Failed to load policies.json: {e}")
    print()

    # List all configuration settings
    print("5. Listing all configuration keys...")
    try:
        settings = client.list_configuration_settings()
        keys = [setting.key for setting in settings]
        print(f"   ✅ Found {len(keys)} configuration keys:")
        for key in keys:
            print(f"      - {key}")
    except Exception as e:
        print(f"   ❌ Failed to list settings: {e}")
    print()

    # Test write operation (if requested)
    print("6. Testing write operation...")
    test_write = input("   Do you want to test writing a test key? (y/n): ").lower()
    if test_write == 'y':
        try:
            test_config = {"test": True, "timestamp": str(os.times())}
            save_json_config("diagnostic-test.json", test_config)
            print(f"   ✅ Successfully wrote test configuration")
            
            # Read it back
            read_back = load_json_config("diagnostic-test.json", use_cache=False)
            if read_back == test_config:
                print(f"   ✅ Read-back verification successful")
            else:
                print(f"   ⚠️  Read-back data doesn't match")
        except Exception as e:
            print(f"   ❌ Write test failed: {e}")
    print()

    # Check RBAC permissions
    print("7. Checking RBAC permissions...")
    print("   The managed identity needs these roles:")
    print("   - App Configuration Data Reader (for reading)")
    print("   - App Configuration Data Owner (for writing)")
    print()
    print("   To assign roles, run:")
    print(f"   az role assignment create \\")
    print(f"       --assignee <PRINCIPAL_ID> \\")
    print(f"       --role 'App Configuration Data Owner' \\")
    print(f"       --scope <APP_CONFIG_RESOURCE_ID>")
    print()

    print("=" * 60)
    print("Diagnostics Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
