import logging
import json # For parsing LLM response and example usage
import re # For fallback parsing of LLM response
from typing import Optional, Dict, Any, Tuple

from agent.utils.llm_client import call_llm_api

class ErrorAnalysisAgent:
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger

    def analyze_error(
        self,
        failed_objective: str,
        error_reason: str,
        error_context: str,
        original_patches: Optional[str] = None,
        failed_code_snippet: Optional[str] = None,
        test_output: Optional[str] = None,
        capabilities_content: Optional[str] = None,
        roadmap_content: Optional[str] = None
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

        if capabilities_content:
            prompt_parts.extend(["\n[CAPABILITIES DOCUMENT (CAPABILITIES.md)]", capabilities_content])

        if roadmap_content:
            prompt_parts.extend(["\n[ROADMAP DOCUMENT (ROADMAP.md)]", roadmap_content])

        prompt_parts.extend([
            "\n[YOUR TASK]",
            "1. Classify the error. Choose one from: SYNTAX_ERROR, TEST_FAILURE, LOGIC_ERROR, CONFIGURATION_ERROR, TOOL_ERROR, UNKNOWN_ERROR.",
            "2. Based on the classification and details, determine the best suggestion type. Choose one from: REGENERATE_PATCHES, NEW_OBJECTIVE, RETRY_WITH_MODIFICATION, LOG_FOR_REVIEW, FIX_CONFIGURATION.",
            "3. Generate a 'suggested_prompt' for the AI agent's next action. This prompt MUST be directly usable by another AI agent (like an Architect or Objective Generator) to implement the fix or new approach. Ensure it contains all necessary context from the failure analysis. Consider the strategic documents (Capabilities, Roadmap) if the failure suggests a deeper issue than a simple code error.",
            "   - If REGENERATE_PATCHES for a TEST_FAILURE: The prompt should instruct an Architect to create new patches. It MUST include specific details about the test failure and the original patches. Crucially, include the '[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS' string at the end of the prompt.",            "     Example: '[CORRECTION TASK - TEST] Original Objective: <obj>. Test Failure: <test_out>. Regenerate patches for <files> to pass tests. Previous patches: <patches_json>.\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS'",
            "   - If REGENERATE_PATCHES for other errors (e.g. SYNTAX_ERROR): The prompt should instruct an Architect to create new patches, considering the error.",            "     Example: '[CORRECTION TASK - SYNTAX] Original Objective: <obj>. Error: <err>. Fix the syntax in the previous patches: <patches_json>.'",
            "   - If NEW_OBJECTIVE (especially for LOGIC_ERROR, or repeated failures): The prompt should be a new, refined objective. This is a key opportunity for RSI.",
            "     - If the failure indicates a missing capability (refer to [CAPABILITIES DOCUMENT]):",
            "       Example: '[CAPABILITY GAP] The objective \"<failed_objective>\" failed due to missing capability ''<Capability Name>''. Propose a capacitation objective to implement this capability as described in CAPABILITIES.md.'",
            "     - If the failure suggests a problem with an agent's prompt or a strategy (refer to [PERFORMANCE ANALYSIS] if available in context):",
            "       Example: '[PROCESS IMPROVEMENT - PROMPT] The ArchitectAgent''s patches for objectives like \"<failed_objective>\" often result in <type_of_error>. Propose an objective to analyze and refine the ArchitectAgent''s main prompt to mitigate this.'",
            "       Example: '[PROCESS IMPROVEMENT - STRATEGY] The validation strategy ''<strategy_name>'' used for \"<failed_objective>\" was insufficient. Propose an objective to review and enhance this strategy in `hephaestus_config.json` or create a new one.'",
            "     - For general logic errors or if a simpler approach is needed:",
            "       Example: '[REVISED OBJECTIVE - LOGIC] Original: <obj>. Failure: <reason>. New approach: Develop a simpler solution for X before attempting Y.'",
            "     - For deeper, systemic issues or repeated unexplained failures (Meta-Analysis):",
            "       Example: '[META-ANALYSIS OBJECTIVE] The objective \"<failed_objective>\" failed repeatedly due to \"<error_reason>\". Analyze if the objective itself was flawed, if a core assumption was wrong, or if a fundamental agent capability is lacking. Propose a new, strategic objective to address the root cause.'",
            "   - If RETRY_WITH_MODIFICATION: The prompt should be a modification of the original objective, perhaps with specific guidance.",            "     Example: '[MODIFIED OBJECTIVE - TOOL] Original: <obj>. Tool Error: <err>. Retry objective, ensuring tool X is called with parameter Y.'",
            "   - If FIX_CONFIGURATION: The prompt should suggest how to fix a configuration issue.",            "     Example: '[CONFIGURATION FIX] The tool X failed. The configuration file Y seems to be missing parameter Z. Update file Y.'",
            "   - If LOG_FOR_REVIEW: The prompt can be a summary of the issue for logging.",            "     Example: 'Failure during <obj> due to <reason>. Analysis: <your analysis>. Recommended for manual review.'",
            "4. Provide brief 'details' explaining your reasoning, especially if proposing a NEW_OBJECTIVE that deviates significantly from a simple fix.",
            "\n[REQUIRED OUTPUT FORMAT - JSON ONLY]",
            "{",

            "3. Generate a 'suggested_prompt' for the AI agent's next action. This prompt MUST be directly usable by another AI agent (like an Architect or Objective Generator) to implement the fix or new approach. Ensure it contains all necessary context from the failure analysis.",
            "   - If REGENERATE_PATCHES for a TEST_FAILURE: The prompt should instruct an Architect to create new patches. It MUST include specific details about the test failure and the original patches. Crucially, include the '[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS' string at the end of the prompt.",            "     Example: '[CORRECTION TASK - TEST] Original Objective: <obj>. Test Failure: <test_out>. Regenerate patches for <files> to pass tests. Previous patches: <patches_json>.\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS'",            "   - If REGENERATE_PATCHES for other errors (e.g. SYNTAX_ERROR): The prompt should instruct an Architect to create new patches, considering the error.",            "     Example: '[CORRECTION TASK - SYNTAX] Original Objective: <obj>. Error: <err>. Fix the syntax in the previous patches: <patches_json>.'",            "   - If NEW_OBJECTIVE: The prompt should be a new, refined objective that considers the failure. It might be for an ObjectiveGenerator.",            "     Example: '[REVISED OBJECTIVE - LOGIC] Original: <obj>. Failure: <reason>. New approach: Develop a simpler solution for X before attempting Y.'",            "     Example: '[META-ANALYSIS OBJECTIVE] The objective \"<failed_objective>\" failed repeatedly due to \"<error_reason>\". Analyze if the objective itself was flawed or if the chosen strategy was inappropriate. Propose a new, more strategic objective to address the root cause.'",            "   - If RETRY_WITH_MODIFICATION: The prompt should be a modification of the original objective, perhaps with specific guidance.",            "     Example: '[MODIFIED OBJECTIVE - TOOL] Original: <obj>. Tool Error: <err>. Retry objective, ensuring tool X is called with parameter Y.'",            "   - If FIX_CONFIGURATION: The prompt should suggest how to fix a configuration issue.",            "     Example: '[CONFIGURATION FIX] The tool X failed. The configuration file Y seems to be missing parameter Z. Update file Y.'",            "   - If LOG_FOR_REVIEW: The prompt can be a summary of the issue for logging.",            "     Example: 'Failure during <obj> due to <reason>. Analysis: <your analysis>. Recommended for manual review.'",            "4. Provide brief 'details' explaining your reasoning.",            "\n[REQUIRED OUTPUT FORMAT - JSON ONLY]",            "{",            "  \"classification\": \"<Your chosen classification>\",",            "  \"suggestion_type\": \"<Your chosen suggestion type>\",",            "  \"suggested_prompt\": \"<Your generated prompt for the next AI action>\",",            "  \"details\": \"<Your brief reasoning/analysis>\"",            "}"        ])

        prompt = "\n".join(prompt_parts)
        self.logger.debug(f"ErrorAnalysisAgent: Prompt for LLM:\n{prompt}")

        raw_response, error = call_llm_api(
            model_config=self.model_config, prompt=prompt, temperature=0.3, logger=self.logger
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

# Example Usage (for testing purposes, normally called by CycleRunner)
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("ErrorAnalysisAgentTest")

    # This test block needs to be updated to reflect the new model_config structure
    # For now, we'll just create a dummy config for testing.
    mock_model_config = {
        "primary": "gemini/gemini-2.5-pro",
        "fallback": "deepseek/deepseek-chat-v3-0324:free"
    }

    analyzer = ErrorAnalysisAgent(model_config=mock_model_config, logger=logger)

    syntax_error_analysis = analyzer.analyze_error(
        failed_objective="Implement feature X by modifying file Y.py",
        error_reason="SYNTAX_VALIDATION_FAILED",
        error_context="SyntaxError: invalid syntax on line 42 of Y.py",
        original_patches='[{"file_path": "Y.py", "operation": "REPLACE", "content": "def func():\\n print(\\"hello\\")\\n print oops"}]',
        failed_code_snippet="print oops"
    )
    logger.info(f"Syntax Error Analysis Result: {json.dumps(syntax_error_analysis, indent=2)}")

    test_failure_analysis = analyzer.analyze_error(
        failed_objective="Refactor module Z to improve performance.",
        error_reason="PYTEST_FAILURE",
        error_context="AssertionError: assert False == True",
        original_patches='[{"file_path": "Z.py", "operation": "REPLACE", "content": "def optimized_func():\\n  return False"}]',
        test_output="===== TestZ.test_optimized_func FAILED =====\\nAssertionError: assert optimized_func() == True"
    )
    logger.info(f"Test Failure Analysis Result: {json.dumps(test_failure_analysis, indent=2)}")

    logic_error_analysis = analyzer.analyze_error(
        failed_objective="Integrate API A with service B.",
        error_reason="REGRESSION_DETECTED_BY_MANUAL_CHECK",
        error_context="After applying patches, service B returns 500 error when called with data from API A. Expected 200 OK.",
        original_patches='[{"file_path": "integration_module.py", "operation": "INSERT", "content": "call_service_b(transform(data_from_a))"}]'
    )
    logger.info(f"Logic Error Analysis Result: {json.dumps(logic_error_analysis, indent=2)}")

    unknown_error_analysis = analyzer.analyze_error(
        failed_objective="Deploy application to staging.",
        error_reason="UNEXPECTED_TOOL_FAILURE",
        error_context="Tool 'deploy_script.sh' exited with code 127. No further logs."
    )
    logger.info(f"Unknown Error Analysis Result: {json.dumps(unknown_error_analysis, indent=2)}")
import os # For example usage, to fetch API key from env
# The os import was missing for the __main__ block. Adding it to the create_file_with_block content.
# The __main__ block also uses json.dumps, so json import is necessary.
# And re for the fallback.
# All these are now at the top of the file content for `create_file_with_block`.
# The plan step is to "Define `ErrorAnalysisAgent`". This includes:
# 1. Create `agent/error_analyzer.py`
# 2. Implement the `ErrorAnalysisAgent` class.
# The code provided does this.
# I'll also create/update `agent/__init__.py` to make the new agent accessible.
