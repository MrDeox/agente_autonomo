import json # For json.dumps
import logging
from typing import Optional, Dict, Any, List, Tuple # List is used by choose_strategy return type

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response # Import from new location

class MaestroAgent:
    def __init__(self, model_config: Dict[str, str], config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger

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

        self.logger.info(f"MaestroAgent: Tentando decisão com os modelos: {self.model_config}...")

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
            "model": f"primary: {self.model_config.get('primary')}, fallback: {self.model_config.get('fallback')}",
            "raw_response": "",
            "parsed_json": None,
            "success": False,
        }

        content, error_api = call_llm_api(
            model_config=self.model_config,
            prompt=prompt,
            temperature=0.2,
            logger=self.logger
        )

        if error_api:
            attempt_log["raw_response"] = f"Erro da API: {error_api}"
            attempt_logs.append(attempt_log)
            return attempt_logs

        if not content:
            attempt_log["raw_response"] = "Resposta vazia do LLM"
            attempt_logs.append(attempt_log)
            return attempt_logs

        attempt_log["raw_response"] = content
        parsed_json, error_parsing = parse_json_response(content, self.logger)

        if error_parsing:
            attempt_log["raw_response"] = f"Erro ao fazer parse: {error_parsing}. Conteúdo: {content[:200]}"
            attempt_logs.append(attempt_log)
            return attempt_logs

        if not parsed_json:
            attempt_log["raw_response"] = f"JSON convertido para None sem erro explícito. Conteúdo: {content[:200]}"
            attempt_logs.append(attempt_log)
            return attempt_logs

        if not isinstance(parsed_json, dict) or "strategy_key" not in parsed_json:
            error_msg = f"JSON com formato inválido ou faltando 'strategy_key'. Recebido: {parsed_json}"
            if self.logger: self.logger.warning(f"MaestroAgent: {error_msg}")
            attempt_log["raw_response"] = f"{error_msg}. Original: {content[:200]}"
            attempt_logs.append(attempt_log)
            return attempt_logs

        chosen_strategy = parsed_json.get("strategy_key")
        if chosen_strategy not in available_strategies and chosen_strategy not in ["CAPACITATION_REQUIRED", "WEB_SEARCH_REQUIRED"]:
            error_msg = f"Estratégia escolhida ('{chosen_strategy}') não é válida. Válidas: {available_keys}, CAPACITATION_REQUIRED"
            if self.logger: self.logger.warning(f"MaestroAgent: {error_msg}")
            attempt_log["raw_response"] = f"{error_msg}. Original: {content[:200]}"
            attempt_logs.append(attempt_log)
            return attempt_logs

        attempt_log["parsed_json"] = parsed_json
        attempt_log["success"] = True
        attempt_logs.append(attempt_log)

        return attempt_logs
