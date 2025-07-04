import pytest
from unittest.mock import patch, MagicMock
import requests.exceptions
from agent.tool_executor import web_search

@patch('agent.tool_executor.requests.get')
def test_web_search_success(mock_requests_get):
    # Mock successful API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Results": [
            {"Text": "Test result 1", "FirstURL": "https://example.com/1"},
            {"Text": "Test result 2", "FirstURL": "https://example.com/2"}
        ]
    }
    mock_requests_get.return_value = mock_response
    
    success, results = web_search("test query")
    
    assert success is True
    assert "🔍 RESULTADOS DA PESQUISA WEB:" in results
    assert "1. **Test result 1**" in results
    assert "https://example.com/1" in results
    assert "⭐ Relevância:" in results

@patch('agent.tool_executor.requests.get')
def test_web_search_no_results(mock_requests_get):
    # Mock empty results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Results": []}
    mock_requests_get.return_value = mock_response
    
    success, results = web_search("test query")
    
    assert success is True
    assert "Nenhum resultado relevante encontrado para: 'test query'" in results

@patch('agent.tool_executor.requests.get')
def test_web_search_api_error(mock_requests_get):
    # Mock API error
    mock_requests_get.side_effect = Exception("API error")
    
    success, results = web_search("test query")
    
    assert success is False
    assert "Erro na pesquisa web" in results

@patch('agent.tool_executor.requests.get')
def test_web_search_connection_error(mock_requests_get):
    # Mock connection error
    mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
    
    success, results = web_search("test query")
    
    assert success is False
    assert "Erro na pesquisa web" in results
    assert "Connection failed" in results
