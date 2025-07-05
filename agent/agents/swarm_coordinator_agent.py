"""
Swarm Coordinator Agent - Agente especializado em coordenação de enxame
Facilita comunicação, colaboração e resolução coletiva de problemas entre agentes
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

from agent.utils.llm_client import call_llm_with_fallback
from agent.inter_agent_communication import (
    InterAgentCommunication, AgentMessage, MessageType, 
    AgentRole, Conversation, CollaborationSession
)


@dataclass
class SwarmObjective:
    """Objetivo do enxame"""
    objective_id: str
    description: str
    complexity_level: str  # simple, moderate, complex, expert
    required_capabilities: List[str]
    estimated_duration: int  # minutos
    priority: int
    status: str = "pending"  # pending, active, completed, failed
    participants: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.participants is None:
            self.participants = []
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class SwarmMetrics:
    """Métricas do enxame"""
    total_agents: int
    active_conversations: int
    collaboration_sessions: int
    messages_per_minute: float
    average_response_time: float
    success_rate: float
    collective_intelligence_score: float


class SwarmCoordinatorAgent:
    """Agente coordenador de enxame inteligente"""
    
    def __init__(self, model_config: str, config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger.getChild("SwarmCoordinator")
        
        # Cliente LLM
        self.model_config = model_config
        
        # Sistema de comunicação
        self.communication_system = None  # Será inicializado pelo HephaestusAgent
        
        # Estado do enxame
        self.swarm_objectives: Dict[str, SwarmObjective] = {}
        self.active_collaborations: Dict[str, CollaborationSession] = {}
        self.agent_performance_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Configurações
        self.max_concurrent_objectives = config.get("swarm_coordination", {}).get("max_concurrent_objectives", 5)
        self.min_agents_per_objective = config.get("swarm_coordination", {}).get("min_agents_per_objective", 2)
        self.max_agents_per_objective = config.get("swarm_coordination", {}).get("max_agents_per_objective", 6)
        
        self.logger.info("🐝 SwarmCoordinatorAgent initialized")
    
    def set_communication_system(self, communication_system: InterAgentCommunication):
        """Define o sistema de comunicação"""
        self.communication_system = communication_system
        self.logger.info("🤝 Communication system connected")
    
    async def handle_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Processa mensagens recebidas de outros agentes"""
        try:
            self.logger.info(f"📨 Received message from {message.sender}: {message.message_type.value}")
            
            if message.message_type == MessageType.REQUEST:
                return await self._handle_request(message)
            elif message.message_type == MessageType.COLLABORATION:
                return await self._handle_collaboration(message)
            elif message.message_type == MessageType.NEGOTIATION:
                return await self._handle_negotiation(message)
            elif message.message_type == MessageType.PROBLEM_SOLVING:
                return await self._handle_problem_solving(message)
            elif message.message_type == MessageType.ERROR_REPORT:
                return await self._handle_error_report(message)
            else:
                self.logger.warning(f"⚠️ Unknown message type: {message.message_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error handling message: {e}")
            return {"error": str(e)}
    
    async def _handle_request(self, message: AgentMessage) -> Dict[str, Any]:
        """Processa solicitações de outros agentes"""
        content = message.content
        request_type = content.get("request_type")
        
        if request_type == "coordinate_objective":
            return await self.coordinate_new_objective(content.get("objective"), content.get("requesting_agent"))
        elif request_type == "resolve_conflict":
            return await self.resolve_agent_conflict(content.get("conflict_description"), content.get("involved_agents"))
        elif request_type == "optimize_collaboration":
            return await self.optimize_collaboration_strategy(content.get("session_id"))
        else:
            return {"error": f"Unknown request type: {request_type}"}
    
    async def _handle_collaboration(self, message: AgentMessage) -> Dict[str, Any]:
        """Processa mensagens de colaboração"""
        content = message.content
        action = content.get("action")
        
        if action == "progress_update":
            return await self._update_collaboration_progress(content.get("session_id"), content.get("progress"))
        elif action == "completion_notification":
            return await self._handle_collaboration_completion(content.get("session_id"), content.get("results"))
        else:
            return {"status": "acknowledged"}
    
    async def _handle_negotiation(self, message: AgentMessage) -> Dict[str, Any]:
        """Processa mensagens de negociação"""
        # Facilitar negociação entre agentes
        return await self._facilitate_negotiation(message)
    
    async def _handle_problem_solving(self, message: AgentMessage) -> Dict[str, Any]:
        """Processa mensagens de resolução de problemas"""
        # Coordenar resolução coletiva
        return await self._coordinate_problem_solving(message)
    
    async def _handle_error_report(self, message: AgentMessage) -> Dict[str, Any]:
        """Processa relatórios de erro"""
        content = message.content
        error_description = content.get("error_description")
        agent_name = message.sender
        
        self.logger.warning(f"⚠️ Error reported by {agent_name}: {error_description}")
        
        # Registrar erro no histórico
        if agent_name not in self.agent_performance_history:
            self.agent_performance_history[agent_name] = []
        
        self.agent_performance_history[agent_name].append({
            "timestamp": datetime.now(),
            "type": "error",
            "description": error_description,
            "severity": content.get("severity", "medium")
        })
        
        # Tentar resolver automaticamente se possível
        return await self._attempt_error_resolution(agent_name, error_description)
    
    async def coordinate_new_objective(self, objective_description: str, requesting_agent: str) -> Dict[str, Any]:
        """Coordena um novo objetivo do enxame"""
        try:
            self.logger.info(f"🎯 Coordinating new objective: {objective_description}")
            
            # Analisar complexidade do objetivo
            complexity_analysis = await self._analyze_objective_complexity(objective_description)
            
            # Identificar agentes necessários
            required_capabilities = complexity_analysis.get("required_capabilities", [])
            suitable_agents = await self._identify_suitable_agents(required_capabilities)
            
            if len(suitable_agents) < self.min_agents_per_objective:
                return {
                    "success": False,
                    "error": f"Insufficient agents. Need at least {self.min_agents_per_objective}, found {len(suitable_agents)}"
                }
            
            # Criar objetivo do enxame
            objective_id = f"swarm_obj_{int(time.time())}"
            swarm_objective = SwarmObjective(
                objective_id=objective_id,
                description=objective_description,
                complexity_level=complexity_analysis.get("complexity_level", "moderate"),
                required_capabilities=required_capabilities,
                estimated_duration=complexity_analysis.get("estimated_duration", 30),
                priority=complexity_analysis.get("priority", 5),
                participants=suitable_agents
            )
            
            self.swarm_objectives[objective_id] = swarm_objective
            
            # Iniciar sessão de colaboração
            if self.communication_system:
                collaboration_result = await self.communication_system.create_collaboration_session(
                    objective_description,
                    suitable_agents,
                    await self._assign_roles(suitable_agents, complexity_analysis)
                )
                
                # Iniciar conversa de coordenação
                conversation_id = await self.communication_system.start_conversation(
                    requesting_agent,
                    suitable_agents,
                    f"Swarm Objective: {objective_description}",
                    f"Let's work together to accomplish this objective. I'll coordinate our efforts."
                )
                
                return {
                    "success": True,
                    "objective_id": objective_id,
                    "session_id": collaboration_result.get("session_id"),
                    "conversation_id": conversation_id,
                    "participants": suitable_agents,
                    "estimated_duration": swarm_objective.estimated_duration
                }
            
            return {"success": False, "error": "Communication system not available"}
            
        except Exception as e:
            self.logger.error(f"❌ Error coordinating objective: {e}")
            return {"success": False, "error": str(e)}
    
    async def resolve_agent_conflict(self, conflict_description: str, involved_agents: List[str]) -> Dict[str, Any]:
        """Resolve conflitos entre agentes"""
        try:
            self.logger.info(f"⚖️ Resolving conflict: {conflict_description}")
            
            if not self.communication_system:
                return {"success": False, "error": "Communication system not available"}
            
            # Iniciar processo de negociação
            negotiation_result = await self.communication_system.negotiate_solution(
                conflict_description,
                involved_agents
            )
            
            # Facilitar negociação estruturada
            facilitation_result = await self._facilitate_structured_negotiation(
                conflict_description,
                involved_agents,
                negotiation_result.get("conversation_id")
            )
            
            return {
                "success": True,
                "negotiation_session": negotiation_result,
                "facilitation_result": facilitation_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error resolving conflict: {e}")
            return {"success": False, "error": str(e)}
    
    async def optimize_collaboration_strategy(self, session_id: str) -> Dict[str, Any]:
        """Otimiza estratégia de colaboração em andamento"""
        try:
            if session_id not in self.active_collaborations:
                return {"success": False, "error": "Session not found"}
            
            session = self.active_collaborations[session_id]
            
            # Analisar progresso atual
            progress_analysis = await self._analyze_collaboration_progress(session)
            
            # Gerar otimizações
            optimizations = await self._generate_collaboration_optimizations(session, progress_analysis)
            
            # Aplicar otimizações
            if optimizations:
                await self._apply_collaboration_optimizations(session_id, optimizations)
            
            return {
                "success": True,
                "optimizations_applied": len(optimizations),
                "progress_analysis": progress_analysis
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizing collaboration: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_objective_complexity(self, objective_description: str) -> Dict[str, Any]:
        """Analisa a complexidade de um objetivo usando LLM"""
        try:
            prompt = f"""
            Analyze the complexity of this objective and determine:
            1. Complexity level (simple/moderate/complex/expert)
            2. Required capabilities
            3. Estimated duration in minutes
            4. Priority level (1-10)
            
            Objective: {objective_description}
            
            Respond in JSON format:
            {{
                "complexity_level": "moderate",
                "required_capabilities": ["code_analysis", "problem_solving"],
                "estimated_duration": 45,
                "priority": 7
            }}
            """
            
            response = await self.llm_client.call_llm(prompt)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback para análise básica
                return {
                    "complexity_level": "moderate",
                    "required_capabilities": ["general_problem_solving"],
                    "estimated_duration": 30,
                    "priority": 5
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error analyzing complexity: {e}")
            return {
                "complexity_level": "moderate",
                "required_capabilities": ["general_problem_solving"],
                "estimated_duration": 30,
                "priority": 5
            }
    
    async def _identify_suitable_agents(self, required_capabilities: List[str]) -> List[str]:
        """Identifica agentes com capacidades necessárias"""
        if not self.communication_system:
            return []
        
        suitable_agents = []
        
        for agent_name, capabilities in self.communication_system.agent_capabilities.items():
            if any(cap in capabilities for cap in required_capabilities):
                suitable_agents.append(agent_name)
        
        # Limitar número de agentes
        return suitable_agents[:self.max_agents_per_objective]
    
    async def _assign_roles(self, agents: List[str], complexity_analysis: Dict[str, Any]) -> Dict[str, AgentRole]:
        """Atribui papéis aos agentes baseado na complexidade"""
        roles = {}
        
        if len(agents) == 1:
            roles[agents[0]] = AgentRole.SPECIALIST
        elif len(agents) == 2:
            roles[agents[0]] = AgentRole.COORDINATOR
            roles[agents[1]] = AgentRole.SPECIALIST
        else:
            # Para 3+ agentes
            roles[agents[0]] = AgentRole.COORDINATOR
            roles[agents[1]] = AgentRole.SPECIALIST
            roles[agents[2]] = AgentRole.VALIDATOR
            
            # Restantes como especialistas
            for agent in agents[3:]:
                roles[agent] = AgentRole.SPECIALIST
        
        return roles
    
    async def _facilitate_structured_negotiation(self, conflict_description: str, 
                                               involved_agents: List[str], 
                                               conversation_id: str) -> Dict[str, Any]:
        """Facilita negociação estruturada"""
        try:
            prompt = f"""
            As a swarm coordinator, facilitate this conflict resolution:
            
            Conflict: {conflict_description}
            Involved agents: {involved_agents}
            
            Provide a structured negotiation approach with:
            1. Clear discussion points
            2. Decision criteria
            3. Consensus building steps
            
            Format as JSON:
            {{
                "discussion_points": ["point1", "point2"],
                "decision_criteria": ["criterion1", "criterion2"],
                "consensus_steps": ["step1", "step2"]
            }}
            """
            
            response = await self.llm_client.call_llm(prompt)
            
            try:
                negotiation_structure = json.loads(response)
                
                # Enviar estrutura para a conversa
                if self.communication_system:
                    structure_message = AgentMessage(
                        message_id=f"structure_{int(time.time())}",
                        sender="swarm_coordinator",
                        recipients=involved_agents,
                        message_type=MessageType.NEGOTIATION,
                        content={
                            "action": "provide_structure",
                            "negotiation_structure": negotiation_structure,
                            "conversation_id": conversation_id
                        },
                        conversation_id=conversation_id
                    )
                    
                    await self.communication_system.send_message(structure_message)
                
                return negotiation_structure
                
            except json.JSONDecodeError:
                return {"error": "Failed to parse negotiation structure"}
                
        except Exception as e:
            self.logger.error(f"❌ Error facilitating negotiation: {e}")
            return {"error": str(e)}
    
    async def _attempt_error_resolution(self, agent_name: str, error_description: str) -> Dict[str, Any]:
        """Tenta resolver erros automaticamente"""
        try:
            # Analisar erro
            prompt = f"""
            Analyze this agent error and suggest resolution:
            
            Agent: {agent_name}
            Error: {error_description}
            
            Provide resolution strategy in JSON:
            {{
                "error_type": "classification",
                "resolution_strategy": "strategy_description",
                "requires_intervention": true/false,
                "suggested_actions": ["action1", "action2"]
            }}
            """
            
            response = await self.llm_client.call_llm(prompt)
            
            try:
                resolution = json.loads(response)
                
                if not resolution.get("requires_intervention", True):
                    # Tentar resolução automática
                    return await self._execute_automatic_resolution(agent_name, resolution)
                else:
                    # Requer intervenção manual
                    return {
                        "resolution_type": "manual_intervention_required",
                        "analysis": resolution
                    }
                    
            except json.JSONDecodeError:
                return {"error": "Failed to parse error resolution"}
                
        except Exception as e:
            self.logger.error(f"❌ Error attempting resolution: {e}")
            return {"error": str(e)}
    
    async def _execute_automatic_resolution(self, agent_name: str, resolution: Dict[str, Any]) -> Dict[str, Any]:
        """Executa resolução automática de erro"""
        try:
            actions = resolution.get("suggested_actions", [])
            
            # Implementar ações de resolução
            results = []
            for action in actions:
                if "restart" in action.lower():
                    # Lógica para reiniciar agente
                    results.append({"action": action, "status": "executed"})
                elif "reconfigure" in action.lower():
                    # Lógica para reconfigurar
                    results.append({"action": action, "status": "executed"})
                else:
                    results.append({"action": action, "status": "not_implemented"})
            
            return {
                "resolution_type": "automatic",
                "actions_executed": results,
                "success": any(r["status"] == "executed" for r in results)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error executing automatic resolution: {e}")
            return {"error": str(e)}
    
    def get_swarm_metrics(self) -> SwarmMetrics:
        """Retorna métricas do enxame"""
        try:
            total_agents = len(self.communication_system.registered_agents) if self.communication_system else 0
            active_conversations = len([c for c in self.communication_system.conversations.values() 
                                      if c.status == "active"]) if self.communication_system else 0
            collaboration_sessions = len(self.active_collaborations)
            
            # Calcular métricas de performance
            messages_per_minute = self.communication_system.communication_metrics.get("messages_sent", 0) / 60 if self.communication_system else 0
            average_response_time = self.communication_system.communication_metrics.get("average_response_time", 0) if self.communication_system else 0
            
            # Calcular taxa de sucesso
            completed_objectives = len([obj for obj in self.swarm_objectives.values() if obj.status == "completed"])
            total_objectives = len(self.swarm_objectives)
            success_rate = completed_objectives / total_objectives if total_objectives > 0 else 0
            
            # Calcular score de inteligência coletiva
            collective_intelligence_score = self._calculate_collective_intelligence_score()
            
            return SwarmMetrics(
                total_agents=total_agents,
                active_conversations=active_conversations,
                collaboration_sessions=collaboration_sessions,
                messages_per_minute=messages_per_minute,
                average_response_time=average_response_time,
                success_rate=success_rate,
                collective_intelligence_score=collective_intelligence_score
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating swarm metrics: {e}")
            return SwarmMetrics(0, 0, 0, 0.0, 0.0, 0.0, 0.0)
    
    def _calculate_collective_intelligence_score(self) -> float:
        """Calcula score de inteligência coletiva"""
        try:
            # Fatores que contribuem para inteligência coletiva
            factors = {
                "diversity": len(set(self.communication_system.agent_capabilities.values())) if self.communication_system else 1,
                "collaboration": len(self.active_collaborations),
                "communication": self.communication_system.communication_metrics.get("conversations_started", 0) if self.communication_system else 0,
                "success_rate": len([obj for obj in self.swarm_objectives.values() if obj.status == "completed"]) / max(len(self.swarm_objectives), 1)
            }
            
            # Fórmula de inteligência coletiva
            score = (
                factors["diversity"] * 0.3 +
                factors["collaboration"] * 0.25 +
                factors["communication"] * 0.25 +
                factors["success_rate"] * 0.2
            )
            
            return min(score, 1.0)  # Normalizar para 0-1
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating collective intelligence: {e}")
            return 0.0
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Retorna status detalhado do enxame"""
        metrics = self.get_swarm_metrics()
        
        return {
            "swarm_metrics": {
                "total_agents": metrics.total_agents,
                "active_conversations": metrics.active_conversations,
                "collaboration_sessions": metrics.collaboration_sessions,
                "messages_per_minute": metrics.messages_per_minute,
                "average_response_time": metrics.average_response_time,
                "success_rate": metrics.success_rate,
                "collective_intelligence_score": metrics.collective_intelligence_score
            },
            "active_objectives": len([obj for obj in self.swarm_objectives.values() if obj.status == "active"]),
            "completed_objectives": len([obj for obj in self.swarm_objectives.values() if obj.status == "completed"]),
            "system_status": "operational" if self.communication_system else "disconnected"
        } 