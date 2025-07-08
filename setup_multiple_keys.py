#!/usr/bin/env python3
"""
🔧 Setup de Múltiplas Chaves API
Script para configurar várias chaves API com redundância
"""

import os
from pathlib import Path

def setup_env_template():
    """Cria template do .env com múltiplas chaves"""
    
    env_content = '''# ========================
# 🔑 MÚLTIPLAS CHAVES API
# ========================
# Configure até 5 chaves por provedor para máxima redundância

# OpenRouter Keys (Free tier: https://openrouter.ai/)
OPENROUTER_API_KEY_1=sk-or-v1-sua_primeira_chave_aqui
OPENROUTER_API_KEY_2=sk-or-v1-sua_segunda_chave_aqui  
OPENROUTER_API_KEY_3=sk-or-v1-sua_terceira_chave_aqui
OPENROUTER_API_KEY_4=sk-or-v1-sua_quarta_chave_aqui
OPENROUTER_API_KEY_5=sk-or-v1-sua_quinta_chave_aqui

# Gemini Keys (Free tier: https://ai.google.dev/aistudio)
GEMINI_API_KEY_1=AIzaSy-sua_primeira_chave_gemini_aqui
GEMINI_API_KEY_2=AIzaSy-sua_segunda_chave_gemini_aqui
GEMINI_API_KEY_3=AIzaSy-sua_terceira_chave_gemini_aqui
GEMINI_API_KEY_4=AIzaSy-sua_quarta_chave_gemini_aqui
GEMINI_API_KEY_5=AIzaSy-sua_quinta_chave_gemini_aqui

# ========================
# 💡 DICAS IMPORTANTES:
# ========================
# 1. OpenRouter oferece modelos GRATUITOS (deepseek, mistral, qwen)
# 2. Gemini tem tier gratuito generoso
# 3. O sistema automaticamente faz fallback entre chaves
# 4. Chaves inválidas são desabilitadas automaticamente
# 5. Rate limits são gerenciados automaticamente

# Backward compatibility (primeira chave)
OPENROUTER_API_KEY=${OPENROUTER_API_KEY_1}
GEMINI_API_KEY=${GEMINI_API_KEY_1}
'''
    
    env_path = Path(".env")
    
    # Backup existing .env
    if env_path.exists():
        backup_path = Path(".env.backup")
        with open(env_path, 'r') as f:
            content = f.read()
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"📋 Backup criado: {backup_path}")
    
    # Write new template
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Template .env criado: {env_path}")
    print()
    print("🔧 PRÓXIMOS PASSOS:")
    print("1. Edite o arquivo .env com suas chaves reais")
    print("2. OpenRouter: https://openrouter.ai/ → Settings → Keys")
    print("3. Gemini: https://ai.google.dev/aistudio → Get API Key")
    print("4. Execute: poetry run python test_multiple_keys.py")

def create_key_test_script():
    """Cria script de teste para múltiplas chaves"""
    
    test_content = '''#!/usr/bin/env python3
"""
🧪 Teste de Múltiplas Chaves API
"""

import sys
sys.path.append('src')

from hephaestus.utils.api_key_manager import get_api_key_manager
import logging

logging.basicConfig(level=logging.INFO)

def main():
    print("🔍 Testando Sistema de Múltiplas Chaves API...")
    print("=" * 60)
    
    manager = get_api_key_manager()
    
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
'''
    
    with open("test_multiple_keys.py", 'w') as f:
        f.write(test_content)
    
    print(f"✅ Script de teste criado: test_multiple_keys.py")

def show_providers_info():
    """Mostra informações sobre os provedores"""
    print()
    print("🌟 INFORMAÇÕES DOS PROVEDORES:")
    print("=" * 40)
    print()
    print("🔷 OPENROUTER (Recomendado)")
    print("  • URL: https://openrouter.ai/")
    print("  • Modelos gratuitos: ✅")
    print("  • Rate limit: Generoso")
    print("  • Modelos: Deepseek, Mistral, Qwen, etc.")
    print()
    print("🔷 GEMINI (Google)")
    print("  • URL: https://ai.google.dev/aistudio")
    print("  • Tier gratuito: ✅")
    print("  • Rate limit: 15 RPM gratuito")
    print("  • Modelo: Gemini Pro")
    print()
    print("💡 ESTRATÉGIA RECOMENDADA:")
    print("  1. Crie 3-5 contas OpenRouter (email diferentes)")
    print("  2. Crie 2-3 contas Gemini")
    print("  3. Configure todas as chaves no .env")
    print("  4. O sistema automaticamente gerencia fallbacks")

if __name__ == "__main__":
    print("🔧 Setup de Múltiplas Chaves API para Hephaestus")
    print("=" * 50)
    
    setup_env_template()
    create_key_test_script()
    show_providers_info()
    
    print()
    print("🚀 Setup completo! Agora configure suas chaves no .env")