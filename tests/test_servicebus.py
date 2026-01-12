#!/usr/bin/env python3
"""
Script to send a test message to the Service Bus queue for testing the agent.
"""
import json
import os
from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage

# Configuration
SERVICE_BUS_NAMESPACE = "sb-xcpeyeriwqbc4.servicebus.windows.net"
QUEUE_NAME = "teams-messages"

def send_test_message():
    """Send a test message to the Service Bus queue."""
    
    # Create Service Bus client
    credential = DefaultAzureCredential()
    servicebus_client = ServiceBusClient(
        fully_qualified_namespace=SERVICE_BUS_NAMESPACE,
        credential=credential
    )
    
    # Test message payload
    test_message = {
        "messageId": "test-123",
        "channelId": "general",
        "content": "This is a test message to verify Service Bus processing",
        "timestamp": "2026-01-08T15:40:00Z",
        "user": {
            "displayName": "Test User",
            "email": "test@example.com"
        }
    }
    
    # Send message
    with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        with sender:
            message = ServiceBusMessage(json.dumps(test_message))
            sender.send_messages(message)
            print(f"✅ Test message sent to queue '{QUEUE_NAME}'")
            print(f"Message content: {json.dumps(test_message, indent=2)}")

if __name__ == "__main__":
    send_test_message()