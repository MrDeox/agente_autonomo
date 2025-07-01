from typing import Tuple

from .base import ValidationStep
from .patch_applicator import PatchApplicatorStep
from .pytest_validator import PytestValidator
from .syntax_validator import SyntaxValidator
from .pytest_new_file_validator import PytestNewFileValidator

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

# Placeholder for ValidateJsonSyntax (if not yet implemented)
class ValidateJsonSyntax(ValidationStep):
    def execute(self) -> Tuple[bool, str, str]:
        self.logger.info("JSON syntax validation skipped (placeholder).")
        return True, "JSON_SYNTAX_SKIPPED", "JSON syntax validation is a placeholder."

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
