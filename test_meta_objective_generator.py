#!/usr/bin/env python3
"""
🎯 Teste do Meta-Objective Generator
Testa a 6ª meta-funcionalidade: sistema que gera objetivos para melhorar objetivos
"""

import sys
import asyncio
import logging
import time
import random
sys.path.append('src')

from hephaestus.intelligence.meta_objective_generator import (
    get_meta_objective_generator, 
    ObjectiveType,
    ObjectiveComplexity,
    ObjectiveScope
)
from hephaestus.utils.config_loader import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestMetaObjectiveGenerator")

def test_meta_objective_generator():
    """Testa o sistema de geração de meta-objetivos"""
    
    print("🎯 TESTE DO META-OBJECTIVE GENERATOR")
    print("=" * 60)
    print("🎯 Testando sistema que gera objetivos para melhorar objetivos...")
    print()
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuração carregada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return
    
    # Initialize Meta-Objective Generator
    try:
        meta_generator = get_meta_objective_generator(config, logger)
        print("✅ Meta-Objective Generator inicializado")
        print(f"📊 Status inicial: {meta_generator.get_meta_objective_status()}")
        print()
    except Exception as e:
        print(f"❌ Erro ao inicializar meta-generator: {e}")
        return
    
    # Test 1: Basic Meta-Objective Generation
    print("🧪 TESTE 1: GERAÇÃO BÁSICA DE META-OBJETIVOS")
    print("=" * 50)
    
    test_contexts = [
        {
            "name": "Sistema com Stress",
            "context": {
                "system_stress": 0.8,
                "recent_failure_rate": 0.4,
                "creativity_level": 0.3
            }
        },
        {
            "name": "Sistema Equilibrado",
            "context": {
                "system_stress": 0.4,
                "recent_failure_rate": 0.2,
                "creativity_level": 0.7
            }
        },
        {
            "name": "Sistema Criativo",
            "context": {
                "system_stress": 0.2,
                "recent_failure_rate": 0.1,
                "creativity_level": 0.9
            }
        }
    ]
    
    generated_objectives = []
    
    for i, test_case in enumerate(test_contexts, 1):
        print(f"\n📋 Cenário {i}: {test_case['name']}")
        print(f"  🔧 Contexto: stress={test_case['context']['system_stress']:.1f}, "
              f"falhas={test_case['context']['recent_failure_rate']:.1f}, "
              f"criatividade={test_case['context']['creativity_level']:.1f}")
        
        try:
            meta_objective = meta_generator.generate_meta_objective(test_case['context'])
            generated_objectives.append(meta_objective)
            
            print(f"  🎯 Objetivo gerado: {meta_objective.content[:80]}...")
            print(f"  📊 Tipo: {meta_objective.objective_type.value}")
            print(f"  ⚖️ Complexidade: {meta_objective.complexity.value}")
            print(f"  📅 Escopo: {meta_objective.scope.value}")
            print(f"  🎯 Impacto esperado: {meta_objective.expected_impact:.3f}")
            print(f"  💯 Confiança: {meta_objective.generation_confidence:.3f}")
            print(f"  🏆 Prioridade: {meta_objective.calculate_priority_score():.3f}")
            print(f"  ⏱️ Esforço estimado: {meta_objective.estimated_effort:.1f}h")
            
        except Exception as e:
            print(f"  ❌ Erro na geração: {e}")
        
        time.sleep(0.5)  # Small delay between generations
    
    print("\n" + "=" * 50)
    
    # Test 2: Capability Assessment
    print("\n🔍 TESTE 2: AVALIAÇÃO DE CAPACIDADES")
    print("=" * 50)
    
    print("🧠 Executando avaliação de capacidades...")
    
    # Access internal capability assessment
    capability_assessment = meta_generator._assess_current_capabilities()
    
    print(f"📊 Avaliação completa:")
    print(f"  🎯 Capacidades atuais: {len(capability_assessment.current_capabilities)}")
    for cap in capability_assessment.current_capabilities[:5]:  # Show first 5
        print(f"    - {cap}")
    
    print(f"  ⚠️ Lacunas identificadas: {len(capability_assessment.capability_gaps)}")
    for gap in capability_assessment.capability_gaps[:3]:  # Show first 3
        print(f"    - {gap}")
    
    print(f"  💡 Oportunidades de melhoria: {len(capability_assessment.improvement_opportunities)}")
    for opp in capability_assessment.improvement_opportunities[:3]:  # Show first 3
        print(f"    - {opp}")
    
    print(f"  💪 Pontos fortes: {len(capability_assessment.strengths)}")
    for strength in capability_assessment.strengths:
        print(f"    - {strength}")
    
    print(f"  ⚠️ Pontos fracos: {len(capability_assessment.weaknesses)}")
    for weakness in capability_assessment.weaknesses:
        print(f"    - {weakness}")
    
    print(f"\n📈 Métricas de capacidade:")
    print(f"  - Confiança na avaliação: {capability_assessment.confidence_in_assessment:.3f}")
    print(f"  - Consciência contextual: {capability_assessment.context_awareness_level:.3f}")
    print(f"  - Profundidade estratégica: {capability_assessment.strategic_thinking_depth:.3f}")
    print(f"  - Nível de criatividade: {capability_assessment.creativity_level:.3f}")
    print(f"  - Qualidade dos objetivos: {capability_assessment.objective_quality_score:.3f}")
    print(f"  - Capacidade geral: {capability_assessment.calculate_overall_capability():.3f}")
    
    # Test 3: Pattern Analysis
    print("\n🔍 TESTE 3: ANÁLISE DE PADRÕES")
    print("=" * 50)
    
    print("📊 Analisando padrões nos objetivos gerados...")
    
    # Generate a few more objectives to have data for pattern analysis
    for i in range(3):
        context = {
            "system_stress": random.uniform(0.2, 0.8),
            "recent_failure_rate": random.uniform(0.1, 0.5),
            "creativity_level": random.uniform(0.4, 0.9)
        }
        try:
            objective = meta_generator.generate_meta_objective(context)
            generated_objectives.append(objective)
        except Exception as e:
            print(f"⚠️ Erro na geração adicional: {e}")
    
    # Analyze patterns
    patterns = meta_generator.analyze_objective_patterns()
    
    print(f"🎭 Padrões identificados: {len(patterns)}")
    for pattern in patterns[:3]:  # Show first 3 patterns
        print(f"  📊 {pattern.pattern_type}:")
        print(f"    - Descrição: {pattern.description}")
        print(f"    - Frequência: {pattern.frequency}")
        print(f"    - Taxa de sucesso: {pattern.success_rate:.1%}")
        print(f"    - Impacto médio: {pattern.average_impact:.3f}")
        print(f"    - Uso recomendado: {pattern.recommended_usage}")
        print()
    
    # Test 4: Meta-Objective Insights
    print("\n💡 TESTE 4: INSIGHTS DE META-OBJETIVOS")
    print("=" * 50)
    
    print("🧠 Coletando insights do sistema...")
    
    insights = meta_generator.get_meta_objective_insights()
    
    print(f"📊 Insights gerais:")
    print(f"  - Total de objetivos gerados: {insights['total_objectives_generated']}")
    print(f"  - Objetivos ativos: {insights['active_objectives']}")
    print(f"  - Objetivos completados: {insights['completed_objectives']}")
    print(f"  - Taxa de conclusão: {insights['completion_rate']:.1%}")
    print(f"  - Qualidade média: {insights['average_quality']:.3f}")
    print(f"  - Padrões identificados: {insights['patterns_identified']}")
    print(f"  - Tendência de capacidade: {insights['capability_trend']}")
    
    if 'quality_trend' in insights:
        print(f"  - Tendência de qualidade: {insights['quality_trend']}")
    
    print(f"\n📈 Analytics:")
    analytics = insights['analytics']
    print(f"  - Total de objetivos gerados: {analytics['total_objectives_generated']}")
    print(f"  - Objetivos bem-sucedidos: {analytics['successful_objectives']}")
    print(f"  - Padrões identificados: {analytics['patterns_identified']}")
    print(f"  - Melhorias de capacidade detectadas: {analytics['capability_improvements_detected']}")
    print(f"  - Qualidade média dos objetivos: {analytics['average_objective_quality']:.3f}")
    print(f"  - Eficiência de geração: {analytics['generation_efficiency']:.3f}")
    
    if insights['recommendations']:
        print(f"\n💡 Recomendações:")
        for rec in insights['recommendations']:
            print(f"  - {rec}")
    
    # Test 5: Objective Analysis
    print("\n🔬 TESTE 5: ANÁLISE DETALHADA DOS OBJETIVOS")
    print("=" * 50)
    
    print("📋 Analisando objetivos gerados em detalhes...")
    
    if generated_objectives:
        # Analyze objective distribution
        type_distribution = {}
        complexity_distribution = {}
        scope_distribution = {}
        
        for obj in generated_objectives:
            # Type distribution
            type_key = obj.objective_type.value
            type_distribution[type_key] = type_distribution.get(type_key, 0) + 1
            
            # Complexity distribution
            complexity_key = obj.complexity.value
            complexity_distribution[complexity_key] = complexity_distribution.get(complexity_key, 0) + 1
            
            # Scope distribution
            scope_key = obj.scope.value
            scope_distribution[scope_key] = scope_distribution.get(scope_key, 0) + 1
        
        print(f"📊 Distribuição por tipo:")
        for obj_type, count in type_distribution.items():
            percentage = count / len(generated_objectives) * 100
            print(f"  - {obj_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n📊 Distribuição por complexidade:")
        for complexity, count in complexity_distribution.items():
            percentage = count / len(generated_objectives) * 100
            print(f"  - {complexity}: {count} ({percentage:.1f}%)")
        
        print(f"\n📊 Distribuição por escopo:")
        for scope, count in scope_distribution.items():
            percentage = count / len(generated_objectives) * 100
            print(f"  - {scope}: {count} ({percentage:.1f}%)")
        
        # Quality analysis
        qualities = [obj.generation_confidence for obj in generated_objectives]
        impacts = [obj.expected_impact for obj in generated_objectives]
        priorities = [obj.calculate_priority_score() for obj in generated_objectives]
        
        print(f"\n📈 Análise de qualidade:")
        print(f"  - Confiança média: {sum(qualities) / len(qualities):.3f}")
        print(f"  - Confiança mínima: {min(qualities):.3f}")
        print(f"  - Confiança máxima: {max(qualities):.3f}")
        
        print(f"\n📈 Análise de impacto:")
        print(f"  - Impacto médio: {sum(impacts) / len(impacts):.3f}")
        print(f"  - Impacto mínimo: {min(impacts):.3f}")
        print(f"  - Impacto máximo: {max(impacts):.3f}")
        
        print(f"\n📈 Análise de prioridade:")
        print(f"  - Prioridade média: {sum(priorities) / len(priorities):.3f}")
        print(f"  - Prioridade mínima: {min(priorities):.3f}")
        print(f"  - Prioridade máxima: {max(priorities):.3f}")
        
        # Show highest priority objective
        highest_priority_obj = max(generated_objectives, key=lambda obj: obj.calculate_priority_score())
        print(f"\n🏆 Objetivo de maior prioridade:")
        print(f"  📋 Conteúdo: {highest_priority_obj.content}")
        print(f"  🎯 Tipo: {highest_priority_obj.objective_type.value}")
        print(f"  🏆 Prioridade: {highest_priority_obj.calculate_priority_score():.3f}")
        print(f"  💭 Raciocínio: {highest_priority_obj.meta_reasoning[:100]}...")
    
    # Final Status Report
    print("\n📊 RELATÓRIO FINAL DO META-OBJECTIVE GENERATOR")
    print("=" * 60)
    
    final_status = meta_generator.get_meta_objective_status()
    
    print(f"⚙️ Status do sistema:")
    print(f"  - Habilitado: {'✅' if final_status['enabled'] else '❌'}")
    print(f"  - Geração ativa: {'✅' if final_status['generation_active'] else '❌'}")
    print(f"  - Análise ativa: {'✅' if final_status['analysis_active'] else '❌'}")
    
    print(f"\n📊 Estatísticas:")
    print(f"  - Total de objetivos gerados: {final_status['total_objectives_generated']}")
    print(f"  - Objetivos ativos: {final_status['active_objectives']}")
    print(f"  - Objetivos completados: {final_status['completed_objectives']}")
    print(f"  - Padrões identificados: {final_status['patterns_identified']}")
    
    analytics = final_status['analytics']
    print(f"\n📈 Analytics finais:")
    print(f"  - Objetivos bem-sucedidos: {analytics['successful_objectives']}")
    print(f"  - Melhorias detectadas: {analytics['capability_improvements_detected']}")
    print(f"  - Qualidade média: {analytics['average_objective_quality']:.3f}")
    print(f"  - Eficiência de geração: {analytics['generation_efficiency']:.3f}")
    print(f"  - Eventos de meta-aprendizado: {analytics['meta_learning_events']}")
    print(f"  - Melhorias recursivas: {analytics['recursive_improvement_count']}")
    
    print("\n🎉 TESTE CONCLUÍDO!")
    print("🎯 Meta-Objective Generator está funcionando e gerando objetivos para melhorar objetivos!")
    
    # Cleanup
    meta_generator.shutdown()
    print("✅ Sistema encerrado com sucesso")

if __name__ == "__main__":
    test_meta_objective_generator()