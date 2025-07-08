"""
📊 EVOLUTION ANALYTICS - Análise de Longo Prazo

Sistema para monitorar e analisar a evolução do sistema ao longo do tempo:
1. Coleta de métricas históricas
2. Análise de tendências de melhoria
3. Detecção de regressões
4. Relatórios de evolução
5. Previsões de performance futura
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, deque

@dataclass
class EvolutionMetric:
    """Métrica de evolução capturada"""
    timestamp: datetime
    metric_name: str
    value: float
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_name": self.metric_name,
            "value": self.value,
            "context": self.context
        }

@dataclass
class EvolutionTrend:
    """Tendência de evolução identificada"""
    metric_name: str
    trend_type: str  # "improving", "declining", "stable", "fluctuating"
    slope: float
    confidence: float
    period_days: int
    start_value: float
    end_value: float
    change_percentage: float
    data_points: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "trend_type": self.trend_type,
            "slope": self.slope,
            "confidence": self.confidence,
            "period_days": self.period_days,
            "start_value": self.start_value,
            "end_value": self.end_value,
            "change_percentage": self.change_percentage,
            "data_points": self.data_points
        }

class EvolutionAnalytics:
    """
    Sistema de análise de evolução de longo prazo
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("EvolutionAnalytics")
        
        # Configurações
        self.retention_days = config.get("evolution_analytics", {}).get("retention_days", 30)
        self.analysis_interval_hours = config.get("evolution_analytics", {}).get("analysis_interval_hours", 6)
        self.min_data_points = config.get("evolution_analytics", {}).get("min_data_points", 10)
        
        # Diretórios
        self.data_dir = Path("data/evolution_analytics")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Armazenamento
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.trends_history: List[EvolutionTrend] = []
        
        # Carregar dados existentes
        self._load_existing_data()
        
        self.logger.info("📊 Evolution Analytics initialized - Long-term improvement tracking active!")
    
    def capture_metric(self, metric_name: str, value: float, context: Dict[str, Any] = None):
        """Captura uma nova métrica"""
        try:
            if context is None:
                context = {}
            
            metric = EvolutionMetric(
                timestamp=datetime.now(),
                metric_name=metric_name,
                value=value,
                context=context
            )
            
            self.metrics_history[metric_name].append(metric)
            
            # Salvar periodicamente
            if len(self.metrics_history[metric_name]) % 10 == 0:
                self._save_metrics(metric_name)
                
        except Exception as e:
            self.logger.error(f"❌ Error capturing metric {metric_name}: {e}")
    
    def analyze_trends(self, days: int = 7) -> List[EvolutionTrend]:
        """Analisa tendências dos últimos N dias"""
        try:
            trends = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for metric_name, metrics in self.metrics_history.items():
                # Filtrar métricas recentes
                recent_metrics = [
                    m for m in metrics 
                    if m.timestamp >= cutoff_date
                ]
                
                if len(recent_metrics) < self.min_data_points:
                    continue
                
                # Ordenar por timestamp
                recent_metrics.sort(key=lambda x: x.timestamp)
                
                # Calcular tendência
                trend = self._calculate_trend(metric_name, recent_metrics, days)
                if trend:
                    trends.append(trend)
            
            # Salvar tendências
            self.trends_history.extend(trends)
            self._save_trends()
            
            self.logger.info(f"📈 Analyzed {len(trends)} trends over {days} days")
            return trends
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing trends: {e}")
            return []
    
    def _calculate_trend(self, metric_name: str, metrics: List[EvolutionMetric], days: int) -> Optional[EvolutionTrend]:
        """Calcula tendência para uma métrica específica"""
        try:
            if len(metrics) < 2:
                return None
            
            # Extrair valores e timestamps
            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # Converter timestamps para dias desde o início
            start_time = timestamps[0]
            days_since_start = [(t - start_time).total_seconds() / 86400 for t in timestamps]
            
            # Calcular regressão linear
            slope, intercept = np.polyfit(days_since_start, values, 1)
            
            # Calcular R² (confiança)
            y_pred = [slope * x + intercept for x in days_since_start]
            ss_res = sum((y - y_pred[i]) ** 2 for i, y in enumerate(values))
            ss_tot = sum((y - np.mean(values)) ** 2 for y in values)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Determinar tipo de tendência
            change_percentage = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
            
            if abs(change_percentage) < 5:
                trend_type = "stable"
            elif change_percentage > 10 and r_squared > 0.3:
                trend_type = "improving"
            elif change_percentage < -10 and r_squared > 0.3:
                trend_type = "declining"
            else:
                trend_type = "fluctuating"
            
            return EvolutionTrend(
                metric_name=metric_name,
                trend_type=trend_type,
                slope=slope,
                confidence=r_squared,
                period_days=days,
                start_value=values[0],
                end_value=values[-1],
                change_percentage=change_percentage,
                data_points=len(metrics)
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating trend for {metric_name}: {e}")
            return None
    
    def get_improvement_report(self, days: int = 7) -> Dict[str, Any]:
        """Gera relatório de melhoria"""
        try:
            trends = self.analyze_trends(days)
            
            # Estatísticas gerais
            improving_metrics = [t for t in trends if t.trend_type == "improving"]
            declining_metrics = [t for t in trends if t.trend_type == "declining"]
            stable_metrics = [t for t in trends if t.trend_type == "stable"]
            
            # Calcular score de melhoria geral
            improvement_score = 0
            if trends:
                positive_changes = sum(t.change_percentage for t in improving_metrics)
                negative_changes = sum(abs(t.change_percentage) for t in declining_metrics)
                total_changes = positive_changes + negative_changes
                improvement_score = (positive_changes / total_changes * 100) if total_changes > 0 else 50
            
            report = {
                "analysis_period_days": days,
                "total_metrics_analyzed": len(trends),
                "improving_metrics": len(improving_metrics),
                "declining_metrics": len(declining_metrics),
                "stable_metrics": len(stable_metrics),
                "improvement_score": improvement_score,
                "top_improvements": sorted(improving_metrics, key=lambda x: x.change_percentage, reverse=True)[:5],
                "top_declines": sorted(declining_metrics, key=lambda x: x.change_percentage)[:5],
                "trends": [t.to_dict() for t in trends],
                "generated_at": datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating improvement report: {e}")
            return {"error": str(e)}
    
    def generate_evolution_chart(self, metric_name: str, days: int = 7) -> Optional[str]:
        """Gera gráfico de evolução para uma métrica"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            metrics = [
                m for m in self.metrics_history[metric_name]
                if m.timestamp >= cutoff_date
            ]
            
            if len(metrics) < 2:
                return None
            
            # Preparar dados
            timestamps = [m.timestamp for m in metrics]
            values = [m.value for m in metrics]
            
            # Criar gráfico
            plt.figure(figsize=(12, 6))
            plt.plot(timestamps, values, 'b-o', linewidth=2, markersize=4)
            plt.title(f'Evolution of {metric_name} over {days} days')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            # Adicionar linha de tendência
            if len(metrics) >= 2:
                trend = self._calculate_trend(metric_name, metrics, days)
                if trend and trend.confidence > 0.1:
                    x_trend = [timestamps[0], timestamps[-1]]
                    y_trend = [trend.start_value, trend.end_value]
                    plt.plot(x_trend, y_trend, 'r--', linewidth=2, label=f'Trend ({trend.trend_type})')
                    plt.legend()
            
            # Salvar gráfico
            chart_path = self.data_dir / f"chart_{metric_name}_{days}d.png"
            plt.tight_layout()
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating chart for {metric_name}: {e}")
            return None
    
    def predict_future_performance(self, metric_name: str, days_ahead: int = 7) -> Optional[Dict[str, Any]]:
        """Prediz performance futura baseada em tendências"""
        try:
            # Usar dados dos últimos 14 dias para predição
            recent_trends = [t for t in self.trends_history if t.metric_name == metric_name]
            if not recent_trends:
                return None
            
            latest_trend = recent_trends[-1]
            
            # Calcular predição
            current_value = latest_trend.end_value
            predicted_change = latest_trend.slope * days_ahead
            predicted_value = current_value + predicted_change
            
            # Calcular intervalo de confiança
            confidence_interval = 1 - latest_trend.confidence
            margin_of_error = abs(predicted_change) * confidence_interval
            
            return {
                "metric_name": metric_name,
                "current_value": current_value,
                "predicted_value": predicted_value,
                "predicted_change": predicted_change,
                "confidence": latest_trend.confidence,
                "margin_of_error": margin_of_error,
                "prediction_horizon_days": days_ahead,
                "trend_type": latest_trend.trend_type
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error predicting future performance for {metric_name}: {e}")
            return None
    
    def _load_existing_data(self):
        """Carrega dados existentes"""
        try:
            # Carregar métricas
            metrics_file = self.data_dir / "metrics_history.json"
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for metric_name, metrics_data in data.items():
                        for metric_dict in metrics_data:
                            metric = EvolutionMetric(
                                timestamp=datetime.fromisoformat(metric_dict["timestamp"]),
                                metric_name=metric_dict["metric_name"],
                                value=metric_dict["value"],
                                context=metric_dict.get("context", {})
                            )
                            self.metrics_history[metric_name].append(metric)
            
            # Carregar tendências
            trends_file = self.data_dir / "trends_history.json"
            if trends_file.exists():
                with open(trends_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for trend_dict in data:
                        trend = EvolutionTrend(**trend_dict)
                        self.trends_history.append(trend)
            
            self.logger.info(f"📊 Loaded {sum(len(metrics) for metrics in self.metrics_history.values())} metrics and {len(self.trends_history)} trends")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading existing data: {e}")
    
    def _save_metrics(self, metric_name: str):
        """Salva métricas para arquivo"""
        try:
            metrics_file = self.data_dir / "metrics_history.json"
            
            # Carregar dados existentes
            data = {}
            if metrics_file.exists():
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Atualizar dados
            data[metric_name] = [m.to_dict() for m in self.metrics_history[metric_name]]
            
            # Salvar
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving metrics: {e}")
    
    def _save_trends(self):
        """Salva tendências para arquivo"""
        try:
            trends_file = self.data_dir / "trends_history.json"
            
            # Converter para dict
            trends_data = [t.to_dict() for t in self.trends_history]
            
            # Salvar
            with open(trends_file, 'w', encoding='utf-8') as f:
                json.dump(trends_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving trends: {e}")
    
    def cleanup_old_data(self):
        """Remove dados antigos"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            
            # Limpar métricas antigas
            for metric_name in list(self.metrics_history.keys()):
                self.metrics_history[metric_name] = deque(
                    [m for m in self.metrics_history[metric_name] if m.timestamp >= cutoff_date],
                    maxlen=1000
                )
            
            # Limpar tendências antigas
            self.trends_history = [
                t for t in self.trends_history
                if datetime.now() - timedelta(days=t.period_days) >= cutoff_date
            ]
            
            self.logger.info(f"🧹 Cleaned up data older than {self.retention_days} days")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up old data: {e}")


# Singleton instance
_evolution_analytics = None

def get_evolution_analytics(config: Dict[str, Any], logger: logging.Logger) -> EvolutionAnalytics:
    """Get singleton instance of Evolution Analytics"""
    global _evolution_analytics
    if _evolution_analytics is None:
        _evolution_analytics = EvolutionAnalytics(config, logger)
    return _evolution_analytics 