import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from agent.utils.llm_client import call_llm_with_fallback
from agent.utils.intelligent_cache import IntelligentCache

class StrategyCache:
    """LRU cache with TTL for strategy decisions."""
    def __init__(self, maxsize=100, ttl=3600):
        self.cache = IntelligentCache(max_size=maxsize, default_ttl=ttl)

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache.set(key, value)

class MaestroAgent:
    """Orchestrates strategy selection and execution for the Hephaestus system with weighted strategy selection and fallback."""
    
    def __init__(self, model_config: Dict[str, str], logger, config: Optional[Dict[str, Any]] = None):
        self.model_config = model_config
        self.logger = logger
        self.config = config or {}
        self.strategy_cache = StrategyCache()
        self.strategy_weights = defaultdict(float)
        self.fallback_models = [
            "deepseek/deepseek-chat-v3-0324:free",
            "mistralai/mistral-7b-instruct:free",
            "anthropic/claude-3-haiku:free"
        ]
        self._load_strategy_weights()

    def _load_strategy_weights(self):
        """Initialize strategy weights based on historical performance."""
        # Default weights if no history exists
        self.strategy_weights = {
            "direct_execution": 0.7,
            "parallel_processing": 0.6,
            "meta_cognitive": 0.5,
            "fallback": 0.3
        }
        
        # TODO: Load actual weights from evolution_log.csv analysis
        # This should be implemented after analyzing the log file

    def _update_strategy_weights(self, strategy: str, success: bool):
        """Dynamically adjust strategy weights based on outcomes."""
        adjustment = 0.05 if success else -0.1
        self.strategy_weights[strategy] = max(0.1, min(1.0, self.strategy_weights[strategy] + adjustment))

    def select_strategy(self, context: Dict) -> str:
        """Selects the optimal strategy using weighted random selection."""
        # Normalize weights
        total = sum(self.strategy_weights.values())
        normalized = {k: v/total for k, v in self.strategy_weights.items()}
        
        # Weighted random selection
        rand = random.random()
        cumulative = 0.0
        for strategy, weight in normalized.items():
            cumulative += weight
            if rand < cumulative:
                return strategy

        return "fallback"

    def execute_strategy(self, strategy: str, context: Dict) -> Dict:
        """Executes the selected strategy with proper monitoring."""
        try:
            result = self._execute_strategy_impl(strategy, context)
            self._update_strategy_weights(strategy, True)
            return result
        except Exception as e:
            self.logger.error(f"Strategy {strategy} failed: {str(e)}")
            self._update_strategy_weights(strategy, False)
            raise

    def _execute_strategy_impl(self, strategy: str, context: Dict) -> Dict:
        """Actual strategy implementation logic."""
        # Existing strategy implementations would go here
        # This is a placeholder for the actual implementation
        return {"status": "success", "strategy": strategy}

    def analyze_evolution_log(self, log_path: str) -> Dict[str, float]:
        """Analyzes the evolution log to calculate strategy success rates."""
        # TODO: Implement actual log analysis
        # This should parse the CSV and calculate success rates per strategy
        return {
            "direct_execution": 0.45,
            "parallel_processing": 0.32,
            "meta_cognitive": 0.27,
            "fallback": 0.15
        }

    def choose_strategy(self, action_plan_data: Dict[str, Any], memory_summary: str = "", failed_strategy_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Choose the best strategy for executing the current objective with fallback and retry logic."""
        logs = []
        
        # Try primary model first
        primary_result = self._try_with_model(self.model_config, action_plan_data, memory_summary, failed_strategy_context)
        logs.append(primary_result)
        
        # If primary fails, try fallback models
        if not primary_result.get("success"):
            for fallback_model in self.fallback_models:
                if fallback_model != self.model_config.get("model"):
                    self.logger.info(f"Trying fallback model: {fallback_model}")
                    fallback_config = self.model_config.copy()
                    fallback_config["model"] = fallback_model
                    
                    fallback_result = self._try_with_model(fallback_config, action_plan_data, memory_summary, failed_strategy_context)
                    logs.append(fallback_result)
                    
                    if fallback_result.get("success"):
                        self.logger.info(f"Fallback model {fallback_model} succeeded")
                        break
        
        # If all models fail, use automatic fallback strategy
        if not any(log.get("success") for log in logs):
            self.logger.warning("All models failed, using automatic fallback strategy")
            fallback_log = {
                "success": True,
                "model": "automatic_fallback",
                "parsed_json": {
                    "strategy_key": "NO_OP_STRATEGY",
                    "reasoning": "Automatic fallback due to model failures",
                    "confidence": 0.5
                },
                "raw_response": "Automatic fallback strategy selected",
                "execution_time": 0.1
            }
            logs.append(fallback_log)
        
        return logs

    def _try_with_model(self, model_config: Dict[str, str], action_plan_data: Dict[str, Any], memory_summary: str, failed_strategy_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Try to get strategy decision with a specific model."""
        start_time = datetime.now()
        
        try:
            # Build prompt for strategy selection
            prompt = self._build_strategy_prompt(action_plan_data, memory_summary, failed_strategy_context)
            
            # Call LLM with retry logic
            response, error = call_llm_with_fallback(
                model_config=model_config,
                prompt=prompt,
                temperature=0.7,
                logger=self.logger
            )
            
            if error or response is None:
                raise Exception(f"LLM call failed: {error or 'No response received'}")
            
            # Parse response
            parsed_json = self._parse_strategy_response(response)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            model_name = model_config.get("model", "unknown") if isinstance(model_config, dict) else str(model_config)
            return {
                "success": True,
                "model": model_name,
                "parsed_json": parsed_json,
                "raw_response": response,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            model_name = model_config.get('model', 'unknown') if isinstance(model_config, dict) else str(model_config)
            self.logger.error(f"Model {model_name} failed: {str(e)}")
            
            return {
                "success": False,
                "model": model_name,
                "error": str(e),
                "raw_response": "",
                "execution_time": execution_time
            }

    def _build_strategy_prompt(self, action_plan_data: Dict[str, Any], memory_summary: str, failed_strategy_context: Optional[Dict[str, Any]] = None) -> str:
        """Build a comprehensive prompt for strategy selection."""
        
        # Get available strategies from config
        available_strategies = list(self.config.get("validation_strategies", {}).keys())
        available_strategies.append("CAPACITATION_REQUIRED")
        
        prompt = f"""You are the MaestroAgent, responsible for choosing the best strategy to execute an objective.

AVAILABLE STRATEGIES:
{chr(10).join(f"- {strategy}" for strategy in available_strategies)}

ACTION PLAN DATA:
{json.dumps(action_plan_data, indent=2)}

MEMORY SUMMARY:
{memory_summary[:1000]}...

{f"FAILED STRATEGY CONTEXT: {json.dumps(failed_strategy_context, indent=2)}" if failed_strategy_context else ""}

TASK: Analyze the action plan and choose the most appropriate strategy. Consider:
1. The complexity and risk of the changes
2. Whether validation is needed
3. Whether the changes should be applied immediately or tested first
4. Any previous failures that might inform the decision

RESPONSE FORMAT (JSON only):
{{
    "strategy_key": "CHOSEN_STRATEGY_NAME",
    "reasoning": "Brief explanation of why this strategy was chosen",
    "confidence": 0.85
}}

Choose the strategy and respond with valid JSON:"""

        return prompt

    def _parse_strategy_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured strategy decision."""
        try:
            # Try to extract JSON from response
            response_clean = response.strip()
            
            # Find JSON in the response
            start_idx = response_clean.find('{')
            end_idx = response_clean.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_clean[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                # Validate required fields
                if "strategy_key" not in parsed:
                    raise ValueError("Missing strategy_key in response")
                
                return parsed
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            self.logger.error(f"Failed to parse strategy response: {str(e)}")
            # Return fallback strategy
            return {
                "strategy_key": "NO_OP_STRATEGY",
                "reasoning": f"Fallback due to parsing error: {str(e)}",
                "confidence": 0.3
            }