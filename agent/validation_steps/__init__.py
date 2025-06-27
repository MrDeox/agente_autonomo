
from typing import Type

from agent.validation_steps.base import ValidationStep
from agent.validation_steps.pytest_validator import PytestValidator
from agent.validation_steps.syntax_validator import SyntaxValidator
from agent.validation_steps.patch_applicator import PatchApplicator

def get_validation_step(step_name: str) -> Type[ValidationStep]:
    """Returns the validation step class for the given step name."""
    if step_name == "run_pytest_validation":
        return PytestValidator
    elif step_name == "validate_syntax":
        return SyntaxValidator
    elif step_name == "apply_patches_to_disk":
        return PatchApplicator
    else:
        raise ValueError(f"Unknown validation step: {step_name}")
