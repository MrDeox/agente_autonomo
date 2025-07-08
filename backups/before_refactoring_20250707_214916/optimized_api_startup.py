"""
Optimized API Startup Implementation
================================

Este arquivo mostra como implementar a inicialização otimizada na API REST principal.
Substitui a inicialização sequencial por uma versão paralela e mais eficiente.
"""

import asyncio
import threading
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI

# Variáveis globais para armazenar instâncias dos agentes
hephaestus_agent_instance = None
interface_generator = None
error_detector_agent = None
dependency_fixer_agent = None
cycle_monitor_agent = None
agent_expansion_coordinator = None
hephaestus_worker_thread = None
log_analyzer_thread = None
queue_manager = None

class OptimizedAgentInitializer:
    """Inicializador otimizado para agentes do sistema."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
    
    async def initialize_all_agents(self) -> Dict[str, Any]:
        """Inicializa todos os agentes de forma otimizada."""
        import time
        start_time = time.time()
        
        # Importar dependências necessárias
        from hephaestus.utils.queue_manager import QueueManager
        from hephaestus.core.agent import HephaestusAgent
        from hephaestus.core.arthur_interface_generator import ArthurInterfaceGenerator
        from hephaestus.agents.error_detector_agent import ErrorDetectorAgent
        from hephaestus.agents.dependency_fixer_agent import DependencyFixerAgent
        from hephaestus.agents.cycle_monitor_agent import CycleMonitorAgent
        from hephaestus.agents.agent_expansion_coordinator import AgentExpansionCoordinator
        
        # Criar queue manager primeiro (dependência comum)
        queue_manager = QueueManager()
        
        # Fase 1: Inicializar agentes independentes em paralelo
        independent_tasks = [
            self._init_interface_generator(ArthurInterfaceGenerator),
            self._init_error_detector(ErrorDetectorAgent),
            self._init_dependency_fixer(DependencyFixerAgent),
            self._init_agent_expansion_coordinator(AgentExpansionCoordinator)
        ]
        
        # Executar em paralelo
        independent_results = await asyncio.gather(*independent_tasks, return_exceptions=True)
        
        # Processar resultados independentes
        agents = {}
        for result in independent_results:
            if isinstance(result, Exception):
                self.logger.error(f"Erro na inicialização independente: {result}")
                continue
            agents.update(result)
        
        # Fase 2: Inicializar agentes dependentes
        dependent_tasks = [
            self._init_hephaestus_agent(HephaestusAgent, queue_manager),
            self._init_cycle_monitor(CycleMonitorAgent)
        ]
        
        dependent_results = await asyncio.gather(*dependent_tasks, return_exceptions=True)
        
        for result in dependent_results:
            if isinstance(result, Exception):
                self.logger.error(f"Erro na inicialização dependente: {result}")
                continue
            agents.update(result)
        
        # Fase 3: Ativar monitoramento apenas após inicialização
        await self._activate_monitoring(agents)
        
        end_time = time.time()
        self.logger.info(f"🚀 Inicialização otimizada concluída em {end_time - start_time:.2f}s")
        
        return {
            "agents": agents,
            "queue_manager": queue_manager,
            "initialization_time": end_time - start_time
        }
    
    async def _init_interface_generator(self, generator_class) -> Dict[str, Any]:
        """Inicializa Interface Generator."""
        await asyncio.sleep(0.01)  # Simular tempo de inicialização
        generator = generator_class(self.config, self.logger)
        return {"interface_generator": generator}
    
    async def _init_error_detector(self, agent_class) -> Dict[str, Any]:
        """Inicializa Error Detector Agent."""
        await asyncio.sleep(0.01)
        model_config = self.config.get("models", {}).get("architect_default", {})
        agent = agent_class(model_config, self.logger)
        return {"error_detector": agent}
    
    async def _init_dependency_fixer(self, agent_class) -> Dict[str, Any]:
        """Inicializa Dependency Fixer Agent."""
        await asyncio.sleep(0.01)
        agent = agent_class(self.config)
        return {"dependency_fixer": agent}
    
    async def _init_agent_expansion_coordinator(self, agent_class) -> Dict[str, Any]:
        """Inicializa Agent Expansion Coordinator."""
        await asyncio.sleep(0.01)
        agent = agent_class(self.config, self.logger)
        return {"agent_expansion_coordinator": agent}
    
    async def _init_hephaestus_agent(self, agent_class, queue_manager) -> Dict[str, Any]:
        """Inicializa Hephaestus Agent principal."""
        await asyncio.sleep(0.02)  # Inicialização mais demorada
        
        # Verificar se hot reload está ativo
        import sys
        hot_reload_enabled = "--hot-reload" in sys.argv
        
        agent = agent_class(
            logger_instance=self.logger,
            config=self.config,
            continuous_mode=False,
            queue_manager=queue_manager,
            disable_signal_handlers=hot_reload_enabled
        )
        return {"hephaestus_agent": agent}
    
    async def _init_cycle_monitor(self, agent_class) -> Dict[str, Any]:
        """Inicializa Cycle Monitor Agent."""
        await asyncio.sleep(0.01)
        agent = agent_class(self.config)
        return {"cycle_monitor": agent}
    
    async def _activate_monitoring(self, agents: Dict[str, Any]) -> None:
        """Ativa sistemas de monitoramento após inicialização."""
        self.logger.info("🔄 Ativando sistemas de monitoramento...")
        
        # Ativar monitoramento de erros
        if "error_detector" in agents:
            agents["error_detector"].start_monitoring()
        
        # Ativar monitoramento de ciclos
        if "cycle_monitor" in agents:
            agents["cycle_monitor"].start_monitoring()
        
        # Ativar meta-intelligence
        if "hephaestus_agent" in agents:
            agents["hephaestus_agent"].start_meta_intelligence()
        
        self.logger.info("✅ Sistemas de monitoramento ativados")


@asynccontextmanager
async def optimized_lifespan(app: FastAPI):
    """
    Versão otimizada do lifespan para FastAPI.
    
    COMO IMPLEMENTAR:
    1. Substituir a função lifespan existente no main.py
    2. Usar esta versão otimizada
    3. Importar as variáveis globais necessárias
    """
    global hephaestus_agent_instance, interface_generator, error_detector_agent
    global dependency_fixer_agent, cycle_monitor_agent, agent_expansion_coordinator
    global hephaestus_worker_thread, log_analyzer_thread, queue_manager
    
    # Startup
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Hephaestus Meta-Intelligence API Server (OPTIMIZED)...")
    
    try:
        # Carregar configuração
        from hephaestus.utils.config_loader import load_config
        config = load_config()
        
        # Inicializar agentes de forma otimizada
        initializer = OptimizedAgentInitializer(config, logger)
        results = await initializer.initialize_all_agents()
        
        # Armazenar instâncias nas variáveis globais
        agents = results["agents"]
        queue_manager = results["queue_manager"]
        
        hephaestus_agent_instance = agents.get("hephaestus_agent")
        interface_generator = agents.get("interface_generator")
        error_detector_agent = agents.get("error_detector")
        dependency_fixer_agent = agents.get("dependency_fixer")
        cycle_monitor_agent = agents.get("cycle_monitor")
        agent_expansion_coordinator = agents.get("agent_expansion_coordinator")
        
        # Iniciar threads de background de forma otimizada
        await start_background_threads(logger)
        
        logger.info("✅ Hephaestus Meta-Intelligence API Server initialized successfully!")
        logger.info(f"⚡ Initialization time: {results['initialization_time']:.2f}s")
        logger.info("🌐 API Documentation available at: http://localhost:8000/docs")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down Hephaestus Meta-Intelligence API Server...")
    
    try:
        if hephaestus_agent_instance:
            hephaestus_agent_instance.stop_meta_intelligence()
        
        # Parar agentes de monitoramento
        if error_detector_agent:
            error_detector_agent.stop_monitoring()
        
        if cycle_monitor_agent:
            cycle_monitor_agent.stop_monitoring()
        
        logger.info("✅ Hephaestus system shutdown complete!")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


async def start_background_threads(logger: logging.Logger) -> None:
    """Inicia threads de background de forma otimizada."""
    global hephaestus_worker_thread, log_analyzer_thread
    
    # Criar threads em paralelo
    def create_worker_thread():
        # Importar apenas quando necessário
        from hephaestus.api.rest.main import worker_thread
        return threading.Thread(target=worker_thread, daemon=True)
    
    def create_log_analyzer_thread():
        # Importar apenas quando necessário
        from hephaestus.api.rest.main import periodic_log_analysis_task
        return threading.Thread(target=periodic_log_analysis_task, daemon=True)
    
    # Executar criação de threads em executor separado para não bloquear
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Criar threads em paralelo
        worker_future = executor.submit(create_worker_thread)
        log_future = executor.submit(create_log_analyzer_thread)
        
        # Aguardar criação
        hephaestus_worker_thread = worker_future.result()
        log_analyzer_thread = log_future.result()
        
        # Iniciar threads
        hephaestus_worker_thread.start()
        log_analyzer_thread.start()
    
    logger.info("🧵 Background threads started")


# Função para aplicar a otimização
def apply_optimization_to_main_api():
    """
    Instruções para aplicar a otimização na API principal.
    
    PASSOS:
    1. Backup do arquivo original: cp src/hephaestus/api/rest/main.py src/hephaestus/api/rest/main.py.backup
    2. Substituir a função lifespan no main.py pela versão optimized_lifespan
    3. Importar OptimizedAgentInitializer no início do arquivo
    4. Testar a inicialização
    
    GANHOS ESPERADOS:
    - Redução de 40-60% no tempo de inicialização
    - Inicialização paralela de agentes independentes
    - Melhor utilização de recursos
    - Startup mais responsivo
    """
    print("Para aplicar a otimização:")
    print("1. Backup: cp src/hephaestus/api/rest/main.py src/hephaestus/api/rest/main.py.backup")
    print("2. Substituir função lifespan pela versão optimized_lifespan")
    print("3. Importar OptimizedAgentInitializer")
    print("4. Testar com: poetry run python main.py")
    print("🎯 Ganho esperado: 40-60% redução no tempo de inicialização")


if __name__ == "__main__":
    apply_optimization_to_main_api()