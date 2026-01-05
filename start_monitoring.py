"""
Continuous Monitoring Mode - Production-ready Teams channel monitoring.

This script continuously monitors your Teams channels and analyzes messages in real-time.
"""

import os
import asyncio
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import sys
import re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from integrations.teams_client import TeamsClient
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeTextOptions
from azure.core.credentials import AzureKeyCredential
from utils.config_loader import load_json_config

load_dotenv()

def strip_html(html_content):
    """Remove HTML tags from content."""
    clean = re.sub('<[^<]+?>', '', html_content)
    return clean.strip()

class ModerationMonitor:
    def __init__(self):
        self.teams_client = None
        self.content_safety_client = None
        self.policies = None
        self.channels_config = None
        self.processed_messages = set()
        self.enforce_mode = os.getenv("MODERATION_MODE", "monitor").lower() == "enforce"
        
    async def initialize(self):
        """Initialize all clients and configurations."""
        print("🔧 Initializing Teams Moderation System...")
        
        # Load configurations
        self.channels_config = load_json_config("channels.json")
        self.policies = load_json_config("policies.json")
        
        # Initialize Teams client
        self.teams_client = TeamsClient(
            tenant_id=os.getenv("TEAMS_TENANT_ID"),
            client_id=os.getenv("TEAMS_CLIENT_ID"),
            client_secret=os.getenv("TEAMS_CLIENT_SECRET"),
            team_id=os.getenv("TEAMS_TEAM_ID"),
        )
        
        # Initialize Content Safety client
        self.content_safety_client = ContentSafetyClient(
            endpoint=os.getenv("CONTENT_SAFETY_ENDPOINT"),
            credential=AzureKeyCredential(os.getenv("CONTENT_SAFETY_KEY"))
        )
        
        print("✅ System initialized successfully!")
        
        mode_indicator = "🔨 ENFORCE" if self.enforce_mode else "👁️  MONITOR"
        print(f"📋 Mode: {mode_indicator} ({'Deletions enabled' if self.enforce_mode else 'Logging only'})")
        
        # Count enabled policies
        text_policies = self.policies.get('text_policies', {})
        enabled_count = len([k for k, v in text_policies.items() if v.get('enabled', False)])
        print(f"📊 Policies loaded: {enabled_count}")
        print(f"📢 Monitored channels: {', '.join(self.channels_config.get('monitored_channels', []))}")
        
    async def analyze_message(self, message):
        """Analyze a single message for policy violations."""
        # Extract and clean content
        raw_content = message['content']
        clean_content = strip_html(raw_content)
        
        if not clean_content or len(clean_content.strip()) == 0:
            return None
        
        # Skip if already processed
        msg_id = message['id']
        if msg_id in self.processed_messages:
            return None
        
        self.processed_messages.add(msg_id)
        
        try:
            # Analyze with Azure Content Safety
            request = AnalyzeTextOptions(text=clean_content)
            response = self.content_safety_client.analyze_text(request)
            
            # Check categories
            categories = [
                ("Hate", response.categories_analysis[0]),
                ("Self-Harm", response.categories_analysis[1]),
                ("Sexual", response.categories_analysis[2]),
                ("Violence", response.categories_analysis[3])
            ]
            
            violations = []
            for category, result in categories:
                if result.severity > 0:
                    violations.append({
                        "category": category,
                        "severity": result.severity
                    })
            
            return {
                "message": message,
                "content": clean_content,
                "violations": violations,
                "timestamp": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            print(f"❌ Error analyzing message {msg_id}: {e}")
            return None
    
    async def process_violation(self, analysis):
        """Process a detected violation."""
        message = analysis['message']
        violations = analysis['violations']
        
        timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
        
        print(f"\n{'='*70}")
        print(f"⚠️  VIOLATION DETECTED at {timestamp}")
        print(f"{'='*70}")
        print(f"Channel: {message.get('channel_name', 'Unknown')}")
        print(f"From: {message['from_user']['display_name']}")
        print(f"Content: \"{analysis['content'][:100]}{'...' if len(analysis['content']) > 100 else ''}\"")
        print(f"\nViolations:")
        
        for violation in violations:
            severity_map = {0: "Safe", 2: "Low", 4: "Medium", 6: "High"}
            severity_label = severity_map.get(violation['severity'], f"Level {violation['severity']}")
            print(f"  • {violation['category']}: {severity_label} (severity: {violation['severity']})")
        
        # Take action based on mode
        if self.enforce_mode:
            print(f"\n🔨 ENFORCE MODE: Attempting to delete message...")
            try:
                success = await self.teams_client.delete_message(
                    channel_id=message['channel_id'],
                    message_id=message['id']
                )
                if success:
                    print(f"✅ Message deleted successfully!")
                else:
                    print(f"⚠️  Failed to delete message (may require additional permissions)")
            except Exception as e:
                print(f"❌ Delete failed: {e}")
        else:
            print(f"\n📝 MONITOR MODE: Message flagged for review (not deleted)")
        
        print(f"🔗 Message ID: {message['id']}")
        print(f"{'='*70}\n")
    
    async def monitor_loop(self):
        """Main monitoring loop."""
        print("\n🔍 Starting continuous monitoring...")
        print("💡 Press Ctrl+C to stop\n")
        
        # Get monitored channels
        monitored_channel_names = self.channels_config.get('monitored_channels', [])
        channels = await self.teams_client.get_channels(monitored_channel_names)
        
        if not channels:
            print("❌ No channels found to monitor!")
            return
        
        channel_map = {ch['id']: ch for ch in channels}
        last_check = {ch_id: datetime.now(timezone.utc) - timedelta(minutes=1) for ch_id in channel_map.keys()}
        
        poll_interval = 30  # Check every 30 seconds
        
        while True:
            try:
                for channel_id, channel in channel_map.items():
                    # Get new messages since last check
                    messages = await self.teams_client.get_recent_messages(
                        channel_id=channel_id,
                        since=last_check[channel_id],
                        limit=50
                    )
                    
                    # Filter user messages only
                    user_messages = [msg for msg in messages if msg['from_user']['id'] is not None]
                    
                    for message in user_messages:
                        message['channel_name'] = channel['name']
                        
                        # Analyze message
                        analysis = await self.analyze_message(message)
                        
                        if analysis and analysis['violations']:
                            await self.process_violation(analysis)
                        elif analysis:
                            # Clean message - silent pass
                            timestamp = datetime.now(timezone.utc).strftime('%H:%M:%S')
                            print(f"[{timestamp}] ✅ Clean message in {channel['name']} from {message['from_user']['display_name']}")
                    
                    # Update last check time
                    last_check[channel_id] = datetime.now(timezone.utc)
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(poll_interval)
        
        await self.teams_client.close()

async def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       Teams Content Moderation - Continuous Monitoring      ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    monitor = ModerationMonitor()
    await monitor.initialize()
    await monitor.monitor_loop()
    
    print("\n✅ Monitoring session ended")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
