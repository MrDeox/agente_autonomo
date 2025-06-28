import logging
import json # For parsing LLM response and example usage
import re # For fallback parsing of LLM response
from typing import Optional, Dict, Any, Tuple

from agent.utils.llm_client import call_llm_api

class ErrorAnalysisAgent:
    def __init__(self, api_key: str, model: str, logger: logging.Logger, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.logger = logger
        self.base_url = base_url

    async def analyze_error( # Changed to async
        self,
        failed_objective: str,
        error_reason: str,
        error_context: str,
        original_patches: Optional[str] = None,
        failed_code_snippet: Optional[str] = None,
        test_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyzes a failure and suggests a course of action.

        Args:
            failed_objective: The objective that failed.
            error_reason: A short code for the failure (e.g., "SYNTAX_VALIDATION_FAILED").
            error_context: Detailed error message or stack trace.
            original_patches: JSON string of the patches that were attempted.
            failed_code_snippet: Snippet of code that failed, if available.
            test_output: Output from test execution, if the failure was test-related.

        Returns:
            A dictionary containing:
            - "classification": (e.g., "SYNTAX_ERROR", "TEST_FAILURE", "LOGIC_ERROR", "UNKNOWN_ERROR")
            - "suggestion_type": (e.g., "REGENERATE_PATCHES", "NEW_OBJECTIVE", "RETRY_WITH_MODIFICATION", "LOG_FOR_REVIEW")
            - "suggested_prompt": A prompt for the next LLM call (e.g., to ArchitectAgent or ObjectiveGenerator).
            - "details": Additional details or reasoning.
        """
        self.logger.info(f"ErrorAnalysisAgent: Analyzing error for objective: {failed_objective}")
        self.logger.debug(f"Error reason: {error_reason}")
        self.logger.debug(f"Error context: {error_context[:500]}...") # Log snippet of context

        prompt_parts = [
            "[CONTEXT]",
            "You are an Error Analysis Agent. Your task is to diagnose a failure that occurred while an AI agent was trying to achieve an objective.",
            "Based on the provided information, classify the error and recommend a specific, actionable next step for the AI agent.",
            "The goal is to automatically recover from this failure if possible, or to learn from it.",
            "\n[FAILED OBJECTIVE]",
            failed_objective,
            "\n[FAILURE REASON CODE]",
            error_reason,
            "\n[FAILURE CONTEXT/DETAILS]",
            error_context
        ]

        if original_patches and original_patches.lower() != "n/a":
            prompt_parts.extend(["\n[ORIGINAL PATCHES ATTEMPTED (JSON)]", original_patches])

        if failed_code_snippet:
            prompt_parts.extend(["\n[FAILED CODE SNIPPET]", failed_code_snippet])

        if test_output:
            prompt_parts.extend(["\n[TEST OUTPUT]", test_output])

        prompt_parts.extend([
            "\n[YOUR TASK]",
            "1. Classify the error. Choose one from: SYNTAX_ERROR, TEST_FAILURE, LOGIC_ERROR, CONFIGURATION_ERROR, TOOL_ERROR, UNKNOWN_ERROR.",
            "2. Based on the classification and details, determine the best suggestion type. Choose one from: REGENERATE_PATCHES, NEW_OBJECTIVE, RETRY_WITH_MODIFICATION, LOG_FOR_REVIEW, FIX_CONFIGURATION.",
            "3. Generate a 'suggested_prompt' for the AI agent's next action. This prompt MUST be directly usable by another AI agent (like an Architect or Objective Generator) to implement the fix or new approach. Ensure it contains all necessary context from the failure analysis.",
            "   - If REGENERATE_PATCHES for a TEST_FAILURE: The prompt should instruct an Architect to create new patches. It MUST include specific details about the test failure and the original patches. Crucially, include the '[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS' string at the end of the prompt.",
            "     Example: '[CORRECTION TASK - TEST] Original Objective: <obj>. Test Failure: <test_out>. Regenerate patches for <files> to pass tests. Previous patches: <patches_json>.\\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS'",
            "   - If REGENERATE_PATCHES for other errors (e.g. SYNTAX_ERROR): The prompt should instruct an Architect to create new patches, considering the error.",
            "     Example: '[CORRECTION TASK - SYNTAX] Original Objective: <obj>. Error: <err>. Fix the syntax in the previous patches: <patches_json>.'",
            "   - If NEW_OBJECTIVE: The prompt should be a new, refined objective that considers the failure. It might be for an ObjectiveGenerator.",
            "     Example: '[REVISED OBJECTIVE - LOGIC] Original: <obj>. Failure: <reason>. New approach: Develop a simpler solution for X before attempting Y.'",
            "   - If RETRY_WITH_MODIFICATION: The prompt should be a modification of the original objective, perhaps with specific guidance.",
            "     Example: '[MODIFIED OBJECTIVE - TOOL] Original: <obj>. Tool Error: <err>. Retry objective, ensuring tool X is called with parameter Y.'",
            "   - If FIX_CONFIGURATION: The prompt should suggest how to fix a configuration issue.",
            "     Example: '[CONFIGURATION FIX] The tool X failed. The configuration file Y seems to be missing parameter Z. Update file Y.'",
            "   - If LOG_FOR_REVIEW: The prompt can be a summary of the issue for logging.",
            "     Example: 'Failure during <obj> due to <reason>. Analysis: <your analysis>. Recommended for manual review.'",
            "4. Provide brief 'details' explaining your reasoning.",
            "\n[REQUIRED OUTPUT FORMAT - JSON ONLY]",
            "{",
            "  \"classification\": \"<Your chosen classification>\",",
            "  \"suggestion_type\": \"<Your chosen suggestion type>\",",
            "  \"suggested_prompt\": \"<Your generated prompt for the next AI action>\",",
            "  \"details\": \"<Your brief reasoning/analysis>\"",
            "}"
        ])

        prompt = "\n".join(prompt_parts)
        self.logger.debug(f"ErrorAnalysisAgent: Prompt for LLM:\n{prompt}")

        raw_response, error = await call_llm_api( # Changed to await
            self.api_key, self.model, prompt, temperature=0.3, base_url=self.base_url, logger=self.logger
        )

        if error:
            self.logger.error(f"ErrorAnalysisAgent: LLM API call failed: {error}")
            return {
                "classification": "UNKNOWN_ERROR",
                "suggestion_type": "LOG_FOR_REVIEW",
                "suggested_prompt": f"ErrorAnalysisAgent failed to get analysis from LLM for objective: {failed_objective}. LLM Error: {error}",
                "details": "LLM call failed during error analysis.",
            }

        if not raw_response:
            self.logger.error("ErrorAnalysisAgent: Received empty response from LLM.")
            return {
                "classification": "UNKNOWN_ERROR",
                "suggestion_type": "LOG_FOR_REVIEW",
                "suggested_prompt": f"ErrorAnalysisAgent received empty response from LLM for objective: {failed_objective}.",
                "details": "Empty response from LLM during error analysis.",
            }

        try:
            # Attempt to parse the LLM response, expecting it to be a JSON string.
            parsed_response = json.loads(raw_response)

            required_keys = ["classification", "suggestion_type", "suggested_prompt", "details"]
            if not all(key in parsed_response for key in required_keys):
                self.logger.error(f"ErrorAnalysisAgent: LLM response missing required keys. Response: {raw_response}")
                # Still try to return what we have, but log the error.
                # Or, raise an error to be handled by a more generic fallback.
                # For now, let's create a fallback structure but include the problematic response.
                return {
                    "classification": parsed_response.get("classification", "UNKNOWN_ERROR_PARSING"),
                    "suggestion_type": parsed_response.get("suggestion_type", "LOG_FOR_REVIEW"),
                    "suggested_prompt": parsed_response.get("suggested_prompt", f"ErrorAnalysisAgent: LLM response missing keys. Raw: {raw_response[:1000]}"),
                    "details": parsed_response.get("details", f"LLM response parsing error: missing keys. Original response: {raw_response[:500]}...")
                }

            self.logger.info(f"ErrorAnalysisAgent: Analysis complete. Classification: {parsed_response.get('classification')}, Suggestion: {parsed_response.get('suggestion_type')}")
            return parsed_response
        except json.JSONDecodeError as e:
            self.logger.error(f"ErrorAnalysisAgent: Failed to parse LLM JSON response: {e}. Response was: {raw_response}")

            classification_guess = "UNKNOWN_ERROR"
            suggestion_type_guess = "LOG_FOR_REVIEW"

            class_match = re.search(r'"classification":\s*"([^"]+)"', raw_response, re.IGNORECASE)
            if class_match:
                classification_guess = class_match.group(1)

            sugg_match = re.search(r'"suggestion_type":\s*"([^"]+)"', raw_response, re.IGNORECASE)
            if sugg_match:
                suggestion_type_guess = sugg_match.group(1)

            return {
                "classification": classification_guess,
                "suggestion_type": suggestion_type_guess,
                "suggested_prompt": f"ErrorAnalysisAgent failed to parse LLM response for objective: {failed_objective}. Raw response: {raw_response[:1000]}",
                "details": f"Failed to parse LLM JSON response. Original response: {raw_response[:500]}...",
            }

import os # For example usage, to fetch API key from env
import asyncio # For running async test functions

# Example Usage (for testing purposes, normally called by CycleRunner)
async def main_test(): # Renamed and made async
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ErrorAnalysisAgentTest")

    mock_api_key = os.getenv("OPENROUTER_API_KEY", "test_api_key_not_set")
    mock_model = "deepseek/deepseek-chat-v3-0324:free" # A real free model

    if mock_api_key == "test_api_key_not_set":
        logger.warning("OPENROUTER_API_KEY not set. LLM calls in test will likely fail or use fallbacks.")

    analyzer = ErrorAnalysisAgent(api_key=mock_api_key, model=mock_model, logger=logger)

    syntax_error_analysis = await analyzer.analyze_error( # await here
        failed_objective="Implement feature X by modifying file Y.py",
        error_reason="SYNTAX_VALIDATION_FAILED",
        error_context="SyntaxError: invalid syntax on line 42 of Y.py",
        original_patches='[{"file_path": "Y.py", "operation": "REPLACE", "content": "def func():\\n print(\\"hello\\")\\n print oops"}]',
        failed_code_snippet="print oops"
    )
    logger.info(f"Syntax Error Analysis Result: {json.dumps(syntax_error_analysis, indent=2)}")

    test_failure_analysis = await analyzer.analyze_error( # await here
        failed_objective="Refactor module Z to improve performance.",
        error_reason="PYTEST_FAILURE",
        error_context="AssertionError: assert False == True",
        original_patches='[{"file_path": "Z.py", "operation": "REPLACE", "content": "def optimized_func():\\n  return False"}]',
        test_output="===== TestZ.test_optimized_func FAILED =====\\nAssertionError: assert optimized_func() == True"
    )
    logger.info(f"Test Failure Analysis Result: {json.dumps(test_failure_analysis, indent=2)}")

    logic_error_analysis = await analyzer.analyze_error( # await here
        failed_objective="Integrate API A with service B.",
        error_reason="REGRESSION_DETECTED_BY_MANUAL_CHECK",
        error_context="After applying patches, service B returns 500 error when called with data from API A. Expected 200 OK.",
        original_patches='[{"file_path": "integration_module.py", "operation": "INSERT", "content": "call_service_b(transform(data_from_a))"}]'
    )
    logger.info(f"Logic Error Analysis Result: {json.dumps(logic_error_analysis, indent=2)}")

    unknown_error_analysis = await analyzer.analyze_error( # await here
        failed_objective="Deploy application to staging.",
        error_reason="UNEXPECTED_TOOL_FAILURE",
        error_context="Tool 'deploy_script.sh' exited with code 127. No further logs."
    )
    logger.info(f"Unknown Error Analysis Result: {json.dumps(unknown_error_analysis, indent=2)}")

if __name__ == '__main__':
    asyncio.run(main_test())
