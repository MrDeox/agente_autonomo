"""
Autonomous Monitor Agent - Agente de monitoramento autônomo
"""

import logging
import threading
import time
from typing import Dict, Any, List
from datetime import datetime

class AutonomousMonitorAgent:
    """Agente de monitoramento autônomo do sistema."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger('AutonomousMonitorAgent')
        self.monitoring_active = False
        self.monitor_thread = None
        self.metrics = {
            'system_health': 100,
            'performance_score': 0,
            'last_check': None,
            'alerts': []
        }
    
    def start_monitoring(self):
        """Iniciar monitoramento autônomo."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("🔍 Monitoramento autônomo iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("🛑 Monitoramento autônomo parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento."""
        while self.monitoring_active:
            try:
                self._check_system_health()
                self.metrics['last_check'] = datetime.now()
                time.sleep(self.config.get('check_interval', 30))
            except Exception as e:
                self.logger.error(f"Erro no monitoramento: {e}")
                time.sleep(5)
    
    def _check_system_health(self):
        """Verificar saúde do sistema."""
        # Simular verificação de saúde
        self.metrics['system_health'] = 100
        self.metrics['performance_score'] = 85
        self.logger.debug("✅ Verificação de saúde concluída")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obter métricas atuais."""
        return self.metrics.copy()
    
    def add_alert(self, message: str, severity: str = "info"):
        """Adicionar alerta."""
        alert = {
            'timestamp': datetime.now(),
            'message': message,
            'severity': severity
        }
        self.metrics['alerts'].append(alert)
        self.logger.warning(f"🚨 Alerta: {message}")
    
    def is_healthy(self) -> bool:
        """Verificar se sistema está saudável."""
        return self.metrics['system_health'] > 50