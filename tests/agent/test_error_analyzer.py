import pytest
import logging
import json
from unittest.mock import patch, MagicMock # Usaremos AsyncMock para call_llm_api se necessário
import asyncio

from agent.error_analyzer import ErrorAnalysisAgent

# Mock para a função async call_llm_api
def async_mock_call_llm_api_error_analyzer(return_value=("Default Response", None)):
    async def mock_llm(*args, **kwargs):
        return return_value
    return mock_llm

@pytest.fixture
def logger_fixture_ea():
    logger = logging.getLogger("TestErrorAnalyzerAsync")
    logger.setLevel(logging.CRITICAL + 1) # Suprime logs a menos que desejado
    return logger

@pytest.fixture
def error_analyzer_fixture(logger_fixture_ea):
    return ErrorAnalysisAgent(
        api_key="test_api_key_ea",
        model="test_model_ea",
        logger=logger_fixture_ea
    )

@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api', new_callable=lambda: async_mock_call_llm_api_error_analyzer(
    return_value=(json.dumps({
        "classification": "SYNTAX_ERROR",
        "suggestion_type": "REGENERATE_PATCHES",
        "suggested_prompt": "[CORRECTION TASK - SYNTAX] Original Objective: Test. Error: Syntax. Fix patches.",
        "details": "Syntax error found."
    }), None)
))
async def test_analyze_error_success_syntax_error(mock_call_llm_api_patched, error_analyzer_fixture):
    result = await error_analyzer_fixture.analyze_error(
        failed_objective="Test objective",
        error_reason="SYNTAX_VALIDATION_FAILED",
        error_context="SyntaxError: invalid syntax",
        original_patches='[{"op": "replace", "path": "/foo", "value": "bar"}]'
    )
    assert result["classification"] == "SYNTAX_ERROR"
    assert result["suggestion_type"] == "REGENERATE_PATCHES"
    assert "Fix patches" in result["suggested_prompt"]
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api', new_callable=lambda: async_mock_call_llm_api_error_analyzer(
    return_value=(json.dumps({
        "classification": "TEST_FAILURE",
        "suggestion_type": "REGENERATE_PATCHES",
        "suggested_prompt": "[CORRECTION TASK - TEST] Objective: Test. Failure: Assert. Regenerate. [CONTEXT_FLAG] TEST_FIX_IN_PROGRESS",
        "details": "Test failed due to assertion."
    }), None)
))
async def test_analyze_error_success_test_failure(mock_call_llm_api_patched, error_analyzer_fixture):
    result = await error_analyzer_fixture.analyze_error(
        failed_objective="Test objective for test failure",
        error_reason="PYTEST_FAILURE",
        error_context="AssertionError: expected True, got False",
        test_output="TestMyFunction.test_case1 failed: AssertionError",
        original_patches='[]'
    )
    assert result["classification"] == "TEST_FAILURE"
    assert result["suggestion_type"] == "REGENERATE_PATCHES"
    assert "[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS" in result["suggested_prompt"]
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api', new_callable=lambda: async_mock_call_llm_api_error_analyzer(
    return_value=(None, "LLM API Error: Connection timed out")
))
async def test_analyze_error_llm_api_error(mock_call_llm_api_patched, error_analyzer_fixture):
    result = await error_analyzer_fixture.analyze_error(
        failed_objective="Objective causing API error",
        error_reason="ANY_REASON",
        error_context="Some context"
    )
    assert result["classification"] == "UNKNOWN_ERROR"
    assert result["suggestion_type"] == "LOG_FOR_REVIEW"
    assert "LLM API Error: Connection timed out" in result["suggested_prompt"]
    assert "LLM call failed during error analysis" in result["details"]
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api', new_callable=lambda: async_mock_call_llm_api_error_analyzer(
    return_value=("", None) # Empty string response
))
async def test_analyze_error_llm_empty_response(mock_call_llm_api_patched, error_analyzer_fixture):
    result = await error_analyzer_fixture.analyze_error(
        failed_objective="Objective with empty LLM response",
        error_reason="ANY_REASON",
        error_context="Some context"
    )
    assert result["classification"] == "UNKNOWN_ERROR"
    assert result["suggestion_type"] == "LOG_FOR_REVIEW"
    assert "empty response from LLM" in result["suggested_prompt"]
    assert "Empty response from LLM" in result["details"]
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api') # Patching a coroutine
async def test_analyze_error_llm_malformed_json_response(mock_call_llm_api_patched, error_analyzer_fixture):
    malformed_json_string = '{"classification": "SYNTAX_ERROR", "suggestion_type": "REGENERATE_PATCHES"'
    # O mock para call_llm_api precisa retornar uma tupla onde o primeiro elemento é o que call_llm_api retorna
    # (que é uma string raw da LLM), e o segundo é o erro (None neste caso).
    # Se call_llm_api é async, o mock também precisa ser async ou retornar um awaitable.
    # Usando new_callable no patch para fornecer um mock async.
    mock_call_llm_api_patched.return_value = (malformed_json_string, None)


    failed_objective_str = "Objective with malformed JSON"
    result = await error_analyzer_fixture.analyze_error(
        failed_objective=failed_objective_str,
        error_reason="ANY_REASON",
        error_context="Some context"
    )
    assert result["classification"] == "SYNTAX_ERROR"
    assert result["suggestion_type"] == "REGENERATE_PATCHES"
    expected_prompt_start_lower = f"erroranalysisagent failed to parse llm response for objective: {failed_objective_str.lower()}"
    assert result["suggested_prompt"].lower().startswith(expected_prompt_start_lower)
    assert malformed_json_string in result["suggested_prompt"]
    expected_details_start_lower = "failed to parse llm json response."
    assert result["details"].lower().startswith(expected_details_start_lower)
    assert malformed_json_string in result["details"]
    mock_call_llm_api_patched.assert_called_once()


