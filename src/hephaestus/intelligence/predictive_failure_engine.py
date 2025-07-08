"""
🔮 PREDICTIVE FAILURE ENGINE 🔮

Sistema de meta-inteligência que:
1. Analisa padrões históricos de falhas
2. Prediz probabilidade de falha ANTES da execução
3. Modifica objetivos preventivamente para evitar falhas
4. Aprende continuamente com novos dados

This is where we prevent failures before they happen!
"""

import re
import json
import logging
import hashlib
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import csv

from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response


@dataclass
class FailurePattern:
    """Representa um padrão de falha identificado"""
    pattern_id: str
    pattern_type: str  # "keyword", "complexity", "async", "validation"
    trigger_conditions: List[str]
    failure_probability: float
    historical_occurrences: int
    avg_failure_time: float
    common_error_types: List[str]
    preventive_modifications: List[str]
    confidence_score: float
    last_seen: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "trigger_conditions": self.trigger_conditions,
            "failure_probability": self.failure_probability,
            "historical_occurrences": self.historical_occurrences,
            "avg_failure_time": self.avg_failure_time,
            "common_error_types": self.common_error_types,
            "preventive_modifications": self.preventive_modifications,
            "confidence_score": self.confidence_score,
            "last_seen": self.last_seen.isoformat()
        }


@dataclass
class ObjectiveAnalysis:
    """Análise preditiva de um objetivo"""
    objective: str
    failure_probability: float
    risk_factors: List[str]
    predicted_failure_types: List[str]
    recommended_modifications: List[str]
    confidence_level: float
    analysis_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "objective": self.objective,
            "failure_probability": self.failure_probability,
            "risk_factors": self.risk_factors,
            "predicted_failure_types": self.predicted_failure_types,
            "recommended_modifications": self.recommended_modifications,
            "confidence_level": self.confidence_level,
            "analysis_timestamp": self.analysis_timestamp.isoformat()
        }


