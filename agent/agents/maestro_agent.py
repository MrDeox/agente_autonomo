from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import logging

class StrategyCache:
    """
    LRU cache with TTL for strategy decisions.
    
    Attributes:
        max_size: Maximum number of strategies to cache
        ttl: Time-to-live for cached strategies in seconds
    """
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = timedelta(seconds=ttl)

    def get(self, key: str) -> Optional[Dict]:
        """Retrieve a strategy from cache if it exists and isn't expired."""
        if key not in self.cache:
            return None
            
        strategy, timestamp = self.cache[key]
        if datetime.now() - timestamp > self.ttl:
            self.cache.pop(key)
            return None
            
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return strategy

    def set(self, key: str, strategy: Dict) -> None:
        """Store a strategy in the cache."""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
        self.cache[key] = (strategy, datetime.now())


class MaestroAgent:
    """
    Orchestrates strategy selection and execution for the Hephaestus system.
    
    Attributes:
        strategy_cache: Cache for storing strategy decisions
        logger: Logger instance for logging
        performance_data: Tracks performance of different strategies
    """
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        # The agent is responsible for getting its own model config from the main config
        self.model_config = config.get("models", {}).get("maestro_default", {})
        self.logger = logger
        self.created_strategies = {}  # Track dynamically created strategies
        self.strategy_cache = StrategyCache()
        self.performance_data = {}

    def select_strategy(self, context: Dict) -> Dict:
        """
        Selects the optimal strategy based on the given context.
        
        Args:
            context: Dictionary containing context for strategy selection
            
        Returns:
            Dictionary containing the selected strategy
        """
        cache_key = self._generate_cache_key(context)
        
        # Check cache first
        cached_strategy = self.strategy_cache.get(cache_key)
        if cached_strategy:
            self.logger.debug(f"Using cached strategy for key: {cache_key}")
            return cached_strategy
            
        # Generate new strategy
        strategy = self._generate_strategy(context)
        
        # Store in cache
        self.strategy_cache.set(cache_key, strategy)
        
        return strategy

    def _generate_cache_key(self, context: Dict) -> str:
        """Generates a cache key from the context dictionary."""
        # TODO: Implement robust key generation
        return str(sorted(context.items()))

    def _generate_strategy(self, context: Dict) -> Dict:
        """
        Generates a new strategy based on the context.
        
        Args:
            context: Dictionary containing context for strategy generation
            
        Returns:
            Dictionary containing the generated strategy
        """
        # TODO: Implement adaptive strategy generation
        return {
            "strategy_type": "default",
            "parameters": {},
            "fallback_strategy": None
        }

    def record_performance(self, strategy: Dict, success: bool, metrics: Dict) -> None:
        """
        Records the performance of a strategy for future optimization.
        
        Args:
            strategy: The strategy that was executed
            success: Whether the strategy was successful
            metrics: Performance metrics for the strategy
        """
        strategy_type = strategy.get("strategy_type", "unknown")
        
        if strategy_type not in self.performance_data:
            self.performance_data[strategy_type] = {
                "success_count": 0,
                "failure_count": 0,
                "total_executions": 0,
                "average_metrics": {}
            }
            
        stats = self.performance_data[strategy_type]
        stats["total_executions"] += 1
        
        if success:
            stats["success_count"] += 1
        else:
            stats["failure_count"] += 1
            
        # Update average metrics
        for metric, value in metrics.items():
            if metric not in stats["average_metrics"]:
                stats["average_metrics"][metric] = value
            else:
                current_avg = stats["average_metrics"][metric]
                n = stats["total_executions"]
                stats["average_metrics"][metric] = ((current_avg * (n-1)) + value) / n
        
        self.logger.debug(f"Recorded performance for strategy {strategy_type}: {stats}")

    def get_success_rate(self, strategy_type: str) -> float:
        """
        Returns the success rate for a given strategy type.
        
        Args:
            strategy_type: The type of strategy to get success rate for
            
        Returns:
            The success rate as a float between 0 and 1
        """
        if strategy_type not in self.performance_data:
            return 0.0
            
        stats = self.performance_data[strategy_type]
        if stats["total_executions"] == 0:
            return 0.0
            
        return stats["success_count"] / stats["total_executions"]

    def _classify_strategy_by_rules(self, action_plan_data: Dict[str, Any]) -> Optional[str]:
        patches = action_plan_data.get("patches_to_apply", [])
        if not patches:
            return "DISCARD"

        if any("tests/" in p.get("file_path", "") and p.get("operation") in ["REPLACE", "INSERT"] and p.get("block_to_replace") is None for p in patches):
            self.logger.info("Rule-based classification: Detected new test file creation.")
            return "CREATE_NEW_TEST_FILE_STRATEGY"
        
        if any("config/" in p.get("file_path", "") for p in patches):
            self.logger.info("Rule-based classification: Detected config file modification.")
            return "CONFIG_UPDATE_STRATEGY"

        if all(p.get("file_path", "").endswith(".md") for p in patches):
            self.logger.info("Rule-based classification: Detected documentation-only change.")
            return "DOC_UPDATE_STRATEGY"
            
        return None

    def choose_strategy(self, action_plan_data: Dict[str, Any], memory_summary: Optional[str] = None, failed_strategy_context: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        if not failed_strategy_context:
            cached_strategy = self.strategy_cache.get(action_plan_data, memory_summary or "")
            if cached_strategy:
                self.logger.info(f"MaestroAgent: Cache hit! Using cached strategy: {cached_strategy}")
                return [{"model": "cache", "parsed_json": {"strategy_key": cached_strategy}, "success": True}]
        
        rule_based_strategy = self._classify_strategy_by_rules(action_plan_data)
        if rule_based_strategy:
            self.logger.info(f"MaestroAgent: Strategy '{rule_based_strategy}' chosen by rule-based classifier.")
            self.strategy_cache.put(action_plan_data, memory_summary or "", rule_based_strategy)
            return [{"model": "rule_based_classifier", "parsed_json": {"strategy_key": rule_based_strategy}, "success": True}]
            
        self.logger.info("MaestroAgent: No rule matched. Falling back to LLM for strategy decision.")
        
        # (A lógica completa de chamada do LLM e parsing da resposta segue aqui)
        # Por simplicidade na restauração, vamos usar uma lógica de fallback mais simples por enquanto
        # para garantir que o método exista e funcione.

        available_strategies = self.config.get("validation_strategies", {})
        
        # Fallback simples: se tiver testes, use uma estratégia com pytest. Senão, use uma mais simples.
        has_test_files = any("tests/" in p.get("file_path", "") for p in action_plan_data.get("patches_to_apply", []))
        
        if has_test_files and "CREATE_NEW_TEST_FILE_STRATEGY" in available_strategies:
             chosen_strategy = "CREATE_NEW_TEST_FILE_STRATEGY"
        elif "sandbox_validation_no_tests" in available_strategies:
            chosen_strategy = "sandbox_validation_no_tests"
        else:
            chosen_strategy = "NO_OP_STRATEGY"

        self.logger.info(f"MaestroAgent: Using simple fallback logic, chose strategy: {chosen_strategy}")
        return [{"model": "simple_fallback", "parsed_json": {"strategy_key": chosen_strategy}, "success": True}]

    # O resto dos métodos como analyze_strategy_need, create_new_strategy, etc. podem ser adicionados aqui depois.