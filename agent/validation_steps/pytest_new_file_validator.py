import logging
import asyncio # Changed from subprocess to asyncio
from typing import Tuple, List, Dict, Any
from pathlib import Path
from agent.validation_steps.base import ValidationStep
from agent.tool_executor import run_pytest # Import the async version

class PytestNewFileValidator(ValidationStep):
    """
    A validation step that runs pytest specifically on newly created test files.
    Assumes that the patch details for the new test file are provided.
    """

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    async def execute(self) -> Tuple[bool, str, str]:
        """
        Executes pytest on the new test file specified in patches_to_apply.

        Expects one patch that creates a new test file.
        The file_path of this new test file will be used for pytest.
        """
        self.logger.info("Executing PytestNewFileValidator...")

        new_test_files_patches = [
            p for p in self.patches_to_apply
            if p.get("operation") == "REPLACE" and p.get("block_to_replace") is None and \
               (p.get("file_path", "").startswith("tests/") or "test" in p.get("file_path", ""))
        ]

        if not new_test_files_patches:
            return False, "NO_NEW_TEST_FILE_PATCH", "No patch found for creating a new test file."

        if len(new_test_files_patches) > 1:
            self.logger.warning(f"Multiple new test file patches found: {[p['file_path'] for p in new_test_files_patches]}. Using the first one.")

        patch_detail = new_test_files_patches[0]
        new_file_path_str = patch_detail.get("file_path")

        if not new_file_path_str:
            return False, "MISSING_FILE_PATH", "New test file patch is missing 'file_path'."

        # Determine the actual path (sandbox or direct)
        # For this validator, we assume the file has been written to a temporary location or sandbox
        # by a previous step (like a specialized patch applicator for validation).
        # If running in a real environment, ensure the file exists at new_file_path_str relative to base_path.

        # For now, let's assume the patch applicator (or a prior validation step)
        # has already placed the file content in the correct location in the sandbox if use_sandbox is true.
        # The PatchApplicatorStep in a validation strategy would handle this.
        # This validator purely runs pytest on that path.

        target_file_path = Path(self.base_path) / new_file_path_str

        # We need to ensure the file is actually written before pytest can run on it.
        # This validator should run AFTER a step that applies the patch to a temporary/sandbox location.
        # The PatchApplicatorStep, when made async, will handle writing files using aiofiles.
        # This validator assumes the file exists at target_file_path.

        target_file_path = Path(self.base_path) / new_file_path_str

        # Check if the file exists (using asyncio.to_thread for os.path.exists)
        if not await asyncio.to_thread(target_file_path.exists):
            self.logger.error(f"New test file {target_file_path} does not exist. It should have been created by a previous step.")
            return False, "TEST_FILE_NOT_FOUND", f"Test file {new_file_path_str} not found in {self.base_path}."

        self.logger.info(f"Running pytest on new file: {target_file_path} (within CWD: {self.base_path})")

        # run_pytest now takes the specific file to test as an argument to pytest,
        # and cwd is the base_path.
        # The `test_dir` argument to `run_pytest` should be the specific file path relative to `cwd`.
        success, details = await run_pytest(test_dir=str(new_file_path_str), cwd=self.base_path)

        if not success:
            self.logger.error(
                f"Pytest failed for new file {new_file_path_str}. Details:\n{details}"
            )
            # The reason_code will be PYTEST_FAILURE_IN_SANDBOX or PYTEST_FAILURE from run_pytest
            return False, "PYTEST_NEW_FILE_FAILED", details

        self.logger.info(f"Pytest passed for new file {new_file_path_str}.")
        return True, "PYTEST_NEW_FILE_PASSED", f"Pytest passed for {new_file_path_str}.\n{details}"
