from typing import Dict, Optional, Tuple, List, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import logging
import hashlib
import json
import csv
from pathlib import Path

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
    
    def get(self, action_plan_data: Dict[str, Any], memory_summary: str = "") -> Optional[str]:
        """Retrieve a strategy from cache if it exists and isn't expired."""
        key = self._generate_key(action_plan_data, memory_summary)
        
        if key not in self.cache:
            return None
            
        strategy, timestamp = self.cache[key]
        if datetime.now() - timestamp > self.ttl:
            self.cache.pop(key)
            return None
            
        # Move to end to mark as recently used
        self.cache.move_to_end(key)
        return strategy

    def put(self, action_plan_data: Dict[str, Any], memory_summary: str, strategy: str):
        """Adiciona estratégia ao cache"""
        key = self._generate_key(action_plan_data, memory_summary)
        
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)
        
        self.cache[key] = (strategy, datetime.now())

    def _generate_key(self, action_plan_data: Dict[str, Any], memory_summary: str = "") -> str:
        """Generates a cache key from the context dictionary."""
        context_str = json.dumps({
            'patches_count': len(action_plan_data.get('patches_to_apply', [])),
            'patch_operations': [p.get('operation') for p in action_plan_data.get('patches_to_apply', [])],
            'target_files': sorted([p.get('file_path') for p in action_plan_data.get('patches_to_apply', [])]),
            'memory_hash': hashlib.md5(memory_summary.encode()).hexdigest()[:8] if memory_summary else ""
        }, sort_keys=True)
        
        return hashlib.md5(context_str.encode()).hexdigest()

