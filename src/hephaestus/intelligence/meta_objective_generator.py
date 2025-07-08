"""
🎯 META-OBJECTIVE GENERATOR
Sistema que gera objetivos para melhorar a própria capacidade de gerar objetivos - a 6ª meta-funcionalidade!

Este sistema implementa meta-cognição recursiva através de:
- Self-Capability Analysis: Análise das próprias capacidades de geração de objetivos
- Recursive Improvement: Melhoria recursiva dos processos de geração
- Meta-Objective Generation: Criação de objetivos para melhorar objetivos
- Performance Pattern Analysis: Análise de padrões de performance na geração
- Strategic Depth Enhancement: Aumento da profundidade estratégica
- Context-Aware Objective Crafting: Criação de objetivos conscientes do contexto

É literalmente o sistema que ensina a si mesmo como ser melhor em definir o que fazer!
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
import re

class ObjectiveType(Enum):
    """Tipos de objetivos que podem ser gerados"""
    CAPABILITY_EXPANSION = "capability_expansion"        # Expandir capacidades
    EFFICIENCY_IMPROVEMENT = "efficiency_improvement"    # Melhorar eficiência
    QUALITY_ENHANCEMENT = "quality_enhancement"         # Melhorar qualidade
    STRATEGIC_DEEPENING = "strategic_deepening"         # Aprofundar estratégia
    CREATIVE_EXPLORATION = "creative_exploration"       # Exploração criativa
    LEARNING_ACCELERATION = "learning_acceleration"     # Acelerar aprendizado
    ERROR_REDUCTION = "error_reduction"                 # Reduzir erros
    CONTEXT_AWARENESS = "context_awareness"             # Melhorar consciência contextual
    COLLABORATIVE_ENHANCEMENT = "collaborative_enhancement"  # Melhorar colaboração
    SELF_OPTIMIZATION = "self_optimization"             # Auto-otimização

class ObjectiveComplexity(Enum):
    """Níveis de complexidade dos objetivos"""
    SIMPLE = "simple"           # Objetivos simples, diretos
    MODERATE = "moderate"       # Objetivos moderados
    COMPLEX = "complex"         # Objetivos complexos
    STRATEGIC = "strategic"     # Objetivos estratégicos
    TRANSFORMATIONAL = "transformational"  # Objetivos transformacionais

class ObjectiveScope(Enum):
    """Escopo dos objetivos"""
    IMMEDIATE = "immediate"     # Impacto imediato
    SHORT_TERM = "short_term"   # Curto prazo (horas)
    MEDIUM_TERM = "medium_term" # Médio prazo (dias)
    LONG_TERM = "long_term"     # Longo prazo (semanas)
    STRATEGIC = "strategic"     # Estratégico (meses)

@dataclass
class GeneratedObjective:
    """Objetivo gerado pelo sistema"""
    objective_id: str
    content: str
    objective_type: ObjectiveType
    complexity: ObjectiveComplexity
    scope: ObjectiveScope
    expected_impact: float          # 0.0 - 1.0
    generation_confidence: float    # 0.0 - 1.0
    prerequisites: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    estimated_effort: float = 0.0   # Hours
    meta_reasoning: str = ""        # Why this objective was generated
    context_factors: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def calculate_priority_score(self) -> float:
        """Calcula pontuação de prioridade do objetivo"""
        # Fatores: impacto esperado, confiança, escopo, complexidade
        impact_weight = 0.4
        confidence_weight = 0.3
        scope_weight = 0.2
        complexity_weight = 0.1
        
        # Scope scoring
        scope_scores = {
            ObjectiveScope.IMMEDIATE: 1.0,
            ObjectiveScope.SHORT_TERM: 0.8,
            ObjectiveScope.MEDIUM_TERM: 0.6,
            ObjectiveScope.LONG_TERM: 0.4,
            ObjectiveScope.STRATEGIC: 0.9
        }
        
        # Complexity scoring (moderate complexity preferred)
        complexity_scores = {
            ObjectiveComplexity.SIMPLE: 0.6,
            ObjectiveComplexity.MODERATE: 1.0,
            ObjectiveComplexity.COMPLEX: 0.7,
            ObjectiveComplexity.STRATEGIC: 0.8,
            ObjectiveComplexity.TRANSFORMATIONAL: 0.5
        }
        
        priority = (
            self.expected_impact * impact_weight +
            self.generation_confidence * confidence_weight +
            scope_scores[self.scope] * scope_weight +
            complexity_scores[self.complexity] * complexity_weight
        )
        
        return min(1.0, max(0.0, priority))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "objective_id": self.objective_id,
            "content": self.content,
            "objective_type": self.objective_type.value,
            "complexity": self.complexity.value,
            "scope": self.scope.value,
            "expected_impact": self.expected_impact,
            "generation_confidence": self.generation_confidence,
            "prerequisites": self.prerequisites,
            "success_criteria": self.success_criteria,
            "estimated_effort": self.estimated_effort,
            "meta_reasoning": self.meta_reasoning,
            "context_factors": self.context_factors,
            "timestamp": self.timestamp.isoformat(),
            "priority_score": self.calculate_priority_score()
        }

@dataclass
class CapabilityAssessment:
    """Avaliação das capacidades de geração de objetivos"""
    assessment_id: str
    timestamp: datetime
    current_capabilities: List[str]
    capability_gaps: List[str]
    improvement_opportunities: List[str]
    strengths: List[str]
    weaknesses: List[str]
    confidence_in_assessment: float
    context_awareness_level: float
    strategic_thinking_depth: float
    creativity_level: float
    objective_quality_score: float
    
    def calculate_overall_capability(self) -> float:
        """Calcula capacidade geral de geração de objetivos"""
        factors = [
            self.confidence_in_assessment,
            self.context_awareness_level,
            self.strategic_thinking_depth,
            self.creativity_level,
            self.objective_quality_score
        ]
        return statistics.mean(factors)

@dataclass
class MetaObjectivePattern:
    """Padrão identificado na geração de meta-objetivos"""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    success_rate: float
    average_impact: float
    conditions: List[str]
    recommended_usage: str
    discovered_at: datetime = field(default_factory=datetime.now)

class MetaObjectiveGenerator:
    """
    🎯 Meta-Objective Generator - Sistema que gera objetivos para melhorar objetivos
    
    Este é o sistema de meta-cognição recursiva que:
    1. Analisa as próprias capacidades de geração de objetivos
    2. Identifica pontos de melhoria na geração
    3. Cria objetivos para melhorar a capacidade de criar objetivos
    4. Aprende padrões de sucesso na geração
    5. Melhora recursivamente sua própria estratégia
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("MetaObjectiveGenerator")
        
        # Configuration
        meta_objective_config = config.get("meta_objective_generator", {})
        self.generation_interval = meta_objective_config.get("generation_interval", 600)  # 10 minutes
        self.max_concurrent_objectives = meta_objective_config.get("max_concurrent_objectives", 5)
        self.capability_analysis_interval = meta_objective_config.get("capability_analysis_interval", 1800)  # 30 minutes
        self.pattern_detection_threshold = meta_objective_config.get("pattern_detection_threshold", 3)
        self.improvement_threshold = meta_objective_config.get("improvement_threshold", 0.1)
        self.enabled = meta_objective_config.get("enabled", True)
        
        # Data storage
        self.data_dir = Path("data/intelligence/meta_objectives")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # State
        self.generated_objectives: deque = deque(maxlen=1000)
        self.capability_assessments: deque = deque(maxlen=100)
        self.detected_patterns: Dict[str, MetaObjectivePattern] = {}
        self.active_objectives: List[GeneratedObjective] = []
        self.completed_objectives: List[GeneratedObjective] = []
        self.generation_history: List[Dict[str, Any]] = []
        
        # Analytics
        self.meta_objective_analytics = {
            "total_objectives_generated": 0,
            "successful_objectives": 0,
            "patterns_identified": 0,
            "capability_improvements_detected": 0,
            "average_objective_quality": 0.0,
            "generation_efficiency": 0.0,
            "recursive_improvement_count": 0,
            "meta_learning_events": 0
        }
        
        # Threading
        self.should_stop = threading.Event()
        self.generation_thread = None
        self.analysis_thread = None
        
        # Load data
        self._load_meta_objective_data()
        
        # Initialize
        if self.enabled:
            self._start_background_processing()
            self.logger.info("🎯 Meta-Objective Generator initialized!")
            self.logger.info(f"📊 Generation interval: {self.generation_interval}s")
            self.logger.info(f"📈 {len(self.generated_objectives)} objectives in history")
        else:
            self.logger.info("⚠️ Meta-Objective Generator disabled in configuration")
    
    def generate_meta_objective(self, context: Optional[Dict[str, Any]] = None) -> GeneratedObjective:
        """Gera um meta-objetivo para melhorar a geração de objetivos"""
        if not self.enabled:
            raise RuntimeError("Meta-Objective Generator is disabled")
        
        self.logger.info("🎯 Starting meta-objective generation...")
        
        # 1. Analyze current capabilities
        capability_assessment = self._assess_current_capabilities()
        
        # 2. Identify improvement opportunities
        opportunities = self._identify_improvement_opportunities(capability_assessment)
        
        # 3. Select best opportunity
        selected_opportunity = self._select_best_opportunity(opportunities, context)
        
        # 4. Generate objective based on opportunity
        meta_objective = self._craft_meta_objective(selected_opportunity, capability_assessment, context)
        
        # 5. Store and track
        self.generated_objectives.append(meta_objective)
        self.active_objectives.append(meta_objective)
        self.meta_objective_analytics["total_objectives_generated"] += 1
        
        # 6. Update analytics
        self._update_generation_analytics(meta_objective)
        
        self.logger.info(f"✅ Meta-objective generated: {meta_objective.content[:100]}...")
        self.logger.info(f"🎯 Type: {meta_objective.objective_type.value}, Priority: {meta_objective.calculate_priority_score():.3f}")
        
        return meta_objective
    
    def _assess_current_capabilities(self) -> CapabilityAssessment:
        """Avalia capacidades atuais de geração de objetivos"""
        assessment_id = f"capability_assessment_{int(time.time())}"
        
        # Analyze recent objective generation performance
        recent_objectives = list(self.generated_objectives)[-20:]  # Last 20 objectives
        
        # Current capabilities (what we can do well)
        current_capabilities = [
            "basic_objective_generation",
            "context_analysis",
            "priority_assessment",
            "success_criteria_definition"
        ]
        
        # Capability gaps (what we need to improve)
        capability_gaps = []
        
        if len(recent_objectives) > 0:
            avg_quality = statistics.mean(obj.generation_confidence for obj in recent_objectives)
            if avg_quality < 0.7:
                capability_gaps.append("objective_quality_improvement")
            
            avg_impact = statistics.mean(obj.expected_impact for obj in recent_objectives)
            if avg_impact < 0.6:
                capability_gaps.append("impact_assessment_accuracy")
            
            # Check for diversity in objective types
            types_used = set(obj.objective_type for obj in recent_objectives)
            if len(types_used) < 5:
                capability_gaps.append("objective_type_diversity")
        else:
            capability_gaps.extend([
                "objective_generation_experience",
                "pattern_recognition",
                "impact_assessment"
            ])
        
        # Improvement opportunities
        improvement_opportunities = [
            "enhance_strategic_thinking",
            "improve_context_awareness", 
            "increase_creativity",
            "optimize_effort_estimation",
            "enhance_success_criteria_definition"
        ]
        
        # Strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if len(recent_objectives) > 5:
            # Calculate performance metrics
            completion_rate = len([obj for obj in recent_objectives if obj in self.completed_objectives]) / len(recent_objectives)
            if completion_rate > 0.6:
                strengths.append("good_completion_rate")
            else:
                weaknesses.append("low_completion_rate")
            
            # Check consistency
            quality_variance = statistics.variance([obj.generation_confidence for obj in recent_objectives]) if len(recent_objectives) > 1 else 0
            if quality_variance < 0.1:
                strengths.append("consistent_quality")
            else:
                weaknesses.append("inconsistent_quality")
        
        # Confidence and capability scores
        confidence_in_assessment = min(1.0, len(recent_objectives) / 20.0)  # More data = more confidence
        context_awareness_level = 0.7  # Base level, could be enhanced
        strategic_thinking_depth = 0.6  # Base level
        creativity_level = 0.5  # Base level
        objective_quality_score = statistics.mean([obj.generation_confidence for obj in recent_objectives]) if recent_objectives else 0.5
        
        assessment = CapabilityAssessment(
            assessment_id=assessment_id,
            timestamp=datetime.now(),
            current_capabilities=current_capabilities,
            capability_gaps=capability_gaps,
            improvement_opportunities=improvement_opportunities,
            strengths=strengths,
            weaknesses=weaknesses,
            confidence_in_assessment=confidence_in_assessment,
            context_awareness_level=context_awareness_level,
            strategic_thinking_depth=strategic_thinking_depth,
            creativity_level=creativity_level,
            objective_quality_score=objective_quality_score
        )
        
        self.capability_assessments.append(assessment)
        return assessment
    
    def _identify_improvement_opportunities(self, assessment: CapabilityAssessment) -> List[Dict[str, Any]]:
        """Identifica oportunidades de melhoria específicas"""
        opportunities = []
        
        # Based on capability gaps
        for gap in assessment.capability_gaps:
            if gap == "objective_quality_improvement":
                opportunities.append({
                    "type": ObjectiveType.QUALITY_ENHANCEMENT,
                    "description": "Improve the quality and clarity of generated objectives",
                    "priority": 0.9,
                    "complexity": ObjectiveComplexity.MODERATE,
                    "scope": ObjectiveScope.SHORT_TERM
                })
            
            elif gap == "impact_assessment_accuracy":
                opportunities.append({
                    "type": ObjectiveType.EFFICIENCY_IMPROVEMENT,
                    "description": "Enhance accuracy in predicting objective impact",
                    "priority": 0.8,
                    "complexity": ObjectiveComplexity.COMPLEX,
                    "scope": ObjectiveScope.MEDIUM_TERM
                })
            
            elif gap == "objective_type_diversity":
                opportunities.append({
                    "type": ObjectiveType.CREATIVE_EXPLORATION,
                    "description": "Expand repertoire of objective types and approaches",
                    "priority": 0.7,
                    "complexity": ObjectiveComplexity.MODERATE,
                    "scope": ObjectiveScope.MEDIUM_TERM
                })
        
        # Based on weaknesses
        for weakness in assessment.weaknesses:
            if weakness == "low_completion_rate":
                opportunities.append({
                    "type": ObjectiveType.STRATEGIC_DEEPENING,
                    "description": "Improve objective feasibility and completion rates",
                    "priority": 0.85,
                    "complexity": ObjectiveComplexity.STRATEGIC,
                    "scope": ObjectiveScope.MEDIUM_TERM
                })
            
            elif weakness == "inconsistent_quality":
                opportunities.append({
                    "type": ObjectiveType.SELF_OPTIMIZATION,
                    "description": "Standardize objective generation process for consistency",
                    "priority": 0.75,
                    "complexity": ObjectiveComplexity.MODERATE,
                    "scope": ObjectiveScope.SHORT_TERM
                })
        
        # Based on improvement opportunities
        for improvement in assessment.improvement_opportunities:
            if improvement == "enhance_strategic_thinking":
                opportunities.append({
                    "type": ObjectiveType.STRATEGIC_DEEPENING,
                    "description": "Develop deeper strategic thinking capabilities",
                    "priority": 0.8,
                    "complexity": ObjectiveComplexity.STRATEGIC,
                    "scope": ObjectiveScope.LONG_TERM
                })
            
            elif improvement == "improve_context_awareness":
                opportunities.append({
                    "type": ObjectiveType.CONTEXT_AWARENESS,
                    "description": "Enhance understanding of context in objective generation",
                    "priority": 0.85,
                    "complexity": ObjectiveComplexity.COMPLEX,
                    "scope": ObjectiveScope.MEDIUM_TERM
                })
        
        # Always include recursive improvement opportunity
        opportunities.append({
            "type": ObjectiveType.SELF_OPTIMIZATION,
            "description": "Analyze and improve the meta-objective generation process itself",
            "priority": 0.9,
            "complexity": ObjectiveComplexity.TRANSFORMATIONAL,
            "scope": ObjectiveScope.STRATEGIC
        })
        
        return opportunities
    
    def _select_best_opportunity(self, opportunities: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Seleciona a melhor oportunidade baseada no contexto"""
        if not opportunities:
            # Fallback opportunity
            return {
                "type": ObjectiveType.CAPABILITY_EXPANSION,
                "description": "Expand meta-objective generation capabilities",
                "priority": 0.7,
                "complexity": ObjectiveComplexity.MODERATE,
                "scope": ObjectiveScope.MEDIUM_TERM
            }
        
        # Score opportunities based on context and current needs
        scored_opportunities = []
        
        for opportunity in opportunities:
            score = opportunity["priority"]
            
            # Context adjustments
            if context:
                # If system is under stress, prefer immediate improvements
                if context.get("system_stress", 0) > 0.7:
                    if opportunity["scope"] == ObjectiveScope.IMMEDIATE:
                        score += 0.2
                    elif opportunity["scope"] == ObjectiveScope.SHORT_TERM:
                        score += 0.1
                
                # If recent failures, prefer error reduction
                if context.get("recent_failure_rate", 0) > 0.3:
                    if opportunity["type"] == ObjectiveType.ERROR_REDUCTION:
                        score += 0.3
                
                # If low creativity, prefer creative exploration
                if context.get("creativity_level", 0.5) < 0.4:
                    if opportunity["type"] == ObjectiveType.CREATIVE_EXPLORATION:
                        score += 0.2
            
            scored_opportunities.append((score, opportunity))
        
        # Select highest scored opportunity
        scored_opportunities.sort(key=lambda x: x[0], reverse=True)
        return scored_opportunities[0][1]
    
    def _craft_meta_objective(self, opportunity: Dict[str, Any], assessment: CapabilityAssessment, context: Optional[Dict[str, Any]]) -> GeneratedObjective:
        """Cria um meta-objetivo específico baseado na oportunidade"""
        objective_id = f"meta_obj_{int(time.time())}_{hashlib.md5(opportunity['description'].encode()).hexdigest()[:8]}"
        
        # Craft detailed objective content
        base_description = opportunity["description"]
        
        # Add specific context and reasoning
        meta_reasoning = f"Generated to address {opportunity['type'].value} based on capability assessment. "
        meta_reasoning += f"Current capability level: {assessment.calculate_overall_capability():.2f}. "
        
        if assessment.capability_gaps:
            meta_reasoning += f"Addressing gaps: {', '.join(assessment.capability_gaps[:3])}. "
        
        # Enhance description with specific actions
        if opportunity["type"] == ObjectiveType.QUALITY_ENHANCEMENT:
            content = f"Enhance objective generation quality by implementing better validation criteria and clarity checks. Current quality score: {assessment.objective_quality_score:.2f}. Target: 0.85+"
            success_criteria = [
                "Achieve average objective clarity score > 0.85",
                "Reduce ambiguous objectives by 50%",
                "Implement quality validation checklist"
            ]
        
        elif opportunity["type"] == ObjectiveType.STRATEGIC_DEEPENING:
            content = f"Deepen strategic thinking in objective generation by incorporating longer-term vision and interconnected planning. Current depth: {assessment.strategic_thinking_depth:.2f}."
            success_criteria = [
                "Generate objectives with clear strategic alignment",
                "Include interconnected objective chains",
                "Improve long-term impact prediction accuracy"
            ]
        
        elif opportunity["type"] == ObjectiveType.CONTEXT_AWARENESS:
            content = f"Improve context awareness in objective generation by better analyzing environmental factors and constraints. Current level: {assessment.context_awareness_level:.2f}."
            success_criteria = [
                "Include context analysis in 100% of objectives",
                "Reduce context-mismatched objectives by 70%",
                "Improve contextual relevance scores"
            ]
        
        elif opportunity["type"] == ObjectiveType.SELF_OPTIMIZATION:
            content = "Analyze and optimize the meta-objective generation process through recursive self-improvement and process refinement."
            success_criteria = [
                "Identify 3+ process improvement opportunities",
                "Implement automated process optimization",
                "Achieve 20% improvement in generation efficiency"
            ]
        
        else:
            content = base_description
            success_criteria = [
                "Achieve measurable improvement in target area",
                "Implement systematic approach",
                "Validate improvement through metrics"
            ]
        
        # Prerequisites
        prerequisites = []
        if opportunity["complexity"] in [ObjectiveComplexity.COMPLEX, ObjectiveComplexity.STRATEGIC]:
            prerequisites.append("Complete capability assessment")
        if opportunity["type"] == ObjectiveType.SELF_OPTIMIZATION:
            prerequisites.append("Gather sufficient historical data")
        
        # Estimate effort
        effort_mapping = {
            ObjectiveComplexity.SIMPLE: 2.0,
            ObjectiveComplexity.MODERATE: 8.0,
            ObjectiveComplexity.COMPLEX: 24.0,
            ObjectiveComplexity.STRATEGIC: 72.0,
            ObjectiveComplexity.TRANSFORMATIONAL: 168.0
        }
        estimated_effort = effort_mapping.get(opportunity["complexity"], 8.0)
        
        # Context factors
        context_factors = {
            "capability_assessment_id": assessment.assessment_id,
            "opportunity_type": opportunity["type"].value,
            "system_state": context or {},
            "generation_method": "automated_meta_analysis"
        }
        
        meta_objective = GeneratedObjective(
            objective_id=objective_id,
            content=content,
            objective_type=opportunity["type"],
            complexity=opportunity["complexity"],
            scope=opportunity["scope"],
            expected_impact=opportunity["priority"],
            generation_confidence=assessment.confidence_in_assessment,
            prerequisites=prerequisites,
            success_criteria=success_criteria,
            estimated_effort=estimated_effort,
            meta_reasoning=meta_reasoning,
            context_factors=context_factors
        )
        
        return meta_objective
    
    def analyze_objective_patterns(self) -> List[MetaObjectivePattern]:
        """Analisa padrões nos objetivos gerados"""
        if len(self.generated_objectives) < self.pattern_detection_threshold:
            return []
        
        patterns = []
        objectives = list(self.generated_objectives)
        
        # Pattern 1: Type frequency analysis
        type_counts = defaultdict(int)
        for obj in objectives:
            type_counts[obj.objective_type] += 1
        
        for obj_type, count in type_counts.items():
            if count >= self.pattern_detection_threshold:
                # Analyze success rate for this type
                type_objectives = [obj for obj in objectives if obj.objective_type == obj_type]
                completed_type_objectives = [obj for obj in type_objectives if obj in self.completed_objectives]
                success_rate = len(completed_type_objectives) / len(type_objectives) if type_objectives else 0
                
                avg_impact = statistics.mean([obj.expected_impact for obj in type_objectives])
                
                pattern = MetaObjectivePattern(
                    pattern_id=f"type_frequency_{obj_type.value}",
                    pattern_type="objective_type_frequency",
                    description=f"Frequent generation of {obj_type.value} objectives",
                    frequency=count,
                    success_rate=success_rate,
                    average_impact=avg_impact,
                    conditions=[f"objective_type == {obj_type.value}"],
                    recommended_usage=f"Continue using for {obj_type.value} when success_rate > 0.6"
                )
                patterns.append(pattern)
        
        # Pattern 2: Complexity vs Success correlation
        complexity_success = defaultdict(list)
        for obj in objectives:
            if obj in self.completed_objectives:
                complexity_success[obj.complexity].append(1)
            else:
                complexity_success[obj.complexity].append(0)
        
        for complexity, results in complexity_success.items():
            if len(results) >= 3:
                success_rate = statistics.mean(results)
                pattern = MetaObjectivePattern(
                    pattern_id=f"complexity_success_{complexity.value}",
                    pattern_type="complexity_success_correlation",
                    description=f"{complexity.value} objectives have {success_rate:.1%} success rate",
                    frequency=len(results),
                    success_rate=success_rate,
                    average_impact=0.5,  # Placeholder
                    conditions=[f"complexity == {complexity.value}"],
                    recommended_usage=f"Use {complexity.value} complexity when success_rate > 0.5"
                )
                patterns.append(pattern)
        
        # Store detected patterns
        for pattern in patterns:
            self.detected_patterns[pattern.pattern_id] = pattern
        
        self.meta_objective_analytics["patterns_identified"] = len(self.detected_patterns)
        
        return patterns
    
    def get_meta_objective_insights(self) -> Dict[str, Any]:
        """Retorna insights sobre geração de meta-objetivos"""
        insights = {
            "total_objectives_generated": len(self.generated_objectives),
            "active_objectives": len(self.active_objectives),
            "completed_objectives": len(self.completed_objectives),
            "completion_rate": len(self.completed_objectives) / max(1, len(self.generated_objectives)),
            "average_quality": statistics.mean([obj.generation_confidence for obj in self.generated_objectives]) if self.generated_objectives else 0,
            "patterns_identified": len(self.detected_patterns),
            "analytics": self.meta_objective_analytics,
            "capability_trend": "improving" if len(self.capability_assessments) > 1 else "unknown"
        }
        
        # Recent performance trend
        if len(self.generated_objectives) >= 10:
            recent_quality = statistics.mean([obj.generation_confidence for obj in list(self.generated_objectives)[-5:]])
            older_quality = statistics.mean([obj.generation_confidence for obj in list(self.generated_objectives)[-10:-5]])
            insights["quality_trend"] = "improving" if recent_quality > older_quality else "stable" if abs(recent_quality - older_quality) < 0.05 else "declining"
        
        # Recommendations
        recommendations = []
        if insights["completion_rate"] < 0.6:
            recommendations.append("Focus on generating more achievable objectives")
        if insights["average_quality"] < 0.7:
            recommendations.append("Improve objective quality assessment")
        if len(self.detected_patterns) < 3:
            recommendations.append("Generate more diverse objectives to identify patterns")
        
        insights["recommendations"] = recommendations
        
        return insights
    
    def _start_background_processing(self):
        """Inicia processamento em background"""
        self.generation_thread = threading.Thread(target=self._background_generation_loop, daemon=True)
        self.analysis_thread = threading.Thread(target=self._background_analysis_loop, daemon=True)
        
        self.generation_thread.start()
        self.analysis_thread.start()
        
        self.logger.info("🔄 Background meta-objective processing started")
    
    def _background_generation_loop(self):
        """Loop de geração automática de meta-objetivos"""
        while not self.should_stop.wait(self.generation_interval):
            try:
                # Only generate if we don't have too many active objectives
                if len(self.active_objectives) < self.max_concurrent_objectives:
                    context = {
                        "system_stress": len(self.active_objectives) / self.max_concurrent_objectives,
                        "recent_failure_rate": self._calculate_recent_failure_rate(),
                        "creativity_level": self._assess_creativity_level()
                    }
                    
                    meta_objective = self.generate_meta_objective(context)
                    self.logger.info(f"🎯 Auto-generated meta-objective: {meta_objective.objective_type.value}")
                
            except Exception as e:
                self.logger.error(f"Error in background generation: {e}")
    
    def _background_analysis_loop(self):
        """Loop de análise automática de padrões"""
        while not self.should_stop.wait(self.capability_analysis_interval):
            try:
                # Analyze patterns
                patterns = self.analyze_objective_patterns()
                if patterns:
                    self.logger.info(f"📊 Identified {len(patterns)} new objective patterns")
                
                # Update analytics
                self._update_meta_analytics()
                
            except Exception as e:
                self.logger.error(f"Error in background analysis: {e}")
    
    def _calculate_recent_failure_rate(self) -> float:
        """Calcula taxa de falha recente"""
        recent_objectives = list(self.generated_objectives)[-10:]
        if not recent_objectives:
            return 0.0
        
        failed_count = len([obj for obj in recent_objectives if obj not in self.completed_objectives])
        return failed_count / len(recent_objectives)
    
    def _assess_creativity_level(self) -> float:
        """Avalia nível de criatividade recente"""
        recent_objectives = list(self.generated_objectives)[-10:]
        if not recent_objectives:
            return 0.5
        
        # Check diversity of types
        types_used = set(obj.objective_type for obj in recent_objectives)
        type_diversity = len(types_used) / len(ObjectiveType)
        
        # Check complexity distribution
        complexities = [obj.complexity for obj in recent_objectives]
        complexity_variance = len(set(complexities)) / len(ObjectiveComplexity)
        
        return (type_diversity + complexity_variance) / 2
    
    def _update_generation_analytics(self, objective: GeneratedObjective):
        """Atualiza analytics de geração"""
        self.meta_objective_analytics["generation_efficiency"] = len(self.generated_objectives) / max(1, time.time() - self._start_time) * 3600  # objectives per hour
        
        # Update average quality
        if self.generated_objectives:
            self.meta_objective_analytics["average_objective_quality"] = statistics.mean([obj.generation_confidence for obj in self.generated_objectives])
    
    def _update_meta_analytics(self):
        """Atualiza analytics meta"""
        self.meta_objective_analytics["successful_objectives"] = len(self.completed_objectives)
        
        if len(self.capability_assessments) > 1:
            recent_capability = self.capability_assessments[-1].calculate_overall_capability()
            previous_capability = self.capability_assessments[-2].calculate_overall_capability()
            
            if recent_capability > previous_capability + self.improvement_threshold:
                self.meta_objective_analytics["capability_improvements_detected"] += 1
    
    def _load_meta_objective_data(self):
        """Carrega dados persistidos"""
        data_file = self.data_dir / "meta_objective_data.json"
        
        try:
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load objectives
                if "generated_objectives" in data:
                    for obj_data in data["generated_objectives"]:
                        try:
                            objective = GeneratedObjective(
                                objective_id=obj_data["objective_id"],
                                content=obj_data["content"],
                                objective_type=ObjectiveType(obj_data["objective_type"]),
                                complexity=ObjectiveComplexity(obj_data["complexity"]),
                                scope=ObjectiveScope(obj_data["scope"]),
                                expected_impact=obj_data["expected_impact"],
                                generation_confidence=obj_data["generation_confidence"],
                                prerequisites=obj_data.get("prerequisites", []),
                                success_criteria=obj_data.get("success_criteria", []),
                                estimated_effort=obj_data.get("estimated_effort", 0.0),
                                meta_reasoning=obj_data.get("meta_reasoning", ""),
                                context_factors=obj_data.get("context_factors", {}),
                                timestamp=datetime.fromisoformat(obj_data["timestamp"])
                            )
                            self.generated_objectives.append(objective)
                        except Exception as e:
                            self.logger.warning(f"Failed to load objective: {e}")
                
                # Load analytics
                if "meta_objective_analytics" in data:
                    self.meta_objective_analytics.update(data["meta_objective_analytics"])
                
                self.logger.info(f"📂 Loaded {len(self.generated_objectives)} meta-objectives from disk")
                
        except Exception as e:
            self.logger.warning(f"Failed to load meta-objective data: {e}")
        
        # Set start time for analytics
        self._start_time = time.time()
    
    def _save_meta_objective_data(self):
        """Salva dados persistidos"""
        data_file = self.data_dir / "meta_objective_data.json"
        
        try:
            data = {
                "generated_objectives": [obj.to_dict() for obj in self.generated_objectives],
                "meta_objective_analytics": self.meta_objective_analytics,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save meta-objective data: {e}")
    
    def get_meta_objective_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de meta-objetivos"""
        return {
            "enabled": self.enabled,
            "total_objectives_generated": len(self.generated_objectives),
            "active_objectives": len(self.active_objectives),
            "completed_objectives": len(self.completed_objectives),
            "patterns_identified": len(self.detected_patterns),
            "analytics": self.meta_objective_analytics,
            "generation_active": self.generation_thread.is_alive() if self.generation_thread else False,
            "analysis_active": self.analysis_thread.is_alive() if self.analysis_thread else False
        }
    
    def shutdown(self):
        """Encerra sistema de meta-objetivos"""
        self.logger.info("🛑 Shutting down Meta-Objective Generator...")
        
        self.should_stop.set()
        
        if self.generation_thread and self.generation_thread.is_alive():
            self.generation_thread.join(timeout=5)
        
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5)
        
        # Final save
        self._save_meta_objective_data()
        
        self.logger.info("✅ Meta-Objective Generator shutdown complete")

# Singleton instance
_meta_objective_generator = None

def get_meta_objective_generator(config: Dict[str, Any], logger: logging.Logger) -> MetaObjectiveGenerator:
    """Get singleton instance of MetaObjectiveGenerator"""
    global _meta_objective_generator
    if _meta_objective_generator is None:
        _meta_objective_generator = MetaObjectiveGenerator(config, logger)
    return _meta_objective_generator