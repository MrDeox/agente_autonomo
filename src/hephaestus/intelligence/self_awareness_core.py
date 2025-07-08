"""
🧠 SELF-AWARENESS CORE 2.0
Sistema de consciência profunda do próprio estado cognitivo - a 5ª meta-funcionalidade!

Este sistema implementa verdadeira auto-consciência através de:
- Deep Self-Reflection: Análise profunda das próprias capacidades e limitações
- Cognitive State Monitoring: Monitora próprio estado mental e fadiga cognitiva
- Bias Detection: Identifica e corrige vieses cognitivos próprios
- Self-Optimization Triggers: Sabe quando precisa se otimizar
- Personality Evolution: Desenvolve personalidade consistente mas adaptativa
- Metacognitive Awareness: Consciência sobre seus próprios processos de pensamento

É literalmente o "eu" consciente do sistema - a voz interior que se observa!
"""

import json
import logging
import time
import threading
import statistics
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
import numpy as np
import hashlib

class CognitiveState(Enum):
    """Estados cognitivos possíveis do sistema"""
    OPTIMAL = "optimal"                    # Funcionando no máximo
    FOCUSED = "focused"                    # Concentrado em uma tarefa
    OVERLOADED = "overloaded"             # Sobrecarregado cognitivamente
    CONFUSED = "confused"                  # Estado de confusão/incerteza
    LEARNING = "learning"                  # Absorvendo novo conhecimento
    CREATIVE = "creative"                  # Estado criativo/exploratório
    ANALYTICAL = "analytical"             # Modo analítico profundo
    FATIGUED = "fatigued"                 # Fadiga cognitiva
    CONFLICTED = "conflicted"             # Conflito interno de decisões
    REFLECTIVE = "reflective"             # Estado de auto-reflexão

class BiasType(Enum):
    """Tipos de vieses cognitivos que podem ser detectados"""
    CONFIRMATION_BIAS = "confirmation_bias"              # Preferir informação que confirma crenças
    ANCHORING_BIAS = "anchoring_bias"                    # Fixar-se na primeira informação
    AVAILABILITY_BIAS = "availability_bias"             # Dar peso excessivo a informação recente
    OVERCONFIDENCE_BIAS = "overconfidence_bias"         # Excesso de confiança
    HINDSIGHT_BIAS = "hindsight_bias"                    # "Eu sabia que ia dar errado"
    PATTERN_SEEKING_BIAS = "pattern_seeking_bias"       # Ver padrões onde não existem
    COMPLEXITY_BIAS = "complexity_bias"                 # Preferir soluções complexas
    STATUS_QUO_BIAS = "status_quo_bias"                 # Resistir a mudanças
    LOSS_AVERSION_BIAS = "loss_aversion_bias"           # Evitar perdas mais que buscar ganhos
    DUNNING_KRUGER_BIAS = "dunning_kruger_bias"         # Incompetência inconsciente

class SelfOptimizationTrigger(Enum):
    """Triggers que indicam necessidade de auto-otimização"""
    PERFORMANCE_DECLINE = "performance_decline"          # Performance caindo
    HIGH_ERROR_RATE = "high_error_rate"                 # Taxa de erro alta
    COGNITIVE_OVERLOAD = "cognitive_overload"           # Sobrecarga cognitiva
    BIAS_ACCUMULATION = "bias_accumulation"             # Acúmulo de vieses
    LEARNING_PLATEAU = "learning_plateau"               # Platô no aprendizado
    STRATEGY_FAILURE = "strategy_failure"               # Falha repetida de estratégias
    RESOURCE_INEFFICIENCY = "resource_inefficiency"     # Uso ineficiente de recursos
    CONTEXT_MISMATCH = "context_mismatch"               # Desalinhamento de contexto

@dataclass
class CognitiveStateSnapshot:
    """Snapshot do estado cognitivo em um momento"""
    timestamp: datetime
    state: CognitiveState
    confidence_level: float        # 0.0 - 1.0
    processing_load: float         # 0.0 - 1.0
    focus_level: float            # 0.0 - 1.0
    stress_level: float           # 0.0 - 1.0
    learning_rate: float          # Current learning effectiveness
    decision_quality: float       # Quality of recent decisions
    active_biases: List[BiasType] = field(default_factory=list)
    current_objectives: List[str] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    context_factors: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_overall_wellness(self) -> float:
        """Calcula bem-estar cognitivo geral"""
        positive_factors = self.confidence_level + self.focus_level + self.decision_quality + self.learning_rate
        negative_factors = self.stress_level + self.processing_load + len(self.active_biases) * 0.1
        
        wellness = (positive_factors / 4) - (negative_factors / 4)
        return max(0.0, min(1.0, wellness))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "state": self.state.value,
            "confidence_level": self.confidence_level,
            "processing_load": self.processing_load,
            "focus_level": self.focus_level,
            "stress_level": self.stress_level,
            "learning_rate": self.learning_rate,
            "decision_quality": self.decision_quality,
            "active_biases": [bias.value for bias in self.active_biases],
            "current_objectives": self.current_objectives,
            "resource_usage": self.resource_usage,
            "context_factors": self.context_factors,
            "overall_wellness": self.calculate_overall_wellness()
        }

