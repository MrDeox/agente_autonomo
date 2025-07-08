#!/usr/bin/env python3
"""
🧪 Teste do Parallel Reality Testing System
Testa a 3ª meta-funcionalidade: execução de múltiplas estratégias em paralelo
"""

import sys
import asyncio
import logging
sys.path.append('src')

from hephaestus.intelligence.parallel_reality_testing import get_parallel_reality_tester
from hephaestus.utils.config_loader import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestParallelReality")

async def test_parallel_reality_system():
    """Testa o sistema de realidades paralelas"""
    
    print("🧪 TESTE DO PARALLEL REALITY TESTING SYSTEM")
    print("=" * 60)
    print("🎯 Testando execução de múltiplas estratégias em paralelo...")
    print()
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuração carregada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
        return
    
    # Initialize Parallel Reality Tester
    try:
        tester = get_parallel_reality_tester(config, logger)
        print("✅ Parallel Reality Tester inicializado")
        print(f"📊 Status: {tester.get_system_status()}")
        print()
    except Exception as e:
        print(f"❌ Erro ao inicializar tester: {e}")
        return
    
    # Test objectives with different complexity levels
    test_objectives = [
        {
            "objective": "Create a simple function to calculate the sum of two numbers",
            "complexity": "low",
            "expected_strategies": ["aggressive", "optimized", "experimental"]
        },
        {
            "objective": "Refactor the large agent.py file (2435 LOC) into smaller modules while maintaining all functionality and adding comprehensive tests",
            "complexity": "high", 
            "expected_strategies": ["conservative", "balanced", "experimental"]
        },
        {
            "objective": "Implement a new feature for user authentication with database integration and error handling",
            "complexity": "medium",
            "expected_strategies": ["balanced", "aggressive", "optimized"]
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_objectives, 1):
        print(f"🎯 TESTE {i}/3: {test_case['complexity'].upper()} COMPLEXITY")
        print(f"📝 Objetivo: {test_case['objective'][:80]}...")
        print()
        
        try:
            # Execute parallel reality testing
            start_time = asyncio.get_event_loop().time()
            
            winner_test, session = await tester.test_multiple_realities(
                objective=test_case['objective'],
                context={"test_mode": True, "complexity": test_case['complexity']}
            )
            
            end_time = asyncio.get_event_loop().time()
            execution_time = end_time - start_time
            
            # Analyze results
            print(f"⏱️ Tempo de execução: {execution_time:.2f}s")
            print(f"🧪 Estratégias testadas: {len(session.reality_tests)}")
            
            if winner_test:
                print(f"🏆 Estratégia vencedora: {winner_test.strategy_name}")
                print(f"📊 Score composto: {winner_test.composite_score:.3f}")
                print(f"✅ Probabilidade de sucesso: {winner_test.success_probability:.1%}")
                print(f"⚡ Score de eficiência: {winner_test.efficiency_score:.3f}")
                print(f"🎯 Score de qualidade: {winner_test.quality_score:.3f}")
                print(f"⚠️ Score de risco: {winner_test.risk_score:.3f}")
            else:
                print("❌ Nenhuma estratégia vencedora identificada")
            
            # Show all strategies tested
            print("\n📋 Detalhes de todas as estratégias:")
            for test in session.reality_tests:
                status_icon = {"completed": "✅", "failed": "❌", "terminated_early": "⏹️", "winner": "🏆"}.get(test.status.value, "❓")
                print(f"  {status_icon} {test.strategy_name} ({test.strategy_type.value}): {test.composite_score:.3f}")
            
            # Learning insights
            if session.learning_insights:
                print("\n🧠 Insights aprendidos:")
                for insight in session.learning_insights:
                    print(f"  💡 {insight}")
            
            results.append({
                "test_case": test_case,
                "winner": winner_test.strategy_name if winner_test else None,
                "winner_score": winner_test.composite_score if winner_test else 0,
                "strategies_tested": len(session.reality_tests),
                "execution_time": execution_time,
                "session_id": session.session_id
            })
            
        except Exception as e:
            print(f"❌ Erro durante teste: {e}")
            logger.exception("Error during parallel reality test")
        
        print("\n" + "=" * 60 + "\n")
    
    # Final analysis
    print("📊 ANÁLISE FINAL DOS RESULTADOS")
    print("=" * 60)
    
    if results:
        total_strategies = sum(r["strategies_tested"] for r in results)
        avg_execution_time = sum(r["execution_time"] for r in results) / len(results)
        successful_tests = len([r for r in results if r["winner"]])
        
        print(f"✅ Testes bem-sucedidos: {successful_tests}/{len(results)}")
        print(f"🧪 Total de estratégias testadas: {total_strategies}")
        print(f"⏱️ Tempo médio de execução: {avg_execution_time:.2f}s")
        print()
        
        print("🏆 Estratégias vencedoras por teste:")
        for i, result in enumerate(results, 1):
            complexity = result["test_case"]["complexity"]
            winner = result["winner"] or "Nenhuma"
            score = result["winner_score"]
            print(f"  {i}. {complexity.capitalize()}: {winner} (score: {score:.3f})")
        
        # Strategy performance summary
        strategy_performance = tester.get_strategy_performance_summary()
        if strategy_performance:
            print("\n📈 Performance das estratégias:")
            for strategy_type, stats in strategy_performance.items():
                print(f"  📊 {strategy_type}: avg={stats['average_score']:.3f}, best={stats['best_score']:.3f}, tests={stats['total_tests']}")
        
        print("\n🎯 CONCLUSÃO:")
        if successful_tests == len(results):
            print("🎉 TODOS OS TESTES PASSARAM! Parallel Reality Testing está funcionando perfeitamente!")
        elif successful_tests > 0:
            print(f"⚠️ {successful_tests} de {len(results)} testes passaram. Sistema parcialmente funcional.")
        else:
            print("❌ Nenhum teste passou. Sistema precisa de correções.")
    
    else:
        print("❌ Nenhum resultado para analisar")
    
    # System status
    print(f"\n🔧 Status final do sistema: {tester.get_system_status()}")
    
    # Cleanup
    tester.shutdown()
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_parallel_reality_system())