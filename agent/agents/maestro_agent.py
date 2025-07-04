import json # For json.dumps
import logging
from typing import Optional, Dict, Any, List, Tuple # List is used by choose_strategy return type
import hashlib
import time
from collections import OrderedDict

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response # Import from new location
from agent.validation_steps.syntax_validator import validate_config_structure

class StrategyCache:
    """Cache LRU com TTL para decisões de estratégia"""
    
    def __init__(self, maxsize: int = 100, ttl_seconds: int = 3600):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl_seconds
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, action_plan_data: Dict[str, Any], memory_summary: str = "") -> str:
        """Gera chave única para o cache baseada no contexto"""
        # Cria string representativa do contexto
        context_str = json.dumps({
            'patches_count': len(action_plan_data.get('patches_to_apply', [])),
            'patch_operations': [p.get('operation') for p in action_plan_data.get('patches_to_apply', [])],
            'target_files': sorted([p.get('file_path') for p in action_plan_data.get('patches_to_apply', [])]),
            'memory_hash': hashlib.md5(memory_summary.encode()).hexdigest()[:8] if memory_summary else ""
        }, sort_keys=True)
        
        return hashlib.md5(context_str.encode()).hexdigest()
    
    def get(self, action_plan_data: Dict[str, Any], memory_summary: str = "") -> Optional[str]:
        """Busca estratégia no cache"""
        key = self._generate_key(action_plan_data, memory_summary)
        
        if key in self.cache:
            timestamp, strategy = self.cache[key]
            if time.time() - timestamp < self.ttl:
                # Move para o final (LRU)
                self.cache.move_to_end(key)
                self.hits += 1
                return strategy
            else:
                # Expirado
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def put(self, action_plan_data: Dict[str, Any], memory_summary: str, strategy: str):
        """Adiciona estratégia ao cache"""
        key = self._generate_key(action_plan_data, memory_summary)
        
        # Remove item mais antigo se necessário
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        
        self.cache[key] = (time.time(), strategy)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total = self.hits + self.misses
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total if total > 0 else 0,
            'size': len(self.cache),
            'maxsize': self.maxsize
        }

