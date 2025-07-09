#!/usr/bin/env python3
"""
Script de teste para verificar se o hot reload está funcionando
"""

import time
import logging
from pathlib import Path
from src.hephaestus.core.hot_reload_manager import HotReloadManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hot_reload():
    """Testa o sistema de hot reload"""
    logger.info("🔄 Iniciando teste de hot reload...")
    
    # Criar instance do hot reload manager
    hot_reload_manager = HotReloadManager(logger)
    
    # Tentar adicionar um módulo
    try:
        hot_reload_manager.add_module("hephaestus.core.agent")
        logger.info("✅ Módulo adicionado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro adicionando módulo: {e}")
        return False
    
    # Tentar iniciar watching
    try:
        src_path = str(Path("src/hephaestus").absolute())
        hot_reload_manager.start_watching(src_path)
        logger.info(f"✅ Watching iniciado em: {src_path}")
        
        # Verificar status
        watched_modules = hot_reload_manager.get_watched_modules()
        logger.info(f"📋 Módulos sendo observados: {list(watched_modules.keys())}")
        
        # Aguardar um pouco
        logger.info("⏱️ Aguardando 5 segundos...")
        time.sleep(5)
        
        # Parar watching
        hot_reload_manager.stop_watching()
        logger.info("🛑 Watching parado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no watching: {e}")
        return False

if __name__ == "__main__":
    success = test_hot_reload()
    if success:
        print("✅ Hot reload test passed!")
    else:
        print("❌ Hot reload test failed!")