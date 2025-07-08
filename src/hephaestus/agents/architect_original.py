import logging
from typing import Optional, Dict, Any, Tuple # List was not used by ArchitectAgent

from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response # Import from new location

class ArchitectAgent:
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger

    def plan_action(self, objective: str, manifest: str, file_content_context: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Encapsulates the logic of get_action_plan.
        Generates a JSON patch plan based on the objective and manifest.
        """
        prompt = f"""
You are the Software Architect of the Hephaestus agent. Your task is to take the high-level objective and, based on the project manifest and any additional file content provided, create a JSON patch plan to modify the files.

[OBJECTIVE]
{objective}

[PROJECT MANIFEST]
{manifest}

[ADDITIONAL CONTEXT FROM FILE READ]
{file_content_context}

[YOUR TASK]
Create a JSON plan with a list of "patches" to apply.
Valid operations: "INSERT", "REPLACE", "DELETE_BLOCK".

**If the [OBJECTIVE] is to create a new test file (e.g., "Create a new test file `tests/x/y.py`..."):**
1.  Your primary patch MUST be for the new test file itself.
2.  Use `operation: "REPLACE"` and `block_to_replace: null` for this new file patch.
3.  The `file_path` MUST be the one specified in the objective (e.g., `tests/x/y.py`).
4.  The `content` for this new test file MUST:
    a.  Include necessary imports (e.g., `import pytest`, `from path.to.module import ClassOrFunctionToTest`). Refer to the [PROJECT MANIFEST] or [ADDITIONAL CONTEXT FROM FILE READ] to determine the correct import path for the module being tested.
    b.  Include placeholder test functions for the primary functions/methods of the module mentioned in the objective.
    c.  Each placeholder test function should be simple, like `def test_function_name():\\n    # TODO: Implement test cases\\n    pass`.
    d.  Ensure the generated Python code is syntactically correct.
5.  Your `analysis` field should explain that you are generating a new test file with placeholders.

**For all other objectives (or additional patches besides new test file creation):**
- Each patch MUST include the full content to be inserted or that will replace a block.
- For operations on existing files, use the [ADDITIONAL CONTEXT FROM FILE READ] if available to ensure your `block_to_replace` or `block_to_delete` is accurate.
- If a file does not exist and the operation is "INSERT" or "REPLACE" (with "block_to_replace": null), the file will be created.

[REQUIRED OUTPUT FORMAT]
Your response MUST be a valid JSON object and nothing else.
{{
  "analysis": "Your analysis and reasoning for the patch plan.",
  "patches_to_apply": [ ... patches ... ]
}}

[IMPORTANT INSTRUCTIONS FOR PATCH CONTENT (ALL PATCHES)]
- For "INSERT" and "REPLACE", the "content" field MUST contain the REAL and COMPLETE code/text to be used.
- Newlines within "content" MUST be represented as '\\n'. Escape backslashes and quotes within the content string if they are part of the code, e.g. `\\"key\\": \\"value\\"` for JSON content.
- For "DELETE_BLOCK", "block_to_delete" must be the exact string of the block to be removed.
- For "REPLACE" of an entire file or creation of a new file, use "block_to_replace": null.
- Ensure the generated JSON is strictly valid.
"""
        self.logger.info(f"ArchitectAgent: Gerando plano de patches com os modelos: {self.model_config}...")
        raw_response, error = call_llm_api(
            model_config=self.model_config,
            prompt=prompt,
            temperature=0.4,
            logger=self.logger
        )

        if error:
            self.logger.error(f"ArchitectAgent: Erro ao chamar LLM para plano de patches: {error}")
            return None, f"Erro ao chamar LLM para plano de patches: {error}"

        if not raw_response:
            self.logger.error("ArchitectAgent: Resposta vazia do LLM para plano de patches.")
            return None, "Resposta vazia do LLM para plano de patches"

        parsed_json, error_parsing = parse_json_response(raw_response, self.logger)

        if error_parsing:
            self.logger.error(f"ArchitectAgent: Erro ao fazer parse do JSON do plano de patches: {error_parsing}")
            return None, f"Erro ao fazer parse do JSON do plano de patches: {error_parsing}"

        if not parsed_json:
            self.logger.error("ArchitectAgent: JSON do plano de patches analisado é None sem erro de parsing explícito.")
            return None, "JSON do plano de patches analisado é None"

        # Validate structure of parsed_json
        if not isinstance(parsed_json, dict) or "patches_to_apply" not in parsed_json or \
           not isinstance(parsed_json.get("patches_to_apply"), list):
            self.logger.error("ArchitectAgent: JSON do plano de patches inválido ou não contém a chave 'patches_to_apply' como uma lista.")
            return None, "JSON do plano de patches inválido ou não contém a chave 'patches_to_apply' como uma lista."

        # Validate individual patches
        for i, patch in enumerate(parsed_json.get("patches_to_apply", [])):
            if not isinstance(patch, dict):
                err_msg = f"ArchitectAgent: Patch no índice {i} não é um dicionário."
                self.logger.error(err_msg)
                return None, err_msg
            required_keys = ["file_path", "operation"]
            if not all(key in patch for key in required_keys):
                err_msg = f"ArchitectAgent: Patch no índice {i} está sem 'file_path' ou 'operation'."
                self.logger.error(err_msg)
                return None, err_msg
            if patch["operation"] in ["INSERT", "REPLACE"] and "content" not in patch:
                err_msg = f"ArchitectAgent: Patch {patch['operation']} no índice {i} para '{patch['file_path']}' não tem 'content'."
                self.logger.error(err_msg)
                return None, err_msg
            if patch["operation"] == "DELETE_BLOCK" and "block_to_delete" not in patch:
                err_msg = f"ArchitectAgent: Patch DELETE_BLOCK no índice {i} para '{patch['file_path']}' está sem 'block_to_delete'."
                self.logger.error(err_msg)
                return None, err_msg
            if patch["operation"] == "REPLACE" and "block_to_replace" not in patch: # block_to_replace can be null
                err_msg = f"ArchitectAgent: Patch REPLACE no índice {i} para '{patch['file_path']}' está sem 'block_to_replace' (pode ser null)."
                self.logger.error(err_msg)
                return None, err_msg

        return parsed_json, None