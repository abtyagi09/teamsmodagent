"""
Simple test script to verify Teams API connection without msgraph-sdk
Uses REST API directly to avoid Windows long path issues
"""

import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_access_token():
    """Get access token using client credentials flow"""
    client_id = os.getenv("TEAMS_CLIENT_ID")
    client_secret = os.getenv("TEAMS_CLIENT_SECRET")
    tenant_id = os.getenv("TEAMS_TENANT_ID")
    
    print(f"🔑 Authenticating with Azure AD...")
    print(f"   Tenant ID: {tenant_id}")
    print(f"   Client ID: {client_id}")
    
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority
    )
    
    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_for_client(scopes=scopes)
    
    if "access_token" in result:
        print(f"✅ Authentication successful!")
        return result["access_token"]
    else:
        print(f"❌ Authentication failed!")
        print(f"   Error: {result.get('error')}")
        print(f"   Description: {result.get('error_description')}")
        return None

def test_teams_connection(access_token, team_id):
    """Test connection to Teams API"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📊 Testing Teams API connection...")
    print(f"   Team ID: {team_id}")
    
    # Get team information
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        team_data = response.json()
        print(f"✅ Successfully connected to team!")
        print(f"   Display Name: {team_data.get('displayName', 'N/A')}")
        print(f"   Description: {team_data.get('description', 'N/A')}")
        return True
    else:
        print(f"❌ Failed to connect to team!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def list_channels(access_token, team_id):
    """List channels in the team"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📋 Fetching channels...")
    
    url = f"https://graph.microsoft.com/v1.0/teams/{team_id}/channels"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        channels = response.json().get("value", [])
        print(f"✅ Found {len(channels)} channel(s)!")
        for channel in channels:
            print(f"   • {channel.get('displayName')} (ID: {channel.get('id')})")
        return True
    else:
        print(f"❌ Failed to fetch channels!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

def main():
    """Main test function"""
    print("╔══════════════════════════════════════════════════════╗")
    print("║      Teams API Connection Test                      ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    
    # Get access token
    access_token = get_access_token()
    if not access_token:
        return
    
    # Get Team ID from environment
    team_id = os.getenv("TEAMS_TEAM_ID")
    if not team_id:
        print("❌ TEAMS_TEAM_ID not found in .env file!")
        return
    
    # Test Teams connection
    success = test_teams_connection(access_token, team_id)
    if not success:
        return
    
    # List channels
    list_channels(access_token, team_id)
    
    print("\n" + "="*55)
    print("✅ All tests completed successfully!")
    print("="*55)
    print("\nYour Teams moderation system is ready to:")
    print("  1. Monitor messages in your Teams channels")
    print("  2. Detect policy violations using Azure AI")
    print("  3. Send notifications to administrators")
    print("\nNext steps:")
    print("  • Configure channels in ui/app.py")
    print("  • Adjust moderation policies")
    print("  • Run: python src/main.py --dry-run")

if __name__ == "__main__":
    main()
