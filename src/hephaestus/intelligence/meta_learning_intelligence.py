"""
🧠 META-LEARNING INTELLIGENCE SYSTEM
Sistema que aprende como aprender melhor - a 4ª meta-funcionalidade!

Este sistema observa os próprios padrões de aprendizado e otimiza:
- Como processar diferentes tipos de feedback
- Qual taxa de aprendizado usar em cada contexto
- Que tipos de experiência são mais valiosos
- Como transferir conhecimento entre domínios
- Como esquecer informação irrelevante

É literalmente inteligência sobre inteligência!
"""

import json
import logging
import time
import threading
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from enum import Enum
import numpy as np
import statistics
import hashlib

class LearningType(Enum):
    """Tipos de aprendizado que o sistema pode fazer"""
    ERROR_CORRECTION = "error_correction"
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    PERFORMANCE_IMPROVEMENT = "performance_improvement"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"
    BIAS_CORRECTION = "bias_correction"
    FAILURE_ANALYSIS = "failure_analysis"

class LearningContext(Enum):
    """Contextos onde o aprendizado acontece"""
    OBJECTIVE_EXECUTION = "objective_execution"
    STRATEGY_SELECTION = "strategy_selection"
    ERROR_HANDLING = "error_handling"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    KNOWLEDGE_ACQUISITION = "knowledge_acquisition"
    DECISION_MAKING = "decision_making"

class LearningEffectiveness(Enum):
    """Níveis de efetividade do aprendizado"""
    HIGHLY_EFFECTIVE = "highly_effective"    # >80% improvement
    EFFECTIVE = "effective"                  # 50-80% improvement
    MODERATELY_EFFECTIVE = "moderately_effective"  # 20-50% improvement
    SLIGHTLY_EFFECTIVE = "slightly_effective"      # 5-20% improvement
    INEFFECTIVE = "ineffective"              # <5% improvement
    COUNTERPRODUCTIVE = "counterproductive"  # Negative improvement

@dataclass
class LearningEvent:
    """Representa um evento de aprendizado"""
    event_id: str
    learning_type: LearningType
    context: LearningContext
    trigger: str  # What triggered this learning
    input_data: Dict[str, Any]
    learning_rate_used: float
    feedback_quality: float  # 0.0 - 1.0
    time_to_learn: float  # seconds
    knowledge_gained: str
    confidence_before: float
    confidence_after: float
    performance_before: float
    performance_after: float
    effectiveness: LearningEffectiveness
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_learning_gain(self) -> float:
        """Calcula o ganho total do aprendizado"""
        confidence_gain = self.confidence_after - self.confidence_before
        performance_gain = self.performance_after - self.performance_before
        
        # Weighted combination
        return (confidence_gain * 0.3 + performance_gain * 0.7)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "learning_type": self.learning_type.value,
            "context": self.context.value,
            "trigger": self.trigger,
            "input_data": self.input_data,
            "learning_rate_used": self.learning_rate_used,
            "feedback_quality": self.feedback_quality,
            "time_to_learn": self.time_to_learn,
            "knowledge_gained": self.knowledge_gained,
            "confidence_before": self.confidence_before,
            "confidence_after": self.confidence_after,
            "performance_before": self.performance_before,
            "performance_after": self.performance_after,
            "effectiveness": self.effectiveness.value,
            "learning_gain": self.calculate_learning_gain(),
            "timestamp": self.timestamp.isoformat()
        }

@dataclass
class LearningPattern:
    """Padrão de aprendizado identificado"""
    pattern_id: str
    pattern_type: str
    conditions: List[str]
    optimal_learning_rate: float
    optimal_feedback_types: List[str]
    typical_time_to_learn: float
    success_rate: float
    contexts_where_effective: List[LearningContext]
    knowledge_domains: List[str]
    confidence_score: float
    last_updated: datetime = field(default_factory=datetime.now)
    usage_count: int = 0

