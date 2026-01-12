"""
Initialize policies in Azure App Configuration from local file.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Set the endpoint
os.environ["APP_CONFIG_ENDPOINT"] = "https://appconfig-lwzjbolv6jpio.azconfig.io"

from src.utils.config_loader import load_json_config, save_json_config


def main():
    print("=" * 60)
    print("Initializing policies in App Configuration")
    print("=" * 60)
    print()

    # Load policies from local file
    print("📖 Loading policies from local file...")
    try:
        policies = load_json_config("policies.json")
        print(f"✅ Loaded policies with {len(policies)} categories")
    except Exception as e:
        print(f"❌ Failed to load local policies: {e}")
        return False

    # Save to App Configuration
    print()
    print("💾 Saving policies to App Configuration...")
    try:
        save_json_config("policies.json", policies)
        print("✅ Policies saved successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to save policies: {e}")
        return False


if __name__ == "__main__":
    success = main()
    print()
    print("=" * 60)
    if success:
        print("✅ Initialization complete!")
        print()
        print("Next steps:")
        print("1. Restart agent to pick up policies immediately:")
        print("   az containerapp restart -g rg-azdteamsmod -n ca-agent-lwzjbolv6jpio")
        print()
        print("2. Or wait 5 minutes for auto-refresh")
    else:
        print("❌ Initialization failed")
    print("=" * 60)
    sys.exit(0 if success else 1)
