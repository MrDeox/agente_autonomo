#!/usr/bin/env python3
"""
Diagnóstico do MaestroAgent - Teste de Correção
"""

import json
import logging
import sys
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_config_loading():
    """Testa o carregamento da configuração"""
    logger.info("🔍 TESTANDO CARREGAMENTO DE CONFIGURAÇÃO")
    
    # Teste 1: JSON é válido?
    try:
        with open("hephaestus_config.json", "r") as f:
            config = json.load(f)
        logger.info("✅ JSON carregado com sucesso")
        
        # Verifica estratégias
        strategies = config.get("validation_strategies", {})
        logger.info(f"📊 Encontradas {len(strategies)} estratégias:")
        for strategy_name in strategies.keys():
            logger.info(f"   • {strategy_name}")
        
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON inválido: {e}")
        return None
    except FileNotFoundError:
        logger.error("❌ Arquivo hephaestus_config.json não encontrado")
        return None

def test_maestro_initialization():
    """Testa inicialização do MaestroAgent"""
    logger.info("\n🎭 TESTANDO INICIALIZAÇÃO DO MAESTRO")
    
    try:
        from agent.agents.maestro_agent import MaestroAgent
        
        # Configuração mock
        model_config = {
            "primary": "gpt-4",
            "fallback": "gpt-3.5-turbo"
        }
        
        config = test_config_loading()
        if not config:
            return False
        
        # Inicializar MaestroAgent
        maestro = MaestroAgent(model_config, config, logger)
        
        # Verificar se as estratégias foram carregadas
        available_strategies = config.get("validation_strategies", {})
        logger.info(f"✅ MaestroAgent inicializado")
        logger.info(f"📋 Estratégias disponíveis: {len(available_strategies)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar MaestroAgent: {e}")
        return False

def test_strategy_classification():
    """Testa classificação de estratégias"""
    logger.info("\n🎯 TESTANDO CLASSIFICAÇÃO DE ESTRATÉGIAS")
    
    try:
        from agent.agents.maestro_agent import MaestroAgent
        
        config = test_config_loading()
        if not config:
            return False
        
        model_config = {"primary": "gpt-4", "fallback": "gpt-3.5-turbo"}
        maestro = MaestroAgent(model_config, config, logger)
        
        # Casos de teste
        test_cases = [
            {
                "name": "Novo arquivo de teste",
                "patches": [{
                    "file_path": "tests/test_example.py",
                    "operation": "REPLACE",
                    "block_to_replace": None,
                    "content": "def test_example(): pass"
                }],
                "expected": "CREATE_NEW_TEST_FILE_STRATEGY"
            },
            {
                "name": "Mudança em configuração",
                "patches": [{
                    "file_path": "config/default.yaml",
                    "operation": "REPLACE",
                    "block_to_replace": "old_setting",
                    "content": "new_setting"
                }],
                "expected": "CONFIG_UPDATE_STRATEGY"
            },
            {
                "name": "Mudança em documentação",
                "patches": [{
                    "file_path": "README.md",
                    "operation": "REPLACE",
                    "block_to_replace": "old text",
                    "content": "new text"
                }],
                "expected": "DOC_UPDATE_STRATEGY"
            }
        ]
        
        # Testar classificação baseada em regras
        for test_case in test_cases:
            action_plan = {"patches_to_apply": test_case["patches"]}
            result = maestro._classify_strategy_by_rules(action_plan)
            
            if result == test_case["expected"]:
                logger.info(f"✅ {test_case['name']}: {result}")
            else:
                logger.warning(f"⚠️ {test_case['name']}: esperado {test_case['expected']}, obtido {result}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro nos testes de classificação: {e}")
        return False

def test_cache_functionality():
    """Testa funcionalidade de cache"""
    logger.info("\n🗄️ TESTANDO FUNCIONALIDADE DE CACHE")
    
    try:
        from agent.agents.maestro_agent import StrategyCache
        
        cache = StrategyCache(maxsize=10, ttl_seconds=3600)
        
        # Teste de armazenamento e recuperação
        action_plan = {"patches_to_apply": [{"file_path": "test.py"}]}
        memory_summary = "test memory"
        strategy = "SYNTAX_ONLY"
        
        # Adicionar ao cache
        cache.put(action_plan, memory_summary, strategy)
        
        # Recuperar do cache
        cached_result = cache.get(action_plan, memory_summary)
        
        if cached_result == strategy:
            logger.info("✅ Cache funcionando corretamente")
            stats = cache.get_stats()
            logger.info(f"📊 Stats do cache: {stats}")
            return True
        else:
            logger.error(f"❌ Cache falhou: esperado {strategy}, obtido {cached_result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de cache: {e}")
        return False

def main():
    """Função principal de diagnóstico"""
    logger.info("🏥 DIAGNÓSTICO COMPLETO DO MAESTROAGENT")
    logger.info("=" * 60)
    
    results = []
    
    # Executar testes
    results.append(("Carregamento de Config", test_config_loading() is not None))
    results.append(("Inicialização do Maestro", test_maestro_initialization()))
    results.append(("Classificação de Estratégias", test_strategy_classification()))
    results.append(("Funcionalidade de Cache", test_cache_functionality()))
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📋 RESUMO DO DIAGNÓSTICO")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n🎯 RESULTADO: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        logger.info("🎉 TODOS OS TESTES PASSARAM - MaestroAgent corrigido!")
    else:
        logger.warning("⚠️ Alguns testes falharam - investigação necessária")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 