from .base import ValidationStep
from .patch_applicator import PatchApplicatorStep
from .pytest_validator import PytestValidator
from .syntax_validator import SyntaxValidator
from .pytest_new_file_validator import PytestNewFileValidator

validation_steps = {
    "ValidationStep": ValidationStep,
    "PatchApplicatorStep": PatchApplicatorStep,
    "PytestValidator": PytestValidator,
    "SyntaxValidator": SyntaxValidator,
    "PytestNewFileValidator": PytestNewFileValidator,
    "validate_syntax": SyntaxValidator
}

def get_validation_step(name: str) -> ValidationStep:
    return validation_steps[name]

__all__ = [
    "ValidationStep",
    "PatchApplicatorStep",
    "PytestValidator",
    "SyntaxValidator",
    "PytestNewFileValidator",
    "get_validation_step"
]
