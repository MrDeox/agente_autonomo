import logging
from typing import Optional, Dict, Any, Tuple

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response

class CodeReviewAgent:
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger

    def review_patches(self, patches_to_apply: list[dict]) -> Tuple[bool, str]:
        """
        Reviews a list of patches for code quality, style, and potential bugs.

        Args:
            patches_to_apply: The list of patch instructions from the Architect.

        Returns:
            A tuple containing:
            - bool: True if the review passed, False otherwise.
            - str: A string with feedback and suggestions if the review failed, or "OK" if it passed.
        """
        if not patches_to_apply:
            return True, "No patches to review."

        patches_str = "\n".join([f"--- PATCH FOR {p.get('file_path')} ---\n{p.get('content', '')}\n" for p in patches_to_apply])

        prompt = f"""
[IDENTITY]
You are an expert Senior Software Engineer performing a code review. Your standards are high, but your goal is to be helpful and constructive.

[TASK]
Review the following code patches. Your review should focus on:
1. **Code Quality:** Is the code clean, readable, and maintainable?
2. **Correctness:** Are there any obvious logic errors, bugs, or anti-patterns?
3. **Best Practices:** Does the code follow standard Python conventions (PEP 8)?
4. **Security:** Are there any potential security vulnerabilities?

[CODE PATCHES TO REVIEW]
{patches_str}

[YOUR DECISION]
Respond ONLY with a JSON object in the following format:
{{
  "review_passed": boolean,
  "feedback": "If the review failed, provide a CONCISE and ACTIONABLE list of required changes. If it passed, write 'OK'."
}}

Example of FAILED review feedback:
"1. The function `my_func` should be split into smaller functions to reduce complexity.
 2. Add docstrings explaining the purpose of the `process_data` function.
 3. The variable `x` is too generic; rename it to `user_id` for clarity."

Example of PASSED review:
"OK"
"""
        self.logger.info(f"CodeReviewAgent: Reviewing {len(patches_to_apply)} patches...")
        raw_response, error = call_llm_api(self.model_config, prompt, 0.2, self.logger)

        if error:
            self.logger.error(f"CodeReviewAgent: API call failed: {error}")
            return False, f"API call failed: {error}"

        if not raw_response:
            self.logger.error("CodeReviewAgent: Received empty response from LLM.")
            return False, "Received empty response from LLM."

        parsed, error = parse_json_response(raw_response, self.logger)
        if error or not isinstance(parsed, dict):
            self.logger.error(f"CodeReviewAgent: Failed to parse review response: {error or 'Invalid format'}")
            return False, f"Failed to parse review response: {raw_response}"

        review_passed = parsed.get("review_passed", False)
        feedback = parsed.get("feedback", "No feedback provided.")

        if not review_passed:
            self.logger.warning(f"CodeReviewAgent: Review FAILED. Feedback: {feedback}")
        else:
            self.logger.info("CodeReviewAgent: Review PASSED.")
            
        return review_passed, feedback 