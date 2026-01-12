"""
Teams webhook receiver that forwards messages to Service Bus.
This endpoint will be subscribed to Teams channel events.
"""

import json
import os
from datetime import datetime

from azure.identity import DefaultAzureCredential
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from flask import Flask, request, jsonify


app = Flask(__name__)

# Service Bus configuration
SERVICE_BUS_ENDPOINT = os.getenv("SERVICE_BUS_ENDPOINT")
SERVICE_BUS_QUEUE_NAME = os.getenv("SERVICE_BUS_QUEUE_NAME")

# Extract namespace from endpoint
if SERVICE_BUS_ENDPOINT:
    if SERVICE_BUS_ENDPOINT.startswith("sb://"):
        namespace = SERVICE_BUS_ENDPOINT.replace("sb://", "").replace("/", "").strip()
    else:
        namespace = SERVICE_BUS_ENDPOINT.replace("https://", "").replace("/", "").strip()
        if not namespace.endswith(".servicebus.windows.net"):
            namespace = f"{namespace}.servicebus.windows.net"
    
    credential = DefaultAzureCredential()
    service_bus_client = ServiceBusClient(
        fully_qualified_namespace=namespace,
        credential=credential,
    )
    sender = service_bus_client.get_queue_sender(queue_name=SERVICE_BUS_QUEUE_NAME)
else:
    service_bus_client = None
    sender = None


@app.route("/webhook/teams", methods=["POST"])
def teams_webhook():
    """
    Receive Teams webhook notifications and forward to Service Bus.
    
    Expected payload from Teams Graph API subscription:
    {
        "value": [{
            "subscriptionId": "...",
            "changeType": "created",
            "resource": "teams('...')/channels('...')/messages('...')",
            "resourceData": {
                "id": "...",
                "@odata.type": "#microsoft.graph.chatMessage"
            }
        }]
    }
    """
    try:
        if not sender:
            return jsonify({"error": "Service Bus not configured"}), 500
        
        # Handle validation token (initial subscription)
        validation_token = request.args.get("validationToken")
        if validation_token:
            return validation_token, 200
        
        data = request.get_json()
        
        if not data or "value" not in data:
            return jsonify({"error": "Invalid payload"}), 400
        
        # Process each notification
        for notification in data["value"]:
            change_type = notification.get("changeType")
            resource = notification.get("resource")
            
            # Only process new messages
            if change_type == "created" and "/messages/" in resource:
                # Extract IDs from resource path
                # Format: teams('teamId')/channels('channelId')/messages('messageId')
                parts = resource.split("/")
                team_id = parts[0].split("'")[1] if len(parts) > 0 else None
                channel_id = parts[1].split("'")[1] if len(parts) > 1 else None
                message_id = parts[2].split("'")[1] if len(parts) > 2 else None
                
                # Create message for Service Bus
                message_payload = {
                    "team_id": team_id,
                    "channel_id": channel_id,
                    "message_id": message_id,
                    "change_type": change_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    "resource": resource,
                    "subscription_id": notification.get("subscriptionId")
                }
                
                # Send to Service Bus
                message = ServiceBusMessage(json.dumps(message_payload))
                sender.send_messages(message)
                
                print(f"✅ Forwarded message to Service Bus: {message_id}")
        
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
