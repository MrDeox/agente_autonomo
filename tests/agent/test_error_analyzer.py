import unittest
import logging
import json
from unittest.mock import patch, MagicMock

from agent.error_analyzer import ErrorAnalysisAgent

class TestErrorAnalysisAgent(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        # Suppress logging during tests unless specifically needed
        self.logger.setLevel(logging.CRITICAL + 1)

        self.api_key = "test_api_key"
        self.model = "test_model"
        self.analyzer = ErrorAnalysisAgent(
            api_key=self.api_key,
            model=self.model,
            logger=self.logger
        )

    @patch('agent.error_analyzer.call_llm_api')
    def test_analyze_error_success_syntax_error(self, mock_call_llm_api):
        mock_llm_response = {
            "classification": "SYNTAX_ERROR",
            "suggestion_type": "REGENERATE_PATCHES",
            "suggested_prompt": "[CORRECTION TASK - SYNTAX] Original Objective: Test. Error: Syntax. Fix patches.",
            "details": "Syntax error found."
        }
        mock_call_llm_api.return_value = (json.dumps(mock_llm_response), None)

        result = self.analyzer.analyze_error(
            failed_objective="Test objective",
            error_reason="SYNTAX_VALIDATION_FAILED",
            error_context="SyntaxError: invalid syntax",
            original_patches='[{"op": "replace", "path": "/foo", "value": "bar"}]'
        )

        self.assertEqual(result["classification"], "SYNTAX_ERROR")
        self.assertEqual(result["suggestion_type"], "REGENERATE_PATCHES")
        self.assertIn("Fix patches", result["suggested_prompt"])
        mock_call_llm_api.assert_called_once()
        # You could add more assertions here to check the prompt sent to the LLM if needed

    @patch('agent.error_analyzer.call_llm_api')
    def test_analyze_error_success_test_failure(self, mock_call_llm_api):
        mock_llm_response = {
            "classification": "TEST_FAILURE",
            "suggestion_type": "REGENERATE_PATCHES",
            "suggested_prompt": "[CORRECTION TASK - TEST] Objective: Test. Failure: Assert. Regenerate. [CONTEXT_FLAG] TEST_FIX_IN_PROGRESS",
            "details": "Test failed due to assertion."
        }
        mock_call_llm_api.return_value = (json.dumps(mock_llm_response), None)

        result = self.analyzer.analyze_error(
            failed_objective="Test objective for test failure",
            error_reason="PYTEST_FAILURE",
            error_context="AssertionError: expected True, got False",
            test_output="TestMyFunction.test_case1 failed: AssertionError",
            original_patches='[]'
        )
        self.assertEqual(result["classification"], "TEST_FAILURE")
        self.assertEqual(result["suggestion_type"], "REGENERATE_PATCHES")
        self.assertIn("[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS", result["suggested_prompt"])
        mock_call_llm_api.assert_called_once()

    @patch('agent.error_analyzer.call_llm_api')
    def test_analyze_error_llm_api_error(self, mock_call_llm_api):
        mock_call_llm_api.return_value = (None, "LLM API Error: Connection timed out")

        result = self.analyzer.analyze_error(
            failed_objective="Objective causing API error",
            error_reason="ANY_REASON",
            error_context="Some context"
        )

        self.assertEqual(result["classification"], "UNKNOWN_ERROR")
        self.assertEqual(result["suggestion_type"], "LOG_FOR_REVIEW")
        self.assertIn("LLM API Error: Connection timed out", result["suggested_prompt"])
        self.assertIn("LLM call failed during error analysis", result["details"])
        mock_call_llm_api.assert_called_once()

    @patch('agent.error_analyzer.call_llm_api')
    def test_analyze_error_llm_empty_response(self, mock_call_llm_api):
        mock_call_llm_api.return_value = ("", None) # Empty string response

        result = self.analyzer.analyze_error(
            failed_objective="Objective with empty LLM response",
            error_reason="ANY_REASON",
            error_context="Some context"
        )

        self.assertEqual(result["classification"], "UNKNOWN_ERROR")
        self.assertEqual(result["suggestion_type"], "LOG_FOR_REVIEW")
        self.assertIn("empty response from LLM", result["suggested_prompt"])
        self.assertIn("Empty response from LLM", result["details"])
        mock_call_llm_api.assert_called_once()

    @patch('agent.error_analyzer.call_llm_api')
    def test_analyze_error_llm_malformed_json_response(self, mock_call_llm_api):
        malformed_json_string = '{"classification": "SYNTAX_ERROR", "suggestion_type": "REGENERATE_PATCHES"' # Missing closing brace and other fields
        mock_call_llm_api.return_value = (malformed_json_string, None)

        failed_objective_str = "Objective with malformed JSON" # Define for use in assertion string
        result = self.analyzer.analyze_error(
            failed_objective=failed_objective_str,
            error_reason="ANY_REASON",
            error_context="Some context"
        )

        # Check fallback behavior
        self.assertEqual(result["classification"], "SYNTAX_ERROR") # Regex should pick this up
        self.assertEqual(result["suggestion_type"], "REGENERATE_PATCHES") # Regex should pick this up

        # Verify suggested_prompt content for malformed JSON
        expected_prompt_start_lower = f"erroranalysisagent failed to parse llm response for objective: {failed_objective_str.lower()}"
        self.assertTrue(result["suggested_prompt"].lower().startswith(expected_prompt_start_lower))
        self.assertIn(malformed_json_string, result["suggested_prompt"]) # Raw response should be included

        # Verify details content for malformed JSON
        expected_details_start_lower = "failed to parse llm json response."
        self.assertTrue(result["details"].lower().startswith(expected_details_start_lower))
        self.assertIn(malformed_json_string, result["details"]) # Raw response should be included

        mock_call_llm_api.assert_called_once()

    @patch('agent.error_analyzer.call_llm_api')
    def test_analyze_error_llm_json_missing_keys(self, mock_call_llm_api):
        json_missing_keys = '{"classification": "LOGIC_ERROR", "details": "Some logic issue found."}' # Missing suggestion_type and suggested_prompt
        mock_call_llm_api.return_value = (json_missing_keys, None)

        result = self.analyzer.analyze_error(
            failed_objective="Objective with JSON missing keys",
            error_reason="ANY_REASON",
            error_context="Some context"
        )

        self.assertEqual(result["classification"], "LOGIC_ERROR")
        self.assertEqual(result["suggestion_type"], "LOG_FOR_REVIEW") # Fallback for missing suggestion_type
        self.assertTrue(result["suggested_prompt"].startswith("ErrorAnalysisAgent: LLM response missing keys."))
        # If 'details' is provided in the LLM response, it should be used directly.
        # The fallback "missing keys" detail message is only if 'details' itself is missing.
        self.assertEqual(result["details"], "Some logic issue found.")
        mock_call_llm_api.assert_called_once()

    def test_prompt_construction(self):
        # More of an integration test for the prompt string itself, but can be useful
        # This test does not mock call_llm_api as we are testing the prompt string
        with patch('agent.error_analyzer.call_llm_api') as mock_llm_call:
            # To prevent actual call and check args
            mock_llm_call.return_value = (json.dumps({
                "classification": "TEST_FAILURE", "suggestion_type": "REGENERATE_PATCHES",
                "suggested_prompt": "dummy", "details": "dummy"
            }), None)

            self.analyzer.analyze_error(
                failed_objective="O1",
                error_reason="R1",
                error_context="C1",
                original_patches='P1',
                failed_code_snippet="S1",
                test_output="T1"
            )

            mock_llm_call.assert_called_once()
            args, _ = mock_llm_call.call_args
            prompt_sent_to_llm = args[2] # prompt is the 3rd argument (api_key, model, prompt, ...)

            self.assertIn("[FAILED OBJECTIVE]\nO1", prompt_sent_to_llm)
            self.assertIn("[FAILURE REASON CODE]\nR1", prompt_sent_to_llm)
            self.assertIn("[FAILURE CONTEXT/DETAILS]\nC1", prompt_sent_to_llm)
            self.assertIn("[ORIGINAL PATCHES ATTEMPTED (JSON)]\nP1", prompt_sent_to_llm)
            self.assertIn("[FAILED CODE SNIPPET]\nS1", prompt_sent_to_llm)
            self.assertIn("[TEST OUTPUT]\nT1", prompt_sent_to_llm)
            self.assertIn("Example: '[CORRECTION TASK - TEST] Original Objective: <obj>. Test Failure: <test_out>. Regenerate patches for <files> to pass tests. Previous patches: <patches_json>.\\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS'", prompt_sent_to_llm)

if __name__ == '__main__':
    unittest.main()
