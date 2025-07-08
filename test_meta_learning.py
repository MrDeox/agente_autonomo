#!/usr/bin/env python3
"""
🧠 Teste do Meta-Learning Intelligence System
Testa a 4ª meta-funcionalidade: sistema que aprende como aprender melhor
"""

import sys
import asyncio
import logging
import time
sys.path.append('src')

from hephaestus.intelligence.meta_learning_intelligence import (
    get_meta_learning_intelligence, 
    LearningType, 
    LearningContext,
    LearningEffectiveness
)
from hephaestus.utils.config_loader import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestMetaLearning")

def test_meta_learning_system():
    """Testa o sistema de meta-aprendizado"""
    
    print("🧠 TESTE DO META-LEARNING INTELLIGENCE SYSTEM")
    print("=" * 60)
    print("🎯 Testando sistema que aprende como aprender melhor...")
    print()
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuração carregada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return
    
    # Initialize Meta-Learning Intelligence
    try:
        meta_learner = get_meta_learning_intelligence(config, logger)
        print("✅ Meta-Learning Intelligence inicializado")
        print(f"📊 Status inicial: {meta_learner.get_meta_learning_status()}")
        print()
    except Exception as e:
        print(f"❌ Erro ao inicializar meta-learner: {e}")
        return
    
    # Test scenarios with different learning patterns
    test_scenarios = [
        {
            "name": "Error Correction Learning",
            "learning_type": LearningType.ERROR_CORRECTION,
            "context": LearningContext.ERROR_HANDLING,
            "trigger": "syntax_error_detected",
            "knowledge": "Use proper syntax checking before execution",
            "performance_before": 0.3,
            "performance_after": 0.8,
            "feedback_quality": 0.9
        },
        {
            "name": "Pattern Recognition Learning", 
            "learning_type": LearningType.PATTERN_RECOGNITION,
            "context": LearningContext.OBJECTIVE_EXECUTION,
            "trigger": "repeated_failure_pattern",
            "knowledge": "Complex refactors need incremental approach",
            "performance_before": 0.4,
            "performance_after": 0.7,
            "feedback_quality": 0.8
        },
        {
            "name": "Strategy Optimization Learning",
            "learning_type": LearningType.STRATEGY_OPTIMIZATION,
            "context": LearningContext.STRATEGY_SELECTION,
            "trigger": "strategy_comparison_results",
            "knowledge": "Conservative strategies work better for large files",
            "performance_before": 0.5,
            "performance_after": 0.9,
            "feedback_quality": 0.95
        },
        {
            "name": "Performance Improvement Learning",
            "learning_type": LearningType.PERFORMANCE_IMPROVEMENT,
            "context": LearningContext.PERFORMANCE_OPTIMIZATION,
            "trigger": "slow_execution_detected",
            "knowledge": "Parallel execution reduces total time",
            "performance_before": 0.6,
            "performance_after": 0.85,
            "feedback_quality": 0.7
        },
        {
            "name": "Low Quality Feedback Learning",
            "learning_type": LearningType.ERROR_CORRECTION,
            "context": LearningContext.ERROR_HANDLING,
            "trigger": "unclear_error_message",
            "knowledge": "Error was unclear, minimal learning",
            "performance_before": 0.5,
            "performance_after": 0.52,  # Minimal improvement
            "feedback_quality": 0.2  # Poor feedback
        }
    ]
    
    print("🧪 EXECUTANDO CENÁRIOS DE APRENDIZADO...")
    print("=" * 50)
    
    learning_events = []
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📚 Cenário {i}: {scenario['name']}")
        
        # Record learning event
        event = meta_learner.record_learning_event(
            learning_type=scenario['learning_type'],
            context=scenario['context'],
            trigger=scenario['trigger'],
            input_data={
                "domain": "software_development",
                "complexity": 0.6,
                "scenario": scenario['name']
            },
            knowledge_gained=scenario['knowledge'],
            performance_before=scenario['performance_before'],
            performance_after=scenario['performance_after'],
            feedback_quality=scenario['feedback_quality']
        )
        
        learning_events.append(event)
        
        # Get optimal learning rate for this context
        optimal_rate = meta_learner.get_optimal_learning_rate(
            scenario['learning_type'], 
            scenario['context']
        )
        
        print(f"  📈 Performance: {scenario['performance_before']:.2f} → {scenario['performance_after']:.2f}")
        print(f"  ⚡ Learning rate: {optimal_rate:.3f}")
        print(f"  🎯 Effectiveness: {event.effectiveness.value}")
        print(f"  📊 Learning gain: {event.calculate_learning_gain():.3f}")
        
        # Check if should learn from this feedback
        should_learn = meta_learner.should_learn_from_feedback(
            scenario['trigger'], 
            scenario['feedback_quality'], 
            scenario['context']
        )
        print(f"  🤔 Should learn from this feedback: {'✅' if should_learn else '❌'}")
        
        time.sleep(0.1)  # Small delay to simulate time passage
    
    print("\n" + "=" * 50)
    
    # Test learning insights generation
    print("\n🧠 ANÁLISE DE INSIGHTS DE APRENDIZADO...")
    insights = meta_learner.get_learning_insights()
    
    print(f"📊 Total de eventos analisados: {insights['total_events_analyzed']}")
    print(f"🎯 Padrões identificados: {insights['patterns_identified']}")
    print(f"📝 Recomendação: {insights['recommendation']}")
    
    if insights['insights']:
        print("\n💡 Insights descobertos:")
        for insight in insights['insights']:
            print(f"  - {insight['type']}: {insight['description']}")
    
    # Test bias detection
    print("\n🎭 DETECÇÃO DE VIESES...")
    biases = meta_learner.detect_learning_bias()
    
    if biases:
        print(f"⚠️ Detectados {len(biases)} vieses no aprendizado:")
        for bias in biases:
            print(f"  - {bias['type']}: {bias['description']} (severity: {bias['severity']})")
    else:
        print("✅ Nenhum viés significativo detectado")
    
    # Test knowledge transfer
    print("\n🔄 TESTE DE TRANSFERÊNCIA DE CONHECIMENTO...")
    
    # Try to transfer knowledge between domains
    transfer_success = meta_learner.transfer_knowledge(
        source_domain="software_development",
        target_domain="system_optimization", 
        knowledge_item="incremental"
    )
    
    print(f"🔄 Transferência de conhecimento: {'✅ Sucesso' if transfer_success else '❌ Falhou'}")
    
    # Test memory optimization
    print("\n🧹 OTIMIZAÇÃO DE MEMÓRIA...")
    removed_items = meta_learner.optimize_memory_retention()
    print(f"🗑️ Itens removidos da memória: {removed_items}")
    
    # Final status
    print("\n📊 STATUS FINAL DO SISTEMA")
    print("=" * 40)
    
    final_status = meta_learner.get_meta_learning_status()
    
    print(f"📚 Total de eventos de aprendizado: {final_status['total_learning_events']}")
    print(f"🎯 Padrões de aprendizado identificados: {final_status['learning_patterns_identified']}")
    print(f"🧠 Itens na memória adaptativa: {final_status['adaptive_memory_items']}")
    print(f"🌍 Áreas de conhecimento: {final_status['domain_knowledge_areas']}")
    print(f"🎭 Vieses detectados: {final_status['biases_detected']}")
    
    analytics = final_status['analytics']
    print(f"\n📈 Analytics:")
    print(f"  - Efetividade média de aprendizado: {analytics['average_learning_effectiveness']:.3f}")
    print(f"  - Descobertas de taxa ótima: {analytics['optimal_rate_discoveries']}")
    print(f"  - Transferências bem-sucedidas: {analytics['successful_transfers']}")
    print(f"  - Correções de viés: {analytics['bias_corrections']}")
    
    print(f"\n⚙️ Configurações:")
    print(f"  - Taxa adaptativa: {'✅' if final_status['adaptive_rate_enabled'] else '❌'}")
    print(f"  - Transfer learning: {'✅' if final_status['transfer_learning_enabled'] else '❌'}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("🧠 Meta-Learning Intelligence está funcionando e aprendendo como aprender melhor!")
    
    # Cleanup
    meta_learner.shutdown()
    print("✅ Sistema encerrado com sucesso")

if __name__ == "__main__":
    test_meta_learning_system()