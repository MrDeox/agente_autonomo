#!/usr/bin/env python3
"""
Script para testar a ativação de funcionalidades não utilizadas
"""

import sys
import os
import logging
import time
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config_loader import load_config
from agent.system_activator import get_system_activator

def setup_logging():
    """Configura logging para o teste"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/feature_activation_test.log')
        ]
    )
    return logging.getLogger("feature_activation_test")

def test_feature_activation():
    """Testa a ativação de funcionalidades"""
    logger = setup_logging()
    logger.info("🧪 Iniciando teste de ativação de funcionalidades")
    
    try:
        # Carregar configuração
        config = load_config()
        logger.info("✅ Configuração carregada")
        
        # Criar ativador do sistema
        activator = get_system_activator(logger, config)
        logger.info("✅ SystemActivator criado")
        
        # Ativar todas as funcionalidades
        logger.info("🚀 Iniciando ativação de funcionalidades...")
        start_time = time.time()
        
        results = activator.activate_all_features()
        
        end_time = time.time()
        activation_time = end_time - start_time
        
        # Gerar relatório
        report = activator.get_activation_report()
        active_features = activator.get_active_features()
        
        # Mostrar resultados
        logger.info("=" * 60)
        logger.info("📊 RESULTADOS DO TESTE DE ATIVAÇÃO")
        logger.info("=" * 60)
        logger.info(f"⏱️  Tempo total: {activation_time:.2f} segundos")
        logger.info(f"✅ Funcionalidades ativadas: {len(active_features)}")
        logger.info(f"📈 Taxa de sucesso: {(len(active_features)/len(activator.features_to_activate)*100):.1f}%")
        
        logger.info("\n🎯 FUNCIONALIDADES ATIVAS:")
        for feature in active_features:
            logger.info(f"   • {feature}")
        
        logger.info("\n📋 RELATÓRIO DETALHADO:")
        logger.info(report)
        
        # Verificar funcionalidades específicas
        logger.info("\n🔍 VERIFICAÇÃO DE FUNCIONALIDADES ESPECÍFICAS:")
        
        # Testar cache inteligente
        try:
            from agent.utils.intelligent_cache import IntelligentCache
            cache = IntelligentCache()
            cache.set("test_key", "test_value", ttl=60)
            result = cache.get("test_key")
            if result == "test_value":
                logger.info("   ✅ Cache inteligente funcionando")
            else:
                logger.warning("   ⚠️ Cache inteligente com problema")
        except Exception as e:
            logger.error(f"   ❌ Erro no cache inteligente: {e}")
        
        # Testar UX enhancer
        try:
            from agent.utils.ux_enhancer import UXEnhancer
            ux = UXEnhancer()
            welcome_msg = ux.format_welcome_message("Test User")
            logger.info(f"   ✅ UX enhancer funcionando: {welcome_msg}")
        except Exception as e:
            logger.error(f"   ❌ Erro no UX enhancer: {e}")
        
        # Testar monitor contínuo
        try:
            from agent.utils.continuous_monitor import get_continuous_monitor
            monitor = get_continuous_monitor(logger)
            if monitor:
                logger.info("   ✅ Monitor contínuo funcionando")
            else:
                logger.warning("   ⚠️ Monitor contínuo com problema")
        except Exception as e:
            logger.error(f"   ❌ Erro no monitor contínuo: {e}")
        
        # Testar validador inteligente
        try:
            from agent.utils.smart_validator import SmartValidator
            validator = SmartValidator()
            if validator:
                logger.info("   ✅ Validador inteligente funcionando")
            else:
                logger.warning("   ⚠️ Validador inteligente com problema")
        except Exception as e:
            logger.error(f"   ❌ Erro no validador inteligente: {e}")
        
        logger.info("\n🎉 Teste de ativação concluído com sucesso!")
        
        return {
            "success": True,
            "activated_features": active_features,
            "total_activated": len(active_features),
            "activation_time": activation_time,
            "report": report
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no teste de ativação: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Função principal"""
    print("🚀 Teste de Ativação de Funcionalidades do Hephaestus")
    print("=" * 60)
    
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    # Executar teste
    result = test_feature_activation()
    
    if result["success"]:
        print(f"\n✅ Teste concluído com sucesso!")
        print(f"📊 Funcionalidades ativadas: {result['total_activated']}")
        print(f"⏱️  Tempo de ativação: {result['activation_time']:.2f}s")
    else:
        print(f"\n❌ Teste falhou: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 