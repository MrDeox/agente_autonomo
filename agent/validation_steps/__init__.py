import logging
from typing import Tuple, List, Dict, Any
from pathlib import Path

from .base import ValidationStep
from .patch_applicator import PatchApplicatorStep
from .pytest_validator import PytestValidator
from .syntax_validator import SyntaxValidator
from .pytest_new_file_validator import PytestNewFileValidator
from agent.code_validator import validate_json_syntax

# Placeholder for BenchmarkValidator (if not yet implemented)
class BenchmarkValidator(ValidationStep):
    def execute(self) -> Tuple[bool, str, str]:
        self.logger.info("Benchmark validation skipped (placeholder).")
        return True, "BENCHMARK_SKIPPED", "Benchmark validation is a placeholder."

# Placeholder for CheckFileExistenceValidator (if not yet implemented)
class CheckFileExistenceValidator(ValidationStep):
    def execute(self) -> Tuple[bool, str, str]:
        self.logger.info("File existence check skipped (placeholder).")
        return True, "FILE_EXISTENCE_CHECK_SKIPPED", "File existence check is a placeholder."

class ValidateJsonSyntax(ValidationStep):
    """Validates the syntax of JSON files mentioned in patches."""
    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    def execute(self) -> Tuple[bool, str, str]:
        if not self.patches_to_apply:
            self.logger.info("No patches applied to validate JSON syntax. Skipping.")
            return True, "JSON_SYNTAX_VALIDATION_SKIPPED", "No patches to validate."

        self.logger.info(f"Starting JSON syntax validation in: {self.base_path}")
        all_syntax_valid = True
        error_details = []
        files_to_validate = {p.get("file_path") for p in self.patches_to_apply if p.get("file_path")}

        for file_path_relative in files_to_validate:
            if not file_path_relative or not file_path_relative.endswith(".json"):
                continue

            full_file_path_in_target = Path(self.base_path) / file_path_relative
            self.logger.debug(f"Validating JSON syntax of: {full_file_path_in_target}")

            if not full_file_path_in_target.exists():
                self.logger.warning(f"File {full_file_path_in_target} not found in '{self.base_path}' for JSON validation.")
                continue
            
            is_valid, msg = validate_json_syntax(full_file_path_in_target, self.logger)
            if not is_valid:
                self.logger.warning(
                    f"JSON syntax error in {full_file_path_in_target}: {msg}"
                )
                all_syntax_valid = False
                error_details.append(f"{file_path_relative}: {msg}")

        if not all_syntax_valid:
            reason_code = "JSON_SYNTAX_VALIDATION_FAILED_IN_SANDBOX" if self.use_sandbox else "JSON_SYNTAX_VALIDATION_FAILED"
            return False, reason_code, "\n".join(error_details)

        self.logger.info(f"JSON syntax validation in '{self.base_path}': SUCCESS.")
        return True, "JSON_SYNTAX_VALIDATION_SUCCESS", "All JSON files passed syntax validation."

validation_steps = {
    "ValidationStep": ValidationStep,
    "PatchApplicatorStep": PatchApplicatorStep,
    "PytestValidator": PytestValidator,
    "SyntaxValidator": SyntaxValidator,
    "PytestNewFileValidator": PytestNewFileValidator,
    "validate_syntax": SyntaxValidator,
    "run_pytest": PytestValidator,
    "run_pytest_new_file": PytestNewFileValidator,
    "run_benchmark_validation": BenchmarkValidator, # Added mapping
    "check_file_existence": CheckFileExistenceValidator, # Added mapping
    "validate_json_syntax": ValidateJsonSyntax, # Added mapping
    "ValidateJsonSyntax": ValidateJsonSyntax, # Added exact mapping for class name
    "apply_patches_to_disk": PatchApplicatorStep # Added explicit mapping
}

def get_validation_step(name: str) -> ValidationStep:
    return validation_steps[name]

__all__ = [
    "ValidationStep",
    "PatchApplicatorStep",
    "PytestValidator",
    "SyntaxValidator",
    "PytestNewFileValidator",
    "get_validation_step",
    "BenchmarkValidator",
    "CheckFileExistenceValidator",
    "ValidateJsonSyntax"
]