"""
Notification Agent for sending alerts when policy violations are detected.

Supports multiple notification channels:
- Email notifications
- Microsoft Teams webhooks
- Custom webhook endpoints
"""

import json
from datetime import datetime
from typing import Any

import aiohttp
from agent_framework import ChatAgent, ChatMessage, Role
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity import DefaultAzureCredential
from azure.communication.email import EmailClient


class NotificationAgent:
    """
    Agent responsible for notifying HR/admins about content violations.
    """

    def __init__(
        self,
        foundry_endpoint: str,
        model_deployment: str,
        notification_email: str | None = None,
        notification_webhook: str | None = None,
        email_connection_string: str | None = None,
        email_sender: str | None = None,
    ):
        """
        Initialize the notification agent.

        Args:
            foundry_endpoint: Microsoft Foundry project endpoint
            model_deployment: Model deployment name
            notification_email: Email address for notifications
            notification_webhook: Webhook URL for notifications
            email_connection_string: Azure Communication Services connection string
            email_sender: Sender email address (from ACS Email domain)
        """
        self.notification_email = notification_email
        self.notification_webhook = notification_webhook
        self.email_connection_string = email_connection_string
        self.email_sender = email_sender or "DoNotReply@teams-moderation.com"
        
        # Initialize email client if connection string provided
        self.email_client = None
        if email_connection_string:
            try:
                self.email_client = EmailClient.from_connection_string(email_connection_string)
            except Exception as e:
                print(f"Warning: Failed to initialize email client: {e}")

        # Initialize AI agent for composing notifications
        self.agent_client = AzureAIAgentClient(
            project_endpoint=foundry_endpoint,
            model_deployment_name=model_deployment,
            async_credential=DefaultAzureCredential(),
            agent_name="NotificationAgent",
        )

        self.chat_agent = ChatAgent(
            chat_client=self.agent_client,
            instructions=self._build_instructions(),
        )

    def _build_instructions(self) -> str:
        """Build agent instructions for composing notifications."""
        return """You are a notification specialist for Russell Cellular's HR team.

Your role is to compose clear, professional, and actionable notifications when
policy violations are detected in Microsoft Teams.

For each violation, compose a notification that includes:
1. Clear subject line indicating urgency
2. Summary of the violation (what policy was broken)
3. Excerpt from the offending message (sanitized if needed)
4. Context (who, when, which channel)
5. Action taken (deleted, flagged, etc.)
6. Recommended follow-up actions for HR

Guidelines:
- Be professional and factual
- Don't include the full violating content if it's highly offensive
- Prioritize actionable information
- Use appropriate urgency indicators (🔴 Critical, 🟡 Warning, 🟢 Info)
- Keep emails concise but complete

Respond in JSON format:
{
    "subject": "Subject line",
    "body": "Email body with proper formatting",
    "urgency": "high|medium|low",
    "recommended_actions": ["action1", "action2"]
}
"""

    async def notify_violation(
        self,
        violation_details: dict[str, Any],
        message_content: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send notification about a policy violation.

        Args:
            violation_details: Results from moderation agent
            message_content: The original message content (may be sanitized)
            context: Context information (author, channel, timestamp, etc.)

        Returns:
            Dictionary with notification status
        """
        # Step 1: Use agent to compose the notification
        notification_content = await self._compose_notification(violation_details, message_content, context)

        # Step 2: Send notifications through configured channels
        results = []

        if self.notification_webhook:
            webhook_result = await self._send_webhook_notification(notification_content, violation_details, context)
            results.append(webhook_result)

        if self.notification_email:
            email_result = await self._send_email_notification(notification_content, violation_details, context)
            results.append(email_result)

        return {
            "notification_sent": len(results) > 0,
            "channels": results,
            "composed_by": "agent",
            "notification_content": notification_content,
        }

    async def _compose_notification(
        self,
        violation_details: dict[str, Any],
        message_content: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Use AI agent to compose a professional notification.

        Args:
            violation_details: Moderation results
            message_content: Original message
            context: Context information

        Returns:
            Composed notification
        """
        try:
            # Build prompt with violation details
            author = context.get("author", "Unknown User")
            channel = context.get("channel", "Unknown Channel")
            timestamp = context.get("timestamp", datetime.utcnow().isoformat())
            violations = violation_details.get("violations", [])
            severity = violation_details.get("severity", "medium")
            action = violation_details.get("action", "flagged")
            justification = violation_details.get("justification", "")

            # Sanitize message content if needed
            sanitized_content = self._sanitize_content(message_content, violation_details)

            user_message = f"""Compose a notification for this policy violation:

Violation Details:
- Policies Violated: {', '.join(violations)}
- Severity: {severity}
- Action Taken: {action}
- Justification: {justification}

Context:
- Author: {author}
- Channel: {channel}
- Timestamp: {timestamp}
- Message Excerpt: "{sanitized_content}"

Compose a professional notification in JSON format."""

            messages = [ChatMessage(role=Role.USER, text=user_message)]
            response = await self.chat_agent.run(messages)

            # Parse agent response
            agent_text = response.text
            if "```json" in agent_text:
                agent_text = agent_text.split("```json")[1].split("```")[0]
            elif "```" in agent_text:
                agent_text = agent_text.split("```")[1].split("```")[0]

            return json.loads(agent_text.strip())

        except Exception as e:
            # Fallback notification
            return {
                "subject": f"⚠️ Content Policy Violation Detected - {severity.upper()}",
                "body": f"A policy violation was detected.\n\nViolations: {', '.join(violations)}\nAction: {action}\n\nPlease review the moderation logs for details.",
                "urgency": severity,
                "recommended_actions": ["Review incident", "Contact user if needed"],
                "composition_error": str(e),
            }

    def _sanitize_content(self, content: str, violation_details: dict[str, Any]) -> str:
        """
        Sanitize content for notification to avoid exposing highly offensive material.

        Args:
            content: Original message content
            violation_details: Violation details

        Returns:
            Sanitized content excerpt
        """
        severity = violation_details.get("severity", "low")

        # For high severity violations, heavily redact
        if severity == "high":
            return "[Content redacted due to severe violation]"

        # For medium severity, show excerpt
        if len(content) > 100:
            return content[:100] + "... [truncated]"

        return content

    async def _send_webhook_notification(
        self,
        notification_content: dict[str, Any],
        violation_details: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send notification via webhook (Microsoft Teams or custom endpoint).

        Args:
            notification_content: Composed notification
            violation_details: Violation details
            context: Context information

        Returns:
            Status of webhook notification
        """
        try:
            # Build adaptive card for Teams webhook
            card = self._build_teams_card(notification_content, violation_details, context)

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.notification_webhook,
                    json=card,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    success = response.status == 200

                    return {
                        "channel": "teams_webhook",
                        "success": success,
                        "status_code": response.status,
                        "webhook_url": self.notification_webhook,
                    }

        except Exception as e:
            return {
                "channel": "teams_webhook",
                "success": False,
                "error": str(e),
            }

    def _build_teams_card(
        self,
        notification_content: dict[str, Any],
        violation_details: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build Microsoft Teams Adaptive Card for notification.

        Returns:
            Adaptive Card JSON
        """
        urgency = notification_content.get("urgency", "medium")
        urgency_color = {"high": "attention", "medium": "warning", "low": "good"}.get(urgency, "default")

        urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(urgency, "ℹ️")

        return {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"{urgency_emoji} {notification_content.get('subject', 'Policy Violation Detected')}",
                                "weight": "bolder",
                                "size": "large",
                                "wrap": True,
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {"title": "Severity:", "value": urgency.upper()},
                                    {
                                        "title": "Violations:",
                                        "value": ", ".join(violation_details.get("violations", [])),
                                    },
                                    {"title": "Author:", "value": context.get("author", "Unknown")},
                                    {"title": "Channel:", "value": context.get("channel", "Unknown")},
                                    {"title": "Action Taken:", "value": violation_details.get("action", "flagged")},
                                ],
                            },
                            {
                                "type": "TextBlock",
                                "text": notification_content.get("body", ""),
                                "wrap": True,
                                "separator": True,
                            },
                        ],
                        "msteams": {"width": "Full"},
                    },
                }
            ],
        }

    async def _send_email_notification(
        self,
        notification_content: dict[str, Any],
        violation_details: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Send email notification using Azure Communication Services.

        Args:
            notification_content: Composed notification
            violation_details: Violation details
            context: Context information

        Returns:
            Status of email notification
        """
        if not self.email_client:
            return {
                "channel": "email",
                "success": False,
                "error": "Email client not configured. Set EMAIL_CONNECTION_STRING in environment.",
            }

        try:
            subject = notification_content.get("subject", "Policy Violation Detected")
            body = self._format_email_body(notification_content, violation_details, context)
            urgency = notification_content.get("urgency", "medium")
            
            # Build email message
            message = {
                "senderAddress": self.email_sender,
                "recipients": {
                    "to": [{"address": self.notification_email}],
                },
                "content": {
                    "subject": subject,
                    "html": body,
                },
                "importance": "high" if urgency == "high" else "normal",
            }

            # Send email
            poller = self.email_client.begin_send(message)
            result = poller.result()

            return {
                "channel": "email",
                "success": True,
                "recipient": self.notification_email,
                "subject": subject,
                "message_id": result.message_id if hasattr(result, "message_id") else None,
                "status": result.status if hasattr(result, "status") else "sent",
            }

        except Exception as e:
            return {
                "channel": "email",
                "success": False,
                "error": str(e),
                "recipient": self.notification_email,
            }

    def _format_email_body(
        self,
        notification_content: dict[str, Any],
        violation_details: dict[str, Any],
        context: dict[str, Any],
    ) -> str:
        """
        Format email body as HTML.

        Args:
            notification_content: Composed notification
            violation_details: Violation details
            context: Context information

        Returns:
            HTML formatted email body
        """
        urgency = notification_content.get("urgency", "medium")
        urgency_color = {"high": "#dc3545", "medium": "#ffc107", "low": "#28a745"}.get(urgency, "#6c757d")
        urgency_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(urgency, "ℹ️")
        
        violations = ", ".join(violation_details.get("violations", []))
        author = context.get("author", "Unknown")
        channel = context.get("channel", "Unknown")
        timestamp = context.get("timestamp", datetime.utcnow().isoformat())
        action = violation_details.get("action", "flagged")
        body_text = notification_content.get("body", "")
        recommended_actions = notification_content.get("recommended_actions", [])
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: {urgency_color}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
        .content {{ background-color: #f8f9fa; padding: 20px; border: 1px solid #dee2e6; border-top: none; }}
        .info-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        .info-table td {{ padding: 8px; border-bottom: 1px solid #dee2e6; }}
        .info-table td:first-child {{ font-weight: bold; width: 150px; }}
        .actions {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #6c757d; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{urgency_emoji} Teams Moderation Alert</h2>
            <p style="margin: 0;">{notification_content.get('subject', 'Policy Violation Detected')}</p>
        </div>
        <div class="content">
            <p>{body_text}</p>
            
            <table class="info-table">
                <tr>
                    <td>Severity:</td>
                    <td><strong style="color: {urgency_color};">{urgency.upper()}</strong></td>
                </tr>
                <tr>
                    <td>Policies Violated:</td>
                    <td>{violations}</td>
                </tr>
                <tr>
                    <td>Author:</td>
                    <td>{author}</td>
                </tr>
                <tr>
                    <td>Channel:</td>
                    <td>{channel}</td>
                </tr>
                <tr>
                    <td>Timestamp:</td>
                    <td>{timestamp}</td>
                </tr>
                <tr>
                    <td>Action Taken:</td>
                    <td><strong>{action}</strong></td>
                </tr>
            </table>
            
            {f'''<div class="actions">
                <h4 style="margin-top: 0;">📋 Recommended Actions:</h4>
                <ul>{''.join(f'<li>{action}</li>' for action in recommended_actions)}</ul>
            </div>''' if recommended_actions else ''}
            
            <p style="margin-top: 20px;"><em>This is an automated notification from the Teams Moderation System.</em></p>
        </div>
        <div class="footer">
            <p>Teams Moderation System | Powered by Azure AI</p>
        </div>
    </div>
</body>
</html>"""
        return html

    async def close(self):
        """Clean up resources."""
        if hasattr(self.chat_agent, "close"):
            await self.chat_agent.close()
