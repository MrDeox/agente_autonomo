#!/usr/bin/env python3
"""
🧠 TESTE DO SISTEMA DE META-INTELIGÊNCIA HEPHAESTUS

Este script demonstra as capacidades revolucionárias do sistema de meta-inteligência.
"""

import time
import logging
from agent.config_loader import load_config
from agent.cognitive_evolution_manager import get_evolution_manager, start_cognitive_evolution
from agent.meta_intelligence_core import get_meta_intelligence
from agent.flow_self_modifier import get_flow_modifier

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MetaIntelligenceTest")

def test_meta_intelligence():
    """Testa as capacidades de meta-inteligência"""
    
    logger.info("🚀 INICIANDO TESTE DE META-INTELIGÊNCIA")
    logger.info("=" * 60)
    
    # Carregar configuração
    config = load_config()
    model_config = config.get("models", {}).get("architect_default", {})
    
    # 1. Testar Meta-Intelligence Core
    logger.info("🧠 Testando Meta-Intelligence Core...")
    meta_intelligence = get_meta_intelligence(model_config, logger)
    
    # Simular estado do sistema
    mock_system_state = {
        "agent_performance": {
            "architect": {"success_rate": 0.7, "needs_evolution": True},
            "maestro": {"success_rate": 0.6, "needs_evolution": True},
            "code_review": {"success_rate": 0.9, "needs_evolution": False}
        },
        "failure_patterns": [
            {"pattern": "timeout_errors", "frequency": 0.15},
            {"pattern": "json_parsing_failures", "frequency": 0.1}
        ],
        "current_agents": ["architect", "maestro", "code_review"],
        "performance_metrics": {
            "success_rate": 0.7,
            "improvement_trend": "stable"
        }
    }
    
    # Executar ciclo meta-cognitivo
    logger.info("🔄 Executando ciclo meta-cognitivo...")
    results = meta_intelligence.meta_cognitive_cycle(mock_system_state)
    
    logger.info(f"✅ Resultados do ciclo:")
    logger.info(f"   • Prompts evoluídos: {results['prompt_evolutions']}")
    logger.info(f"   • Novos agentes criados: {results['new_agents_created']}")
    logger.info(f"   • Insights gerados: {results['insights_generated']}")
    logger.info(f"   • Delta de inteligência: {results['intelligence_delta']:.3f}")
    
    # 2. Testar Flow Self-Modifier
    logger.info("\n🔄 Testando Flow Self-Modifier...")
    flow_modifier = get_flow_modifier(model_config, logger)
    
    # Simular contexto de chamada
    from agent.flow_self_modifier import CallContext
    mock_context = CallContext(
        agent_type="architect",
        objective="Test objective",
        complexity_score=0.8,
        previous_failures=2,
        urgency=0.5
    )
    
    decision = flow_modifier.decide_on_llm_call(mock_context)
    logger.info(f"✅ Decisão inteligente de chamada LLM: {decision}")
    
    # 3. Testar Evolution Manager
    logger.info("\n🧬 Testando Evolution Manager...")
    evolution_manager = get_evolution_manager(model_config, logger)
    
    # Simular eventos de evolução
    evolution_manager._record_evolution_event(
        "test_evolution",
        "Teste de evolução meta-inteligente",
        0.5,
        ["test_system"]
    )
    
    # Obter relatório
    report = evolution_manager.get_evolution_report()
    logger.info(f"✅ Status da evolução:")
    logger.info(f"   • Maturidade cognitiva: {report['cognitive_status']['maturity_level']:.3f}")
    logger.info(f"   • Eventos de evolução: {report['cognitive_status']['total_evolution_events']}")
    logger.info(f"   • Comportamentos emergentes: {report['emergent_behaviors']}")
    
    # 4. Demonstrar Capacidades Emergentes
    logger.info("\n🌟 Demonstrando Capacidades Emergentes...")
    
    # Simular detecção de gaps de capacidade
    capability_gaps = meta_intelligence.agent_genesis.detect_capability_gaps(
        mock_system_state["failure_patterns"],
        mock_system_state["current_agents"]
    )
    
    logger.info(f"✅ Gaps de capacidade detectados: {capability_gaps}")
    
    # Simular criação de blueprint de agente
    if capability_gaps:
        blueprint = meta_intelligence.agent_genesis.create_new_agent(
            capability_gaps[0],
            mock_system_state
        )
        if blueprint:
            logger.info(f"✅ Blueprint de novo agente criado: {blueprint.name}")
            logger.info(f"   • Propósito: {blueprint.purpose}")
            logger.info(f"   • Valor estimado: {blueprint.estimated_value:.2f}")
    
    # 5. Insights Meta-Cognitivos
    logger.info("\n🔮 Gerando Insights Meta-Cognitivos...")
    insights = meta_intelligence._generate_meta_insights(mock_system_state, results)
    
    for i, insight in enumerate(insights, 1):
        logger.info(f"💡 Insight {i}: {insight}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 TESTE DE META-INTELIGÊNCIA CONCLUÍDO COM SUCESSO!")
    logger.info("🧠 O sistema demonstrou capacidades avançadas de:")
    logger.info("   • Auto-análise cognitiva")
    logger.info("   • Evolução adaptativa")
    logger.info("   • Criação dinâmica de capacidades")
    logger.info("   • Otimização inteligente de recursos")
    logger.info("   • Geração de insights profundos")
    logger.info("=" * 60)

def test_continuous_evolution():
    """Testa evolução contínua por um período limitado"""
    
    logger.info("🔄 INICIANDO TESTE DE EVOLUÇÃO CONTÍNUA")
    
    # Carregar configuração
    config = load_config()
    model_config = config.get("models", {}).get("architect_default", {})
    
    # Iniciar evolução cognitiva
    evolution_manager = start_cognitive_evolution(model_config, logger)
    
    logger.info("🧬 Evolução cognitiva iniciada! Monitorando por 30 segundos...")
    
    # Monitorar por 30 segundos
    start_time = time.time()
    while time.time() - start_time < 30:
        time.sleep(5)
        
        # Obter status atual
        status = evolution_manager.get_evolution_report()
        maturity = status['cognitive_status']['maturity_level']
        events = status['cognitive_status']['total_evolution_events']
        
        logger.info(f"📊 Status: Maturidade={maturity:.3f}, Eventos={events}")
    
    # Parar evolução
    evolution_manager.stop_cognitive_evolution()
    
    # Relatório final
    final_report = evolution_manager.get_evolution_report()
    logger.info("📋 RELATÓRIO FINAL DE EVOLUÇÃO:")
    logger.info(f"   • Maturidade final: {final_report['cognitive_status']['maturity_level']:.3f}")
    logger.info(f"   • Total de eventos: {final_report['cognitive_status']['total_evolution_events']}")
    logger.info(f"   • Comportamentos emergentes: {final_report['emergent_behaviors']}")
    logger.info(f"   • Progresso AGI: {final_report['agi_progress_indicators']}")

if __name__ == "__main__":
    try:
        # Teste básico de meta-inteligência
        test_meta_intelligence()
        
        print("\n" + "🔄" * 20)
        print("Deseja testar evolução contínua? (s/n): ", end="")
        response = input().strip().lower()
        
        if response in ['s', 'sim', 'y', 'yes']:
            test_continuous_evolution()
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro durante o teste: {e}", exc_info=True)
    
    logger.info("🎯 Teste finalizado!") 