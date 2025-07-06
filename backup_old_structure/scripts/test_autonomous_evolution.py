#!/usr/bin/env python3
"""
Script para testar o sistema de evolução autônoma do Hephaestus.
Este script submete alguns objetivos e monitora a evolução do sistema.
"""

import requests
import time
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

BASE_URL = "http://localhost:8000"

def submit_objective(objective: str):
    """Submit an objective to the Hephaestus agent."""
    try:
        response = requests.post(
            f"{BASE_URL}/submit_objective",
            json={"objective": objective},
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Objetivo submetido: {objective}")
            return True
        else:
            print(f"❌ Erro ao submeter objetivo: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return False

def get_status():
    """Get the current status of the Hephaestus agent."""
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro ao obter status: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return None

def monitor_evolution(duration_minutes=10):
    """Monitor the evolution of the system for a specified duration."""
    print(f"🔍 Monitorando evolução por {duration_minutes} minutos...")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    while time.time() < end_time:
        status = get_status()
        if status:
            print(f"\n📊 Status do Sistema:")
            print(f"   • Queue Size: {status.get('queue_size', 'N/A')}")
            print(f"   • Worker Active: {status.get('worker_active', 'N/A')}")
            print(f"   • Evolution Active: {status.get('evolution_active', 'N/A')}")
            
            meta_intel = status.get('meta_intelligence', {})
            if meta_intel and meta_intel.get('status') != 'inactive':
                print(f"   • Meta-Intelligence: ✅ ATIVO")
                if 'evolution_summary' in meta_intel:
                    summary = meta_intel['evolution_summary']
                    print(f"   • Cycles: {summary.get('total_cycles', 0)}")
                    print(f"   • Prompts Evolved: {summary.get('prompts_evolved', 0)}")
                    print(f"   • Agents Created: {summary.get('agents_created', 0)}")
            else:
                print(f"   • Meta-Intelligence: ❌ INATIVO")
        
        time.sleep(30)  # Check every 30 seconds
    
    print(f"\n✅ Monitoramento concluído!")

def main():
    """Main function to test autonomous evolution."""
    print("🚀 TESTE DE EVOLUÇÃO AUTÔNOMA DO HEPHAESTUS")
    print("=" * 50)
    
    # Check if server is running
    print("🔍 Verificando se o servidor está rodando...")
    status = get_status()
    if not status:
        print("❌ Servidor não está rodando. Execute: python main.py")
        return
    
    print("✅ Servidor está ativo!")
    
    # Submit some initial objectives to kickstart evolution
    objectives = [
        "Analisar o estado atual do sistema e identificar oportunidades de melhoria",
        "Revisar e otimizar os prompts dos agentes baseado na performance histórica",
        "Identificar e corrigir possíveis gargalos no sistema de validação"
    ]
    
    print(f"\n📝 Submetendo {len(objectives)} objetivos iniciais...")
    for obj in objectives:
        submit_objective(obj)
        time.sleep(2)  # Small delay between submissions
    
    # Monitor the evolution
    monitor_evolution(duration_minutes=5)
    
    # Final status check
    print(f"\n📊 Status Final:")
    final_status = get_status()
    if final_status:
        print(json.dumps(final_status, indent=2))

if __name__ == "__main__":
    main() 