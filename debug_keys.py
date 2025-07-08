#!/usr/bin/env python3
"""
Debug para verificar carregamento das chaves
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Debug das Chaves API:")
print("=" * 40)

for i in range(1, 6):
    key = os.getenv(f"OPENROUTER_API_KEY_{i}")
    print(f"OPENROUTER_API_KEY_{i}: {'✅' if key else '❌'} {key[:20] + '...' if key else 'None'}")

print()
print("Chave principal (backward compatibility):")
main_key = os.getenv("OPENROUTER_API_KEY")
print(f"OPENROUTER_API_KEY: {'✅' if main_key else '❌'} {main_key[:20] + '...' if main_key else 'None'}")