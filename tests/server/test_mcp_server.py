#!/usr/bin/env python3
"""
Unit tests for Hephaestus MCP Server
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path

# Import the server module to test
from hephaestus_mcp_server import HephaestusMCPServer

@pytest.fixture
def mock_server():
    """Fixture that provides a mock HephaestusMCPServer instance"""
    server = HephaestusMCPServer()
    server.logger = MagicMock()
    server.config = {}
    server.hephaestus_agent = MagicMock()
    server.meta_intelligence = MagicMock()
    server.memory = MagicMock()
    server.initialized = True
    return server

@pytest.mark.asyncio
async def test_analyze_code_rsi(mock_server):
    """Test the analyze_code_rsi endpoint"""
    # Mock dependencies
    mock_server.hephaestus_agent.state = MagicMock()
    mock_server.hephaestus_agent._generate_manifest = MagicMock(return_value=True)
    mock_server.hephaestus_agent._run_architect_phase = MagicMock(return_value=True)
    
    # Test with sample code
    test_code = "def example():\n    pass"
    result = await mock_server.analyze_code_rsi(test_code, "test context")
    
    # Basic assertions
    assert "analysis" in result
    assert "code_metrics" in result
    assert "suggested_patches" in result
    assert isinstance(result["code_metrics"], dict)

@pytest.mark.asyncio
async def test_deep_self_reflection(mock_server):
    """Test the deep_self_reflection endpoint"""
    # Mock the agent's reflection method
    mock_reflection_result = {
        "meta_awareness": 0.8,
        "new_insights": [{"description": "test insight"}],
        "self_narrative": {"identity": "test"},
        "current_cognitive_state": {}
    }
    mock_server.hephaestus_agent.perform_deep_self_reflection = AsyncMock(return_value=mock_reflection_result)
    
    # Test with focus area
    result = await mock_server.perform_deep_self_reflection("general")
    
    # Basic assertions
    assert "meta_awareness" in result
    assert "new_insights" in result
    assert isinstance(result["new_insights"], list)

@pytest.mark.asyncio
async def test_server_initialization(mock_server):
    """Test server initialization"""
    # Mock initialization dependencies
    with patch('agent.hephaestus_agent.HephaestusAgent') as mock_agent, \
         patch('agent.memory.Memory') as mock_memory, \
         patch('agent.meta_intelligence_core.get_meta_intelligence') as mock_meta:
        
        # Test initialization
        await mock_server.initialize()
        
        # Verify initialization steps
        assert mock_server.initialized is True
        assert mock_server.hephaestus_agent is not None
        assert mock_server.memory is not None
        assert mock_server.meta_intelligence is not None

# TODO: Add more test cases for:
# - Error scenarios
# - Edge cases
# - Additional endpoints
# - Performance testing

if __name__ == "__main__":
    pytest.main()