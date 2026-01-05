"""
Setup verification script.

Run this to verify your Azure resources and configuration are correct
before starting the moderation system.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config_loader import get_settings, load_json_config


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_check(name: str, status: bool, details: str = ""):
    """Print check result."""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")


async def verify_settings():
    """Verify environment configuration."""
    print_header("Checking Environment Configuration")

    try:
        settings = get_settings()
        print_check("Environment file loaded", True, f"Found .env file")

        # Check required settings
        checks = [
            ("Microsoft Foundry Endpoint", bool(settings.foundry_project_endpoint)),
            ("Model Deployment", bool(settings.foundry_model_deployment)),
            ("Content Safety Endpoint", bool(settings.content_safety_endpoint)),
            ("Teams Tenant ID", bool(settings.teams_tenant_id)),
            ("Teams Client ID", bool(settings.teams_client_id)),
            ("Teams Client Secret", bool(settings.teams_client_secret)),
            ("Teams Team ID", bool(settings.teams_team_id)),
        ]

        all_passed = True
        for name, passed in checks:
            print_check(name, passed)
            if not passed:
                all_passed = False

        return all_passed

    except Exception as e:
        print_check("Load environment", False, str(e))
        return False


def verify_config_files():
    """Verify configuration files exist."""
    print_header("Checking Configuration Files")

    try:
        # Check channels config
        try:
            channels = load_json_config("channels.json")
            monitored = channels.get("monitored_channels", [])
            print_check(
                "Channels configuration",
                True,
                f"Monitoring {len(monitored)} channels: {', '.join(monitored)}",
            )
        except FileNotFoundError:
            print_check(
                "Channels configuration",
                False,
                "Copy config/channels.example.json to config/channels.json",
            )
            return False

        # Check policies config
        try:
            policies = load_json_config("policies.json")
            text_policies = policies.get("text_policies", {})
            enabled_count = sum(1 for p in text_policies.values() if p.get("enabled", False))
            print_check(
                "Policies configuration",
                True,
                f"{enabled_count}/{len(text_policies)} policies enabled",
            )
        except FileNotFoundError:
            print_check(
                "Policies configuration",
                False,
                "Copy config/policies.example.json to config/policies.json",
            )
            return False

        return True

    except Exception as e:
        print_check("Configuration files", False, str(e))
        return False


async def verify_azure_foundry():
    """Verify Microsoft Foundry connection."""
    print_header("Checking Microsoft Foundry Connection")

    try:
        from azure.identity import DefaultAzureCredential
        from agent_framework_azure_ai import AzureAIAgentClient

        settings = get_settings()

        # Try to create client (doesn't make API call yet)
        try:
            credential = DefaultAzureCredential()
            client = AzureAIAgentClient(
                project_endpoint=settings.foundry_project_endpoint,
                model_deployment_name=settings.foundry_model_deployment,
                async_credential=credential,
                agent_name="TestAgent",
            )
            print_check("Microsoft Foundry client initialized", True)
            print_check("Endpoint configured", True, settings.foundry_project_endpoint)
            print_check("Model deployment", True, settings.foundry_model_deployment)
            return True
        except Exception as e:
            print_check("Microsoft Foundry connection", False, str(e))
            return False

    except ImportError as e:
        print_check("Agent Framework installed", False, "Run: pip install agent-framework-azure-ai --pre")
        return False


async def verify_content_safety():
    """Verify Content Safety connection."""
    print_header("Checking Azure AI Content Safety")

    try:
        from azure.ai.contentsafety import ContentSafetyClient
        from azure.core.credentials import AzureKeyCredential

        settings = get_settings()

        if not settings.content_safety_key:
            print_check("Content Safety key", False, "Key not configured in .env")
            return False

        try:
            client = ContentSafetyClient(
                endpoint=settings.content_safety_endpoint,
                credential=AzureKeyCredential(settings.content_safety_key),
            )
            print_check("Content Safety client initialized", True)
            print_check("Endpoint configured", True, settings.content_safety_endpoint)
            return True
        except Exception as e:
            print_check("Content Safety connection", False, str(e))
            return False

    except ImportError:
        print_check("Content Safety SDK installed", False, "Check requirements.txt")
        return False


async def verify_teams_access():
    """Verify Teams Graph API access."""
    print_header("Checking Microsoft Teams Access")

    try:
        from azure.identity.aio import ClientSecretCredential
        from msgraph import GraphServiceClient

        settings = get_settings()

        try:
            credential = ClientSecretCredential(
                tenant_id=settings.teams_tenant_id,
                client_id=settings.teams_client_id,
                client_secret=settings.teams_client_secret,
            )

            client = GraphServiceClient(
                credentials=credential,
                scopes=["https://graph.microsoft.com/.default"],
            )

            print_check("Teams credentials configured", True)
            print_check("Team ID configured", True, settings.teams_team_id)

            # Note: We don't test actual API call to avoid auth issues in verification
            print("   ℹ️  Note: Actual API access will be tested when running the app")

            await credential.close()
            return True

        except Exception as e:
            print_check("Teams access", False, str(e))
            return False

    except ImportError:
        print_check("Graph SDK installed", False, "Check requirements.txt")
        return False


async def main():
    """Run all verification checks."""
    print("\n🔍 Teams Moderation System - Setup Verification\n")

    results = []

    # Run all checks
    results.append(await verify_settings())
    results.append(verify_config_files())
    results.append(await verify_azure_foundry())
    results.append(await verify_content_safety())
    results.append(await verify_teams_access())

    # Summary
    print_header("Verification Summary")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("\n🚀 Your system is ready to run!")
        print("\nNext steps:")
        print("  1. Test in dry-run mode: python src/main.py --dry-run")
        print("  2. Monitor a specific channel: python src/main.py --dry-run --channel general")
        print("  3. Review policies: edit config/policies.json")
        print("\n")
        return 0
    else:
        print(f"❌ Some checks failed ({passed}/{total} passed)")
        print("\n⚠️  Please fix the issues above before proceeding.")
        print("\nCommon solutions:")
        print("  • Missing .env: Copy .env.example to .env and fill in values")
        print("  • Missing config: Copy config/*.example.json to config/*.json")
        print("  • Import errors: Run 'pip install -r requirements.txt'")
        print("  • Auth errors: Verify Azure credentials and permissions")
        print("\n📖 See QUICKSTART.md for detailed setup instructions")
        print("\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
