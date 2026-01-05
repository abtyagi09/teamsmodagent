"""
Main entry point for Teams content moderation system.

Initializes all components and starts the monitoring workflow.
"""

import argparse
import asyncio

from .agents.moderation_agent import ModerationAgent
from .agents.notification_agent import NotificationAgent
from .integrations.teams_client import TeamsClient
from .orchestrator.workflow import ModerationWorkflow
from .utils.config_loader import get_settings, load_json_config
from .utils.logging_config import get_logger, setup_logging


async def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Teams Content Moderation System")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (don't actually delete messages)",
    )
    parser.add_argument(
        "--channel",
        type=str,
        help="Monitor specific channel only (overrides config)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Override log level from config",
    )

    args = parser.parse_args()

    # Load configuration
    settings = get_settings()
    channels_config = load_json_config("channels.json")
    policies_config = load_json_config("policies.json")

    # Setup logging
    log_level = args.log_level or settings.log_level
    setup_logging(log_level=log_level, log_file="logs/moderation.log")
    logger = get_logger(__name__)

    logger.info(
        "Starting Teams moderation system",
        mode=settings.moderation_mode,
        dry_run=args.dry_run,
    )

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
            notification_webhook=settings.notification_webhook,
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
        )

        # Determine which channels to monitor
        if args.channel:
            monitored_channels = [args.channel]
            logger.info("Monitoring single channel", channel=args.channel)
        else:
            monitored_channels = channels_config.get("monitored_channels", [])
            logger.info("Monitoring configured channels", channels=monitored_channels)

        # Start monitoring
        logger.info("Starting channel monitoring")
        await workflow.start_monitoring(
            monitored_channels=monitored_channels,
            polling_interval=settings.polling_interval,
        )

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")

    except Exception as e:
        logger.error("Fatal error", error=str(e), exc_info=True)
        raise

    finally:
        # Cleanup
        logger.info("Cleaning up resources")
        if "moderation_agent" in locals():
            await moderation_agent.close()
        if "notification_agent" in locals():
            await notification_agent.close()
        if "teams_client" in locals():
            await teams_client.close()


if __name__ == "__main__":
    asyncio.run(main())
