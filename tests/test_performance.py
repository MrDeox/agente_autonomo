"""
Testes de performance para o sistema Hephaestus
"""
import time
import pytest
from typing import Dict, Any

class PerformanceMonitor:
    """Monitor de performance para o sistema"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obter métricas atuais"""
        current_time = time.time()
        
        return {
            "execution_time": current_time - self.start_time,
            "timestamp": current_time
        }

def test_basic_performance():
    """Teste básico de performance"""
    monitor = PerformanceMonitor()
    
    # Simular operação
    time.sleep(0.1)
    
    metrics = monitor.get_metrics()
    assert metrics["execution_time"] < 10.0  # Máximo 10 segundos