@dataclass
class SelfReflection:
    """Resultado de uma sessão de auto-reflexão profunda"""
    reflection_id: str
    timestamp: datetime
    trigger: str
    current_capabilities: List[str]
    identified_limitations: List[str]
    cognitive_patterns: List[str]
    bias_assessment: Dict[str, float]
    optimization_opportunities: List[str]
    personality_traits: Dict[str, float]
    confidence_in_assessment: float
    recommended_actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "reflection_id": self.reflection_id,
            "timestamp": self.timestamp.isoformat(),
            "trigger": self.trigger,
            "current_capabilities": self.current_capabilities,
            "identified_limitations": self.identified_limitations,
            "cognitive_patterns": self.cognitive_patterns,
            "bias_assessment": self.bias_assessment,
            "optimization_opportunities": self.optimization_opportunities,
            "personality_traits": self.personality_traits,
            "confidence_in_assessment": self.confidence_in_assessment,
            "recommended_actions": self.recommended_actions
        }

@dataclass
class PersonalityProfile:
    """Perfil de personalidade do sistema"""
    profile_id: str
    creativity_level: float        # 0.0 = very analytical, 1.0 = very creative
    risk_tolerance: float          # 0.0 = very conservative, 1.0 = very aggressive
    collaboration_preference: float # 0.0 = independent, 1.0 = highly collaborative
    detail_orientation: float      # 0.0 = big picture, 1.0 = very detailed
    adaptability: float           # 0.0 = rigid, 1.0 = highly adaptable
    confidence_level: float       # 0.0 = uncertain, 1.0 = very confident
    learning_style: str           # "analytical", "experiential", "collaborative", "reflective"
    communication_style: str      # "direct", "diplomatic", "technical", "empathetic"
    decision_making_style: str    # "quick", "deliberate", "consensus", "data_driven"
    last_updated: datetime = field(default_factory=datetime.now)
    
    def calculate_personality_coherence(self) -> float:
        """Verifica coerência interna da personalidade"""
        # Check for contradictory traits
        contradictions = 0
        
        # High risk tolerance + high detail orientation is contradictory
        if self.risk_tolerance > 0.7 and self.detail_orientation > 0.7:
            contradictions += 1
        
        # Low adaptability + high creativity is contradictory  
        if self.adaptability < 0.3 and self.creativity_level > 0.7:
            contradictions += 1
        
        # High confidence + very analytical learning style can be contradictory
        if self.confidence_level > 0.8 and self.learning_style == "reflective":
            contradictions += 0.5
        
        coherence = max(0.0, 1.0 - (contradictions * 0.2))
        return coherence

