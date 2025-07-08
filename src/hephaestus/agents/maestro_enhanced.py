"""
Enhanced Maestro Agent - Strategy selection and orchestration with new architecture
"""

import json
import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from hephaestus.agents.enhanced_base import EnhancedBaseAgent
from hephaestus.agents.base import AgentCapability
from hephaestus.utils.llm_manager import llm_call_with_metrics


class MaestroAgentEnhanced(EnhancedBaseAgent):
    """
    Enhanced Maestro Agent using the new modular architecture.
    
    Orchestrates strategy selection and execution with:
    - Weighted strategy selection
    - Dynamic strategy adjustment
    - Fallback mechanisms
    - Performance tracking
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize strategy management
        self.strategy_weights = defaultdict(float)
        self.fallback_models = [
            "deepseek/deepseek-chat-v3-0324:free",
            "mistralai/mistral-7b-instruct:free",
            "anthropic/claude-3-haiku:free"
        ]
        
        # Load or initialize strategy weights
        self._load_strategy_weights()
        
        self.logger.info("🎭 Enhanced Maestro Agent initialized with strategy management")
    
    def get_default_capabilities(self) -> list:
        """Get default capabilities for the Maestro Agent."""
        return [
            AgentCapability.STRATEGY_SELECTION,
            AgentCapability.ORCHESTRATION,
            AgentCapability.DECISION_MAKING,
            AgentCapability.COORDINATION
        ]
    
    async def execute(self, objective: str) -> Tuple[bool, Optional[str]]:
        """
        Execute an objective using strategic orchestration.
        
        Args:
            objective: The objective to execute
            
        Returns:
            Tuple of (success, error_message)
        """
        self.logger.info(f"🎭 Maestro orchestrating: {objective}")
        
        try:
            # Select optimal strategy
            strategy = await self.select_strategy(objective)
            
            if not strategy:
                return False, "Failed to select appropriate strategy"
            
            # Execute with selected strategy
            result = await self.execute_strategy(strategy, objective)
            
            # Update strategy weights based on result
            self._update_strategy_weights(strategy['name'], result['success'])
            
            self.logger.info(f"✅ Maestro orchestration completed: {strategy['name']}")
            return result['success'], result.get('error')
            
        except Exception as e:
            error_message = self.handle_error(e, "execute")
            return False, error_message
    
    @llm_call_with_metrics
    async def select_strategy(self, objective: str) -> Optional[Dict[str, Any]]:
        """
        Select the optimal strategy for the given objective.
        
        Args:
            objective: The objective to create strategy for
            
        Returns:
            Strategy dictionary or None if failed
        """
        # Check cache first
        cache_key = f"strategy_{hash(objective)}"
        cached_strategy = self.get_cached_result(cache_key)
        if cached_strategy:
            self.logger.info("Using cached strategy selection")
            return cached_strategy
        
        # Build strategy selection prompt
        prompt = self._build_strategy_prompt(objective)
        
        # Make LLM call
        strategy_json, error = await self.llm_call_json(prompt)
        
        if error:
            self.logger.error(f"Strategy selection failed: {error}")
            return self._get_fallback_strategy(objective)
        
        if not strategy_json:
            return self._get_fallback_strategy(objective)
        
        # Validate strategy structure
        if not self._validate_strategy(strategy_json):
            return self._get_fallback_strategy(objective)
        
        # Apply strategy weights
        strategy_json = self._apply_strategy_weights(strategy_json)
        
        # Cache the strategy
        self.set_cached_result(cache_key, strategy_json, ttl=1800)
        
        return strategy_json
    
    async def execute_strategy(self, strategy: Dict[str, Any], objective: str) -> Dict[str, Any]:
        """
        Execute the selected strategy.
        
        Args:
            strategy: The strategy to execute
            objective: The original objective
            
        Returns:
            Execution result dictionary
        """
        strategy_name = strategy.get('name', 'unknown')
        
        return await self.execute_with_metrics(
            f"execute_strategy_{strategy_name}",
            self._perform_strategy_execution,
            strategy,
            objective
        )
    
    async def _perform_strategy_execution(self, strategy: Dict[str, Any], objective: str) -> Dict[str, Any]:
        """Perform the actual strategy execution."""
        strategy_name = strategy.get('name', 'unknown')
        
        # Strategy execution logic would be implemented here
        # For now, return a mock result
        
        self.logger.info(f"Executing strategy: {strategy_name}")
        
        # Simulate strategy execution
        success_probability = strategy.get('confidence', 0.8)
        success = random.random() < success_probability
        
        return {
            'success': success,
            'strategy': strategy_name,
            'objective': objective,
            'execution_time': 0.5,
            'details': f"Strategy {strategy_name} executed with {'success' if success else 'failure'}"
        }
    
    def _build_strategy_prompt(self, objective: str) -> str:
        """Build the strategy selection prompt."""
        available_strategies = list(self.strategy_weights.keys())
        
        prompt = f"""
You are the Maestro Agent of the Hephaestus system. Your role is to select the optimal strategy for executing objectives.

[OBJECTIVE]
{objective}

[AVAILABLE STRATEGIES]
{json.dumps(available_strategies, indent=2)}

[CURRENT STRATEGY WEIGHTS]
{json.dumps(dict(self.strategy_weights), indent=2)}

