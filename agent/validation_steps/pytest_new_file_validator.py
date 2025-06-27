import logging
import subprocess
from typing import Tuple, List, Dict, Any
from pathlib import Path
from agent.validation_steps.base import ValidationStep

class PytestNewFileValidator(ValidationStep):
    """
    A validation step that runs pytest specifically on newly created test files.
    Assumes that the patch details for the new test file are provided.
    """

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    def execute(self) -> Tuple[bool, str, str]:
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
        # For simplicity in this step, we'll check if the file exists.
        # In a full flow, a 'sandbox_patch_applicator' step would precede this.

        # Let's assume the file content from the patch needs to be written temporarily if not already handled.
        # This is a simplified approach. A dedicated sandbox applicator step is better.
        temp_file_written = False
        if not target_file_path.exists():
            try:
                self.logger.info(f"Test file {target_file_path} does not exist. Attempting to write from patch content for validation.")
                target_file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(target_file_path, "w", encoding="utf-8") as f:
                    f.write(patch_detail.get("content", ""))
                temp_file_written = True
                self.logger.info(f"Temporarily wrote content of {new_file_path_str} for pytest validation.")
            except Exception as e:
                self.logger.error(f"Error temporarily writing new test file {new_file_path_str} for validation: {e}")
                return False, "TEMP_WRITE_ERROR", f"Could not write temporary file for validation: {e}"

        self.logger.info(f"Running pytest on new file: {target_file_path}")
        try:
            # Ensure a conftest.py is picked up if it exists in the root or tests directory
            # Running pytest from the project root (self.base_path)
            process = subprocess.run(
                ["pytest", str(target_file_path)],
                cwd=self.base_path, # Run pytest from the project root
                capture_output=True,
                text=True,
                timeout=60  # 60-second timeout
            )

            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            if process.returncode == 0:
                self.logger.info(f"Pytest passed for new file {new_file_path_str}.\nSTDOUT:\n{stdout}")
                if temp_file_written: target_file_path.unlink(missing_ok=True)
                return True, "PYTEST_PASSED", f"Pytest passed for {new_file_path_str}.\n{stdout}"
            else:
                # Pytest exit codes:
                # 0: All tests passed
                # 1: Tests were collected and run but some tests failed
                # 2: Test execution was interrupted by the user
                # 3: Internal error happened while executing tests
                # 4: pytest command line usage error
                # 5: No tests were collected
                # We consider exit code 5 (no tests collected) as a failure here,
                # because we expect the generated file to have runnable placeholder tests.
                self.logger.error(f"Pytest failed for new file {new_file_path_str}. Return code: {process.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
                if temp_file_written: target_file_path.unlink(missing_ok=True)
                return False, "PYTEST_FAILED", f"Pytest failed for {new_file_path_str} (exit code {process.returncode}).\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"

        except subprocess.TimeoutExpired:
            self.logger.error(f"Pytest timed out for new file {new_file_path_str}.")
            if temp_file_written: target_file_path.unlink(missing_ok=True)
            return False, "PYTEST_TIMEOUT", f"Pytest timed out for {new_file_path_str}."
        except Exception as e:
            self.logger.error(f"Error running pytest for new file {new_file_path_str}: {e}", exc_info=True)
            if temp_file_written: target_file_path.unlink(missing_ok=True)
            return False, "PYTEST_EXECUTION_ERROR", f"Error running pytest on {new_file_path_str}: {e}"
