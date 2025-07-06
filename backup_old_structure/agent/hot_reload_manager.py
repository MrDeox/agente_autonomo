"""
🔄 Hot Reload Manager - Sistema de Auto-Atualização em Tempo Real
Permite que o Hephaestus evolua e se atualize automaticamente sem reiniciar
"""

import os
import sys
import importlib
import threading
import time
import logging
from typing import Dict, Set, Callable, Any, Optional
from pathlib import Path
import inspect
import ast
import types

from agent.state import AgentState

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️ watchdog not installed. Run: pip install watchdog")

class HotReloadManager:
    """Sistema de hot reload para evolução em tempo real"""
    
    def __init__(self, agent_state: AgentState, logger: logging.Logger, base_path: str = None):
        self.agent_state = agent_state
        self.logger = logger
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.observers = []
        self.module_cache = {}
        self.reload_callbacks = {}
        self.auto_evolution_enabled = True
        self.evolution_history = []
        self.active_modules = set()
        self.reload_lock = threading.Lock()
        
    def start_hot_reload(self):
        """Iniciar monitoramento de arquivos para hot reload"""
        self.logger.info("🔄 Starting Hot Reload Manager...")
        
        if not WATCHDOG_AVAILABLE:
            self.logger.warning("❌ Watchdog not available. Install with: pip install watchdog")
            return False
        
        # Monitorar diretório agent
        agent_handler = AgentFileHandler(self)
        agent_observer = Observer()
        agent_observer.schedule(agent_handler, self.base_path, recursive=True)
        agent_observer.start()
        self.observers.append(agent_observer)
        
        # Monitorar diretório tools
        tools_path = os.path.join(os.path.dirname(self.base_path), "tools")
        if os.path.exists(tools_path):
            tools_handler = ToolsFileHandler(self)
            tools_observer = Observer()
            tools_observer.schedule(tools_handler, tools_path, recursive=True)
            tools_observer.start()
            self.observers.append(tools_observer)
        
        # Monitorar config
        config_path = os.path.join(os.path.dirname(self.base_path), "config")
        if os.path.exists(config_path):
            config_handler = ConfigFileHandler(self)
            config_observer = Observer()
            config_observer.schedule(config_handler, config_path, recursive=True)
            config_observer.start()
            self.observers.append(config_observer)
        
        self.logger.info("✅ Hot Reload Manager active - Real-time evolution enabled!")
        return True
        
    def stop_hot_reload(self):
        """Parar monitoramento de hot reload"""
        self.logger.info("🛑 Stopping Hot Reload Manager...")
        for observer in self.observers:
            observer.stop()
            observer.join()
        self.observers.clear()
        
    def reload_module(self, module_path: str, force: bool = False):
        """Recarregar módulo específico"""
        with self.reload_lock:
            try:
                # Converter path para module name
                module_name = self._path_to_module_name(module_path)
                
                if not module_name:
                    return False
                
                self.logger.info(f"🔄 Reloading module: {module_name}")
                
                # Backup do módulo atual
                old_module = sys.modules.get(module_name)
                
                # Recarregar módulo
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                
                # Executar callbacks de reload
                if module_name in self.reload_callbacks:
                    for callback in self.reload_callbacks[module_name]:
                        try:
                            callback(sys.modules[module_name], old_module)
                        except Exception as e:
                            self.logger.error(f"❌ Error in reload callback: {e}")
                
                # Registrar evolução
                self.evolution_history.append({
                    "timestamp": time.time(),
                    "module": module_name,
                    "type": "hot_reload",
                    "success": True
                })
                
                self.logger.info(f"✅ Module {module_name} reloaded successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Failed to reload module {module_path}: {e}")
                
                # Registrar falha
                self.evolution_history.append({
                    "timestamp": time.time(),
                    "module": module_path,
                    "type": "hot_reload",
                    "success": False,
                    "error": str(e)
                })
                return False
    
    def register_reload_callback(self, module_name: str, callback: Callable):
        """Registrar callback para quando módulo for recarregado"""
        if module_name not in self.reload_callbacks:
            self.reload_callbacks[module_name] = []
        self.reload_callbacks[module_name].append(callback)
        
    def self_modify_code(self, module_name: str, new_code: str):
        """Permitir que o sistema modifique seu próprio código"""
        try:
            # Encontrar arquivo do módulo
            module_file = self._find_module_file(module_name)
            if not module_file:
                self.logger.error(f"❌ Module file not found: {module_name}")
                return False
            
            # Validar sintaxe do novo código
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                self.logger.error(f"❌ Syntax error in new code: {e}")
                return False
            
            # Backup do código atual
            backup_path = f"{module_file}.backup.{int(time.time())}"
            with open(module_file, 'r') as f:
                old_code = f.read()
            
            with open(backup_path, 'w') as f:
                f.write(old_code)
            
            # Escrever novo código
            with open(module_file, 'w') as f:
                f.write(new_code)
            
            self.logger.info(f"🔄 Self-modified code for module: {module_name}")
            self.logger.info(f"📁 Backup saved to: {backup_path}")
            
            # Recarregar módulo automaticamente
            time.sleep(0.1)  # Dar tempo para o file watcher detectar
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to self-modify code: {e}")
            return False
    
    def dynamic_import(self, code: str, module_name: str = None):
        """Importar código dinamicamente em tempo de execução"""
        try:
            # Criar módulo temporário
            temp_module_name = module_name or f"dynamic_module_{int(time.time())}"
            
            # Compilar código
            compiled_code = compile(code, f"<{temp_module_name}>", "exec")
            
            # Criar módulo
            module = types.ModuleType(temp_module_name)
            module.__file__ = f"<dynamic:{temp_module_name}>"
            
            # Executar código no módulo
            exec(compiled_code, module.__dict__)
            
            # Adicionar ao sys.modules
            sys.modules[temp_module_name] = module
            
            self.logger.info(f"✅ Dynamic module imported: {temp_module_name}")
            
            return module
            
        except Exception as e:
            self.logger.error(f"❌ Failed to import dynamic code: {e}")
            return None
    
    def get_evolution_status(self):
        """Obter status da evolução em tempo real"""
        return {
            "hot_reload_active": len(self.observers) > 0,
            "monitored_paths": len(self.observers),
            "evolution_history": self.evolution_history[-10:],  # Últimas 10 evoluções
            "active_modules": len(self.active_modules),
            "reload_callbacks": len(self.reload_callbacks),
            "auto_evolution_enabled": self.auto_evolution_enabled,
            "watchdog_available": WATCHDOG_AVAILABLE
        }
    
    def enable_auto_evolution(self):
        """Habilitar evolução automática"""
        self.auto_evolution_enabled = True
        self.logger.info("🧬 Auto-evolution enabled!")
    
    def disable_auto_evolution(self):
        """Desabilitar evolução automática"""
        self.auto_evolution_enabled = False
        self.logger.info("⏸️ Auto-evolution disabled!")
    
    def _path_to_module_name(self, file_path: str) -> Optional[str]:
        """Converter path do arquivo para nome do módulo"""
        try:
            # Normalizar path
            file_path = os.path.abspath(file_path)
            
            # Encontrar root do projeto
            project_root = os.path.dirname(self.base_path)
            
            # Calcular path relativo
            rel_path = os.path.relpath(file_path, project_root)
            
            # Converter para module name
            if rel_path.endswith('.py'):
                rel_path = rel_path[:-3]  # Remove .py
            
            module_name = rel_path.replace(os.sep, '.')
            
            return module_name if module_name != '__init__' else None
            
        except Exception as e:
            self.logger.error(f"❌ Error converting path to module name: {e}")
            return None
    
    def _find_module_file(self, module_name: str) -> Optional[str]:
        """Encontrar arquivo do módulo"""
        try:
            # Converter module name para path
            module_path = module_name.replace('.', os.sep) + '.py'
            project_root = os.path.dirname(self.base_path)
            full_path = os.path.join(project_root, module_path)
            
            if os.path.exists(full_path):
                return full_path
            
            # Tentar __init__.py
            init_path = os.path.join(project_root, module_name.replace('.', os.sep), '__init__.py')
            if os.path.exists(init_path):
                return init_path
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding module file: {e}")
            return None


