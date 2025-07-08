"""
Swarm Coordinator Agent - Coordena múltiplos agentes em enxame
"""

import logging
from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentCapability

class SwarmCoordinatorAgent(BaseAgent):
    """Agente coordenador de enxame."""
    
    def __init__(self, model_config: str, config: Dict, logger: logging.Logger):
        super().__init__(
            name="SwarmCoordinator",
            capabilities=[AgentCapability.COORDINATION, AgentCapability.ORCHESTRATION],
            logger=logger
        )
        self.config = config
        self.communication_system = None
        self.swarm_agents = []
        self.coordination_active = False
        
        self._logger.info("🐝 Swarm Coordinator Agent initialized")
    
    def set_communication_system(self, communication_system):
        """Definir sistema de comunicação."""
        self.communication_system = communication_system
        self._logger.info("🗣️ Sistema de comunicação configurado")
    
    def add_agent(self, agent):
        """Adicionar agente ao enxame."""
        self.swarm_agents.append(agent)
        self._logger.info(f"🤖 Agente adicionado ao enxame: {type(agent).__name__}")
    
    def start_coordination(self):
        """Iniciar coordenação do enxame."""
        self.coordination_active = True
        self._logger.info("🐝 Coordenação de enxame iniciada")
    
    def stop_coordination(self):
        """Parar coordenação."""
        self.coordination_active = False
        self._logger.info("🛑 Coordenação de enxame parada")
    
    def coordinate_agents(self, task: str) -> Dict[str, Any]:
        """Coordenar agentes para uma tarefa."""
        if not self.coordination_active:
            return {"status": "inactive", "message": "Coordenação não está ativa"}
        
        try:
            results = []
            for agent in self.swarm_agents:
                if hasattr(agent, 'execute'):
                    result = agent.execute(task)
                    results.append({
                        "agent": type(agent).__name__,
                        "result": result
                    })
            
            return {
                "status": "success",
                "task": task,
                "results": results,
                "agents_coordinated": len(results)
            }
        
        except Exception as e:
            self._logger.error(f"❌ Erro na coordenação: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Obter status do enxame."""
        return {
            "coordination_active": self.coordination_active,
            "total_agents": len(self.swarm_agents),
            "agent_types": [type(agent).__name__ for agent in self.swarm_agents],
            "communication_system": self.communication_system is not None
        }
    
    def execute(self, objective: str = "", context: Dict = None) -> Dict[str, Any]:
        """Executar coordenação baseada no objetivo."""
        if not objective:
            return self.get_swarm_status()
        
        return self.coordinate_agents(objective)