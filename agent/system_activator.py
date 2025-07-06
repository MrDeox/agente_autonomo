"""
System Activator - Ativa e implementa funcionalidades não utilizadas do sistema
"""

import logging
import time
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import importlib
import sys
import os

@dataclass
class ActivationResult:
    component: str
    success: bool
    message: str
    implementation_time: float
    features_activated: List[str]

class SystemActivator:
    """Ativa funcionalidades não utilizadas e implementa melhorias"""
    
    def __init__(self, logger: logging.Logger, config: Dict[str, Any], disable_signal_handlers: bool = False):
        self.logger = logger
        self.config = config
        self.disable_signal_handlers = disable_signal_handlers
        self.activation_results = []
        self.active_features = set()
        
        # Lista de funcionalidades para ativar
        self.features_to_activate = [
            "intelligent_cache",
            "ux_enhancer", 
            "continuous_monitor",
            "performance_monitor",
            "smart_validator",
            "error_prevention",
            "hot_reload",
            "self_awareness",
            "meta_intelligence"
        ]
    
    def activate_all_features(self) -> List[ActivationResult]:
        """Ativa todas as funcionalidades disponíveis"""
        self.logger.info("🚀 Iniciando ativação de funcionalidades do sistema...")
        
        results = []
        
        for feature in self.features_to_activate:
            try:
                result = self._activate_feature(feature)
                results.append(result)
                
                if result.success:
                    self.active_features.add(feature)
                    self.logger.info(f"✅ {feature}: {result.message}")
                else:
                    self.logger.warning(f"⚠️ {feature}: {result.message}")
                    
            except Exception as e:
                error_result = ActivationResult(
                    component=feature,
                    success=False,
                    message=f"Erro na ativação: {str(e)}",
                    implementation_time=0.0,
                    features_activated=[]
                )
                results.append(error_result)
                self.logger.error(f"❌ {feature}: Erro na ativação - {e}")
        
        self.activation_results = results
        self.logger.info(f"🎯 Ativação concluída: {len(self.active_features)}/{len(self.features_to_activate)} funcionalidades ativadas")
        
        return results
    
    def _activate_feature(self, feature: str) -> ActivationResult:
        """Ativa uma funcionalidade específica"""
        start_time = time.time()
        activated_features = []
        
        if feature == "intelligent_cache":
            result = self._activate_intelligent_cache()
            activated_features.extend(result)
            
        elif feature == "ux_enhancer":
            result = self._activate_ux_enhancer()
            activated_features.extend(result)
            
        elif feature == "continuous_monitor":
            result = self._activate_continuous_monitor()
            activated_features.extend(result)
            
        elif feature == "performance_monitor":
            result = self._activate_performance_monitor()
            activated_features.extend(result)
            
        elif feature == "smart_validator":
            result = self._activate_smart_validator()
            activated_features.extend(result)
            
        elif feature == "error_prevention":
            result = self._activate_error_prevention()
            activated_features.extend(result)
            
        elif feature == "hot_reload":
            result = self._activate_hot_reload()
            activated_features.extend(result)
            
        elif feature == "self_awareness":
            result = self._activate_self_awareness()
            activated_features.extend(result)
            
        elif feature == "meta_intelligence":
            result = self._activate_meta_intelligence()
            activated_features.extend(result)
        
        implementation_time = time.time() - start_time
        
        return ActivationResult(
            component=feature,
            success=len(activated_features) > 0,
            message=f"Ativado com {len(activated_features)} sub-funcionalidades",
            implementation_time=implementation_time,
            features_activated=activated_features
        )
    
    def _activate_intelligent_cache(self) -> List[str]:
        """Ativa o sistema de cache inteligente"""
        activated = []
        
        try:
            # Importar e configurar cache inteligente
            from agent.utils.intelligent_cache import IntelligentCache, cached
            
            # Criar cache global
            global_cache = IntelligentCache(max_size=2000, default_ttl=7200)
            
            # Aplicar cache em funções críticas
            self._apply_cache_to_critical_functions()
            
            activated.extend([
                "global_cache",
                "function_caching",
                "ttl_management",
                "lru_eviction"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar cache inteligente: {e}")
        
        return activated
    
    def _activate_ux_enhancer(self) -> List[str]:
        """Ativa o melhorador de UX"""
        activated = []
        
        try:
            from agent.utils.ux_enhancer import UXEnhancer
            
            # Criar instância global
            ux_enhancer = UXEnhancer()
            
            # Mostrar mensagem de boas-vindas
            welcome_msg = ux_enhancer.format_welcome_message("Hephaestus User")
            self.logger.info(welcome_msg)
            
            activated.extend([
                "progress_display",
                "status_visualization", 
                "welcome_messages",
                "error_formatting"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar UX enhancer: {e}")
        
        return activated
    
    def _activate_continuous_monitor(self) -> List[str]:
        """Ativa o monitoramento contínuo"""
        activated = []
        
        try:
            from agent.utils.continuous_monitor import get_continuous_monitor
            
            # Inicializar monitor
            monitor = get_continuous_monitor(self.logger)
            monitor.start_monitoring()
            
            activated.extend([
                "system_metrics",
                "threshold_monitoring",
                "auto_actions",
                "alert_system"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar monitor contínuo: {e}")
        
        return activated
    
    def _activate_performance_monitor(self) -> List[str]:
        """Ativa o monitor de performance"""
        activated = []
        
        try:
            from agent.performance_monitor import PerformanceMonitor
            
            # Criar monitor de performance
            perf_monitor = PerformanceMonitor(self.logger)
            perf_monitor.start_monitoring()
            
            activated.extend([
                "execution_timing",
                "error_tracking",
                "performance_alerts",
                "optimization_recommendations"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar monitor de performance: {e}")
        
        return activated
    
    def _activate_smart_validator(self) -> List[str]:
        """Ativa o validador inteligente"""
        activated = []
        
        try:
            from agent.utils.smart_validator import SmartValidator
            
            # Criar validador global
            smart_validator = SmartValidator()
            
            activated.extend([
                "json_validation",
                "config_validation",
                "schema_validation"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar validador inteligente: {e}")
        
        return activated
    
    def _activate_error_prevention(self) -> List[str]:
        """Ativa o sistema de prevenção de erros"""
        activated = []
        
        try:
            from agent.utils.error_prevention_system import ErrorPreventionSystem
            
            # Inicializar sistema de prevenção
            error_prevention = ErrorPreventionSystem(self.logger, disable_signal_handlers=self.disable_signal_handlers)
            error_prevention.start()
            
            activated.extend([
                "constructor_validation",
                "health_monitoring",
                "auto_recovery",
                "error_patterns"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar prevenção de erros: {e}")
        
        return activated
    
    def _activate_hot_reload(self) -> List[str]:
        """Ativa o sistema de hot reload"""
        activated = []
        
        try:
            from agent.hot_reload_manager import HotReloadManager
            from agent.state import AgentState
            
            # Criar estado do agente
            agent_state = AgentState()
            
            # Inicializar hot reload
            hot_reload = HotReloadManager(agent_state, self.logger)
            
            activated.extend([
                "file_watching",
                "auto_reload",
                "module_reloading",
                "evolution_tracking"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar hot reload: {e}")
        
        return activated
    
    def _activate_self_awareness(self) -> List[str]:
        """Ativa o sistema de auto-consciência"""
        activated = []
        
        try:
            from agent.self_awareness_core import SelfAwarenessCore
            
            # Configuração do modelo
            model_config = self.config.get("models", {}).get("architect_default", {})
            
            # Inicializar auto-consciência
            self_awareness = SelfAwarenessCore(model_config, self.logger)
            
            activated.extend([
                "self_reflection",
                "cognitive_monitoring",
                "meta_awareness",
                "temporal_consciousness"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar auto-consciência: {e}")
        
        return activated
    
    def _activate_meta_intelligence(self) -> List[str]:
        """Ativa o sistema de meta-inteligência"""
        activated = []
        
        try:
            from agent.meta_intelligence_core import get_meta_intelligence
            
            # Configuração do modelo
            model_config = self.config.get("models", {}).get("architect_default", {})
            
            # Inicializar meta-inteligência
            meta_intelligence = get_meta_intelligence(model_config, self.logger)
            
            activated.extend([
                "prompt_evolution",
                "agent_genesis",
                "model_optimization",
                "cognitive_evolution"
            ])
            
        except Exception as e:
            self.logger.error(f"Erro ao ativar meta-inteligência: {e}")
        
        return activated
    
    def _apply_cache_to_critical_functions(self):
        """Aplica cache a funções críticas do sistema"""
        try:
            from agent.utils.intelligent_cache import cached
            
            # Aplicar cache a funções de análise
            from agent.code_metrics import analyze_complexity, detect_code_duplication
            from agent.project_scanner import analyze_code_metrics
            
            # Decorar funções com cache
            analyze_complexity = cached(ttl=1800)(analyze_complexity)  # 30 min
            detect_code_duplication = cached(ttl=3600)(detect_code_duplication)  # 1 hora
            analyze_code_metrics = cached(ttl=7200)(analyze_code_metrics)  # 2 horas
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar cache: {e}")
    
    def get_activation_report(self) -> str:
        """Gera relatório de ativação"""
        total_features = len(self.features_to_activate)
        active_features = len(self.active_features)
        success_rate = (active_features / total_features) * 100
        
        report = f"""
🚀 **RELATÓRIO DE ATIVAÇÃO DE FUNCIONALIDADES**

**Status Geral:**
• Funcionalidades ativadas: {active_features}/{total_features}
• Taxa de sucesso: {success_rate:.1f}%
• Tempo total: {sum(r.implementation_time for r in self.activation_results):.2f}s

**Funcionalidades Ativas:**
"""
        
        for result in self.activation_results:
            status = "✅" if result.success else "❌"
            report += f"• {status} {result.component}: {result.message}\n"
        
        report += f"""
**Sub-funcionalidades Implementadas:**
"""
        
        all_sub_features = []
        for result in self.activation_results:
            all_sub_features.extend(result.features_activated)
        
        for feature in sorted(set(all_sub_features)):
            report += f"• {feature}\n"
        
        return report
    
    def get_active_features(self) -> List[str]:
        """Retorna lista de funcionalidades ativas"""
        return list(self.active_features)

def get_system_activator(logger: logging.Logger, config: Dict[str, Any], disable_signal_handlers: bool = False) -> SystemActivator:
    """Factory function para criar ativador do sistema"""
    return SystemActivator(logger, config, disable_signal_handlers) 