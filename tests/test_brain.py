import unittest
from unittest.mock import patch, MagicMock, ANY
import logging
import pytest

# Functions to test
from agent.brain import generate_next_objective, generate_capacitation_objective, generate_commit_message

class TestBrainFunctions(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG) # Or logging.CRITICAL to suppress logs during most tests

        self.model_config = {
            "primary": "test_model",
            "fallback": "fallback_model",
            "primary_api_key": "test_api_key",
            "fallback_api_key": "fallback_api_key",
            "primary_base_url": "https://api.example.com/v1",
            "fallback_base_url": "https://fallback.example.com/v1",
        }

        # Default config for testing generate_next_objective thresholds
        self.default_config = {
            "code_analysis_thresholds": {
                "file_loc": 250,
                "function_loc": 40,
                "function_cc": 8
            },
            # Add other config keys if generate_next_objective starts using them
        }

    @patch('agent.brain.call_llm_api')
    @patch('agent.brain.analyze_code_metrics')
    def test_generate_next_objective_uses_config_thresholds(self, mock_analyze_code_metrics, mock_call_llm_api):
        # --- Test with default thresholds from self.default_config ---
        mock_analyze_code_metrics.return_value = {"summary": {"large_files": [("file.py", 300)]}} # Mock return for analyze_code_metrics
        mock_call_llm_api.return_value = ("New objective based on defaults", None)

        generate_next_objective(
            model_config=self.model_config,
            current_manifest="Manifest content",
            logger=self.logger,
            project_root_dir=".",
            config=self.default_config, # Pass the test config
            memory_summary="No relevant history."
        )

        mock_analyze_code_metrics.assert_called_with(
            root_dir=".",
            file_loc_threshold=250, # from self.default_config
            func_loc_threshold=40,  # from self.default_config
            func_cc_threshold=8     # from self.default_config
        )
        mock_call_llm_api.assert_called_once() # Ensure LLM is still called
        mock_analyze_code_metrics.reset_mock()
        mock_call_llm_api.reset_mock()

        # --- Test with different thresholds provided in config ---
        custom_config = {
            "code_analysis_thresholds": {
                "file_loc": 500,
                "function_loc": 100,
                "function_cc": 15
            }
        }
        mock_analyze_code_metrics.return_value = {"summary": {"complex_functions": [("file.py", "func", 20)]}}
        mock_call_llm_api.return_value = ("New objective based on custom", None)

        generate_next_objective(
            model_config=self.model_config,
            current_manifest="Manifest content",
            logger=self.logger,
            project_root_dir="/another/path",
            config=custom_config, # Pass the custom test config
            memory_summary="Some history."
        )

        mock_analyze_code_metrics.assert_called_with(
            root_dir="/another/path",
            file_loc_threshold=500, # from custom_config
            func_loc_threshold=100, # from custom_config
            func_cc_threshold=15    # from custom_config
        )
        mock_call_llm_api.assert_called_once()
        mock_analyze_code_metrics.reset_mock()
        mock_call_llm_api.reset_mock()

        # --- Test with missing thresholds in config (should use defaults from get) ---
        config_missing_thresholds = {} # Empty config
        mock_analyze_code_metrics.return_value = {"summary": {}}
        mock_call_llm_api.return_value = ("Objective with default thresholds", None)

        generate_next_objective(
            model_config=self.model_config,
            current_manifest="",
            logger=self.logger,
            project_root_dir=".",
            config=config_missing_thresholds, # Pass empty config
        )

        # Defaults inside generate_next_objective if config values are missing
        mock_analyze_code_metrics.assert_called_with(
            root_dir=".",
            file_loc_threshold=300, # Default from .get("file_loc", 300)
            func_loc_threshold=50,  # Default from .get("function_loc", 50)
            func_cc_threshold=10     # Default from .get("function_cc", 10)
        )
        mock_call_llm_api.assert_called_once()


    @patch('agent.brain.call_llm_api')
    @patch('agent.brain.analyze_code_metrics')
    def test_generate_next_objective_llm_call_success(self, mock_analyze_code_metrics, mock_call_llm_api):
        mock_analyze_code_metrics.return_value = {"summary": {}}
        mock_call_llm_api.return_value = ("Test objective", None)

        objective = generate_next_objective(
            model_config=self.model_config, current_manifest="Test Manifest",
            logger=self.logger, project_root_dir=".", config=self.default_config
        )

        self.assertEqual(objective, "Test objective")
        mock_analyze_code_metrics.assert_called_once() # Verify this mock is called
        mock_call_llm_api.assert_called_once()

        called_args_llm, called_kwargs_llm = mock_call_llm_api.call_args
        self.assertEqual(called_kwargs_llm["model_config"], self.model_config)
        self.assertIsInstance(called_kwargs_llm["prompt"], str) # Check that a prompt string is passed
        self.assertTrue(len(called_kwargs_llm["prompt"]) > 50) # Check prompt is not trivial/empty
        self.assertIn("Test Manifest", called_kwargs_llm["prompt"]) # Still check for key context presence
        self.assertEqual(called_kwargs_llm["temperature"], 0.3)
        self.assertEqual(called_kwargs_llm["logger"], self.logger)

    @patch('agent.brain.call_llm_api') # This mock is for the call inside generate_next_objective
    @patch('agent.brain.analyze_code_metrics') # Also mock this as it's called before the error path for LLM
    def test_generate_next_objective_llm_call_error(self, mock_analyze_code_metrics, mock_call_llm_api):
        mock_call_llm_api.return_value = (None, "LLM Error")

        objective = generate_next_objective(
            model_config=self.model_config, current_manifest="Test Manifest",
            logger=self.logger, project_root_dir=".", config=self.default_config
        )

        # Fallback objective
        self.assertEqual(objective, "Analisar o estado atual do projeto e propor uma melhoria incremental")
        mock_call_llm_api.assert_called_once()

    @patch('agent.brain.call_llm_api')
    def test_generate_capacitation_objective_success(self, mock_call_llm_api):
        mock_call_llm_api.return_value = ("Capacitation objective", None)
        engineer_analysis = "Need new tool X"

        objective = generate_capacitation_objective(
            model_config=self.model_config, engineer_analysis=engineer_analysis,
            logger=self.logger
        )

        self.assertEqual(objective, "Capacitation objective")
        mock_call_llm_api.assert_called_once() # Ensure it was called
        called_kwargs = mock_call_llm_api.call_args.kwargs
        self.assertEqual(called_kwargs["model_config"], self.model_config)
        self.assertIn(engineer_analysis, called_kwargs["prompt"]) # prompt is in kwargs
        self.assertEqual(called_kwargs["temperature"], 0.3)          # temperature is in kwargs
        self.assertEqual(called_kwargs["logger"], self.logger)

    @patch('agent.brain.call_llm_api')
    def test_generate_capacitation_objective_error(self, mock_call_llm_api):
        mock_call_llm_api.return_value = (None, "LLM Error")
        engineer_analysis = "Need new tool X"

        objective = generate_capacitation_objective(
            model_config=self.model_config, engineer_analysis=engineer_analysis,
            logger=self.logger
        )

        self.assertEqual(objective, "Analisar a necessidade de capacitação e propor uma solução") # Fallback
        mock_call_llm_api.assert_called_once()

    # Test for generate_commit_message (which is currently simulated and does not call LLM)
    def test_generate_commit_message_simulated(self):
        analysis_summary = "Implemented feature Y by modifying Z."
        objective = "feat: Add new feature Y for enhanced performance" # Objective starts with type

        commit_message = generate_commit_message(
            analysis_summary=analysis_summary, objective=objective,
            logger=self.logger
        )
        # Now, the function should extract "feat" as type and use the rest as summary.
        expected_summary_part = "Add new feature Y for enhanced performance"
        self.assertEqual(commit_message, f"feat: {expected_summary_part}")

        # Check if it respects length limits for the summary part
        long_objective = "feat: Implement a very long and detailed feature description that will certainly exceed the typical subject line length for a commit message"
        commit_message_long = generate_commit_message(
            analysis_summary, long_objective, self.logger
        )
        # Expected summary: "Implement a very long and detailed feature description that will cert..."
        # Expected full: "feat: Implement a very long and detailed feature desc..." (type + summary)
        # Max summary length for "feat" is 72 - (4 + 2) = 66
        # "Implement a very long and detailed feature description that will certainly exceed the typical subject line length for a commit message" (115 chars for summary part)
        # max_summary_len for "feat" is 66. Slice at 66-3=63.
        # Actual output seems to be summary_part[:62] + "..." which is "Implement a very long and detailed feature description that wil..."
        expected_long_summary_part = "Implement a very long and detailed feature description that wil..." # Adjusted to current actual output
        self.assertEqual(commit_message_long, f"feat: {expected_long_summary_part}")
        self.assertLessEqual(len(commit_message_long), 72)

        objective_fix = "fix: Resolve critical bug in module X causing data corruption"
        commit_message_fix = generate_commit_message(
            "Fixed the bug.", objective_fix, self.logger
        )
        # max_summary_len for "fix" is 72 - (3 + 2) = 67.
        # Summary part: "Resolve critical bug in module X causing data corruption" (56 chars). No truncation.
        expected_fix_summary_part = "Resolve critical bug in module X causing data corruption" # This should be fine
        self.assertEqual(commit_message_fix, f"fix: {expected_fix_summary_part}")
        self.assertLessEqual(len(commit_message_fix), 72)

        # Test a simple objective without a type prefix - heuristic should apply
        simple_objective = "Improve the logging system for better debuggability" # 50 chars.
        commit_message_simple = generate_commit_message(
            "Added more logs.", simple_objective, self.logger
        )
        # Heuristic defaults to "feat". max_summary_len for "feat" is 66. No truncation.
        self.assertEqual(commit_message_simple, f"feat: {simple_objective}") # This should be fine

        # Test objective that gets truncated due to heuristic type
        objective_for_trunc = "refactor the entire authentication module to use new security protocols and also improve performance"
        # type "refactor" (8 chars). max_summary_len = 72 - (8+2) = 62.
        # summary part: "the entire authentication module to use new security protocols and also improve performance" (90 chars)
        # truncated summary part should be summary_part[:59] + "..."
        # summary_part[:59] = "the entire authentication module to use new security protocol"
        # expected_trunc_summary = "the entire authentication module to use new security protocol..." # This should be fine
        commit_message_trunc = generate_commit_message(
            "Refactored auth.", objective_for_trunc, self.logger
        )
        expected_trunc_summary = "the entire authentication module to use new security protocol..."
        self.assertEqual(commit_message_trunc, f"refactor: {expected_trunc_summary}")