@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api', new_callable=lambda: async_mock_call_llm_api_error_analyzer(
    return_value=('{"classification": "LOGIC_ERROR", "details": "Some logic issue found."}', None)
))
async def test_analyze_error_llm_json_missing_keys(mock_call_llm_api_patched, error_analyzer_fixture):
    result = await error_analyzer_fixture.analyze_error(
        failed_objective="Objective with JSON missing keys",
        error_reason="ANY_REASON",
        error_context="Some context"
    )
    assert result["classification"] == "LOGIC_ERROR"
    assert result["suggestion_type"] == "LOG_FOR_REVIEW"
    assert result["suggested_prompt"].startswith("ErrorAnalysisAgent: LLM response missing keys.")
    assert result["details"] == "Some logic issue found."
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.error_analyzer.call_llm_api')
async def test_prompt_construction(mock_call_llm_api_patched, error_analyzer_fixture):
    mock_call_llm_api_patched.return_value = (json.dumps({
        "classification": "TEST_FAILURE", "suggestion_type": "REGENERATE_PATCHES",
        "suggested_prompt": "dummy", "details": "dummy"
    }), None)

    await error_analyzer_fixture.analyze_error(
        failed_objective="O1",
        error_reason="R1",
        error_context="C1",
        original_patches='P1',
        failed_code_snippet="S1",
        test_output="T1"
    )
    mock_call_llm_api_patched.assert_called_once()
    args, _ = mock_call_llm_api_patched.call_args
    prompt_sent_to_llm = args[2]
    assert "[FAILED OBJECTIVE]\nO1" in prompt_sent_to_llm
    assert "[FAILURE REASON CODE]\nR1" in prompt_sent_to_llm
    assert "[FAILURE CONTEXT/DETAILS]\nC1" in prompt_sent_to_llm
    assert "[ORIGINAL PATCHES ATTEMPTED (JSON)]\nP1" in prompt_sent_to_llm
    assert "[FAILED CODE SNIPPET]\nS1" in prompt_sent_to_llm
    assert "[TEST OUTPUT]\nT1" in prompt_sent_to_llm
    assert "Example: '[CORRECTION TASK - TEST] Original Objective: <obj>. Test Failure: <test_out>. Regenerate patches for <files> to pass tests. Previous patches: <patches_json>.\\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS'" in prompt_sent_to_llm

# Remover if __name__ == '__main__': unittest.main() se existir
