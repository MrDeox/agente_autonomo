
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
import logging
from pathlib import Path

class ValidationStep(ABC):
    """Abstract base class for a validation step."""

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        self.logger = logger
        self.base_path = base_path
        self.patches_to_apply = patches_to_apply
        self.use_sandbox = use_sandbox

    @abstractmethod
    def execute(self) -> Tuple[bool, str, str]:
        """
        Executes the validation step.

        Returns:
            A tuple containing:
            - bool: True if the validation succeeded, False otherwise.
            - str: A reason code for the result.
            - str: A detailed message about the result.
        """
        pass