class MaestroAgent:
    """
    Orchestrates strategy selection and execution for the Hephaestus system.
    
    Attributes:
        strategy_cache: Cache for storing strategy decisions
        logger: Logger instance for logging
        performance_data: Tracks performance of different strategies
        strategy_weights: Dynamic weights for strategy selection
    """
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.model_config = config.get("models", {}).get("maestro_default", {})
        self.logger = logger
        self.created_strategies = {}  # Track dynamically created strategies
        self.strategy_cache = StrategyCache()
        self.performance_data = {}
        self.strategy_weights = {}
        self.error_analyzer = None
        self._load_historical_performance()

    def _load_historical_performance(self) -> None:
        """Load historical performance data from evolution_log.csv."""
        log_path = Path("logs/evolution_log.csv")
        if not log_path.exists():
            self.logger.warning("No evolution_log.csv found, using default weights")
            return

        try:
            with open(log_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    strategy = row.get('strategy')
                    success = row.get('success', '').lower() == 'true'
                    
                    if strategy:
                        if strategy not in self.performance_data:
                            self.performance_data[strategy] = {
                                "success_count": 0,
                                "failure_count": 0,
                                "total_executions": 0,
                                "average_metrics": {}
                            }
                        
                        stats = self.performance_data[strategy]
                        stats["total_executions"] += 1
                        if success:
                            stats["success_count"] += 1
                        else:
                            stats["failure_count"] += 1
            
            self._calculate_strategy_weights()
        except Exception as e:
            self.logger.error(f"Failed to load historical performance data: {e}")

    def _calculate_strategy_weights(self) -> None:
        """Calculate dynamic weights for each strategy based on historical performance."""
        total_success = sum(data["success_count"] for data in self.performance_data.values())
        
        for strategy, data in self.performance_data.items():
            if data["total_executions"] > 0:
                success_rate = data["success_count"] / data["total_executions"]
                # Weight is success rate adjusted by execution count and error analysis
                weight = success_rate * (1 + min(data["total_executions"]/100, 1))
                
                # Apply error analysis adjustment if available
                if self.error_analyzer:
                    error_factor = self.error_analyzer.get_error_factor(strategy)
                    weight *= (1 - error_factor)
                
                self.strategy_weights[strategy] = weight
            else:
                self.strategy_weights[strategy] = 0.5  # Default weight for untested strategies

    def select_strategy(self, context: Dict) -> Dict:
        """
        Selects the optimal strategy based on the given context and historical performance.
        
        Args:
            context: Dictionary containing context for strategy selection
            
        Returns:
            Dictionary containing the selected strategy
        """
        cache_key = self._generate_cache_key(context)
        
        # Check cache first
        cached_strategy = self.strategy_cache.get(context, "")
        if cached_strategy:
            self.logger.debug(f"Using cached strategy for key: {cache_key}")
            return cached_strategy
            
        # Generate new strategy with dynamic weighting
        strategy = self._generate_weighted_strategy(context)
        
        # Store in cache
        self.strategy_cache.set(cache_key, strategy)
        
        return strategy

    def _generate_weighted_strategy(self, context: Dict) -> Dict:
        """
        Generates a new strategy based on the context and historical performance weights.
        
        Args:
            context: Dictionary containing context for strategy generation
            
        Returns:
            Dictionary containing the generated strategy
        """
        available_strategies = self.config.get("validation_strategies", {})
        
        if not available_strategies:
            return {
                "strategy_type": "default",
                "parameters": {},
                "fallback_strategy": None
            }
        
        # Filter strategies by context
        applicable_strategies = [
            s for s in available_strategies 
            if self._is_strategy_applicable(s, context)
        ]
        
        if not applicable_strategies:
            return {
                "strategy_type": "default",
                "parameters": {},
                "fallback_strategy": None
            }
        
        # Sort by weight descending
        sorted_strategies = sorted(
            applicable_strategies,
            key=lambda s: self.strategy_weights.get(s, 0.5),
            reverse=True
        )
        
        primary_strategy = sorted_strategies[0]
        fallback_strategy = sorted_strategies[1] if len(sorted_strategies) > 1 else None
        
        return {
            "strategy_type": primary_strategy,
            "parameters": {},
            "fallback_strategy": fallback_strategy
        }

    def _is_strategy_applicable(self, strategy: str, context: Dict) -> bool:
        """Determines if a strategy is applicable to the given context."""
        # First check rule-based classification
        rule_based = self._classify_strategy_by_rules(context)
        if rule_based and rule_based == strategy:
            return True
            
        # Then check other applicability criteria
        patches = context.get("patches_to_apply", [])
        
        if strategy == "CREATE_NEW_TEST_FILE_STRATEGY":
            return any("tests/" in p.get("file_path", "") for p in patches)
        elif strategy == "CONFIG_UPDATE_STRATEGY":
            return any("config/" in p.get("file_path", "") for p in patches)
        elif strategy == "DOC_UPDATE_STRATEGY":
            return all(p.get("file_path", "").endswith(".md") for p in patches)
        
        return True
    
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
        self._calculate_strategy_weights()

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
        """
        Chooses the best strategy based on context and historical performance.
        
        Args:
            action_plan_data: Data about the action to be performed
            memory_summary: Summary of relevant memory
            failed_strategy_context: Context about any previous failed strategy
            
        Returns:
            List of strategy results
        """
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
            
        # Use weighted strategy selection
        selected_strategy = self._generate_weighted_strategy(action_plan_data)
        strategy_key = selected_strategy["strategy_type"]
        
        self.logger.info(f"MaestroAgent: Selected strategy '{strategy_key}' based on weighted selection")
        self.strategy_cache.put(action_plan_data, memory_summary or "", strategy_key)
        
        return [{"model": "weighted_selection", "parsed_json": {"strategy_key": strategy_key}, "success": True}]

    def integrate_error_analyzer(self, error_analyzer: Any) -> None:
        """
        Integrates the ErrorAnalysisAgent with the MaestroAgent.
        
        Args:
            error_analyzer: Instance of ErrorAnalysisAgent
        """
        self.error_analyzer = error_analyzer
        self.logger.info("Successfully integrated ErrorAnalysisAgent with MaestroAgent")