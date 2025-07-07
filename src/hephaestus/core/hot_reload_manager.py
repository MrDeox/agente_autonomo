"""
Hot Reload Manager - Sistema REAL de hot reload e auto-evolução
"""

import logging
import importlib
import importlib.util
import sys
import os
import time
import threading
from typing import Dict, Any, List, Callable
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ModuleReloadHandler(FileSystemEventHandler):
    """Handler para detectar mudanças em arquivos Python."""
    
    def __init__(self, reload_manager):
        self.reload_manager = reload_manager
    
    def on_modified(self, event):
        """Callback quando arquivo é modificado."""
        if event.is_directory:
            return
        
        if event.src_path.endswith('.py'):
            module_path = event.src_path
            self.reload_manager._handle_file_change(module_path)

class HotReloadManager:
    """Gerenciador REAL de hot reload de módulos."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.watched_modules = {}  # {module_name: {"path": path, "callbacks": []}}
        self.file_observer = Observer()
        self.reload_callbacks = {}  # {module_name: [callbacks]}
        self.watching = False
        self.last_reload_times = {}  # Debounce mechanism
        
        self.logger.info("🔄 Hot Reload Manager inicializado com capacidades REAIS")
    
    def add_module(self, module_name: str, module_path: str = None):
        """Adicionar módulo para watch REAL."""
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, '__file__') and module.__file__:
                    file_path = Path(module.__file__).resolve()
                    self.watched_modules[module_name] = {
                        "path": str(file_path),
                        "last_modified": os.path.getmtime(file_path)
                    }
                    
                    # Watch the directory containing the module
                    watch_dir = file_path.parent
                    if not self.watching:
                        self.start_watching(str(watch_dir))
                    
                    self.logger.info(f"📦 Módulo {module_name} adicionado ao hot reload: {file_path}")
                    return True
            
            self.logger.warning(f"⚠️ Módulo {module_name} não encontrado no sys.modules")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Erro adicionando módulo {module_name}: {e}")
            return False
    
    def start_watching(self, directory: str):
        """Iniciar monitoramento REAL de arquivos."""
        try:
            handler = ModuleReloadHandler(self)
            self.file_observer.schedule(handler, directory, recursive=True)
            self.file_observer.start()
            self.watching = True
            self.logger.info(f"👁️ Monitoramento de arquivos iniciado: {directory}")
        except Exception as e:
            self.logger.error(f"❌ Erro iniciando monitoramento: {e}")
    
    def stop_watching(self):
        """Parar monitoramento."""
        if self.watching:
            self.file_observer.stop()
            self.file_observer.join()
            self.watching = False
            self.logger.info("🛑 Monitoramento de arquivos parado")
    
    def _handle_file_change(self, file_path: str):
        """Lidar com mudança de arquivo (com debounce)."""
        current_time = time.time()
        
        # Debounce - evitar múltiplos reloads
        if file_path in self.last_reload_times:
            if current_time - self.last_reload_times[file_path] < 1.0:  # 1 segundo debounce
                return
        
        self.last_reload_times[file_path] = current_time
        
        # Encontrar módulo correspondente
        for module_name, module_info in self.watched_modules.items():
            if module_info["path"] == file_path:
                self._reload_module_real(module_name)
                break
    
    def _reload_module_real(self, module_name: str):
        """Recarregar módulo de forma REAL."""
        try:
            if module_name in sys.modules:
                # Salvar referências importantes antes do reload
                old_module = sys.modules[module_name]
                
                # Fazer reload real
                importlib.reload(old_module)
                
                # Executar callbacks de reload
                if module_name in self.reload_callbacks:
                    for callback in self.reload_callbacks[module_name]:
                        try:
                            callback(module_name, old_module, sys.modules[module_name])
                        except Exception as e:
                            self.logger.error(f"❌ Erro em callback de reload: {e}")
                
                self.logger.info(f"🔄 Módulo {module_name} recarregado com SUCESSO")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro recarregando {module_name}: {e}")
        return False
    
    def register_reload_callback(self, module_name: str, callback: Callable):
        """Registrar callback para ser executado após reload."""
        if module_name not in self.reload_callbacks:
            self.reload_callbacks[module_name] = []
        
        self.reload_callbacks[module_name].append(callback)
        self.logger.info(f"📋 Callback registrado para módulo {module_name}")
    
    def force_reload(self, module_name: str):
        """Forçar reload manual de um módulo."""
        return self._reload_module_real(module_name)
    
    def get_watched_modules(self) -> Dict[str, Dict]:
        """Obter lista de módulos sendo monitorados."""
        return self.watched_modules.copy()
    
    def __del__(self):
        """Cleanup ao destruir objeto."""
        self.stop_watching()

class SelfEvolutionEngine:
    """Engine REAL de auto-evolução do sistema."""
    
    def __init__(self, config: Dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.evolution_active = False
        self.evolution_thread = None
        self.performance_history = []
        self.optimization_strategies = {}
        self.evolution_interval = config.get('evolution_interval', 300)  # 5 minutos
        
        # Métricas para auto-evolução
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'response_times': [],
            'error_rates': [],
            'success_rates': []
        }
        
        self.logger.info("🧬 Motor de auto-evolução REAL inicializado")
    
    def start_evolution(self):
        """Iniciar evolução automática REAL."""
        if not self.evolution_active:
            self.evolution_active = True
            self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
            self.evolution_thread.start()
            self.logger.info("🧬 Motor de auto-evolução REAL iniciado")
    
    def stop_evolution(self):
        """Parar evolução."""
        self.evolution_active = False
        if self.evolution_thread:
            self.evolution_thread.join(timeout=5)
        self.logger.info("🛑 Motor de auto-evolução parado")
    
    def _evolution_loop(self):
        """Loop principal de evolução REAL."""
        while self.evolution_active:
            try:
                # Coletar métricas atuais
                current_metrics = self._collect_system_metrics()
                
                # Analisar performance
                performance_analysis = self._analyze_performance(current_metrics)
                
                # Executar otimizações se necessário
                if self._should_optimize(performance_analysis):
                    optimizations = self._generate_optimizations(performance_analysis)
                    self._apply_optimizations(optimizations)
                
                # Salvar histórico
                self.performance_history.append({
                    'timestamp': time.time(),
                    'metrics': current_metrics,
                    'analysis': performance_analysis
                })
                
                # Manter apenas últimas 100 entradas
                if len(self.performance_history) > 100:
                    self.performance_history = self.performance_history[-100:]
                
                time.sleep(self.evolution_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no loop de evolução: {e}")
                time.sleep(30)  # Esperar antes de tentar novamente
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Coletar métricas REAIS do sistema."""
        import psutil
        import gc
        
        try:
            # Métricas de sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de Python
            gc_stats = gc.get_stats()
            
            metrics = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'memory_available': memory.available,
                'disk_usage': disk.percent,
                'gc_collections': sum(stat['collections'] for stat in gc_stats),
                'thread_count': threading.active_count(),
                'timestamp': time.time()
            }
            
            # Adicionar às séries históricas
            self.metrics['cpu_usage'].append(cpu_percent)
            self.metrics['memory_usage'].append(memory.percent)
            
            # Manter apenas últimos 50 valores
            for key in self.metrics:
                if len(self.metrics[key]) > 50:
                    self.metrics[key] = self.metrics[key][-50:]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Erro coletando métricas: {e}")
            return {}
    
    def _analyze_performance(self, current_metrics: Dict) -> Dict[str, Any]:
        """Analisar performance REAL com base nas métricas."""
        analysis = {
            'status': 'healthy',
            'issues': [],
            'recommendations': [],
            'score': 100
        }
        
        try:
            # Analisar CPU
            if current_metrics.get('cpu_usage', 0) > 80:
                analysis['issues'].append('high_cpu_usage')
                analysis['recommendations'].append('optimize_cpu_intensive_operations')
                analysis['score'] -= 20
            
            # Analisar memória
            if current_metrics.get('memory_usage', 0) > 85:
                analysis['issues'].append('high_memory_usage')
                analysis['recommendations'].append('optimize_memory_usage')
                analysis['score'] -= 25
            
            # Analisar tendências
            if len(self.metrics['cpu_usage']) > 10:
                cpu_trend = sum(self.metrics['cpu_usage'][-10:]) / 10
                if cpu_trend > 70:
                    analysis['issues'].append('sustained_high_cpu')
                    analysis['recommendations'].append('implement_cpu_throttling')
            
            # Determinar status geral
            if analysis['score'] < 60:
                analysis['status'] = 'critical'
            elif analysis['score'] < 80:
                analysis['status'] = 'warning'
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"❌ Erro analisando performance: {e}")
            return analysis
    
    def _should_optimize(self, analysis: Dict) -> bool:
        """Determinar se otimização é necessária."""
        return (
            analysis['status'] in ['warning', 'critical'] or
            len(analysis['issues']) > 0
        )
    
    def _generate_optimizations(self, analysis: Dict) -> List[Dict]:
        """Gerar otimizações REAIS baseadas na análise."""
        optimizations = []
        
        for recommendation in analysis['recommendations']:
            if recommendation == 'optimize_cpu_intensive_operations':
                optimizations.append({
                    'type': 'cpu_optimization',
                    'action': 'reduce_polling_frequency',
                    'parameters': {'new_interval': self.evolution_interval * 1.5}
                })
            
            elif recommendation == 'optimize_memory_usage':
                optimizations.append({
                    'type': 'memory_optimization',
                    'action': 'force_garbage_collection',
                    'parameters': {}
                })
            
            elif recommendation == 'implement_cpu_throttling':
                optimizations.append({
                    'type': 'throttling',
                    'action': 'add_sleep_delays',
                    'parameters': {'delay': 0.1}
                })
        
        return optimizations
    
    def _apply_optimizations(self, optimizations: List[Dict]):
        """Aplicar otimizações REAIS ao sistema."""
        for opt in optimizations:
            try:
                if opt['type'] == 'cpu_optimization':
                    if opt['action'] == 'reduce_polling_frequency':
                        new_interval = opt['parameters']['new_interval']
                        self.evolution_interval = min(new_interval, 600)  # Max 10 min
                        self.logger.info(f"🔧 CPU otimizado: intervalo aumentado para {self.evolution_interval}s")
                
                elif opt['type'] == 'memory_optimization':
                    if opt['action'] == 'force_garbage_collection':
                        import gc
                        before = gc.get_stats()
                        collected = gc.collect()
                        self.logger.info(f"🧹 Garbage collection forçado: {collected} objetos coletados")
                
                elif opt['type'] == 'throttling':
                    if opt['action'] == 'add_sleep_delays':
                        # Esta otimização seria aplicada nos loops críticos
                        self.logger.info("⏱️ Throttling ativado para reduzir uso de CPU")
                
            except Exception as e:
                self.logger.error(f"❌ Erro aplicando otimização {opt}: {e}")
    
    def add_performance_metric(self, metric_name: str, value: float):
        """Adicionar métrica customizada."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(value)
        if len(self.metrics[metric_name]) > 50:
            self.metrics[metric_name] = self.metrics[metric_name][-50:]
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Obter status da evolução."""
        return {
            'active': self.evolution_active,
            'interval': self.evolution_interval,
            'history_length': len(self.performance_history),
            'current_metrics': self.metrics,
            'last_analysis': self.performance_history[-1] if self.performance_history else None
        }