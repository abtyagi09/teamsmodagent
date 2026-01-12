"""
Quick test to verify App Configuration read/write after deployment.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import save_json_config, load_json_config


def test_write_read():
    """Test write and read operations."""
    print("=" * 60)
    print("Testing App Configuration Write/Read")
    print("=" * 60)
    print()

    # Check environment variable
    endpoint = os.getenv("APP_CONFIG_ENDPOINT")
    if not endpoint:
        print("❌ APP_CONFIG_ENDPOINT not set!")
        print("Set it with:")
        print('  $env:APP_CONFIG_ENDPOINT = "https://appconfig-lwzjbolv6jpio.azconfig.io"')
        return False
    
    print(f"✅ Using endpoint: {endpoint}")
    print()

    # Test data
    test_config = {
        "monitored_channels": ["general", "test-channel"],
        "test_timestamp": "2026-01-06T20:00:00Z"
    }

    # Test write
    print("📝 Testing WRITE operation...")
    try:
        save_json_config("channels.json", test_config)
        print("✅ Write completed (check logs above)")
    except Exception as e:
        print(f"❌ Write failed: {e}")
        return False
    
    print()

    # Test read
    print("📖 Testing READ operation...")
    try:
        loaded_config = load_json_config("channels.json", use_cache=False)
        print(f"✅ Read completed")
        print(f"   Monitored channels: {loaded_config.get('monitored_channels', [])}")
        
        # Verify
        if loaded_config.get("monitored_channels") == test_config["monitored_channels"]:
            print("✅ Data matches - round-trip successful!")
            return True
        else:
            print("⚠️  Data doesn't match - may be reading from local file")
            return False
    except Exception as e:
        print(f"❌ Read failed: {e}")
        return False


if __name__ == "__main__":
    success = test_write_read()
    print()
    print("=" * 60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed - check errors above")
    print("=" * 60)
    sys.exit(0 if success else 1)
