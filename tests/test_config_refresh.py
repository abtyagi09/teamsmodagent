"""
Test configuration refresh mechanism.

Tests that configuration can be reloaded dynamically without restarting the agent.
"""

import asyncio
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock

import pytest


def test_load_json_config_with_cache_parameter():
    """Test that load_json_config accepts use_cache parameter."""
    from src.utils.config_loader import load_json_config
    
    # Mock the app config client
    with patch('src.utils.config_loader.get_app_config_client') as mock_client:
        mock_client.return_value = None  # Fall back to file
        
        # Should not raise error with use_cache parameter
        try:
            # Will fail to find file, but parameter should be accepted
            config = load_json_config("test.json", use_cache=False)
        except FileNotFoundError:
            pass  # Expected - test file doesn't exist
        

def test_moderation_agent_refresh_policies():
    """Test that ModerationAgent can refresh policies dynamically."""
    from src.agents.moderation_agent import ModerationAgent
    
    # Mock dependencies
    with patch('src.agents.moderation_agent.ContentSafetyClient'), \
         patch('src.agents.moderation_agent.AzureAIAgentClient'), \
         patch('src.agents.moderation_agent.ChatAgent') as mock_chat_agent:
        
        # Create agent with initial policies
        initial_policies = {"category1": {"enabled": True}}
        agent = ModerationAgent(
            foundry_endpoint="https://test.com",
            model_deployment="test-model",
            content_safety_endpoint="https://test.com",
            policies=initial_policies,
        )
        
        # Verify agent has refresh_policies method
        assert hasattr(agent, 'refresh_policies')
        
        # Refresh with new policies
        new_policies = {"category1": {"enabled": False}, "category2": {"enabled": True}}
        agent.refresh_policies(new_policies)
        
        # Verify policies were updated
        assert agent.policies == new_policies


@pytest.mark.asyncio
async def test_workflow_configuration_refresh():
    """Test that workflow can refresh configuration periodically."""
    from src.orchestrator.workflow import ModerationWorkflow
    
    # Mock all dependencies
    mock_moderation_agent = Mock()
    mock_moderation_agent.refresh_policies = Mock()
    mock_notification_agent = Mock()
    mock_teams_client = Mock()
    
    # Create workflow with short refresh interval
    workflow = ModerationWorkflow(
        moderation_agent=mock_moderation_agent,
        notification_agent=mock_notification_agent,
        teams_client=mock_teams_client,
        config_refresh_interval=1,  # 1 second for testing
    )
    
    # Verify workflow has refresh method
    assert hasattr(workflow, '_refresh_configuration')
    assert hasattr(workflow, '_last_config_refresh')
    assert hasattr(workflow, '_monitored_channels')
    
    # Mock config loading
    with patch('src.orchestrator.workflow.load_json_config') as mock_load:
        mock_load.side_effect = [
            {"category1": {"enabled": True}},  # policies
            {"monitored_channels": ["general"]},  # channels
        ]
        
        # Call refresh
        await workflow._refresh_configuration()
        
        # Verify config was loaded with use_cache=False
        assert mock_load.call_count == 2
        assert mock_load.call_args_list[0][1]['use_cache'] is False
        assert mock_load.call_args_list[1][1]['use_cache'] is False
        
        # Verify agent policies were refreshed
        mock_moderation_agent.refresh_policies.assert_called_once()


def test_workflow_config_refresh_interval():
    """Test that workflow accepts config_refresh_interval parameter."""
    from src.orchestrator.workflow import ModerationWorkflow
    
    mock_moderation_agent = Mock()
    mock_notification_agent = Mock()
    mock_teams_client = Mock()
    
    # Test default interval
    workflow1 = ModerationWorkflow(
        moderation_agent=mock_moderation_agent,
        notification_agent=mock_notification_agent,
        teams_client=mock_teams_client,
    )
    assert workflow1.config_refresh_interval == 300  # Default 5 minutes
    
    # Test custom interval
    workflow2 = ModerationWorkflow(
        moderation_agent=mock_moderation_agent,
        notification_agent=mock_notification_agent,
        teams_client=mock_teams_client,
        config_refresh_interval=60,
    )
    assert workflow2.config_refresh_interval == 60


if __name__ == "__main__":
    # Run basic tests
    print("Testing configuration refresh mechanism...")
    
    print("✓ Test 1: load_json_config with cache parameter")
    test_load_json_config_with_cache_parameter()
    
    print("✓ Test 2: ModerationAgent refresh_policies")
    test_moderation_agent_refresh_policies()
    
    print("✓ Test 3: Workflow config_refresh_interval")
    test_workflow_config_refresh_interval()
    
    print("\n✅ All basic tests passed!")
    print("\nNote: Run 'pytest test_config_refresh.py' for async tests")
