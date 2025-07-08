"""
Inter-Agent Communication System - Sistema de comunicação entre agentes
Permite conversas diretas, colaboração e resolução coletiva de problemas
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
from collections import defaultdict, deque

from hephaestus.utils.llm_client import call_llm_with_fallback


class MessageType(Enum):
    """Tipos de mensagens entre agentes"""
    REQUEST = "request"
    RESPONSE = "response"
    COLLABORATION = "collaboration"
    NEGOTIATION = "negotiation"
    PROBLEM_SOLVING = "problem_solving"
    KNOWLEDGE_SHARE = "knowledge_share"
    STRATEGY_DISCUSSION = "strategy_discussion"
    DECISION_MAKING = "decision_making"
    ERROR_REPORT = "error_report"
    SUCCESS_REPORT = "success_report"


class AgentRole(Enum):
    """Papéis dos agentes na comunicação"""
    INITIATOR = "initiator"
    RESPONDER = "responder"
    MEDIATOR = "mediator"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    VALIDATOR = "validator"


@dataclass
class AgentMessage:
    """Mensagem entre agentes"""
    message_id: str
    sender: str
    recipients: List[str]
    message_type: MessageType
    content: Dict[str, Any]
    priority: int = 5
    timestamp: datetime = field(default_factory=datetime.now)
    requires_response: bool = True
    conversation_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.conversation_id is None:
            self.conversation_id = str(uuid.uuid4())


@dataclass
class Conversation:
    """Conversa entre múltiplos agentes"""
    conversation_id: str
    participants: List[str]
    topic: str
    messages: List[AgentMessage] = field(default_factory=list)
    status: str = "active"  # active, resolved, failed
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    outcome: Optional[Dict[str, Any]] = None


@dataclass
class CollaborationSession:
    """Sessão de colaboração para tarefas complexas"""
    session_id: str
    objective: str
    participants: List[str]
    roles: Dict[str, AgentRole]
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    progress: Dict[str, float] = field(default_factory=dict)
    status: str = "planning"  # planning, executing, reviewing, completed
    created_at: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None


class InterAgentCommunication:
    """Sistema de comunicação inter-agente"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        
        # Sistema de mensagens
        self.message_queue = asyncio.Queue()
        self.conversations: Dict[str, Conversation] = {}
        self.collaboration_sessions: Dict[str, CollaborationSession] = {}
        
        # Registro de agentes
        self.registered_agents: Dict[str, Any] = {}
        self.agent_capabilities: Dict[str, List[str]] = {}
        
        # Sistema de roteamento
        self.message_routes: Dict[str, Callable] = {}
        self.model_config = config.get("models", {}).get("architect_default", "gpt-4")
        
        # Métricas
        self.communication_metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "conversations_started": 0,
            "collaborations_completed": 0,
            "average_response_time": 0.0
        }
        
        self.logger.info("🤝 Inter-Agent Communication System initialized")
    
    def register_agent(self, agent_name: str, agent_instance: Any, capabilities: List[str]):
        """Registra um agente no sistema de comunicação"""
        self.registered_agents[agent_name] = agent_instance
        self.agent_capabilities[agent_name] = capabilities
        
        # Registrar handlers de mensagens
        if hasattr(agent_instance, 'handle_message'):
            self.message_routes[agent_name] = agent_instance.handle_message
        
        self.logger.info(f"📝 Agent '{agent_name}' registered with capabilities: {capabilities}")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Envia uma mensagem para outros agentes"""
        try:
            self.logger.info(f"📤 Sending message from {message.sender} to {message.recipients}")
            
            # Adicionar à fila de mensagens
            await self.message_queue.put(message)
            
            # Processar mensagem
            await self._process_message(message)
            
            self.communication_metrics["messages_sent"] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error sending message: {e}")
            return False
    
    async def _process_message(self, message: AgentMessage):
        """Processa uma mensagem recebida"""
        try:
            # Criar ou atualizar conversa
            if message.conversation_id not in self.conversations:
                self.conversations[message.conversation_id] = Conversation(
                    conversation_id=message.conversation_id,
                    participants=list(set([message.sender] + message.recipients)),
                    topic=message.content.get("topic", "General discussion")
                )
            
            conversation = self.conversations[message.conversation_id]
            conversation.messages.append(message)
            
            # Rotear mensagem para destinatários
            for recipient in message.recipients:
                if recipient in self.message_routes:
                    try:
                        await self.message_routes[recipient](message)
                    except Exception as e:
                        self.logger.error(f"❌ Error routing message to {recipient}: {e}")
            
            self.communication_metrics["messages_received"] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error processing message: {e}")
    
    async def start_conversation(self, initiator: str, participants: List[str], topic: str, 
                               initial_message: str) -> str:
        """Inicia uma nova conversa entre agentes"""
        conversation_id = str(uuid.uuid4())
        
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender=initiator,
            recipients=[p for p in participants if p != initiator],
            message_type=MessageType.COLLABORATION,
            content={
                "topic": topic,
                "message": initial_message,
                "conversation_id": conversation_id
            },
            conversation_id=conversation_id
        )
        
        await self.send_message(message)
        self.communication_metrics["conversations_started"] += 1
        
        self.logger.info(f"💬 Started conversation '{topic}' with {len(participants)} participants")
        return conversation_id
    
    async def create_collaboration_session(self, objective: str, participants: List[str], 
                                         roles: Dict[str, AgentRole]) -> str:
        """Cria uma sessão de colaboração para tarefas complexas"""
        session_id = str(uuid.uuid4())
        
        session = CollaborationSession(
            session_id=session_id,
            objective=objective,
            participants=participants,
            roles=roles
        )
        
        self.collaboration_sessions[session_id] = session
        
        # Notificar participantes
        notification_message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender="system",
            recipients=participants,
            message_type=MessageType.COLLABORATION,
            content={
                "action": "collaboration_started",
                "session_id": session_id,
                "objective": objective,
                "roles": {k: v.value for k, v in roles.items()}
            },
            requires_response=False
        )
        
        await self.send_message(notification_message)
        
        self.logger.info(f"🤝 Created collaboration session for: {objective}")
        return session_id
    
    async def coordinate_complex_task(self, task_description: str, 
                                    required_capabilities: List[str]) -> Dict[str, Any]:
        """Coordena uma tarefa complexa entre múltiplos agentes"""
        self.logger.info(f"🎯 Coordinating complex task: {task_description}")
        
        # Identificar agentes com capacidades necessárias
        suitable_agents = []
        for agent_name, capabilities in self.agent_capabilities.items():
            if any(cap in capabilities for cap in required_capabilities):
                suitable_agents.append(agent_name)
        
        if not suitable_agents:
            raise ValueError(f"No agents found with required capabilities: {required_capabilities}")
        
        # Criar sessão de colaboração
        roles = {}
        for i, agent in enumerate(suitable_agents):
            if i == 0:
                roles[agent] = AgentRole.COORDINATOR
            elif i == 1:
                roles[agent] = AgentRole.SPECIALIST
            else:
                roles[agent] = AgentRole.SPECIALIST
        
        session_id = await self.create_collaboration_session(
            task_description, suitable_agents, roles
        )
        
        # Iniciar conversa de coordenação
        conversation_id = await self.start_conversation(
            suitable_agents[0],  # Coordenador
            suitable_agents,
            f"Coordination for: {task_description}",
            f"Let's work together to accomplish: {task_description}. I'll coordinate our efforts."
        )
        
        return {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "participants": suitable_agents,
            "roles": {k: v.value for k, v in roles.items()}
        }
    
    async def negotiate_solution(self, problem: str, conflicting_agents: List[str]) -> Dict[str, Any]:
        """Facilita negociação entre agentes com soluções conflitantes"""
        self.logger.info(f"⚖️ Facilitating negotiation for: {problem}")
        
        # Criar sessão de negociação
        session_id = str(uuid.uuid4())
        
        # Adicionar mediador se necessário
        participants = conflicting_agents.copy()
        mediator = None
        for agent_name, capabilities in self.agent_capabilities.items():
            if "mediation" in capabilities and agent_name not in conflicting_agents:
                mediator = agent_name
                participants.append(mediator)
                break
        
        # Iniciar conversa de negociação
        conversation_id = await self.start_conversation(
            participants[0],
            participants,
            f"Negotiation: {problem}",
            f"We need to resolve conflicting approaches to: {problem}. Let's discuss and find a consensus."
        )
        
        # Enviar mensagem de negociação estruturada
        negotiation_message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender="system",
            recipients=participants,
            message_type=MessageType.NEGOTIATION,
            content={
                "problem": problem,
                "conflicting_agents": conflicting_agents,
                "mediator": mediator,
                "process": "structured_negotiation"
            },
            conversation_id=conversation_id
        )
        
        await self.send_message(negotiation_message)
        
        return {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "participants": participants,
            "mediator": mediator
        }
    
    async def collective_problem_solving(self, problem: str, 
                                       agent_perspectives: Dict[str, str]) -> Dict[str, Any]:
        """Facilita resolução coletiva de problemas"""
        self.logger.info(f"🧠 Collective problem solving for: {problem}")
        
        # Identificar agentes com perspectivas relevantes
        participants = list(agent_perspectives.keys())
        
        # Criar sessão de resolução de problemas
        session_id = str(uuid.uuid4())
        
        # Iniciar conversa estruturada
        conversation_id = await self.start_conversation(
            participants[0],
            participants,
            f"Collective Problem Solving: {problem}",
            f"Let's solve this together: {problem}. Each of us has a unique perspective to contribute."
        )
        
        # Enviar perspectivas individuais
        for agent, perspective in agent_perspectives.items():
            perspective_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender=agent,
                recipients=[p for p in participants if p != agent],
                message_type=MessageType.PROBLEM_SOLVING,
                content={
                    "problem": problem,
                    "perspective": perspective,
                    "contribution_type": "analysis"
                },
                conversation_id=conversation_id
            )
            
            await self.send_message(perspective_message)
        
        return {
            "session_id": session_id,
            "conversation_id": conversation_id,
            "participants": participants,
            "problem": problem
        }
    
    async def knowledge_sharing_session(self, topic: str, 
                                      knowledge_providers: List[str]) -> Dict[str, Any]:
        """Facilita sessão de compartilhamento de conhecimento"""
        self.logger.info(f"📚 Knowledge sharing session: {topic}")
        
        # Identificar agentes com conhecimento relevante
        participants = knowledge_providers.copy()
        
        # Adicionar agentes que podem se beneficiar do conhecimento
        for agent_name, capabilities in self.agent_capabilities.items():
            if any(cap in capabilities for cap in ["learning", "adaptation"]) and agent_name not in participants:
                participants.append(agent_name)
        
        # Iniciar sessão de conhecimento
        conversation_id = await self.start_conversation(
            participants[0],
            participants,
            f"Knowledge Sharing: {topic}",
            f"Let's share our knowledge about: {topic}. This will help us all improve."
        )
        
        # Estruturar sessão de conhecimento
        for provider in knowledge_providers:
            knowledge_message = AgentMessage(
                message_id=str(uuid.uuid4()),
                sender=provider,
                recipients=[p for p in participants if p != provider],
                message_type=MessageType.KNOWLEDGE_SHARE,
                content={
                    "topic": topic,
                    "knowledge_type": "expertise",
                    "sharing_method": "structured"
                },
                conversation_id=conversation_id
            )
            
            await self.send_message(knowledge_message)
        
        return {
            "conversation_id": conversation_id,
            "participants": participants,
            "knowledge_providers": knowledge_providers,
            "topic": topic
        }
    
    def get_communication_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de comunicação"""
        return {
            "active_conversations": len([c for c in self.conversations.values() if c.status == "active"]),
            "active_collaborations": len([s for s in self.collaboration_sessions.values() if s.status != "completed"]),
            "registered_agents": len(self.registered_agents),
            "metrics": self.communication_metrics,
            "system_status": "operational"
        }
    
    async def start_message_processor(self):
        """Inicia o processador de mensagens em background"""
        self.logger.info("🔄 Starting message processor...")
        
        while True:
            try:
                # Processar mensagens da fila
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._process_message(message)
                
                # Limpar conversas antigas
                await self._cleanup_old_conversations()
                
                await asyncio.sleep(0.1)  # Pequena pausa para não sobrecarregar
                
            except Exception as e:
                self.logger.error(f"❌ Error in message processor: {e}")
                await asyncio.sleep(1)
    
    async def _cleanup_old_conversations(self):
        """Limpa conversas antigas e finalizadas"""
        current_time = datetime.now()
        cutoff_time = current_time.replace(hour=current_time.hour - 1)  # 1 hora atrás
        
        # Marcar conversas antigas como resolvidas
        for conversation in self.conversations.values():
            if (conversation.status == "active" and 
                conversation.messages and 
                conversation.messages[-1].timestamp < cutoff_time):
                conversation.status = "resolved"
                conversation.resolved_at = current_time
                self.logger.info(f"📝 Marked conversation {conversation.conversation_id} as resolved")


# Instância global do sistema de comunicação
_inter_agent_comm = None

def get_inter_agent_communication(config: Dict[str, Any], logger: logging.Logger) -> InterAgentCommunication:
    """Retorna instância global do sistema de comunicação inter-agente"""
    global _inter_agent_comm
    if _inter_agent_comm is None:
        _inter_agent_comm = InterAgentCommunication(config, logger)
    return _inter_agent_comm 