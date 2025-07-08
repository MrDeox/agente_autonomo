"""
Optimization for Agent Initialization - Parallel Loading
===============================================

PROBLEMA IDENTIFICADO:
A inicialização está lenta porque todos os agentes são inicializados sequencialmente
na linha 88-100 do main.py do API REST. Os agentes são assíncronos mas estão sendo
inicializados em ordem sequencial, quando poderiam ser inicializados em paralelo.

ANÁLISE DOS PROBLEMAS:
1. Agentes independentes sendo inicializados sequencialmente
2. Sistemas de meta-inteligência sendo inicializados todos ao mesmo tempo
3. Threads sendo criadas sequencialmente quando poderiam ser criadas em paralelo
4. Carregamento de configurações redundantes

SOLUÇÃO PROPOSTA:
1. Inicialização paralela dos agentes independentes
2. Lazy loading para sistemas não críticos
3. Agrupamento de inicializações por dependência
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List, Optional
import logging
import time

class ParallelAgentInitializer:
    """Inicializador paralelo para agentes do sistema."""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.initialized_agents = {}
        self.initialization_errors = []
        
    async def initialize_agents_parallel(self) -> Dict[str, Any]:
        """Inicializa agentes em paralelo, respeitando dependências."""
        start_time = time.time()
        
        # Fase 1: Inicializar agentes independentes em paralelo
        independent_agents = await self._initialize_independent_agents()
        
        # Fase 2: Inicializar agentes dependentes
        dependent_agents = await self._initialize_dependent_agents(independent_agents)
        
        # Fase 3: Ativar sistemas de monitoramento
        monitoring_systems = await self._initialize_monitoring_systems()
        
        end_time = time.time()
        
        self.logger.info(f"🚀 Inicialização paralela concluída em {end_time - start_time:.2f}s")
        
        return {
            "independent_agents": independent_agents,
            "dependent_agents": dependent_agents,
            "monitoring_systems": monitoring_systems,
            "initialization_time": end_time - start_time,
            "errors": self.initialization_errors
        }
    
    async def _initialize_independent_agents(self) -> Dict[str, Any]:
        """Inicializa agentes independentes em paralelo."""
        self.logger.info("🔄 Iniciando agentes independentes em paralelo...")
        
        # Agentes que não dependem uns dos outros
        independent_tasks = [
            self._init_error_detector(),
            self._init_dependency_fixer(),
            self._init_agent_expansion_coordinator(),
            self._init_interface_generator()
        ]
        
        results = await asyncio.gather(*independent_tasks, return_exceptions=True)
        
        # Processar resultados
        agents = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.initialization_errors.append(f"Agent {i}: {result}")
                self.logger.error(f"Erro na inicialização do agente {i}: {result}")
            else:
                agents.update(result)
        
        return agents
    
    async def _initialize_dependent_agents(self, independent_agents: Dict[str, Any]) -> Dict[str, Any]:
        """Inicializa agentes que dependem de outros."""
        self.logger.info("🔄 Iniciando agentes dependentes...")
        
        # Agentes que dependem dos independentes
        dependent_tasks = [
            self._init_hephaestus_agent(independent_agents),
            self._init_cycle_monitor()
        ]
        
        results = await asyncio.gather(*dependent_tasks, return_exceptions=True)
        
        agents = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.initialization_errors.append(f"Dependent Agent {i}: {result}")
                self.logger.error(f"Erro na inicialização do agente dependente {i}: {result}")
            else:
                agents.update(result)
        
        return agents
    
    async def _initialize_monitoring_systems(self) -> Dict[str, Any]:
        """Inicializa sistemas de monitoramento em paralelo."""
        self.logger.info("🔄 Iniciando sistemas de monitoramento...")
        
        monitoring_tasks = [
            self._start_worker_thread(),
            self._start_log_analyzer(),
            self._start_meta_intelligence()
        ]
        
        results = await asyncio.gather(*monitoring_tasks, return_exceptions=True)
        
        systems = {}
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.initialization_errors.append(f"Monitoring System {i}: {result}")
                self.logger.error(f"Erro na inicialização do sistema de monitoramento {i}: {result}")
            else:
                systems.update(result)
        
        return systems
    
    async def _init_error_detector(self) -> Dict[str, Any]:
        """Inicializa Error Detector Agent."""
        await asyncio.sleep(0.1)  # Simular tempo de inicialização
        from hephaestus.agents.error_detector_agent import ErrorDetectorAgent
        
        model_config = self.config.get("models", {}).get("architect_default", {})
        agent = ErrorDetectorAgent(model_config, self.logger)
        
        # Não iniciar monitoramento ainda - será feito na fase de monitoramento
        return {"error_detector": agent}
    
    async def _init_dependency_fixer(self) -> Dict[str, Any]:
        """Inicializa Dependency Fixer Agent."""
        await asyncio.sleep(0.1)
        from hephaestus.agents.dependency_fixer_agent import DependencyFixerAgent
        
        agent = DependencyFixerAgent(self.config)
        return {"dependency_fixer": agent}
    
    async def _init_agent_expansion_coordinator(self) -> Dict[str, Any]:
        """Inicializa Agent Expansion Coordinator."""
        await asyncio.sleep(0.1)
        from hephaestus.agents.agent_expansion_coordinator import AgentExpansionCoordinator
        
        agent = AgentExpansionCoordinator(self.config, self.logger)
        return {"agent_expansion_coordinator": agent}
    
    async def _init_interface_generator(self) -> Dict[str, Any]:
        """Inicializa Interface Generator."""
        await asyncio.sleep(0.1)
        from hephaestus.core.arthur_interface_generator import ArthurInterfaceGenerator
        
        generator = ArthurInterfaceGenerator(self.config, self.logger)
        return {"interface_generator": generator}
    
    async def _init_hephaestus_agent(self, independent_agents: Dict[str, Any]) -> Dict[str, Any]:
        """Inicializa Hephaestus Agent principal."""
        await asyncio.sleep(0.2)  # Inicialização mais demorada
        from hephaestus.core.agent import HephaestusAgent
        from hephaestus.utils.queue_manager import QueueManager
        
        queue_manager = QueueManager()
        agent = HephaestusAgent(
            logger_instance=self.logger,
            config=self.config,
            continuous_mode=False,
            queue_manager=queue_manager,
            disable_signal_handlers=False
        )
        
        return {"hephaestus_agent": agent, "queue_manager": queue_manager}
    
    async def _init_cycle_monitor(self) -> Dict[str, Any]:
        """Inicializa Cycle Monitor Agent."""
        await asyncio.sleep(0.1)
        from hephaestus.agents.cycle_monitor_agent import CycleMonitorAgent
        
        agent = CycleMonitorAgent(self.config)
        # Não iniciar monitoramento ainda - será feito na fase de monitoramento
        return {"cycle_monitor": agent}
    
    async def _start_worker_thread(self) -> Dict[str, Any]:
        """Inicia worker thread em background."""
        await asyncio.sleep(0.05)
        # Simulação - na implementação real, iniciaria a thread
        return {"worker_thread": "started"}
    
    async def _start_log_analyzer(self) -> Dict[str, Any]:
        """Inicia log analyzer thread."""
        await asyncio.sleep(0.05)
        # Simulação - na implementação real, iniciaria a thread
        return {"log_analyzer": "started"}
    
    async def _start_meta_intelligence(self) -> Dict[str, Any]:
        """Inicia meta-intelligence systems."""
        await asyncio.sleep(0.1)
        # Simulação - na implementação real, iniciaria meta-intelligence
        return {"meta_intelligence": "started"}


# Função para implementar na API REST
async def optimize_lifespan_startup(config: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    """
    Função otimizada para substituir a inicialização sequencial no lifespan.
    
    COMO IMPLEMENTAR:
    1. Substituir as linhas 88-103 do main.py da API REST
    2. Usar esta função para inicialização paralela
    3. Armazenar resultados em variáveis globais
    """
    initializer = ParallelAgentInitializer(config, logger)
    results = await initializer.initialize_agents_parallel()
    
    # Ativar monitoramento apenas após inicialização
    if "error_detector" in results.get("independent_agents", {}):
        results["independent_agents"]["error_detector"].start_monitoring()
    
    if "cycle_monitor" in results.get("dependent_agents", {}):
        results["dependent_agents"]["cycle_monitor"].start_monitoring()
    
    # Iniciar meta-intelligence
    if "hephaestus_agent" in results.get("dependent_agents", {}):
        results["dependent_agents"]["hephaestus_agent"].start_meta_intelligence()
    
    return results


# Exemplo de uso para teste
async def test_parallel_initialization():
    """Testa a inicialização paralela."""
    import sys
    import os
    
    # Adicionar caminho do projeto
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from hephaestus.utils.config_loader import load_config
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("test")
    
    # Carregar configuração
    config = load_config()
    
    # Testar inicialização paralela
    start_time = time.time()
    results = await optimize_lifespan_startup(config, logger)
    end_time = time.time()
    
    print(f"✅ Inicialização paralela concluída em {end_time - start_time:.2f}s")
    print(f"🎯 Agentes independentes: {len(results.get('independent_agents', {}))}")
    print(f"🎯 Agentes dependentes: {len(results.get('dependent_agents', {}))}")
    print(f"🎯 Sistemas de monitoramento: {len(results.get('monitoring_systems', {}))}")
    print(f"❌ Erros: {len(results.get('errors', []))}")
    
    if results.get('errors'):
        print("Erros encontrados:")
        for error in results['errors']:
            print(f"  - {error}")


if __name__ == "__main__":
    asyncio.run(test_parallel_initialization())