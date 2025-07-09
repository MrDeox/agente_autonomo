"""
🕐 TEMPORAL INTELLIGENCE SYSTEM
Sistema de consciência temporal que pensa no passado, presente e futuro - a 7ª meta-funcionalidade!

Este sistema implementa consciência temporal através de:
- Historical Pattern Analysis: Análise profunda de padrões históricos
- Present Context Awareness: Consciência total do momento atual
- Future Prediction Engine: Predição de necessidades e oportunidades futuras
- Temporal Decision Making: Decisões considerando linha temporal completa
- Proactive Planning: Planejamento proativo baseado em tendências
- Temporal Memory Management: Gerenciamento inteligente de memória temporal

É literalmente o sistema que "viaja no tempo" cognitivamente para otimizar o presente!
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
from abc import ABC, abstractmethod

class TemporalPerspective(Enum):
    """Perspectivas temporais do sistema"""
    PAST = "past"               # Análise histórica
    PRESENT = "present"         # Estado atual
    FUTURE = "future"           # Predição e planejamento
    CYCLICAL = "cyclical"       # Padrões cíclicos
    TRENDING = "trending"       # Tendências emergentes

class TemporalScope(Enum):
    """Escopo temporal de análise"""
    IMMEDIATE = "immediate"     # Últimos minutos/horas
    SHORT_TERM = "short_term"   # Últimos dias
    MEDIUM_TERM = "medium_term" # Últimas semanas
    LONG_TERM = "long_term"     # Últimos meses
    DEEP_HISTORY = "deep_history" # Todo o histórico

class PredictionConfidence(Enum):
    """Níveis de confiança nas predições"""
    VERY_LOW = "very_low"       # 0-20%
    LOW = "low"                 # 20-40%
    MODERATE = "moderate"       # 40-60%
    HIGH = "high"               # 60-80%
    VERY_HIGH = "very_high"     # 80-100%

@dataclass
class TemporalPattern:
    """Padrão identificado na linha temporal"""
    pattern_id: str
    pattern_type: str
    description: str
    first_occurrence: datetime
    last_occurrence: datetime
    frequency: int
    confidence: float
    cyclical_period: Optional[timedelta] = None
    trend_direction: Optional[str] = None  # "increasing", "decreasing", "stable"
    impact_score: float = 0.0
    related_events: List[str] = field(default_factory=list)
    
    def calculate_pattern_strength(self) -> float:
        """Calcula força do padrão baseado em frequência e consistência"""
        time_span = (self.last_occurrence - self.first_occurrence).total_seconds()
        if time_span <= 0:
            return 0.0
        
        # Frequência normalizada
        frequency_score = min(1.0, self.frequency / 10.0)
        
        # Consistência temporal
        if self.cyclical_period:
            expected_occurrences = time_span / self.cyclical_period.total_seconds()
            consistency_score = min(1.0, self.frequency / max(1, expected_occurrences))
        else:
            consistency_score = 0.5
        
        # Combinação ponderada
        pattern_strength = (
            self.confidence * 0.4 +
            frequency_score * 0.3 +
            consistency_score * 0.2 +
            self.impact_score * 0.1
        )
        
        return min(1.0, max(0.0, pattern_strength))

@dataclass
class FuturePrediction:
    """Predição sobre eventos/necessidades futuras"""
    prediction_id: str
    predicted_event: str
    predicted_time: datetime
    confidence: PredictionConfidence
    confidence_score: float
    reasoning: str
    impact_assessment: str
    preparation_suggestions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    based_on_patterns: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "prediction_id": self.prediction_id,
            "predicted_event": self.predicted_event,
            "predicted_time": self.predicted_time.isoformat(),
            "confidence": self.confidence.value,
            "confidence_score": self.confidence_score,
            "reasoning": self.reasoning,
            "impact_assessment": self.impact_assessment,
            "preparation_suggestions": self.preparation_suggestions,
            "dependencies": self.dependencies,
            "based_on_patterns": self.based_on_patterns,
            "created_at": self.created_at.isoformat()
        }

@dataclass
class TemporalContext:
    """Contexto temporal completo para tomada de decisões"""
    timestamp: datetime
    relevant_past_events: List[Dict[str, Any]]
    current_state: Dict[str, Any]
    active_trends: List[TemporalPattern]
    future_predictions: List[FuturePrediction]
    temporal_recommendations: List[str]
    confidence_factors: Dict[str, float]

class TemporalIntelligence:
    """
    🕐 Temporal Intelligence System - Consciência temporal completa
    
    Este sistema implementa verdadeira consciência temporal que:
    1. Analisa padrões históricos profundos
    2. Compreende o contexto presente completamente
    3. Prediz necessidades e oportunidades futuras
    4. Toma decisões considerando toda a linha temporal
    5. Planeja proativamente baseado em tendências
    6. Gerencia memória temporal inteligentemente
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("TemporalIntelligence")
        
        # Configuration - com valores seguros por padrão
        temporal_config = config.get("temporal_intelligence", {})
        self.analysis_interval = temporal_config.get("analysis_interval", 1800)  # 30 minutes
        self.pattern_detection_threshold = temporal_config.get("pattern_detection_threshold", 3)
        self.prediction_horizon_days = temporal_config.get("prediction_horizon_days", 7)
        self.max_historical_events = temporal_config.get("max_historical_events", 10000)
        self.pattern_confidence_threshold = temporal_config.get("pattern_confidence_threshold", 0.6)
        self.enabled = temporal_config.get("enabled", True)
        
        # Data storage
        self.data_dir = Path("data/intelligence/temporal")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Temporal state
        self.historical_events: deque = deque(maxlen=self.max_historical_events)
        self.detected_patterns: Dict[str, TemporalPattern] = {}
        self.active_predictions: List[FuturePrediction] = []
        self.temporal_memory: Dict[TemporalScope, List[Dict[str, Any]]] = {
            scope: [] for scope in TemporalScope
        }
        
        # Analytics
        self.temporal_analytics = {
            "total_events_analyzed": 0,
            "patterns_discovered": 0,
            "predictions_made": 0,
            "successful_predictions": 0,
            "average_prediction_accuracy": 0.0,
            "temporal_coverage_score": 0.0,
            "proactive_actions_taken": 0,
            "historical_insights_generated": 0
        }
        
        # Threading
        self.should_stop = threading.Event()
        self.analysis_thread = None
        
        # Load existing data
        self._load_temporal_data()
        
        # Initialize
        if self.enabled:
            self._start_temporal_analysis()
            self.logger.info("🕐 Temporal Intelligence initialized!")
            self.logger.info(f"📊 Analysis interval: {self.analysis_interval}s")
            self.logger.info(f"📈 {len(self.historical_events)} events in memory")
        else:
            self.logger.info("⚠️ Temporal Intelligence disabled in configuration")
    
    def analyze_temporal_patterns(self, scope: TemporalScope = TemporalScope.MEDIUM_TERM) -> List[TemporalPattern]:
        """Analisa padrões temporais no escopo especificado"""
        if not self.enabled:
            return []
        
        self.logger.info(f"🔍 Analyzing temporal patterns for {scope.value}...")
        
        # Filtrar eventos pelo escopo temporal
        events = self._filter_events_by_scope(scope)
        
        if len(events) < self.pattern_detection_threshold:
            self.logger.info(f"📊 Insufficient events ({len(events)}) for pattern detection")
            return []
        
        patterns = []
        
        try:
            # 1. Detectar padrões cíclicos
            cyclical_patterns = self._detect_cyclical_patterns(events)
            patterns.extend(cyclical_patterns)
            
            # 2. Detectar tendências
            trend_patterns = self._detect_trend_patterns(events)
            patterns.extend(trend_patterns)
            
            # 3. Detectar padrões de correlação temporal
            correlation_patterns = self._detect_correlation_patterns(events)
            patterns.extend(correlation_patterns)
            
            # 4. Validar e filtrar padrões
            validated_patterns = self._validate_patterns(patterns)
            
            # Atualizar padrões detectados
            for pattern in validated_patterns:
                self.detected_patterns[pattern.pattern_id] = pattern
            
            self.temporal_analytics["patterns_discovered"] = len(self.detected_patterns)
            
            self.logger.info(f"✅ Discovered {len(validated_patterns)} temporal patterns")
            
            return validated_patterns
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing temporal patterns: {e}")
            return []
    
    def predict_future_needs(self, horizon_hours: int = 24) -> List[FuturePrediction]:
        """Prediz necessidades futuras baseado em padrões temporais"""
        if not self.enabled:
            return []
        
        self.logger.info(f"🔮 Predicting future needs for next {horizon_hours} hours...")
        
        predictions = []
        current_time = datetime.now()
        future_time = current_time + timedelta(hours=horizon_hours)
        
        try:
            # 1. Predições baseadas em padrões cíclicos
            cyclical_predictions = self._predict_from_cyclical_patterns(current_time, future_time)
            predictions.extend(cyclical_predictions)
            
            # 2. Predições baseadas em tendências
            trend_predictions = self._predict_from_trends(current_time, future_time)
            predictions.extend(trend_predictions)
            
            # 3. Predições baseadas em contexto atual
            contextual_predictions = self._predict_from_current_context(current_time, future_time)
            predictions.extend(contextual_predictions)
            
            # 4. Validar e priorizar predições
            validated_predictions = self._validate_predictions(predictions)
            
            # Atualizar predições ativas
            self.active_predictions.extend(validated_predictions)
            
            # Limpar predições antigas
            self._cleanup_old_predictions()
            
            self.temporal_analytics["predictions_made"] += len(validated_predictions)
            
            self.logger.info(f"🎯 Generated {len(validated_predictions)} future predictions")
            
            return validated_predictions
            
        except Exception as e:
            self.logger.error(f"❌ Error predicting future needs: {e}")
            return []
    
    def get_temporal_context(self) -> TemporalContext:
        """Obtém contexto temporal completo para tomada de decisões"""
        current_time = datetime.now()
        
        # Eventos passados relevantes
        relevant_past = self._get_relevant_past_events(current_time)
        
        # Estado atual
        current_state = self._assess_current_state()
        
        # Tendências ativas
        active_trends = [
            pattern for pattern in self.detected_patterns.values()
            if pattern.trend_direction and pattern.confidence > self.pattern_confidence_threshold
        ]
        
        # Predições futuras
        future_predictions = [
            pred for pred in self.active_predictions
            if pred.predicted_time > current_time
        ]
        
        # Recomendações temporais
        recommendations = self._generate_temporal_recommendations(
            relevant_past, current_state, active_trends, future_predictions
        )
        
        # Fatores de confiança
        confidence_factors = self._calculate_confidence_factors()
        
        return TemporalContext(
            timestamp=current_time,
            relevant_past_events=relevant_past,
            current_state=current_state,
            active_trends=active_trends,
            future_predictions=future_predictions,
            temporal_recommendations=recommendations,
            confidence_factors=confidence_factors
        )
    
    def record_temporal_event(self, event_type: str, event_data: Dict[str, Any], 
                             timestamp: Optional[datetime] = None) -> bool:
        """Registra evento temporal para análise"""
        if not self.enabled:
            return False
        
        try:
            event_timestamp = timestamp or datetime.now()
            
            event = {
                "event_id": f"event_{int(time.time())}_{hashlib.md5(event_type.encode()).hexdigest()[:8]}",
                "event_type": event_type,
                "timestamp": event_timestamp,
                "data": event_data,
                "recorded_at": datetime.now()
            }
            
            self.historical_events.append(event)
            self.temporal_analytics["total_events_analyzed"] += 1
            
            # Atualizar memória temporal por escopo
            self._update_temporal_memory(event)
            
            # Salvar dados imediatamente para persistência
            self._save_temporal_data()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error recording temporal event: {e}")
            return False
    
    def record_real_system_event(self, event_type: str, result: Any, metrics: Dict[str, Any] = None) -> bool:
        """Registra eventos reais do sistema em execução"""
        try:
            event_data = {
                "result": str(result)[:200] if result else "no_result",  # Limitar tamanho
                "success": getattr(result, 'success', True) if hasattr(result, 'success') else True,
                "execution_time": metrics.get("execution_time", 0) if metrics else 0,
                "system_metrics": {
                    "timestamp": datetime.now().isoformat(),
                    "event_source": "real_system"
                }
            }
            
            if metrics:
                event_data["performance_metrics"] = metrics
                
            return self.record_temporal_event(event_type, event_data)
            
        except Exception as e:
            self.logger.error(f"❌ Error recording real system event: {e}")
            return False
    
    def _filter_events_by_scope(self, scope: TemporalScope) -> List[Dict[str, Any]]:
        """Filtra eventos pelo escopo temporal"""
        current_time = datetime.now()
        
        scope_filters = {
            TemporalScope.IMMEDIATE: timedelta(hours=6),
            TemporalScope.SHORT_TERM: timedelta(days=3),
            TemporalScope.MEDIUM_TERM: timedelta(weeks=2),
            TemporalScope.LONG_TERM: timedelta(days=90),
            TemporalScope.DEEP_HISTORY: None  # Todo o histórico
        }
        
        if scope == TemporalScope.DEEP_HISTORY:
            return list(self.historical_events)
        
        cutoff_time = current_time - scope_filters[scope]
        
        return [
            event for event in self.historical_events
            if event["timestamp"] >= cutoff_time
        ]
    
    def _detect_cyclical_patterns(self, events: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """Detecta padrões cíclicos nos eventos"""
        patterns = []
        
        # Agrupar eventos por tipo
        events_by_type = defaultdict(list)
        for event in events:
            events_by_type[event["event_type"]].append(event)
        
        for event_type, type_events in events_by_type.items():
            if len(type_events) < 3:  # Mínimo para detectar ciclo
                continue
            
            # Analisar intervalos entre eventos
            intervals = []
            for i in range(1, len(type_events)):
                interval = type_events[i]["timestamp"] - type_events[i-1]["timestamp"]
                intervals.append(interval.total_seconds())
            
            if len(intervals) < 2:
                continue
            
            # Detectar periodicidade
            avg_interval = statistics.mean(intervals)
            interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
            
            # Considerar padrão cíclico se variância é baixa
            if interval_variance < (avg_interval * 0.3):  # 30% de tolerância
                pattern_id = f"cyclical_{event_type}_{int(avg_interval)}"
                
                pattern = TemporalPattern(
                    pattern_id=pattern_id,
                    pattern_type="cyclical",
                    description=f"Cyclical pattern in {event_type} every {avg_interval/3600:.1f} hours",
                    first_occurrence=type_events[0]["timestamp"],
                    last_occurrence=type_events[-1]["timestamp"],
                    frequency=len(type_events),
                    confidence=max(0.1, min(0.9, 1.0 - (interval_variance / avg_interval))),
                    cyclical_period=timedelta(seconds=avg_interval),
                    impact_score=min(1.0, len(type_events) / 10.0)
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _detect_trend_patterns(self, events: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """Detecta padrões de tendência nos eventos"""
        patterns = []
        
        # Analisar frequência de eventos ao longo do tempo
        time_buckets = defaultdict(int)
        earliest_time = min(event["timestamp"] for event in events)
        
        # Dividir em buckets de 1 hora
        for event in events:
            hours_since_start = int((event["timestamp"] - earliest_time).total_seconds() / 3600)
            time_buckets[hours_since_start] += 1
        
        if len(time_buckets) < 3:
            return patterns
        
        # Calcular tendência
        hours = sorted(time_buckets.keys())
        frequencies = [time_buckets[h] for h in hours]
        
        # Regressão linear simples
        n = len(hours)
        sum_x = sum(hours)
        sum_y = sum(frequencies)
        sum_xy = sum(h * f for h, f in zip(hours, frequencies))
        sum_x2 = sum(h * h for h in hours)
        
        if n * sum_x2 - sum_x * sum_x != 0:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determinar direção da tendência
            if abs(slope) > 0.1:  # Threshold para considerar tendência significativa
                trend_direction = "increasing" if slope > 0 else "decreasing"
                confidence = min(0.9, abs(slope) / 2.0)
                
                pattern_id = f"trend_{trend_direction}_{int(time.time())}"
                
                pattern = TemporalPattern(
                    pattern_id=pattern_id,
                    pattern_type="trend",
                    description=f"Event frequency is {trend_direction}",
                    first_occurrence=earliest_time,
                    last_occurrence=max(event["timestamp"] for event in events),
                    frequency=len(events),
                    confidence=confidence,
                    trend_direction=trend_direction,
                    impact_score=min(1.0, abs(slope))
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _detect_correlation_patterns(self, events: List[Dict[str, Any]]) -> List[TemporalPattern]:
        """Detecta padrões de correlação temporal entre tipos de eventos"""
        patterns = []
        
        # Implementação básica - pode ser expandida
        event_types = set(event["event_type"] for event in events)
        
        for event_type in event_types:
            type_events = [e for e in events if e["event_type"] == event_type]
            
            if len(type_events) >= self.pattern_detection_threshold:
                pattern_id = f"correlation_{event_type}_{len(type_events)}"
                
                pattern = TemporalPattern(
                    pattern_id=pattern_id,
                    pattern_type="correlation",
                    description=f"Correlation pattern for {event_type}",
                    first_occurrence=type_events[0]["timestamp"],
                    last_occurrence=type_events[-1]["timestamp"],
                    frequency=len(type_events),
                    confidence=0.5,  # Base confidence
                    impact_score=min(1.0, len(type_events) / 20.0)
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _validate_patterns(self, patterns: List[TemporalPattern]) -> List[TemporalPattern]:
        """Valida e filtra padrões baseado em critérios de qualidade"""
        validated = []
        
        for pattern in patterns:
            # Critérios de validação
            if (pattern.confidence >= self.pattern_confidence_threshold and
                pattern.frequency >= self.pattern_detection_threshold and
                pattern.calculate_pattern_strength() > 0.3):
                
                validated.append(pattern)
        
        return validated
    
    def _predict_from_cyclical_patterns(self, start_time: datetime, end_time: datetime) -> List[FuturePrediction]:
        """Gera predições baseadas em padrões cíclicos"""
        predictions = []
        
        for pattern in self.detected_patterns.values():
            if pattern.pattern_type == "cyclical" and pattern.cyclical_period:
                # Calcular próxima ocorrência esperada
                time_since_last = start_time - pattern.last_occurrence
                period_seconds = pattern.cyclical_period.total_seconds()
                
                # Se já passou do período, prever próxima ocorrência
                if time_since_last.total_seconds() > period_seconds * 0.8:
                    next_occurrence = pattern.last_occurrence + pattern.cyclical_period
                    
                    if start_time <= next_occurrence <= end_time:
                        prediction_id = f"cyclical_pred_{pattern.pattern_id}_{int(time.time())}"
                        
                        prediction = FuturePrediction(
                            prediction_id=prediction_id,
                            predicted_event=f"Next occurrence of {pattern.description}",
                            predicted_time=next_occurrence,
                            confidence=PredictionConfidence.HIGH if pattern.confidence > 0.8 else PredictionConfidence.MODERATE,
                            confidence_score=pattern.confidence,
                            reasoning=f"Based on cyclical pattern with {pattern.frequency} occurrences",
                            impact_assessment=f"Expected impact: {pattern.impact_score:.2f}",
                            based_on_patterns=[pattern.pattern_id]
                        )
                        
                        predictions.append(prediction)
        
        return predictions
    
    def _predict_from_trends(self, start_time: datetime, end_time: datetime) -> List[FuturePrediction]:
        """Gera predições baseadas em tendências"""
        predictions = []
        
        for pattern in self.detected_patterns.values():
            if pattern.pattern_type == "trend" and pattern.trend_direction:
                prediction_id = f"trend_pred_{pattern.pattern_id}_{int(time.time())}"
                
                # Prever continuação da tendência
                predicted_time = start_time + timedelta(hours=12)  # Meio do horizonte
                
                if predicted_time <= end_time:
                    prediction = FuturePrediction(
                        prediction_id=prediction_id,
                        predicted_event=f"Trend continuation: {pattern.trend_direction} pattern",
                        predicted_time=predicted_time,
                        confidence=PredictionConfidence.MODERATE if pattern.confidence > 0.6 else PredictionConfidence.LOW,
                        confidence_score=pattern.confidence,
                        reasoning=f"Based on {pattern.trend_direction} trend pattern",
                        impact_assessment=f"Trend impact: {pattern.impact_score:.2f}",
                        based_on_patterns=[pattern.pattern_id]
                    )
                    
                    predictions.append(prediction)
        
        return predictions
    
    def _predict_from_current_context(self, start_time: datetime, end_time: datetime) -> List[FuturePrediction]:
        """Gera predições baseadas no contexto atual"""
        predictions = []
        
        # Análise simples do contexto atual
        recent_events = [
            event for event in self.historical_events
            if (start_time - event["timestamp"]).total_seconds() < 3600  # Última hora
        ]
        
        if len(recent_events) > 5:  # Alta atividade recente
            prediction_id = f"context_pred_{int(time.time())}"
            predicted_time = start_time + timedelta(hours=2)
            
            if predicted_time <= end_time:
                prediction = FuturePrediction(
                    prediction_id=prediction_id,
                    predicted_event="Continued high activity expected",
                    predicted_time=predicted_time,
                    confidence=PredictionConfidence.MODERATE,
                    confidence_score=0.6,
                    reasoning=f"High recent activity: {len(recent_events)} events in last hour",
                    impact_assessment="Medium impact expected",
                    preparation_suggestions=[
                        "Monitor system resources",
                        "Prepare for increased load"
                    ]
                )
                
                predictions.append(prediction)
        
        return predictions
    
    def _validate_predictions(self, predictions: List[FuturePrediction]) -> List[FuturePrediction]:
        """Valida e filtra predições"""
        validated = []
        
        for prediction in predictions:
            # Critérios básicos de validação
            if (prediction.confidence_score > 0.3 and
                prediction.predicted_time > datetime.now()):
                
                validated.append(prediction)
        
        return validated
    
    def _cleanup_old_predictions(self):
        """Remove predições antigas e desatualizadas"""
        current_time = datetime.now()
        
        # Manter apenas predições futuras ou recentes
        self.active_predictions = [
            pred for pred in self.active_predictions
            if (pred.predicted_time > current_time or 
                (current_time - pred.predicted_time).total_seconds() < 86400)  # 24 horas
        ]
    
    def _get_relevant_past_events(self, current_time: datetime, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Obtém eventos passados relevantes"""
        cutoff_time = current_time - timedelta(hours=hours_back)
        
        return [
            event for event in self.historical_events
            if event["timestamp"] >= cutoff_time
        ]
    
    def _assess_current_state(self) -> Dict[str, Any]:
        """Avalia estado atual do sistema"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_patterns": len(self.detected_patterns),
            "recent_events": len([
                e for e in self.historical_events
                if (datetime.now() - e["timestamp"]).total_seconds() < 3600
            ]),
            "prediction_confidence": statistics.mean([
                pred.confidence_score for pred in self.active_predictions
            ]) if self.active_predictions else 0.0
        }
    
    def _generate_temporal_recommendations(self, past_events: List[Dict[str, Any]], 
                                         current_state: Dict[str, Any],
                                         trends: List[TemporalPattern],
                                         predictions: List[FuturePrediction]) -> List[str]:
        """Gera recomendações baseadas no contexto temporal"""
        recommendations = []
        
        # Recomendações baseadas em tendências
        for trend in trends:
            if trend.trend_direction == "increasing":
                recommendations.append(f"Prepare for increased {trend.description}")
            elif trend.trend_direction == "decreasing":
                recommendations.append(f"Consider intervention for {trend.description}")
        
        # Recomendações baseadas em predições
        high_confidence_predictions = [
            pred for pred in predictions
            if pred.confidence in [PredictionConfidence.HIGH, PredictionConfidence.VERY_HIGH]
        ]
        
        for pred in high_confidence_predictions:
            recommendations.extend(pred.preparation_suggestions)
        
        # Recomendação geral se atividade alta
        if len(past_events) > 10:
            recommendations.append("Monitor system performance due to high recent activity")
        
        return list(set(recommendations))  # Remove duplicatas
    
    def _calculate_confidence_factors(self) -> Dict[str, float]:
        """Calcula fatores de confiança para diferentes aspectos"""
        return {
            "pattern_detection": len(self.detected_patterns) / 10.0,  # Normalizado para 10 padrões
            "prediction_accuracy": self.temporal_analytics["average_prediction_accuracy"],
            "data_coverage": min(1.0, len(self.historical_events) / 1000.0),
            "temporal_span": min(1.0, len(self.historical_events) / 100.0)
        }
    
    def _update_temporal_memory(self, event: Dict[str, Any]):
        """Atualiza memória temporal por escopo"""
        current_time = datetime.now()
        event_time = event["timestamp"]
        
        # Adicionar a todos os escopos relevantes
        for scope in TemporalScope:
            scope_limit = {
                TemporalScope.IMMEDIATE: timedelta(hours=6),
                TemporalScope.SHORT_TERM: timedelta(days=3),
                TemporalScope.MEDIUM_TERM: timedelta(weeks=2),
                TemporalScope.LONG_TERM: timedelta(days=90),
                TemporalScope.DEEP_HISTORY: None
            }
            
            if scope_limit[scope] is None or (current_time - event_time) <= scope_limit[scope]:
                self.temporal_memory[scope].append(event)
                
                # Limitar tamanho da memória
                if len(self.temporal_memory[scope]) > 1000:
                    self.temporal_memory[scope] = self.temporal_memory[scope][-800:]
    
    def _start_temporal_analysis(self):
        """Inicia análise temporal em background"""
        self.analysis_thread = threading.Thread(target=self._temporal_analysis_loop, daemon=True)
        self.analysis_thread.start()
        self.logger.info("🔄 Temporal analysis started")
    
    def _temporal_analysis_loop(self):
        """Loop principal de análise temporal"""
        while not self.should_stop.wait(self.analysis_interval):
            try:
                # Análise de padrões
                patterns = self.analyze_temporal_patterns()
                
                # Predições futuras
                predictions = self.predict_future_needs()
                
                # Atualizar analytics
                self._update_temporal_analytics()
                
                if patterns or predictions:
                    self.logger.info(f"📊 Temporal analysis: {len(patterns)} patterns, {len(predictions)} predictions")
                
            except Exception as e:
                self.logger.error(f"❌ Error in temporal analysis loop: {e}")
    
    def _update_temporal_analytics(self):
        """Atualiza analytics temporais"""
        self.temporal_analytics["temporal_coverage_score"] = min(1.0, len(self.historical_events) / 1000.0)
        
        # Calcular precisão das predições (implementação básica)
        if len(self.active_predictions) > 0:
            accurate_predictions = sum(1 for pred in self.active_predictions if pred.confidence_score > 0.7)
            self.temporal_analytics["average_prediction_accuracy"] = accurate_predictions / len(self.active_predictions)
    
    def _load_temporal_data(self):
        """Carrega dados temporais persistidos"""
        data_file = self.data_dir / "temporal_data.json"
        
        try:
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Carregar eventos históricos
                if "historical_events" in data:
                    for event_data in data["historical_events"]:
                        try:
                            event_data["timestamp"] = datetime.fromisoformat(event_data["timestamp"])
                            event_data["recorded_at"] = datetime.fromisoformat(event_data["recorded_at"])
                            self.historical_events.append(event_data)
                        except Exception as e:
                            self.logger.warning(f"Failed to load event: {e}")
                
                # Carregar analytics
                if "temporal_analytics" in data:
                    self.temporal_analytics.update(data["temporal_analytics"])
                
                self.logger.info(f"📂 Loaded {len(self.historical_events)} temporal events from disk")
                
        except Exception as e:
            self.logger.warning(f"Failed to load temporal data: {e}")
    
    def _save_temporal_data(self):
        """Salva dados temporais"""
        data_file = self.data_dir / "temporal_data.json"
        
        try:
            # Preparar eventos para serialização
            events_to_save = []
            for event in list(self.historical_events)[-1000:]:  # Últimos 1000 eventos
                event_copy = event.copy()
                event_copy["timestamp"] = event_copy["timestamp"].isoformat()
                event_copy["recorded_at"] = event_copy["recorded_at"].isoformat()
                events_to_save.append(event_copy)
            
            data = {
                "historical_events": events_to_save,
                "temporal_analytics": self.temporal_analytics,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save temporal data: {e}")
    
    def get_temporal_status(self) -> Dict[str, Any]:
        """Retorna status do sistema temporal"""
        return {
            "enabled": self.enabled,
            "total_historical_events": len(self.historical_events),
            "detected_patterns": len(self.detected_patterns),
            "active_predictions": len(self.active_predictions),
            "analytics": self.temporal_analytics,
            "analysis_active": self.analysis_thread.is_alive() if self.analysis_thread else False
        }
    
    def shutdown(self):
        """Encerra sistema temporal"""
        self.logger.info("🛑 Shutting down Temporal Intelligence...")
        
        self.should_stop.set()
        
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5)
        
        # Salvar dados
        self._save_temporal_data()
        
        self.logger.info("✅ Temporal Intelligence shutdown complete")

# Singleton instance
_temporal_intelligence = None

def get_temporal_intelligence(config: Dict[str, Any], logger: logging.Logger) -> TemporalIntelligence:
    """Get singleton instance of TemporalIntelligence"""
    global _temporal_intelligence
    if _temporal_intelligence is None:
        _temporal_intelligence = TemporalIntelligence(config, logger)
    return _temporal_intelligence