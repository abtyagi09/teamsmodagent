"""
Test suite for moderation agent.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.moderation_agent import ModerationAgent


@pytest.fixture
def mock_content_safety_client():
    """Mock Azure Content Safety client."""
    with patch("src.agents.moderation_agent.ContentSafetyClient") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_agent_client():
    """Mock Azure AI Agent client."""
    with patch("src.agents.moderation_agent.AzureAIAgentClient") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def moderation_agent(mock_content_safety_client, mock_agent_client):
    """Create moderation agent instance for testing."""
    policies = {
        "text_policies": {
            "hate_speech": {
                "enabled": True,
                "threshold": "medium",
                "action": "delete",
                "notify": True,
            }
        }
    }

    return ModerationAgent(
        foundry_endpoint="https://test.api.azureml.ms",
        model_deployment="test-model",
        content_safety_endpoint="https://test.cognitiveservices.azure.com",
        content_safety_key="test-key",
        policies=policies,
    )


@pytest.mark.asyncio
async def test_analyze_text_no_violation(moderation_agent, mock_content_safety_client):
    """Test analyzing safe content."""
    # Mock Content Safety response (no violation)
    mock_response = MagicMock()
    mock_response.categories_analysis = [
        MagicMock(severity=0),  # hate
        MagicMock(severity=0),  # self_harm
        MagicMock(severity=0),  # sexual
        MagicMock(severity=0),  # violence
    ]
    mock_content_safety_client.analyze_text.return_value = mock_response

    # Mock agent response
    mock_agent_response = MagicMock()
    mock_agent_response.text = """```json
{
    "is_violation": false,
    "violations": [],
    "severity": "low",
    "confidence": 0.1,
    "justification": "Content appears safe",
    "recommended_action": "allow"
}
```"""
    moderation_agent.chat_agent.run = AsyncMock(return_value=mock_agent_response)

    # Analyze text
    result = await moderation_agent.analyze_text("Hello, how are you today?")

    # Verify
    assert result["is_violation"] is False
    assert result["action"] == "allow"


@pytest.mark.asyncio
async def test_analyze_text_with_violation(moderation_agent, mock_content_safety_client):
    """Test analyzing violating content."""
    # Mock Content Safety response (violation detected)
    mock_response = MagicMock()
    mock_response.categories_analysis = [
        MagicMock(severity=4),  # hate - high severity
        MagicMock(severity=0),
        MagicMock(severity=0),
        MagicMock(severity=0),
    ]
    mock_content_safety_client.analyze_text.return_value = mock_response

    # Mock agent response
    mock_agent_response = MagicMock()
    mock_agent_response.text = """```json
{
    "is_violation": true,
    "violations": ["hate_speech"],
    "severity": "high",
    "confidence": 0.95,
    "justification": "Content contains hate speech",
    "recommended_action": "delete"
}
```"""
    moderation_agent.chat_agent.run = AsyncMock(return_value=mock_agent_response)

    # Analyze text
    result = await moderation_agent.analyze_text("Offensive hate speech content here")

    # Verify
    assert result["is_violation"] is True
    assert result["action"] == "delete"
    assert result["notify"] is True
    assert "hate_speech" in result["violations"]


@pytest.mark.asyncio
async def test_apply_policies(moderation_agent):
    """Test policy application logic."""
    content_safety_result = {"flagged": True, "categories": {"hate": 4}}

    agent_result = {
        "is_violation": True,
        "violations": ["hate_speech"],
        "severity": "high",
        "confidence": 0.9,
        "recommended_action": "delete",
    }

    result = moderation_agent._apply_policies(content_safety_result, agent_result)

    assert result["is_violation"] is True
    assert result["action"] == "delete"
    assert result["notify"] is True
