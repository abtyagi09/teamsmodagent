"""
Multi-agent workflow orchestrator for Teams content moderation.

Coordinates the moderation agent, notification agent, and Teams operations
using Microsoft Agent Framework.
"""

from datetime import datetime
from typing import Any

from agent_framework import Executor, WorkflowBuilder, WorkflowContext, handler
from typing_extensions import Never

from ..agents.moderation_agent import ModerationAgent
from ..agents.notification_agent import NotificationAgent
from ..integrations.teams_client import TeamsClient


class MessageProcessingContext:
    """Context object passed between workflow executors."""

    def __init__(self, message: dict[str, Any]):
        self.message = message
        self.moderation_result: dict[str, Any] | None = None
        self.notification_result: dict[str, Any] | None = None
        self.action_taken: str | None = None
        self.timestamp = datetime.utcnow()


class MessageIntakeExecutor(Executor):
    """
    First step: Receives raw message from Teams and prepares it for moderation.
    """

    def __init__(self, id: str = "message_intake"):
        super().__init__(id=id)

    @handler
    async def handle_message(
        self,
        message: dict[str, Any],
        ctx: WorkflowContext[MessageProcessingContext],
    ) -> None:
        """
        Receive and validate incoming message.

        Args:
            message: Raw message from Teams
            ctx: Workflow context to send to next executor
        """
        print(f"📨 Received message from {message.get('from_user', {}).get('display_name', 'Unknown')}")

        # Create processing context
        processing_ctx = MessageProcessingContext(message)

        # Forward to moderation
        await ctx.send_message(processing_ctx)


class ModerationExecutor(Executor):
    """
    Second step: Analyzes message content using the Moderation Agent.
    """

    def __init__(self, moderation_agent: ModerationAgent, id: str = "moderation"):
        self.moderation_agent = moderation_agent
        super().__init__(id=id)

    @handler
    async def handle_moderation(
        self,
        processing_ctx: MessageProcessingContext,
        ctx: WorkflowContext[MessageProcessingContext],
    ) -> None:
        """
        Analyze message for policy violations.

        Args:
            processing_ctx: Message processing context
            ctx: Workflow context
        """
        message = processing_ctx.message
        content = message.get("content", "")

        print(f"🔍 Analyzing content: '{content[:50]}{'...' if len(content) > 50 else ''}'")

        # Prepare context for moderation agent
        moderation_context = {
            "author": message.get("from_user", {}).get("display_name", "Unknown"),
            "channel": message.get("channel_name", "Unknown"),
            "timestamp": message.get("created_at", ""),
            "message_id": message.get("id", ""),
        }

        # Analyze content
        result = await self.moderation_agent.analyze_text(content, moderation_context)

        # Store result
        processing_ctx.moderation_result = result

        print(f"📊 Moderation result: {result.get('action', 'allow')} (confidence: {result.get('confidence', 0):.2f})")

        # Forward to decision executor
        await ctx.send_message(processing_ctx)


class DecisionExecutor(Executor):
    """
    Third step: Decides what action to take based on moderation results.
    Routes to notification and/or deletion.
    """

    def __init__(self, teams_client: TeamsClient, dry_run: bool = False, id: str = "decision"):
        self.teams_client = teams_client
        self.dry_run = dry_run
        super().__init__(id=id)

    @handler
    async def handle_decision(
        self,
        processing_ctx: MessageProcessingContext,
        ctx: WorkflowContext[MessageProcessingContext],
    ) -> None:
        """
        Make decision and take action on message.

        Args:
            processing_ctx: Message processing context
            ctx: Workflow context
        """
        result = processing_ctx.moderation_result
        message = processing_ctx.message

        is_violation = result.get("is_violation", False)
        action = result.get("action", "allow")
        should_notify = result.get("notify", False)

        if not is_violation or action == "allow":
            print("✅ Message allowed - no policy violations detected")
            processing_ctx.action_taken = "allowed"
            # Workflow ends here (no further processing)
            await ctx.yield_output(processing_ctx)
            return

        # Handle violation
        if action == "delete":
            if self.dry_run:
                print(f"🧪 [DRY RUN] Would delete message: {message.get('id')}")
                processing_ctx.action_taken = "would_delete"
            else:
                print(f"🗑️  Deleting violating message: {message.get('id')}")
                success = await self.teams_client.delete_message(
                    channel_id=message.get("channel_id"),
                    message_id=message.get("id"),
                )
                processing_ctx.action_taken = "deleted" if success else "delete_failed"

        elif action == "flag":
            print(f"🚩 Flagging message for review: {message.get('id')}")
            processing_ctx.action_taken = "flagged"

        # If notification is needed, forward to notification executor
        if should_notify:
            await ctx.send_message(processing_ctx)
        else:
            # Workflow completes here
            await ctx.yield_output(processing_ctx)


