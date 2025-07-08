#!/usr/bin/env python3
"""
🔍 ANALISADOR DE META-FUNCIONALIDADES
Script para analisar os logs e verificar se todas as 6 meta-funcionalidades estão operacionais
"""

import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import time

def analyze_logs():
    """Analisa logs para verificar status das meta-funcionalidades"""
    
    print("🔍 ANÁLISE DE META-FUNCIONALIDADES EM TEMPO REAL")
    print("=" * 70)
    print("📊 Verificando se todas as 6 meta-funcionalidades estão operacionais...")
    print()
    
    # Meta-funcionalidades esperadas
    meta_functionalities = {
        "1_predictive_failure": {
            "name": "Predictive Failure Engine",
            "keywords": ["PredictiveFailureEngine", "failure probability", "preventive"],
            "active": False,
            "last_activity": None,
            "activity_count": 0
        },
        "2_real_time_evolution": {
            "name": "Real-Time Evolution Engine", 
            "keywords": ["RealTimeEvolutionEngine", "mutation", "evolution", "fitness"],
            "active": False,
            "last_activity": None,
            "activity_count": 0
        },
        "3_parallel_reality": {
            "name": "Parallel Reality Testing",
            "keywords": ["ParallelRealityTester", "strategy", "parallel", "A/B testing"],
            "active": False,
            "last_activity": None,
            "activity_count": 0
        },
        "4_meta_learning": {
            "name": "Meta-Learning Intelligence",
            "keywords": ["MetaLearningIntelligence", "learning pattern", "adaptive"],
            "active": False,
            "last_activity": None,
            "activity_count": 0
        },
        "5_self_awareness": {
            "name": "Self-Awareness Core 2.0",
            "keywords": ["SelfAwarenessCore", "cognitive", "bias detection", "reflection"],
            "active": False,
            "last_activity": None,
            "activity_count": 0
        },
        "6_meta_objective": {
            "name": "Meta-Objective Generator",
            "keywords": ["MetaObjectiveGenerator", "meta-objective", "capability assessment"],
            "active": False,
            "last_activity": None,
            "activity_count": 0
        }
    }
    
    # Buscar logs recentes
    log_sources = [
        "data/logs/",
        "logs/",
        "reports/logs/"
    ]
    
    recent_logs = []
    
    for log_dir in log_sources:
        log_path = Path(log_dir)
        if log_path.exists():
            for log_file in log_path.glob("*.log"):
                try:
                    if log_file.stat().st_mtime > time.time() - 3600:  # Last hour
                        with open(log_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            recent_logs.append((log_file.name, content))
                except Exception as e:
                    continue
    
    print(f"📂 Analisando {len(recent_logs)} arquivos de log recentes...")
    print()
    
    # Analisar logs
    for log_name, content in recent_logs:
        lines = content.split('\n')
        
        for line in lines:
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', line)
            if timestamp_match:
                timestamp_str = timestamp_match.group(1)
                try:
                    if 'T' in timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                    else:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                except:
                    continue
                
                # Check each meta-functionality
                for func_id, func_info in meta_functionalities.items():
                    for keyword in func_info["keywords"]:
                        if keyword.lower() in line.lower():
                            func_info["active"] = True
                            func_info["last_activity"] = timestamp
                            func_info["activity_count"] += 1
                            break
    
    # Display results
    print("🧠 STATUS DAS META-FUNCIONALIDADES:")
    print("=" * 50)
    
    for func_id, func_info in meta_functionalities.items():
        status = "✅ ATIVO" if func_info["active"] else "❌ INATIVO"
        name = func_info["name"]
        count = func_info["activity_count"]
        last_activity = func_info["last_activity"]
        
        print(f"{status} {name}")
        print(f"  📊 Atividades detectadas: {count}")
        if last_activity:
            time_ago = datetime.now() - last_activity
            print(f"  ⏰ Última atividade: {time_ago.total_seconds():.0f}s atrás")
        print()
    
    # Summary
    active_count = sum(1 for func in meta_functionalities.values() if func["active"])
    total_count = len(meta_functionalities)
    
    print("📊 RESUMO GERAL")
    print("=" * 30)
    print(f"🎯 Meta-funcionalidades ativas: {active_count}/{total_count}")
    print(f"📈 Taxa de ativação: {active_count/total_count*100:.1f}%")
    
    if active_count == total_count:
        print("🎉 TODAS as meta-funcionalidades estão operacionais!")
    elif active_count >= total_count * 0.8:
        print("🟡 Maioria das meta-funcionalidades ativas")
    else:
        print("🔴 Várias meta-funcionalidades inativas")
    
    return meta_functionalities

def check_memory_files():
    """Verifica arquivos de memória para estado das meta-funcionalidades"""
    
    print("\n🧠 VERIFICAÇÃO DE ARQUIVOS DE MEMÓRIA")
    print("=" * 50)
    
    memory_files = [
        "data/memory/HEPHAESTUS_MEMORY.json",
        "reports/memory/HEPHAESTUS_MEMORY.json",
        "data/memory/META_FUNCTIONALITIES_MEMORY.json",
        "data/intelligence/",
        "data/reports/"
    ]
    
    for memory_path in memory_files:
        path = Path(memory_path)
        
        if path.is_file() and path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"📂 {path.name}:")
                
                if "meta_functionalities_roadmap" in data:
                    roadmap = data["meta_functionalities_roadmap"]
                    implemented = roadmap.get("implemented_count", 0)
                    total = roadmap.get("total_functionalities", 9)
                    print(f"  🎯 Implementadas: {implemented}/{total}")
                
                if "meta_intelligence_active" in data:
                    print(f"  🧠 Meta-inteligência: {'✅' if data['meta_intelligence_active'] else '❌'}")
                
                if "completed_objectives" in data:
                    completed = len(data["completed_objectives"])
                    failed = len(data.get("failed_objectives", []))
                    print(f"  📊 Objetivos: {completed} completados, {failed} falharam")
                
                print()
                
            except Exception as e:
                print(f"⚠️ Erro ao ler {path}: {e}")
        
        elif path.is_dir() and path.exists():
            files = list(path.glob("*.json"))
            if files:
                print(f"📁 {path.name}/: {len(files)} arquivos de dados")
                for file in files[:3]:  # Show first 3
                    size = file.stat().st_size
                    print(f"  - {file.name}: {size} bytes")
                print()

