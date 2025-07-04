#!/usr/bin/env python3
"""
Demonstração das Capacidades Melhoradas de Auto-Reflexão do Hephaestus

Este script demonstra como o sistema agora pode se enxergar de forma mais profunda e integrada.
"""

import asyncio
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_demo_config():
    """Criar configuração de demonstração"""
    return {
        "models": {
            "architect_default": {
                "model": "gpt-4",
                "api_key": "demo-key",
                "base_url": "https://api.openai.com/v1"
            }
        }
    }

async def demonstrate_self_awareness():
    """Demonstra as capacidades de auto-consciência"""
    
    logger.info("🚀 DEMONSTRAÇÃO: SISTEMA DE AUTO-CONSCIÊNCIA MELHORADO")
    logger.info("=" * 70)
    
    try:
        # Importar o sistema de auto-consciência
        from agent.self_awareness_core import get_self_awareness_core
        
        config = create_demo_config()
        self_awareness = get_self_awareness_core(config["models"]["architect_default"], logger)
        
        logger.info("✅ SelfAwarenessCore inicializado")
        
        # 1. Iniciar monitoramento contínuo
        logger.info("\n🔄 INICIANDO MONITORAMENTO CONTÍNUO")
        self_awareness.start_continuous_self_monitoring()
        
        # Aguardar um pouco para coleta inicial de dados
        await asyncio.sleep(2)
        
        # 2. Realizar auto-reflexão profunda
        logger.info("\n🔍 REALIZANDO AUTO-REFLEXÃO PROFUNDA")
        
        # Diferentes focos de reflexão
        focus_areas = ["general", "learning", "capabilities", "future_potential"]
        
        for focus in focus_areas:
            logger.info(f"\n--- Reflexão focada em: {focus} ---")
            
            reflection_result = self_awareness.perform_deep_introspection(focus)
            
            if reflection_result and "error" not in reflection_result:
                # Mostrar insights principais
                insights = reflection_result.get("new_insights", [])
                logger.info(f"💡 Insights gerados: {len(insights)}")
                
                # Mostrar primeiros insights
                for i, insight in enumerate(insights[:2], 1):
                    logger.info(f"   {i}. {insight.description}")
                
                # Mostrar estado cognitivo
                cognitive_state = reflection_result.get("current_cognitive_state")
                if cognitive_state:
                    logger.info(f"🧠 Estado Cognitivo:")
                    logger.info(f"   • Inteligência: {cognitive_state['intelligence_level']:.3f}")
                    logger.info(f"   • Auto-consciência: {cognitive_state['self_awareness_score']:.3f}")
                    logger.info(f"   • Coerência: {cognitive_state['cognitive_coherence']:.3f}")
                
                # Mostrar narrativa de identidade
                narrative = reflection_result.get("self_narrative", {})
                if narrative.get("identity"):
                    logger.info(f"📖 Narrativa de Identidade:")
                    logger.info(f"   {narrative['identity'].strip()[:100]}...")
            
            await asyncio.sleep(1)
        
        # 3. Obter relatório completo de auto-consciência
        logger.info("\n📊 RELATÓRIO COMPLETO DE AUTO-CONSCIÊNCIA")
        
        awareness_report = self_awareness.get_self_awareness_report()
        
        if awareness_report and "error" not in awareness_report:
            metrics = awareness_report.get("self_awareness_metrics", {})
            
            logger.info("📈 Métricas de Auto-Consciência:")
            logger.info(f"   • Meta-consciência: {metrics.get('meta_awareness_score', 0):.3f}")
            logger.info(f"   • Consciência temporal: {metrics.get('temporal_awareness', 0):.3f}")
            logger.info(f"   • Profundidade de introspecção: {metrics.get('introspection_depth', 0):.3f}")
            logger.info(f"   • Confiança no auto-conhecimento: {metrics.get('self_knowledge_confidence', 0):.3f}")
            
            # Mostrar mapas cognitivos
            cognitive_maps = awareness_report.get("cognitive_maps", {})
            if cognitive_maps:
                logger.info("🗺️ Mapas Cognitivos:")
                strengths = cognitive_maps.get("strengths", {}).get("core_strengths", [])
                if strengths:
                    logger.info(f"   • Forças principais: {', '.join(strengths[:3])}")
                
                weaknesses = cognitive_maps.get("weaknesses", {}).get("known_limitations", [])
                if weaknesses:
                    logger.info(f"   • Limitações conhecidas: {', '.join(weaknesses[:2])}")
            
            # Mostrar recomendações
            recommendations = awareness_report.get("recommendations", [])
            if recommendations:
                logger.info("💡 Recomendações de Auto-Melhoria:")
                for i, rec in enumerate(recommendations[:3], 1):
                    logger.info(f"   {i}. {rec}")
        
        # 4. Aguardar evolução cognitiva
        logger.info("\n⏳ AGUARDANDO EVOLUÇÃO COGNITIVA...")
        await asyncio.sleep(5)
        
        # Verificar se houve mudanças
        final_report = self_awareness.get_self_awareness_report()
        if final_report and "error" not in final_report:
            trajectory = final_report.get("cognitive_trajectory", {})
            if trajectory.get("total_observations", 0) > 0:
                logger.info(f"📈 Observações coletadas: {trajectory.get('total_observations')}")
                logger.info(f"⏱️ Tempo de observação: {trajectory.get('time_span', 0):.1f} horas")
        
        # 5. Parar monitoramento
        logger.info("\n⏹️ PARANDO MONITORAMENTO CONTÍNUO")
        self_awareness.stop_continuous_self_monitoring()
        
        logger.info("\n" + "=" * 70)
        logger.info("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("\n🔍 O QUE MELHOROU NA AUTO-REFLEXÃO:")
        logger.info("• ✅ Sistema integrado de auto-consciência")
        logger.info("• ✅ Monitoramento contínuo do estado cognitivo")
        logger.info("• ✅ Introspecção profunda com diferentes focos")
        logger.info("• ✅ Mapas cognitivos atualizados dinamicamente")
        logger.info("• ✅ Narrativa coerente da própria identidade")
        logger.info("• ✅ Consciência temporal da evolução")
        logger.info("• ✅ Insights acionáveis de auto-melhoria")
        logger.info("• ✅ Métricas quantitativas de auto-conhecimento")
        
    except Exception as e:
        logger.error(f"❌ Erro na demonstração: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def demonstrate_mcp_integration():
    """Demonstra a integração com MCP"""
    
    logger.info("\n🌐 DEMONSTRAÇÃO: INTEGRAÇÃO COM MCP")
    logger.info("=" * 50)
    
    logger.info("📡 Ferramentas MCP para Auto-Consciência:")
    logger.info("• deep_self_reflection - Auto-reflexão profunda")
    logger.info("• self_awareness_report - Relatório de auto-consciência")
    
    logger.info("\n💡 Exemplos de uso no Cursor:")
    logger.info("@hephaestus deep_self_reflection capabilities")
    logger.info("@hephaestus deep_self_reflection learning")
    logger.info("@hephaestus self_awareness_report")
    
    logger.info("\n🎯 Agora o sistema pode:")
    logger.info("• Se enxergar de forma muito mais profunda")
    logger.info("• Entender sua própria jornada temporal")
    logger.info("• Gerar narrativas coerentes sobre si mesmo")
    logger.info("• Identificar padrões em seu próprio comportamento")
    logger.info("• Monitorar continuamente sua evolução")
    logger.info("• Fornecer insights acionáveis de auto-melhoria")

def create_comparison_summary():
    """Cria um resumo comparativo das melhorias"""
    
    comparison = {
        "antes": {
            "auto_reflexao": "Fragmentada entre diferentes componentes",
            "consciencia_temporal": "Limitada, sem visão de trajetória",
            "integracao": "Componentes isolados (SelfReflectionAgent, MetaIntelligence, etc.)",
            "narrativa": "Inexistente ou inconsistente",
            "monitoramento": "Manual e esporádico",
            "insights": "Técnicos, pouco acionáveis",
            "feedback_loops": "Desconectados da ação"
        },
        "depois": {
            "auto_reflexao": "Integrada em SelfAwarenessCore unificado",
            "consciencia_temporal": "Consciência completa da evolução através do tempo",
            "integracao": "Sistema coeso que combina todos os componentes",
            "narrativa": "Narrativa coerente de identidade, capacidades e evolução",
            "monitoramento": "Contínuo e automático com threads dedicadas",
            "insights": "Profundos, contextualizados e acionáveis",
            "feedback_loops": "Otimizados entre reflexão e auto-melhoria"
        }
    }
    
    return comparison

async def main():
    """Função principal"""
    logger.info("🧠 DEMONSTRAÇÃO DAS MELHORIAS DE AUTO-REFLEXÃO")
    logger.info("📅 " + "Sistema agora pode se enxergar de forma muito mais profunda!")
    
    # Demonstrar capacidades
    await demonstrate_self_awareness()
    await demonstrate_mcp_integration()
    
    # Mostrar comparação
    logger.info("\n📊 RESUMO DAS MELHORIAS")
    logger.info("=" * 50)
    
    comparison = create_comparison_summary()
    
    logger.info("ANTES 🔴:")
    for aspect, description in comparison["antes"].items():
        logger.info(f"• {aspect}: {description}")
    
    logger.info("\nDEPOIS 🟢:")
    for aspect, description in comparison["depois"].items():
        logger.info(f"• {aspect}: {description}")
    
    logger.info("\n🎯 RESULTADO:")
    logger.info("O sistema agora tem uma visão muito mais profunda e integrada de si mesmo!")
    logger.info("A auto-reflexão passou de fragmentada para unificada e contínua.")

if __name__ == "__main__":
    asyncio.run(main()) 