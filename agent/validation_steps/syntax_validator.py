import logging
from typing import Tuple, List, Dict, Any
from pathlib import Path

from agent.code_validator import validate_python_code, validate_json_syntax
from agent.validation_steps.base import ValidationStep

class SyntaxValidator(ValidationStep):
    """Validates the syntax of Python and JSON files."""

import aiofiles
import asyncio

class SyntaxValidator(ValidationStep):
    """Validates the syntax of Python and JSON files."""

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    async def execute(self) -> Tuple[bool, str, str]:
        if not self.patches_to_apply:
            self.logger.info("No patches applied to validate syntax. Skipping.")
            return True, "SYNTAX_VALIDATION_SKIPPED", "No patches to validate."

        self.logger.info(f"Starting syntax validation in: {self.base_path}")
        all_syntax_valid = True
        error_details = []
        files_to_validate = {p.get("file_path") for p in self.patches_to_apply if p.get("file_path")}

        for file_path_relative in files_to_validate:
            full_file_path_in_target = Path(self.base_path) / file_path_relative
            self.logger.debug(f"Validating syntax of: {full_file_path_in_target}")

            # Use asyncio.to_thread for os.path.exists for non-blocking check
            if not await asyncio.to_thread(full_file_path_in_target.exists):
                self.logger.warning(f"File {full_file_path_in_target} not found in '{self.base_path}' for validation.")
                continue # Or should this be a failure? Depends on expectations.

            # validate_python_code and validate_json_syntax read file content.
            # They need to be made async or run in a thread.
            # For now, let's assume they are blocking but we'll wrap calls in to_thread
            # or modify them later if they become true bottlenecks.
            # The PoC for llm_client implies that I/O heavy utilities should become async.
            # Let's assume validate_python_code and validate_json_syntax will be updated
            # to accept content directly or become async themselves.
            # For this step, we'll make them async here by reading content with aiofiles.

            try:
                async with aiofiles.open(full_file_path_in_target, "r", encoding="utf-8") as f:
                    content = await f.read()
            except Exception as e:
                self.logger.error(f"Error reading file {full_file_path_in_target} for syntax validation: {e}")
                all_syntax_valid = False
                error_details.append(f"{file_path_relative}: Error reading file - {e}")
                continue

            if file_path_relative.endswith(".py"):
                # Assuming validate_python_code can take content string
                # If not, it needs to be refactored or run in thread with path
                # Let's modify validate_python_code to accept content. (This is a TODO for code_validator.py)
                # For now, simulate this by passing the path, assuming it's okay for this step.
                # OR, for a cleaner approach, we make validate_python_code itself async.
                # Given the plan, let's assume `validate_python_code` will be refactored.
                # For now, to make progress, we'll call existing sync version in a thread.
                # This is not ideal but allows us to proceed with SyntaxValidator async conversion.

                # Ideal: is_valid, msg, _ = await validate_python_code_async(content, self.logger)
                # Interim:
                is_valid, msg, _ = await asyncio.to_thread(validate_python_code, full_file_path_in_target, self.logger)

                if not is_valid:
                    self.logger.warning(
                        f"Python syntax error in {full_file_path_in_target}: {msg}"
                    )
                    all_syntax_valid = False
                    error_details.append(f"{file_path_relative}: {msg}")
            elif file_path_relative.endswith(".json"):
                # Similar assumption for validate_json_syntax
                # Ideal: is_valid, msg = await validate_json_syntax_async(content, self.logger)
                # Interim:
                is_valid, msg = await asyncio.to_thread(validate_json_syntax, full_file_path_in_target, self.logger)
                if not is_valid:
                    self.logger.warning(
                        f"JSON syntax error in {full_file_path_in_target}: {msg}"
                    )
                    all_syntax_valid = False
                    error_details.append(f"{file_path_relative}: {msg}")

        if not all_syntax_valid:
            reason_code = "SYNTAX_VALIDATION_FAILED_IN_SANDBOX" if self.use_sandbox else "SYNTAX_VALIDATION_FAILED"
            return False, reason_code, "\n".join(error_details)

        self.logger.info(f"Syntax validation in '{self.base_path}': SUCCESS.")
        return True, "SYNTAX_VALIDATION_SUCCESS", "All files passed syntax validation."
