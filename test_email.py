"""
Test script for email notifications.
Verifies Azure Communication Services email configuration.
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from src.agents.notification_agent import NotificationAgent

# Load environment variables
load_dotenv()


async def test_email_notification():
    """Test sending an email notification."""
    print("🧪 Testing Email Notification System\n")

    # Get configuration
    foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_deployment = os.getenv("FOUNDRY_MODEL_DEPLOYMENT")
    notification_email = os.getenv("NOTIFICATION_EMAIL")
    email_connection_string = os.getenv("EMAIL_CONNECTION_STRING")
    email_sender = os.getenv("EMAIL_SENDER")

    # Check configuration
    print("Configuration:")
    print(f"  Notification Email: {notification_email}")
    print(f"  Email Sender: {email_sender}")
    print(f"  Connection String: {'✓ Set' if email_connection_string else '✗ Missing'}")
    print()

    if not email_connection_string:
        print("❌ ERROR: EMAIL_CONNECTION_STRING not set in .env file")
        print("📖 See docs/EMAIL_SETUP.md for setup instructions")
        return

    # Initialize notification agent
    print("Initializing notification agent...")
    agent = NotificationAgent(
        foundry_endpoint=foundry_endpoint,
        model_deployment=model_deployment,
        notification_email=notification_email,
        email_connection_string=email_connection_string,
        email_sender=email_sender,
    )

    # Create test violation
    print("Creating test violation data...")
    violation_details = {
        "violations": ["Hate Speech", "Harassment"],
        "severity": "high",
        "action": "deleted",
        "justification": "Message contained severe hate speech targeting protected characteristics",
        "notify": True,
    }

    message_content = "This is a test message for email notification verification."

    context = {
        "author": "Test User",
        "channel": "General",
        "timestamp": datetime.now(datetime.UTC).isoformat() if hasattr(datetime, 'UTC') else datetime.utcnow().isoformat(),
        "message_id": "test-message-123",
    }

    # Send notification
    print("\n📧 Sending test email notification...")
    try:
        result = await agent.notify_violation(violation_details, message_content, context)

        print("\n✅ Notification sent!")
        print("\nResults:")
        print(f"  Notification Sent: {result['notification_sent']}")
        print(f"  Channels: {len(result['channels'])}")

        for channel_result in result["channels"]:
            channel_name = channel_result.get("channel", "unknown")
            success = channel_result.get("success", False)
            status = "✓" if success else "✗"

            print(f"\n  {status} {channel_name.upper()}")
            if success:
                if channel_name == "email":
                    print(f"    Recipient: {channel_result.get('recipient')}")
                    print(f"    Subject: {channel_result.get('subject')}")
                    print(f"    Message ID: {channel_result.get('message_id', 'N/A')}")
                    print(f"    Status: {channel_result.get('status', 'sent')}")
            else:
                error = channel_result.get("error", "Unknown error")
                print(f"    Error: {error}")

        # Show composed content
        if "notification_content" in result:
            content = result["notification_content"]
            print("\n📝 Notification Content:")
            print(f"  Subject: {content.get('subject')}")
            print(f"  Urgency: {content.get('urgency')}")
            print(f"  Recommended Actions: {len(content.get('recommended_actions', []))}")

        print("\n✨ Test complete! Check your inbox at:", notification_email)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await agent.close()


if __name__ == "__main__":
    asyncio.run(test_email_notification())
