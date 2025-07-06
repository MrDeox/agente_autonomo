"""
Agente Detector de Erros Autônomo - Sistema de Autocorreção
Monitora a API REST em tempo real e resolve erros automaticamente
"""
import logging
import re
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from agent.utils.llm_client import call_llm_api
from agent.utils.json_parser import parse_json_response

@dataclass
class ErrorPattern:
    """Representa um padrão de erro detectado"""
    pattern: str
    severity: str
    frequency: int
    last_seen: datetime
    auto_correctable: bool = False

class ErrorDetectorAgent:
    """Agente que monitora erros da API REST e implementa correções automáticas"""
    
    def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger.getChild("ErrorDetector")
        
        # Configurações de monitoramento
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Armazenamento de erros detectados
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.recent_errors = deque(maxlen=1000)
        self.error_frequency = defaultdict(int)
        
        # Padrões de erro conhecidos
        self.known_patterns = {
            r"'(\w+)' object has no attribute '(\w+)'": {
                "severity": "high",
                "type": "attribute_error",
                "auto_correctable": True
            },
            r"'dict' object has no attribute '(\w+)'": {
                "severity": "high", 
                "type": "dict_access_error",
                "auto_correctable": True
            },
            r"KeyError: '(\w+)'": {
                "severity": "medium",
                "type": "missing_key_error",
                "auto_correctable": True
            },
            r"AttributeError: (.+)": {
                "severity": "high",
                "type": "attribute_error",
                "auto_correctable": True
            },
            r"TypeError: (.+)": {
                "severity": "medium",
                "type": "type_error",
                "auto_correctable": True
            }
        }
        
        # Estatísticas
        self.stats = {
            "total_errors_detected": 0,
            "auto_corrections_attempted": 0,
            "auto_corrections_successful": 0,
            "correction_success_rate": 0.0,
            "monitoring_start_time": None
        }
        
    def start_monitoring(self) -> bool:
        """Inicia o monitoramento ativo de erros"""
        if self.monitoring_active:
            self.logger.warning("Error monitoring is already active")
            return False
            
        self.monitoring_active = True
        self.stats["monitoring_start_time"] = datetime.now()
        
        # Inicia thread de monitoramento
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("🛡️ Error Detector Agent monitoring started!")
        return True
    
    def stop_monitoring(self) -> bool:
        """Para o monitoramento de erros"""
        if not self.monitoring_active:
            return False
            
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
            
        self.logger.info("🛡️ Error Detector Agent monitoring stopped")
        return True
    
    def _monitor_loop(self):
        """Loop principal de monitoramento de erros"""
        self.logger.info("🔍 Starting error monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Por enquanto, simula monitoramento básico
                # Em implementação completa, monitoriaria logs em tempo real
                time.sleep(5)
                
                # Verifica se há padrões críticos que precisam de atenção
                self._check_critical_patterns()
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def _check_critical_patterns(self):
        """Verifica padrões críticos de erro"""
        # Implementação básica - pode ser expandida
        current_time = datetime.now()
        
        # Se houver muitos erros recentes, gera alerta
        recent_errors = [e for e in self.recent_errors 
                        if (current_time - e.get("timestamp", current_time)).total_seconds() < 300]
        
        if len(recent_errors) > 10:
            self.logger.warning(f"🚨 High error rate detected: {len(recent_errors)} errors in last 5 minutes")
    
    def process_error(self, error_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Processa um erro manualmente fornecido"""
        self.stats["total_errors_detected"] += 1
        
        # Adiciona à lista de erros recentes
        error_info = {
            "timestamp": datetime.now(),
            "error_message": error_message,
            "context": context or {},
            "severity": "unknown",
            "auto_correctable": False
        }
        
        # Verifica padrões conhecidos
        matched_pattern = None
        for pattern, pattern_info in self.known_patterns.items():
            if re.search(pattern, error_message):
                matched_pattern = pattern
                error_info["severity"] = pattern_info["severity"]
                error_info["type"] = pattern_info["type"]
                error_info["auto_correctable"] = pattern_info["auto_correctable"]
                
                # Atualiza frequência do padrão
                self.error_frequency[pattern] += 1
                
                # Atualiza padrão de erro
                if pattern not in self.error_patterns:
                    self.error_patterns[pattern] = ErrorPattern(
                        pattern=pattern,
                        severity=pattern_info["severity"],
                        frequency=1,
                        last_seen=datetime.now(),
                        auto_correctable=pattern_info["auto_correctable"]
                    )
                else:
                    self.error_patterns[pattern].frequency += 1
                    self.error_patterns[pattern].last_seen = datetime.now()
                
                break
        
        self.recent_errors.append(error_info)
        
        # Se é um erro crítico ou de alta severidade, gera correção
        if error_info.get("severity") in ["critical", "high"] and error_info.get("auto_correctable", False):
            correction = self._generate_correction_suggestion(error_info, matched_pattern)
            error_info["suggested_correction"] = correction
        
        # Log do erro processado
        severity = error_info.get("severity", "unknown")
        self.logger.info(f"🔍 Error processed [{severity}]: {error_message[:100]}...")
        
        return error_info
    
    def _generate_correction_suggestion(self, error_info: Dict[str, Any], pattern: Optional[str]) -> Optional[str]:
        """Gera sugestão de correção usando LLM"""
        try:
            self.stats["auto_corrections_attempted"] += 1
            
            prompt = f"""
You are an expert Python debugging agent. Analyze this error and provide a correction suggestion.

[ERROR INFORMATION]
Error Message: {error_info['error_message']}
Error Type: {error_info.get('type', 'unknown')}
Severity: {error_info.get('severity', 'unknown')}
Context: {error_info.get('context', {})}

[TASK]
Provide a brief, actionable correction suggestion for this error.

[OUTPUT FORMAT]
Return a concise correction suggestion (1-2 sentences):
"""
            
            response, error = call_llm_api(
                model_config=self.model_config,
                prompt=prompt,
                temperature=0.2,
                logger=self.logger
            )
            
            if not error and response:
                self.stats["auto_corrections_successful"] += 1
                return response.strip()
            else:
                self.logger.error(f"Failed to generate correction: {error}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating correction: {e}")
            return None
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Retorna o status do monitoramento"""
        return {
            "monitoring_active": self.monitoring_active,
            "stats": self.stats.copy(),
            "recent_errors_count": len(self.recent_errors),
            "error_patterns_detected": len(self.error_patterns),
            "top_error_patterns": sorted(
                self.error_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5] if self.error_frequency else [],
            "uptime_seconds": (
                datetime.now() - self.stats["monitoring_start_time"]
            ).total_seconds() if self.stats["monitoring_start_time"] else 0
        }
    
    def get_error_report(self) -> Dict[str, Any]:
        """Gera relatório detalhado de erros"""
        # Últimos 24h
        cutoff = datetime.now() - timedelta(hours=24)
        recent_24h = [e for e in self.recent_errors 
                     if e.get("timestamp", datetime.min) > cutoff]
        
        # Agrupa por severidade
        by_severity = defaultdict(int)
        for error in recent_24h:
            by_severity[error.get("severity", "unknown")] += 1
        
        return {
            "monitoring_period": "24 hours",
            "total_errors": len(recent_24h),
            "errors_by_severity": dict(by_severity),
            "auto_correctable_errors": len([e for e in recent_24h if e.get("auto_correctable", False)]),
            "correction_success_rate": (
                self.stats["auto_corrections_successful"] / 
                max(1, self.stats["auto_corrections_attempted"])
            ),
            "most_frequent_patterns": sorted(
                self.error_frequency.items(),
                key=lambda x: x[1], 
                reverse=True
            )[:10] if self.error_frequency else [],
            "error_patterns": {
                pattern: {
                    "frequency": info.frequency,
                    "severity": info.severity,
                    "last_seen": info.last_seen.isoformat(),
                    "auto_correctable": info.auto_correctable
                }
                for pattern, info in self.error_patterns.items()
            }
        }
    
    def inject_error_for_testing(self, error_message: str) -> Dict[str, Any]:
        """Injeta um erro para teste do sistema de correção"""
        self.logger.info(f"🧪 Testing error injection: {error_message}")
        return self.process_error(error_message, {"source": "test_injection"})
    
    def capture_agent_error(self, agent_name: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Captura erro específico de um agente durante execução
        """
        enhanced_context = {
            "source": "agent_execution",
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            **(context or {})
        }
        
        self.logger.warning(f"🚨 Agent Error Captured [{agent_name}]: {error_message}")
        
        # Processa o erro
        error_info = self.process_error(error_message, enhanced_context)
        
        # Se é um erro crítico, tenta gerar ação corretiva imediata
        if error_info.get("severity") in ["critical", "high"]:
            self._generate_immediate_action(agent_name, error_info)
        
        return error_info
    
    def _generate_immediate_action(self, agent_name: str, error_info: Dict[str, Any]):
        """Gera ação corretiva imediata para erros críticos"""
        try:
            # Gera objetivo de correção para a fila
            correction_objective = self._create_correction_objective(agent_name, error_info)
            
            if correction_objective:
                self.logger.info(f"🔧 Generated correction objective: {correction_objective[:100]}...")
                
                # Aqui poderia integrar com o queue_manager para adicionar o objetivo
                # Por enquanto, apenas registra a ação sugerida
                error_info["immediate_action"] = correction_objective
                
        except Exception as e:
            self.logger.error(f"Failed to generate immediate action: {e}")
    
    def _create_correction_objective(self, agent_name: str, error_info: Dict[str, Any]) -> Optional[str]:
        """Cria objetivo de correção baseado no erro"""
        error_type = error_info.get("type", "unknown")
        error_message = error_info.get("error_message", "")
        
        # Templates de correção baseados no tipo de erro
        if error_type == "attribute_error" and "object has no attribute" in error_message:
            # Extrai método faltante
            match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_message)
            if match:
                object_type, missing_method = match.groups()
                return f"[AUTO-CORRECTION] Fix AttributeError in {agent_name}: Replace '{missing_method}' with correct method name in {object_type} class"
        
        elif error_type == "dict_access_error":
            return f"[AUTO-CORRECTION] Fix dict access error in {agent_name}: Add type checking before calling string methods on dict objects"
        
        elif error_type == "missing_key_error":
            match = re.search(r"KeyError: '(\w+)'", error_message)
            if match:
                missing_key = match.groups()[0]
                return f"[AUTO-CORRECTION] Fix KeyError in {agent_name}: Add default value or validation for key '{missing_key}'"
        
        elif error_type == "type_error":
            return f"[AUTO-CORRECTION] Fix TypeError in {agent_name}: Add proper type validation and conversion for incompatible types"
        
        # Correção genérica
        return f"[AUTO-CORRECTION] Investigate and fix {error_type} in {agent_name}: {error_message[:100]}"
    
    def get_real_time_analysis(self) -> Dict[str, Any]:
        """Análise em tempo real dos erros mais recentes"""
        current_time = datetime.now()
        
        # Últimos 5 minutos
        cutoff = current_time - timedelta(minutes=5)
        recent_errors = [e for e in self.recent_errors 
                        if e.get("timestamp", datetime.min) > cutoff]
        
        # Análise de tendências
        error_trend = "stable"
        if len(recent_errors) > 15:
            error_trend = "high"
        elif len(recent_errors) > 5:
            error_trend = "rising"
        
        # Agentes com mais problemas
        agent_errors = defaultdict(int)
        for error in recent_errors:
            agent_name = error.get("context", {}).get("agent_name", "unknown")
            if agent_name != "unknown":
                agent_errors[agent_name] += 1
        
        return {
            "analysis_time": current_time.isoformat(),
            "recent_errors_5min": len(recent_errors),
            "error_trend": error_trend,
            "problematic_agents": sorted(agent_errors.items(), key=lambda x: x[1], reverse=True)[:3],
            "critical_errors": len([e for e in recent_errors if e.get("severity") == "critical"]),
            "auto_correctable_ratio": (
                len([e for e in recent_errors if e.get("auto_correctable", False)]) / 
                max(1, len(recent_errors))
            ),
            "system_health": "healthy" if error_trend == "stable" and len(recent_errors) < 5 else "degraded"
        } 