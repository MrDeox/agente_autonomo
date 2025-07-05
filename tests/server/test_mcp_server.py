#!/usr/bin/env python3
"""
Unit tests for the HephaestusMCPServer module.

Focuses on testing critical API endpoints:
- /analyze_code_rsi
- /system_status
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

# Import the server module to test
from hephaestus_mcp_server import HephaestusMCPServer

@pytest.fixture
def mock_server():
    """Fixture to create a mock HephaestusMCPServer instance"""
    server = HephaestusMCPServer()
    server.initialized = True
    server.hephaestus_agent = MagicMock()
    server.memory = MagicMock()
    server.config = {}
    server.meta_intelligence = MagicMock()
    return server

@pytest.mark.asyncio
async def test_analyze_code_rsi(mock_server):
    """Test the analyze_code_rsi endpoint"""
    # Mock dependencies
    mock_server.hephaestus_agent.state = MagicMock()
    mock_server.hephaestus_agent.state.get_architect_analysis.return_value = "Mock analysis"
    mock_server.hephaestus_agent.state.get_patches_to_apply.return_value = []
    
    # Test basic functionality
    test_code = "def test(): pass"
    result = await mock_server.analyze_code_rsi(test_code)
    
    assert "analysis" in result
    assert "code_metrics" in result
    assert "rsi_insights" in result

@pytest.mark.asyncio
async def test_system_status(mock_server):
    """Test the system_status endpoint"""
    # Test basic functionality
    result = await mock_server.system_status()
    
    assert "initialized" in result
    assert "meta_intelligence_active" in result
    assert "memory_loaded" in result
    assert "config_loaded" in result
    assert "agent_ready" in result

@pytest.mark.asyncio
async def test_system_status_not_initialized():
    """Test system_status when server is not initialized"""
    server = HephaestusMCPServer()
    server.initialized = False
    
    result = await server.system_status()
    
    assert result["initialized"] == False
    assert result["meta_intelligence_active"] == False

# TODO: Add more test cases for error scenarios
# TODO: Add tests for mocking external dependencies
# TODO: Expand test coverage for edge cases