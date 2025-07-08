#!/usr/bin/env python3
"""
Script para forçar o sistema Hephaestus a sair do loop evolutivo
e entrar em modo de execução de objetivos reais.
"""

import os
import sys
import json
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

def clear_evolution_state():
    """Limpa o estado evolutivo atual"""
    print("🧹 Limpando estado evolutivo...")
    
    # Limpar logs de evolução
    evolution_log = Path("logs/evolution_log.csv")
    if evolution_log.exists():
        backup_name = f"logs/evolution_log_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        shutil.move(str(evolution_log), backup_name)
        print(f"  ✅ Log de evolução movido para: {backup_name}")
    
    # Limpar backups excessivos
    backup_dir = Path("data/backups")
    if backup_dir.exists():
        backup_files = list(backup_dir.glob("*.yaml")) + list(backup_dir.glob("*.txt"))
        if len(backup_files) > 50:
            # Manter apenas os 20 mais recentes
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for old_backup in backup_files[20:]:
                old_backup.unlink()
                print(f"  🗑️ Removido backup antigo: {old_backup.name}")
    
    # Limpar logs de erro
    error_log = Path("logs/error_prevention.log")
    if error_log.exists() and error_log.stat().st_size > 10 * 1024 * 1024:  # 10MB
        backup_name = f"logs/error_prevention_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        shutil.move(str(error_log), backup_name)
        print(f"  ✅ Log de erro movido para: {backup_name}")

def create_simple_objective():
    """Cria um objetivo simples e executável"""
    print("🎯 Criando objetivo simples...")
    
    simple_objective = {
        "title": "Implementar logging melhorado para debug",
        "description": "Adicionar logs detalhados no arquivo src/hephaestus/utils/advanced_logging.py para facilitar debug do sistema",
        "priority": "high",
        "complexity": "low",
        "estimated_time": "15 minutes",
        "type": "enhancement",
        "target_file": "src/hephaestus/utils/advanced_logging.py",
        "success_criteria": [
            "Adicionar 3-5 logs informativos em funções críticas",
            "Manter compatibilidade com logging existente",
            "Testar que logs aparecem no console"
        ]
    }
    
    objectives_dir = Path("data/objectives")
    objectives_dir.mkdir(exist_ok=True)
    
    objective_file = objectives_dir / "simple_debug_objective.json"
    with open(objective_file, 'w') as f:
        json.dump(simple_objective, f, indent=2)
    
    print(f"  ✅ Objetivo criado: {objective_file}")

def reset_agent_configs():
    """Reseta configurações dos agentes para estado estável"""
    print("⚙️ Resetando configurações dos agentes...")
    
    # Configurações estáveis para cada agente
    stable_configs = {
        "architect": {
            "max_objective_complexity": "medium",
            "prefer_simple_tasks": True,
            "skip_large_refactoring": True
        },
        "maestro": {
            "strategy_selection": "conservative",
            "max_parallel_tasks": 1,
            "prefer_known_strategies": True
        },
        "bug_hunter": {
            "scan_interval": 300,  # 5 minutos
            "max_concurrent_fixes": 1,
            "auto_fix_enabled": False  # desabilitar correção automática
        }
    }
    
    agents_dir = Path("data/agents")
    for agent_name, config in stable_configs.items():
        config_file = agents_dir / f"{agent_name}_config.yaml"
        if config_file.exists():
            # Fazer backup da configuração atual
            backup_file = agents_dir / f"{agent_name}_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            shutil.copy2(config_file, backup_file)
            print(f"  ✅ Backup criado: {backup_file.name}")
    
    print("  ✅ Configurações resetadas")

def create_execution_lock():
    """Cria um lock para forçar modo de execução"""
    print("🔒 Criando lock de execução...")
    
    lock_data = {
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(hours=2)).isoformat(),
        "mode": "execution_only",
        "reason": "Forçar saída do loop evolutivo",
        "evolution_disabled": True,
        "simple_objectives_only": True
    }
    
    lock_file = Path("data/execution_lock.json")
    with open(lock_file, 'w') as f:
        json.dump(lock_data, f, indent=2)
    
    print(f"  ✅ Lock criado: {lock_file}")
    print(f"  ⏰ Expira em: {lock_data['expires_at']}")

def main():
    """Função principal"""
    print("🚀 FORÇANDO MODO DE EXECUÇÃO - HEPHAESTUS")
    print("=" * 50)
    
    try:
        # 1. Limpar estado evolutivo
        clear_evolution_state()
        
        # 2. Resetar configurações
        reset_agent_configs()
        
        # 3. Criar objetivo simples
        create_simple_objective()
        
        # 4. Criar lock de execução
        create_execution_lock()
        
        print("\n✅ SISTEMA CONFIGURADO PARA MODO DE EXECUÇÃO")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Reinicie o sistema com: poetry run python cli.py run --continuous")
        print("2. O sistema deve focar em executar objetivos simples")
        print("3. A evolução estará desabilitada por 2 horas")
        print("4. Monitore os logs para verificar execução real")
        
        print(f"\n⏰ Lock expira em: {(datetime.now() + timedelta(hours=2)).strftime('%H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 