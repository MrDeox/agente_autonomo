import json
import logging
from jsonschema import validate, ValidationError
from typing import Tuple, List, Dict, Any
from pathlib import Path

from hephaestus.core.code_validator import validate_python_code, validate_json_syntax
from .base import ValidationStep
from hephaestus.utils.config_loader import load_config

def validate_config_structure(config: dict, logger: logging.Logger) -> bool:
    """Valida a estrutura do hephaestus_config.json contra um esquema definido."""
    try:
        # This assumes a schema is defined in the config. This might need to be created.
        schema = load_config().get('validation_strategies', {}).get('json_structure_schema', {})
        if not schema:
            logger.warning("No 'json_structure_schema' found in validation_strategies. Skipping structure validation.")
            return True
        validate(instance=config, schema=schema)
        return True
    except ValidationError as e:
        logger.error(f"Validação de estrutura JSON falhou: {e}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao validar estrutura do config: {e}", exc_info=True)
        return False

class SyntaxValidator(ValidationStep):
    """Validates the syntax of Python and JSON files."""

    def __init__(self, logger: logging.Logger, base_path: str, patches_to_apply: List[Dict[str, Any]], use_sandbox: bool):
        super().__init__(logger, base_path, patches_to_apply, use_sandbox)

    def execute(self) -> Tuple[bool, str, str]:
        if not self.patches_to_apply:
            self.logger.info("No patches applied to validate syntax. Skipping.")
            return True, "SYNTAX_VALIDATION_SKIPPED", "No patches to validate."

        self.logger.info(f"Starting syntax validation in: {self.base_path}")
        all_syntax_valid = True
        error_details = []
        files_to_validate = {p.get("file_path") for p in self.patches_to_apply if p.get("file_path")}

        for file_path_relative in files_to_validate:
            if not file_path_relative:
                continue
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
                else:
                    # If it's the main config, also validate structure
                    if "hephaestus_config.json" in file_path_relative:
                        with open(full_file_path_in_target, 'r') as f:
                            try:
                                config_data = json.load(f)
                                if not validate_config_structure(config_data, self.logger):
                                    all_syntax_valid = False
                                    error_details.append(f"{file_path_relative}: Invalid structure.")
                            except json.JSONDecodeError:
                                # This should have been caught by validate_json_syntax, but as a safeguard
                                pass


        if not all_syntax_valid:
            reason_code = "SYNTAX_VALIDATION_FAILED_IN_SANDBOX" if self.use_sandbox else "SYNTAX_VALIDATION_FAILED"
            return False, reason_code, "\n".join(error_details)

        self.logger.info(f"Syntax validation in '{self.base_path}': SUCCESS.")
        return True, "SYNTAX_VALIDATION_SUCCESS", "All files passed syntax validation."