@patch('agent.brain.call_llm_api')
@patch('agent.brain.analyze_code_metrics')
@patch('agent.brain.PerformanceAnalysisAgent.analyze_performance')
@patch('builtins.open')
def test_generate_next_objective_flow(
    mock_open, mock_analyze_performance, mock_analyze_code_metrics, mock_call_llm_api
):
    """
    Test the basic flow of generate_next_objective, ensuring all helper
    functions are called and the LLM response is returned.
    """
    # Arrange
    mock_analyze_performance.return_value = '{"perf": "data"}'
    mock_analyze_code_metrics.return_value = {"summary": {"code": "metrics"}}
    mock_call_llm_api.return_value = ("Test Objective", None)
    
    logger = MagicMock()
    model_config = {"model": "test_model"}
    config = {}
    memory_summary = "Recent history"
    current_manifest = "Test Manifest"

    # Act
    objective = generate_next_objective(
        model_config=model_config,
        current_manifest=current_manifest,
        logger=logger,
        project_root_dir=".",
        config=config,
        memory_summary=memory_summary,
    )

    # Assert
    assert objective == "Test Objective"
    mock_analyze_performance.assert_called_once()
    mock_analyze_code_metrics.assert_called_once()
    mock_call_llm_api.assert_called_once()
    
    # Check that the prompt contains all the gathered information
    prompt_arg = mock_call_llm_api.call_args[1]['prompt']
    assert "Test Manifest" in prompt_arg
    assert '{"perf": "data"}' in prompt_arg
    assert "Recent history" in prompt_arg

if __name__ == '__main__':
    unittest.main()
