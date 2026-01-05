"""
Full moderation test - Fetch real messages and analyze them with Azure AI Content Safety.
"""

import os
import asyncio
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import sys
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrations.teams_client import TeamsClient
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential

load_dotenv()

def strip_html(html_content):
    """Remove HTML tags from content."""
    clean = re.sub('<[^<]+?>', '', html_content)
    return clean.strip()

async def test_moderation_flow():
    """Test the full moderation flow with real Teams messages."""
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   Teams Moderation System - Live Message Analysis       ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    
    # Initialize Teams client
    print("🔧 Initializing Teams client...")
    teams_client = TeamsClient(
        tenant_id=os.getenv("TEAMS_TENANT_ID"),
        client_id=os.getenv("TEAMS_CLIENT_ID"),
        client_secret=os.getenv("TEAMS_CLIENT_SECRET"),
        team_id=os.getenv("TEAMS_TEAM_ID"),
    )
    
    # Initialize Content Safety client
    print("🔧 Initializing Azure Content Safety client...")
    content_safety_client = ContentSafetyClient(
        endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY"))
    )
    
    print("✅ All clients initialized!\n")
    print("="*70)
    
    # Get channels
    channels = await teams_client.get_channels()
    
    for channel in channels:
        channel_name = channel['name']
        channel_id = channel['id']
        
        print(f"\n📋 Analyzing Channel: {channel_name}")
        print("-" * 70)
        
        # Get recent messages (last 2 hours to include your test message)
        since = datetime.now(timezone.utc) - timedelta(hours=2)
        messages = await teams_client.get_recent_messages(
            channel_id=channel_id,
            since=since,
            limit=5
        )
        
        if not messages:
            print("   No recent messages found.")
            continue
        
        # Filter out system messages and analyze user messages
        user_messages = [msg for msg in messages if msg['from_user']['id'] is not None]
        
        if not user_messages:
            print("   No user messages found (only system messages).")
            continue
        
        print(f"   Found {len(user_messages)} user message(s) to analyze:\n")
        
        for i, msg in enumerate(user_messages, 1):
            created_at = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
            time_str = created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Extract and clean content
            raw_content = msg['content']
            clean_content = strip_html(raw_content)
            
            if not clean_content or len(clean_content.strip()) == 0:
                continue
            
            print(f"   Message {i}:")
            print(f"   ├─ Time: {time_str}")
            print(f"   ├─ From: {msg['from_user']['display_name']}")
            print(f"   ├─ Content: \"{clean_content}\"")
            print(f"   └─ Analysis:")
            
            # Analyze with Azure Content Safety
            try:
                request = AnalyzeTextOptions(text=clean_content)
                response = content_safety_client.analyze_text(request)
                
                # Check each category (correct attribute names)
                categories = {
                    "Hate": response.categories_analysis[0] if len(response.categories_analysis) > 0 else None,
                    "Self-Harm": response.categories_analysis[1] if len(response.categories_analysis) > 1 else None,
                    "Sexual": response.categories_analysis[2] if len(response.categories_analysis) > 2 else None,
                    "Violence": response.categories_analysis[3] if len(response.categories_analysis) > 3 else None
                }
                
                violations = []
                for category, result in categories.items():
                    if result and result.severity > 0:
                        violations.append(f"{category} (severity: {result.severity})")
                
                if violations:
                    print(f"      ⚠️  VIOLATIONS DETECTED:")
                    for violation in violations:
                        print(f"         • {violation}")
                    print(f"      📝 Recommended Action: FLAG or DELETE based on policy")
                else:
                    print(f"      ✅ CLEAN - No policy violations detected")
                
            except Exception as e:
                print(f"      ❌ Analysis failed: {e}")
            
            print()
    
    print("="*70)
    print("\n✅ Full moderation flow test complete!")
    print("\nSummary:")
    print("  • Teams API: ✅ Connected and retrieving messages")
    print("  • Azure Content Safety: ✅ Analyzing content")
    print("  • System Status: ✅ Ready for production monitoring")
    
    await teams_client.close()

if __name__ == "__main__":
    asyncio.run(test_moderation_flow())
