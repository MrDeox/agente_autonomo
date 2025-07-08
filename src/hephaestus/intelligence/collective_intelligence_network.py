"""
⚡ COLLECTIVE INTELLIGENCE NETWORK ⚡

Sistema de rede de inteligência coletiva onde agentes compartilham conhecimento,
aprendem uns com os outros e desenvolvem insights coletivos em tempo real.

É como uma "mente coletiva" onde cada agente contribui com suas experiências
e todos se beneficiam do conhecimento compartilhado.
"""

import asyncio
import logging
import time
import json
import threading
from typing import Dict, Any, List, Optional, Set, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import uuid
import hashlib
import copy
import statistics

from hephaestus.utils.config_loader import load_config
from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response


class KnowledgeType(Enum):
    """Tipos de conhecimento compartilhado"""
    SOLUTION_PATTERN = "solution_pattern"
    FAILURE_PATTERN = "failure_pattern"
    OPTIMIZATION_INSIGHT = "optimization_insight"
    STRATEGY_DISCOVERY = "strategy_discovery"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_RECOVERY = "error_recovery"
    COLLABORATION_PATTERN = "collaboration_pattern"
    INNOVATION_IDEA = "innovation_idea"


class KnowledgeRelevance(Enum):
    """Níveis de relevância do conhecimento"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DEPRECATED = "deprecated"


@dataclass
class KnowledgeItem:
    """Item de conhecimento compartilhado"""
    knowledge_id: str
    knowledge_type: KnowledgeType
    source_agent: str
    title: str
    content: str
    context: Dict[str, Any]
    relevance: KnowledgeRelevance
    confidence: float
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    validation_count: int = 0
    success_applications: int = 0
    failed_applications: int = 0
    tags: List[str] = field(default_factory=list)
    related_knowledge: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.knowledge_id:
            self.knowledge_id = f"{self.knowledge_type.value}_{uuid.uuid4().hex[:8]}"
    
    def calculate_value_score(self) -> float:
        """Calcula score de valor baseado em uso e sucesso"""
        try:
            # Fatores de valor
            recency_factor = max(0, 1 - (datetime.now() - self.created_at).days / 30)  # Decai em 30 dias
            access_factor = min(self.access_count / 100, 1.0)  # Normalizar para 100 acessos
            validation_factor = min(self.validation_count / 10, 1.0)  # Normalizar para 10 validações
            success_factor = self.success_applications / max(self.success_applications + self.failed_applications, 1)
            
            # Pesos
            weights = {
                "recency": 0.2,
                "access": 0.3,
                "validation": 0.2,
                "success": 0.3
            }
            
            value_score = (
                weights["recency"] * recency_factor +
                weights["access"] * access_factor +
                weights["validation"] * validation_factor +
                weights["success"] * success_factor
            )
            
            return max(0, min(1, value_score))
            
        except Exception:
            return 0.0


@dataclass
class AgentProfile:
    """Perfil de um agente na rede"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    expertise_areas: List[str]
    contribution_score: float
    reputation_score: float
    knowledge_shared: int
    knowledge_consumed: int
    successful_collaborations: int
    failed_collaborations: int
    last_active: datetime
    specialization_tags: List[str] = field(default_factory=list)
    
    def calculate_reputation(self) -> float:
        """Calcula score de reputação baseado em contribuições"""
        try:
            # Fatores de reputação
            contribution_factor = min(self.knowledge_shared / 50, 1.0)  # Normalizar para 50 contribuições
            success_factor = self.successful_collaborations / max(self.successful_collaborations + self.failed_collaborations, 1)
            balance_factor = min(self.knowledge_consumed / max(self.knowledge_shared, 1), 1.0)  # Balanceamento dar/receber
            
            # Pesos
            weights = {
                "contribution": 0.5,
                "success": 0.3,
                "balance": 0.2
            }
            
            reputation = (
                weights["contribution"] * contribution_factor +
                weights["success"] * success_factor +
                weights["balance"] * balance_factor
            )
            
            self.reputation_score = max(0, min(1, reputation))
            return self.reputation_score
            
        except Exception:
            self.reputation_score = 0.0
            return 0.0


@dataclass
class CollectiveInsight:
    """Insight coletivo gerado pela rede"""
    insight_id: str
    title: str
    description: str
    contributing_agents: List[str]
    contributing_knowledge: List[str]
    confidence: float
    potential_impact: float
    applications: List[str]
    created_at: datetime
    validated_by: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.insight_id:
            self.insight_id = f"insight_{uuid.uuid4().hex[:8]}"


