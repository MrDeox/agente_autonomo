import pytest
from hephaestus.utils.json_parser import parse_json_response, _fix_common_json_errors
from hephaestus.utils.advanced_logging import setup_advanced_logging
import logging

@pytest.fixture
def logger():
    return setup_advanced_logging('test_json_serialization', level=logging.DEBUG)

def test_parse_json_response_valid(logger):
    """Test that valid JSON is parsed correctly."""
    test_json = '{\"key\": \"value\"}'
    result, error = parse_json_response(test_json, logger)
    assert error is None
    assert isinstance(result, dict)
    assert result == {"key": "value"}

def test_parse_json_response_invalid(logger):
    """Test that invalid JSON is fixed and parsed correctly."""
    test_json = '{key: "value"}'  # Invalid JSON - missing quotes around key
    result, error = parse_json_response(test_json, logger)
    assert error is None
    assert isinstance(result, dict)
    assert result == {"key": "value"}

def test_fix_common_json_errors(logger):
    """Test common JSON error fixing functionality."""
    test_cases = [
        ('{key: "value"}', '{"key": "value"}'),  # Missing quotes
        ('{"key": "value"', '{"key": "value"}'),  # Missing closing brace
        ('{"key": value}', '{"key": "value"}')  # Missing quotes around value
    ]
    
    for input_json, expected in test_cases:
        fixed = _fix_common_json_errors(input_json, logger)
        assert fixed == expected

def test_json_in_evolution_cycle(logger):
    """Test that JSON serialization works in the context of evolution cycles."""
    # TODO: Implement test that verifies JSON serialization during evolution cycles
    # This will require mocking or creating a test evolution cycle
    pass