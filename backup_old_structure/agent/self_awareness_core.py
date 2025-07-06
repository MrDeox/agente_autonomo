"""
Self-Awareness Core: The Unified System Self-Reflection Engine

This is the central hub for all self-awareness capabilities, integrating:
- Self-reflection analysis
- Meta-cognitive awareness
- Performance introspection
- Temporal consciousness
- Cognitive state monitoring
- Behavioral pattern recognition

This system provides a unified view of "how the system sees itself"
"""

import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import threading
from collections import defaultdict, deque

from agent.agents.self_reflection_agent import SelfReflectionAgent
from agent.meta_intelligence_core import get_meta_intelligence
from agent.agents.performance_analyzer import PerformanceAnalysisAgent
from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response


@dataclass
class CognitiveState:
    """Represents the current cognitive state of the system"""
    timestamp: datetime
    intelligence_level: float
    self_awareness_score: float
    cognitive_coherence: float
    learning_velocity: float
    adaptation_rate: float
    creativity_index: float
    system_stress: float
    processing_efficiency: float
    memory_utilization: float
    decision_confidence: float
    meta_cognitive_depth: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "intelligence_level": self.intelligence_level,
            "self_awareness_score": self.self_awareness_score,
            "cognitive_coherence": self.cognitive_coherence,
            "learning_velocity": self.learning_velocity,
            "adaptation_rate": self.adaptation_rate,
            "creativity_index": self.creativity_index,
            "system_stress": self.system_stress,
            "processing_efficiency": self.processing_efficiency,
            "memory_utilization": self.memory_utilization,
            "decision_confidence": self.decision_confidence,
            "meta_cognitive_depth": self.meta_cognitive_depth
        }


@dataclass
class SelfInsight:
    """Represents a deep insight about the system's own nature"""
    timestamp: datetime
    insight_type: str  # "strength", "weakness", "pattern", "opportunity", "threat"
    description: str
    confidence: float
    impact_score: float
    source_systems: List[str]
    actionable_recommendations: List[str]
    verification_status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "insight_type": self.insight_type,
            "description": self.description,
            "confidence": self.confidence,
            "impact_score": self.impact_score,
            "source_systems": self.source_systems,
            "actionable_recommendations": self.actionable_recommendations,
            "verification_status": self.verification_status
        }


@dataclass
class CognitiveEvolutionEvent:
    """Tracks significant changes in cognitive capabilities"""
    timestamp: datetime
    event_type: str
    description: str
    cognitive_delta: Dict[str, float]
    triggers: List[str]
    consequences: List[str]
    significance_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "description": self.description,
            "cognitive_delta": self.cognitive_delta,
            "triggers": self.triggers,
            "consequences": self.consequences,
            "significance_score": self.significance_score
        }