@dataclass
class AdaptiveMemory:
    """Sistema de memória que adapta retention baseado na relevância"""
    memory_id: str
    knowledge_item: Dict[str, Any]
    importance_score: float
    access_frequency: int
    last_accessed: datetime
    creation_date: datetime
    domain: str
    related_memories: List[str] = field(default_factory=list)
    decay_rate: float = 0.1
    reinforcement_count: int = 0
    
    def calculate_retention_strength(self) -> float:
        """Calcula força de retenção na memória"""
        time_factor = max(0, 1 - (datetime.now() - self.last_accessed).days * self.decay_rate / 30)
        frequency_factor = min(1, self.access_frequency / 10)
        importance_factor = self.importance_score
        
        return (time_factor * 0.3 + frequency_factor * 0.3 + importance_factor * 0.4)

class MetaLearningIntelligence:
    """
    🧠 Meta-Learning Intelligence System
    
    Sistema que observa e otimiza os próprios processos de aprendizado.
    Implementa meta-cognição sobre como o agente aprende.
    
    Features:
    - Learning Pattern Analysis: Identifica padrões nos próprios processos de aprendizado
    - Optimal Learning Rate: Ajusta taxa de aprendizado baseado no contexto
    - Learning Strategy Optimization: Otimiza quais tipos de feedback são mais valiosos
    - Adaptive Memory: Sistema de memória que esquece/retém baseado na relevância
    - Transfer Learning: Aplica lições de um domínio em outros
    - Bias Detection: Identifica e corrige vieses no próprio aprendizado
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("MetaLearningIntelligence")
        
        # Configuration
        meta_learning_config = config.get("meta_learning", {})
        self.base_learning_rate = meta_learning_config.get("base_learning_rate", 0.1)
        self.adaptive_rate_enabled = meta_learning_config.get("adaptive_rate_enabled", True)
        self.pattern_detection_threshold = meta_learning_config.get("pattern_detection_threshold", 5)
        self.memory_retention_threshold = meta_learning_config.get("memory_retention_threshold", 0.3)
        self.transfer_learning_enabled = meta_learning_config.get("transfer_learning_enabled", True)
        self.max_learning_events = meta_learning_config.get("max_learning_events", 1000)
        
        # State
        self.learning_events: deque = deque(maxlen=self.max_learning_events)
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.adaptive_memory: Dict[str, AdaptiveMemory] = {}
        self.optimal_learning_rates: Dict[str, float] = {}
        self.domain_knowledge_map: Dict[str, Set[str]] = defaultdict(set)
        self.bias_indicators: Dict[str, float] = {}
        
        # Analytics
        self.learning_analytics = {
            "total_learning_events": 0,
            "average_learning_effectiveness": 0.0,
            "optimal_rate_discoveries": 0,
            "successful_transfers": 0,
            "bias_corrections": 0,
            "memory_optimizations": 0
        }
        
        # Threading
        self.analysis_thread = None
        self.should_stop = threading.Event()
        
        # Load existing data
        self._load_learning_data()
        
        # Start analysis
        self._start_continuous_analysis()
        
        self.logger.info("🧠 Meta-Learning Intelligence System initialized!")
        self.logger.info(f"📊 Loaded {len(self.learning_events)} learning events")
        self.logger.info(f"🎯 Identified {len(self.learning_patterns)} learning patterns")
    
    def record_learning_event(self, 
                            learning_type: LearningType,
                            context: LearningContext,
                            trigger: str,
                            input_data: Dict[str, Any],
                            knowledge_gained: str,
                            performance_before: float,
                            performance_after: float,
                            confidence_before: float = 0.5,
                            confidence_after: float = 0.5,
                            feedback_quality: float = 1.0) -> LearningEvent:
        """
        🎯 CORE FUNCTION: Registra um evento de aprendizado
        
        Args:
            learning_type: Tipo de aprendizado
            context: Contexto onde aconteceu
            trigger: O que disparou o aprendizado
            input_data: Dados de entrada
            knowledge_gained: Conhecimento adquirido
            performance_before/after: Performance antes e depois
            confidence_before/after: Confiança antes e depois
            feedback_quality: Qualidade do feedback (0.0-1.0)
        """
        
        # Determine optimal learning rate for this context
        optimal_rate = self._get_optimal_learning_rate(learning_type, context, input_data)
        
        # Calculate learning time (simulated based on complexity)
        time_to_learn = self._estimate_learning_time(learning_type, input_data, optimal_rate)
        
        # Determine effectiveness
        performance_improvement = performance_after - performance_before
        effectiveness = self._classify_learning_effectiveness(performance_improvement)
        
        # Create learning event
        event = LearningEvent(
            event_id=str(int(time.time() * 1000)),
            learning_type=learning_type,
            context=context,
            trigger=trigger,
            input_data=input_data,
            learning_rate_used=optimal_rate,
            feedback_quality=feedback_quality,
            time_to_learn=time_to_learn,
            knowledge_gained=knowledge_gained,
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            performance_before=performance_before,
            performance_after=performance_after,
            effectiveness=effectiveness
        )
        
        # Store event
        self.learning_events.append(event)
        self.learning_analytics["total_learning_events"] += 1
        
        # Update adaptive memory
        self._store_in_adaptive_memory(event)
        
        # Detect new patterns
        self._detect_learning_patterns()
        
        # Update domain knowledge mapping
        self._update_domain_knowledge_map(event)
        
        self.logger.info(f"📚 Learning event recorded: {learning_type.value} in {context.value}")
        self.logger.debug(f"    Performance improvement: {performance_improvement:.3f}")
        self.logger.debug(f"    Effectiveness: {effectiveness.value}")
        
        return event
    
    def get_optimal_learning_rate(self, learning_type: LearningType, context: LearningContext, current_data: Dict[str, Any] = None) -> float:
        """Obtém taxa de aprendizado otimizada para o contexto"""
        return self._get_optimal_learning_rate(learning_type, context, current_data or {})
    
    def should_learn_from_feedback(self, feedback_type: str, feedback_quality: float, context: LearningContext) -> bool:
        """Determina se vale a pena aprender com um tipo específico de feedback"""
        
        # Check historical effectiveness of this feedback type in this context
        context_key = f"{feedback_type}_{context.value}"
        
        if context_key in self.optimal_learning_rates:
            # We have experience with this combination
            historical_effectiveness = self.optimal_learning_rates[context_key]
            
            # Only learn if feedback quality is good enough and historically effective
            return feedback_quality > 0.5 and historical_effectiveness > 0.3
        else:
            # No historical data - be optimistic but cautious
            return feedback_quality > 0.7
    
    def transfer_knowledge(self, source_domain: str, target_domain: str, knowledge_item: str) -> bool:
        """
        Tenta transferir conhecimento de um domínio para outro
        
        Returns:
            bool: True se a transferência foi bem-sucedida
        """
        if not self.transfer_learning_enabled:
            return False
        
        try:
            # Check if domains are related
            similarity = self._calculate_domain_similarity(source_domain, target_domain)
            
            if similarity > 0.6:  # Domains are similar enough
                # Find relevant knowledge in source domain
                source_knowledge = self.domain_knowledge_map.get(source_domain, set())
                
                if knowledge_item in source_knowledge:
                    # Transfer knowledge
                    self.domain_knowledge_map[target_domain].add(knowledge_item)
                    
                    # Record successful transfer
                    self.learning_analytics["successful_transfers"] += 1
                    
                    self.logger.info(f"🔄 Knowledge transferred: '{knowledge_item}' from {source_domain} to {target_domain}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in knowledge transfer: {e}")
            return False
    
    def detect_learning_bias(self) -> List[Dict[str, Any]]:
        """Detecta vieses no próprio processo de aprendizado"""
        biases_detected = []
        
        if len(self.learning_events) < 10:
            return biases_detected
        
        recent_events = list(self.learning_events)[-50:]  # Last 50 events
        
        # 1. Confirmation bias - tendência a aprender mais de feedbacks que confirmam crenças
        positive_feedback_learning = sum(1 for e in recent_events if e.feedback_quality > 0.7)
        negative_feedback_learning = sum(1 for e in recent_events if e.feedback_quality < 0.3)
        
        if positive_feedback_learning > negative_feedback_learning * 3:
            biases_detected.append({
                "type": "confirmation_bias",
                "description": "Tendência a aprender mais de feedback positivo",
                "severity": "medium",
                "ratio": positive_feedback_learning / max(negative_feedback_learning, 1)
            })
        
        # 2. Recency bias - dar muito peso a eventos recentes
        recent_weight = sum(e.learning_rate_used for e in recent_events[-10:]) / 10
        older_weight = sum(e.learning_rate_used for e in recent_events[-30:-10]) / 20
        
        if recent_weight > older_weight * 1.5:
            biases_detected.append({
                "type": "recency_bias",
                "description": "Dar muito peso a eventos recentes",
                "severity": "low",
                "ratio": recent_weight / older_weight
            })
        
        # 3. Domain bias - aprender desproporcionalmente em alguns domínios
        domain_counts = defaultdict(int)
        for event in recent_events:
            domain = event.input_data.get("domain", "unknown")
            domain_counts[domain] += 1
        
        if domain_counts:
            max_domain_count = max(domain_counts.values())
            min_domain_count = min(domain_counts.values())
            
            if max_domain_count > min_domain_count * 4:
                biases_detected.append({
                    "type": "domain_bias",
                    "description": "Aprendizado concentrado em poucos domínios",
                    "severity": "high",
                    "imbalance_ratio": max_domain_count / min_domain_count
                })
        
        # Update bias indicators
        for bias in biases_detected:
            self.bias_indicators[bias["type"]] = bias.get("ratio", 1.0)
            self.learning_analytics["bias_corrections"] += 1
        
        if biases_detected:
            self.logger.warning(f"🎭 Detected {len(biases_detected)} learning biases")
            for bias in biases_detected:
                self.logger.warning(f"    - {bias['type']}: {bias['description']}")
        
        return biases_detected
    
    def optimize_memory_retention(self) -> int:
        """Otimiza retenção de memória, removendo itens menos relevantes"""
        
        if len(self.adaptive_memory) < 100:  # Not enough to optimize
            return 0
        
        # Calculate retention strength for all memories
        retention_scores = {}
        for memory_id, memory in self.adaptive_memory.items():
            retention_scores[memory_id] = memory.calculate_retention_strength()
        
        # Remove memories below threshold
        memories_to_remove = [
            memory_id for memory_id, score in retention_scores.items()
            if score < self.memory_retention_threshold
        ]
        
        for memory_id in memories_to_remove:
            del self.adaptive_memory[memory_id]
        
        self.learning_analytics["memory_optimizations"] += 1
        
        if memories_to_remove:
            self.logger.info(f"🧹 Optimized memory: removed {len(memories_to_remove)} low-relevance items")
        
        return len(memories_to_remove)
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Gera insights sobre o próprio processo de aprendizado"""
        
        if len(self.learning_events) < 5:
            return {"insights": [], "recommendation": "Need more learning events for analysis"}
        
        recent_events = list(self.learning_events)[-20:]
        insights = []
        
        # 1. Learning effectiveness trends
        effectiveness_scores = [
            self._effectiveness_to_score(event.effectiveness) 
            for event in recent_events
        ]
        
        if len(effectiveness_scores) >= 2:
            trend = "improving" if effectiveness_scores[-1] > effectiveness_scores[0] else "declining"
            avg_effectiveness = statistics.mean(effectiveness_scores)
            
            insights.append({
                "type": "effectiveness_trend",
                "trend": trend,
                "average_effectiveness": avg_effectiveness,
                "description": f"Learning effectiveness is {trend} (avg: {avg_effectiveness:.2f})"
            })
        
        # 2. Optimal learning contexts
        context_effectiveness = defaultdict(list)
        for event in recent_events:
            score = self._effectiveness_to_score(event.effectiveness)
            context_effectiveness[event.context.value].append(score)
        
        if context_effectiveness:
            best_context = max(context_effectiveness.items(), key=lambda x: statistics.mean(x[1]))
            worst_context = min(context_effectiveness.items(), key=lambda x: statistics.mean(x[1]))
            
            insights.append({
                "type": "optimal_contexts",
                "best_context": best_context[0],
                "best_score": statistics.mean(best_context[1]),
                "worst_context": worst_context[0],
                "worst_score": statistics.mean(worst_context[1]),
                "description": f"Learn best in {best_context[0]}, struggle in {worst_context[0]}"
            })
        
        # 3. Learning rate optimization opportunities
        rate_effectiveness = {}
        for event in recent_events:
            rate_bucket = round(event.learning_rate_used, 1)
            if rate_bucket not in rate_effectiveness:
                rate_effectiveness[rate_bucket] = []
            rate_effectiveness[rate_bucket].append(self._effectiveness_to_score(event.effectiveness))
        
        if rate_effectiveness:
            optimal_rate = max(rate_effectiveness.items(), key=lambda x: statistics.mean(x[1]))
            
            insights.append({
                "type": "optimal_learning_rate",
                "optimal_rate": optimal_rate[0],
                "effectiveness": statistics.mean(optimal_rate[1]),
                "description": f"Optimal learning rate appears to be {optimal_rate[0]}"
            })
        
        # 4. Knowledge transfer opportunities
        domain_overlap = {}
        domains = list(self.domain_knowledge_map.keys())
        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                overlap = len(self.domain_knowledge_map[domain1].intersection(self.domain_knowledge_map[domain2]))
                if overlap > 0:
                    domain_overlap[f"{domain1}-{domain2}"] = overlap
        
        if domain_overlap:
            best_transfer_opportunity = max(domain_overlap.items(), key=lambda x: x[1])
            
            insights.append({
                "type": "transfer_learning_opportunity",
                "domain_pair": best_transfer_opportunity[0],
                "shared_knowledge": best_transfer_opportunity[1],
                "description": f"High knowledge overlap between {best_transfer_opportunity[0]}"
            })
        
        return {
            "insights": insights,
            "total_events_analyzed": len(recent_events),
            "patterns_identified": len(self.learning_patterns),
            "biases_detected": len(self.bias_indicators),
            "memory_items": len(self.adaptive_memory),
            "recommendation": self._generate_learning_recommendation(insights)
        }
    
    def _get_optimal_learning_rate(self, learning_type: LearningType, context: LearningContext, data: Dict[str, Any]) -> float:
        """Determina taxa de aprendizado otimizada"""
        
        if not self.adaptive_rate_enabled:
            return self.base_learning_rate
        
        # Create context key
        context_key = f"{learning_type.value}_{context.value}"
        
        # Check if we have learned optimal rate for this combination
        if context_key in self.optimal_learning_rates:
            return self.optimal_learning_rates[context_key]
        
        # Check patterns
        for pattern in self.learning_patterns.values():
            if (learning_type.value in pattern.pattern_type and 
                context in pattern.contexts_where_effective):
                return pattern.optimal_learning_rate
        
        # Adjust base rate based on data complexity
        complexity = self._assess_data_complexity(data)
        
        if complexity > 0.8:
            adjusted_rate = self.base_learning_rate * 0.5  # Slower for complex data
        elif complexity < 0.3:
            adjusted_rate = self.base_learning_rate * 1.5  # Faster for simple data
        else:
            adjusted_rate = self.base_learning_rate
        
        return min(max(adjusted_rate, 0.01), 1.0)  # Clamp between 0.01 and 1.0
    
    def _estimate_learning_time(self, learning_type: LearningType, data: Dict[str, Any], learning_rate: float) -> float:
        """Estima tempo necessário para aprender"""
        
        base_times = {
            LearningType.ERROR_CORRECTION: 2.0,
            LearningType.PATTERN_RECOGNITION: 5.0,
            LearningType.STRATEGY_OPTIMIZATION: 8.0,
            LearningType.PERFORMANCE_IMPROVEMENT: 3.0,
            LearningType.KNOWLEDGE_TRANSFER: 4.0,
            LearningType.BIAS_CORRECTION: 6.0,
            LearningType.FAILURE_ANALYSIS: 7.0
        }
        
        base_time = base_times.get(learning_type, 5.0)
        complexity = self._assess_data_complexity(data)
        
        # Higher learning rate = faster learning, but diminishing returns
        rate_factor = 1.0 / (learning_rate + 0.1)
        
        # More complex data takes longer
        complexity_factor = 1.0 + complexity
        
        return base_time * rate_factor * complexity_factor
    
    def _classify_learning_effectiveness(self, performance_improvement: float) -> LearningEffectiveness:
        """Classifica efetividade do aprendizado baseado na melhoria"""
        
        if performance_improvement < -0.05:
            return LearningEffectiveness.COUNTERPRODUCTIVE
        elif performance_improvement < 0.05:
            return LearningEffectiveness.INEFFECTIVE
        elif performance_improvement < 0.2:
            return LearningEffectiveness.SLIGHTLY_EFFECTIVE
        elif performance_improvement < 0.5:
            return LearningEffectiveness.MODERATELY_EFFECTIVE
        elif performance_improvement < 0.8:
            return LearningEffectiveness.EFFECTIVE
        else:
            return LearningEffectiveness.HIGHLY_EFFECTIVE
    
    def _store_in_adaptive_memory(self, event: LearningEvent):
        """Armazena evento na memória adaptativa"""
        
        # Calculate importance based on effectiveness and novelty
        importance = self._calculate_memory_importance(event)
        
        memory = AdaptiveMemory(
            memory_id=event.event_id,
            knowledge_item=event.to_dict(),
            importance_score=importance,
            access_frequency=1,
            last_accessed=datetime.now(),
            creation_date=event.timestamp,
            domain=event.input_data.get("domain", "general")
        )
        
        self.adaptive_memory[event.event_id] = memory
    
    def _detect_learning_patterns(self):
        """Detecta padrões nos eventos de aprendizado"""
        
        if len(self.learning_events) < self.pattern_detection_threshold:
            return
        
        # Group events by learning type and context
        groups = defaultdict(list)
        for event in self.learning_events:
            key = f"{event.learning_type.value}_{event.context.value}"
            groups[key].append(event)
        
        # Analyze each group for patterns
        for group_key, events in groups.items():
            if len(events) >= 3:  # Need at least 3 events to identify pattern
                pattern = self._analyze_event_group(group_key, events)
                if pattern:
                    self.learning_patterns[group_key] = pattern
    
    def _analyze_event_group(self, group_key: str, events: List[LearningEvent]) -> Optional[LearningPattern]:
        """Analisa um grupo de eventos para identificar padrões"""
        
        if len(events) < 3:
            return None
        
        # Calculate average metrics
        avg_rate = statistics.mean(e.learning_rate_used for e in events)
        avg_time = statistics.mean(e.time_to_learn for e in events)
        success_rate = len([e for e in events if e.effectiveness in [LearningEffectiveness.EFFECTIVE, LearningEffectiveness.HIGHLY_EFFECTIVE]]) / len(events)
        
        # Identify optimal conditions
        effective_events = [e for e in events if e.effectiveness in [LearningEffectiveness.EFFECTIVE, LearningEffectiveness.HIGHLY_EFFECTIVE]]
        
        if effective_events:
            optimal_rate = statistics.mean(e.learning_rate_used for e in effective_events)
            optimal_feedback_types = list(set(e.trigger for e in effective_events))
            effective_contexts = list(set(e.context for e in effective_events))
            domains = list(set(e.input_data.get("domain", "general") for e in effective_events))
        else:
            optimal_rate = avg_rate
            optimal_feedback_types = []
            effective_contexts = []
            domains = []
        
        pattern = LearningPattern(
            pattern_id=group_key,
            pattern_type=group_key,
            conditions=[f"learning_type:{group_key.split('_')[0]}", f"context:{group_key.split('_')[1]}"],
            optimal_learning_rate=optimal_rate,
            optimal_feedback_types=optimal_feedback_types,
            typical_time_to_learn=avg_time,
            success_rate=success_rate,
            contexts_where_effective=effective_contexts,
            knowledge_domains=domains,
            confidence_score=min(1.0, len(events) / 10.0),  # More events = higher confidence
            usage_count=len(events)
        )
        
        return pattern
    
    def _update_domain_knowledge_map(self, event: LearningEvent):
        """Atualiza mapeamento de conhecimento por domínio"""
        
        domain = event.input_data.get("domain", "general")
        knowledge = event.knowledge_gained
        
        # Extract key terms from knowledge
        knowledge_terms = self._extract_knowledge_terms(knowledge)
        
        for term in knowledge_terms:
            self.domain_knowledge_map[domain].add(term)
    
    def _extract_knowledge_terms(self, knowledge: str) -> List[str]:
        """Extrai termos-chave do conhecimento"""
        
        # Simple keyword extraction (could be enhanced with NLP)
        words = knowledge.lower().split()
        
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        return meaningful_words[:5]  # Top 5 terms
    
    def _calculate_domain_similarity(self, domain1: str, domain2: str) -> float:
        """Calcula similaridade entre domínios"""
        
        if domain1 not in self.domain_knowledge_map or domain2 not in self.domain_knowledge_map:
            return 0.0
        
        knowledge1 = self.domain_knowledge_map[domain1]
        knowledge2 = self.domain_knowledge_map[domain2]
        
        if not knowledge1 or not knowledge2:
            return 0.0
        
        # Jaccard similarity
        intersection = knowledge1.intersection(knowledge2)
        union = knowledge1.union(knowledge2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _assess_data_complexity(self, data: Dict[str, Any]) -> float:
        """Avalia complexidade dos dados"""
        
        # Simple complexity assessment based on data structure
        complexity = 0.0
        
        # Number of keys
        complexity += min(len(data), 10) / 10 * 0.3
        
        # Nested structures
        nested_count = sum(1 for v in data.values() if isinstance(v, (dict, list)))
        complexity += min(nested_count, 5) / 5 * 0.4
        
        # String length (if applicable)
        text_length = sum(len(str(v)) for v in data.values() if isinstance(v, str))
        complexity += min(text_length, 1000) / 1000 * 0.3
        
        return complexity
    
    def _calculate_memory_importance(self, event: LearningEvent) -> float:
        """Calcula importância de um evento para armazenamento na memória"""
        
        effectiveness_score = self._effectiveness_to_score(event.effectiveness)
        novelty_score = 1.0 - min(event.usage_count / 10, 1.0) if hasattr(event, 'usage_count') else 1.0
        learning_gain = event.calculate_learning_gain()
        
        importance = (effectiveness_score * 0.4 + novelty_score * 0.3 + abs(learning_gain) * 0.3)
        
        return min(max(importance, 0.0), 1.0)
    
    def _effectiveness_to_score(self, effectiveness: LearningEffectiveness) -> float:
        """Converte efetividade para score numérico"""
        scores = {
            LearningEffectiveness.COUNTERPRODUCTIVE: -0.2,
            LearningEffectiveness.INEFFECTIVE: 0.1,
            LearningEffectiveness.SLIGHTLY_EFFECTIVE: 0.3,
            LearningEffectiveness.MODERATELY_EFFECTIVE: 0.6,
            LearningEffectiveness.EFFECTIVE: 0.8,
            LearningEffectiveness.HIGHLY_EFFECTIVE: 1.0
        }
        return scores.get(effectiveness, 0.5)
    
    def _generate_learning_recommendation(self, insights: List[Dict[str, Any]]) -> str:
        """Gera recomendação baseada nos insights"""
        
        if not insights:
            return "Continue learning to generate insights"
        
        recommendations = []
        
        for insight in insights:
            if insight["type"] == "effectiveness_trend":
                if insight["trend"] == "declining":
                    recommendations.append("Consider adjusting learning strategies - effectiveness is declining")
                else:
                    recommendations.append("Current learning approach is working well")
            
            elif insight["type"] == "optimal_contexts":
                recommendations.append(f"Focus more learning in {insight['best_context']} context")
            
            elif insight["type"] == "optimal_learning_rate":
                recommendations.append(f"Use learning rate around {insight['optimal_rate']} for better results")
            
            elif insight["type"] == "transfer_learning_opportunity":
                recommendations.append(f"High transfer potential between {insight['domain_pair']}")
        
        return "; ".join(recommendations) if recommendations else "Continue current learning approach"
    
    def _start_continuous_analysis(self):
        """Inicia análise contínua em background"""
        
        if self.analysis_thread is None or not self.analysis_thread.is_alive():
            self.analysis_thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.analysis_thread.start()
    
    def _analysis_loop(self):
        """Loop de análise contínua"""
        
        while not self.should_stop.wait(60):  # Run every minute
            try:
                # Detect patterns
                self._detect_learning_patterns()
                
                # Check for biases
                self.detect_learning_bias()
                
                # Optimize memory
                if len(self.adaptive_memory) > 50:
                    self.optimize_memory_retention()
                
                # Update analytics
                self._update_learning_analytics()
                
                # Save state
                self._save_learning_data()
                
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
    
    def _update_learning_analytics(self):
        """Atualiza analytics de aprendizado"""
        
        if self.learning_events:
            recent_events = list(self.learning_events)[-20:]
            effectiveness_scores = [self._effectiveness_to_score(e.effectiveness) for e in recent_events]
            self.learning_analytics["average_learning_effectiveness"] = statistics.mean(effectiveness_scores)
        
        self.learning_analytics["optimal_rate_discoveries"] = len(self.optimal_learning_rates)
    
    def _load_learning_data(self):
        """Carrega dados de aprendizado salvos"""
        
        try:
            data_file = Path("data/meta_learning/learning_data.json")
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load learning events
                for event_data in data.get("learning_events", []):
                    event_data["learning_type"] = LearningType(event_data["learning_type"])
                    event_data["context"] = LearningContext(event_data["context"])
                    event_data["effectiveness"] = LearningEffectiveness(event_data["effectiveness"])
                    event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"])
                    
                    event = LearningEvent(**{k: v for k, v in event_data.items() if k != "learning_gain"})
                    self.learning_events.append(event)
                
                # Load other data
                self.optimal_learning_rates = data.get("optimal_learning_rates", {})
                self.learning_analytics = data.get("learning_analytics", self.learning_analytics)
                
                self.logger.info(f"📂 Loaded {len(self.learning_events)} learning events from disk")
                
        except Exception as e:
            self.logger.warning(f"Could not load learning data: {e}")
    
    def _save_learning_data(self):
        """Salva dados de aprendizado"""
        
        try:
            data_file = Path("data/meta_learning/learning_data.json")
            data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data for serialization
            events_data = [event.to_dict() for event in list(self.learning_events)[-100:]]  # Keep last 100
            
            data = {
                "learning_events": events_data,
                "optimal_learning_rates": self.optimal_learning_rates,
                "learning_analytics": self.learning_analytics,
                "domain_knowledge_map": {k: list(v) for k, v in self.domain_knowledge_map.items()},
                "bias_indicators": self.bias_indicators,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
    
    def get_meta_learning_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de meta-aprendizado"""
        
        return {
            "total_learning_events": len(self.learning_events),
            "learning_patterns_identified": len(self.learning_patterns),
            "adaptive_memory_items": len(self.adaptive_memory),
            "domain_knowledge_areas": len(self.domain_knowledge_map),
            "biases_detected": len(self.bias_indicators),
            "analytics": self.learning_analytics,
            "recent_insights": self.get_learning_insights(),
            "adaptive_rate_enabled": self.adaptive_rate_enabled,
            "transfer_learning_enabled": self.transfer_learning_enabled
        }
    
    def shutdown(self):
        """Encerra o sistema"""
        
        self.logger.info("🛑 Shutting down Meta-Learning Intelligence...")
        
        self.should_stop.set()
        
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5)
        
        # Final save
        self._save_learning_data()
        
        self.logger.info("✅ Meta-Learning Intelligence shutdown complete")

# Singleton instance
_meta_learning_intelligence = None

def get_meta_learning_intelligence(config: Dict[str, Any], logger: logging.Logger) -> MetaLearningIntelligence:
    """Get singleton instance of MetaLearningIntelligence"""
    global _meta_learning_intelligence
    if _meta_learning_intelligence is None:
        _meta_learning_intelligence = MetaLearningIntelligence(config, logger)
    return _meta_learning_intelligence