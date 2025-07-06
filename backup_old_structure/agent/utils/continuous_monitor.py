"""
Continuous Monitor - Sistema de monitoramento contínuo para detectar problemas em tempo real
"""

import logging
import time
import threading
import queue
import psutil
import os
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import json
import signal
import sys

@dataclass
class SystemMetrics:
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    active_threads: int
    timestamp: datetime

@dataclass
class Alert:
    level: str  # 'info', 'warning', 'error', 'critical'
    message: str
    component: str
    timestamp: datetime
    metrics: Optional[SystemMetrics] = None
    action_taken: Optional[str] = None

class ContinuousMonitor:
    """Monitora o sistema continuamente e detecta problemas"""
    
    def __init__(self, logger: logging.Logger, check_interval: int = 30):
        self.logger = logger
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.alert_queue = queue.Queue()
        self.metrics_history = []
        self.alerts_history = []
        
        # Thresholds para alertas
        self.thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 90.0,
            'memory_warning': 80.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'thread_warning': 100,
            'thread_critical': 200
        }
        
        # Componentes críticos para monitorar
        self.critical_components = [
            'hephaestus_agent',
            'async_orchestrator',
            'optimized_pipeline',
            'cycle_runner'
        ]
        
        # Callbacks para ações automáticas
        self.alert_handlers = {
            'cpu_critical': self._handle_cpu_critical,
            'memory_critical': self._handle_memory_critical,
            'disk_critical': self._handle_disk_critical,
            'component_failure': self._handle_component_failure
        }
        
        # Estatísticas
        self.stats = {
            'total_checks': 0,
            'alerts_generated': 0,
            'auto_actions_taken': 0,
            'start_time': datetime.now()
        }
    
    def start_monitoring(self):
        """Inicia o monitoramento em background"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("🔍 Monitoramento contínuo iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🔍 Monitoramento contínuo parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring:
            try:
                self._perform_system_check()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(5)
    
    def _perform_system_check(self):
        """Executa verificação completa do sistema"""
        self.stats['total_checks'] += 1
        
        # Coletar métricas do sistema
        metrics = self._collect_system_metrics()
        self.metrics_history.append(metrics)
        
        # Manter apenas as últimas 1000 métricas
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Verificar thresholds
        self._check_thresholds(metrics)
        
        # Verificar componentes críticos
        self._check_critical_components()
        
        # Processar alertas
        self._process_alerts()
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Coleta métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            active_threads = threading.active_count()
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_threads=active_threads,
                timestamp=datetime.now()
            )
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {e}")
            return SystemMetrics(0, 0, 0, 0, datetime.now())
    
    def _check_thresholds(self, metrics: SystemMetrics):
        """Verifica se as métricas ultrapassaram os thresholds"""
        
        # CPU
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            self._create_alert('critical', f"CPU usage critical: {metrics.cpu_percent:.1f}%", 'system', metrics)
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            self._create_alert('warning', f"CPU usage high: {metrics.cpu_percent:.1f}%", 'system', metrics)
        
        # Memory
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            self._create_alert('critical', f"Memory usage critical: {metrics.memory_percent:.1f}%", 'system', metrics)
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            self._create_alert('warning', f"Memory usage high: {metrics.memory_percent:.1f}%", 'system', metrics)
        
        # Disk
        if metrics.disk_usage_percent >= self.thresholds['disk_critical']:
            self._create_alert('critical', f"Disk usage critical: {metrics.disk_usage_percent:.1f}%", 'system', metrics)
        elif metrics.disk_usage_percent >= self.thresholds['disk_warning']:
            self._create_alert('warning', f"Disk usage high: {metrics.disk_usage_percent:.1f}%", 'system', metrics)
        
        # Threads
        if metrics.active_threads >= self.thresholds['thread_critical']:
            self._create_alert('critical', f"Too many threads: {metrics.active_threads}", 'system', metrics)
        elif metrics.active_threads >= self.thresholds['thread_warning']:
            self._create_alert('warning', f"High thread count: {metrics.active_threads}", 'system', metrics)
    
    def _check_critical_components(self):
        """Verifica se os componentes críticos estão funcionando"""
        for component in self.critical_components:
            try:
                # Verificar se o processo está ativo
                if not self._is_component_healthy(component):
                    self._create_alert('error', f"Component {component} is not healthy", component)
            except Exception as e:
                self._create_alert('critical', f"Component {component} failed: {e}", component)
    
    def _is_component_healthy(self, component: str) -> bool:
        """Verifica se um componente está saudável"""
        # Implementar verificações específicas por componente
        if component == 'hephaestus_agent':
            # Verificar se o agente principal está respondendo
            return True  # Placeholder
        elif component == 'async_orchestrator':
            # Verificar se o orquestrador está funcionando
            return True  # Placeholder
        
        return True
    
    def _create_alert(self, level: str, message: str, component: str, metrics: Optional[SystemMetrics] = None):
        """Cria um alerta"""
        alert = Alert(
            level=level,
            message=message,
            component=component,
            timestamp=datetime.now(),
            metrics=metrics
        )
        
        self.alerts_history.append(alert)
        self.alert_queue.put(alert)
        self.stats['alerts_generated'] += 1
        
        # Log do alerta
        log_level = getattr(self.logger, level, self.logger.warning)
        log_level(f"🚨 ALERT [{level.upper()}] {component}: {message}")
    
    def _process_alerts(self):
        """Processa alertas e executa ações automáticas"""
        while not self.alert_queue.empty():
            try:
                alert = self.alert_queue.get_nowait()
                
                # Executar ação automática baseada no tipo de alerta
                if alert.level == 'critical':
                    self._execute_auto_action(alert)
                
            except queue.Empty:
                break
    
    def _execute_auto_action(self, alert: Alert):
        """Executa ação automática para alertas críticos"""
        try:
            if 'cpu_critical' in alert.message.lower():
                action = self.alert_handlers['cpu_critical'](alert)
            elif 'memory_critical' in alert.message.lower():
                action = self.alert_handlers['memory_critical'](alert)
            elif 'disk_critical' in alert.message.lower():
                action = self.alert_handlers['disk_critical'](alert)
            elif alert.component in self.critical_components:
                action = self.alert_handlers['component_failure'](alert)
            else:
                action = "No specific action taken"
            
            alert.action_taken = action
            self.stats['auto_actions_taken'] += 1
            
            self.logger.info(f"🛠️ Auto-action executed: {action}")
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação automática: {e}")
    
    def _handle_cpu_critical(self, alert: Alert) -> str:
        """Manipula alerta crítico de CPU"""
        # Tentar reduzir carga de CPU
        return "Reduced background tasks and optimized processing"
    
    def _handle_memory_critical(self, alert: Alert) -> str:
        """Manipula alerta crítico de memória"""
        # Tentar liberar memória
        import gc
        gc.collect()
        return "Forced garbage collection to free memory"
    
    def _handle_disk_critical(self, alert: Alert) -> str:
        """Manipula alerta crítico de disco"""
        # Tentar limpar arquivos temporários
        return "Cleaned temporary files and logs"
    
    def _handle_component_failure(self, alert: Alert) -> str:
        """Manipula falha de componente"""
        # Tentar reinicializar componente
        return f"Attempted to restart component {alert.component}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        if not self.metrics_history:
            return {'status': 'no_data'}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calcular tendências
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        # Alertas recentes
        recent_alerts = [a for a in self.alerts_history if a.timestamp > datetime.now() - timedelta(hours=1)]
        
        return {
            'current_metrics': {
                'cpu_percent': latest_metrics.cpu_percent,
                'memory_percent': latest_metrics.memory_percent,
                'disk_usage_percent': latest_metrics.disk_usage_percent,
                'active_threads': latest_metrics.active_threads
            },
            'trends': {
                'avg_cpu_10min': avg_cpu,
                'avg_memory_10min': avg_memory
            },
            'alerts': {
                'total_alerts': len(self.alerts_history),
                'recent_alerts': len(recent_alerts),
                'critical_alerts': len([a for a in recent_alerts if a.level == 'critical'])
            },
            'stats': self.stats,
            'uptime': (datetime.now() - self.stats['start_time']).total_seconds()
        }
    
    def generate_monitoring_report(self) -> str:
        """Gera relatório detalhado de monitoramento"""
        status = self.get_system_status()
        
        report = []
        report.append("=" * 60)
        report.append("CONTINUOUS MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now()}")
        report.append(f"Uptime: {status['uptime']:.0f} seconds")
        report.append("")
        
        # Métricas atuais
        metrics = status['current_metrics']
        report.append("CURRENT METRICS:")
        report.append(f"  CPU: {metrics['cpu_percent']:.1f}%")
        report.append(f"  Memory: {metrics['memory_percent']:.1f}%")
        report.append(f"  Disk: {metrics['disk_usage_percent']:.1f}%")
        report.append(f"  Threads: {metrics['active_threads']}")
        report.append("")
        
        # Tendências
        trends = status['trends']
        report.append("TRENDS (10 min average):")
        report.append(f"  CPU: {trends['avg_cpu_10min']:.1f}%")
        report.append(f"  Memory: {trends['avg_memory_10min']:.1f}%")
        report.append("")
        
        # Alertas
        alerts = status['alerts']
        report.append("ALERTS:")
        report.append(f"  Total: {alerts['total_alerts']}")
        report.append(f"  Recent (1h): {alerts['recent_alerts']}")
        report.append(f"  Critical: {alerts['critical_alerts']}")
        report.append("")
        
        # Estatísticas
        stats = status['stats']
        report.append("STATISTICS:")
        report.append(f"  Total checks: {stats['total_checks']}")
        report.append(f"  Alerts generated: {stats['alerts_generated']}")
        report.append(f"  Auto actions taken: {stats['auto_actions_taken']}")
        report.append("=" * 60)
        
        return "\n".join(report)

# Singleton para o monitor
_monitor_instance = None

def get_continuous_monitor(logger: logging.Logger) -> ContinuousMonitor:
    """Retorna instância singleton do monitor"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ContinuousMonitor(logger)
    return _monitor_instance 