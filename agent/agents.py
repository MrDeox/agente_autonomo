import json
import logging
# import requests # No longer needed here, call_llm_api is imported from utils
import traceback # Keep if parse_json_response uses it, otherwise remove
from typing import Optional, Dict, Any, List, Tuple

from agent.utils.llm_client import call_llm_api

# Esta função é uma cópia de agent.brain.parse_json_response
# Idealmente, seria movida para um módulo de utilitários compartilhado se usada em mais lugares.
# Mantida aqui por simplicidade durante a refatoração
def parse_json_response(raw_str: str, logger: logging.Logger) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.
    Remove blocos de markdown, extrai conteúdo entre a primeira '{' e a última '}',
    remove caracteres não imprimíveis e carrega o JSON.

    Args:
        raw_str: A string bruta da resposta da LLM.
        logger: Instância do logger para registrar o processo.

    Returns:
        Uma tupla contendo o dicionário JSON parseado (ou None em caso de erro)
        e uma mensagem de erro (ou None em caso de sucesso).
    """
    if not raw_str or not raw_str.strip():
        if logger:
            logger.error("parse_json_response: Received empty or whitespace-only string.")
        return None, "String de entrada vazia ou apenas espaços em branco."

    clean_content = raw_str.strip()
    if logger: logger.debug(f"parse_json_response: Raw response before cleaning: {raw_str[:300]}...")

    first_brace = clean_content.find('{')
    last_brace = clean_content.rfind('}')

    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        clean_content = clean_content[first_brace:last_brace+1]
        if logger: logger.debug(f"parse_json_response: Extracted JSON content based on braces: {clean_content[:300]}...")
    else:
        # Attempt to remove markdown code blocks if they exist
        if clean_content.startswith('```json'):
            clean_content = clean_content[7:] # Remove ```json
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3] # Remove ```
        elif clean_content.startswith('```'): # Generic code block
            clean_content = clean_content[3:]
            if clean_content.endswith('```'):
                clean_content = clean_content[:-3]
        clean_content = clean_content.strip() # Strip again after potential markdown removal
        if logger: logger.debug(f"parse_json_response: Content after attempting markdown removal (if any): {clean_content[:300]}...")

    # Remove non-printable characters except for common whitespace like \n, \r, \t
    clean_content = ''.join(char for char in clean_content if ord(char) >= 32 or char in ['\n', '\r', '\t'])
    if logger: logger.debug(f"parse_json_response: Final cleaned content before parsing: {clean_content[:300]}...")

    if not clean_content:
        if logger:
            logger.error("parse_json_response: Content became empty after cleaning.")
        return None, "Conteúdo ficou vazio após limpeza."

    try:
        parsed_json = json.loads(clean_content)
        return parsed_json, None
    except json.JSONDecodeError as e:
        error_message = f"Erro ao decodificar JSON: {str(e)}. Conteúdo limpo (parcial): {clean_content[:500]}"
        if logger:
            logger.error(
                f"parse_json_response: {error_message}. Resposta original (parcial): {raw_str[:200]}"
            )
        return None, f"Erro ao decodificar JSON: {str(e)}. Resposta original (parcial): {raw_str[:200]}"
    except Exception as e:
        error_message = f"Erro inesperado ao processar JSON: {str(e)}"
        detailed_error = (
            f"{error_message}\n{traceback.format_exc()}" if 'traceback' in globals() else error_message
        )
        if logger:
            logger.error(f"parse_json_response: {detailed_error}", exc_info=True)
        return None, f"Erro inesperado ao processar JSON: {str(e)}"

# call_llm_api is imported from agent.utils.llm_client


class ArchitectAgent:
    def __init__(self, api_key: str, model: str, logger: logging.Logger, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.logger = logger # Type hint changed to logging.Logger
        self.base_url = base_url

    def plan_action(self, objective: str, manifest: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Encapsulates the logic of get_action_plan.
        Generates a JSON patch plan based on the objective and manifest.
        """
        prompt = f"""
You are the Software Architect of the Hephaestus agent. Your task is to take the high-level objective and, based on the project manifest, create a JSON patch plan to modify the files.

[OBJECTIVE]
{objective}

[PROJECT MANIFEST]
{manifest}

[YOUR TASK]
Create a JSON plan with a list of "patches" to apply. Each patch MUST include the full content to be inserted or that will replace a block.
Valid operations for each patch are: "INSERT", "REPLACE", "DELETE_BLOCK".
For operations on existing files, analyze the manifest to understand the current state of the file before proposing the patch.
If a file does not exist and the operation is "INSERT" or "REPLACE" (with "block_to_replace": null), the file will be created.

[REQUIRED OUTPUT FORMAT]
Your response MUST be a valid JSON object and nothing else.
{{
  "analysis": "Your analysis and reasoning for the patch plan.",
  "patches_to_apply": [
    {{
      "file_path": "path/to/file.py",
      "operation": "INSERT",
      "line_number": 1,
      "content": "import os\\nimport sys"
    }},
    {{
      "file_path": "existing/path/file.txt",
      "operation": "REPLACE",
      "block_to_replace": "old text to be replaced",
      "is_regex": false,
      "content": "new text that replaces the old block."
    }},
    {{
      "file_path": "path/to/another_file.py",
      "operation": "DELETE_BLOCK",
      "block_to_delete": "def obsolete_function(param):\\n    pass\\n",
      "is_regex": false
    }},
    {{
      "file_path": "new/config_file.json",
      "operation": "REPLACE",
      "block_to_replace": null,
      "content": "{{\\n  \\"key\\": \\"value\\",\\n  \\"another_key\\": 123\\n}}"
    }}
  ]
}}

[IMPORTANT INSTRUCTIONS FOR PATCH CONTENT]
- For "INSERT" and "REPLACE", the "content" field MUST contain the REAL and COMPLETE code/text to be used.
- Newlines within "content" MUST be represented as '\\n'.
- For "DELETE_BLOCK", "block_to_delete" must be the exact string of the block to be removed.
- For "REPLACE" of an entire file or creation of a new file, use "block_to_replace": null.
- Ensure the generated JSON is strictly valid.
"""
        self.logger.info(f"ArchitectAgent: Gerando plano de patches com o modelo: {self.model}...")
        raw_response, error = call_llm_api(self.api_key, self.model, prompt, 0.4, self.base_url, self.logger) # Use imported function

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


