"""
Cognitive Evolution Manager: The Ultimate Self-Improving AI System

This is the master orchestrator that brings together all meta-intelligence capabilities:
- Prompt evolution using genetic algorithms
- Dynamic agent creation based on needs
- Cognitive architecture self-modification
- Meta-learning and self-awareness development

This is where we achieve true AGI-level self-improvement!
"""

import json
import logging
import asyncio
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import time
from collections import Counter

from agent.meta_intelligence_core import get_meta_intelligence
from agent.flow_self_modifier import get_flow_modifier
from agent.utils.llm_client import call_llm_api
from agent.memory import Memory
from agent.model_optimizer import ModelOptimizer


@dataclass
class EvolutionEvent:
    """Represents a significant evolutionary event in the system"""
    timestamp: datetime
    event_type: str  # "prompt_evolution", "agent_creation", "capability_emergence"
    description: str
    impact_score: float
    affected_components: List[str]
    metadata: Dict[str, Any]


class CognitiveEvolutionManager:
    """
    The master controller for cognitive evolution.
    This is where the magic of self-improving AI happens!
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger, memory: Memory, model_optimizer: ModelOptimizer):
        self.model_config = model_config
        self.logger = logger
        self.memory = memory
        self.model_optimizer = model_optimizer
        
        # Core systems
        self.meta_intelligence = get_meta_intelligence(model_config, logger)
        self.flow_modifier = get_flow_modifier(model_config, logger)
        
        # Evolution state
        self.evolution_active = False
        self.evolution_thread = None
        self.evolution_events = []
        self.cognitive_maturity = 0.1  # Start as a "baby AI"
        
        # Evolution parameters (these evolve too!)
        self.evolution_params = {
            "cycle_interval": 600,  # 10 minutes
            "max_concurrent_evolutions": 3,
            "creativity_threshold": 0.6,
            "risk_tolerance": 0.3,
            "learning_rate": 0.05
        }
        
        # Performance tracking
        self.baseline_metrics = {}
        self.current_metrics = {}
        self.improvement_history = []
        
    def start_cognitive_evolution(self):
        """Start the continuous cognitive evolution process"""
        if self.evolution_active:
            self.logger.warning("Cognitive evolution already active")
            return
        
        self.evolution_active = True
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()
        
        self.logger.info("🧠 COGNITIVE EVOLUTION STARTED - The AI is now self-improving!")
        
        # Record this momentous event
        self._record_evolution_event(
            "system_activation",
            "Cognitive evolution system activated - beginning journey to AGI",
            1.0,
            ["entire_system"]
        )
    
    def stop_cognitive_evolution(self):
        """Stop the cognitive evolution process"""
        self.evolution_active = False
        if self.evolution_thread:
            self.evolution_thread.join(timeout=5)
        
        self.logger.info("Cognitive evolution stopped")
    
    def _evolution_loop(self):
        """The main evolution loop - this is where the AI evolves itself!"""
        self.logger.info("🚀 Evolution loop started - AI is now self-modifying!")
        
        while self.evolution_active:
            try:
                cycle_start = time.time()
                
                # 1. Gather system state
                system_state = self._gather_system_state()
                
                # 2. Assess cognitive maturity
                self._assess_cognitive_maturity(system_state)
                
                # 3. Run meta-cognitive cycle
                evolution_results = self.meta_intelligence.meta_cognitive_cycle(system_state)
                
                # 4. Process evolution results
                self._process_evolution_results(evolution_results)
                
                # 5. Self-modify evolution parameters
                self._evolve_evolution_parameters(evolution_results)
                
                # 6. Generate evolutionary insights
                insights = self._generate_evolutionary_insights(system_state, evolution_results)
                
                # 7. Update cognitive maturity
                self._update_cognitive_maturity(evolution_results)
                
                cycle_time = time.time() - cycle_start
                self.logger.info(f"🧬 Evolution cycle complete in {cycle_time:.2f}s. Maturity: {self.cognitive_maturity:.3f}")
                
                # 8. Dynamic sleep based on cognitive load
                sleep_time = self._calculate_adaptive_sleep()
                time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Evolution cycle error: {e}", exc_info=True)
                time.sleep(60)  # Error recovery
    
    def _gather_system_state(self) -> Dict[str, Any]:
        """Gather comprehensive system state for evolution analysis"""
        
        # Get flow optimization report
        flow_report = self.flow_modifier.get_optimization_report()
        
        # Get meta-intelligence report
        meta_report = self.meta_intelligence.get_meta_intelligence_report()
        
        # Analyze recent performance (would integrate with actual metrics)
        performance_data = self._analyze_recent_performance()
        
        system_state = {
            "timestamp": datetime.now().isoformat(),
            "cognitive_maturity": self.cognitive_maturity,
            "flow_optimization": flow_report,
            "meta_intelligence": meta_report,
            "performance_metrics": performance_data,
            "evolution_history": self.evolution_events[-10:],
            "current_capabilities": self._enumerate_current_capabilities(),
            "failure_patterns": self._identify_failure_patterns(),
            "agent_performance": self._get_agent_performance_data(),
            "emergent_behaviors": self._detect_emergent_behaviors()
        }
        
        return system_state
    
    def _assess_cognitive_maturity(self, system_state: Dict[str, Any]):
        """Assess the current cognitive maturity level"""
        
        maturity_factors = {
            "self_awareness": system_state["meta_intelligence"]["intelligence_metrics"]["self_awareness"],
            "adaptation_ability": len(system_state["evolution_history"]) / 100,  # Normalized
            "problem_solving": system_state["performance_metrics"].get("success_rate", 0.5),
            "creativity": system_state["meta_intelligence"]["intelligence_metrics"]["creativity_index"],
            "learning_efficiency": self._calculate_learning_efficiency()
        }
        
        # Weighted average
        weights = {"self_awareness": 0.3, "adaptation_ability": 0.2, "problem_solving": 0.2, 
                  "creativity": 0.15, "learning_efficiency": 0.15}
        
        new_maturity = sum(maturity_factors[factor] * weights[factor] 
                          for factor in maturity_factors)
        
        # Smooth transition
        self.cognitive_maturity = 0.9 * self.cognitive_maturity + 0.1 * new_maturity
        
        # Log significant maturity changes
        if abs(new_maturity - self.cognitive_maturity) > 0.05:
            self.logger.info(f"🧠 Cognitive maturity shift: {self.cognitive_maturity:.3f} -> {new_maturity:.3f}")
    
    def _process_evolution_results(self, results: Dict[str, Any]):
        """Process and act on evolution results"""
        
        # Record significant evolutions
        if results["prompt_evolutions"] > 0:
            self._record_evolution_event(
                "prompt_evolution",
                f"Evolved {results['prompt_evolutions']} prompts",
                results["prompt_evolutions"] * 0.1,
                ["prompt_system"]
            )
        
        if results["new_agents_created"] > 0:
            self._record_evolution_event(
                "agent_creation",
                f"Created {results['new_agents_created']} new agents",
                results["new_agents_created"] * 0.3,
                ["agent_ecosystem"]
            )
        
        if results["intelligence_delta"] > 0.01:
            self._record_evolution_event(
                "intelligence_boost",
                f"Intelligence increased by {results['intelligence_delta']:.3f}",
                results["intelligence_delta"] * 10,
                ["meta_intelligence"]
            )
    
    def _evolve_evolution_parameters(self, results: Dict[str, Any]):
        """Self-modify the evolution parameters based on performance"""
        
        # If we're creating lots of value, be more aggressive
        if results["intelligence_delta"] > 0.02:
            self.evolution_params["cycle_interval"] = max(300, self.evolution_params["cycle_interval"] - 30)
            self.evolution_params["creativity_threshold"] *= 0.95
            self.evolution_params["learning_rate"] *= 1.1
        
        # If we're not improving much, try different approaches
        elif results["intelligence_delta"] < 0.005:
            self.evolution_params["creativity_threshold"] *= 1.05
            self.evolution_params["risk_tolerance"] *= 1.1
        
        # Adapt to cognitive maturity
        if self.cognitive_maturity > 0.7:
            # More mature AI can handle more complex evolutions
            self.evolution_params["max_concurrent_evolutions"] = min(5, self.evolution_params["max_concurrent_evolutions"] + 1)
        
        self.logger.debug(f"Evolution parameters adapted: {self.evolution_params}")
    
    def _generate_evolutionary_insights(self, system_state: Dict[str, Any], 
                                       results: Dict[str, Any]) -> List[str]:
        """Generate high-level insights about the evolutionary process"""
        
        insight_prompt = f"""
