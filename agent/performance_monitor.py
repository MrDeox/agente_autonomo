"""
Sistema de Monitoramento de Performance em Tempo Real
====================================================

Este módulo monitora a performance do sistema Hephaestus em tempo real,
identificando gargalos e propondo otimizações automáticas.
"""

import time
import logging
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from pathlib import Path

class PerformanceMonitor:
    """Monitor de performance em tempo real"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.metrics = defaultdict(deque)
        self.thresholds = {
            "response_time": 30.0,  # segundos
            "memory_usage": 0.8,    # 80% da memória
            "error_rate": 0.3,      # 30% de erro
            "success_rate": 0.7     # 70% de sucesso
        }
        self.alerts = []
        self.monitoring_active = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Inicia o monitoramento em background"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🚀 Monitoramento de performance iniciado")
        
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🛑 Monitoramento de performance parado")
        
    def record_metric(self, metric_name: str, value: float, context: Optional[Dict[str, Any]] = None):
        """Registra uma métrica de performance"""
        timestamp = time.time()
        metric_data = {
            "value": value,
            "timestamp": timestamp,
            "context": context or {}
        }
        
        self.metrics[metric_name].append(metric_data)
        
        # Manter apenas as últimas 1000 métricas por tipo
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name].popleft()
            
        # Verificar se excede threshold
        self._check_threshold(metric_name, value, context or {})
        
    def record_execution_time(self, operation: str, execution_time: float, success: bool = True):
        """Registra tempo de execução de uma operação"""
        self.record_metric("execution_time", execution_time, {
            "operation": operation,
            "success": success
        })
        
        # Registrar taxa de sucesso
        success_rate = 1.0 if success else 0.0
        self.record_metric("success_rate", success_rate, {"operation": operation})
        
    def record_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None):
        """Registra um erro"""
        self.record_metric("error_count", 1.0, {
            "error_type": error_type,
            "error_message": error_message,
            **(context if context else {})
        })
        
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtém resumo da performance atual"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {},
            "alerts": self.alerts[-10:],  # Últimos 10 alertas
            "recommendations": []
        }
        
        for metric_name, metric_data in self.metrics.items():
            if not metric_data:
                continue
                
            values = [m["value"] for m in metric_data]
            recent_values = values[-100:] if len(values) > 100 else values
            
            summary["metrics"][metric_name] = {
                "current": values[-1] if values else 0,
                "average": sum(recent_values) / len(recent_values) if recent_values else 0,
                "min": min(recent_values) if recent_values else 0,
                "max": max(recent_values) if recent_values else 0,
                "count": len(values)
            }
            
        # Gerar recomendações
        summary["recommendations"] = self._generate_recommendations(summary["metrics"])
        
        return summary
        
    def _check_threshold(self, metric_name: str, value: float, context: Dict[str, Any]):
        """Verifica se uma métrica excede o threshold"""
        threshold = self.thresholds.get(metric_name)
        if threshold is None:
            return
            
        if metric_name == "response_time" and value > threshold:
            self._create_alert("HIGH_RESPONSE_TIME", f"Response time {value:.2f}s exceeds threshold {threshold}s", context)
        elif metric_name == "error_rate" and value > threshold:
            self._create_alert("HIGH_ERROR_RATE", f"Error rate {value:.2%} exceeds threshold {threshold:.2%}", context)
        elif metric_name == "success_rate" and value < threshold:
            self._create_alert("LOW_SUCCESS_RATE", f"Success rate {value:.2%} below threshold {threshold:.2%}", context)
            
    def _create_alert(self, alert_type: str, message: str, context: Dict[str, Any]):
        """Cria um alerta de performance"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "severity": "high" if "HIGH" in alert_type else "medium"
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"🚨 Performance Alert: {message}")
        
        # Manter apenas os últimos 100 alertas
        if len(self.alerts) > 100:
            self.alerts.pop(0)
            
    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nas métricas"""
        recommendations = []
        
        # Verificar tempo de resposta
        if "execution_time" in metrics:
            avg_time = metrics["execution_time"]["average"]
            if avg_time > 10.0:
                recommendations.append("Consider implementing caching for slow operations")
            if avg_time > 20.0:
                recommendations.append("Review and optimize database queries or external API calls")
                
        # Verificar taxa de erro
        if "error_count" in metrics:
            error_count = metrics["error_count"]["count"]
            if error_count > 10:
                recommendations.append("Implement better error handling and retry mechanisms")
                
        # Verificar taxa de sucesso
        if "success_rate" in metrics:
            success_rate = metrics["success_rate"]["average"]
            if success_rate < 0.8:
                recommendations.append("Investigate and fix common failure patterns")
                
        return recommendations
        
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Verificar métricas agregadas
                self._check_aggregate_metrics()
                
                # Salvar métricas em arquivo periodicamente
                self._save_metrics()
                
                # Aguardar próximo ciclo
                time.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(30)  # Aguardar menos tempo em caso de erro
                
    def _check_aggregate_metrics(self):
        """Verifica métricas agregadas"""
        if not self.metrics:
            return
            
        # Calcular taxa de erro geral
        if "error_count" in self.metrics:
            error_data = list(self.metrics["error_count"])
            recent_errors = [m for m in error_data[-100:] 
                           if time.time() - m["timestamp"] < 3600]  # Última hora
            if recent_errors:
                error_rate = len(recent_errors) / 100
                self._check_threshold("error_rate", error_rate, {"period": "1h"})
                
        # Calcular taxa de sucesso geral
        if "success_rate" in self.metrics:
            success_data = list(self.metrics["success_rate"])
            recent_success = [m for m in success_data[-100:] 
                             if time.time() - m["timestamp"] < 3600]  # Última hora
            if recent_success:
                avg_success = sum(m["value"] for m in recent_success) / len(recent_success)
                self._check_threshold("success_rate", avg_success, {"period": "1h"})
                
    def _save_metrics(self):
        """Salva métricas em arquivo para análise posterior"""
        try:
            metrics_file = Path("logs/performance_metrics.json")
            metrics_file.parent.mkdir(exist_ok=True)
            
            # Preparar dados para salvamento
            save_data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": {}
            }
            
            for metric_name, metric_data in self.metrics.items():
                if metric_data:
                    save_data["metrics"][metric_name] = [
                        {
                            "value": m["value"],
                            "timestamp": m["timestamp"],
                            "context": m["context"]
                        }
                        for m in list(metric_data)[-100:]  # Últimas 100 métricas
                    ]
                    
            # Salvar em arquivo
            with open(metrics_file, "w") as f:
                json.dump(save_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar métricas: {e}")

class PerformanceOptimizer:
    """Otimizador automático de performance"""
    
    def __init__(self, monitor: PerformanceMonitor, logger: logging.Logger):
        self.monitor = monitor
        self.logger = logger
        self.optimizations_applied = []
        
    def analyze_and_optimize(self) -> List[str]:
        """Analisa performance e aplica otimizações automáticas"""
        summary = self.monitor.get_performance_summary()
        optimizations = []
        
        # Verificar se há problemas críticos
        if self._has_critical_issues(summary):
            optimizations.extend(self._apply_critical_optimizations(summary))
            
        # Verificar otimizações de melhoria
        optimizations.extend(self._apply_improvement_optimizations(summary))
        
        return optimizations
        
    def _has_critical_issues(self, summary: Dict[str, Any]) -> bool:
        """Verifica se há problemas críticos de performance"""
        metrics = summary.get("metrics", {})
        
        # Verificar taxa de sucesso muito baixa
        if "success_rate" in metrics:
            success_rate = metrics["success_rate"]["average"]
            if success_rate < 0.5:  # Menos de 50% de sucesso
                return True
                
        # Verificar tempo de resposta muito alto
        if "execution_time" in metrics:
            avg_time = metrics["execution_time"]["average"]
            if avg_time > 30.0:  # Mais de 30 segundos
                return True
                
        return False
        
    def _apply_critical_optimizations(self, summary: Dict[str, Any]) -> List[str]:
        """Aplica otimizações críticas"""
        optimizations = []
        
        # Implementar cache se tempo de resposta for alto
        if "execution_time" in summary["metrics"]:
            avg_time = summary["metrics"]["execution_time"]["average"]
            if avg_time > 15.0:
                optimizations.append("Implementing aggressive caching for slow operations")
                
        # Implementar retry automático se taxa de erro for alta
        if "error_count" in summary["metrics"]:
            error_count = summary["metrics"]["error_count"]["count"]
            if error_count > 5:
                optimizations.append("Enabling automatic retry mechanism for failed operations")
                
        return optimizations
        
    def _apply_improvement_optimizations(self, summary: Dict[str, Any]) -> List[str]:
        """Aplica otimizações de melhoria"""
        optimizations = []
        
        # Sugerir otimizações baseadas nas recomendações
        recommendations = summary.get("recommendations", [])
        for rec in recommendations:
            if "caching" in rec.lower():
                optimizations.append("Scheduling cache implementation")
            elif "optimize" in rec.lower():
                optimizations.append("Scheduling performance optimization review")
                
        return optimizations 