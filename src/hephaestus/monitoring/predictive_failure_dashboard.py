"""
🔮 Predictive Failure Engine Dashboard

Sistema de monitoramento real-time para o Predictive Failure Engine
que mostra métricas de desempenho, accuracy e padrões aprendidos.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

from hephaestus.intelligence.predictive_failure_engine import get_predictive_failure_engine


class PredictiveFailureDashboard:
    """
    Dashboard para monitorar o desempenho do Predictive Failure Engine
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, memory_path: str):
        self.config = config
        self.logger = logger.getChild("PredictiveFailureDashboard")
        self.memory_path = memory_path
        self.predictive_engine = None
        
        # Métricas
        self.accuracy_metrics = {
            "total_predictions": 0,
            "correct_predictions": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "precision": 0.0,
            "recall": 0.0,
            "accuracy": 0.0
        }
        
        self.logger.info("🔮 Predictive Failure Dashboard initialized")
    
    def get_engine_instance(self):
        """Get or create predictive engine instance"""
        if self.predictive_engine is None:
            self.predictive_engine = get_predictive_failure_engine(
                config=self.config,
                logger=self.logger,
                memory_path=self.memory_path
            )
        return self.predictive_engine
    
    def calculate_accuracy_metrics(self) -> Dict[str, Any]:
        """
        Calcula métricas de accuracy do engine baseado no histórico
        """
        engine = self.get_engine_instance()
        
        if not engine.prediction_history:
            return self.accuracy_metrics
        
        total_predictions = 0
        correct_predictions = 0
        false_positives = 0
        false_negatives = 0
        
        for record in engine.prediction_history:
            if 'predicted_failure' in record and 'actual_success' in record:
                total_predictions += 1
                
                predicted_failure = record['predicted_failure']
                actual_success = record['actual_success']
                actual_failure = not actual_success
                
                if predicted_failure == actual_failure:
                    correct_predictions += 1
                elif predicted_failure and actual_success:
                    false_positives += 1
                elif not predicted_failure and actual_failure:
                    false_negatives += 1
        
        # Calculate metrics
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        true_positives = correct_predictions - (total_predictions - false_positives - false_negatives)
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        
        self.accuracy_metrics = {
            "total_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "accuracy": accuracy
        }
        
        return self.accuracy_metrics
    
    def get_failure_pattern_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo dos padrões de falha aprendidos
        """
        engine = self.get_engine_instance()
        
        patterns_by_type = {}
        total_patterns = len(engine.failure_patterns)
        
        for pattern in engine.failure_patterns.values():
            pattern_type = pattern.pattern_type
            if pattern_type not in patterns_by_type:
                patterns_by_type[pattern_type] = []
            
            patterns_by_type[pattern_type].append({
                "pattern_id": pattern.pattern_id,
                "failure_probability": pattern.failure_probability,
                "historical_occurrences": pattern.historical_occurrences,
                "confidence_score": pattern.confidence_score,
                "last_seen": pattern.last_seen.isoformat()
            })
        
        # Sort by failure probability
        for pattern_type in patterns_by_type:
            patterns_by_type[pattern_type].sort(
                key=lambda x: x["failure_probability"], 
                reverse=True
            )
        
        return {
            "total_patterns": total_patterns,
            "patterns_by_type": patterns_by_type,
            "most_dangerous_patterns": self._get_most_dangerous_patterns()
        }
    
    def _get_most_dangerous_patterns(self) -> List[Dict[str, Any]]:
        """
        Retorna os padrões mais perigosos (alta probabilidade + alta confiança)
        """
        engine = self.get_engine_instance()
        
        dangerous_patterns = []
        
        for pattern in engine.failure_patterns.values():
            danger_score = pattern.failure_probability * pattern.confidence_score
            
            if danger_score > 0.5:  # Threshold for "dangerous"
                dangerous_patterns.append({
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "failure_probability": pattern.failure_probability,
                    "confidence_score": pattern.confidence_score,
                    "danger_score": danger_score,
                    "trigger_conditions": pattern.trigger_conditions,
                    "common_error_types": pattern.common_error_types
                })
        
        # Sort by danger score
        dangerous_patterns.sort(key=lambda x: x["danger_score"], reverse=True)
        
        return dangerous_patterns[:10]  # Top 10
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna predições recentes com seus resultados
        """
        engine = self.get_engine_instance()
        
        recent_predictions = engine.prediction_history[-limit:] if engine.prediction_history else []
        
        # Add accuracy info to each prediction
        for prediction in recent_predictions:
            if 'predicted_failure' in prediction and 'actual_success' in prediction:
                predicted_failure = prediction['predicted_failure']
                actual_success = prediction['actual_success']
                
                if predicted_failure == (not actual_success):
                    prediction['prediction_accuracy'] = 'correct'
                else:
                    prediction['prediction_accuracy'] = 'incorrect'
            else:
                prediction['prediction_accuracy'] = 'unknown'
        
        return recent_predictions
    
    def get_modification_effectiveness(self) -> Dict[str, Any]:
        """
        Analisa a efetividade das modificações preventivas
        """
        engine = self.get_engine_instance()
        
        modified_objectives = []
        unmodified_objectives = []
        
        for record in engine.prediction_history:
            if 'predicted_failure' in record and record['predicted_failure']:
                if 'recommended_modifications' in record and record['recommended_modifications']:
                    modified_objectives.append(record)
                else:
                    unmodified_objectives.append(record)
        
        # Calculate success rates
        modified_success_rate = 0.0
        if modified_objectives:
            modified_successes = sum(1 for r in modified_objectives if r.get('actual_success', False))
            modified_success_rate = modified_successes / len(modified_objectives)
        
        unmodified_success_rate = 0.0
        if unmodified_objectives:
            unmodified_successes = sum(1 for r in unmodified_objectives if r.get('actual_success', False))
            unmodified_success_rate = unmodified_successes / len(unmodified_objectives)
        
        effectiveness = modified_success_rate - unmodified_success_rate
        
        return {
            "modified_objectives_count": len(modified_objectives),
            "unmodified_objectives_count": len(unmodified_objectives),
            "modified_success_rate": modified_success_rate,
            "unmodified_success_rate": unmodified_success_rate,
            "modification_effectiveness": effectiveness,
            "improvement_percentage": effectiveness * 100
        }
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """
        Gera relatório abrangente do Predictive Failure Engine
        """
        engine = self.get_engine_instance()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "engine_status": engine.get_engine_status(),
            "accuracy_metrics": self.calculate_accuracy_metrics(),
            "failure_patterns": self.get_failure_pattern_summary(),
            "recent_predictions": self.get_recent_predictions(),
            "modification_effectiveness": self.get_modification_effectiveness(),
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """
        Gera recomendações baseadas nas métricas atuais
        """
        recommendations = []
        
        accuracy_metrics = self.calculate_accuracy_metrics()
        
        if accuracy_metrics["accuracy"] < 0.7:
            recommendations.append("🎯 Accuracy is below 70% - consider adjusting prediction thresholds")
        
        if accuracy_metrics["false_positives"] > accuracy_metrics["false_negatives"] * 2:
            recommendations.append("⚠️ High false positive rate - may be too conservative")
        
        if accuracy_metrics["false_negatives"] > accuracy_metrics["false_positives"] * 2:
            recommendations.append("🚨 High false negative rate - may miss critical failures")
        
        modification_effectiveness = self.get_modification_effectiveness()
        if modification_effectiveness["modification_effectiveness"] < 0.1:
            recommendations.append("🔧 Preventive modifications showing low effectiveness")
        
        engine = self.get_engine_instance()
        if len(engine.failure_patterns) < 5:
            recommendations.append("📚 Limited failure patterns - needs more learning data")
        
        return recommendations
    
    def save_report(self, filename: str = None):
        """
        Salva relatório em arquivo
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"predictive_failure_report_{timestamp}.json"
        
        report = self.get_comprehensive_report()
        
        report_path = Path("data/reports") / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Predictive Failure report saved to {report_path}")
        
        return report_path
    
    def print_dashboard(self):
        """
        Imprime dashboard no console
        """
        report = self.get_comprehensive_report()
        
        print("\n" + "="*60)
        print("🔮 PREDICTIVE FAILURE ENGINE DASHBOARD")
        print("="*60)
        
        # Engine Status
        engine_status = report["engine_status"]
        print(f"\n📊 ENGINE STATUS:")
        print(f"  • Total Patterns: {engine_status['total_patterns']}")
        print(f"  • Cached Analyses: {engine_status['cached_analyses']}")
        print(f"  • Prediction History: {engine_status['prediction_history_size']}")
        
        # Accuracy Metrics
        accuracy = report["accuracy_metrics"]
        print(f"\n🎯 ACCURACY METRICS:")
        print(f"  • Overall Accuracy: {accuracy['accuracy']:.1%}")
        print(f"  • Precision: {accuracy['precision']:.1%}")
        print(f"  • Recall: {accuracy['recall']:.1%}")
        print(f"  • False Positives: {accuracy['false_positives']}")
        print(f"  • False Negatives: {accuracy['false_negatives']}")
        
        # Modification Effectiveness
        effectiveness = report["modification_effectiveness"]
        print(f"\n🔧 MODIFICATION EFFECTIVENESS:")
        print(f"  • Modified Objectives: {effectiveness['modified_objectives_count']}")
        print(f"  • Success Rate (Modified): {effectiveness['modified_success_rate']:.1%}")
        print(f"  • Success Rate (Unmodified): {effectiveness['unmodified_success_rate']:.1%}")
        print(f"  • Improvement: {effectiveness['improvement_percentage']:+.1f}%")
        
        # Dangerous Patterns
        dangerous_patterns = report["failure_patterns"]["most_dangerous_patterns"]
        if dangerous_patterns:
            print(f"\n⚠️ MOST DANGEROUS PATTERNS:")
            for i, pattern in enumerate(dangerous_patterns[:5], 1):
                print(f"  {i}. {pattern['pattern_id']} ({pattern['danger_score']:.2f})")
                print(f"     Type: {pattern['pattern_type']}")
                print(f"     Failure Prob: {pattern['failure_probability']:.1%}")
        
        # Recommendations
        recommendations = report["recommendations"]
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


# Singleton instance
_dashboard = None

def get_predictive_failure_dashboard(config: Dict[str, Any], logger: logging.Logger, memory_path: str) -> PredictiveFailureDashboard:
    """Get singleton instance of the dashboard"""
    global _dashboard
    if _dashboard is None:
        _dashboard = PredictiveFailureDashboard(config, logger, memory_path)
    return _dashboard