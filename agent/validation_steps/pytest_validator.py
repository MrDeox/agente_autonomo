
import logging
from typing import Tuple, List, Dict, Any

from agent.tool_executor import run_pytest
from agent.validation_steps.base import ValidationStep

class PytestValidator(ValidationStep):
    """Runs pytest as a validation step."""

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    async def execute(self) -> Tuple[bool, str, str]:
        self.logger.info(f"Executing Pytest in: {self.base_path}...")
        success, details = await run_pytest(test_dir='tests/', cwd=self.base_path)

        if not success:
            self.logger.warning(
                f"Pytest failed in '{self.base_path}': {details}"
            )
            reason_code = "PYTEST_FAILURE_IN_SANDBOX" if self.use_sandbox else "PYTEST_FAILURE"
            return False, reason_code, details

        self.logger.info(f"Pytest validation in '{self.base_path}': SUCCESS.")
        return True, "PYTEST_SUCCESS", "Pytest execution succeeded."