if WATCHDOG_AVAILABLE:
    class BaseFileChangeHandler(FileSystemEventHandler):
        def __init__(self, hot_reload_manager: HotReloadManager):
            self.hot_reload_manager = hot_reload_manager
            self.logger = hot_reload_manager.logger
            self.agent_state = hot_reload_manager.agent_state

        def on_modified(self, event):
            if event.is_directory or not event.src_path.endswith('.py'):
                return
            
            # The core logic: check if the agent is modifying itself.
            if self.agent_state.is_self_modifying:
                self.logger.info(f"🧬 Agent self-modification detected for {event.src_path}. Triggering dynamic reload.")
                time.sleep(0.5) # Give file time to be fully written
                self.hot_reload_manager.reload_module(event.src_path)
            else:
                self.logger.info(f"🔧 Manual file change detected for {event.src_path}. Allowing uvicorn to handle reload.")
                # By doing nothing, we let the default uvicorn reloader take over.
                pass

    class AgentFileHandler(BaseFileChangeHandler):
        """Handler for files in the agent directory."""
        pass # Logic is handled by the base class

    class ToolsFileHandler(BaseFileChangeHandler):
        """Handler for files in the tools directory."""
        pass # Logic is handled by the base class

    class ConfigFileHandler(FileSystemEventHandler):
        """Handler para arquivos de configuração (não aciona reload de código)."""
        
        def __init__(self, hot_reload_manager: HotReloadManager):
            self.hot_reload_manager = hot_reload_manager
            self.logger = hot_reload_manager.logger
        
        def on_modified(self, event):
            if event.is_directory:
                return
            
            if event.src_path.endswith(('.yaml', '.yml', '.json')):
                self.logger.info(f"⚙️ Config file modified: {event.src_path}")
                self.logger.info("📄 Configuration change detected. Manual restart may be needed to apply some changes.")
                # For now, just logs. A more advanced version could trigger specific config reload callbacks.


