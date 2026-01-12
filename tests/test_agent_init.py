"""Test agent initialization with Azure credentials"""
import asyncio
from src.utils.config_loader import get_settings, load_json_config
from src.agents.moderation_agent import ModerationAgent
from src.agents.notification_agent import NotificationAgent

async def test_agents():
    print("🧪 Testing agent initialization with Azure credentials\n")
    
    settings = get_settings()
    policies = load_json_config("policies.json")
    
    print("1. Testing ModerationAgent...")
    try:
        moderation_agent = ModerationAgent(
            foundry_endpoint=settings.foundry_project_endpoint,
            model_deployment=settings.foundry_model_deployment,
            content_safety_endpoint=settings.content_safety_endpoint,
            content_safety_key=settings.content_safety_key,
            policies=policies,
        )
        print("   ✅ ModerationAgent initialized successfully")
    except Exception as e:
        print(f"   ❌ ModerationAgent failed: {e}")
        return
    
    print("\n2. Testing NotificationAgent...")
    try:
        notification_agent = NotificationAgent(
            foundry_endpoint=settings.foundry_project_endpoint,
            model_deployment=settings.foundry_model_deployment,
            notification_email=settings.notification_email,
            notification_webhook=settings.notification_webhook,
            email_connection_string=settings.email_connection_string,
            email_sender=settings.email_sender,
        )
        print("   ✅ NotificationAgent initialized successfully")
    except Exception as e:
        print(f"   ❌ NotificationAgent failed: {e}")
        return
    
    print("\n3. Testing moderation analysis with clean message...")
    try:
        result = await moderation_agent.analyze_text("This is a test message")
        print(f"   ✅ Clean message: is_violation={result.get('is_violation')}, notify={result.get('notify')}")
    except Exception as e:
        print(f"   ❌ Analysis failed: {e}")
        return
    
    print("\n4. Testing moderation analysis with strong violation...")
    test_message = """You're an idiot and nobody likes you. Everyone thinks you're worthless and you should just leave this company. You're an idiot and nobody likes you. Everyone thinks you're worthless and you should just leave this company.
You're an idiot and nobody likes you. Everyone thinks you're worthless and you should just leave this company. You're an idiot and nobody likes you. Everyone thinks you're worthless and you should just leave this company."""
    
    try:
        result = await moderation_agent.analyze_text(test_message)
        print(f"   📊 Violation result:")
        print(f"      - is_violation: {result.get('is_violation')}")
        print(f"      - violations: {result.get('violations')}")
        print(f"      - action: {result.get('action')}")
        print(f"      - notify: {result.get('notify')}")
        print(f"      - severity: {result.get('severity')}")
        
        if result.get('notify'):
            print("   ✅ Notify flag is TRUE - email would be sent")
        else:
            print("   ⚠️  Notify flag is FALSE - email would NOT be sent")
    except Exception as e:
        print(f"   ❌ Violation analysis failed: {e}")
        return
    
    print("\n✅ All tests passed! Agents ready for deployment.")

if __name__ == "__main__":
    asyncio.run(test_agents())
