"""
Test suite for orchestration workflow.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.moderation_agent import ModerationAgent
from src.agents.notification_agent import NotificationAgent
from src.integrations.teams_client import TeamsClient
from src.orchestrator.workflow import ModerationWorkflow, MessageProcessingContext


@pytest.fixture
def mock_moderation_agent():
    """Mock moderation agent."""
    agent = MagicMock(spec=ModerationAgent)
    agent.analyze_text = AsyncMock(
        return_value={
            "is_violation": False,
            "violations": [],
            "severity": "low",
            "confidence": 0.1,
            "action": "allow",
            "notify": False,
        }
    )
    return agent


@pytest.fixture
def mock_notification_agent():
    """Mock notification agent."""
    agent = MagicMock(spec=NotificationAgent)
    agent.notify_violation = AsyncMock(
        return_value={
            "notification_sent": True,
            "channels": [],
        }
    )
    return agent


@pytest.fixture
def mock_teams_client():
    """Mock Teams client."""
    client = MagicMock(spec=TeamsClient)
    client.delete_message = AsyncMock(return_value=True)
    return client


@pytest.fixture
def workflow(mock_moderation_agent, mock_notification_agent, mock_teams_client):
    """Create workflow instance for testing."""
    return ModerationWorkflow(
        moderation_agent=mock_moderation_agent,
        notification_agent=mock_notification_agent,
        teams_client=mock_teams_client,
        dry_run=True,
    )


@pytest.mark.asyncio
async def test_process_safe_message(workflow, mock_moderation_agent):
    """Test processing a safe message (no violation)."""
    message = {
        "id": "msg-123",
        "content": "Hello everyone!",
        "from_user": {"display_name": "Test User"},
        "channel_id": "ch-123",
        "channel_name": "general",
    }

    result = await workflow.process_message(message)

    assert result.action_taken == "allowed"
    assert result.notification_result is None


@pytest.mark.asyncio
async def test_process_violating_message(workflow, mock_moderation_agent, mock_notification_agent):
    """Test processing a violating message."""
    # Configure mock to return violation
    mock_moderation_agent.analyze_text.return_value = {
        "is_violation": True,
        "violations": ["hate_speech"],
        "severity": "high",
        "confidence": 0.95,
        "action": "delete",
        "notify": True,
    }

    message = {
        "id": "msg-456",
        "content": "Offensive content",
        "from_user": {"display_name": "Bad Actor"},
        "channel_id": "ch-123",
        "channel_name": "general",
    }

    result = await workflow.process_message(message)

    # In dry-run mode, should mark as "would_delete"
    assert result.action_taken == "would_delete"
    assert result.notification_result is not None
    assert result.notification_result["notification_sent"] is True


@pytest.mark.asyncio
async def test_workflow_end_to_end(workflow, mock_moderation_agent):
    """Test complete workflow execution."""
    message = {
        "id": "msg-789",
        "content": "Test message",
        "from_user": {"display_name": "John Doe"},
        "channel_id": "ch-456",
        "channel_name": "operations",
        "created_at": "2026-01-04T12:00:00Z",
    }

    result = await workflow.process_message(message)

    # Verify moderation was called
    mock_moderation_agent.analyze_text.assert_called_once()

    # Verify context was populated
    assert result.message == message
    assert result.moderation_result is not None