[YOUR TASK]
Select the most appropriate strategy and provide execution parameters.

Return a JSON response with this structure:
{{
    "name": "strategy_name",
    "confidence": 0.8,
    "reasoning": "Why this strategy was selected",
    "parameters": {{
        "priority": "high|medium|low",
        "complexity": "simple|moderate|complex",
        "resources_needed": ["resource1", "resource2"],
        "estimated_duration": "time_estimate"
    }},
    "fallback_strategy": "fallback_strategy_name"
}}

Consider:
- Objective complexity and requirements
- Historical success rates (weights)
- Available resources
- Time constraints
- Risk factors

Respond with ONLY the JSON, no additional text.
"""
        return prompt.strip()
    
    def _validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate strategy structure."""
        required_fields = ['name', 'confidence', 'reasoning', 'parameters']
        
        if not isinstance(strategy, dict):
            return False
        
        for field in required_fields:
            if field not in strategy:
                return False
        
        # Validate confidence is between 0 and 1
        confidence = strategy.get('confidence', 0)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            return False
        
        return True
    
    def _apply_strategy_weights(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Apply strategy weights to adjust confidence."""
        strategy_name = strategy.get('name', '')
        current_weight = self.strategy_weights.get(strategy_name, 0.5)
        
        # Adjust confidence based on historical performance
        original_confidence = strategy.get('confidence', 0.5)
        adjusted_confidence = (original_confidence + current_weight) / 2
        
        strategy['confidence'] = min(1.0, max(0.0, adjusted_confidence))
        strategy['weight_applied'] = current_weight
        
        return strategy
    
    def _get_fallback_strategy(self, objective: str) -> Dict[str, Any]:
        """Get a fallback strategy when primary selection fails."""
        return {
            'name': 'fallback',
            'confidence': 0.3,
            'reasoning': 'Fallback strategy selected due to primary selection failure',
            'parameters': {
                'priority': 'medium',
                'complexity': 'simple',
                'resources_needed': ['basic'],
                'estimated_duration': '5 minutes'
            },
            'fallback_strategy': None
        }
    
    def _load_strategy_weights(self):
        """Load strategy weights from cache or initialize defaults."""
        cached_weights = self.get_cached_result("strategy_weights")
        
        if cached_weights:
            self.strategy_weights = defaultdict(float, cached_weights)
        else:
            # Default weights
            self.strategy_weights = defaultdict(float, {
                "direct_execution": 0.7,
                "parallel_processing": 0.6,
                "meta_cognitive": 0.5,
                "fallback": 0.3,
                "sequential_planning": 0.6,
                "adaptive_learning": 0.4
            })
        
        self.logger.info(f"Loaded {len(self.strategy_weights)} strategy weights")
    
    def _update_strategy_weights(self, strategy: str, success: bool):
        """Update strategy weights based on execution results."""
        current_weight = self.strategy_weights[strategy]
        
        # Learning rate
        alpha = 0.1
        
        if success:
            # Increase weight for successful strategies
            self.strategy_weights[strategy] = min(1.0, current_weight + alpha)
        else:
            # Decrease weight for failed strategies
            self.strategy_weights[strategy] = max(0.0, current_weight - alpha)
        
        # Cache updated weights
        self.set_cached_result("strategy_weights", dict(self.strategy_weights), ttl=86400)
        
        self.logger.debug(f"Updated strategy weight: {strategy} -> {self.strategy_weights[strategy]}")
    
    def get_strategy_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive strategy performance dashboard."""
        return {
            'strategy_weights': dict(self.strategy_weights),
            'total_strategies': len(self.strategy_weights),
            'top_strategy': max(self.strategy_weights.items(), key=lambda x: x[1]) if self.strategy_weights else None,
            'fallback_models': self.fallback_models,
            'cache_stats': self.get_cache_stats()
        }
    
    async def analyze_strategy_performance(self) -> Dict[str, Any]:
        """Analyze strategy performance and provide recommendations."""
        dashboard = self.get_strategy_dashboard()
        
        return await self.execute_with_metrics(
            "analyze_strategy_performance",
            self._perform_strategy_analysis,
            dashboard
        )
    
    async def _perform_strategy_analysis(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed strategy analysis."""
        weights = dashboard.get('strategy_weights', {})
        
        if not weights:
            return {'analysis': 'No strategy data available', 'recommendations': []}
        
        # Calculate statistics
        avg_weight = sum(weights.values()) / len(weights)
        max_weight = max(weights.values())
        min_weight = min(weights.values())
        
        # Generate recommendations
        recommendations = []
        
        if max_weight - min_weight > 0.5:
            recommendations.append("High variance in strategy performance - consider rebalancing")
        
        if avg_weight < 0.4:
            recommendations.append("Overall strategy performance is low - review strategy selection logic")
        
        underperforming = [name for name, weight in weights.items() if weight < 0.3]
        if underperforming:
            recommendations.append(f"Consider reviewing underperforming strategies: {', '.join(underperforming)}")
        
        return {
            'analysis': {
                'average_weight': avg_weight,
                'max_weight': max_weight,
                'min_weight': min_weight,
                'variance': max_weight - min_weight,
                'total_strategies': len(weights)
            },
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }