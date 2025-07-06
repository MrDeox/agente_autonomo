"""
Agent Expansion Coordinator - Expande o uso de todos os agentes disponíveis

Este agente é responsável por:
1. Identificar agentes subutilizados
2. Criar oportunidades para usar agentes específicos
3. Coordenar o uso de agentes especializados
4. Otimizar a distribuição de tarefas entre agentes
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from agent.utils.llm_client import call_llm_api


class AgentExpansionCoordinator:
    """
    Coordenador que expande o uso de todos os agentes disponíveis no sistema
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.agent_usage_stats = {}
        self.expansion_opportunities = []
        
        # Lista completa de agentes disponíveis
        self.available_agents = [
            "architect_agent",
            "bug_hunter_agent", 
            "capability_gap_detector",
            "code_review_agent",
            "cycle_monitor_agent",
            "debt_hunter_agent",
            "dependency_fixer_agent",
            "error_analyzer",
            "error_correction",
            "error_detector_agent",
            "frontend_artisan_agent",
            "integrator_agent",
            "linter_agent",
            "log_analysis_agent",
            "maestro_agent",
            "model_sommelier_agent",
            "organizer_agent",
            "performance_analyzer",
            "prompt_optimizer",
            "self_reflection_agent",
            "swarm_coordinator_agent"
        ]
        
        # Agentes atualmente ativos no pool
        self.active_pool_agents = [
            "architect",
            "maestro", 
            "code_review",
            "log_analysis",
            "model_sommelier",
            "frontend_artisan",
            "bug_hunter"
        ]
        
        # Agentes especializados (fora do pool)
        self.specialized_agents = [
            "error_detector_agent",
            "dependency_fixer_agent", 
            "cycle_monitor_agent",
            "debt_hunter_agent",
            "linter_agent",
            "organizer_agent",
            "performance_analyzer",
            "prompt_optimizer",
            "self_reflection_agent",
            "swarm_coordinator_agent",
            "capability_gap_detector",
            "integrator_agent",
            "error_analyzer",
            "error_correction"
        ]
        
        self.logger.info(f"🤖 Agent Expansion Coordinator initialized with {len(self.available_agents)} total agents")
        self.logger.info(f"📊 Active pool agents: {len(self.active_pool_agents)}")
        self.logger.info(f"🔧 Specialized agents: {len(self.specialized_agents)}")
    
    def analyze_agent_utilization(self) -> Dict[str, Any]:
        """Analisa a utilização atual dos agentes"""
        analysis = {
            "total_agents": len(self.available_agents),
            "active_pool_agents": len(self.active_pool_agents),
            "specialized_agents": len(self.specialized_agents),
            "underutilized_agents": [],
            "expansion_opportunities": [],
            "recommendations": []
        }
        
        # Identificar agentes subutilizados
        underutilized = []
        for agent in self.specialized_agents:
            if agent not in self.active_pool_agents:
                underutilized.append(agent)
        
        analysis["underutilized_agents"] = underutilized
        
        # Gerar oportunidades de expansão
        opportunities = self._generate_expansion_opportunities()
        analysis["expansion_opportunities"] = opportunities
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(analysis)
        analysis["recommendations"] = recommendations
        
        return analysis
    
    def _generate_expansion_opportunities(self) -> List[Dict[str, Any]]:
        """Gera oportunidades para expandir o uso de agentes"""
        opportunities = []
        
        # Oportunidade 1: Integrar agentes especializados no pool
        opportunities.append({
            "type": "pool_integration",
            "agents": ["debt_hunter_agent", "linter_agent", "organizer_agent"],
            "description": "Integrar agentes especializados no pool principal para uso mais frequente",
            "priority": "high",
            "expected_impact": "Aumentar cobertura de análise e otimização"
        })
        
        # Oportunidade 2: Criar ciclos de auto-reflexão
        opportunities.append({
            "type": "reflection_cycle",
            "agents": ["self_reflection_agent", "performance_analyzer"],
            "description": "Implementar ciclos periódicos de auto-reflexão e análise de performance",
            "priority": "medium",
            "expected_impact": "Melhorar auto-consciência e otimização contínua"
        })
        
        # Oportunidade 3: Coordenação de swarm
        opportunities.append({
            "type": "swarm_coordination",
            "agents": ["swarm_coordinator_agent", "integrator_agent"],
            "description": "Ativar coordenação de swarm para tarefas complexas",
            "priority": "medium",
            "expected_impact": "Resolver problemas complexos com múltiplos agentes"
        })
        
        # Oportunidade 4: Detecção de gaps de capacidade
        opportunities.append({
            "type": "capability_gap_analysis",
            "agents": ["capability_gap_detector", "error_analyzer"],
            "description": "Análise contínua de gaps de capacidade e erros",
            "priority": "high",
            "expected_impact": "Identificar e preencher lacunas de funcionalidade"
        })
        
        return opportunities
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        if len(analysis["underutilized_agents"]) > 0:
            recommendations.append(f"Ativar {len(analysis['underutilized_agents'])} agentes subutilizados")
        
        if len(analysis["expansion_opportunities"]) > 0:
            recommendations.append("Implementar oportunidades de expansão identificadas")
        
        recommendations.append("Criar ciclos de rotação de agentes para uso equilibrado")
        recommendations.append("Implementar triggers automáticos para agentes especializados")
        recommendations.append("Adicionar métricas de utilização de agentes")
        
        return recommendations
    
    def create_agent_activation_plan(self) -> Dict[str, Any]:
        """Cria um plano para ativar agentes subutilizados"""
        plan = {
            "immediate_activations": [],
            "gradual_integrations": [],
            "monitoring_setup": [],
            "success_metrics": []
        }
        
        # Ativações imediatas
        plan["immediate_activations"] = [
            {
                "agent": "debt_hunter_agent",
                "trigger": "periodic_scan",
                "frequency": "every_30_minutes",
                "description": "Scan periódico de technical debt"
            },
            {
                "agent": "linter_agent", 
                "trigger": "code_changes",
                "frequency": "on_commit",
                "description": "Análise de qualidade de código"
            },
            {
                "agent": "organizer_agent",
                "trigger": "project_changes",
                "frequency": "daily",
                "description": "Reorganização de estrutura do projeto"
            }
        ]
        
        # Integrações graduais
        plan["gradual_integrations"] = [
            {
                "agent": "self_reflection_agent",
                "integration_type": "meta_cycle",
                "frequency": "every_10_cycles",
                "description": "Ciclos de auto-reflexão"
            },
            {
                "agent": "performance_analyzer",
                "integration_type": "optimization_cycle", 
                "frequency": "every_5_cycles",
                "description": "Análise de performance"
            },
            {
                "agent": "swarm_coordinator_agent",
                "integration_type": "complex_tasks",
                "frequency": "on_demand",
                "description": "Coordenação para tarefas complexas"
            }
        ]
        
        # Configuração de monitoramento
        plan["monitoring_setup"] = [
            "Métricas de utilização por agente",
            "Tempo de resposta por agente", 
            "Taxa de sucesso por agente",
            "Impacto das decisões por agente"
        ]
        
        # Métricas de sucesso
        plan["success_metrics"] = [
            "100% dos agentes utilizados pelo menos uma vez por dia",
            "Redução de 50% em agentes subutilizados",
            "Aumento de 25% na diversidade de abordagens",
            "Melhoria de 15% na qualidade das soluções"
        ]
        
        return plan
    
    def generate_agent_objectives(self) -> List[Dict[str, Any]]:
        """Gera objetivos específicos para ativar agentes subutilizados"""
        objectives = []
        
        # Objetivos para agentes especializados
        objectives.append({
            "agent": "debt_hunter_agent",
            "objective": "Procurar e documentar technical debt no projeto atual",
            "priority": 8,
            "expected_duration": "10-15 minutes"
        })
        
        objectives.append({
            "agent": "linter_agent",
            "objective": "Analisar qualidade de código e sugerir melhorias",
            "priority": 7,
            "expected_duration": "5-10 minutes"
        })
        
        objectives.append({
            "agent": "organizer_agent", 
            "objective": "Analisar estrutura do projeto e sugerir reorganizações",
            "priority": 6,
            "expected_duration": "15-20 minutes"
        })
        
        objectives.append({
            "agent": "self_reflection_agent",
            "objective": "Realizar auto-reflexão sobre o desempenho recente do sistema",
            "priority": 9,
            "expected_duration": "10-15 minutes"
        })
        
        objectives.append({
            "agent": "performance_analyzer",
            "objective": "Analisar performance dos agentes e sugerir otimizações",
            "priority": 8,
            "expected_duration": "15-20 minutes"
        })
        
        objectives.append({
            "agent": "capability_gap_detector",
            "objective": "Identificar gaps de capacidade no sistema atual",
            "priority": 7,
            "expected_duration": "10-15 minutes"
        })
        
        objectives.append({
            "agent": "swarm_coordinator_agent",
            "objective": "Coordenar múltiplos agentes para análise complexa do projeto",
            "priority": 9,
            "expected_duration": "20-30 minutes"
        })
        
        return objectives
    
    def get_expansion_status(self) -> Dict[str, Any]:
        """Retorna status da expansão de agentes"""
        analysis = self.analyze_agent_utilization()
        plan = self.create_agent_activation_plan()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.available_agents),
            "active_agents": len(self.active_pool_agents),
            "utilization_rate": f"{(len(self.active_pool_agents) / len(self.available_agents)) * 100:.1f}%",
            "underutilized_count": len(analysis["underutilized_agents"]),
            "expansion_opportunities": len(analysis["expansion_opportunities"]),
            "recommendations": analysis["recommendations"],
            "activation_plan": plan,
            "next_actions": self._get_next_actions()
        }
    
    def _get_next_actions(self) -> List[str]:
        """Retorna próximas ações recomendadas"""
        return [
            "Implementar ativação automática de agentes subutilizados",
            "Criar triggers baseados em eventos para agentes especializados",
            "Adicionar métricas de utilização ao dashboard",
            "Implementar rotação automática de agentes",
            "Criar ciclos de auto-reflexão periódicos"
        ] 