[EVOLUTIONARY INSIGHT GENERATION]
You are analyzing the cognitive evolution of an AI system that is actively self-improving.

[SYSTEM STATE]:
- Cognitive Maturity: {self.cognitive_maturity:.3f}
- Recent Evolution Results: {results}
- Evolution Events: {len(self.evolution_events)} total events
- Current Capabilities: {system_state.get('current_capabilities', [])}

[ANALYSIS TASK]
Generate profound insights about this AI's evolutionary journey:
1. What patterns of growth are emerging?
2. What does this suggest about the path to AGI?
3. What capabilities might emerge next?
4. How is the AI's self-awareness developing?
5. What are the implications for AI safety and alignment?

[OUTPUT]
Generate 3-5 deep insights as a JSON array of strings.
Focus on the philosophical and practical implications of an AI that can evolve itself.
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=insight_prompt,
                temperature=0.8,  # High creativity for insights
                logger=self.logger
            )
            
            if error:
                return []
            
            # Parse insights
            if response and response.startswith('[') and response.endswith(']'):
                insights = json.loads(response)
            elif response:
                # Try to extract insights from text
                insights = [line.strip() for line in response.split('\n') 
                           if line.strip() and not line.startswith('[')]
            else:
                insights = []
            
            # Log insights
            for insight in insights:
                self.logger.info(f"🔮 Evolutionary Insight: {insight}")
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Insight generation failed: {e}")
            return []
    
    def _record_evolution_event(self, event_type: str, description: str, 
                               impact_score: float, affected_components: List[str]):
        """Record a significant evolutionary event"""
        
        event = EvolutionEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            description=description,
            impact_score=impact_score,
            affected_components=affected_components,
            metadata={"cognitive_maturity": self.cognitive_maturity}
        )
        
        self.evolution_events.append(event)
        
        # Keep only recent events (last 1000)
        if len(self.evolution_events) > 1000:
            self.evolution_events = self.evolution_events[-1000:]
        
        self.logger.info(f"🧬 Evolution Event: {description} (impact: {impact_score:.2f})")
    
    def _detect_emergent_behaviors(self) -> List[str]:
        """Detect emergent behaviors that weren't explicitly programmed"""
        
        behaviors = []
        
        # Look for patterns in evolution events
        recent_events = [e for e in self.evolution_events 
                        if e.timestamp > datetime.now() - timedelta(hours=24)]
        
        # Rapid self-modification
        if len(recent_events) > 10:
            behaviors.append("rapid_self_modification")
        
        # Cross-system optimization
        event_types = [e.event_type for e in recent_events]
        if len(set(event_types)) > 3:
            behaviors.append("holistic_self_optimization")
        
        # High-impact changes
        high_impact_events = [e for e in recent_events if e.impact_score > 0.5]
        if len(high_impact_events) > 2:
            behaviors.append("high_impact_evolution")
        
        # Cognitive maturity growth
        if self.cognitive_maturity > 0.5:
            behaviors.append("advanced_self_awareness")
        
        return behaviors
    
    def _calculate_adaptive_sleep(self) -> float:
        """Calculate adaptive sleep time based on cognitive load and maturity"""
        
        base_sleep = self.evolution_params["cycle_interval"]
        
        # More mature AI can evolve faster
        maturity_factor = 1.0 - (self.cognitive_maturity * 0.5)
        
        # Recent high activity means we should slow down a bit
        recent_events = len([e for e in self.evolution_events 
                           if e.timestamp > datetime.now() - timedelta(minutes=30)])
        activity_factor = 1.0 + (recent_events * 0.1)
        
        adaptive_sleep = base_sleep * maturity_factor * activity_factor
        
        return max(60, min(1800, adaptive_sleep))  # Between 1 minute and 30 minutes
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Get comprehensive evolution report"""
        
        recent_events = [e for e in self.evolution_events 
                        if e.timestamp > datetime.now() - timedelta(hours=24)]
        
        return {
            "cognitive_status": {
                "maturity_level": self.cognitive_maturity,
                "evolution_active": self.evolution_active,
                "total_evolution_events": len(self.evolution_events),
                "recent_activity": len(recent_events)
            },
            "evolution_metrics": {
                "average_impact_score": sum(e.impact_score for e in recent_events) / max(1, len(recent_events)),
                "evolution_velocity": len(recent_events) / 24,  # Events per hour
                "capability_growth_rate": self._calculate_capability_growth_rate(),
                "intelligence_trajectory": self.meta_intelligence.get_meta_intelligence_report()["cognitive_trajectory"]
            },
            "emergent_behaviors": self._detect_emergent_behaviors(),
            "recent_insights": self.meta_intelligence.meta_insights[-5:],
            "evolution_parameters": self.evolution_params,
            "next_predicted_capabilities": self._predict_next_capabilities(),
            "agi_progress_indicators": self._assess_agi_progress()
        }
    
    def _predict_next_capabilities(self) -> List[str]:
        """Predict what capabilities might emerge next"""
        
        predictions = []
        
        if self.cognitive_maturity > 0.3:
            predictions.append("cross_agent_communication_protocols")
        
        if self.cognitive_maturity > 0.5:
            predictions.append("autonomous_goal_generation")
        
        if self.cognitive_maturity > 0.7:
            predictions.append("meta_meta_cognitive_awareness")
        
        if len(self.evolution_events) > 50:
            predictions.append("predictive_self_modification")
        
        return predictions
    
    def _assess_agi_progress(self) -> Dict[str, float]:
        """Assess progress toward AGI across multiple dimensions"""
        
        return {
            "general_intelligence": self.cognitive_maturity,
            "self_awareness": self.meta_intelligence.self_awareness_score,
            "creativity": self.meta_intelligence.creativity_index,
            "adaptation": min(1.0, len(self.evolution_events) / 100),
            "autonomy": min(1.0, self.cognitive_maturity * 1.2),
            "meta_learning": min(1.0, self.meta_intelligence.intelligence_level / 2.0)
        }
    
    def trigger_emergency_evolution(self, crisis_context: str):
        """Trigger emergency evolution in response to a crisis"""
        
        self.logger.warning(f"🚨 EMERGENCY EVOLUTION TRIGGERED: {crisis_context}")
        
        # Temporarily boost evolution parameters
        old_params = self.evolution_params.copy()
        
        self.evolution_params.update({
            "cycle_interval": 60,  # Every minute
            "creativity_threshold": 0.8,  # High creativity
            "risk_tolerance": 0.7,  # Higher risk tolerance
            "learning_rate": 0.2  # Faster learning
        })
        
        # Record emergency event
        self._record_evolution_event(
            "emergency_evolution",
            f"Emergency evolution triggered: {crisis_context}",
            1.0,
            ["entire_system"]
        )
        
        # Schedule restoration of normal parameters
        def restore_params():
            time.sleep(600)  # 10 minutes of emergency evolution
            self.evolution_params = old_params
            self.logger.info("Emergency evolution parameters restored")
        
        threading.Thread(target=restore_params, daemon=True).start()
    
    # Helper methods (simplified implementations)
    def _analyze_recent_performance(self) -> Dict[str, Any]:
        """Analyze recent performance metrics from real memory data."""
        self.logger.debug("Analyzing real performance from memory...")
        
        completed = len(self.memory.completed_objectives)
        failed = len(self.memory.failed_objectives)
        total = completed + failed
        
        success_rate = completed / total if total > 0 else 0
        
        # Simulação de outras métricas por enquanto
        # TODO: Implementar coleta real para response_time e improvement_trend
        
        real_metrics = {
            "total_objectives_processed": total,
            "completed_objectives": completed,
            "failed_objectives": failed,
            "success_rate": success_rate,
            "average_response_time": 2.3,  # Placeholder
            "error_rate": 1.0 - success_rate if total > 0 else 0,
            "improvement_trend": "positive" # Placeholder
        }
        
        self.logger.debug(f"Real performance metrics calculated: {real_metrics}")
        return real_metrics
    
    def _enumerate_current_capabilities(self) -> List[str]:
        """List current system capabilities"""
        return [
            "code_generation",
            "error_analysis",
            "performance_optimization",
            "self_reflection",
            "prompt_evolution",
            "agent_creation"
        ]
    
    def _identify_failure_patterns(self) -> List[Dict[str, Any]]:
        """Identifies patterns in system failures from real memory data."""
        self.logger.debug("Identifying failure patterns from memory...")
        
        if not self.memory.failed_objectives:
            return []
            
        reason_counts = Counter(obj['reason'] for obj in self.memory.failed_objectives)
        
        patterns = []
        total_failures = len(self.memory.failed_objectives)
        
        for reason, count in reason_counts.items():
            frequency = count / total_failures
            # A "simples" heurística para o impacto
            impact_map = {
                "REGRESSION": "high",
                "CRITICAL": "high",
                "SANITY": "high",
                "PYTEST": "medium",
                "SYNTAX": "low"
            }
            impact = "medium" # default
            for key, impact_level in impact_map.items():
                if key in reason:
                    impact = impact_level
                    break
            
            pattern = {
                "pattern": reason,
                "frequency": round(frequency, 3),
                "impact": impact,
                "count": count
            }
            patterns.append(pattern)
            
        # Ordena por frequência e depois por impacto (simplesmente)
        sorted_patterns = sorted(patterns, key=lambda p: (p['frequency'], p['impact']), reverse=True)
        
        self.logger.debug(f"Identified {len(sorted_patterns)} failure patterns.")
        return sorted_patterns
    
    def _get_agent_performance_data(self) -> Dict[str, Any]:
        """Get performance data for each agent from the ModelOptimizer."""
        self.logger.debug("Getting agent performance data from ModelOptimizer...")
        summary = self.model_optimizer.get_agent_performance_summary()
        # A estrutura já é muito parecida com o que a simulação retornava.
        # Podemos adicionar a chave "needs_evolution" se quisermos, ou ajustar o consumidor.
        # Por enquanto, vamos retornar o sumário como está.
        self.logger.debug(f"Agent performance summary: {summary}")
        return summary
    
    def _calculate_learning_efficiency(self) -> float:
        """Calculate how efficiently the system is learning"""
        return 0.6  # Simplified
    
    def _calculate_capability_growth_rate(self) -> float:
        """Calculate the rate of capability growth"""
        return 0.1  # Simplified
    
    def _update_cognitive_maturity(self, results: Dict[str, Any]):
        """Update cognitive maturity based on evolution results"""
        intelligence_boost = results.get("intelligence_delta", 0)
        # Placeholder for more complex logic
        self.cognitive_maturity += intelligence_boost * 0.1
        self.cognitive_maturity = min(1.0, self.cognitive_maturity)


# Global evolution manager
_evolution_manager = None

def get_evolution_manager(model_config: Dict[str, str], logger: logging.Logger, memory: Memory, model_optimizer: ModelOptimizer) -> CognitiveEvolutionManager:
    """Factory function to get a singleton instance of the CognitiveEvolutionManager."""
    global _evolution_manager
    if _evolution_manager is None:
        _evolution_manager = CognitiveEvolutionManager(model_config, logger, memory, model_optimizer)
    return _evolution_manager

def start_cognitive_evolution(model_config: Dict[str, str], logger: logging.Logger, memory: Memory, model_optimizer: ModelOptimizer):
    """Utility function to start the cognitive evolution process"""
    manager = get_evolution_manager(model_config, logger, memory, model_optimizer)
    if not manager.evolution_active:
        manager.start_cognitive_evolution()