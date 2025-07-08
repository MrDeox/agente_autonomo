"""
Cycle Monitor Agent - Monitoramento de ciclos de execução
"""

import logging
import time
import threading
from typing import Dict, Any, List
from datetime import datetime
from hephaestus.agents.base import BaseAgent, AgentCapability

class CycleMonitorAgent(BaseAgent):
    """Agente para monitorar ciclos de execução do sistema."""
    
    def __init__(self, config: Dict[str, Any]):
        logger = logging.getLogger('CycleMonitorAgent')
        super().__init__(
            name="CycleMonitorAgent",
            capabilities=[AgentCapability.PERFORMANCE_ANALYSIS, AgentCapability.ORCHESTRATION],
            logger=logger
        )
        self.config = config
        self.monitoring_active = False
        self.monitor_thread = None
        self.cycle_data = []
        self.performance_metrics = {
            'cycles_completed': 0,
            'avg_cycle_time': 0,
            'success_rate': 0,
            'error_count': 0
        }
        
        self._logger.info("🔄 CycleMonitorAgent inicializado")
    
    def start_monitoring(self):
        """Iniciar monitoramento de ciclos."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self._logger.info("🔄 Monitoramento de ciclos iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento de ciclos."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self._logger.info("🛑 Monitoramento de ciclos parado")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring_active:
            try:
                # Coletar dados de performance
                current_metrics = self._collect_cycle_metrics()
                
                # Analisar performance
                self._analyze_cycle_performance(current_metrics)
                
                # Atualizar métricas
                self._update_metrics(current_metrics)
                
                time.sleep(30)  # Monitor a cada 30 segundos
                
            except Exception as e:
                self._logger.error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(10)
    
    def _collect_cycle_metrics(self) -> Dict[str, Any]:
        """Coletar métricas de ciclos."""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_cycles': self._count_active_cycles(),
            'system_load': self._get_system_load(),
            'memory_usage': self._get_memory_usage()
        }
    
    def _count_active_cycles(self) -> int:
        """Contar ciclos ativos."""
        # Implementação básica - pode ser expandida
        return threading.active_count()
    
    def _get_system_load(self) -> float:
        """Obter carga do sistema."""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except ImportError:
            return 0.0
    
    def _get_memory_usage(self) -> float:
        """Obter uso de memória."""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except ImportError:
            return 0.0
    
    def _analyze_cycle_performance(self, metrics: Dict[str, Any]):
        """Analisar performance dos ciclos."""
        if metrics.get('system_load', 0) > 80:
            self._logger.warning("⚠️ Alta carga do sistema detectada")
        
        if metrics.get('memory_usage', 0) > 85:
            self._logger.warning("⚠️ Alto uso de memória detectado")
    
    def _update_metrics(self, current_metrics: Dict[str, Any]):
        """Atualizar métricas de performance."""
        self.cycle_data.append(current_metrics)
        
        # Manter apenas últimos 100 registros
        if len(self.cycle_data) > 100:
            self.cycle_data = self.cycle_data[-100:]
        
        # Calcular métricas agregadas
        if len(self.cycle_data) > 0:
            self.performance_metrics['cycles_completed'] = len(self.cycle_data)
            avg_load = sum(d.get('system_load', 0) for d in self.cycle_data) / len(self.cycle_data)
            self.performance_metrics['avg_cycle_time'] = avg_load
    
    def get_cycle_summary(self) -> Dict[str, Any]:
        """Obter resumo dos ciclos."""
        return {
            'monitoring_active': self.monitoring_active,
            'performance_metrics': self.performance_metrics,
            'recent_data_points': len(self.cycle_data),
            'last_update': self.cycle_data[-1]['timestamp'] if self.cycle_data else None
        }
    
    async def execute(self, context) -> Dict[str, Any]:
        """Executar tarefa do agente."""
        if hasattr(context, 'metadata'):
            task = context.metadata
        else:
            task = context if isinstance(context, dict) else {}
        """Executar tarefa do agente."""
        task_type = task.get('type', 'monitor')
        
        if task_type == 'start_monitoring':
            self.start_monitoring()
            return {'status': 'success', 'message': 'Monitoramento iniciado'}
        
        elif task_type == 'stop_monitoring':
            self.stop_monitoring()
            return {'status': 'success', 'message': 'Monitoramento parado'}
        
        elif task_type == 'get_summary':
            return self.get_cycle_summary()
        
        else:
            return {'status': 'error', 'message': f'Tipo de tarefa não suportado: {task_type}'}
    
    def get_capabilities(self) -> List[str]:
        """Obter capacidades do agente."""
        return [
            'cycle_monitoring',
            'performance_analysis',
            'system_metrics',
            'real_time_monitoring'
        ]
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status do agente."""
        return {
            'name': self.name,
            'active': self.monitoring_active,
            'cycles_monitored': len(self.cycle_data),
            'performance_metrics': self.performance_metrics
        }