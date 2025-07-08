#!/usr/bin/env python3
"""
🧪 Teste de Múltiplas Chaves API
"""

import sys
sys.path.append('src')

from hephaestus.utils.api_key_manager import APIKeyManager
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    print("🔍 Testando Sistema de Múltiplas Chaves API...")
    print("=" * 60)
    
    # Force new instance instead of singleton to get fresh data
    manager = APIKeyManager()
    
    # Status report
    status = manager.get_status_report()
    print(f"📊 Status Geral:")
    print(f"  Total de chaves ativas: {status['total_active_keys']}")
    print()
    
    for provider, info in status['providers'].items():
        print(f"🔑 {provider.upper()}:")
        print(f"  Total: {info['total_keys']} | Ativas: {info['active_keys']}")
        
        for key_info in info['key_details']:
            status_icon = "✅" if key_info['is_active'] else "❌"
            print(f"    {status_icon} {key_info['name']} (prioridade: {key_info['priority']})")
        print()
    
    # Test key selection
    print("🎯 Testando Seleção de Chaves:")
    
    for provider in ['openrouter', 'gemini']:
        key = manager.get_best_key(provider)
        if key:
            print(f"  ✅ {provider}: {key.name}")
        else:
            print(f"  ❌ {provider}: Nenhuma chave disponível")
    
    # Test fallback
    print()
    print("🔄 Testando Fallback Automático:")
    key, provider = manager.get_key_with_fallback("openrouter")
    if key:
        print(f"  ✅ Selecionado: {key.name} ({provider})")
    else:
        print(f"  ❌ Nenhuma chave disponível em nenhum provedor!")

if __name__ == "__main__":
    main()
