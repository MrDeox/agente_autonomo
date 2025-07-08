#!/usr/bin/env python3
"""
🔍 Monitor de Evolução em Tempo Real
Monitora o sistema Hephaestus para ver execução vs evolução
"""

import time
import json
import os
from datetime import datetime
from pathlib import Path

def monitor_system():
    """Monitora o sistema em tempo real"""
    
    print("🔍 MONITOR DE EVOLUÇÃO HEPHAESTUS")
    print("=" * 60)
    print("🎯 Monitorando: Execução vs Evolução vs Mutação")
    print("📊 Atualizando a cada 30 segundos...")
    print("❌ Ctrl+C para sair")
    print()
    
    last_cycle = 0
    last_mutation = 0
    start_time = datetime.now()
    
    try:
        while True:
            # Limpa a tela (compatível com Linux/Mac/Windows)
            os.system('clear' if os.name == 'posix' else 'cls')
            
            print("🔍 MONITOR DE EVOLUÇÃO HEPHAESTUS")
            print("=" * 60)
            print(f"⏰ Tempo de monitoramento: {datetime.now() - start_time}")
            print(f"🕐 Atualizado: {datetime.now().strftime('%H:%M:%S')}")
            print()
            
            # 1. Status do sistema principal
            try:
                memory_path = Path("data/memory/HEPHAESTUS_MEMORY.json")
                if memory_path.exists():
                    with open(memory_path, 'r') as f:
                        memory = json.load(f)
                    
                    completed = len(memory.get("completed_objectives", []))
                    failed = len(memory.get("failed_objectives", []))
                    total = completed + failed
                    success_rate = (completed / total * 100) if total > 0 else 0
                    
                    print("🎯 STATUS PRINCIPAL:")
                    print(f"  ✅ Objetivos concluídos: {completed}")
                    print(f"  ❌ Objetivos falharam: {failed}")
                    print(f"  📊 Taxa de sucesso: {success_rate:.1f}%")
                    print()
                else:
                    print("🎯 STATUS PRINCIPAL: Arquivo de memória não encontrado")
                    print()
            except Exception as e:
                print(f"🎯 STATUS PRINCIPAL: Erro ao ler memória - {e}")
                print()
            
            # 2. Logs de ciclos (evolution_log.csv)
            try:
                evolution_log = Path("data/logs/evolution_log.csv")
                if evolution_log.exists():
                    lines = evolution_log.read_text().strip().split('\n')
                    current_cycles = len(lines) - 1  # -1 for header
                    
                    if current_cycles > last_cycle:
                        new_cycles = current_cycles - last_cycle
                        print(f"🔄 CICLOS DE EXECUÇÃO: +{new_cycles} novos ciclos!")
                        last_cycle = current_cycles
                    
                    print(f"🔄 Total de ciclos executados: {current_cycles}")
                    
                    # Últimos ciclos
                    if len(lines) > 1:
                        recent_lines = lines[-3:] if len(lines) > 3 else lines[1:]
                        print("📋 Últimos ciclos:")
                        for line in recent_lines:
                            if ',' in line:
                                parts = line.split(',')
                                if len(parts) >= 3:
                                    ciclo = parts[0]
                                    status = parts[2]
                                    tempo = parts[3] if len(parts) > 3 else "N/A"
                                    print(f"    Ciclo {ciclo}: {status} ({tempo}s)")
                    print()
                else:
                    print("🔄 CICLOS DE EXECUÇÃO: Log não encontrado")
                    print()
            except Exception as e:
                print(f"🔄 CICLOS DE EXECUÇÃO: Erro - {e}")
                print()
            
            # 3. Real-Time Evolution Engine
            try:
                evolution_data_path = Path("data/reports/evolution_state_*.json")
                evolution_files = list(Path("data/reports/").glob("evolution_state_*.json"))
                
                if evolution_files:
                    latest_file = max(evolution_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_file, 'r') as f:
                        evolution_data = json.load(f)
                    
                    mutations = evolution_data.get("active_mutations", [])
                    current_mutations = len(mutations)
                    
                    if current_mutations > last_mutation:
                        new_mutations = current_mutations - last_mutation
                        print(f"⚡ EVOLUÇÃO EM TEMPO REAL: +{new_mutations} novas mutações!")
                        last_mutation = current_mutations
                    
                    print("⚡ EVOLUÇÃO EM TEMPO REAL:")
                    print(f"  🧬 Mutações ativas: {current_mutations}")
                    print(f"  📈 Candidatos testados: {evolution_data.get('total_candidates', 0)}")
                    print(f"  🏆 Evoluções aplicadas: {evolution_data.get('deployed_evolutions', 0)}")
                    
                    if mutations:
                        print("  🔬 Mutações ativas:")
                        for mut in mutations[-3:]:  # Last 3
                            print(f"    - {mut.get('type', 'Unknown')}: {mut.get('description', 'No description')[:50]}...")
                    print()
                else:
                    print("⚡ EVOLUÇÃO EM TEMPO REAL: Aguardando dados...")
                    print()
            except Exception as e:
                print(f"⚡ EVOLUÇÃO EM TEMPO REAL: Erro - {e}")
                print()
            
            # 4. API Key Status
            try:
                api_config_path = Path("data/api_keys_config.json")
                if api_config_path.exists():
                    with open(api_config_path, 'r') as f:
                        api_data = json.load(f)
                    
                    stats = api_data.get("stats", {})
                    total_calls = stats.get("total_calls", 0)
                    successful_calls = stats.get("successful_calls", 0)
                    api_success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
                    
                    print("🔑 STATUS DAS CHAVES API:")
                    print(f"  📞 Total de chamadas: {total_calls}")
                    print(f"  ✅ Chamadas bem-sucedidas: {successful_calls}")
                    print(f"  📊 Taxa de sucesso API: {api_success_rate:.1f}%")
                    print(f"  🔄 Fallbacks usados: {stats.get('fallback_usage', 0)}")
                else:
                    print("🔑 STATUS DAS CHAVES API: Aguardando dados...")
                print()
            except Exception as e:
                print(f"🔑 STATUS DAS CHAVES API: Erro - {e}")
                print()
            
            print("📱 Pressione Ctrl+C para sair...")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor encerrado. Tchau!")

if __name__ == "__main__":
    monitor_system()