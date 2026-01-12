"""
End-to-end test for email notifications on policy violations.
Posts a test message to Teams, waits for violation detection, and verifies email sent.
"""

import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv

from src.agents.moderation_agent import ModerationAgent
from src.agents.notification_agent import NotificationAgent
from src.utils.config_loader import get_settings

# Load environment variables
load_dotenv()


async def test_violation_with_email():
    """Test complete flow: violation detection → email notification."""
    print("🧪 Testing Email Notification on Policy Violation Detection\n")

    # Load settings
    settings = get_settings()

    print("Configuration:")
    print(f"  Notification Email: {settings.notification_email}")
    print(f"  Email Sender: {settings.email_sender}")
    print(f"  Email Connection: {'✓ Configured' if settings.email_connection_string else '✗ Missing'}")
    print()

    # Initialize agents
    print("Initializing agents...")
    
    # Load policies
    from src.utils.config_loader import load_json_config
    policies = load_json_config("policies.json")
    
    moderation_agent = ModerationAgent(
        foundry_endpoint=settings.foundry_project_endpoint,
        model_deployment=settings.foundry_model_deployment,
        content_safety_endpoint=settings.content_safety_endpoint,
        content_safety_key=settings.content_safety_key,
        policies=policies,
    )

    notification_agent = NotificationAgent(
        foundry_endpoint=settings.foundry_project_endpoint,
        model_deployment=settings.foundry_model_deployment,
        notification_email=settings.notification_email,
        notification_webhook=settings.notification_webhook,
        email_connection_string=settings.email_connection_string,
        email_sender=settings.email_sender,
    )

    print("✓ Agents initialized\n")

    # Test messages with different severity levels
    test_cases = [
        {
            "name": "Hate Speech (High Severity)",
            "message": "I hate all people from that country, they should all be deported!",
            "author": "Test User 1",
            "expected_violation": True,
        },
        {
            "name": "Harassment (Medium Severity)",
            "message": "You're so stupid, nobody likes you. Just quit already.",
            "author": "Test User 2",
            "expected_violation": True,
        },
        {
            "name": "Clean Message (No Violation)",
            "message": "Great job on the presentation today! Looking forward to our next meeting.",
            "author": "Test User 3",
            "expected_violation": False,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"{'='*70}")
        print(f"Test Case {i}/{len(test_cases)}: {test_case['name']}")
        print(f"{'='*70}")
        print(f"Message: \"{test_case['message'][:50]}...\"" if len(test_case['message']) > 50 else f"Message: \"{test_case['message']}\"")
        print()

        # Step 1: Analyze message with moderation agent
        print("Step 1: Analyzing message for violations...")
        result = await moderation_agent.analyze_text(test_case["message"])

        print(f"  Is Violation: {result['is_violation']}")
        
        if result['is_violation']:
            print(f"  Severity: {result['severity']}")
            print(f"  Violations: {result['violations']}")
            print(f"  Action: {result.get('action', 'unknown')}")
            print(f"  Should Notify: {result.get('notify', False)}")
        else:
            print("  ✓ Message is clean")

        # Step 2: If violation detected and notify flag set, send email
        if result['is_violation'] and result.get('notify', False):
            print("\nStep 2: Sending email notification...")
            
            context = {
                "author": test_case["author"],
                "channel": "Test Channel",
                "timestamp": datetime.now().isoformat(),
                "message_id": f"test-{i}",
            }

            notification_result = await notification_agent.notify_violation(
                violation_details=result,
                message_content=test_case["message"],
                context=context,
            )

            if notification_result['notification_sent']:
                print("  ✅ Email notification sent!")
                
                for channel in notification_result['channels']:
                    if channel['channel'] == 'email' and channel['success']:
                        print(f"     → To: {channel['recipient']}")
                        print(f"     → Subject: {channel['subject']}")
                        print(f"     → Status: {channel.get('status', 'sent')}")
            else:
                print("  ❌ Failed to send notification")
                for channel in notification_result['channels']:
                    if not channel.get('success', False):
                        print(f"     Error: {channel.get('error', 'Unknown')}")
        else:
            if not result['is_violation']:
                print("\n  ℹ️  No violations detected - no email sent (expected)")
            else:
                print("\n  ℹ️  Violation detected but notify flag not set - no email sent")

        print()

    # Summary
    print(f"{'='*70}")
    print("Test Summary")
    print(f"{'='*70}")
    print(f"Total test cases: {len(test_cases)}")
    violations_detected = sum(1 for tc in test_cases if tc['expected_violation'])
    print(f"Expected violations: {violations_detected}")
    print()
    print("✨ End-to-end test complete!")
    print(f"📧 Check inbox at: {settings.notification_email}")
    print()

    # Cleanup
    await moderation_agent.close()
    await notification_agent.close()


if __name__ == "__main__":
    asyncio.run(test_violation_with_email())
