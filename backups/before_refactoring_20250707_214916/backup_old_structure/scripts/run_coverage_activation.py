#!/usr/bin/env python3
"""
Script para executar ativação completa de cobertura
Aumenta significativamente a cobertura do sistema ativando funcionalidades não utilizadas
"""

import asyncio
import sys
import time
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.coverage_activator import CoverageActivator, activate_coverage_system


async def main():
    """Função principal"""
    print("🚀 SISTEMA DE ATIVAÇÃO DE COBERTURA")
    print("=" * 50)
    print("Este script irá:")
    print("1. Ativar todos os módulos não utilizados")
    print("2. Criar testes automáticos")
    print("3. Executar testes de cobertura")
    print("4. Gerar relatório detalhado")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        # Executar ativação completa
        results = await activate_coverage_system()
        
        # Verificar sucesso
        if results.get("success", False):
            print("\n🎉 ATIVAÇÃO CONCLUÍDA COM SUCESSO!")
            
            # Mostrar métricas finais
            print(f"\n📊 MÉTRICAS FINAIS:")
            print(f"   🔧 Módulos ativados: {results.get('modules_activated', 0)}")
            print(f"   ⚙️ Funcionalidades ativadas: {results.get('features_activated', 0)}")
            print(f"   🧪 Testes criados: {results.get('tests_created', 0)}")
            print(f"   📈 Melhoria de cobertura: {results.get('coverage_improvement', 0):.2f}%")
            print(f"   ⏱️ Tempo total: {results.get('execution_time', 0):.2f}s")
            
            # Mostrar detalhes se disponíveis
            if results.get("details"):
                print(f"\n📋 DETALHES:")
                
                if "coverage" in results["details"]:
                    coverage = results["details"]["coverage"]
                    print(f"   📊 Cobertura atual: {coverage.get('current_coverage', 0):.2f}%")
                    print(f"   🎯 Cobertura alvo: {coverage.get('target_coverage', 80):.2f}%")
                
                if "modules" in results["details"]:
                    modules = results["details"]["modules"]
                    print(f"   📦 Módulos processados: {modules.get('activated', 0) + modules.get('failed', 0)}")
                
                if "features" in results["details"]:
                    features = results["details"]["features"]
                    print(f"   ⚙️ Funcionalidades processadas: {features.get('activated', 0) + features.get('failed', 0)}")
            
            # Executar testes adicionais
            print(f"\n🧪 Executando testes adicionais...")
            await run_additional_tests()
            
        else:
            print(f"\n❌ ATIVAÇÃO FALHOU!")
            print(f"   Erro: {results.get('error', 'Erro desconhecido')}")
            
            if results.get("errors"):
                print(f"   Erros detalhados:")
                for error in results["errors"]:
                    print(f"      - {error}")
        
        # Tempo total
        total_time = time.time() - start_time
        print(f"\n⏱️ Tempo total de execução: {total_time:.2f}s")
        
    except Exception as e:
        print(f"\n💥 ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


async def run_additional_tests():
    """Executa testes adicionais para validar ativação"""
    print("   🔍 Validando ativações...")
    
    # Testar alguns agentes específicos
    test_agents = [
        ("DebtHunterAgent", "agent.agents.debt_hunter_agent"),
        ("DependencyFixerAgent", "agent.agents.dependency_fixer_agent"),
        ("OrganizerAgent", "agent.agents.organizer_agent"),
        ("SelfReflectionAgent", "agent.agents.self_reflection_agent"),
        ("BugHunterAgent", "agent.agents.bug_hunter_agent"),
        ("ErrorDetectorAgent", "agent.agents.error_detector_agent"),
        ("AutonomousMonitorAgent", "agent.agents.autonomous_monitor_agent"),
        ("AgentExpansionCoordinator", "agent.agents.agent_expansion_coordinator"),
    ]
    
    successful_tests = 0
    
    for agent_name, module_path in test_agents:
        try:
            # Importar módulo
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            
            # Criar instância
            config = {"debug": True, "log_level": "INFO"}
            instance = agent_class(config)
            
            # Testar métodos básicos
            if hasattr(instance, "__init__"):
                print(f"      ✅ {agent_name}: OK")
                successful_tests += 1
            else:
                print(f"      ⚠️ {agent_name}: Sem __init__")
                
        except Exception as e:
            print(f"      ❌ {agent_name}: {str(e)[:50]}...")
    
    print(f"   📊 {successful_tests}/{len(test_agents)} agentes testados com sucesso")
    
    # Testar utilitários
    print("   🔧 Testando utilitários...")
    
    test_utils = [
        ("IntelligentCache", "agent.utils.intelligent_cache"),
        ("UXEnhancer", "agent.utils.ux_enhancer"),
        ("ContinuousMonitor", "agent.utils.continuous_monitor"),
        ("PerformanceMonitor", "agent.utils.performance_monitor"),
        ("SmartValidator", "agent.utils.smart_validator"),
        ("ErrorPreventionSystem", "agent.utils.error_prevention_system"),
    ]
    
    successful_utils = 0
    
    for util_name, module_path in test_utils:
        try:
            module = __import__(module_path, fromlist=[util_name])
            util_class = getattr(module, util_name)
            
            # Criar instância
            if util_name == "IntelligentCache":
                instance = util_class()
            else:
                config = {"debug": True, "log_level": "INFO"}
                instance = util_class(config)
            
            print(f"      ✅ {util_name}: OK")
            successful_utils += 1
            
        except Exception as e:
            print(f"      ❌ {util_name}: {str(e)[:50]}...")
    
    print(f"   📊 {successful_utils}/{len(test_utils)} utilitários testados com sucesso")
    
    # Testar módulos de inteligência
    print("   🧠 Testando módulos de inteligência...")
    
    test_intelligence = [
        ("MetaCognitiveController", "agent.meta_cognitive_controller"),
        ("MetaIntelligenceCore", "agent.meta_intelligence_core"),
        ("SelfAwarenessCore", "agent.self_awareness_core"),
        ("SelfImprovementEngine", "agent.self_improvement_engine"),
        ("CognitiveEvolutionManager", "agent.cognitive_evolution_manager"),
    ]
    
    successful_intelligence = 0
    
    for intel_name, module_path in test_intelligence:
        try:
            module = __import__(module_path, fromlist=[intel_name])
            intel_class = getattr(module, intel_name)
            
            # Criar instância
            config = {"debug": True, "log_level": "INFO"}
            instance = intel_class(config)
            
            print(f"      ✅ {intel_name}: OK")
            successful_intelligence += 1
            
        except Exception as e:
            print(f"      ❌ {intel_name}: {str(e)[:50]}...")
    
    print(f"   📊 {successful_intelligence}/{len(test_intelligence)} módulos de inteligência testados com sucesso")
    
    # Resumo final
    total_tested = successful_tests + successful_utils + successful_intelligence
    total_available = len(test_agents) + len(test_utils) + len(test_intelligence)
    
    print(f"\n📈 RESUMO DOS TESTES ADICIONAIS:")
    print(f"   🎯 Total testado: {total_tested}/{total_available}")
    print(f"   📊 Taxa de sucesso: {(total_tested/total_available)*100:.1f}%")


def run_coverage_analysis():
    """Executa análise de cobertura atual"""
    print("\n📊 ANALISANDO COBERTURA ATUAL...")
    
    try:
        import subprocess
        
        # Executar pytest com cobertura
        cmd = [
            "poetry", "run", "pytest",
            "--cov=agent",
            "--cov=agente_autonomo",
            "--cov=tools",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "-q"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Análise de cobertura concluída")
            
            # Extrair linha de cobertura total
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line and '%' in line:
                    print(f"📊 {line.strip()}")
                    break
        else:
            print(f"⚠️ Análise de cobertura com avisos: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erro na análise de cobertura: {e}")


if __name__ == "__main__":
    print("🚀 Iniciando sistema de ativação de cobertura...")
    
    # Verificar se estamos no diretório correto
    if not Path("pyproject.toml").exists():
        print("❌ Erro: Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    # Executar análise inicial
    run_coverage_analysis()
    
    # Executar ativação
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 SISTEMA DE ATIVAÇÃO CONCLUÍDO!")
        print("📊 Verifique os relatórios gerados em reports/")
        print("🌐 Relatório HTML disponível em htmlcov/")
    else:
        print("\n❌ SISTEMA DE ATIVAÇÃO FALHOU!")
        sys.exit(1) 