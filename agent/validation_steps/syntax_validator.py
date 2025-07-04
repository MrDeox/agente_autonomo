import logging
from typing import Tuple, List, Dict, Any
from pathlib import Path

from agent.code_validator import validate_python_code, validate_json_syntax
from agent.validation_steps.base import ValidationStep

class SyntaxValidator(ValidationStep):
    """Validates the syntax of Python and JSON files."""

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    def execute(self) -> Tuple[bool, str, str]:
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from agent.config_loader import load_config

def validate_config_structure(config: dict) -> bool:
    """Valida a estrutura do hephaestus_config.json contra um esquema definido."""
    try:
        schema = load_config('validation_strategies/main.yaml')['json_structure_schema']
        validate(instance=config, schema=schema)
        return True
    except ValidationError as e:
        logger.error(f"Validação de estrutura JSON falhou: {e}")
        return False
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

            if not full_file_path_in_target.exists():
                self.logger.warning(f"File {full_file_path_in_target} not found in '{self.base_path}' for validation.")
                continue

            if file_path_relative.endswith(".py"):
                is_valid, msg, _ = validate_python_code(full_file_path_in_target, self.logger)
                if not is_valid:
                    self.logger.warning(
                        f"Python syntax error in {full_file_path_in_target}: {msg}"
                    )
                    all_syntax_valid = False
                    error_details.append(f"{file_path_relative}: {msg}")
            elif file_path_relative.endswith(".json"):
                is_valid, msg = validate_json_syntax(full_file_path_in_target, self.logger)
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