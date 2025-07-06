import pytest
import logging
from unittest.mock import MagicMock, AsyncMock
from agent.agents.swarm_coordinator_agent import SwarmCoordinatorAgent, SwarmObjective

@pytest.fixture
def swarm_agent():
    config = {
        "swarm_coordination": {
            "max_concurrent_objectives": 5,
            "min_agents_per_objective": 2,
            "max_agents_per_objective": 6
        }
    }
    logger = logging.getLogger(__name__)
    return SwarmCoordinatorAgent("gemini-pro", config, logger)

@pytest.fixture
def mock_comm_system(swarm_agent):
    comm_system = MagicMock()
    comm_system.agent_capabilities = {
        "agent1": ["analysis", "coding"],
        "agent2": ["testing", "review"],
        "agent3": ["deployment", "monitoring"]
    }
    swarm_agent.set_communication_system(comm_system)
    return comm_system

@pytest.mark.asyncio
async def test_coordinate_new_objective(swarm_agent, mock_comm_system):
    # Setup
    objective = "Implement new feature"
    requester = "agent1"
    
    # Execute
    result = await swarm_agent.coordinate_new_objective(objective, requester)
    
    # Verify
    assert result["success"] is True
    assert "objective_id" in result
    assert len(result["participants"]) >= swarm_agent.min_agents_per_objective
    assert mock_comm_system.create_collaboration_session.called
    assert mock_comm_system.start_conversation.called

@pytest.mark.asyncio
async def test_handle_message_request(swarm_agent, mock_comm_system):
    # Setup
    message = MagicMock()
    message.message_type = "REQUEST"
    message.content = {
        "request_type": "coordinate_objective",
        "objective": "Fix critical bug",
        "requesting_agent": "agent2"
    }
    
    # Execute
    result = await swarm_agent.handle_message(message)
    
    # Verify
    assert result["success"] is True
    assert "objective_id" in result

@pytest.mark.asyncio
async def test_raft_consensus(swarm_agent):
    # Test leader election
    swarm_agent.raft.state = 'candidate'
    swarm_agent.raft.current_term = 1
    
    # Request vote from other nodes
    vote_granted = await swarm_agent.raft.request_vote("node2", 2)
    assert vote_granted is True
    
    # Verify term update
    assert swarm_agent.raft.current_term == 2
    assert swarm_agent.raft.voted_for == "node2"

def test_get_swarm_metrics(swarm_agent, mock_comm_system):
    # Setup
    swarm_agent.swarm_objectives = {
        "obj1": SwarmObjective("obj1", "Test", "simple", [], 10, 5, "completed"),
        "obj2": SwarmObjective("obj2", "Test", "complex", [], 20, 8, "active")
    }
    
    # Execute
    metrics = swarm_agent.get_swarm_metrics()
    
    # Verify
    assert metrics.total_agents == 3
    assert metrics.success_rate == 0.5
    assert 0 <= metrics.collective_intelligence_score <= 1.0

@pytest.mark.asyncio
async def test_error_handling(swarm_agent):
    # Setup
    agent_name = "agent3"
    error_desc = "Failed to process task"
    
    # Execute
    result = await swarm_agent._attempt_error_resolution(agent_name, error_desc)
    
    # Verify
    assert "resolution_type" in result
    assert result["resolution_type"] in ["automatic", "manual_intervention_required"]