def monitor_real_time_improvements():
    """Monitora melhorias em tempo real"""
    
    print("\n⚡ MONITORAMENTO DE MELHORIAS EM TEMPO REAL")
    print("=" * 50)
    
    # Check for improvement indicators
    improvement_indicators = {
        "learning_events": 0,
        "successful_mutations": 0,
        "bias_corrections": 0,
        "capability_improvements": 0,
        "pattern_discoveries": 0,
        "objective_generations": 0
    }
    
    # Check data directories for recent activity
    data_dirs = [
        "data/intelligence/",
        "data/reports/",
        "data/memory/"
    ]
    
    for data_dir in data_dirs:
        path = Path(data_dir)
        if path.exists():
            for file_path in path.glob("*.json"):
                try:
                    # Check file modification time
                    mtime = file_path.stat().st_mtime
                    if mtime > time.time() - 600:  # Last 10 minutes
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Count improvements
                        if "learning_events" in data:
                            improvement_indicators["learning_events"] += len(data["learning_events"])
                        
                        if "mutations" in data:
                            improvement_indicators["successful_mutations"] += len([m for m in data["mutations"] if m.get("success", False)])
                        
                        if "biases_detected" in data:
                            improvement_indicators["bias_corrections"] += data["biases_detected"]
                        
                        if "generated_objectives" in data:
                            improvement_indicators["objective_generations"] += len(data["generated_objectives"])
                
                except Exception as e:
                    continue
    
    print("📈 INDICADORES DE MELHORIA (últimos 10 minutos):")
    for indicator, count in improvement_indicators.items():
        status = "🟢" if count > 0 else "⚪"
        print(f"  {status} {indicator.replace('_', ' ').title()}: {count}")
    
    total_improvements = sum(improvement_indicators.values())
    print(f"\n🎯 Total de melhorias detectadas: {total_improvements}")
    
    if total_improvements > 5:
        print("🚀 Sistema altamente ativo - muitas melhorias em curso!")
    elif total_improvements > 0:
        print("📈 Sistema ativo - algumas melhorias detectadas")
    else:
        print("🔄 Sistema estável - monitorando para novas melhorias")

def show_key_log_patterns():
    """Mostra padrões-chave para procurar nos logs"""
    
    print("\n🔍 PADRÕES-CHAVE PARA PROCURAR NOS LOGS")
    print("=" * 50)
    
    patterns = {
        "🔮 Predictive Failure Engine": [
            "failure probability",
            "preventive modification",
            "PredictiveFailureEngine",
            "risk assessment"
        ],
        "⚡ Real-Time Evolution Engine": [
            "mutation generated",
            "fitness evaluation",
            "evolution loop",
            "hot-deployment"
        ],
        "🧪 Parallel Reality Testing": [
            "reality test",
            "strategy comparison", 
            "parallel execution",
            "winner selected"
        ],
        "🧠 Meta-Learning Intelligence": [
            "learning pattern",
            "adaptive rate",
            "bias detection",
            "knowledge transfer"
        ],
        "🎭 Self-Awareness Core": [
            "cognitive state",
            "self-reflection",
            "bias correction",
            "personality evolution"
        ],
        "🎯 Meta-Objective Generator": [
            "meta-objective generated",
            "capability assessment",
            "objective pattern",
            "recursive improvement"
        ]
    }
    
    for system, keywords in patterns.items():
        print(f"{system}:")
        for keyword in keywords:
            print(f"  🔎 '{keyword}'")
        print()
    
    print("💡 COMO INTERPRETAR:")
    print("  ✅ Verde: Sistema ativo e funcionando")
    print("  🟡 Amarelo: Sistema parcialmente ativo")  
    print("  ❌ Vermelho: Sistema inativo ou com problemas")
    print("  📊 Números: Quantidade de atividades detectadas")
    print("  ⏰ Tempo: Há quanto tempo foi a última atividade")

if __name__ == "__main__":
    print("🚀 Iniciando análise de meta-funcionalidades...")
    print()
    
    # Main analysis
    meta_status = analyze_logs()
    
    # Memory check
    check_memory_files()
    
    # Real-time monitoring
    monitor_real_time_improvements()
    
    # Show patterns to look for
    show_key_log_patterns()
    
    print("\n" + "=" * 70)
    print("✅ Análise completa! Use este script durante a execução para monitorar.")
    print("🔄 Execute novamente para ver atualizações em tempo real.")
    print("=" * 70)