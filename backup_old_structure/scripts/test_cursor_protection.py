#!/usr/bin/env python3
"""
Script para testar a proteção do Cursor IDE contra o CycleMonitorAgent
"""

import sys
import os
import time
import psutil
import logging
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.config_loader import load_config
from agent.agents.cycle_monitor_agent import CycleMonitorAgent

def setup_logging():
    """Configura logging para o teste"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/cursor_protection_test.log')
        ]
    )
    return logging.getLogger("cursor_protection_test")

def find_cursor_processes():
    """Encontra processos do Cursor IDE"""
    cursor_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'cursor' in proc.info['name'].lower():
                cursor_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return cursor_processes

def test_cursor_protection():
    """Testa se o Cursor está sendo protegido"""
    logger = setup_logging()
    logger.info("🧪 Iniciando teste de proteção do Cursor IDE")
    
    try:
        # Carregar configuração
        config = load_config()
        logger.info("✅ Configuração carregada")
        
        # Criar CycleMonitorAgent
        cycle_monitor = CycleMonitorAgent(config)
        logger.info("✅ CycleMonitorAgent criado")
        
        # Verificar processos do Cursor
        cursor_processes = find_cursor_processes()
        logger.info(f"🔍 Encontrados {len(cursor_processes)} processos do Cursor:")
        
        for proc in cursor_processes:
            logger.info(f"   • PID {proc['pid']}: {proc['name']}")
        
        # Verificar se Cursor está na lista de protegidos
        cursor_protected = 'cursor' in cycle_monitor.protected_processes
        logger.info(f"🛡️ Cursor na lista de protegidos: {'✅ SIM' if cursor_protected else '❌ NÃO'}")
        
        # Mostrar lista completa de processos protegidos
        logger.info("📋 Lista de processos protegidos:")
        for proc in cycle_monitor.protected_processes:
            logger.info(f"   • {proc}")
        
        # Simular detecção de processos travados
        logger.info("🔍 Simulando detecção de processos travados...")
        stuck_processes = cycle_monitor._detect_stuck_processes()
        
        if stuck_processes:
            logger.warning(f"⚠️ Encontrados {len(stuck_processes)} processos travados:")
            for proc in stuck_processes:
                logger.warning(f"   • {proc['name']} (PID: {proc['pid']}) - CPU: {proc['cpu_percent']}%")
        else:
            logger.info("✅ Nenhum processo travado detectado (processos protegidos ignorados)")
        
        # Verificar se algum processo do Cursor foi detectado como travado
        cursor_detected = any('cursor' in proc['name'].lower() for proc in stuck_processes)
        
        if cursor_detected:
            logger.error("❌ ERRO: Cursor foi detectado como processo travado!")
            return False
        else:
            logger.info("✅ SUCESSO: Cursor não foi detectado como processo travado")
            return True
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🛡️ Teste de Proteção do Cursor IDE")
    print("=" * 50)
    
    # Criar diretório de logs se não existir
    Path("logs").mkdir(exist_ok=True)
    
    # Executar teste
    success = test_cursor_protection()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        print("🛡️ Cursor IDE está protegido contra o CycleMonitorAgent")
    else:
        print("\n❌ Teste falhou!")
        print("⚠️ Cursor IDE ainda pode ser morto pelo CycleMonitorAgent")
        sys.exit(1)

if __name__ == "__main__":
    main() 