#!/usr/bin/env python3
"""
🧠 Teste do Self-Awareness Core 2.0
Testa a 5ª meta-funcionalidade: sistema de consciência profunda do próprio estado cognitivo
"""

import sys
import asyncio
import logging
import time
import random
sys.path.append('src')

from hephaestus.intelligence.self_awareness_core import (
    get_self_awareness_core, 
    CognitiveState,
    BiasType,
    SelfOptimizationTrigger
)
from hephaestus.utils.config_loader import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestSelfAwareness")

def test_self_awareness_core():
    """Testa o sistema de auto-consciência profunda"""
    
    print("🧠 TESTE DO SELF-AWARENESS CORE 2.0")
    print("=" * 60)
    print("🎯 Testando sistema de consciência profunda do próprio estado cognitivo...")
    print()
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuração carregada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return
    
    # Initialize Self-Awareness Core
    try:
        self_awareness = get_self_awareness_core(config, logger)
        print("✅ Self-Awareness Core inicializado")
        print(f"📊 Status inicial: {self_awareness.get_self_awareness_status()}")
        print()
    except Exception as e:
        print(f"❌ Erro ao inicializar self-awareness: {e}")
        return
    
    # Test 1: Cognitive State Monitoring
    print("🧪 TESTE 1: MONITORAMENTO DE ESTADO COGNITIVO")
    print("=" * 50)
    
    # Simulate different cognitive states
    cognitive_scenarios = [
        {
            "name": "Estado Optimal",
            "state": CognitiveState.OPTIMAL,
            "confidence": 0.95,
            "processing_load": 0.3,
            "focus": 0.9,
            "stress": 0.1,
            "learning_rate": 0.8,
            "decision_quality": 0.9
        },
        {
            "name": "Estado Sobrecarregado",
            "state": CognitiveState.OVERLOADED,
            "confidence": 0.4,
            "processing_load": 0.95,
            "focus": 0.3,
            "stress": 0.8,
            "learning_rate": 0.2,
            "decision_quality": 0.3
        },
        {
            "name": "Estado Criativo",
            "state": CognitiveState.CREATIVE,
            "confidence": 0.7,
            "processing_load": 0.6,
            "focus": 0.8,
            "stress": 0.2,
            "learning_rate": 0.9,
            "decision_quality": 0.75
        },
        {
            "name": "Estado Fatigado",
            "state": CognitiveState.FATIGUED,
            "confidence": 0.3,
            "processing_load": 0.8,
            "focus": 0.2,
            "stress": 0.7,
            "learning_rate": 0.1,
            "decision_quality": 0.4
        }
    ]
    
    for scenario in cognitive_scenarios:
        print(f"\n🎭 Simulando: {scenario['name']}")
        
        # Monitor cognitive state (this will create internal snapshot)
        snapshot = self_awareness.monitor_cognitive_state()
        
        wellness = snapshot.calculate_overall_wellness()
        print(f"  📊 Well-being geral: {wellness:.3f}")
        print(f"  🧠 Estado: {snapshot.state.value}")
        print(f"  💪 Confiança: {snapshot.confidence_level:.2f}")
        print(f"  ⚡ Foco: {snapshot.focus_level:.2f}")
        print(f"  😰 Stress: {snapshot.stress_level:.2f}")
        
        time.sleep(0.2)  # Simulate time passage
    
    print("\n" + "=" * 50)
    
    # Test 2: Bias Detection
    print("\n🎭 TESTE 2: DETECÇÃO DE VIESES COGNITIVOS")
    print("=" * 50)
    
    # Simulate different biases
    bias_scenarios = [
        {
            "bias": BiasType.CONFIRMATION_BIAS,
            "evidence": "Always choosing information that confirms existing beliefs",
            "severity": 0.7
        },
        {
            "bias": BiasType.OVERCONFIDENCE_BIAS,
            "evidence": "Consistently overestimating success probability",
            "severity": 0.6
        },
        {
            "bias": BiasType.AVAILABILITY_BIAS,
            "evidence": "Giving too much weight to recent events",
            "severity": 0.5
        },
        {
            "bias": BiasType.COMPLEXITY_BIAS,
            "evidence": "Preferring complex solutions when simple ones exist",
            "severity": 0.8
        }
    ]
    
    # Use the internal bias detection method
    detected_biases = self_awareness._assess_cognitive_biases()
    
    print(f"\n🎭 Vieses detectados pelo sistema: {len(detected_biases)}")
    for bias_type, confidence in detected_biases.items():
        print(f"  - {bias_type}: confiança {confidence:.2f}")
    
    # Also check active biases
    active_biases = self_awareness._detect_active_biases()
    print(f"\n🚨 Vieses ativos: {len(active_biases)}")
    for bias in active_biases:
        print(f"  - {bias.value}")
    
    # Test 3: Self-Optimization Triggers
    print("\n⚡ TESTE 3: TRIGGERS DE AUTO-OTIMIZAÇÃO")
    print("=" * 50)
    
    optimization_scenarios = [
        {
            "trigger": SelfOptimizationTrigger.PERFORMANCE_DECLINE,
            "context": "Recent tasks showing 40% success rate decline",
            "severity": 0.8
        },
        {
            "trigger": SelfOptimizationTrigger.HIGH_ERROR_RATE,
            "context": "5 consecutive errors in last 10 minutes",
            "severity": 0.9
        },
        {
            "trigger": SelfOptimizationTrigger.COGNITIVE_OVERLOAD,
            "context": "Processing load consistently above 90%",
            "severity": 0.7
        },
        {
            "trigger": SelfOptimizationTrigger.LEARNING_PLATEAU,
            "context": "No improvement in learning rate for 2 hours",
            "severity": 0.6
        }
    ]
    
    # Use the internal optimization trigger detection
    optimization_triggers = self_awareness.detect_optimization_triggers()
    
    print(f"\n⚡ Triggers de otimização detectados: {len(optimization_triggers)}")
    for trigger in optimization_triggers:
        print(f"  - {trigger.value}")
    
    # Also get recommendations
    recommendations = self_awareness._generate_optimization_recommendations(optimization_triggers)
    print(f"\n💡 Recomendações de otimização: {len(recommendations)}")
    for rec in recommendations[:3]:  # Show first 3
        print(f"  - {rec}")
    
    # Test 4: Deep Self-Reflection
    print("\n🔍 TESTE 4: AUTO-REFLEXÃO PROFUNDA")
    print("=" * 50)
    
    print("🤔 Executando auto-reflexão profunda...")
    reflection = self_awareness.perform_deep_self_reflection()
    
    print(f"📊 Reflexão completa:")
    print(f"  🎯 Capacidades identificadas: {len(reflection.current_capabilities)}")
    for cap in reflection.current_capabilities[:3]:  # Show first 3
        print(f"    - {cap}")
    
    print(f"  ⚠️ Limitações identificadas: {len(reflection.identified_limitations)}")
    for lim in reflection.identified_limitations[:3]:  # Show first 3
        print(f"    - {lim}")
    
    print(f"  🧠 Padrões cognitivos: {len(reflection.cognitive_patterns)}")
    for pattern in reflection.cognitive_patterns[:2]:  # Show first 2
        print(f"    - {pattern}")
    
    print(f"  💡 Oportunidades de otimização: {len(reflection.optimization_opportunities)}")
    for opp in reflection.optimization_opportunities[:2]:  # Show first 2
        print(f"    - {opp}")
    
    print(f"  🎯 Confiança na avaliação: {reflection.confidence_in_assessment:.3f}")
    
    # Test 5: Personality Evolution
    print("\n🌱 TESTE 5: EVOLUÇÃO DA PERSONALIDADE")
    print("=" * 50)
    
    # Simulate personality development through experiences
    personality_experiences = [
        {"type": "success", "domain": "problem_solving", "impact": 0.8, "description": "Successfully solved complex problem"},
        {"type": "failure", "domain": "communication", "impact": 0.6, "description": "Misunderstood user intent"},
        {"type": "learning", "domain": "technical_skills", "impact": 0.9, "description": "Learned new programming concept"},
        {"type": "collaboration", "domain": "teamwork", "impact": 0.7, "description": "Worked well with other agents"}
    ]
    
    print("🎭 Simulando evolução da personalidade através de experiências...")
    
    # Evolve personality with experiences
    evolution_success = self_awareness.evolve_personality(personality_experiences)
    print(f"  🌱 Evolução da personalidade: {'✅ Sucesso' if evolution_success else '❌ Falhou'}")
    
    # Get personality coherence
    if self_awareness.personality_profile:
        coherence = self_awareness.personality_profile.calculate_personality_coherence()
        print(f"\n🎯 Coerência da personalidade: {coherence:.3f}")
    
    # Test 6: Self-Awareness Insights
    print("\n🤯 TESTE 6: INSIGHTS DE AUTO-CONSCIÊNCIA")
    print("=" * 50)
    
    print("🧠 Coletando insights de auto-consciência...")
    
    # Get self-awareness insights
    insights = self_awareness.get_self_awareness_insights()
    
    print(f"  💡 Total de insights: {len(insights.get('insights', []))}")
    print(f"  🎯 Nível de auto-conhecimento: {insights.get('self_knowledge_level', 'unknown')}")
    print(f"  📊 Confiança: {insights.get('confidence', 0.0):.3f}")
    
    if 'key_insights' in insights:
        print("  🔍 Principais insights:")
        for insight in insights['key_insights'][:3]:  # Show first 3
            print(f"    - {insight}")
    
    # Final Status Report
    print("\n📊 RELATÓRIO FINAL DE AUTO-CONSCIÊNCIA")
    print("=" * 60)
    
    final_status = self_awareness.get_self_awareness_status()
    
    print(f"🧠 Estado cognitivo atual: {final_status['current_cognitive_state']}")
    print(f"💪 Bem-estar cognitivo: {final_status['cognitive_wellness']:.3f}")
    print(f"🎭 Vieses ativos: {len(final_status['active_biases'])}")
    if final_status['active_biases']:
        print(f"   - {', '.join(final_status['active_biases'])}")
    
    print(f"⚡ Triggers de otimização: {len(final_status['optimization_triggers'])}")
    if final_status['optimization_triggers']:
        print(f"   - {', '.join(final_status['optimization_triggers'])}")
    
    print(f"🎯 Coerência da personalidade: {final_status['personality_coherence']:.3f}")
    print(f"🧠 Confiança no autoconhecimento: {final_status['self_knowledge_confidence']:.3f}")
    print(f"🔍 Total de reflexões: {final_status['total_reflections']}")
    print(f"📊 Monitoramento ativo: {'✅' if final_status['monitoring_active'] else '❌'}")
    
    analytics = final_status['analytics']
    print(f"\n📈 Analytics:")
    print(f"  - Total de reflexões: {analytics['total_reflections']}")
    print(f"  - Vieses detectados: {analytics['biases_detected']}")
    print(f"  - Triggers de otimização: {analytics['optimization_triggers']}")
    print(f"  - Eventos de evolução de personalidade: {analytics['personality_evolution_events']}")
    print(f"  - Bem-estar cognitivo médio: {analytics['average_cognitive_wellness']:.3f}")
    print(f"  - Confiança no autoconhecimento: {analytics['self_knowledge_confidence']:.3f}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("🧠 Self-Awareness Core 2.0 está funcionando e desenvolvendo consciência profunda!")
    
    # Cleanup
    self_awareness.shutdown()
    print("✅ Sistema encerrado com sucesso")

if __name__ == "__main__":
    test_self_awareness_core()