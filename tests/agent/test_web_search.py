import pytest
from unittest.mock import patch, MagicMock
from agent.tool_executor import web_search

@pytest.fixture
def mock_requests_get():
    with patch('agent.tool_executor.requests.get') as mock_get:
        yield mock_get

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
    assert "1. Test result 1" in results
    assert "URL: https://example.com/1" in results
    assert "2. Test result 2" in results
    assert "URL: https://example.com/2" in results

def test_web_search_no_results(mock_requests_get):
    # Mock empty results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Results": []}
    mock_requests_get.return_value = mock_response

    success, results = web_search("test query")
    
    assert success is True
    assert "Nenhum resultado encontrado para a pesquisa." in results

def test_web_search_api_error(mock_requests_get):
    # Mock API error
    mock_requests_get.side_effect = Exception("API error")
    
    success, results = web_search("test query")
    
    assert success is False
    assert "Erro na pesquisa web" in results

def test_web_search_connection_error(mock_requests_get):
    # Mock connection error
    mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
    
    success, results = web_search("test query")
    
    assert success is False
    assert "Erro na pesquisa web" in results
    assert "Connection failed" in results