class PredictiveFailureEngine:
    """
    🔮 Engine de Predição de Falhas - O Oráculo do Hephaestus
    
    Este sistema analisa padrões históricos e prediz falhas antes que aconteçam,
    permitindo modificações preventivas nos objetivos.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, memory_path: str):
        self.config = config
        self.logger = logger.getChild("PredictiveFailureEngine")
        self.memory_path = memory_path
        
        # Configurações
        self.failure_threshold = config.get("predictive_failure", {}).get("failure_threshold", 0.7)
        self.confidence_threshold = config.get("predictive_failure", {}).get("confidence_threshold", 0.6)
        self.pattern_min_occurrences = config.get("predictive_failure", {}).get("min_occurrences", 3)
        
        # Storage para padrões e análises
        self.failure_patterns: Dict[str, FailurePattern] = {}
        self.analysis_cache: Dict[str, ObjectiveAnalysis] = {}
        self.prediction_history: List[Dict[str, Any]] = []
        
        # Carregar dados existentes
        self._load_failure_patterns()
        
        self.logger.info("🔮 Predictive Failure Engine initialized - The Oracle is active!")
    
    def predict_failure_probability(self, objective: str) -> ObjectiveAnalysis:
        """
        🎯 CORE FUNCTION: Prediz probabilidade de falha para um objetivo
        
        Returns:
            ObjectiveAnalysis com probabilidade de falha e recomendações
        """
        self.logger.info(f"🔮 Predicting failure probability for: {objective[:100]}...")
        
        # Cache check
        objective_hash = hashlib.md5(objective.encode()).hexdigest()
        if objective_hash in self.analysis_cache:
            cached = self.analysis_cache[objective_hash]
            if (datetime.now() - cached.analysis_timestamp).seconds < 3600:  # 1 hour cache
                self.logger.info("📋 Using cached prediction")
                return cached
        
        # Análise multi-dimensional
        risk_factors = []
        failure_probability = 0.0
        predicted_failure_types = []
        recommended_modifications = []
        
        # 1. Pattern-based analysis
        pattern_risk, pattern_factors, pattern_types = self._analyze_patterns(objective)
        risk_factors.extend(pattern_factors)
        predicted_failure_types.extend(pattern_types)
        failure_probability = max(failure_probability, pattern_risk)
        
        # 2. Complexity analysis
        complexity_risk, complexity_factors = self._analyze_complexity(objective)
        risk_factors.extend(complexity_factors)
        failure_probability = max(failure_probability, complexity_risk)
        
        # 3. Historical similarity analysis
        similarity_risk, similarity_factors = self._analyze_historical_similarity(objective)
        risk_factors.extend(similarity_factors)
        failure_probability = max(failure_probability, similarity_risk)
        
        # 4. Async/concurrency risk analysis
        async_risk, async_factors = self._analyze_async_risks(objective)
        risk_factors.extend(async_factors)
        failure_probability = max(failure_probability, async_risk)
        
        # 5. Generate preventive modifications
        if failure_probability > self.failure_threshold:
            recommended_modifications = self._generate_preventive_modifications(
                objective, risk_factors, predicted_failure_types
            )
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence(risk_factors, len(self.failure_patterns))
        
        analysis = ObjectiveAnalysis(
            objective=objective,
            failure_probability=failure_probability,
            risk_factors=list(set(risk_factors)),  # Remove duplicates
            predicted_failure_types=list(set(predicted_failure_types)),
            recommended_modifications=recommended_modifications,
            confidence_level=confidence_level,
            analysis_timestamp=datetime.now()
        )
        
        # Cache the analysis
        self.analysis_cache[objective_hash] = analysis
        
        self.logger.info(f"🎯 Prediction complete: {failure_probability:.2%} failure probability")
        return analysis
    
    def should_modify_objective(self, analysis: ObjectiveAnalysis) -> bool:
        """Determina se o objetivo deve ser modificado baseado na análise"""
        return (analysis.failure_probability > self.failure_threshold and 
                analysis.confidence_level > self.confidence_threshold)
    
    def apply_preventive_modifications(self, objective: str, analysis: ObjectiveAnalysis) -> str:
        """
        Aplica modificações preventivas ao objetivo para reduzir probabilidade de falha
        """
        if not self.should_modify_objective(analysis):
            return objective
        
        modified_objective = objective
        
        for modification in analysis.recommended_modifications:
            modified_objective = self._apply_modification(modified_objective, modification)
        
        self.logger.info(f"🛡️ Applied {len(analysis.recommended_modifications)} preventive modifications")
        return modified_objective
    
    def learn_from_execution(self, objective: str, success: bool, failure_reason: str = None, execution_time: float = 0.0):
        """
        Aprende com resultados de execução para melhorar predições futuras
        """
        prediction_record = {
            "objective": objective,
            "predicted_failure": False,
            "actual_success": success,
            "failure_reason": failure_reason,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if we had a prediction for this objective
        objective_hash = hashlib.md5(objective.encode()).hexdigest()
        if objective_hash in self.analysis_cache:
            analysis = self.analysis_cache[objective_hash]
            prediction_record["predicted_failure"] = analysis.failure_probability > self.failure_threshold
            prediction_record["predicted_probability"] = analysis.failure_probability
            prediction_record["risk_factors"] = analysis.risk_factors
        
        self.prediction_history.append(prediction_record)
        
        # Update patterns based on actual results
        if not success and failure_reason:
            self._update_failure_patterns(objective, failure_reason, execution_time)
        
        # Save updated patterns
        self._save_failure_patterns()
        
        self.logger.info(f"📚 Learned from execution: {'success' if success else 'failure'}")
    
    def _analyze_patterns(self, objective: str) -> Tuple[float, List[str], List[str]]:
        """Analisa padrões conhecidos de falha"""
        risk_factors = []
        failure_types = []
        max_risk = 0.0
        
        for pattern in self.failure_patterns.values():
            if self._objective_matches_pattern(objective, pattern):
                risk_factors.append(f"Matches failure pattern: {pattern.pattern_id}")
                failure_types.extend(pattern.common_error_types)
                max_risk = max(max_risk, pattern.failure_probability)
        
        return max_risk, risk_factors, failure_types
    
    def _analyze_complexity(self, objective: str) -> Tuple[float, List[str]]:
        """Analisa complexidade do objetivo"""
        risk_factors = []
        risk_score = 0.0
        
        # Length-based complexity
        if len(objective) > 1000:
            risk_factors.append("Very long objective (>1000 chars)")
            risk_score += 0.3
        elif len(objective) > 500:
            risk_factors.append("Long objective (>500 chars)")
            risk_score += 0.1
        
        # Keyword complexity indicators
        complex_keywords = [
            "refactor", "split", "modularize", "complex", "comprehensive",
            "multiple", "parallel", "concurrent", "async", "pipeline"
        ]
        
        keyword_count = sum(1 for keyword in complex_keywords if keyword.lower() in objective.lower())
        if keyword_count >= 3:
            risk_factors.append(f"High complexity keywords ({keyword_count})")
            risk_score += 0.2
        
        # LOC indicators
        loc_match = re.search(r'LOC[:\s]*(\d+)', objective)
        if loc_match:
            loc = int(loc_match.group(1))
            if loc > 2000:
                risk_factors.append(f"Very large file (LOC: {loc})")
                risk_score += 0.4
            elif loc > 1000:
                risk_factors.append(f"Large file (LOC: {loc})")
                risk_score += 0.2
        
        return min(risk_score, 1.0), risk_factors
    
    def _analyze_historical_similarity(self, objective: str) -> Tuple[float, List[str]]:
        """Analisa similaridade com objetivos que falharam historicamente"""
        risk_factors = []
        max_risk = 0.0
        
        # Load historical failures
        try:
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                failed_objectives = memory_data.get("failed_objectives", [])
            
            for failed_obj in failed_objectives[-20:]:  # Last 20 failures
                similarity = self._calculate_similarity(objective, failed_obj["objective"])
                if similarity > 0.7:
                    risk_factors.append(f"High similarity to failed objective ({similarity:.2%})")
                    max_risk = max(max_risk, 0.6)
                elif similarity > 0.5:
                    risk_factors.append(f"Moderate similarity to failed objective ({similarity:.2%})")
                    max_risk = max(max_risk, 0.3)
        
        except Exception as e:
            self.logger.warning(f"Could not analyze historical similarity: {e}")
        
        return max_risk, risk_factors
    
    def _analyze_async_risks(self, objective: str) -> Tuple[float, List[str]]:
        """Analisa riscos relacionados a operações assíncronas"""
        risk_factors = []
        risk_score = 0.0
        
        async_keywords = ["async", "await", "concurrent", "parallel", "pipeline", "orchestrat"]
        async_count = sum(1 for keyword in async_keywords if keyword.lower() in objective.lower())
        
        if async_count >= 2:
            risk_factors.append(f"Multiple async-related keywords ({async_count})")
            risk_score += 0.3
        elif async_count >= 1:
            risk_factors.append("Contains async-related keywords")
            risk_score += 0.1
        
        # Known problematic patterns
        problematic_patterns = [
            "ASYNC_PIPELINE_ERROR",
            "coroutine",
            "event loop",
            "concurrent execution"
        ]
        
        for pattern in problematic_patterns:
            if pattern.lower() in objective.lower():
                risk_factors.append(f"Contains problematic async pattern: {pattern}")
                risk_score += 0.2
        
        return min(risk_score, 1.0), risk_factors
    
    def _generate_preventive_modifications(self, objective: str, risk_factors: List[str], failure_types: List[str]) -> List[str]:
        """Gera modificações preventivas baseadas nos fatores de risco"""
        modifications = []
        
        # Async-related modifications
        if any("async" in factor.lower() for factor in risk_factors):
            modifications.append("Add comprehensive error handling for async operations")
            modifications.append("Include timeout and retry mechanisms")
            modifications.append("Add async operation monitoring and logging")
        
        # Complexity-related modifications
        if any("complex" in factor.lower() or "large" in factor.lower() for factor in risk_factors):
            modifications.append("Break down into smaller, incremental steps")
            modifications.append("Add intermediate validation checkpoints")
            modifications.append("Include rollback mechanisms for each step")
        
        # Pattern-based modifications
        if any("pattern" in factor.lower() for factor in risk_factors):
            modifications.append("Apply lessons learned from similar failures")
            modifications.append("Add pre-execution validation checks")
            modifications.append("Include alternative fallback strategies")
        
        # General safety modifications
        modifications.extend([
            "Add comprehensive test coverage",
            "Include performance monitoring",
            "Add detailed logging and debugging information"
        ])
        
        return modifications[:5]  # Limit to top 5 modifications
    
    def _apply_modification(self, objective: str, modification: str) -> str:
        """Aplica uma modificação específica ao objetivo"""
        # This is a simplified version - in practice, would use LLM to intelligently modify
        if "error handling" in modification.lower():
            return objective + f" Ensure {modification.lower()} throughout the implementation."
        elif "break down" in modification.lower():
            return objective.replace("Refactor", "Incrementally refactor") + f" {modification}"
        else:
            return objective + f" {modification}"
    
    def _objective_matches_pattern(self, objective: str, pattern: FailurePattern) -> bool:
        """Verifica se um objetivo corresponde a um padrão de falha"""
        matches = 0
        for condition in pattern.trigger_conditions:
            if condition.lower() in objective.lower():
                matches += 1
        
        # Require at least 50% of conditions to match
        return matches / len(pattern.trigger_conditions) >= 0.5
    
    def _calculate_similarity(self, obj1: str, obj2: str) -> float:
        """Calcula similaridade entre dois objetivos"""
        # Simple word-based similarity
        words1 = set(obj1.lower().split())
        words2 = set(obj2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_confidence(self, risk_factors: List[str], pattern_count: int) -> float:
        """Calcula nível de confiança da predição"""
        base_confidence = 0.5
        
        # More risk factors = higher confidence
        factor_boost = min(len(risk_factors) * 0.1, 0.3)
        
        # More patterns = higher confidence
        pattern_boost = min(pattern_count * 0.05, 0.2)
        
        return min(base_confidence + factor_boost + pattern_boost, 1.0)
    
    def _update_failure_patterns(self, objective: str, failure_reason: str, execution_time: float):
        """Atualiza padrões de falha com novos dados"""
        # Extract keywords and create new patterns
        keywords = self._extract_keywords(objective)
        pattern_id = hashlib.md5(f"{failure_reason}_{'-'.join(keywords[:3])}".encode()).hexdigest()[:8]
        
        if pattern_id in self.failure_patterns:
            # Update existing pattern
            pattern = self.failure_patterns[pattern_id]
            pattern.historical_occurrences += 1
            pattern.avg_failure_time = (pattern.avg_failure_time + execution_time) / 2
            pattern.last_seen = datetime.now()
            if failure_reason not in pattern.common_error_types:
                pattern.common_error_types.append(failure_reason)
        else:
            # Create new pattern
            self.failure_patterns[pattern_id] = FailurePattern(
                pattern_id=pattern_id,
                pattern_type="learned",
                trigger_conditions=keywords,
                failure_probability=0.6,  # Start with moderate probability
                historical_occurrences=1,
                avg_failure_time=execution_time,
                common_error_types=[failure_reason],
                preventive_modifications=[],
                confidence_score=0.6,
                last_seen=datetime.now()
            )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrai palavras-chave relevantes do texto"""
        # Remove common words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", 
            "has", "had", "do", "does", "did", "will", "would", "should", "could"
        }
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency and return most common
        word_counts = Counter(keywords)
        return [word for word, _ in word_counts.most_common(10)]
    
    def _load_failure_patterns(self):
        """Carrega padrões de falha salvos"""
        try:
            patterns_file = Path("data/reports/failure_patterns.json")
            if patterns_file.exists():
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    
                for pattern_id, pattern_data in patterns_data.items():
                    pattern_data['last_seen'] = datetime.fromisoformat(pattern_data['last_seen'])
                    self.failure_patterns[pattern_id] = FailurePattern(**pattern_data)
                
                self.logger.info(f"📂 Loaded {len(self.failure_patterns)} failure patterns")
        except Exception as e:
            self.logger.warning(f"Could not load failure patterns: {e}")
    
    def _save_failure_patterns(self):
        """Salva padrões de falha"""
        try:
            patterns_file = Path("data/reports/failure_patterns.json")
            patterns_file.parent.mkdir(parents=True, exist_ok=True)
            
            patterns_data = {
                pattern_id: pattern.to_dict() 
                for pattern_id, pattern in self.failure_patterns.items()
            }
            
            with open(patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Could not save failure patterns: {e}")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do engine"""
        return {
            "total_patterns": len(self.failure_patterns),
            "cached_analyses": len(self.analysis_cache),
            "prediction_history_size": len(self.prediction_history),
            "failure_threshold": self.failure_threshold,
            "confidence_threshold": self.confidence_threshold,
            "recent_predictions": self.prediction_history[-5:] if self.prediction_history else []
        }


# Singleton instance
_predictive_engine = None

def get_predictive_failure_engine(config: Dict[str, Any], logger: logging.Logger, memory_path: str) -> PredictiveFailureEngine:
    """Get singleton instance of the Predictive Failure Engine"""
    global _predictive_engine
    if _predictive_engine is None:
        _predictive_engine = PredictiveFailureEngine(config, logger, memory_path)
    return _predictive_engine