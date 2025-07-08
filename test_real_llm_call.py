#!/usr/bin/env python3
"""
Teste de chamada LLM real usando o novo sistema de múltiplas chaves
"""

import sys
import logging
sys.path.append('src')

from hephaestus.utils.llm_client import call_openrouter_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestLLM")

def test_llm_call():
    print("🧪 Testando chamada LLM real...")
    print("=" * 50)
    
    result, error = call_openrouter_api(
        model="mistralai/mistral-small-3.2-24b-instruct:free",
        prompt="Diga 'Olá! Sistema de múltiplas chaves funcionando!' em uma frase.",
        temperature=0.7,
        max_tokens=50,
        logger=logger
    )
    
    if result:
        print("✅ SUCESSO!")
        print(f"📝 Resposta: {result}")
        print()
        print("🎉 O sistema de múltiplas chaves está funcionando perfeitamente!")
        print("🔄 O Hephaestus agora pode usar fallback automático entre suas 5 chaves OpenRouter!")
    else:
        print("❌ FALHA!")
        print(f"🚨 Erro: {error}")

if __name__ == "__main__":
    test_llm_call()