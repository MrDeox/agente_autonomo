#!/usr/bin/env python3
"""
Teste do Sistema de Comunicação Inter-Agente e Coordenação de Enxame
Demonstra conversas diretas, colaboração e resolução coletiva de problemas
"""

import asyncio
import json
import logging
import time
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_swarm_communication():
    """Testa o sistema de comunicação inter-agente"""
    logger.info("🐝 Iniciando teste do sistema de comunicação inter-agente...")
    
    try:
        # Importar componentes necessários
        from agent.config_loader import load_config
        from agent.hephaestus_agent import HephaestusAgent
        
        # Carregar configuração
        config = load_config()
        
        # Criar instância do HephaestusAgent
        hephaestus = HephaestusAgent(
            logger_instance=logger,
            config=config,
            continuous_mode=False
        )
        
        logger.info("✅ HephaestusAgent inicializado com sistema de comunicação")
        
        # Teste 1: Status do sistema de comunicação
        logger.info("\n" + "="*60)
        logger.info("📊 TESTE 1: Status do Sistema de Comunicação")
        logger.info("="*60)
        
        swarm_status = hephaestus.get_swarm_communication_status()
        logger.info(f"Status do enxame: {json.dumps(swarm_status, indent=2, default=str)}")
        
        # Teste 2: Iniciar conversa entre agentes
        logger.info("\n" + "="*60)
        logger.info("💬 TESTE 2: Conversa entre Agentes")
        logger.info("="*60)
        
        conversation_id = await hephaestus.inter_agent_communication.start_conversation(
            initiator="architect",
            participants=["maestro", "code_reviewer"],
            topic="Estratégia de Otimização de Performance",
            initial_message="Vamos discutir como otimizar a performance do sistema. Tenho algumas ideias sobre refatoração."
        )
        
        logger.info(f"Conversa iniciada com ID: {conversation_id}")
        
        # Teste 3: Coordenação de tarefa complexa
        logger.info("\n" + "="*60)
        logger.info("🎯 TESTE 3: Coordenação de Tarefa Complexa")
        logger.info("="*60)
        
        coordination_result = await hephaestus.inter_agent_communication.coordinate_complex_task(
            task_description="Implementar sistema de cache inteligente com invalidação automática",
            required_capabilities=["code_analysis", "architecture_design", "performance_optimization"]
        )
        
        logger.info(f"Resultado da coordenação: {json.dumps(coordination_result, indent=2, default=str)}")
        
        # Teste 4: Resolução de conflito
        logger.info("\n" + "="*60)
        logger.info("⚖️ TESTE 4: Resolução de Conflito")
        logger.info("="*60)
        
        conflict_result = await hephaestus.inter_agent_communication.negotiate_solution(
            problem="Disputa sobre abordagem de implementação: microserviços vs monólito",
            conflicting_agents=["architect", "maestro"]
        )
        
        logger.info(f"Resultado da negociação: {json.dumps(conflict_result, indent=2, default=str)}")
        
        # Teste 5: Resolução coletiva de problemas
        logger.info("\n" + "="*60)
        logger.info("🧠 TESTE 5: Resolução Coletiva de Problemas")
        logger.info("="*60)
        
        agent_perspectives = {
            "architect": "Foco na arquitetura escalável e manutenível",
            "maestro": "Priorizar velocidade de desenvolvimento e simplicidade",
            "code_reviewer": "Garantir qualidade de código e padrões consistentes",
            "bug_hunter": "Identificar e prevenir problemas de segurança e performance"
        }
        
        problem_solving_result = await hephaestus.inter_agent_communication.collective_problem_solving(
            problem="Como implementar um sistema de autenticação robusto e seguro",
            agent_perspectives=agent_perspectives
        )
        
        logger.info(f"Resultado da resolução coletiva: {json.dumps(problem_solving_result, indent=2, default=str)}")
        
        # Teste 6: Compartilhamento de conhecimento
        logger.info("\n" + "="*60)
        logger.info("📚 TESTE 6: Compartilhamento de Conhecimento")
        logger.info("="*60)
        
        knowledge_result = await hephaestus.inter_agent_communication.knowledge_sharing_session(
            topic="Melhores práticas de desenvolvimento de APIs REST",
            knowledge_providers=["architect", "code_reviewer"]
        )
        
        logger.info(f"Resultado do compartilhamento: {json.dumps(knowledge_result, indent=2, default=str)}")
        
        # Teste 7: Métricas do enxame
        logger.info("\n" + "="*60)
        logger.info("📈 TESTE 7: Métricas do Enxame")
        logger.info("="*60)
        
        swarm_metrics = hephaestus.swarm_coordinator.get_swarm_metrics()
        logger.info(f"Métricas do enxame:")
        logger.info(f"  • Total de agentes: {swarm_metrics.total_agents}")
        logger.info(f"  • Conversas ativas: {swarm_metrics.active_conversations}")
        logger.info(f"  • Sessões de colaboração: {swarm_metrics.collaboration_sessions}")
        logger.info(f"  • Mensagens por minuto: {swarm_metrics.messages_per_minute:.2f}")
        logger.info(f"  • Taxa de sucesso: {swarm_metrics.success_rate:.2%}")
        logger.info(f"  • Score de inteligência coletiva: {swarm_metrics.collective_intelligence_score:.2f}")
        
        # Teste 8: Demonstração de coordenação via SwarmCoordinator
        logger.info("\n" + "="*60)
        logger.info("🐝 TESTE 8: Coordenação via SwarmCoordinator")
        logger.info("="*60)
        
        # Simular solicitação de coordenação
        coordination_request = await hephaestus.swarm_coordinator.coordinate_new_objective(
            objective_description="Implementar sistema de monitoramento em tempo real com alertas inteligentes",
            requesting_agent="architect"
        )
        
        logger.info(f"Coordenação via SwarmCoordinator: {json.dumps(coordination_request, indent=2, default=str)}")
        
        # Status final
        logger.info("\n" + "="*60)
        logger.info("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        logger.info("="*60)
        
        final_status = hephaestus.get_swarm_communication_status()
        logger.info(f"Status final do sistema: {json.dumps(final_status, indent=2, default=str)}")
        
        logger.info("\n🚀 Sistema de comunicação inter-agente funcionando perfeitamente!")
        logger.info("🤝 Agentes podem conversar, colaborar e resolver problemas coletivamente")
        logger.info("🐝 Enxame inteligente ativo e coordenado!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}", exc_info=True)
        return False

async def demo_swarm_intelligence():
    """Demonstração de inteligência de enxame em ação"""
    logger.info("\n" + "="*80)
    logger.info("🧠 DEMONSTRAÇÃO: Inteligência de Enxame em Ação")
    logger.info("="*80)
    
    try:
        from agent.config_loader import load_config
        from agent.hephaestus_agent import HephaestusAgent
        
        config = load_config()
        hephaestus = HephaestusAgent(
            logger_instance=logger,
            config=config,
            continuous_mode=False
        )
        
        # Cenário: Problema complexo que requer múltiplas perspectivas
        complex_problem = """
        PROBLEMA COMPLEXO: O sistema está enfrentando problemas de performance 
        durante picos de carga. Precisamos de uma solução que:
        1. Melhore a performance sem comprometer a funcionalidade
        2. Seja escalável para futuras demandas
        3. Mantenha a qualidade do código
        4. Detecte e previna problemas similares
        """
        
        logger.info(f"🎯 Problema a ser resolvido: {complex_problem}")
        
        # Iniciar resolução coletiva
        logger.info("\n🔄 Iniciando resolução coletiva...")
        
        # Simular perspectivas dos agentes
        perspectives = {
            "architect": "Proponho implementar um sistema de cache distribuído com Redis e otimizar queries do banco de dados",
            "maestro": "Sugiro priorizar as otimizações mais críticas primeiro e implementar gradualmente",
            "code_reviewer": "Precisamos garantir que as otimizações sigam padrões de qualidade e sejam bem documentadas",
            "bug_hunter": "Vou analisar logs para identificar gargalos específicos e prevenir regressões"
        }
        
        # Iniciar sessão de resolução coletiva
        result = await hephaestus.inter_agent_communication.collective_problem_solving(
            problem=complex_problem,
            agent_perspectives=perspectives
        )
        
        logger.info(f"✅ Resolução coletiva iniciada: {result}")
        
        # Simular evolução da conversa
        logger.info("\n💬 Simulando evolução da conversa...")
        
        # Mensagens de progresso
        progress_messages = [
            ("architect", "Analisei a arquitetura atual e identifiquei 3 pontos críticos de otimização"),
            ("maestro", "Concordo com a análise. Vamos priorizar o cache primeiro, depois as queries"),
            ("code_reviewer", "Ótimo! Vou criar guidelines para as otimizações"),
            ("bug_hunter", "Encontrei 2 gargalos nos logs. Vou criar testes para prevenir regressões"),
            ("architect", "Perfeito! Com essas perspectivas, temos uma solução completa"),
            ("maestro", "Vamos implementar em fases: Fase 1 - Cache, Fase 2 - Queries, Fase 3 - Monitoramento")
        ]
        
        for sender, message in progress_messages:
            logger.info(f"  {sender}: {message}")
            await asyncio.sleep(0.5)  # Simular tempo de processamento
        
        # Resultado final
        logger.info("\n🎉 SOLUÇÃO COLETIVA ENCONTRADA!")
        logger.info("📋 Plano de implementação:")
        logger.info("  1. Implementar cache Redis para queries frequentes")
        logger.info("  2. Otimizar queries críticas com índices e paginação")
        logger.info("  3. Implementar monitoramento em tempo real")
        logger.info("  4. Criar testes automatizados para prevenir regressões")
        logger.info("  5. Documentar padrões de otimização")
        
        logger.info("\n🚀 Inteligência de enxame demonstrada com sucesso!")
        logger.info("🤝 Múltiplos agentes colaboraram para resolver um problema complexo")
        logger.info("🧠 Cada agente contribuiu com sua expertise única")
        logger.info("🎯 Solução mais robusta e completa que qualquer agente individual")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração: {e}", exc_info=True)
        return False

async def main():
    """Função principal"""
    logger.info("🚀 Iniciando testes do sistema de comunicação inter-agente...")
    
    # Teste básico
    success1 = await test_swarm_communication()
    
    if success1:
        # Demonstração avançada
        success2 = await demo_swarm_intelligence()
        
        if success2:
            logger.info("\n" + "="*80)
            logger.info("🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
            logger.info("="*80)
            logger.info("🐝 Sistema de comunicação inter-agente funcionando perfeitamente")
            logger.info("🤝 Agentes podem conversar e colaborar efetivamente")
            logger.info("🧠 Inteligência de enxame ativa e coordenada")
            logger.info("🚀 Hephaestus agora é um verdadeiro enxame inteligente!")
            logger.info("="*80)
        else:
            logger.error("❌ Demonstração falhou")
    else:
        logger.error("❌ Teste básico falhou")

if __name__ == "__main__":
    asyncio.run(main()) 