
import logging
from typing import Tuple, List, Dict, Any

from agent.patch_applicator import apply_patches
from agent.validation_steps.base import ValidationStep

class PatchApplicatorStep(ValidationStep):
    """Applies patches to the specified base path."""

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    def execute(self) -> Tuple[bool, str, str]:
        if not self.patches_to_apply:
            self.logger.info("No patches to apply. Skipping.")
            return True, "PATCH_APPLICATION_SKIPPED", "No patches to apply."

        self.logger.info(f"Applying {len(self.patches_to_apply)} patches in '{self.base_path}'...")
        try:
            apply_patches(instructions=self.patches_to_apply, logger=self.logger, base_path=self.base_path)
            self.logger.info(f"Patches applied successfully in '{self.base_path}'.")
            return True, "PATCH_APPLICATION_SUCCESS", "Patches applied successfully."
        except Exception as e:
            self.logger.error(f"CRITICAL ERROR applying patches in '{self.base_path}': {e}", exc_info=True)
            reason_code = "PATCH_APPLICATION_FAILED_IN_SANDBOX" if self.use_sandbox else "PATCH_APPLICATION_FAILED"
            return False, reason_code, str(e)