class NotificationExecutor(Executor):
    """
    Fourth step: Sends notifications if required.
    """

    def __init__(self, notification_agent: NotificationAgent, id: str = "notification"):
        self.notification_agent = notification_agent
        super().__init__(id=id)

    @handler
    async def handle_notification(
        self,
        processing_ctx: MessageProcessingContext,
        ctx: WorkflowContext[Never, MessageProcessingContext],
    ) -> None:
        """
        Send notification about violation.

        Args:
            processing_ctx: Message processing context
            ctx: Workflow context
        """
        message = processing_ctx.message
        result = processing_ctx.moderation_result

        print(f"🔔 Sending notifications for violation")

        # Prepare context for notification
        notification_context = {
            "author": message.get("from_user", {}).get("display_name", "Unknown"),
            "channel": message.get("channel_name", "Unknown"),
            "timestamp": message.get("created_at", ""),
            "message_id": message.get("id", ""),
            "action_taken": processing_ctx.action_taken,
        }

        # Send notification
        notification_result = await self.notification_agent.notify_violation(
            violation_details=result,
            message_content=message.get("content", ""),
            context=notification_context,
        )

        processing_ctx.notification_result = notification_result

        print(f"📧 Notification sent: {notification_result.get('notification_sent', False)}")

        # Yield final workflow output
        await ctx.yield_output(processing_ctx)


class ModerationWorkflow:
    """
    Main orchestrator that builds and runs the multi-agent workflow.
    """

    def __init__(
        self,
        moderation_agent: ModerationAgent,
        notification_agent: NotificationAgent,
        teams_client: TeamsClient,
        dry_run: bool = False,
    ):
        """
        Initialize the workflow.

        Args:
            moderation_agent: Content moderation agent
            notification_agent: Notification agent
            teams_client: Teams API client
            dry_run: If True, don't actually delete messages
        """
        self.moderation_agent = moderation_agent
        self.notification_agent = notification_agent
        self.teams_client = teams_client
        self.dry_run = dry_run

        # Build the workflow
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """
        Build the multi-agent workflow using WorkflowBuilder.

        Flow: Intake -> Moderation -> Decision -> Notification
        """
        # Create executors
        intake = MessageIntakeExecutor()
        moderation = ModerationExecutor(self.moderation_agent)
        decision = DecisionExecutor(self.teams_client, self.dry_run)
        notification = NotificationExecutor(self.notification_agent)

        # Build workflow graph
        workflow = (
            WorkflowBuilder()
            .set_start_executor(intake)
            .add_edge(intake, moderation)
            .add_edge(moderation, decision)
            .add_edge(decision, notification)
            .build()
        )

        return workflow

    async def process_message(self, message: dict[str, Any]) -> MessageProcessingContext:
        """
        Process a single message through the workflow.

        Args:
            message: Message from Teams

        Returns:
            Final processing context with results
        """
        events = await self.workflow.run(message)
        outputs = events.get_outputs()

        if outputs:
            return outputs[0]

        # Fallback if no output
        return MessageProcessingContext(message)

    async def start_monitoring(
        self,
        monitored_channels: list[str],
        polling_interval: int = 60,
    ):
        """
        Start monitoring Teams channels continuously.

        Args:
            monitored_channels: List of channel names to monitor
            polling_interval: Seconds between polls
        """
        print(f"🚀 Starting Teams moderation workflow")
        print(f"📺 Monitoring channels: {', '.join(monitored_channels)}")
        print(f"🔄 Polling interval: {polling_interval} seconds")
        if self.dry_run:
            print(f"🧪 DRY RUN MODE - No messages will be deleted")

        async def message_callback(message: dict[str, Any]):
            """Callback for processing each new message."""
            try:
                result = await self.process_message(message)
                print(f"✅ Processed message {message.get('id')} - Action: {result.action_taken}")
            except Exception as e:
                print(f"❌ Error processing message {message.get('id')}: {e}")

        # Start monitoring
        await self.teams_client.monitor_channels(
            monitored_channels=monitored_channels,
            callback=message_callback,
            polling_interval=polling_interval,
        )
