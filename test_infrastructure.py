#!/usr/bin/env python3
"""
Teste do Infrastructure Manager
"""

import logging
from agent.utils.infrastructure_manager import get_infrastructure_manager

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Testa o gerenciador de infraestrutura"""
    logger.info("🧪 TESTANDO INFRASTRUCTURE MANAGER")
    logger.info("=" * 50)
    
    # Obter gerenciador
    manager = get_infrastructure_manager(logger)
    
    # 1. Diagnóstico inicial
    logger.info("\n1️⃣ DIAGNÓSTICO INICIAL")
    diagnosis = manager.diagnose_system()
    
    logger.info(f"Issues encontradas: {len(diagnosis['issues'])}")
    for issue in diagnosis['issues']:
        logger.info(f"   ❌ {issue}")
    
    # 2. Status do sistema
    status = manager.get_system_status()
    logger.info(f"\n📊 STATUS DO SISTEMA:")
    logger.info(f"   • Saúde geral: {status['overall_health']}")
    logger.info(f"   • Diretórios: {status['directories']}")
    logger.info(f"   • Arquivos: {status['files']}")
    logger.info(f"   • Configurações: {status['configurations']}")
    logger.info(f"   • Issues totais: {status['total_issues']}")
    
    # 3. Corrigir problemas
    if diagnosis['issues']:
        logger.info("\n🔧 CORRIGINDO PROBLEMAS...")
        fixed = manager.fix_infrastructure_issues(diagnosis)
        if fixed:
            logger.info("✅ Todos os problemas foram corrigidos!")
        else:
            logger.warning("⚠️ Alguns problemas não puderam ser corrigidos")
    else:
        logger.info("\n✅ Nenhum problema encontrado!")
    
    # 4. Verificação final
    logger.info("\n4️⃣ VERIFICAÇÃO FINAL")
    final_status = manager.ensure_infrastructure()
    
    if final_status:
        logger.info("🎉 INFRAESTRUTURA ÍNTEGRA E FUNCIONAL!")
    else:
        logger.error("❌ Ainda há problemas na infraestrutura")
    
    return final_status

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 