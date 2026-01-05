"""
Microsoft Teams integration using Microsoft Graph API.

Provides functionality to:
- Monitor Teams channels for new messages
- Retrieve message content and metadata
- Delete violating messages
- Subscribe to webhooks for real-time notifications
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.teams.item.channels.item.messages.messages_request_builder import MessagesRequestBuilder


class TeamsClient:
    """
    Client for interacting with Microsoft Teams via Microsoft Graph API.
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
        self.team_id = team_id

        # Initialize credentials
        self.credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        )

        # Initialize Graph client
        self.graph_client = GraphServiceClient(
            credentials=self.credential,
            scopes=["https://graph.microsoft.com/.default"],
        )

    async def get_channels(self, monitored_channels: list[str] | None = None) -> list[dict[str, Any]]:
        """
        Get list of channels in the team.

        Args:
            monitored_channels: Optional list of channel names to filter

        Returns:
            List of channel information
        """
        try:
            channels_response = await self.graph_client.teams.by_team_id(self.team_id).channels.get()

            if not channels_response or not channels_response.value:
                return []

            channels = []
            for channel in channels_response.value:
                channel_info = {
                    "id": channel.id,
                    "name": channel.display_name,
                    "description": channel.description,
                }

                # Filter if monitored_channels is specified
                if monitored_channels is None or channel.display_name in monitored_channels:
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
            # Build request with top parameter for pagination
            request_config = MessagesRequestBuilder.MessagesRequestBuilderGetRequestConfiguration(
                query_parameters=MessagesRequestBuilder.MessagesRequestBuilderGetQueryParameters(
                    top=limit,
                )
            )

            messages_response = await (
                self.graph_client.teams.by_team_id(self.team_id)
                .channels.by_channel_id(channel_id)
                .messages.get(request_configuration=request_config)
            )

            if not messages_response or not messages_response.value:
                return []

            messages = []
            for msg in messages_response.value:
                # Parse message timestamp
                created_at = msg.created_date_time

                # Filter by timestamp if specified
                if since and created_at and created_at < since:
                    continue

                message_info = {
                    "id": msg.id,
                    "content": msg.body.content if msg.body else "",
                    "content_type": msg.body.content_type.value if msg.body and msg.body.content_type else "text",
                    "from_user": {
                        "id": msg.from_property.user.id if msg.from_property and msg.from_property.user else None,
                        "display_name": (
                            msg.from_property.user.display_name
                            if msg.from_property and msg.from_property.user
                            else "Unknown"
                        ),
                    },
                    "created_at": created_at.isoformat() if created_at else None,
                    "channel_id": channel_id,
                    "has_attachments": bool(msg.attachments and len(msg.attachments) > 0),
                    "attachments": (
                        [
                            {
                                "id": att.id,
                                "name": att.name,
                                "content_type": att.content_type,
                            }
                            for att in msg.attachments
                        ]
                        if msg.attachments
                        else []
                    ),
                }

                messages.append(message_info)

            return messages

        except Exception as e:
            print(f"Error fetching messages from channel {channel_id}: {e}")
            return []

    async def delete_message(self, channel_id: str, message_id: str) -> bool:
        """
        Delete a message from a channel.

        Args:
            channel_id: Channel ID containing the message
            message_id: Message ID to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            await (
                self.graph_client.teams.by_team_id(self.team_id)
                .channels.by_channel_id(channel_id)
                .messages.by_chat_message_id(message_id)
                .soft_delete()
            )

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
        if self.credential:
            await self.credential.close()


class ContentSafetyIntegration:
    """
    Wrapper for Azure Content Safety service.
    (Already integrated in ModerationAgent, but kept here for reference)
    """

    pass
