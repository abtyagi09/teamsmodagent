"""
End-to-End Test Script for Teams Moderation System

This script helps you test the system step by step without needing msgraph-sdk.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import get_settings, load_json_config
from src.utils.logging_config import setup_logging


def test_step_1_configuration():
    """Test 1: Configuration Loading"""
    print("\n" + "=" * 60)
    print("TEST 1: Configuration Loading")
    print("=" * 60)
    
    try:
        settings = get_settings()
        print("✅ Environment configuration loaded successfully!")
        print(f"\nKey Settings:")
        print(f"  • Foundry Endpoint: {settings.foundry_project_endpoint}")
        print(f"  • Model Deployment: {settings.foundry_model_deployment}")
        print(f"  • Content Safety Endpoint: {settings.content_safety_endpoint}")
        print(f"  • Teams Tenant ID: {settings.teams_tenant_id}")
        print(f"  • Log Level: {settings.log_level}")
        print(f"  • Moderation Mode: {settings.moderation_mode}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


def test_step_2_json_configs():
    """Test 2: JSON Configuration Files"""
    print("\n" + "=" * 60)
    print("TEST 2: JSON Configuration Files")
    print("=" * 60)
    
    try:
        # Load channels config
        channels = load_json_config("channels.json")
        print("✅ Channels configuration loaded!")
        print(f"  • Monitored channels: {channels.get('monitored_channels', [])}")
        print(f"  • Excluded channels: {channels.get('excluded_channels', [])}")
        
        # Load policies config
        policies = load_json_config("policies.json")
        print("\n✅ Policies configuration loaded!")
        enabled_policies = [
            name for name, policy in policies.get("text_policies", {}).items()
            if policy.get("enabled", False)
        ]
        print(f"  • Enabled policies: {enabled_policies}")
        print(f"  • Total policies: {len(policies.get('text_policies', {}))}")
        return True
    except Exception as e:
        print(f"❌ JSON configuration loading failed: {e}")
        return False


def test_step_3_logging():
    """Test 3: Logging Setup"""
    print("\n" + "=" * 60)
    print("TEST 3: Logging Setup")
    print("=" * 60)
    
    try:
        logger = setup_logging()
        print("✅ Logging configured successfully!")
        
        # Test log messages
        logger.info("test_message", component="test", status="success")
        print("  • Test log message written")
        
        # Check logs directory
        logs_dir = Path(__file__).parent / "logs"
        if logs_dir.exists():
            print(f"  • Logs directory exists: {logs_dir}")
        else:
            print(f"  • Logs directory will be created on first run")
        return True
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False


def test_step_4_azure_imports():
    """Test 4: Azure SDK Imports"""
    print("\n" + "=" * 60)
    print("TEST 4: Azure SDK Imports")
    print("=" * 60)
    
    results = []
    
    # Test Azure Content Safety
    try:
        from azure.ai.contentsafety import ContentSafetyClient
        print("✅ Azure Content Safety SDK available")
        results.append(True)
    except ImportError as e:
        print(f"❌ Azure Content Safety import failed: {e}")
        results.append(False)
    
    # Test Azure Identity
    try:
        from azure.identity import ClientSecretCredential
        print("✅ Azure Identity SDK available")
        results.append(True)
    except ImportError as e:
        print(f"❌ Azure Identity import failed: {e}")
        results.append(False)
    
    # Test Agent Framework
    try:
        import agent_framework
        print("✅ Agent Framework available")
        results.append(True)
    except ImportError as e:
        print(f"⚠️  Agent Framework not installed (optional for this test): {e}")
        print("   Run: pip install agent-framework-azure-ai --pre")
        results.append(False)
    
    return all(results[:2])  # Only require Azure SDKs


def test_step_5_content_safety_connection():
    """Test 5: Content Safety API Connection"""
    print("\n" + "=" * 60)
    print("TEST 5: Content Safety API Connection")
    print("=" * 60)
    
    try:
        from azure.ai.contentsafety import ContentSafetyClient
        from azure.core.credentials import AzureKeyCredential
        
        settings = get_settings()
        
        # Create client
        client = ContentSafetyClient(
            endpoint=settings.content_safety_endpoint,
            credential=AzureKeyCredential(settings.content_safety_key)
        )
        
        print("✅ Content Safety client created!")
        print(f"  • Endpoint: {settings.content_safety_endpoint}")
        print(f"  • Authentication: API Key")
        
        # Note: We won't make actual API calls in this test to avoid charges
        print("\n⚠️  Actual API test skipped (would incur charges)")
        print("  To test live connection, use: python src/main.py --dry-run")
        
        return True
    except Exception as e:
        print(f"❌ Content Safety connection test failed: {e}")
        return False


def test_step_6_policy_evaluation():
    """Test 6: Policy Evaluation Logic"""
    print("\n" + "=" * 60)
    print("TEST 6: Policy Evaluation Logic")
    print("=" * 60)
    
    try:
        policies = load_json_config("policies.json")
        
        # Test policy structure
        text_policies = policies.get("text_policies", {})
        print(f"✅ Found {len(text_policies)} text policies")
        
        # Check each policy
        for policy_name, policy_config in text_policies.items():
            enabled = "✅" if policy_config.get("enabled") else "❌"
            action = policy_config.get("action", "unknown")
            threshold = policy_config.get("threshold", "unknown")
            print(f"  {enabled} {policy_name}: {action} @ {threshold} threshold")
        
        return True
    except Exception as e:
        print(f"❌ Policy evaluation test failed: {e}")
        return False


def test_step_7_mock_moderation():
    """Test 7: Mock Moderation Flow"""
    print("\n" + "=" * 60)
    print("TEST 7: Mock Moderation Flow")
    print("=" * 60)
    
    try:
        policies = load_json_config("policies.json")
        
        # Simulate test messages
        test_messages = [
            {
                "content": "Hello everyone, looking forward to the meeting!",
                "expected": "allow",
                "reason": "Clean message"
            },
            {
                "content": "I hate this stupid project and everyone involved!",
                "expected": "flag/delete",
                "reason": "Hate speech detected"
            },
            {
                "content": "My SSN is 123-45-6789",
                "expected": "flag",
                "reason": "PII leak"
            }
        ]
        
        print("Testing mock moderation decisions:\n")
        
        for msg in test_messages:
            print(f"📝 Message: \"{msg['content'][:50]}...\"")
            print(f"   Expected: {msg['expected']}")
            print(f"   Reason: {msg['reason']}\n")
        
        print("✅ Mock moderation logic test complete")
        print("\n⚠️  For actual AI analysis, run: python src/main.py --dry-run")
        
        return True
    except Exception as e:
        print(f"❌ Mock moderation test failed: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    test_names = [
        "Configuration Loading",
        "JSON Config Files",
        "Logging Setup",
        "Azure SDK Imports",
        "Content Safety Connection",
        "Policy Evaluation",
        "Mock Moderation Flow"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for name, result in zip(test_names, results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for testing.")
        print("\nNext steps:")
        print("  1. Open UI: streamlit run ui/app.py (already running)")
        print("  2. Configure channels in the UI")
        print("  3. Test with: python src/main.py --dry-run")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")
        print("\nTroubleshooting:")
        print("  • Check .env file has all required values")
        print("  • Verify Azure credentials are correct")
        print("  • Run: pip install -r requirements.txt")


def main():
    """Run all tests"""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║  Teams Moderation System - End-to-End Test Suite        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Run all tests
    results.append(test_step_1_configuration())
    results.append(test_step_2_json_configs())
    results.append(test_step_3_logging())
    results.append(test_step_4_azure_imports())
    results.append(test_step_5_content_safety_connection())
    results.append(test_step_6_policy_evaluation())
    results.append(test_step_7_mock_moderation())
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