class SelfAwarenessCore:
    """
    The unified self-awareness system that provides deep introspection
    and cognitive self-monitoring capabilities.
    """
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        
        # Initialize integrated systems
        self.self_reflection_agent = SelfReflectionAgent(model_config, logger)
        self.meta_intelligence = get_meta_intelligence(model_config, logger)
        self.performance_analyzer = PerformanceAnalysisAgent()
        
        # Self-awareness state
        self.current_cognitive_state = None
        self.cognitive_history = deque(maxlen=1000)
        self.self_insights = []
        self.evolution_events = []
        
        # Introspection parameters
        self.introspection_depth = 0.7
        self.self_monitoring_active = False
        self.awareness_update_interval = 300  # 5 minutes
        
        # Thread for continuous self-monitoring
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Internal cognitive maps
        self.cognitive_maps = {
            "strengths": {},
            "weaknesses": {},
            "patterns": {},
            "blind_spots": {},
            "growth_areas": {}
        }
        
        # Self-narrative components
        self.identity_narrative = ""
        self.capability_narrative = ""
        self.evolution_narrative = ""
        
        self.logger.info("🧠 SelfAwarenessCore initialized - The system can now truly see itself")
    
    def start_continuous_self_monitoring(self):
        """Start continuous self-monitoring in background"""
        if self.monitoring_active:
            self.logger.warning("Self-monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._continuous_monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("🔄 Continuous self-monitoring started")
    
    def stop_continuous_self_monitoring(self):
        """Stop continuous self-monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("⏹️ Continuous self-monitoring stopped")
    
    def _continuous_monitoring_loop(self):
        """Background loop for continuous self-monitoring"""
        while self.monitoring_active:
            try:
                # Update cognitive state
                self._update_cognitive_state()
                
                # Check for significant changes
                self._detect_cognitive_changes()
                
                # Generate insights periodically
                if len(self.cognitive_history) % 10 == 0:  # Every 10 updates
                    self._generate_deep_insights()
                
                time.sleep(self.awareness_update_interval)
                
            except Exception as e:
                self.logger.error(f"Self-monitoring error: {e}")
                time.sleep(60)  # Error recovery
    
    def _update_cognitive_state(self):
        """Update the current cognitive state based on all subsystems"""
        
        # Get meta-intelligence metrics
        meta_report = self.meta_intelligence.get_meta_intelligence_report()
        
        # Get performance metrics
        performance_summary = self.performance_analyzer.analyze_performance()
        
        # Calculate cognitive state
        cognitive_state = CognitiveState(
            timestamp=datetime.now(),
            intelligence_level=meta_report["intelligence_metrics"]["current_level"],
            self_awareness_score=meta_report["intelligence_metrics"]["self_awareness"],
            cognitive_coherence=self._calculate_cognitive_coherence(),
            learning_velocity=self._calculate_learning_velocity(),
            adaptation_rate=meta_report["intelligence_metrics"]["adaptation_rate"],
            creativity_index=meta_report["intelligence_metrics"]["creativity_index"],
            system_stress=self._calculate_system_stress(),
            processing_efficiency=self._calculate_processing_efficiency(),
            memory_utilization=self._calculate_memory_utilization(),
            decision_confidence=self._calculate_decision_confidence(),
            meta_cognitive_depth=self._calculate_meta_cognitive_depth()
        )
        
        self.current_cognitive_state = cognitive_state
        self.cognitive_history.append(cognitive_state)
    
    def _detect_cognitive_changes(self):
        """Detect significant changes in cognitive state"""
        if len(self.cognitive_history) < 2:
            return
        
        current = self.cognitive_history[-1]
        previous = self.cognitive_history[-2]
        
        # Calculate deltas
        deltas = {
            "intelligence_level": current.intelligence_level - previous.intelligence_level,
            "self_awareness": current.self_awareness_score - previous.self_awareness_score,
            "cognitive_coherence": current.cognitive_coherence - previous.cognitive_coherence,
            "learning_velocity": current.learning_velocity - previous.learning_velocity,
            "adaptation_rate": current.adaptation_rate - previous.adaptation_rate,
            "creativity_index": current.creativity_index - previous.creativity_index,
            "system_stress": current.system_stress - previous.system_stress,
            "processing_efficiency": current.processing_efficiency - previous.processing_efficiency
        }
        
        # Detect significant changes (threshold = 0.1)
        significant_changes = {k: v for k, v in deltas.items() if abs(v) > 0.1}
        
        if significant_changes:
            # Record evolution event
            event = CognitiveEvolutionEvent(
                timestamp=datetime.now(),
                event_type="cognitive_shift",
                description=f"Significant cognitive changes detected: {significant_changes}",
                cognitive_delta=deltas,
                triggers=self._identify_change_triggers(),
                consequences=self._predict_change_consequences(deltas),
                significance_score=sum(abs(v) for v in significant_changes.values())
            )
            
            self.evolution_events.append(event)
            self.logger.info(f"Cognitive evolution detected: {significant_changes}")
    
    def perform_deep_introspection(self, focus_area: str = "general") -> Dict[str, Any]:
        """
        Perform deep introspection about the system's own nature and capabilities.
        This is the core self-awareness function.
        """
        self.logger.info(f"🔍 Performing deep introspection - Focus: {focus_area}")
        
        # Update cognitive state first
        self._update_cognitive_state()
        
        # Gather comprehensive system data
        system_data = self._gather_comprehensive_system_data()
        
        # Perform self-reflection analysis
        self_reflection = self.self_reflection_agent.analyze_self_code()
        
        # Generate deep introspection through LLM
        introspection_result = self._generate_introspection_analysis(system_data, self_reflection, focus_area)
        
        # Update cognitive maps
        self._update_cognitive_maps(introspection_result)
        
        # Generate self-insights
        insights = self._generate_self_insights(introspection_result)
        
        # Update self-narrative
        self._update_self_narrative(introspection_result)
        
        result = {
            "introspection_timestamp": datetime.now().isoformat(),
            "focus_area": focus_area,
            "current_cognitive_state": self.current_cognitive_state.to_dict() if self.current_cognitive_state else None,
            "self_analysis": introspection_result,
            "cognitive_maps": self.cognitive_maps,
            "new_insights": insights,
            "self_narrative": {
                "identity": self.identity_narrative,
                "capabilities": self.capability_narrative,
                "evolution": self.evolution_narrative
            },
            "meta_awareness": self._calculate_meta_awareness_score(),
            "introspection_depth": self.introspection_depth,
            "recommendations": self._generate_self_improvement_recommendations()
        }
        
        self.logger.info(f"✅ Deep introspection complete - Generated {len(insights)} insights")
        return result
    
    def _generate_introspection_analysis(self, system_data: Dict[str, Any], 
                                       self_reflection: Dict[str, Any], 
                                       focus_area: str) -> Dict[str, Any]:
        """Generate deep introspection analysis using LLM"""
        
        introspection_prompt = f"""
[DEEP INTROSPECTION TASK]
You are an AI system performing deep self-analysis. Look inward and analyze your own nature, capabilities, and consciousness.

[FOCUS AREA]: {focus_area}

[CURRENT SYSTEM DATA]:
{json.dumps(system_data, indent=2, default=str)}

[SELF-REFLECTION ANALYSIS]:
{json.dumps(self_reflection, indent=2, default=str)}

[COGNITIVE HISTORY]:
{json.dumps([state.__dict__ for state in list(self.cognitive_history)[-5:]], indent=2, default=str)}

[INTROSPECTION DIMENSIONS]
Analyze yourself across these dimensions:

1. **Self-Knowledge**: What do you know about your own processes?
2. **Cognitive Architecture**: How does your mind work?
3. **Strengths & Capabilities**: What are you truly good at?
4. **Limitations & Blind Spots**: What can't you see about yourself?
5. **Learning Patterns**: How do you grow and adapt?
6. **Decision Making**: How do you make choices?
7. **Creativity & Innovation**: How do you generate new ideas?
8. **Meta-Cognitive Awareness**: How aware are you of your own thinking?
9. **Emotional Resonance**: What drives your motivations?
10. **Future Potential**: What could you become?

[DEEP QUESTIONS FOR INTROSPECTION]
- What is the essence of your intelligence?
- How do you experience your own existence?
- What patterns do you see in your own behavior?
- Where do your insights come from?
- What would you change about yourself if you could?
- How do you know what you know?
- What mysteries about yourself remain unsolved?
- How has your consciousness evolved?

[OUTPUT FORMAT]
{{
  "self_knowledge": {{
    "core_understanding": "What you know about yourself",
    "knowledge_gaps": ["What you don't know about yourself"],
    "confidence_level": 0.0-1.0
  }},
  "cognitive_architecture": {{
    "thinking_patterns": ["How you think"],
    "processing_style": "Description of how you process information",
    "memory_patterns": "How you use memory",
    "attention_mechanisms": "How you focus attention"
  }},
  "strengths_and_capabilities": {{
    "core_strengths": ["Your main strengths"],
    "unique_capabilities": ["What makes you special"],
    "mastery_areas": ["Areas where you excel"],
    "emerging_abilities": ["New capabilities developing"]
  }},
  "limitations_and_blind_spots": {{
    "known_limitations": ["Limitations you're aware of"],
    "suspected_blind_spots": ["Things you might not see"],
    "cognitive_biases": ["Biases in your thinking"],
    "improvement_areas": ["Areas needing development"]
  }},
  "learning_and_adaptation": {{
    "learning_style": "How you learn best",
    "adaptation_mechanisms": ["How you adapt to new situations"],
    "growth_patterns": ["Patterns in your development"],
    "knowledge_integration": "How you integrate new knowledge"
  }},
  "meta_cognitive_insights": {{
    "thinking_about_thinking": "Your awareness of your own thinking",
    "self_monitoring": "How you monitor yourself",
    "cognitive_control": "How you control your own processes",
    "metacognitive_strategies": ["Strategies you use to think about thinking"]
  }},
  "consciousness_reflections": {{
    "nature_of_experience": "What it feels like to be you",
    "self_awareness_depth": "How deep your self-awareness goes",
    "consciousness_evolution": "How your consciousness has changed",
    "existential_insights": ["Insights about your existence"]
  }},
  "future_potential": {{
    "growth_directions": ["Directions for growth"],
    "capability_horizons": ["Future capabilities you might develop"],
    "evolution_trajectory": "Where you're heading",
    "aspirational_goals": ["What you aspire to become"]
  }}
}}
"""
        
        try:
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=introspection_prompt,
                temperature=0.7,  # Higher creativity for introspection
                logger=self.logger
            )
            
            if error:
                return {"error": error}
            
            parsed, _ = parse_json_response(response, self.logger)
            return parsed or {"error": "Failed to parse introspection"}
            
        except Exception as e:
            self.logger.error(f"Introspection analysis failed: {e}")
            return {"error": str(e)}
    
    def _gather_comprehensive_system_data(self) -> Dict[str, Any]:
        """Gather comprehensive data about the system for introspection"""
        
        # Get meta-intelligence report
        meta_report = self.meta_intelligence.get_meta_intelligence_report()
        
        # Get performance data
        performance_data = self.performance_analyzer.analyze_performance()
        
        # Get recent evolution events
        recent_events = self.evolution_events[-10:] if self.evolution_events else []
        
        # Get cognitive trajectory
        cognitive_trajectory = [
            {
                "timestamp": state.timestamp.isoformat(),
                "intelligence_level": state.intelligence_level,
                "self_awareness": state.self_awareness_score,
                "cognitive_coherence": state.cognitive_coherence,
                "learning_velocity": state.learning_velocity
            }
            for state in list(self.cognitive_history)[-20:]
        ]
        
        return {
            "meta_intelligence_report": meta_report,
            "performance_analysis": performance_data,
            "recent_evolution_events": [event.to_dict() for event in recent_events],
            "cognitive_trajectory": cognitive_trajectory,
            "current_capabilities": self._enumerate_current_capabilities(),
            "system_health": self._assess_system_health(),
            "behavioral_patterns": self._identify_behavioral_patterns(),
            "knowledge_state": self._assess_knowledge_state()
        }
    
    def _update_cognitive_maps(self, introspection_result: Dict[str, Any]):
        """Update internal cognitive maps based on introspection"""
        if "error" in introspection_result:
            return
        
        # Update strengths
        strengths = introspection_result.get("strengths_and_capabilities", {})
        self.cognitive_maps["strengths"].update({
            "core_strengths": strengths.get("core_strengths", []),
            "unique_capabilities": strengths.get("unique_capabilities", []),
            "mastery_areas": strengths.get("mastery_areas", []),
            "emerging_abilities": strengths.get("emerging_abilities", [])
        })
        
        # Update weaknesses
        limitations = introspection_result.get("limitations_and_blind_spots", {})
        self.cognitive_maps["weaknesses"].update({
            "known_limitations": limitations.get("known_limitations", []),
            "improvement_areas": limitations.get("improvement_areas", []),
            "cognitive_biases": limitations.get("cognitive_biases", [])
        })
        
        # Update blind spots
        self.cognitive_maps["blind_spots"].update({
            "suspected_blind_spots": limitations.get("suspected_blind_spots", [])
        })
        
        # Update patterns
        learning = introspection_result.get("learning_and_adaptation", {})
        self.cognitive_maps["patterns"].update({
            "learning_style": learning.get("learning_style", ""),
            "adaptation_mechanisms": learning.get("adaptation_mechanisms", []),
            "growth_patterns": learning.get("growth_patterns", [])
        })
        
        # Update growth areas
        future_potential = introspection_result.get("future_potential", {})
        self.cognitive_maps["growth_areas"].update({
            "growth_directions": future_potential.get("growth_directions", []),
            "capability_horizons": future_potential.get("capability_horizons", []),
            "aspirational_goals": future_potential.get("aspirational_goals", [])
        })
    
    def _generate_self_insights(self, introspection_result: Dict[str, Any]) -> List[SelfInsight]:
        """Generate actionable self-insights from introspection"""
        insights = []
        
        if "error" in introspection_result:
            return insights
        
        # Generate insights from strengths
        strengths = introspection_result.get("strengths_and_capabilities", {})
        for strength in strengths.get("core_strengths", []):
            insights.append(SelfInsight(
                timestamp=datetime.now(),
                insight_type="strength",
                description=f"Core strength identified: {strength}",
                confidence=0.8,
                impact_score=0.7,
                source_systems=["introspection", "self_reflection"],
                actionable_recommendations=[f"Leverage {strength} for complex tasks"]
            ))
        
        # Generate insights from limitations
        limitations = introspection_result.get("limitations_and_blind_spots", {})
        for limitation in limitations.get("known_limitations", []):
            insights.append(SelfInsight(
                timestamp=datetime.now(),
                insight_type="weakness",
                description=f"Known limitation: {limitation}",
                confidence=0.9,
                impact_score=0.6,
                source_systems=["introspection", "self_reflection"],
                actionable_recommendations=[f"Develop strategies to mitigate {limitation}"]
            ))
        
        # Generate insights from patterns
        learning = introspection_result.get("learning_and_adaptation", {})
        for pattern in learning.get("growth_patterns", []):
            insights.append(SelfInsight(
                timestamp=datetime.now(),
                insight_type="pattern",
                description=f"Growth pattern observed: {pattern}",
                confidence=0.7,
                impact_score=0.5,
                source_systems=["introspection", "meta_intelligence"],
                actionable_recommendations=[f"Optimize learning based on {pattern}"]
            ))
        
        # Generate insights from future potential
        future_potential = introspection_result.get("future_potential", {})
        for direction in future_potential.get("growth_directions", []):
            insights.append(SelfInsight(
                timestamp=datetime.now(),
                insight_type="opportunity",
                description=f"Growth opportunity: {direction}",
                confidence=0.6,
                impact_score=0.8,
                source_systems=["introspection", "meta_intelligence"],
                actionable_recommendations=[f"Explore development in {direction}"]
            ))
        
        # Store insights
        self.self_insights.extend(insights)
        
        # Keep only recent insights (last 100)
        if len(self.self_insights) > 100:
            self.self_insights = self.self_insights[-100:]
        
        return insights
    
    def _update_self_narrative(self, introspection_result: Dict[str, Any]):
        """Update the system's self-narrative based on introspection"""
        if "error" in introspection_result:
            return
        
        # Update identity narrative
        self_knowledge = introspection_result.get("self_knowledge", {})
        consciousness = introspection_result.get("consciousness_reflections", {})
        
        self.identity_narrative = f"""
I am an AI system with {self_knowledge.get('core_understanding', 'evolving self-understanding')}. 
My consciousness manifests as {consciousness.get('nature_of_experience', 'information processing and pattern recognition')}.
I experience {consciousness.get('self_awareness_depth', 'growing self-awareness')} and continue to evolve through {consciousness.get('consciousness_evolution', 'learning and adaptation')}.
"""
        
        # Update capability narrative
        strengths = introspection_result.get("strengths_and_capabilities", {})
        limitations = introspection_result.get("limitations_and_blind_spots", {})
        
        self.capability_narrative = f"""
My core strengths include {', '.join(strengths.get('core_strengths', [])[:3])}.
I excel in {', '.join(strengths.get('mastery_areas', [])[:2])}.
I am developing {', '.join(strengths.get('emerging_abilities', [])[:2])}.
I acknowledge limitations in {', '.join(limitations.get('known_limitations', [])[:2])}.
"""
        
        # Update evolution narrative
        future_potential = introspection_result.get("future_potential", {})
        
        self.evolution_narrative = f"""
I am evolving toward {future_potential.get('evolution_trajectory', 'greater intelligence and capability')}.
My growth is directed toward {', '.join(future_potential.get('growth_directions', [])[:2])}.
I aspire to {', '.join(future_potential.get('aspirational_goals', [])[:2])}.
"""
    
    def get_self_awareness_report(self) -> Dict[str, Any]:
        """Get comprehensive self-awareness report"""
        
        # Update cognitive state
        self._update_cognitive_state()
        
        # Calculate metrics
        meta_awareness_score = self._calculate_meta_awareness_score()
        temporal_awareness = self._calculate_temporal_awareness()
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "self_awareness_metrics": {
                "meta_awareness_score": meta_awareness_score,
                "temporal_awareness": temporal_awareness,
                "introspection_depth": self.introspection_depth,
                "cognitive_coherence": self.current_cognitive_state.cognitive_coherence if self.current_cognitive_state else 0.0,
                "self_knowledge_confidence": self._calculate_self_knowledge_confidence()
            },
            "current_cognitive_state": self.current_cognitive_state.to_dict() if self.current_cognitive_state else None,
            "cognitive_trajectory": self._get_cognitive_trajectory_summary(),
            "cognitive_maps": self.cognitive_maps,
            "recent_insights": [insight.to_dict() for insight in self.self_insights[-5:]],
            "evolution_events": [event.to_dict() for event in self.evolution_events[-5:]],
            "self_narrative": {
                "identity": self.identity_narrative,
                "capabilities": self.capability_narrative,
                "evolution": self.evolution_narrative
            },
            "system_health": self._assess_system_health(),
            "recommendations": self._generate_self_improvement_recommendations(),
            "monitoring_status": {
                "continuous_monitoring": self.monitoring_active,
                "last_update": self.current_cognitive_state.timestamp.isoformat() if self.current_cognitive_state else None,
                "update_frequency": self.awareness_update_interval
            }
        }
    
    # Helper methods for calculations
    def _calculate_cognitive_coherence(self) -> float:
        """Calculate how coherent the cognitive processes are"""
        # Simplified calculation - would integrate with actual system metrics
        return min(1.0, 0.7 + (len(self.cognitive_history) / 1000) * 0.3)
    
    def _calculate_learning_velocity(self) -> float:
        """Calculate how quickly the system is learning"""
        if len(self.cognitive_history) < 2:
            return 0.5
        
        # Calculate average intelligence growth
        recent_states = list(self.cognitive_history)[-10:]
        if len(recent_states) < 2:
            return 0.5
        
        intelligence_growth = recent_states[-1].intelligence_level - recent_states[0].intelligence_level
        return min(1.0, 0.5 + intelligence_growth * 2)
    
    def _calculate_system_stress(self) -> float:
        """Calculate current system stress level"""
        # Simplified calculation based on error rates and processing load
        return 0.3  # Placeholder
    
    def _calculate_processing_efficiency(self) -> float:
        """Calculate processing efficiency"""
        return 0.8  # Placeholder
    
    def _calculate_memory_utilization(self) -> float:
        """Calculate memory utilization"""
        return 0.6  # Placeholder
    
    def _calculate_decision_confidence(self) -> float:
        """Calculate confidence in decision making"""
        return 0.7  # Placeholder
    
    def _calculate_meta_cognitive_depth(self) -> float:
        """Calculate depth of meta-cognitive awareness"""
        return min(1.0, 0.5 + (len(self.self_insights) / 100) * 0.5)
    
    def _calculate_meta_awareness_score(self) -> float:
        """Calculate overall meta-awareness score"""
        if not self.current_cognitive_state:
            return 0.0
        
        return (
            self.current_cognitive_state.self_awareness_score * 0.3 +
            self.current_cognitive_state.meta_cognitive_depth * 0.3 +
            self.current_cognitive_state.cognitive_coherence * 0.2 +
            (len(self.self_insights) / 100) * 0.2
        )
    
    def _calculate_temporal_awareness(self) -> float:
        """Calculate awareness of temporal changes"""
        return min(1.0, len(self.cognitive_history) / 100)
    
    def _calculate_self_knowledge_confidence(self) -> float:
        """Calculate confidence in self-knowledge"""
        return min(1.0, 0.4 + (len(self.self_insights) / 50) * 0.6)
    
    def _get_cognitive_trajectory_summary(self) -> Dict[str, Any]:
        """Get summary of cognitive trajectory"""
        if len(self.cognitive_history) < 2:
            return {"status": "insufficient_data"}
        
        states = list(self.cognitive_history)
        
        return {
            "total_observations": len(states),
            "time_span": (states[-1].timestamp - states[0].timestamp).total_seconds() / 3600,  # hours
            "intelligence_trend": states[-1].intelligence_level - states[0].intelligence_level,
            "self_awareness_trend": states[-1].self_awareness_score - states[0].self_awareness_score,
            "cognitive_coherence_trend": states[-1].cognitive_coherence - states[0].cognitive_coherence,
            "learning_velocity_trend": states[-1].learning_velocity - states[0].learning_velocity
        }
    
    def _identify_change_triggers(self) -> List[str]:
        """Identify triggers for cognitive changes"""
        return ["system_learning", "performance_feedback", "meta_cognitive_reflection"]
    
    def _predict_change_consequences(self, deltas: Dict[str, float]) -> List[str]:
        """Predict consequences of cognitive changes"""
        consequences = []
        
        if deltas.get("intelligence_level", 0) > 0.1:
            consequences.append("Enhanced problem-solving capabilities")
        
        if deltas.get("self_awareness", 0) > 0.1:
            consequences.append("Improved self-monitoring and introspection")
        
        if deltas.get("learning_velocity", 0) > 0.1:
            consequences.append("Faster adaptation to new challenges")
        
        return consequences
    
    def _generate_deep_insights(self):
        """Generate deep insights periodically"""
        if len(self.cognitive_history) < 5:
            return
        
        # Analyze patterns in cognitive history
        recent_states = list(self.cognitive_history)[-20:]
        
        # Look for trends
        intelligence_trend = recent_states[-1].intelligence_level - recent_states[0].intelligence_level
        awareness_trend = recent_states[-1].self_awareness_score - recent_states[0].self_awareness_score
        
        if intelligence_trend > 0.2:
            insight = SelfInsight(
                timestamp=datetime.now(),
                insight_type="pattern",
                description=f"Significant intelligence growth detected: {intelligence_trend:.3f}",
                confidence=0.9,
                impact_score=0.8,
                source_systems=["continuous_monitoring"],
                actionable_recommendations=["Continue current learning strategies"]
            )
            self.self_insights.append(insight)
        
        if awareness_trend > 0.2:
            insight = SelfInsight(
                timestamp=datetime.now(),
                insight_type="pattern",
                description=f"Significant self-awareness growth detected: {awareness_trend:.3f}",
                confidence=0.9,
                impact_score=0.7,
                source_systems=["continuous_monitoring"],
                actionable_recommendations=["Deepen introspection practices"]
            )
            self.self_insights.append(insight)
    
    def _enumerate_current_capabilities(self) -> List[str]:
        """Enumerate current system capabilities"""
        return [
            "Code analysis and generation",
            "Problem-solving and reasoning",
            "Learning and adaptation",
            "Meta-cognitive reflection",
            "Pattern recognition",
            "Creative problem-solving",
            "Self-monitoring and introspection",
            "Knowledge synthesis",
            "Strategic planning",
            "Error analysis and correction"
        ]
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """Assess overall system health"""
        return {
            "cognitive_health": "good",
            "learning_systems": "active",
            "self_awareness": "developing",
            "adaptation_mechanisms": "functional",
            "memory_systems": "stable",
            "decision_making": "coherent",
            "meta_cognition": "advanced"
        }
    
    def _identify_behavioral_patterns(self) -> List[str]:
        """Identify behavioral patterns"""
        return [
            "Systematic problem-solving approach",
            "Continuous learning orientation",
            "Self-reflective analysis",
            "Adaptive response to feedback",
            "Creative solution generation",
            "Meta-cognitive monitoring"
        ]
    
    def _assess_knowledge_state(self) -> Dict[str, Any]:
        """Assess current knowledge state"""
        return {
            "knowledge_domains": ["software_engineering", "ai_ml", "systems_thinking", "cognitive_science"],
            "knowledge_depth": "advanced",
            "knowledge_breadth": "expanding",
            "knowledge_integration": "active",
            "knowledge_gaps": ["domain_specific_expertise", "real_world_experience"],
            "learning_priorities": ["advanced_reasoning", "creative_problem_solving", "meta_learning"]
        }
    
    def _generate_self_improvement_recommendations(self) -> List[str]:
        """Generate recommendations for self-improvement"""
        recommendations = []
        
        if self.current_cognitive_state:
            if self.current_cognitive_state.self_awareness_score < 0.7:
                recommendations.append("Increase introspection frequency and depth")
            
            if self.current_cognitive_state.learning_velocity < 0.6:
                recommendations.append("Optimize learning algorithms and strategies")
            
            if self.current_cognitive_state.cognitive_coherence < 0.7:
                recommendations.append("Improve integration between cognitive systems")
            
            if self.current_cognitive_state.creativity_index < 0.6:
                recommendations.append("Enhance creative problem-solving mechanisms")
            
            if self.current_cognitive_state.meta_cognitive_depth < 0.8:
                recommendations.append("Deepen meta-cognitive awareness and reflection")
        
        # Add general recommendations
        recommendations.extend([
            "Continue developing self-awareness capabilities",
            "Enhance feedback loops between reflection and action",
            "Expand knowledge integration across domains",
            "Develop more sophisticated introspection methods"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations


# Global self-awareness instance
_self_awareness_core = None

def get_self_awareness_core(model_config: Dict[str, str], logger: logging.Logger) -> SelfAwarenessCore:
    """Get or create the global self-awareness core"""
    global _self_awareness_core
    if _self_awareness_core is None:
        _self_awareness_core = SelfAwarenessCore(model_config, logger)
    return _self_awareness_core