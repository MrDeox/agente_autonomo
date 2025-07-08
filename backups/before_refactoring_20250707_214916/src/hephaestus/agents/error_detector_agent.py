"""
Error Detector Agent - Agente de detecção de erros
"""

import logging
from typing import Dict, Any, List

class ErrorDetectorAgent:
    """Agente especializado em detectar erros."""
    
    def __init__(self, model_config: str, logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.detected_errors = []
        
        self.logger.info("🔍 ErrorDetectorAgent inicializado")
    
    def detect_errors(self, code: str) -> List[Dict]:
        """Detectar erros no código."""
        errors = []
        
        # Detecção básica de erros
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if 'import' in line and 'undefined' in line:
                errors.append({
                    'line': i + 1,
                    'type': 'import_error',
                    'message': 'Módulo não definido'
                })
        
        return errors
    
    def start_monitoring(self):
        """Iniciar monitoramento de erros."""
        self.logger.info("🔍 Monitoramento de erros iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento de erros."""
        self.logger.info("🛑 Monitoramento de erros parado")
    
    def process_error(self, error_message: str, error_context: Dict[str, Any]):
        """Processar um erro detectado."""
        error_entry = {
            'message': error_message,
            'context': error_context,
            'timestamp': error_context.get('timestamp'),
            'url': error_context.get('url'),
            'method': error_context.get('method')
        }
        
        self.detected_errors.append(error_entry)
        
        # Log do erro
        self.logger.warning(f"🔍 Erro detectado: {error_message}")
        
        # Manter apenas os últimos 100 erros
        if len(self.detected_errors) > 100:
            self.detected_errors = self.detected_errors[-100:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Obter resumo dos erros detectados."""
        return {
            'total_errors': len(self.detected_errors),
            'error_types': {},
            'recent_errors': self.detected_errors[-5:] if self.detected_errors else []
        }