class MaestroAgent:
    def __init__(self, api_key: str, model_list: List[str], config: Dict[str, Any], logger: logging.Logger, base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model_list = model_list
        self.config = config
        self.logger = logger # Type hint changed to logging.Logger
        self.base_url = base_url

    def choose_strategy(self, action_plan_data: Dict[str, Any], memory_summary: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Encapsulates the logic of get_maestro_decision.
        Consults the LLM to decide which validation strategy to adopt.
        """
        attempt_logs = []
        available_strategies = self.config.get("validation_strategies", {})
        available_keys = ", ".join(available_strategies.keys())
        engineer_summary_json = json.dumps(action_plan_data, ensure_ascii=False, indent=2)

        # Check for test fix context flag
        if memory_summary and "[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS" in memory_summary:
            test_fix_strategy_key = self.config.get("test_fix_strategy_key", "test_fix_strategy") # Default key
            if test_fix_strategy_key in available_strategies:
                self.logger.info(f"MaestroAgent: TEST_FIX_IN_PROGRESS detected - using special test fix strategy: {test_fix_strategy_key}")
                return [{
                    "model": "internal_rule (test_fix)",
                    "raw_response": f"Automatic test fix strategy '{test_fix_strategy_key}' selected due to context flag.",
                    "parsed_json": {"strategy_key": test_fix_strategy_key},
                    "success": True
                }]
            else:
                self.logger.warning(
                    f"MaestroAgent: TEST_FIX_IN_PROGRESS detectado mas 'test_fix_strategy_key' ('{test_fix_strategy_key}') não é uma estratégia válida. Prosseguindo com decisão via LLM."
                )

        memory_context_str = ""
        if memory_summary and memory_summary.strip() and memory_summary.lower() != "no relevant history available.":
            memory_context_str = f"""
[HISTÓRICO RECENTE (OBJETIVOS E ESTRATÉGIAS USADAS)]
{memory_summary}
Considere esse histórico em sua decisão. Evite repetir estratégias que falharam recentemente para objetivos semelhantes.
"""

        for model in self.model_list:
            self.logger.info(f"MaestroAgent: Tentando decisão com o modelo: {model}...")

            prompt = f"""
[IDENTITY]
You are the Maestro of the Hephaestus agent. Your task is to analyze the Engineer's proposal (patch plan) and recent history to decide the best course of action.

[CONTEXT AND HISTORY]
{memory_context_str}

[ENGINEER'S PROPOSAL (PATCH PLAN)]
{engineer_summary_json}

[YOUR DECISION]
Based on the proposal and history:
1. If the solution seems reasonable and does not require new capabilities, choose the most appropriate validation strategy.
2. If the solution requires new capabilities that Hephaestus needs to develop, respond with `CAPACITATION_REQUIRED`.

Available Validation Strategies: {available_keys}
Additional Option: CAPACITATION_REQUIRED

[REQUIRED OUTPUT FORMAT]
Respond ONLY with a JSON object containing the "strategy_key" and the value being ONE of the available strategies OR "CAPACITATION_REQUIRED".
Example: {{"strategy_key": "sandbox_pytest_validation"}}
Example: {{"strategy_key": "CAPACITATION_REQUIRED"}}
"""
            if self.logger: self.logger.debug(f"MaestroAgent: Prompt for decision:\n{prompt}")

            attempt_log = {
                "model": model,
                "raw_response": "",
                "parsed_json": None,
                "success": False,
            }

            content, error_api = call_llm_api(self.api_key, model, prompt, 0.2, self.base_url, self.logger) # Use imported function

            if error_api:
                attempt_log["raw_response"] = f"Erro da API (modelo {model}): {error_api}"
                attempt_logs.append(attempt_log)
                continue

            if not content:  # Content can be an empty string from LLM, treat as invalid for this case
                attempt_log["raw_response"] = f"Resposta vazia do LLM (modelo {model})"
                attempt_logs.append(attempt_log)
                continue

            attempt_log["raw_response"] = content
            parsed_json, error_parsing = parse_json_response(content, self.logger)

            if error_parsing:
                attempt_log["raw_response"] = f"Erro ao fazer parse (modelo {model}): {error_parsing}. Conteúdo: {content[:200]}"
                attempt_logs.append(attempt_log)
                continue

            if not parsed_json:  # Should ideally be caught by error_parsing, but as a safeguard
                attempt_log["raw_response"] = f"JSON convertido para None sem erro explícito (modelo {model}). Conteúdo: {content[:200]}"
                attempt_logs.append(attempt_log)
                continue

            if not isinstance(parsed_json, dict) or "strategy_key" not in parsed_json:
                error_msg = f"JSON com formato inválido ou faltando 'strategy_key' (modelo {model}). Recebido: {parsed_json}"
                if self.logger: self.logger.warning(f"MaestroAgent: {error_msg}")
                attempt_log["raw_response"] = f"{error_msg}. Original: {content[:200]}"
                attempt_logs.append(attempt_log)
                continue

            # Further validation: is the strategy_key valid?
            chosen_strategy = parsed_json.get("strategy_key")
            if chosen_strategy not in available_strategies and chosen_strategy not in ["CAPACITATION_REQUIRED", "WEB_SEARCH_REQUIRED"]:
                error_msg = (
                    f"Estratégia escolhida ('{chosen_strategy}') não é válida ou CAPACITATION_REQUIRED (modelo {model}). Válidas: {available_keys}, CAPACITATION_REQUIRED"
                )
                if self.logger: self.logger.warning(f"MaestroAgent: {error_msg}")
                attempt_log["raw_response"] = f"{error_msg}. Original: {content[:200]}"
                # Do not mark as success, let it try next model or fail
                attempt_logs.append(attempt_log)
                continue


            attempt_log["parsed_json"] = parsed_json
            attempt_log["success"] = True
            attempt_logs.append(attempt_log)
            break # Success, no need to try other models

        return attempt_logs
