"""
Otimizador inteligente para chamadas LLM
"""
from typing import Dict, Any
import time
import logging

class LLMCallOptimizer:
    """Otimizador inteligente para chamadas LLM"""
    
    def __init__(self):
        self.call_history = []
        self.logger = logging.getLogger(__name__)
    
    def should_optimize_call(self, context: Dict[str, Any]) -> bool:
        """Decidir se deve otimizar a chamada"""
        complexity = context.get("complexity", 0.5)
        urgency = context.get("urgency", "medium")
        recent_failures = context.get("recent_failures", 0)
        
        # Otimizar se baixa complexidade e baixa urgência
        if complexity < 0.3 and urgency == "low":
            return True
        
        # Otimizar se muitas falhas recentes
        if recent_failures > 3:
            return True
        
        return False
    
    def optimize_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Otimizar prompt baseado no contexto"""
        if self.should_optimize_call(context):
            # Simplificar prompt para casos simples
            lines = prompt.split('\n')
            essential_lines = [line for line in lines if any(keyword in line.lower() 
                             for keyword in ['task', 'output', 'format', 'return'])]
            
            if len(essential_lines) < len(lines) * 0.5:
                return '\n'.join(essential_lines)
        
        return prompt
    
    def record_call_result(self, context: Dict[str, Any], success: bool, response_time: float):
        """Registrar resultado da chamada para aprendizado"""
        self.call_history.append({
            "context": context,
            "success": success,
            "response_time": response_time,
            "timestamp": time.time()
        })
        
        # Manter apenas últimas 1000 chamadas
        if len(self.call_history) > 1000:
            self.call_history = self.call_history[-1000:]