class SelfEvolutionEngine:
    """Engine para auto-evolução do sistema"""
    
    def __init__(self, hot_reload_manager: HotReloadManager):
        self.hot_reload_manager = hot_reload_manager
        self.logger = hot_reload_manager.logger
        self.evolution_patterns = []
        self.learning_database = {}
        
    def analyze_performance_and_evolve(self):
        """Analisar performance e evoluir automaticamente"""
        try:
            self.logger.info("🧬 Analyzing system performance for auto-evolution...")
            
            # Coletar métricas
            metrics = self._collect_performance_metrics()
            
            # Identificar gargalos
            bottlenecks = self._identify_bottlenecks(metrics)
            
            # Gerar otimizações
            optimizations = self._generate_optimizations(bottlenecks)
            
            # Aplicar otimizações
            for optimization in optimizations:
                self._apply_optimization(optimization)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error in auto-evolution: {e}")
            return False
    
    def _collect_performance_metrics(self):
        """Coletar métricas de performance"""
        # Implementar coleta de métricas
        return {
            "cpu_usage": 0.1,
            "memory_usage": 0.2,
            "response_time": 0.001,
            "error_rate": 0.0
        }
    
    def _identify_bottlenecks(self, metrics):
        """Identificar gargalos de performance"""
        bottlenecks = []
        
        if metrics["cpu_usage"] > 0.8:
            bottlenecks.append("high_cpu")
        
        if metrics["memory_usage"] > 0.9:
            bottlenecks.append("high_memory")
        
        if metrics["response_time"] > 1.0:
            bottlenecks.append("slow_response")
        
        return bottlenecks
    
    def _generate_optimizations(self, bottlenecks):
        """Gerar otimizações baseadas nos gargalos"""
        optimizations = []
        
        for bottleneck in bottlenecks:
            if bottleneck == "high_cpu":
                optimizations.append({
                    "type": "cpu_optimization",
                    "action": "add_caching",
                    "target": "agent.llm_client"
                })
            elif bottleneck == "high_memory":
                optimizations.append({
                    "type": "memory_optimization",
                    "action": "optimize_storage",
                    "target": "agent.memory"
                })
        
        return optimizations
    
    def _apply_optimization(self, optimization):
        """Aplicar otimização específica"""
        try:
            self.logger.info(f"🔧 Applying optimization: {optimization['type']}")
            
            # Aqui seria implementada a lógica específica de cada otimização
            # Por exemplo, modificar código para adicionar cache
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error applying optimization: {e}")
            return False 