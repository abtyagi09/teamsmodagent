"""
Test script to fetch and display recent messages from Teams channels.
"""

import os
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrations.teams_client import TeamsClient

load_dotenv()

async def test_recent_messages():
    """Fetch and display recent messages from all channels."""
    print("╔══════════════════════════════════════════════════════╗")
    print("║      Teams Live Messages Test                       ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    
    # Initialize Teams client
    client = TeamsClient(
        tenant_id=os.getenv("TEAMS_TENANT_ID"),
        client_id=os.getenv("TEAMS_CLIENT_ID"),
        client_secret=os.getenv("TEAMS_CLIENT_SECRET"),
        team_id=os.getenv("TEAMS_TEAM_ID"),
    )
    
    print("🔍 Fetching channels...\n")
    
    # Get all channels
    channels = await client.get_channels()
    
    if not channels:
        print("❌ No channels found!")
        return
    
    print(f"✅ Found {len(channels)} channel(s)\n")
    print("="*70)
    
    # Fetch messages from each channel
    for channel in channels:
        channel_name = channel['name']
        channel_id = channel['id']
        
        print(f"\n📋 Channel: {channel_name}")
        print("-" * 70)
        
        # Get messages from last 24 hours (timezone-aware)
        from datetime import timezone
        since = datetime.now(timezone.utc) - timedelta(hours=24)
        messages = await client.get_recent_messages(
            channel_id=channel_id,
            since=since,
            limit=10
        )
        
        if not messages:
            print("   No recent messages in last 24 hours")
            continue
        
        print(f"   Found {len(messages)} message(s):\n")
        
        for i, msg in enumerate(messages, 1):
            created_at = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00')) if msg['created_at'] else None
            time_str = created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if created_at else 'Unknown'
            
            # Extract text content (strip HTML tags for display)
            content = msg['content']
            if '<div>' in content:
                # Simple HTML stripping
                import re
                content = re.sub('<[^<]+?>', '', content)
            
            # Truncate long messages
            if len(content) > 200:
                content = content[:200] + "..."
            
            print(f"   {i}. [{time_str}]")
            print(f"      From: {msg['from_user']['display_name']}")
            print(f"      Content: {content.strip()}")
            
            if msg['has_attachments']:
                print(f"      Attachments: {len(msg['attachments'])} file(s)")
            print()
    
    print("="*70)
    print("\n✅ Test complete!")
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_recent_messages())
