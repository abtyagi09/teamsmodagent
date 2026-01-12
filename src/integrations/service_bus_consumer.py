"""
Service Bus consumer for processing Teams messages from queue.
"""

import json
import os
from typing import Any

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusReceiver


class ServiceBusConsumer:
    """Consumer for Teams messages from Service Bus queue."""

    def __init__(self, endpoint: str, queue_name: str):
        """
        Initialize Service Bus consumer.

        Args:
            endpoint: Service Bus namespace endpoint
            queue_name: Name of the queue to consume from
        """
        self.endpoint = endpoint
        self.queue_name = queue_name
        self.credential = DefaultAzureCredential()
        
        # Extract namespace from endpoint (e.g., "https://namespace.servicebus.windows.net:443/")
        if endpoint.startswith("sb://"):
            self.namespace = endpoint.replace("sb://", "").replace("/", "").strip()
        else:
            # Handle https endpoint format with possible port
            self.namespace = endpoint.replace("https://", "").replace("/", "").strip()
            # Remove port if present (e.g., ":443")
            if ":" in self.namespace:
                self.namespace = self.namespace.split(":")[0]
            if not self.namespace.endswith(".servicebus.windows.net"):
                self.namespace = f"{self.namespace}.servicebus.windows.net"
        
        self.client: ServiceBusClient | None = None
        self.receiver: ServiceBusReceiver | None = None

    def connect(self) -> None:
        """Connect to Service Bus."""
        self.client = ServiceBusClient(
            fully_qualified_namespace=self.namespace,
            credential=self.credential,
        )
        self.receiver = self.client.get_queue_receiver(queue_name=self.queue_name)
        print(f"✅ Connected to Service Bus queue: {self.queue_name}")

    def receive_messages(self, max_messages: int = 10, max_wait_time: float = 5.0):
        """
        Receive and process messages from the queue.

        Args:
            max_messages: Maximum number of messages to receive in one batch
            max_wait_time: Maximum time to wait for messages (seconds)

        Yields:
            Parsed message content
        """
        if not self.receiver:
            raise RuntimeError("Not connected. Call connect() first.")

        received_msgs = self.receiver.receive_messages(
            max_message_count=max_messages, max_wait_time=max_wait_time
        )

        for msg in received_msgs:
            try:
                # Parse message body
                message_data = json.loads(str(msg))
                
                yield message_data

                # Complete the message (remove from queue)
                self.receiver.complete_message(msg)
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                # Dead letter the message
                self.receiver.dead_letter_message(msg, reason="ProcessingError", error_description=str(e))

    def close(self) -> None:
        """Close Service Bus connections."""
        if self.receiver:
            self.receiver.close()
        if self.client:
            self.client.close()
        print("✅ Disconnected from Service Bus")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
