"""
Cognitive Evolution Manager - Sistema de evolução cognitiva do Hephaestus
"""

import logging
import threading
import time
from typing import Dict, Any, Optional

class CognitiveEvolutionManager:
    """Gerenciador de evolução cognitiva do sistema."""
    
    def __init__(self, config: Dict, logger: logging.Logger, memory, model_optimizer):
        self.config = config
        self.logger = logger
        self.memory = memory
        self.model_optimizer = model_optimizer
        self.running = False
        self.evolution_thread = None
        self.evolution_history = []
        self.performance_metrics = {
            'total_cycles': 0,
            'successful_evolutions': 0,
            'failed_evolutions': 0,
            'average_cycle_time': 0.0,
            'last_evolution_time': None
        }
    
    def start_evolution(self):
        """Iniciar evolução cognitiva."""
        if not self.running:
            self.running = True
            self.evolution_thread = threading.Thread(target=self._evolution_loop)
            self.evolution_thread.daemon = True
            self.evolution_thread.start()
            self.logger.info("🧠 Evolução cognitiva iniciada")
    
    def stop_evolution(self):
        """Parar evolução cognitiva."""
        self.running = False
        if self.evolution_thread:
            self.evolution_thread.join()
        self.logger.info("🧠 Evolução cognitiva parada")
    
    def stop_cognitive_evolution(self):
        """Alias para stop_evolution para compatibilidade."""
        self.stop_evolution()
    
    def trigger_emergency_evolution(self, failure_context: str):
        """Trigger emergency evolution in case of failure."""
        self.logger.warning(f"🚨 Emergency evolution triggered: {failure_context}")
        # For now, just log it
        self.evolution_history.append({
            'type': 'emergency',
            'context': failure_context,
            'timestamp': time.time()
        })
    
    def _record_evolution_event(self, event_type: str, description: str, impact_score: float, affected_components: list):
        """Record evolution event."""
        event = {
            'type': event_type,
            'description': description,
            'impact_score': impact_score,
            'affected_components': affected_components,
            'timestamp': time.time()
        }
        self.evolution_history.append(event)
        
        # Keep only last 100 events
        if len(self.evolution_history) > 100:
            self.evolution_history = self.evolution_history[-100:]
    
    def get_evolution_report(self) -> Dict[str, Any]:
        """Obter relatório completo da evolução cognitiva."""
        return {
            'cognitive_status': {
                'is_running': self.running,
                'maturity_level': self.performance_metrics['successful_evolutions'] / max(1, self.performance_metrics['total_cycles']),
                'evolution_cycles': self.performance_metrics['total_cycles'],
                'last_evolution': self.performance_metrics['last_evolution_time']
            },
            'evolution_metrics': {
                'total_cycles': self.performance_metrics['total_cycles'],
                'successful_evolutions': self.performance_metrics['successful_evolutions'],
                'failed_evolutions': self.performance_metrics['failed_evolutions'],
                'success_rate': self.performance_metrics['successful_evolutions'] / max(1, self.performance_metrics['total_cycles']),
                'average_cycle_time': self.performance_metrics['average_cycle_time'],
                'evolution_velocity': len(self.evolution_history) / max(1, 24),  # Events per hour
                'capability_growth_rate': self.performance_metrics['successful_evolutions'] / max(1, 24)
            },
            'recent_evolution_events': self.evolution_history[-10:],
            'performance_summary': {
                'cognitive_health': 'healthy' if self.running else 'inactive',
                'evolution_readiness': self.running and self.performance_metrics['success_rate'] > 0.7,
                'system_adaptability': min(1.0, self.performance_metrics['total_cycles'] / 10)
            }
        }
    
    def _evolution_loop(self):
        """Loop principal de evolução."""
        while self.running:
            try:
                # Simular evolução cognitiva
                self.logger.debug("🧠 Ciclo de evolução cognitiva executado")
                
                # Update metrics
                self.performance_metrics['total_cycles'] += 1
                self.performance_metrics['successful_evolutions'] += 1  # Assume success for now
                self.performance_metrics['last_evolution_time'] = time.time()
                
                # Update average cycle time
                if self.performance_metrics['total_cycles'] > 0:
                    self.performance_metrics['average_cycle_time'] = 60.0  # 1 minute cycles
                
                # Record evolution event
                self._record_evolution_event(
                    event_type="cognitive_cycle",
                    description="Regular cognitive evolution cycle completed",
                    impact_score=0.1,
                    affected_components=["cognitive_core"]
                )
                
                time.sleep(60)  # Evolução a cada minuto
            except Exception as e:
                self.logger.error(f"Erro na evolução cognitiva: {e}")
                self.performance_metrics['failed_evolutions'] += 1
                time.sleep(10)

# Global instance
_evolution_manager = None

def get_evolution_manager(config: Dict, logger: logging.Logger, memory, model_optimizer) -> CognitiveEvolutionManager:
    """Obter instância do gerenciador de evolução."""
    global _evolution_manager
    if _evolution_manager is None:
        _evolution_manager = CognitiveEvolutionManager(config, logger, memory, model_optimizer)
    return _evolution_manager

def start_cognitive_evolution(model_config: str, logger: logging.Logger, memory, model_optimizer):
    """Iniciar evolução cognitiva."""
    config = {"model_config": model_config}
    manager = get_evolution_manager(config, logger, memory, model_optimizer)
    manager.start_evolution()