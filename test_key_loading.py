#!/usr/bin/env python3
"""
Teste específico de carregamento de chaves
"""

import os
import sys
from dotenv import load_dotenv

# Carrega explicitamente o .env
load_dotenv()

print("🔍 Testando carregamento de chaves:")
print("=" * 50)

# Simula a lógica do APIKeyManager
openrouter_keys = []
existing_keys = set()

for i in range(1, 11):
    key = os.getenv(f"OPENROUTER_API_KEY_{i}")
    print(f"Chave {i}: {key[:20] + '...' if key else 'None'}")
    
    if key and key not in existing_keys:
        existing_keys.add(key)
        openrouter_keys.append({
            "key": key[:20] + "...",
            "name": f"openrouter_{i}",
            "priority": 1 if i <= 2 else (2 if i <= 5 else 3)
        })
        print(f"  ✅ Adicionada como openrouter_{i}")
    elif key:
        print(f"  ⚠️ Duplicata detectada")
    else:
        print(f"  ❌ Não encontrada")

print()
print(f"📊 Total de chaves únicas carregadas: {len(openrouter_keys)}")
for key_info in openrouter_keys:
    print(f"  - {key_info['name']}: {key_info['key']} (prioridade: {key_info['priority']})")