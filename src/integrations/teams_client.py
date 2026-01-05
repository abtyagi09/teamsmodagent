"""
Microsoft Teams integration using Microsoft Graph API.

Provides functionality to:
- Monitor Teams channels for new messages
- Retrieve message content and metadata
- Delete violating messages
- Subscribe to webhooks for real-time notifications

Uses REST API approach to avoid msgraph-sdk Windows long path issues.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

import requests
from msal import ConfidentialClientApplication


class TeamsClient:
    """
    Client for interacting with Microsoft Teams via Microsoft Graph REST API.
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        team_id: str,
    ):
        """
        Initialize Teams client.

        Args:
            tenant_id: Microsoft Entra ID tenant ID
            client_id: App registration client ID
            client_secret: App registration client secret
            team_id: Teams team ID to monitor
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.team_id = team_id
        self.graph_url = "https://graph.microsoft.com/v1.0"
        self._access_token = None
        self._token_expiry = None

        # Initialize MSAL client
        authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.msal_app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority,
        )

    def _get_access_token(self) -> str:
        """Get or refresh access token."""
        # Check if token is still valid
        if self._access_token and self._token_expiry:
            if datetime.utcnow() < self._token_expiry:
                return self._access_token

        # Acquire new token
        scopes = ["https://graph.microsoft.com/.default"]
        result = self.msal_app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            self._access_token = result["access_token"]
            # Set expiry to 55 minutes (tokens are valid for 60 minutes)
            self._token_expiry = datetime.utcnow() + timedelta(minutes=55)
            return self._access_token
        else:
            raise Exception(f"Failed to acquire token: {result.get('error_description')}")

    def _get_headers(self) -> dict:
        """Get HTTP headers with authentication."""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }


    async def get_channels(self, monitored_channels: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Get list of channels in the team.

        Args:
            monitored_channels: Optional list of channel names to filter

        Returns:
            List of channel information
        """
        try:
            url = f"{self.graph_url}/teams/{self.team_id}/channels"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            data = response.json()
            channels = []

            for channel in data.get("value", []):
                channel_info = {
                    "id": channel.get("id"),
                    "name": channel.get("displayName"),
                    "description": channel.get("description"),
                }

                # Filter if monitored_channels is specified
                if monitored_channels is None or channel.get("displayName") in monitored_channels:
                    channels.append(channel_info)

            return channels

        except Exception as e:
            print(f"Error fetching channels: {e}")
            return []



    async def get_recent_messages(
        self,
        channel_id: str,
        since: datetime | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get recent messages from a specific channel.

        Args:
            channel_id: Channel ID to fetch messages from
            since: Only fetch messages after this timestamp
            limit: Maximum number of messages to fetch

        Returns:
            List of message information
        """
        try:
            url = f"{self.graph_url}/teams/{self.team_id}/channels/{channel_id}/messages"
            params = {"$top": limit}
            
            response = requests.get(url, headers=self._get_headers(), params=params)
            response.raise_for_status()

            data = response.json()
            messages = []

            for msg in data.get("value", []):
                # Parse message timestamp
                created_at_str = msg.get("createdDateTime")
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else None

                # Filter by timestamp if specified
                if since and created_at and created_at < since:
                    continue

                # Extract user information
                from_info = msg.get("from", {})
                user_info = from_info.get("user", {}) if from_info else {}

                # Extract body content
                body = msg.get("body", {})
                content = body.get("content", "")
                content_type = body.get("contentType", "text")

                # Extract attachments
                attachments_data = msg.get("attachments", [])
                attachments = [
                    {
                        "id": att.get("id"),
                        "name": att.get("name"),
                        "content_type": att.get("contentType"),
                    }
                    for att in attachments_data
                ]

                message_info = {
                    "id": msg.get("id"),
                    "content": content,
                    "content_type": content_type,
                    "from_user": {
                        "id": user_info.get("id"),
                        "display_name": user_info.get("displayName", "Unknown"),
                    },
                    "created_at": created_at.isoformat() if created_at else None,
                    "channel_id": channel_id,
                    "has_attachments": bool(attachments),
                    "attachments": attachments,
                }

                messages.append(message_info)

            return messages

        except Exception as e:
            print(f"Error fetching messages from channel {channel_id}: {e}")
            return []



    async def delete_message(self, channel_id: str, message_id: str) -> bool:
        """
        Delete a message from a channel.

        Note: Soft delete requires specific permissions and may not be available
        for all app registrations. This uses the softDelete endpoint.

        Args:
            channel_id: Channel ID containing the message
            message_id: Message ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.graph_url}/teams/{self.team_id}/channels/{channel_id}/messages/{message_id}/softDelete"
            response = requests.post(url, headers=self._get_headers())
            response.raise_for_status()
            return True

        except Exception as e:
            print(f"Error deleting message {message_id}: {e}")
            return False



    async def monitor_channels(
        self,
        monitored_channels: list[str],
        callback: callable,
        polling_interval: int = 60,
    ):
        """
        Continuously monitor channels for new messages.

        Args:
            monitored_channels: List of channel names to monitor
            callback: Async function to call with new messages
            polling_interval: Seconds between polls (default: 60)
        """
        # Get channel IDs for monitored channels
        channels = await self.get_channels(monitored_channels)
        channel_map = {ch["name"]: ch for ch in channels}

        print(f"Monitoring {len(channel_map)} channels: {', '.join(channel_map.keys())}")

        # Track last check time for each channel
        last_check = {ch_id: datetime.utcnow() - timedelta(minutes=5) for ch_id in [ch["id"] for ch in channels]}

        while True:
            try:
                for channel_name, channel_info in channel_map.items():
                    channel_id = channel_info["id"]

                    # Get messages since last check
                    messages = await self.get_recent_messages(
                        channel_id=channel_id,
                        since=last_check[channel_id],
                        limit=50,
                    )

                    # Process new messages
                    for message in messages:
                        # Add channel context
                        message["channel_name"] = channel_name

                        # Call the callback with the message
                        await callback(message)

                    # Update last check time
                    if messages:
                        last_check[channel_id] = datetime.utcnow()

                # Wait before next poll
                await asyncio.sleep(polling_interval)

            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(polling_interval)

    async def close(self):
        """Clean up resources."""
        # No async resources to clean up with REST API approach
        pass



class ContentSafetyIntegration:
    """
    Wrapper for Azure Content Safety service.
    (Already integrated in ModerationAgent, but kept here for reference)
    """

    pass