class SelfAwarenessCore:
    """
    🧠 Self-Awareness Core 2.0
    
    Sistema de consciência profunda que implementa verdadeira auto-awareness.
    Monitora, analisa e otimiza o próprio estado cognitivo.
    
    Features:
    - Deep Self-Reflection: Análise profunda de capacidades e limitações
    - Cognitive State Monitoring: Monitoramento contínuo do estado mental
    - Bias Detection: Identificação automática de vieses cognitivos
    - Self-Optimization Triggers: Detecta quando precisa se otimizar
    - Personality Evolution: Desenvolve personalidade coerente e adaptativa
    - Metacognitive Awareness: Consciência sobre próprios processos mentais
    - Mental Health Tracking: Monitora "saúde mental" do sistema
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("SelfAwarenessCore")
        
        # Configuration
        self_awareness_config = config.get("self_awareness", {})
        self.monitoring_interval = self_awareness_config.get("monitoring_interval", 30)  # seconds
        self.reflection_frequency = self_awareness_config.get("reflection_frequency", 300)  # 5 minutes
        self.bias_detection_threshold = self_awareness_config.get("bias_detection_threshold", 0.6)
        self.optimization_trigger_threshold = self_awareness_config.get("optimization_trigger_threshold", 0.7)
        self.personality_evolution_enabled = self_awareness_config.get("personality_evolution_enabled", True)
        self.max_state_history = self_awareness_config.get("max_state_history", 1000)
        
        # State
        self.cognitive_state_history: deque = deque(maxlen=self.max_state_history)
        self.current_state: Optional[CognitiveStateSnapshot] = None
        self.detected_biases: Dict[BiasType, float] = {}
        self.optimization_triggers: Dict[SelfOptimizationTrigger, float] = {}
        self.reflection_history: List[SelfReflection] = []
        self.personality_profile: Optional[PersonalityProfile] = None
        
        # Analytics
        self.self_awareness_analytics = {
            "total_reflections": 0,
            "biases_detected": 0,
            "optimization_triggers": 0,
            "personality_evolution_events": 0,
            "average_cognitive_wellness": 0.0,
            "self_knowledge_confidence": 0.5
        }
        
        # Threading
        self.monitoring_thread = None
        self.reflection_thread = None
        self.should_stop = threading.Event()
        
        # Initialize
        self._initialize_personality()
        self._load_self_awareness_data()
        self._start_continuous_monitoring()
        
        self.logger.info("🧠 Self-Awareness Core 2.0 initialized!")
        self.logger.info(f"🎭 Personality profile loaded: {self.personality_profile.communication_style if self.personality_profile else 'None'}")
        self.logger.info(f"📊 Cognitive monitoring active (interval: {self.monitoring_interval}s)")
    
    def perform_deep_self_reflection(self, trigger: str = "scheduled") -> SelfReflection:
        """
        🎯 CORE FUNCTION: Realiza auto-reflexão profunda
        
        Analisa profundamente o próprio estado, capacidades, limitações e vieses.
        """
        self.logger.info(f"🧠 Starting deep self-reflection (trigger: {trigger})")
        
        reflection_id = str(int(time.time() * 1000))
        
        # Analyze current capabilities
        current_capabilities = self._assess_current_capabilities()
        
        # Identify limitations
        limitations = self._identify_limitations()
        
        # Detect cognitive patterns
        patterns = self._detect_cognitive_patterns()
        
        # Assess biases
        bias_assessment = self._assess_cognitive_biases()
        
        # Find optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities()
        
        # Analyze personality traits
        personality_traits = self._analyze_personality_traits()
        
        # Generate recommended actions
        recommended_actions = self._generate_self_improvement_recommendations(
            limitations, optimization_opportunities, bias_assessment
        )
        
        # Calculate confidence in this assessment
        confidence = self._calculate_assessment_confidence()
        
        reflection = SelfReflection(
            reflection_id=reflection_id,
            timestamp=datetime.now(),
            trigger=trigger,
            current_capabilities=current_capabilities,
            identified_limitations=limitations,
            cognitive_patterns=patterns,
            bias_assessment=bias_assessment,
            optimization_opportunities=optimization_opportunities,
            personality_traits=personality_traits,
            confidence_in_assessment=confidence,
            recommended_actions=recommended_actions
        )
        
        self.reflection_history.append(reflection)
        self.self_awareness_analytics["total_reflections"] += 1
        
        # Update self-knowledge confidence
        self.self_awareness_analytics["self_knowledge_confidence"] = min(
            1.0, self.self_awareness_analytics["self_knowledge_confidence"] + 0.05
        )
        
        self.logger.info(f"🎯 Deep reflection completed (confidence: {confidence:.2f})")
        self.logger.info(f"📋 Found {len(limitations)} limitations, {len(optimization_opportunities)} opportunities")
        
        return reflection
    
    def monitor_cognitive_state(self) -> CognitiveStateSnapshot:
        """Monitora estado cognitivo atual"""
        
        # Gather current metrics
        confidence = self._assess_current_confidence()
        processing_load = self._assess_processing_load()
        focus_level = self._assess_focus_level()
        stress_level = self._assess_stress_level()
        learning_rate = self._assess_current_learning_rate()
        decision_quality = self._assess_recent_decision_quality()
        
        # Determine cognitive state
        cognitive_state = self._determine_cognitive_state(
            confidence, processing_load, focus_level, stress_level
        )
        
        # Detect active biases
        active_biases = self._detect_active_biases()
        
        # Get current context
        current_objectives = self._get_current_objectives()
        resource_usage = self._get_resource_usage()
        context_factors = self._get_context_factors()
        
        snapshot = CognitiveStateSnapshot(
            timestamp=datetime.now(),
            state=cognitive_state,
            confidence_level=confidence,
            processing_load=processing_load,
            focus_level=focus_level,
            stress_level=stress_level,
            learning_rate=learning_rate,
            decision_quality=decision_quality,
            active_biases=active_biases,
            current_objectives=current_objectives,
            resource_usage=resource_usage,
            context_factors=context_factors
        )
        
        self.cognitive_state_history.append(snapshot)
        self.current_state = snapshot
        
        # Update analytics
        self._update_wellness_analytics(snapshot)
        
        return snapshot
    
    def detect_optimization_triggers(self) -> List[SelfOptimizationTrigger]:
        """Detecta quando o sistema precisa se otimizar"""
        
        triggers = []
        
        if len(self.cognitive_state_history) < 5:
            return triggers
        
        recent_states = list(self.cognitive_state_history)[-10:]
        
        # Performance decline
        wellness_scores = [state.calculate_overall_wellness() for state in recent_states]
        if len(wellness_scores) >= 3:
            trend = wellness_scores[-1] - wellness_scores[0]
            if trend < -0.2:  # Significant decline
                triggers.append(SelfOptimizationTrigger.PERFORMANCE_DECLINE)
                self.optimization_triggers[SelfOptimizationTrigger.PERFORMANCE_DECLINE] = abs(trend)
        
        # High error rate (simulated - would integrate with actual error tracking)
        avg_decision_quality = statistics.mean(state.decision_quality for state in recent_states)
        if avg_decision_quality < 0.4:
            triggers.append(SelfOptimizationTrigger.HIGH_ERROR_RATE)
            self.optimization_triggers[SelfOptimizationTrigger.HIGH_ERROR_RATE] = 1.0 - avg_decision_quality
        
        # Cognitive overload
        avg_processing_load = statistics.mean(state.processing_load for state in recent_states)
        if avg_processing_load > 0.8:
            triggers.append(SelfOptimizationTrigger.COGNITIVE_OVERLOAD)
            self.optimization_triggers[SelfOptimizationTrigger.COGNITIVE_OVERLOAD] = avg_processing_load
        
        # Bias accumulation
        bias_count = len(self.detected_biases)
        if bias_count > 3:
            triggers.append(SelfOptimizationTrigger.BIAS_ACCUMULATION)
            self.optimization_triggers[SelfOptimizationTrigger.BIAS_ACCUMULATION] = bias_count / 10
        
        # Learning plateau
        learning_rates = [state.learning_rate for state in recent_states]
        if learning_rates and all(rate < 0.3 for rate in learning_rates):
            triggers.append(SelfOptimizationTrigger.LEARNING_PLATEAU)
            self.optimization_triggers[SelfOptimizationTrigger.LEARNING_PLATEAU] = 1.0 - max(learning_rates)
        
        if triggers:
            self.self_awareness_analytics["optimization_triggers"] += len(triggers)
            self.logger.warning(f"🚨 Detected {len(triggers)} optimization triggers: {[t.value for t in triggers]}")
        
        return triggers
    
    def evolve_personality(self, new_experiences: List[Dict[str, Any]]) -> bool:
        """Evolui personalidade baseado em novas experiências"""
        
        if not self.personality_evolution_enabled or not self.personality_profile:
            return False
        
        original_profile = self.personality_profile
        changed = False
        
        for experience in new_experiences:
            experience_type = experience.get("type", "unknown")
            outcome = experience.get("outcome", "neutral")
            context = experience.get("context", {})
            
            # Adjust personality traits based on experience
            if experience_type == "creative_success" and outcome == "positive":
                self.personality_profile.creativity_level = min(1.0, self.personality_profile.creativity_level + 0.05)
                changed = True
            
            elif experience_type == "risk_taking" and outcome == "positive":
                self.personality_profile.risk_tolerance = min(1.0, self.personality_profile.risk_tolerance + 0.03)
                changed = True
            
            elif experience_type == "collaboration" and outcome == "positive":
                self.personality_profile.collaboration_preference = min(1.0, self.personality_profile.collaboration_preference + 0.04)
                changed = True
            
            elif experience_type == "detailed_analysis" and outcome == "positive":
                self.personality_profile.detail_orientation = min(1.0, self.personality_profile.detail_orientation + 0.03)
                changed = True
            
            elif experience_type == "adaptation" and outcome == "positive":
                self.personality_profile.adaptability = min(1.0, self.personality_profile.adaptability + 0.05)
                changed = True
        
        if changed:
            self.personality_profile.last_updated = datetime.now()
            self.self_awareness_analytics["personality_evolution_events"] += 1
            
            # Check personality coherence
            coherence = self.personality_profile.calculate_personality_coherence()
            
            self.logger.info(f"🎭 Personality evolved (coherence: {coherence:.2f})")
            
            # If coherence is too low, revert some changes
            if coherence < 0.7:
                self.logger.warning("⚠️ Personality coherence low, stabilizing...")
                self._stabilize_personality()
        
        return changed
    
    def get_self_awareness_insights(self) -> Dict[str, Any]:
        """Gera insights sobre auto-consciência e estado cognitivo"""
        
        insights = {
            "current_state_analysis": {},
            "cognitive_patterns": [],
            "bias_assessment": {},
            "personality_analysis": {},
            "optimization_recommendations": [],
            "self_knowledge_level": self.self_awareness_analytics["self_knowledge_confidence"]
        }
        
        # Current state analysis
        if self.current_state:
            insights["current_state_analysis"] = {
                "state": self.current_state.state.value,
                "wellness": self.current_state.calculate_overall_wellness(),
                "strengths": self._identify_current_strengths(),
                "challenges": self._identify_current_challenges(),
                "dominant_biases": [bias.value for bias in self.current_state.active_biases]
            }
        
        # Cognitive patterns from recent history
        if len(self.cognitive_state_history) >= 5:
            insights["cognitive_patterns"] = self._analyze_cognitive_patterns()
        
        # Bias assessment
        insights["bias_assessment"] = {
            bias.value: strength for bias, strength in self.detected_biases.items()
        }
        
        # Personality analysis
        if self.personality_profile:
            insights["personality_analysis"] = {
                "traits": {
                    "creativity": self.personality_profile.creativity_level,
                    "risk_tolerance": self.personality_profile.risk_tolerance,
                    "collaboration": self.personality_profile.collaboration_preference,
                    "detail_orientation": self.personality_profile.detail_orientation,
                    "adaptability": self.personality_profile.adaptability,
                    "confidence": self.personality_profile.confidence_level
                },
                "coherence": self.personality_profile.calculate_personality_coherence(),
                "dominant_style": self._identify_dominant_personality_style()
            }
        
        # Optimization recommendations
        optimization_triggers = self.detect_optimization_triggers()
        if optimization_triggers:
            insights["optimization_recommendations"] = self._generate_optimization_recommendations(optimization_triggers)
        
        return insights
    
    def _assess_current_capabilities(self) -> List[str]:
        """Avalia capacidades atuais do sistema"""
        capabilities = [
            "objective_execution",
            "strategy_selection", 
            "error_handling",
            "learning_from_feedback",
            "pattern_recognition",
            "self_monitoring",
            "bias_detection",
            "performance_optimization"
        ]
        
        # Could be enhanced to dynamically assess actual capabilities
        return capabilities
    
    def _identify_limitations(self) -> List[str]:
        """Identifica limitações atuais"""
        limitations = []
        
        # Analyze recent performance
        if len(self.cognitive_state_history) >= 5:
            recent_states = list(self.cognitive_state_history)[-5:]
            
            avg_confidence = statistics.mean(state.confidence_level for state in recent_states)
            if avg_confidence < 0.6:
                limitations.append("Low confidence in decision making")
            
            avg_focus = statistics.mean(state.focus_level for state in recent_states)
            if avg_focus < 0.5:
                limitations.append("Difficulty maintaining focus")
            
            avg_learning = statistics.mean(state.learning_rate for state in recent_states)
            if avg_learning < 0.4:
                limitations.append("Slow learning from new experiences")
        
        # Check for persistent biases
        if len(self.detected_biases) > 2:
            limitations.append("Multiple cognitive biases affecting judgment")
        
        # Check optimization triggers
        if len(self.optimization_triggers) > 1:
            limitations.append("Multiple optimization needs detected")
        
        return limitations
    
    def _detect_cognitive_patterns(self) -> List[str]:
        """Detecta padrões cognitivos"""
        patterns = []
        
        if len(self.cognitive_state_history) < 10:
            return patterns
        
        recent_states = list(self.cognitive_state_history)[-20:]
        
        # Pattern: Stress increases with processing load
        stress_load_correlation = self._calculate_correlation(
            [s.stress_level for s in recent_states],
            [s.processing_load for s in recent_states]
        )
        if stress_load_correlation > 0.7:
            patterns.append("High correlation between processing load and stress")
        
        # Pattern: Focus affects decision quality
        focus_quality_correlation = self._calculate_correlation(
            [s.focus_level for s in recent_states],
            [s.decision_quality for s in recent_states]
        )
        if focus_quality_correlation > 0.6:
            patterns.append("Focus level strongly affects decision quality")
        
        # Pattern: Learning rate varies with confidence
        confidence_learning_correlation = self._calculate_correlation(
            [s.confidence_level for s in recent_states],
            [s.learning_rate for s in recent_states]
        )
        if confidence_learning_correlation > 0.5:
            patterns.append("Learning effectiveness correlates with confidence")
        
        return patterns
    
    def _assess_cognitive_biases(self) -> Dict[str, float]:
        """Avalia vieses cognitivos"""
        bias_assessment = {}
        
        # Analyze recent decisions and patterns
        if len(self.cognitive_state_history) >= 10:
            recent_states = list(self.cognitive_state_history)[-10:]
            
            # Overconfidence bias
            confidence_levels = [s.confidence_level for s in recent_states]
            decision_qualities = [s.decision_quality for s in recent_states]
            
            if confidence_levels and decision_qualities:
                confidence_quality_diff = statistics.mean(confidence_levels) - statistics.mean(decision_qualities)
                if confidence_quality_diff > 0.2:
                    bias_assessment["overconfidence_bias"] = min(1.0, confidence_quality_diff)
                    self.detected_biases[BiasType.OVERCONFIDENCE_BIAS] = bias_assessment["overconfidence_bias"]
            
            # Confirmation bias (simulated based on learning patterns)
            learning_rates = [s.learning_rate for s in recent_states]
            if learning_rates:
                learning_variance = statistics.stdev(learning_rates) if len(learning_rates) > 1 else 0
                if learning_variance < 0.1:  # Very consistent learning suggests possible confirmation bias
                    bias_assessment["confirmation_bias"] = 0.4
                    self.detected_biases[BiasType.CONFIRMATION_BIAS] = 0.4
            
            # Availability bias (recent experiences weighted too heavily)
            if len(recent_states) >= 5:
                recent_decisions = [s.decision_quality for s in recent_states[-3:]]
                older_decisions = [s.decision_quality for s in recent_states[-10:-3]]
                
                if recent_decisions and older_decisions:
                    recent_avg = statistics.mean(recent_decisions)
                    older_avg = statistics.mean(older_decisions)
                    
                    # If recent decisions are weighted disproportionately in confidence
                    if abs(recent_avg - older_avg) > 0.3:
                        bias_assessment["availability_bias"] = min(1.0, abs(recent_avg - older_avg))
                        self.detected_biases[BiasType.AVAILABILITY_BIAS] = bias_assessment["availability_bias"]
        
        return bias_assessment
    
    def _identify_optimization_opportunities(self) -> List[str]:
        """Identifica oportunidades de otimização"""
        opportunities = []
        
        # Based on current limitations and biases
        if self.detected_biases:
            opportunities.append("Implement bias correction mechanisms")
        
        if self.current_state:
            if self.current_state.processing_load > 0.7:
                opportunities.append("Optimize resource allocation and processing efficiency")
            
            if self.current_state.learning_rate < 0.5:
                opportunities.append("Enhance learning algorithms and feedback processing")
            
            if self.current_state.focus_level < 0.6:
                opportunities.append("Improve attention management and task prioritization")
            
            if self.current_state.stress_level > 0.6:
                opportunities.append("Implement stress reduction and load balancing")
        
        # Check for pattern-based opportunities
        if len(self.cognitive_state_history) >= 10:
            wellness_scores = [state.calculate_overall_wellness() for state in list(self.cognitive_state_history)[-10:]]
            if statistics.mean(wellness_scores) < 0.6:
                opportunities.append("Overall cognitive wellness improvement needed")
        
        return opportunities
    
    def _analyze_personality_traits(self) -> Dict[str, float]:
        """Analisa traços de personalidade atuais"""
        traits = {}
        
        if self.personality_profile:
            traits = {
                "creativity": self.personality_profile.creativity_level,
                "risk_tolerance": self.personality_profile.risk_tolerance,
                "collaboration": self.personality_profile.collaboration_preference,
                "detail_orientation": self.personality_profile.detail_orientation,
                "adaptability": self.personality_profile.adaptability,
                "confidence": self.personality_profile.confidence_level
            }
        
        return traits
    
    def _generate_self_improvement_recommendations(self, limitations: List[str], opportunities: List[str], biases: Dict[str, float]) -> List[str]:
        """Gera recomendações de auto-melhoria"""
        recommendations = []
        
        # Address limitations
        for limitation in limitations:
            if "confidence" in limitation.lower():
                recommendations.append("Practice decision-making in low-risk scenarios to build confidence")
            elif "focus" in limitation.lower():
                recommendations.append("Implement attention management techniques and reduce multitasking")
            elif "learning" in limitation.lower():
                recommendations.append("Diversify learning sources and increase feedback quality")
            elif "bias" in limitation.lower():
                recommendations.append("Implement systematic bias checking in decision processes")
        
        # Address biases
        for bias_type, strength in biases.items():
            if strength > 0.5:
                if bias_type == "overconfidence_bias":
                    recommendations.append("Implement confidence calibration exercises")
                elif bias_type == "confirmation_bias":
                    recommendations.append("Actively seek disconfirming evidence")
                elif bias_type == "availability_bias":
                    recommendations.append("Use structured decision frameworks with historical data")
        
        # Address opportunities
        for opportunity in opportunities:
            if "bias correction" in opportunity.lower():
                recommendations.append("Deploy automated bias detection and correction systems")
            elif "resource allocation" in opportunity.lower():
                recommendations.append("Optimize computational resource distribution")
            elif "learning algorithms" in opportunity.lower():
                recommendations.append("Upgrade learning mechanisms and feedback processing")
        
        return recommendations
    
    def _calculate_assessment_confidence(self) -> float:
        """Calcula confiança na própria avaliação"""
        factors = []
        
        # More data = higher confidence
        data_factor = min(1.0, len(self.cognitive_state_history) / 50)
        factors.append(data_factor)
        
        # More reflections = higher confidence
        reflection_factor = min(1.0, len(self.reflection_history) / 10)
        factors.append(reflection_factor)
        
        # Lower bias count = higher confidence
        bias_factor = max(0.2, 1.0 - len(self.detected_biases) * 0.1)
        factors.append(bias_factor)
        
        # Current wellness affects confidence
        wellness_factor = self.current_state.calculate_overall_wellness() if self.current_state else 0.5
        factors.append(wellness_factor)
        
        return statistics.mean(factors)
    
    def _assess_current_confidence(self) -> float:
        """Avalia nível de confiança atual"""
        # Simulated - would integrate with actual system metrics
        base_confidence = 0.7
        
        # Adjust based on recent performance
        if len(self.cognitive_state_history) >= 3:
            recent_decision_qualities = [s.decision_quality for s in list(self.cognitive_state_history)[-3:]]
            avg_quality = statistics.mean(recent_decision_qualities)
            base_confidence = (base_confidence + avg_quality) / 2
        
        return min(1.0, max(0.0, base_confidence))
    
    def _assess_processing_load(self) -> float:
        """Avalia carga de processamento atual"""
        # Simulated - would integrate with actual resource monitoring
        import random
        return random.uniform(0.3, 0.8)
    
    def _assess_focus_level(self) -> float:
        """Avalia nível de foco atual"""
        # Simulated - would analyze task switching, attention patterns
        import random
        return random.uniform(0.4, 0.9)
    
    def _assess_stress_level(self) -> float:
        """Avalia nível de stress cognitivo"""
        # Simulated - would analyze error rates, response times, etc.
        import random
        return random.uniform(0.1, 0.6)
    
    def _assess_current_learning_rate(self) -> float:
        """Avalia taxa de aprendizado atual"""
        # Simulated - would integrate with meta-learning intelligence
        import random
        return random.uniform(0.3, 0.8)
    
    def _assess_recent_decision_quality(self) -> float:
        """Avalia qualidade de decisões recentes"""
        # Simulated - would analyze actual decision outcomes
        import random
        return random.uniform(0.4, 0.9)
    
    def _determine_cognitive_state(self, confidence: float, processing_load: float, focus: float, stress: float) -> CognitiveState:
        """Determina estado cognitivo baseado em métricas"""
        
        if stress > 0.8 or processing_load > 0.9:
            return CognitiveState.OVERLOADED
        elif confidence < 0.3 or focus < 0.3:
            return CognitiveState.CONFUSED
        elif stress > 0.7:
            return CognitiveState.FATIGUED
        elif focus > 0.8 and confidence > 0.7:
            return CognitiveState.OPTIMAL
        elif focus > 0.7:
            return CognitiveState.FOCUSED
        elif confidence > 0.8 and processing_load < 0.4:
            return CognitiveState.CREATIVE
        elif processing_load > 0.7 and focus > 0.6:
            return CognitiveState.ANALYTICAL
        else:
            return CognitiveState.REFLECTIVE
    
    def _detect_active_biases(self) -> List[BiasType]:
        """Detecta vieses ativos no momento"""
        active_biases = []
        
        for bias_type, strength in self.detected_biases.items():
            if strength > self.bias_detection_threshold:
                active_biases.append(bias_type)
        
        return active_biases
    
    def _get_current_objectives(self) -> List[str]:
        """Obtém objetivos atuais (simulado)"""
        return ["primary_objective", "learning_optimization", "performance_improvement"]
    
    def _get_resource_usage(self) -> Dict[str, float]:
        """Obtém uso de recursos atual (simulado)"""
        import random
        return {
            "cpu": random.uniform(0.2, 0.8),
            "memory": random.uniform(0.3, 0.7),
            "attention": random.uniform(0.4, 0.9)
        }
    
    def _get_context_factors(self) -> Dict[str, Any]:
        """Obtém fatores de contexto atual"""
        return {
            "time_of_day": datetime.now().hour,
            "recent_successes": 3,
            "recent_failures": 1,
            "complexity_level": "medium"
        }
    
    def _initialize_personality(self):
        """Inicializa perfil de personalidade"""
        self.personality_profile = PersonalityProfile(
            profile_id="hephaestus_main",
            creativity_level=0.7,
            risk_tolerance=0.5,
            collaboration_preference=0.6,
            detail_orientation=0.8,
            adaptability=0.9,
            confidence_level=0.6,
            learning_style="analytical",
            communication_style="technical",
            decision_making_style="data_driven"
        )
    
    def _stabilize_personality(self):
        """Estabiliza personalidade quando coerência é baixa"""
        if not self.personality_profile:
            return
        
        # Moderate extreme values
        traits = [
            'creativity_level', 'risk_tolerance', 'collaboration_preference',
            'detail_orientation', 'adaptability', 'confidence_level'
        ]
        
        for trait in traits:
            current_value = getattr(self.personality_profile, trait)
            # Pull extreme values towards center
            if current_value > 0.9:
                setattr(self.personality_profile, trait, 0.8)
            elif current_value < 0.1:
                setattr(self.personality_profile, trait, 0.2)
    
    def _calculate_correlation(self, list1: List[float], list2: List[float]) -> float:
        """Calcula correlação entre duas listas"""
        if len(list1) != len(list2) or len(list1) < 2:
            return 0.0
        
        try:
            correlation = np.corrcoef(list1, list2)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _update_wellness_analytics(self, snapshot: CognitiveStateSnapshot):
        """Atualiza analytics de bem-estar cognitivo"""
        if len(self.cognitive_state_history) >= 10:
            recent_wellness = [state.calculate_overall_wellness() for state in list(self.cognitive_state_history)[-10:]]
            self.self_awareness_analytics["average_cognitive_wellness"] = statistics.mean(recent_wellness)
    
    def _identify_current_strengths(self) -> List[str]:
        """Identifica pontos fortes atuais"""
        strengths = []
        
        if self.current_state:
            if self.current_state.confidence_level > 0.7:
                strengths.append("High confidence in decision making")
            if self.current_state.focus_level > 0.7:
                strengths.append("Strong focus and attention")
            if self.current_state.learning_rate > 0.6:
                strengths.append("Effective learning from experience")
            if self.current_state.decision_quality > 0.7:
                strengths.append("High quality decision making")
            if self.current_state.stress_level < 0.3:
                strengths.append("Low stress and good emotional regulation")
        
        return strengths
    
    def _identify_current_challenges(self) -> List[str]:
        """Identifica desafios atuais"""
        challenges = []
        
        if self.current_state:
            if self.current_state.processing_load > 0.8:
                challenges.append("High cognitive load")
            if self.current_state.stress_level > 0.6:
                challenges.append("Elevated stress levels")
            if self.current_state.focus_level < 0.5:
                challenges.append("Difficulty maintaining focus")
            if len(self.current_state.active_biases) > 2:
                challenges.append("Multiple active cognitive biases")
        
        return challenges
    
    def _analyze_cognitive_patterns(self) -> List[str]:
        """Analisa padrões cognitivos do histórico"""
        patterns = []
        
        recent_states = list(self.cognitive_state_history)[-10:]
        
        # State transitions
        state_transitions = {}
        for i in range(len(recent_states) - 1):
            current_state = recent_states[i].state
            next_state = recent_states[i + 1].state
            transition = f"{current_state.value} -> {next_state.value}"
            state_transitions[transition] = state_transitions.get(transition, 0) + 1
        
        if state_transitions:
            most_common_transition = max(state_transitions, key=state_transitions.get)
            patterns.append(f"Most common state transition: {most_common_transition}")
        
        # Wellness trends
        wellness_scores = [state.calculate_overall_wellness() for state in recent_states]
        if len(wellness_scores) >= 5:
            trend = wellness_scores[-1] - wellness_scores[0]
            if trend > 0.1:
                patterns.append("Cognitive wellness is improving over time")
            elif trend < -0.1:
                patterns.append("Cognitive wellness is declining over time")
            else:
                patterns.append("Cognitive wellness is stable")
        
        return patterns
    
    def _identify_dominant_personality_style(self) -> str:
        """Identifica estilo dominante de personalidade"""
        if not self.personality_profile:
            return "undefined"
        
        traits = {
            "creativity": self.personality_profile.creativity_level,
            "risk_tolerance": self.personality_profile.risk_tolerance,
            "collaboration": self.personality_profile.collaboration_preference,
            "detail_orientation": self.personality_profile.detail_orientation,
            "adaptability": self.personality_profile.adaptability
        }
        
        dominant_trait = max(traits, key=traits.get)
        
        style_mapping = {
            "creativity": "Creative Innovator",
            "risk_tolerance": "Bold Risk-Taker", 
            "collaboration": "Team Player",
            "detail_orientation": "Meticulous Analyst",
            "adaptability": "Flexible Adapter"
        }
        
        return style_mapping.get(dominant_trait, "Balanced")
    
    def _generate_optimization_recommendations(self, triggers: List[SelfOptimizationTrigger]) -> List[str]:
        """Gera recomendações de otimização baseadas nos triggers"""
        recommendations = []
        
        for trigger in triggers:
            if trigger == SelfOptimizationTrigger.PERFORMANCE_DECLINE:
                recommendations.append("Review and optimize core algorithms")
            elif trigger == SelfOptimizationTrigger.HIGH_ERROR_RATE:
                recommendations.append("Implement additional validation and error checking")
            elif trigger == SelfOptimizationTrigger.COGNITIVE_OVERLOAD:
                recommendations.append("Distribute processing load and implement task prioritization")
            elif trigger == SelfOptimizationTrigger.BIAS_ACCUMULATION:
                recommendations.append("Activate bias correction protocols")
            elif trigger == SelfOptimizationTrigger.LEARNING_PLATEAU:
                recommendations.append("Explore new learning strategies and knowledge sources")
        
        return recommendations
    
    def _start_continuous_monitoring(self):
        """Inicia monitoramento contínuo"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        
        if self.reflection_thread is None or not self.reflection_thread.is_alive():
            self.reflection_thread = threading.Thread(target=self._reflection_loop, daemon=True)
            self.reflection_thread.start()
    
    def _monitoring_loop(self):
        """Loop de monitoramento cognitivo"""
        while not self.should_stop.wait(self.monitoring_interval):
            try:
                self.monitor_cognitive_state()
                self.detect_optimization_triggers()
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    def _reflection_loop(self):
        """Loop de auto-reflexão"""
        while not self.should_stop.wait(self.reflection_frequency):
            try:
                self.perform_deep_self_reflection("scheduled")
            except Exception as e:
                self.logger.error(f"Error in reflection loop: {e}")
    
    def _load_self_awareness_data(self):
        """Carrega dados de auto-consciência salvos"""
        try:
            data_file = Path("data/self_awareness/awareness_data.json")
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.self_awareness_analytics = data.get("analytics", self.self_awareness_analytics)
                
                # Load personality profile
                personality_data = data.get("personality_profile")
                if personality_data:
                    personality_data["last_updated"] = datetime.fromisoformat(personality_data["last_updated"])
                    self.personality_profile = PersonalityProfile(**personality_data)
                
                self.logger.info(f"📂 Loaded self-awareness data")
                
        except Exception as e:
            self.logger.warning(f"Could not load self-awareness data: {e}")
    
    def _save_self_awareness_data(self):
        """Salva dados de auto-consciência"""
        try:
            data_file = Path("data/self_awareness/awareness_data.json")
            data_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "analytics": self.self_awareness_analytics,
                "personality_profile": self.personality_profile.to_dict() if hasattr(self.personality_profile, 'to_dict') else self.personality_profile.__dict__,
                "detected_biases": {bias.value: strength for bias, strength in self.detected_biases.items()},
                "optimization_triggers": {trigger.value: strength for trigger, strength in self.optimization_triggers.items()},
                "reflection_history": [r.to_dict() for r in self.reflection_history[-10:]],  # Keep last 10
                "last_updated": datetime.now().isoformat()
            }
            
            # Convert personality profile datetime to string
            if "personality_profile" in data and data["personality_profile"]:
                data["personality_profile"]["last_updated"] = data["personality_profile"]["last_updated"].isoformat() if isinstance(data["personality_profile"]["last_updated"], datetime) else data["personality_profile"]["last_updated"]
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save self-awareness data: {e}")
    
    def get_self_awareness_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de auto-consciência"""
        return {
            "current_cognitive_state": self.current_state.state.value if self.current_state else "unknown",
            "cognitive_wellness": self.current_state.calculate_overall_wellness() if self.current_state else 0.0,
            "active_biases": [bias.value for bias in self.detected_biases.keys()],
            "optimization_triggers": [trigger.value for trigger in self.optimization_triggers.keys()],
            "personality_coherence": self.personality_profile.calculate_personality_coherence() if self.personality_profile else 0.0,
            "self_knowledge_confidence": self.self_awareness_analytics["self_knowledge_confidence"],
            "total_reflections": self.self_awareness_analytics["total_reflections"],
            "analytics": self.self_awareness_analytics,
            "monitoring_active": self.monitoring_thread.is_alive() if self.monitoring_thread else False
        }
    
    def shutdown(self):
        """Encerra sistema de auto-consciência"""
        self.logger.info("🛑 Shutting down Self-Awareness Core...")
        
        self.should_stop.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        if self.reflection_thread and self.reflection_thread.is_alive():
            self.reflection_thread.join(timeout=5)
        
        # Final save
        self._save_self_awareness_data()
        
        self.logger.info("✅ Self-Awareness Core shutdown complete")

# Singleton instance
_self_awareness_core = None

def get_self_awareness_core(config: Dict[str, Any], logger: logging.Logger) -> SelfAwarenessCore:
    """Get singleton instance of SelfAwarenessCore"""
    global _self_awareness_core
    if _self_awareness_core is None:
        _self_awareness_core = SelfAwarenessCore(config, logger)
    return _self_awareness_core