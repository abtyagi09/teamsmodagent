"""
Service Bus-based entry point for Teams content moderation system.

Uses Service Bus queue to receive Teams message events instead of polling.
"""

import argparse
import asyncio
import os

from .agents.moderation_agent import ModerationAgent
from .agents.notification_agent import NotificationAgent
from .integrations.service_bus_consumer import ServiceBusConsumer
from .integrations.teams_client import TeamsClient
from .orchestrator.workflow import ModerationWorkflow
from .utils.config_loader import get_settings, load_json_config
from .utils.logging_config import get_logger, setup_logging


async def main():
    """Main application entry point with Service Bus integration."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Teams Content Moderation System (Service Bus)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (don't actually delete messages)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Override log level from config",
    )
    parser.add_argument(
        "--config-refresh-interval",
        type=int,
        default=300,
        help="Seconds between configuration refreshes from App Configuration (default: 300)",
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=10,
        help="Maximum messages to process per batch (default: 10)",
    )
    parser.add_argument(
        "--wait-time",
        type=float,
        default=5.0,
        help="Wait time for messages in seconds (default: 5.0)",
    )

    args = parser.parse_args()

    # Load configuration
    settings = get_settings()
    policies_config = load_json_config("policies.json")

    # Setup logging
    log_level = args.log_level or settings.log_level
    setup_logging(log_level=log_level, log_file="logs/moderation.log")
    logger = get_logger(__name__)

    logger.info(
        "Starting Teams moderation system (Service Bus mode)",
        mode=settings.moderation_mode,
        dry_run=args.dry_run,
    )

    # Validate Service Bus configuration
    service_bus_endpoint = os.getenv("SERVICE_BUS_ENDPOINT")
    service_bus_queue = os.getenv("SERVICE_BUS_QUEUE_NAME")
    
    if not service_bus_endpoint or not service_bus_queue:
        logger.error("SERVICE_BUS_ENDPOINT and SERVICE_BUS_QUEUE_NAME must be set")
        return

    try:
        # Initialize agents
        logger.info("Initializing moderation agent")
        moderation_agent = ModerationAgent(
            foundry_endpoint=settings.foundry_project_endpoint,
            model_deployment=settings.foundry_model_deployment,
            content_safety_endpoint=settings.content_safety_endpoint,
            content_safety_key=settings.content_safety_key,
            policies=policies_config,
        )

        logger.info("Initializing notification agent")
        notification_agent = NotificationAgent(
            foundry_endpoint=settings.foundry_project_endpoint,
            model_deployment=settings.foundry_model_deployment,
            notification_email=settings.notification_email,
            email_connection_string=settings.email_connection_string,
            email_sender=settings.email_sender,
        )

        logger.info("Initializing Teams client")
        teams_client = TeamsClient(
            tenant_id=settings.teams_tenant_id,
            client_id=settings.teams_client_id,
            client_secret=settings.teams_client_secret,
            team_id=settings.teams_team_id,
        )

        # Build workflow
        logger.info("Building moderation workflow")
        workflow = ModerationWorkflow(
            moderation_agent=moderation_agent,
            notification_agent=notification_agent,
            teams_client=teams_client,
            dry_run=args.dry_run or settings.moderation_mode == "monitor",
            config_refresh_interval=args.config_refresh_interval,
        )

        # Initialize Service Bus consumer
        logger.info("Connecting to Service Bus", endpoint=service_bus_endpoint, queue=service_bus_queue)
        consumer = ServiceBusConsumer(
            endpoint=service_bus_endpoint,
            queue_name=service_bus_queue,
        )
        consumer.connect()

        logger.info("Starting message processing from Service Bus")
        logger.info("Waiting for messages...")
        
        # Continuous message processing
        while True:
            try:
                # Receive messages from queue
                messages = consumer.receive_messages(
                    max_messages=args.max_messages,
                    max_wait_time=args.wait_time,
                )
                
                for message_data in messages:
                    team_id = message_data.get("team_id")
                    channel_id = message_data.get("channel_id")
                    message_id = message_data.get("message_id")
                    
                    logger.info(
                        "Processing message from queue",
                        team_id=team_id,
                        channel_id=channel_id,
                        message_id=message_id,
                    )
                    
                    # Fetch the actual message content from Teams
                    message_content = await teams_client.get_message(
                        team_id=team_id,
                        channel_id=channel_id,
                        message_id=message_id,
                    )
                    
                    if message_content:
                        # Process the message through workflow
                        await workflow.process_message(
                            message=message_content,
                            channel_id=channel_id,
                        )
                    else:
                        logger.warning("Could not fetch message content", message_id=message_id)
                
                # Small sleep to avoid tight loop
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                logger.info("Shutting down gracefully...")
                break
            except Exception as e:
                logger.error("Error processing messages", error=str(e), exc_info=True)
                await asyncio.sleep(5)  # Wait before retrying

    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        raise

    finally:
        # Cleanup
        logger.info("Cleaning up resources")
        if "consumer" in locals():
            consumer.close()
        if "moderation_agent" in locals():
            await moderation_agent.close()
        if "notification_agent" in locals():
            await notification_agent.close()
        if "teams_client" in locals():
            await teams_client.close()


if __name__ == "__main__":
    asyncio.run(main())
