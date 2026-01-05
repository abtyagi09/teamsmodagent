"""Test script to verify notification flow in Docker container"""
import asyncio
import sys
from src.utils.config_loader import get_settings, load_json_config
from src.agents.moderation_agent import ModerationAgent
from src.agents.notification_agent import NotificationAgent

async def test():
    print("🧪 Testing notification flow in Docker container\n")
    
    settings = get_settings()
    policies = load_json_config("policies.json")
    
    print(f"✓ Email configured: {bool(settings.email_connection_string)}")
    print(f"✓ Policies loaded: {len(policies.get('text_policies', {}))}")
    print()
    
    # Create agents
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
    
    # Test violation message
    test_message = "You're an idiot and nobody likes you"
    print(f"Testing message: {test_message}\n")
    
    result = await moderation_agent.analyze_text(test_message)
    
    print(f"📊 Analysis Result:")
    print(f"   Is Violation: {result.get('is_violation')}")
    print(f"   Violations: {result.get('violations')}")
    print(f"   Action: {result.get('action')}")
    print(f"   Notify: {result.get('notify')}")
    print()
    
    if result.get('notify'):
        print("✅ Notify flag is TRUE - sending email...")
        email_result = await notification_agent.notify_violation(
            violation_type="test",
            message="Test message",
            severity="high",
            channel="Test Channel",
            author="Test User",
            details=result
        )
        print(f"   Email sent: {email_result}")
    else:
        print("❌ Notify flag is FALSE - no email will be sent")
        print(f"   This is the problem we're debugging!")

if __name__ == "__main__":
    asyncio.run(test())