class CollectiveIntelligenceNetwork:
    """
    Rede de inteligência coletiva que permite compartilhamento de conhecimento
    e geração de insights coletivos entre agentes.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("CollectiveIntelligenceNetwork")
        
        # Configurações
        self.max_knowledge_items = config.get("collective_intelligence", {}).get("max_knowledge_items", 1000)
        self.knowledge_retention_days = config.get("collective_intelligence", {}).get("retention_days", 30)
        self.insight_generation_interval = config.get("collective_intelligence", {}).get("insight_interval", 300)  # 5 minutos
        self.auto_cleanup_enabled = config.get("collective_intelligence", {}).get("auto_cleanup", True)
        
        # Armazenamento de conhecimento
        self.knowledge_base: Dict[str, KnowledgeItem] = {}
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.collective_insights: Dict[str, CollectiveInsight] = {}
        
        # Índices para busca eficiente
        self.knowledge_by_type: Dict[KnowledgeType, List[str]] = defaultdict(list)
        self.knowledge_by_agent: Dict[str, List[str]] = defaultdict(list)
        self.knowledge_by_tag: Dict[str, List[str]] = defaultdict(list)
        
        # Sistema de broadcasting
        self.broadcast_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Threading
        self.network_lock = threading.Lock()
        self.insight_generation_thread: Optional[threading.Thread] = None
        self.insight_generation_running = False
        
        # Métricas
        self.metrics = {
            "total_knowledge_shared": 0,
            "total_insights_generated": 0,
            "active_agents": 0,
            "knowledge_applications": 0,
            "successful_collaborations": 0
        }
        
        # Diretórios
        self.network_dir = Path("data/collective_intelligence")
        self.knowledge_dir = self.network_dir / "knowledge"
        self.insights_dir = self.network_dir / "insights"
        self.agents_dir = self.network_dir / "agents"
        
        # Criar diretórios
        for directory in [self.network_dir, self.knowledge_dir, self.insights_dir, self.agents_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Carregar estado existente
        self._load_existing_network_state()
        
        # Iniciar sistema de insights
        self._start_insight_generation()
        
        self.logger.info("🧠 Collective Intelligence Network initialized!")
    
    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str], expertise_areas: List[str]) -> bool:
        """
        Registra um agente na rede de inteligência coletiva
        """
        try:
            with self.network_lock:
                if agent_id in self.agent_profiles:
                    # Atualizar perfil existente
                    profile = self.agent_profiles[agent_id]
                    profile.capabilities = capabilities
                    profile.expertise_areas = expertise_areas
                    profile.last_active = datetime.now()
                else:
                    # Criar novo perfil
                    profile = AgentProfile(
                        agent_id=agent_id,
                        agent_type=agent_type,
                        capabilities=capabilities,
                        expertise_areas=expertise_areas,
                        contribution_score=0.0,
                        reputation_score=0.0,
                        knowledge_shared=0,
                        knowledge_consumed=0,
                        successful_collaborations=0,
                        failed_collaborations=0,
                        last_active=datetime.now()
                    )
                    self.agent_profiles[agent_id] = profile
                
                # Atualizar métricas
                self.metrics["active_agents"] = len(self.agent_profiles)
                
                # Salvar perfil
                self._save_agent_profile(agent_id, profile)
                
                # Adicionar conhecimento inicial sobre o agente
                initial_knowledge = KnowledgeItem(
                    knowledge_id="",
                    knowledge_type=KnowledgeType.STRATEGY_DISCOVERY,
                    source_agent=agent_id,
                    title=f"Agent {agent_id} Registration",
                    content=f"New agent {agent_id} of type {agent_type} registered with capabilities: {', '.join(capabilities)}",
                    context={"agent_type": agent_type, "capabilities": capabilities, "expertise": expertise_areas},
                    relevance=KnowledgeRelevance.HIGH,
                    confidence=1.0,
                    created_at=datetime.now(),
                    last_accessed=datetime.now(),
                    tags=["agent_registration", "system_evolution", agent_type]
                )
                
                self.knowledge_base[initial_knowledge.knowledge_id] = initial_knowledge
                self.knowledge_by_type[initial_knowledge.knowledge_type].append(initial_knowledge.knowledge_id)
                self.knowledge_by_agent[initial_knowledge.source_agent].append(initial_knowledge.knowledge_id)
                for tag in initial_knowledge.tags:
                    self.knowledge_by_tag[tag].append(initial_knowledge.knowledge_id)
                
                self._save_knowledge_item(initial_knowledge)
                
                self.logger.info(f"👤 Agent {agent_id} registered in collective intelligence network")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error registering agent {agent_id}: {e}")
            return False
    
    def share_knowledge(self, agent_id: str, knowledge_type: KnowledgeType, title: str, content: str, 
                       context: Optional[Dict[str, Any]] = None, tags: Optional[List[str]] = None) -> Optional[str]:
        """
        Compartilha conhecimento na rede
        """
        try:
            if context is None:
                context = {}
            if tags is None:
                tags = []
            
            # Criar item de conhecimento
            knowledge_item = KnowledgeItem(
                knowledge_id="",
                knowledge_type=knowledge_type,
                source_agent=agent_id,
                title=title,
                content=content,
                context=context,
                relevance=KnowledgeRelevance.MEDIUM,  # Será calculado dinamicamente
                confidence=0.8,  # Valor padrão
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                tags=tags
            )
            
            with self.network_lock:
                # Adicionar ao knowledge base
                self.knowledge_base[knowledge_item.knowledge_id] = knowledge_item
                
                # Atualizar índices
                self.knowledge_by_type[knowledge_type].append(knowledge_item.knowledge_id)
                self.knowledge_by_agent[agent_id].append(knowledge_item.knowledge_id)
                for tag in tags:
                    self.knowledge_by_tag[tag].append(knowledge_item.knowledge_id)
                
                # Atualizar perfil do agente
                if agent_id in self.agent_profiles:
                    profile = self.agent_profiles[agent_id]
                    profile.knowledge_shared += 1
                    profile.last_active = datetime.now()
                    profile.calculate_reputation()
                
                # Atualizar métricas
                self.metrics["total_knowledge_shared"] += 1
                
                # Salvar conhecimento
                self._save_knowledge_item(knowledge_item)
                
                # Broadcast para subscribers
                self._broadcast_knowledge_update(knowledge_item)
                
                self.logger.info(f"📚 Knowledge shared by {agent_id}: {title}")
                return knowledge_item.knowledge_id
                
        except Exception as e:
            self.logger.error(f"❌ Error sharing knowledge: {e}")
            return None
    
    def search_knowledge(self, agent_id: str, query: str, knowledge_types: Optional[List[KnowledgeType]] = None, 
                        tags: Optional[List[str]] = None, max_results: int = 10) -> List[KnowledgeItem]:
        """
        Busca conhecimento na rede
        """
        try:
            results = []
            
            with self.network_lock:
                # Filtrar por tipos se especificado
                candidate_ids = set()
                if knowledge_types:
                    for ktype in knowledge_types:
                        candidate_ids.update(self.knowledge_by_type[ktype])
                else:
                    candidate_ids = set(self.knowledge_base.keys())
                
                # Filtrar por tags se especificado
                if tags:
                    tag_ids = set()
                    for tag in tags:
                        tag_ids.update(self.knowledge_by_tag[tag])
                    candidate_ids = candidate_ids.intersection(tag_ids)
                
                # Buscar por relevância de texto
                scored_results = []
                for knowledge_id in candidate_ids:
                    knowledge_item = self.knowledge_base[knowledge_id]
                    
                    # Calcular score de relevância
                    relevance_score = self._calculate_text_relevance(query, knowledge_item)
                    value_score = knowledge_item.calculate_value_score()
                    
                    combined_score = relevance_score * 0.7 + value_score * 0.3
                    
                    scored_results.append((combined_score, knowledge_item))
                
                # Ordenar por score e retornar top resultados
                scored_results.sort(key=lambda x: x[0], reverse=True)
                results = [item for score, item in scored_results[:max_results]]
                
                # Atualizar estatísticas de acesso
                for item in results:
                    item.access_count += 1
                    item.last_accessed = datetime.now()
                
                # Atualizar perfil do agente
                if agent_id in self.agent_profiles:
                    profile = self.agent_profiles[agent_id]
                    profile.knowledge_consumed += len(results)
                    profile.last_active = datetime.now()
                
                self.logger.info(f"🔍 Agent {agent_id} searched knowledge: {len(results)} results for '{query}'")
                return results
                
        except Exception as e:
            self.logger.error(f"❌ Error searching knowledge: {e}")
            return []
    
    def validate_knowledge(self, agent_id: str, knowledge_id: str, success: bool, feedback: str = "") -> bool:
        """
        Valida conhecimento compartilhado baseado em aplicação real
        """
        try:
            with self.network_lock:
                if knowledge_id not in self.knowledge_base:
                    self.logger.warning(f"⚠️ Knowledge {knowledge_id} not found for validation")
                    return False
                
                knowledge_item = self.knowledge_base[knowledge_id]
                
                # Atualizar estatísticas
                knowledge_item.validation_count += 1
                if success:
                    knowledge_item.success_applications += 1
                else:
                    knowledge_item.failed_applications += 1
                
                # Atualizar relevância baseada no sucesso
                success_rate = knowledge_item.success_applications / max(knowledge_item.validation_count, 1)
                if success_rate > 0.8:
                    knowledge_item.relevance = KnowledgeRelevance.HIGH
                elif success_rate > 0.6:
                    knowledge_item.relevance = KnowledgeRelevance.MEDIUM
                elif success_rate < 0.3:
                    knowledge_item.relevance = KnowledgeRelevance.LOW
                
                # Atualizar perfis dos agentes
                if agent_id in self.agent_profiles:
                    validator_profile = self.agent_profiles[agent_id]
                    if success:
                        validator_profile.successful_collaborations += 1
                    else:
                        validator_profile.failed_collaborations += 1
                    validator_profile.calculate_reputation()
                
                source_agent = knowledge_item.source_agent
                if source_agent in self.agent_profiles:
                    source_profile = self.agent_profiles[source_agent]
                    if success:
                        source_profile.successful_collaborations += 1
                    else:
                        source_profile.failed_collaborations += 1
                    source_profile.calculate_reputation()
                
                # Atualizar métricas
                self.metrics["knowledge_applications"] += 1
                if success:
                    self.metrics["successful_collaborations"] += 1
                
                # Salvar conhecimento atualizado
                self._save_knowledge_item(knowledge_item)
                
                self.logger.info(f"✅ Knowledge {knowledge_id} validated by {agent_id}: {'success' if success else 'failure'}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Error validating knowledge: {e}")
            return False
    
    def get_agent_recommendations(self, agent_id: str, task_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Gera recomendações personalizadas para um agente
        """
        try:
            recommendations = []
            
            with self.network_lock:
                if agent_id not in self.agent_profiles:
                    return recommendations
                
                agent_profile = self.agent_profiles[agent_id]
                
                # Buscar conhecimento relevante para as expertise areas do agente
                relevant_knowledge = []
                for expertise in agent_profile.expertise_areas:
                    # Buscar por tags relacionadas
                    knowledge_ids = self.knowledge_by_tag.get(expertise, [])
                    for knowledge_id in knowledge_ids:
                        knowledge_item = self.knowledge_base[knowledge_id]
                        if knowledge_item.source_agent != agent_id:  # Não recomendar próprio conhecimento
                            relevant_knowledge.append(knowledge_item)
                
                # Buscar agentes com expertise complementar
                complementary_agents = []
                for other_agent_id, other_profile in self.agent_profiles.items():
                    if other_agent_id != agent_id:
                        # Calcular sobreposição de expertise
                        overlap = set(agent_profile.expertise_areas).intersection(set(other_profile.expertise_areas))
                        if overlap and other_profile.reputation_score > 0.5:
                            complementary_agents.append({
                                "agent_id": other_agent_id,
                                "expertise": other_profile.expertise_areas,
                                "reputation": other_profile.reputation_score,
                                "shared_expertise": list(overlap)
                            })
                
                # Ordenar por reputação
                complementary_agents.sort(key=lambda x: x["reputation"], reverse=True)
                
                # Criar recomendações
                if relevant_knowledge:
                    recommendations.append({
                        "type": "knowledge_recommendation",
                        "title": "Relevant Knowledge Available",
                        "description": f"Found {len(relevant_knowledge)} knowledge items related to your expertise",
                        "items": [
                            {
                                "knowledge_id": item.knowledge_id,
                                "title": item.title,
                                "source_agent": item.source_agent,
                                "relevance": item.relevance.value,
                                "value_score": item.calculate_value_score()
                            }
                            for item in relevant_knowledge[:5]  # Top 5
                        ]
                    })
                
                if complementary_agents:
                    recommendations.append({
                        "type": "collaboration_recommendation",
                        "title": "Potential Collaborators",
                        "description": f"Found {len(complementary_agents)} agents with complementary expertise",
                        "agents": complementary_agents[:3]  # Top 3
                    })
                
                self.logger.info(f"💡 Generated {len(recommendations)} recommendations for {agent_id}")
                return recommendations
                
        except Exception as e:
            self.logger.error(f"❌ Error generating recommendations: {e}")
            return []
    
    def subscribe_to_knowledge_updates(self, agent_id: str, callback: Callable[[KnowledgeItem], None]):
        """
        Subscreve a updates de conhecimento
        """
        try:
            with self.network_lock:
                self.broadcast_subscribers[agent_id].append(callback)
                self.logger.info(f"📡 Agent {agent_id} subscribed to knowledge updates")
                
        except Exception as e:
            self.logger.error(f"❌ Error subscribing to updates: {e}")
    
    def _start_insight_generation(self):
        """Inicia thread de geração de insights coletivos"""
        if self.insight_generation_running:
            return
        
        self.insight_generation_running = True
        self.insight_generation_thread = threading.Thread(target=self._insight_generation_loop, daemon=True)
        self.insight_generation_thread.start()
        
        self.logger.info("🔮 Collective insight generation started")
    
    def _insight_generation_loop(self):
        """Loop de geração de insights coletivos"""
        while self.insight_generation_running:
            try:
                # Gerar insights periodicamente
                insights = self._generate_collective_insights()
                
                with self.network_lock:
                    for insight in insights:
                        self.collective_insights[insight.insight_id] = insight
                        self._save_collective_insight(insight)
                        
                        # Broadcast insight para subscribers
                        self._broadcast_insight(insight)
                        
                        self.metrics["total_insights_generated"] += 1
                
                if insights:
                    self.logger.info(f"🔮 Generated {len(insights)} collective insights")
                
                # Aguardar próximo ciclo
                time.sleep(self.insight_generation_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in insight generation loop: {e}")
                time.sleep(30)  # Aguardar mais tempo em caso de erro
    
    def _generate_collective_insights(self) -> List[CollectiveInsight]:
        """Gera insights coletivos usando LLM"""
        try:
            insights = []
            
            with self.network_lock:
                # Coletar dados para análise
                knowledge_summary = self._prepare_knowledge_summary()
                agent_interactions = self._analyze_agent_interactions()
                
                if not knowledge_summary:
                    return insights
                
                # Prompt para geração de insights
                insight_prompt = f"""
                Analyze the following collective knowledge and agent interactions to generate insights:
                
                Knowledge Summary:
                {json.dumps(knowledge_summary, indent=2)}
                
                Agent Interactions:
                {json.dumps(agent_interactions, indent=2)}
                
                Generate 1-3 collective insights that:
                1. Identify patterns across different agents and knowledge types
                2. Suggest improvements or optimizations
                3. Highlight emerging trends or opportunities
                
                Return as JSON array with format:
                [
                    {{
                        "title": "Insight Title",
                        "description": "Detailed description of the insight",
                        "confidence": 0.8,
                        "potential_impact": 0.9,
                        "applications": ["application1", "application2"]
                    }}
                ]
                """
                
                # Chamar LLM
                response = call_llm_api(
                    prompt=insight_prompt,
                    model_config=self.config.get("llm", {}),
                    temperature=0.7,
                    logger=self.logger
                )
                
                if response and len(response) >= 2 and response[1]:
                    # Parsear resposta
                    insight_data = parse_json_response(response[1], self.logger)
                    
                    if isinstance(insight_data, list):
                        for insight_info in insight_data:
                            if isinstance(insight_info, dict):
                                insight = CollectiveInsight(
                                    insight_id="",
                                    title=insight_info.get("title", "Generated Insight"),
                                    description=insight_info.get("description", ""),
                                    contributing_agents=list(self.agent_profiles.keys()),
                                    contributing_knowledge=list(self.knowledge_base.keys())[-10:],  # Últimos 10
                                    confidence=insight_info.get("confidence", 0.7),
                                    potential_impact=insight_info.get("potential_impact", 0.6),
                                    applications=insight_info.get("applications", []),
                                    created_at=datetime.now()
                                )
                                insights.append(insight)
                
                return insights
                
        except Exception as e:
            self.logger.error(f"❌ Error generating collective insights: {e}")
            # Gerar insights padrão quando LLM falha
            try:
                insights = []
                if len(self.agent_profiles) > 0:
                    # Insight padrão sobre evolução do sistema
                    evolution_insight = CollectiveInsight(
                        insight_id="",
                        title="System Evolution Pattern Detected",
                        description="The system is showing continuous evolution patterns with emergency corrections and fitness optimization. This indicates a healthy adaptive system.",
                        contributing_agents=list(self.agent_profiles.keys()),
                        contributing_knowledge=[],
                        confidence=0.8,
                        potential_impact=0.7,
                        applications=["system_optimization", "evolution_monitoring"],
                        created_at=datetime.now()
                    )
                    insights.append(evolution_insight)
                    
                    # Insight padrão sobre performance
                    performance_insight = CollectiveInsight(
                        insight_id="",
                        title="Performance Optimization Opportunities",
                        description="Multiple agents are contributing to system optimization. Focus on reducing emergency evolution triggers and improving baseline performance.",
                        contributing_agents=list(self.agent_profiles.keys()),
                        contributing_knowledge=[],
                        confidence=0.7,
                        potential_impact=0.8,
                        applications=["performance_tuning", "emergency_prevention"],
                        created_at=datetime.now()
                    )
                    insights.append(performance_insight)
                
                return insights
            except Exception as fallback_error:
                self.logger.error(f"❌ Error generating fallback insights: {fallback_error}")
                return []
    
    def _prepare_knowledge_summary(self) -> Dict[str, Any]:
        """Prepara resumo do conhecimento para análise"""
        try:
            summary = {
                "total_knowledge_items": len(self.knowledge_base),
                "knowledge_by_type": {},
                "top_contributors": [],
                "most_accessed_knowledge": [],
                "recent_trends": []
            }
            
            # Contagem por tipo
            for ktype, items in self.knowledge_by_type.items():
                summary["knowledge_by_type"][ktype.value] = len(items)
            
            # Top contributors
            contributor_stats = {}
            for knowledge_item in self.knowledge_base.values():
                agent = knowledge_item.source_agent
                if agent not in contributor_stats:
                    contributor_stats[agent] = 0
                contributor_stats[agent] += 1
            
            summary["top_contributors"] = sorted(
                contributor_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            # Conhecimento mais acessado
            most_accessed = sorted(
                self.knowledge_base.values(),
                key=lambda x: x.access_count,
                reverse=True
            )[:5]
            
            summary["most_accessed_knowledge"] = [
                {
                    "title": item.title,
                    "type": item.knowledge_type.value,
                    "access_count": item.access_count,
                    "success_rate": item.success_applications / max(item.validation_count, 1)
                }
                for item in most_accessed
            ]
            
            return summary
            
        except Exception as e:
            self.logger.error(f"❌ Error preparing knowledge summary: {e}")
            return {}
    
    def _analyze_agent_interactions(self) -> Dict[str, Any]:
        """Analisa interações entre agentes"""
        try:
            interactions = {
                "total_agents": len(self.agent_profiles),
                "collaboration_patterns": {},
                "expertise_distribution": {},
                "reputation_distribution": []
            }
            
            # Distribuição de expertise
            all_expertise = []
            for profile in self.agent_profiles.values():
                all_expertise.extend(profile.expertise_areas)
            
            expertise_count = {}
            for expertise in all_expertise:
                expertise_count[expertise] = expertise_count.get(expertise, 0) + 1
            
            interactions["expertise_distribution"] = dict(sorted(
                expertise_count.items(),
                key=lambda x: x[1],
                reverse=True
            ))
            
            # Distribuição de reputação
            reputations = [profile.reputation_score for profile in self.agent_profiles.values()]
            if reputations:
                interactions["reputation_distribution"] = {
                    "average": statistics.mean(reputations),
                    "median": statistics.median(reputations),
                    "std_dev": statistics.stdev(reputations) if len(reputations) > 1 else 0
                }
            
            return interactions
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing agent interactions: {e}")
            return {}
    
    def _calculate_text_relevance(self, query: str, knowledge_item: KnowledgeItem) -> float:
        """Calcula relevância de texto simples"""
        try:
            query_lower = query.lower()
            
            # Verificar correspondências
            title_match = query_lower in knowledge_item.title.lower()
            content_match = query_lower in knowledge_item.content.lower()
            tag_match = any(query_lower in tag.lower() for tag in knowledge_item.tags)
            
            # Calcular score
            score = 0.0
            if title_match:
                score += 0.5
            if content_match:
                score += 0.3
            if tag_match:
                score += 0.2
            
            return min(score, 1.0)
            
        except Exception:
            return 0.0
    
    def _broadcast_knowledge_update(self, knowledge_item: KnowledgeItem):
        """Faz broadcast de atualização de conhecimento"""
        try:
            for agent_id, callbacks in self.broadcast_subscribers.items():
                for callback in callbacks:
                    try:
                        callback(knowledge_item)
                    except Exception as e:
                        self.logger.error(f"❌ Error in broadcast callback for {agent_id}: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Error broadcasting knowledge update: {e}")
    
    def _broadcast_insight(self, insight: CollectiveInsight):
        """Faz broadcast de insight coletivo"""
        try:
            self.logger.info(f"🔮 Broadcasting collective insight: {insight.title}")
            # Implementar broadcast específico para insights se necessário
            
        except Exception as e:
            self.logger.error(f"❌ Error broadcasting insight: {e}")
    
    def _load_existing_network_state(self):
        """Carrega estado existente da rede"""
        try:
            # Carregar perfis de agentes
            for agent_file in self.agents_dir.glob("*.json"):
                with open(agent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    profile = AgentProfile(**data)
                    self.agent_profiles[profile.agent_id] = profile
            
            # Carregar conhecimento
            for knowledge_file in self.knowledge_dir.glob("*.json"):
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Converter string para enum
                    data["knowledge_type"] = KnowledgeType(data["knowledge_type"])
                    data["relevance"] = KnowledgeRelevance(data["relevance"])
                    # Converter timestamps
                    data["created_at"] = datetime.fromisoformat(data["created_at"])
                    data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
                    
                    knowledge_item = KnowledgeItem(**data)
                    self.knowledge_base[knowledge_item.knowledge_id] = knowledge_item
                    
                    # Reconstruir índices
                    self.knowledge_by_type[knowledge_item.knowledge_type].append(knowledge_item.knowledge_id)
                    self.knowledge_by_agent[knowledge_item.source_agent].append(knowledge_item.knowledge_id)
                    for tag in knowledge_item.tags:
                        self.knowledge_by_tag[tag].append(knowledge_item.knowledge_id)
            
            # Carregar insights
            for insight_file in self.insights_dir.glob("*.json"):
                with open(insight_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data["created_at"] = datetime.fromisoformat(data["created_at"])
                    insight = CollectiveInsight(**data)
                    self.collective_insights[insight.insight_id] = insight
            
            self.logger.info(f"📁 Loaded network state: {len(self.agent_profiles)} agents, {len(self.knowledge_base)} knowledge items")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading network state: {e}")
    
    def _save_agent_profile(self, agent_id: str, profile: AgentProfile):
        """Salva perfil do agente"""
        try:
            profile_file = self.agents_dir / f"{agent_id}.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                data = {
                    "agent_id": profile.agent_id,
                    "agent_type": profile.agent_type,
                    "capabilities": list(profile.capabilities) if isinstance(profile.capabilities, set) else profile.capabilities,
                    "expertise_areas": list(profile.expertise_areas) if isinstance(profile.expertise_areas, set) else profile.expertise_areas,
                    "contribution_score": profile.contribution_score,
                    "reputation_score": profile.reputation_score,
                    "knowledge_shared": profile.knowledge_shared,
                    "knowledge_consumed": profile.knowledge_consumed,
                    "successful_collaborations": profile.successful_collaborations,
                    "failed_collaborations": profile.failed_collaborations,
                    "last_active": profile.last_active.isoformat(),
                    "specialization_tags": list(profile.specialization_tags) if isinstance(profile.specialization_tags, set) else profile.specialization_tags
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving agent profile: {e}")
    
    def _save_knowledge_item(self, knowledge_item: KnowledgeItem):
        """Salva item de conhecimento"""
        try:
            knowledge_file = self.knowledge_dir / f"{knowledge_item.knowledge_id}.json"
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                data = {
                    "knowledge_id": knowledge_item.knowledge_id,
                    "knowledge_type": knowledge_item.knowledge_type.value,
                    "source_agent": knowledge_item.source_agent,
                    "title": knowledge_item.title,
                    "content": knowledge_item.content,
                    "context": knowledge_item.context,
                    "relevance": knowledge_item.relevance.value,
                    "confidence": knowledge_item.confidence,
                    "created_at": knowledge_item.created_at.isoformat(),
                    "last_accessed": knowledge_item.last_accessed.isoformat(),
                    "access_count": knowledge_item.access_count,
                    "validation_count": knowledge_item.validation_count,
                    "success_applications": knowledge_item.success_applications,
                    "failed_applications": knowledge_item.failed_applications,
                    "tags": list(knowledge_item.tags) if isinstance(knowledge_item.tags, set) else knowledge_item.tags,
                    "related_knowledge": list(knowledge_item.related_knowledge) if isinstance(knowledge_item.related_knowledge, set) else knowledge_item.related_knowledge
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving knowledge item: {e}")
    
    def _save_collective_insight(self, insight: CollectiveInsight):
        """Salva insight coletivo"""
        try:
            insight_file = self.insights_dir / f"{insight.insight_id}.json"
            with open(insight_file, 'w', encoding='utf-8') as f:
                data = {
                    "insight_id": insight.insight_id,
                    "title": insight.title,
                    "description": insight.description,
                    "contributing_agents": list(insight.contributing_agents) if isinstance(insight.contributing_agents, set) else insight.contributing_agents,
                    "contributing_knowledge": list(insight.contributing_knowledge) if isinstance(insight.contributing_knowledge, set) else insight.contributing_knowledge,
                    "confidence": insight.confidence,
                    "potential_impact": insight.potential_impact,
                    "applications": list(insight.applications) if isinstance(insight.applications, set) else insight.applications,
                    "created_at": insight.created_at.isoformat(),
                    "validated_by": list(insight.validated_by) if isinstance(insight.validated_by, set) else insight.validated_by
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving collective insight: {e}")
    
    def get_network_status(self) -> Dict[str, Any]:
        """Retorna status da rede"""
        return {
            "active_agents": len(self.agent_profiles),
            "knowledge_items": len(self.knowledge_base),
            "collective_insights": len(self.collective_insights),
            "metrics": self.metrics,
            "insight_generation_running": self.insight_generation_running,
            "top_contributors": sorted(
                [(agent_id, profile.knowledge_shared) for agent_id, profile in self.agent_profiles.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    def cleanup_old_knowledge(self):
        """Remove conhecimento antigo baseado em retention policy"""
        try:
            if not self.auto_cleanup_enabled:
                return
            
            cutoff_date = datetime.now() - timedelta(days=self.knowledge_retention_days)
            removed_count = 0
            
            with self.network_lock:
                # Identificar conhecimento antigo e pouco usado
                to_remove = []
                for knowledge_id, knowledge_item in self.knowledge_base.items():
                    if (knowledge_item.created_at < cutoff_date and 
                        knowledge_item.access_count < 5 and 
                        knowledge_item.success_applications < 2):
                        to_remove.append(knowledge_id)
                
                # Remover conhecimento
                for knowledge_id in to_remove:
                    knowledge_item = self.knowledge_base[knowledge_id]
                    
                    # Remover dos índices
                    self.knowledge_by_type[knowledge_item.knowledge_type].remove(knowledge_id)
                    self.knowledge_by_agent[knowledge_item.source_agent].remove(knowledge_id)
                    for tag in knowledge_item.tags:
                        if knowledge_id in self.knowledge_by_tag[tag]:
                            self.knowledge_by_tag[tag].remove(knowledge_id)
                    
                    # Remover do knowledge base
                    del self.knowledge_base[knowledge_id]
                    
                    # Remover arquivo
                    knowledge_file = self.knowledge_dir / f"{knowledge_id}.json"
                    if knowledge_file.exists():
                        knowledge_file.unlink()
                    
                    removed_count += 1
                
                if removed_count > 0:
                    self.logger.info(f"🧹 Cleaned up {removed_count} old knowledge items")
                    
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up old knowledge: {e}")
    
    def stop_insight_generation(self):
        """Para a geração de insights"""
        self.insight_generation_running = False
        if self.insight_generation_thread:
            self.insight_generation_thread.join(timeout=5)
        self.logger.info("🛑 Collective insight generation stopped")
    
    def share_evolution_knowledge(self, agent_id: str, evolution_type: str, details: Dict[str, Any]) -> Optional[str]:
        """
        Compartilha conhecimento sobre evolução do sistema automaticamente
        """
        try:
            # Determinar tipo de conhecimento baseado na evolução
            if evolution_type == "mutation_applied":
                knowledge_type = KnowledgeType.OPTIMIZATION_INSIGHT
                title = f"Evolution: {details.get('mutation', 'Unknown')} Applied"
                content = f"System evolution applied: {details.get('description', '')}. Fitness score: {details.get('fitness', 'N/A')}"
                tags = ["evolution", "mutation", "optimization", "fitness"]
                
            elif evolution_type == "performance_degradation":
                knowledge_type = KnowledgeType.FAILURE_PATTERN
                title = f"Performance Degradation: {details.get('degradation', 'Unknown')}%"
                content = f"System detected performance degradation of {details.get('degradation', 'Unknown')}%. Emergency evolution triggered."
                tags = ["performance", "degradation", "emergency", "evolution"]
                
            elif evolution_type == "fitness_improvement":
                knowledge_type = KnowledgeType.OPTIMIZATION_INSIGHT
                title = f"Fitness Improvement: {details.get('fitness', 'Unknown')}"
                content = f"System fitness improved to {details.get('fitness', 'Unknown')}. Strategy: {details.get('strategy', 'Unknown')}"
                tags = ["fitness", "improvement", "optimization", "strategy"]
                
            elif evolution_type == "emergency_evolution":
                knowledge_type = KnowledgeType.ERROR_RECOVERY
                title = f"Emergency Evolution: {details.get('trigger', 'Unknown')}"
                content = f"Emergency evolution triggered due to {details.get('trigger', 'Unknown')}. Applied corrections: {details.get('corrections', [])}"
                tags = ["emergency", "recovery", "correction", "evolution"]
                
            else:
                knowledge_type = KnowledgeType.STRATEGY_DISCOVERY
                title = f"System Evolution: {evolution_type}"
                content = f"System evolution event: {evolution_type}. Details: {details}"
                tags = ["evolution", "system", "discovery"]
            
            # Compartilhar conhecimento
            return self.share_knowledge(
                agent_id=agent_id,
                knowledge_type=knowledge_type,
                title=title,
                content=content,
                context=details,
                tags=tags
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error sharing evolution knowledge: {e}")
            return None


# Singleton instance
_collective_network = None

def get_collective_intelligence_network(config: Dict[str, Any], logger: logging.Logger) -> CollectiveIntelligenceNetwork:
    """Get singleton instance of Collective Intelligence Network"""
    global _collective_network
    if _collective_network is None:
        _collective_network = CollectiveIntelligenceNetwork(config, logger)
    return _collective_network 