class MaestroAgent:
    def __init__(self, model_config: Dict[str, str], config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger
        self.created_strategies = {}  # Track dynamically created strategies
        self.strategy_cache = StrategyCache()

    def _classify_strategy_by_rules(self, action_plan_data: Dict[str, Any]) -> Optional[str]:
        """
        A rule-based classifier to quickly select a strategy for common cases.
        Returns a strategy key if a rule matches, otherwise None.
        """
        patches = action_plan_data.get("patches_to_apply", [])
        if not patches:
            return "DISCARD"  # No patches, no action needed.

        # Rule 1: If creating a new test file, use the dedicated strategy.
        for patch in patches:
            file_path = patch.get("file_path", "")
            if "tests/" in file_path and patch.get("operation") in ["REPLACE", "INSERT"] and patch.get("block_to_replace") is None:
                self.logger.info("Rule-based classification: Detected new test file creation.")
                return "CREATE_NEW_TEST_FILE_STRATEGY"

        # Rule 2: If modifying the agent's configuration, use the config update strategy.
        for patch in patches:
            if "hephaestus_config.json" in patch.get("file_path", "") or "config/" in patch.get("file_path", ""):
                self.logger.info("Rule-based classification: Detected config file modification.")
                return "CONFIG_UPDATE_STRATEGY"
        
        # Rule 3: If only documentation is being changed.
        is_only_doc_changes = all(p.get("file_path", "").endswith(".md") for p in patches)
        if is_only_doc_changes:
            self.logger.info("Rule-based classification: Detected documentation-only change.")
            return "DOC_UPDATE_STRATEGY"
            
        # Add more rules here as patterns emerge...

        # Default: No rule matched
        return None

    def choose_strategy(self, action_plan_data: Dict[str, Any], memory_summary: Optional[str] = None, failed_strategy_context: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Encapsulates the logic of get_maestro_decision.
        Consults the LLM to decide which validation strategy to adopt.
        """
        attempt_logs = []
        
        # Verifica cache primeiro (apenas se não há contexto de falha)
        if not failed_strategy_context:
            cached_strategy = self.strategy_cache.get(action_plan_data, memory_summary or "")
            if cached_strategy:
                self.logger.info(f"MaestroAgent: Cache hit! Using cached strategy: {cached_strategy}")
                self.logger.debug(f"Cache stats: {self.strategy_cache.get_stats()}")
                return [{
                    "model": "cache",
                    "raw_response": f'{{"strategy_key": "{cached_strategy}"}}',
                    "parsed_json": {"strategy_key": cached_strategy},
                    "success": True
                }]
        
        # First, try to classify using rules
        rule_based_strategy = self._classify_strategy_by_rules(action_plan_data)
        if rule_based_strategy:
            self.logger.info(f"MaestroAgent: Strategy '{rule_based_strategy}' chosen by rule-based classifier.")
            # Adiciona ao cache
            self.strategy_cache.put(action_plan_data, memory_summary or "", rule_based_strategy)
            return [{
                "model": "rule_based_classifier",
                "raw_response": f'{{"strategy_key": "{rule_based_strategy}"}}',
                "parsed_json": {"strategy_key": rule_based_strategy},
                "success": True
            }]
            
        # If no rules match, fall back to the LLM
        self.logger.info("MaestroAgent: No rule matched. Falling back to LLM for strategy decision.")
        
        failure_context_str = ""
        if failed_strategy_context:
            self.logger.info(f"MaestroAgent: Re-evaluating strategy due to previous failure: {failed_strategy_context}")
            failure_context_str = f"""
[PREVIOUS ATTEMPT FAILED]
The last strategy attempted ('{failed_strategy_context.get('strategy')}') failed with the reason: '{failed_strategy_context.get('reason')}'.
Details: {failed_strategy_context.get('details')}
Your task is to choose a DIFFERENT and potentially SAFER strategy to achieve the objective. For example, if a strategy with tests failed, consider one with only syntax validation.
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
{failure_context_str}
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

        # Use optimized LLM call for better performance
        from agent.llm_performance_booster import optimized_llm_call
        content, metadata = optimized_llm_call(
            agent_type="MaestroAgent",
            prompt=prompt,
            model_config=self.model_config,
            temperature=0.2,
            context={"action_plan_data": action_plan_data, "memory_summary": memory_summary},
            logger=self.logger
        )
        
        # Check if it was an error response
        error_api = metadata.get('error')

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
        
        # Adiciona ao cache se não for contexto de falha
        if not failed_strategy_context and parsed_json.get("strategy_key"):
            self.strategy_cache.put(action_plan_data, memory_summary or "", parsed_json["strategy_key"])
            self.logger.debug(f"Added strategy to cache. Cache stats: {self.strategy_cache.get_stats()}")

        return attempt_logs
    
    def analyze_strategy_need(self, action_plan_data: Dict[str, Any], 
                            memory_summary: Optional[str] = None,
                            performance_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze if existing strategies are sufficient or if a new strategy is needed.
        
        Args:
            action_plan_data: The patch plan from ArchitectAgent
            memory_summary: Historical context
            performance_data: Strategy performance statistics
            
        Returns:
            Analysis results with recommendation for strategy creation
        """
        self.logger.info("MaestroAgent: Analyzing strategy needs...")
        
        available_strategies = self.config.get("validation_strategies", {})
        engineer_summary_json = json.dumps(action_plan_data, ensure_ascii=False, indent=2)
        
        # Build analysis prompt
        analysis_prompt = f"""
[STRATEGIC ANALYSIS TASK]
You are the Maestro Agent analyzing whether existing validation strategies are sufficient for a given objective, or if a new strategy should be created.

[AVAILABLE STRATEGIES]
{json.dumps(available_strategies, indent=2)}

[ENGINEER'S PROPOSAL]
{engineer_summary_json}

[HISTORICAL CONTEXT]
{memory_summary or "No recent history available."}

[PERFORMANCE DATA]
{json.dumps(performance_data, indent=2) if performance_data else "No performance data available."}

[ANALYSIS QUESTIONS]
1. Do any existing strategies adequately handle this type of objective?
2. Are there unique validation requirements not covered by existing strategies?
3. Have similar objectives failed repeatedly with current strategies?
4. Would a specialized strategy significantly improve success rates?

[OUTPUT FORMAT]
Respond with a JSON object:
{{
  "needs_new_strategy": true/false,
  "reasoning": "Detailed explanation of why a new strategy is/isn't needed",
  "strategy_gaps": ["List of specific gaps in current strategies"],
  "recommended_strategy_type": "Type of strategy that would be most effective",
  "estimated_success_improvement": "Percentage improvement expected",
  "complexity_level": "low/medium/high",
  "priority": "low/medium/high"
}}
"""
        
        response, error = call_llm_api(
            model_config=self.model_config,
            prompt=analysis_prompt,
            temperature=0.3,
            logger=self.logger
        )
        
        if error:
            self.logger.error(f"MaestroAgent: Strategy analysis failed: {error}")
            return {"needs_new_strategy": False, "error": error}
        
        parsed_response, parse_error = parse_json_response(response or "", self.logger)
        
        if parse_error or not parsed_response:
            self.logger.error(f"MaestroAgent: Failed to parse strategy analysis response")
            return {"needs_new_strategy": False, "error": "Parse error"}
        
        self.logger.info(f"MaestroAgent: Strategy analysis complete. New strategy needed: {parsed_response.get('needs_new_strategy', False)}")
        return parsed_response
    
    def create_new_strategy(self, strategy_need_analysis: Dict[str, Any],
                          action_plan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new validation strategy based on identified needs.
        
        Args:
            strategy_need_analysis: Results from analyze_strategy_need
            action_plan_data: The patch plan requiring the strategy
            
        Returns:
            New strategy definition or None if creation failed
        """
        if not strategy_need_analysis.get("needs_new_strategy", False):
            self.logger.info("MaestroAgent: No new strategy needed based on analysis")
            return None
        
        self.logger.info("MaestroAgent: Creating new validation strategy...")
        
        # Extract existing strategy patterns for reference
        existing_strategies = self.config.get("validation_strategies", {})
        
        creation_prompt = f"""
[STRATEGY CREATION TASK]
You are the Maestro Agent creating a new validation strategy for the Hephaestus system.

[NEED ANALYSIS]
{json.dumps(strategy_need_analysis, indent=2)}

[TARGET OBJECTIVE]
{json.dumps(action_plan_data, indent=2)}

[EXISTING STRATEGY PATTERNS]
{json.dumps(existing_strategies, indent=2)}

[CREATION GUIDELINES]
1. The strategy must be implementable using existing validation steps
2. Focus on the specific gaps identified in the analysis
3. Consider performance vs. thoroughness trade-offs
4. Ensure the strategy can be reused for similar objectives
5. Include appropriate error handling and fallback options

[AVAILABLE VALIDATION STEPS]
- apply_patches_to_disk: Apply patches to files
- validate_syntax: Check Python/JSON syntax
- validate_json_syntax: Specific JSON validation
- run_pytest_validation: Execute pytest tests
- PatchApplicatorStep: Apply patches in sandbox
- SyntaxValidator: Syntax validation in sandbox
- BenchmarkValidator: Performance benchmarks (placeholder)
- CheckFileExistenceValidator: Verify file existence

[OUTPUT FORMAT]
Create a JSON strategy definition:
{{
  "strategy_name": "descriptive_name_for_strategy",
  "description": "Clear description of what this strategy does",
  "steps": ["ordered_list_of_validation_steps"],
  "use_cases": ["list_of_objective_types_this_handles"],
  "risk_level": "low/medium/high",
  "expected_duration": "estimated_time_in_seconds",
  "success_criteria": "What defines success for this strategy",
  "failure_handling": "How failures should be handled",
  "metadata": {{
    "created_by": "MaestroAgent",
    "creation_reason": "Brief reason for creation",
    "target_improvement": "Expected improvement over existing strategies"
  }}
}}
"""
        
        response, error = call_llm_api(
            model_config=self.model_config,
            prompt=creation_prompt,
            temperature=0.4,  # Slightly higher for creativity
            logger=self.logger
        )
        
        if error:
            self.logger.error(f"MaestroAgent: Strategy creation failed: {error}")
            return None
        
        parsed_response, parse_error = parse_json_response(response or "", self.logger)
        
        if parse_error or not parsed_response:
            self.logger.error(f"MaestroAgent: Failed to parse strategy creation response")
            return None
        
        # Validate the created strategy
        if not self._validate_strategy_definition(parsed_response):
            self.logger.error("MaestroAgent: Created strategy failed validation")
            return None
        
        # Store the created strategy
        strategy_name = parsed_response.get("strategy_name")
        self.created_strategies[strategy_name] = parsed_response
        
        self.logger.info(f"MaestroAgent: Successfully created strategy '{strategy_name}'")
        return parsed_response
    
    def _validate_strategy_definition(self, strategy_def: Dict[str, Any]) -> bool:
        """Validate that a strategy definition is well-formed."""
        required_fields = ["strategy_name", "description", "steps", "use_cases"]
        
        for field in required_fields:
            if field not in strategy_def:
                self.logger.error(f"Strategy definition missing required field: {field}")
                return False
        
        # Validate steps exist
        steps = strategy_def.get("steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            self.logger.error("Strategy must have at least one validation step")
            return False
        
        # Validate step names (basic check)
        valid_steps = [
            "apply_patches_to_disk", "validate_syntax", "validate_json_syntax",
            "run_pytest_validation", "PatchApplicatorStep", "SyntaxValidator",
            "BenchmarkValidator", "CheckFileExistenceValidator"
        ]
        
        for step in steps:
            if step not in valid_steps:
                self.logger.warning(f"Unknown validation step in strategy: {step}")
        
        return True
    
    def enhanced_choose_strategy(self, action_plan_data: Dict[str, Any], 
                               memory_summary: Optional[str] = None,
                               performance_data: Optional[Dict[str, Any]] = None,
                               allow_strategy_creation: bool = True) -> List[Dict[str, Any]]:
        """
        Enhanced strategy selection that can create new strategies if needed.
        
        Args:
            action_plan_data: The patch plan from ArchitectAgent
            memory_summary: Historical context
            performance_data: Strategy performance statistics
            allow_strategy_creation: Whether to allow creating new strategies
            
        Returns:
            Strategy decision with potential new strategy creation
        """
        self.logger.info("MaestroAgent: Enhanced strategy selection with dynamic creation capability")
        
        # First, try normal strategy selection
        normal_decision = self.choose_strategy(action_plan_data, memory_summary)
        
        # If normal selection succeeded, check if we should still consider a new strategy
        if normal_decision and normal_decision[0].get("success"):
            chosen_strategy = normal_decision[0].get("parsed_json", {}).get("strategy_key")
            
            # If we chose a valid strategy, analyze if we could do better
            if chosen_strategy and chosen_strategy not in ["CAPACITATION_REQUIRED", "WEB_SEARCH_REQUIRED"]:
                if allow_strategy_creation and performance_data:
                    # Check if the chosen strategy has poor performance for this type of objective
                    strategy_perf = performance_data.get("strategy_performance", {}).get(chosen_strategy, {})
                    success_rate = strategy_perf.get("success_rate", 1.0)
                    
                    if success_rate < 0.6:  # Poor performance threshold
                        self.logger.info(f"Chosen strategy '{chosen_strategy}' has low success rate ({success_rate:.1%}). Analyzing need for new strategy...")
                        
                        strategy_analysis = self.analyze_strategy_need(action_plan_data, memory_summary, performance_data)
                        
                        if strategy_analysis.get("needs_new_strategy"):
                            new_strategy = self.create_new_strategy(strategy_analysis, action_plan_data)
                            
                            if new_strategy:
                                # Return decision to use the newly created strategy
                                return [{
                                    "model": "dynamic_strategy_creation",
                                    "raw_response": f"Created new strategy '{new_strategy['strategy_name']}' based on performance analysis",
                                    "parsed_json": {"strategy_key": "DYNAMIC_STRATEGY_CREATED", "new_strategy": new_strategy},
                                    "success": True,
                                    "strategy_analysis": strategy_analysis
                                }]
        
        # If we couldn't create a better strategy or weren't allowed to, return normal decision
        return normal_decision
    
    def get_strategy_recommendation_objective(self, analysis_results: Dict[str, Any]) -> Optional[str]:
        """Generate an objective for implementing a dynamically created strategy."""
        new_strategy = analysis_results.get("new_strategy")
        if not new_strategy:
            return None
        
        strategy_name = new_strategy.get("strategy_name", "unknown_strategy")
        description = new_strategy.get("description", "")
        
        return f"[STRATEGY IMPLEMENTATION] Implement the new validation strategy '{strategy_name}' in the configuration system. Strategy: {description[:100]}..."
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from functools import lru_cache
import time

class StrategyCache:
    """
    LRU cache with TTL for strategy decisions.
    
    Attributes:
        maxsize: Maximum number of items to cache
        ttl: Time-to-live for cache entries in seconds
    """
    def __init__(self, maxsize: int = 128, ttl: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Dict]:
        """Get a cached strategy decision if it exists and is fresh."""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.ttl:
                return self._cache[key]
            self._cache.pop(key)
            self._timestamps.pop(key)
        return None

    def set(self, key: str, value: Dict) -> None:
        """Cache a strategy decision."""
        if len(self._cache) >= self.maxsize:
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            self._cache.pop(oldest_key)
            self._timestamps.pop(oldest_key)
        self._cache[key] = value
        self._timestamps[key] = time.time()

class MaestroAgent:
    """
    Orchestrates strategy selection and execution for the Hephaestus agent system.
    
    The refactored version modularizes strategy evaluation into focused sub-functions
    for better maintainability and testability.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.strategy_cache = StrategyCache()
        
    def _evaluate_syntax_strategy(self, context: Dict) -> Dict:
        """
        Evaluate and select syntax validation strategies.
        
        Args:
            context: Context dictionary with analysis data
            
        Returns:
            Dictionary with selected strategy and parameters
        """
        # TODO: Implement syntax strategy evaluation logic
        raise NotImplementedError("Syntax strategy evaluation not implemented")
        
    def _evaluate_test_strategy(self, context: Dict) -> Dict:
        """
        Evaluate and select testing strategies.
        
        Args:
            context: Context dictionary with analysis data
            
        Returns:
            Dictionary with selected strategy and parameters
        """
        # TODO: Implement test strategy evaluation logic
        raise NotImplementedError("Test strategy evaluation not implemented")
        
    def _select_fallback_strategy(self, context: Dict) -> Dict:
        """
        Select a fallback strategy when primary strategies fail.
        
        Args:
            context: Context dictionary with analysis data
            
        Returns:
            Dictionary with fallback strategy and parameters
        """
        # TODO: Implement fallback strategy selection
        raise NotImplementedError("Fallback strategy selection not implemented")
        
    def execute_strategy(self, context: Dict) -> Dict:
        """
        Main entry point for strategy execution.
        
        Args:
            context: Context dictionary with analysis data
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Check cache first
            cache_key = self._generate_cache_key(context)
            cached_strategy = self.strategy_cache.get(cache_key)
            if cached_strategy:
                return cached_strategy
                
            # Evaluate strategies
            strategy = self._evaluate_primary_strategies(context)
            
            # Cache and return the strategy
            self.strategy_cache.set(cache_key, strategy)
            return strategy
            
        except Exception as e:
            self.logger.error(f"Strategy execution failed: {str(e)}")
            return self._select_fallback_strategy(context)
    
    def _evaluate_primary_strategies(self, context: Dict) -> Dict:
        """
        Evaluate all primary strategies and select the best one.
        
        Args:
            context: Context dictionary with analysis data
            
        Returns:
            Dictionary with selected strategy and parameters
        """
        strategies = []
        
        # Evaluate syntax strategy
        try:
            syntax_strategy = self._evaluate_syntax_strategy(context)
            strategies.append(syntax_strategy)
        except Exception as e:
            self.logger.warning(f"Syntax strategy evaluation failed: {str(e)}")
        
        # Evaluate test strategy
        try:
            test_strategy = self._evaluate_test_strategy(context)
            strategies.append(test_strategy)
        except Exception as e:
            self.logger.warning(f"Test strategy evaluation failed: {str(e)}")
        
        if not strategies:
            raise ValueError("No valid strategies could be evaluated")
            
        # TODO: Implement strategy selection logic
        return strategies[0]
    
    def _generate_cache_key(self, context: Dict) -> str:
        """Generate a cache key from the context."""
        # TODO: Implement proper cache key generation
        return str(hash(frozenset(context.items())))