#!/usr/bin/env python3
"""
🔧 Environment Setup Script
Configura as variáveis de ambiente necessárias para o Hephaestus
"""

import os
from pathlib import Path

def setup_environment():
    """Configura o ambiente com as variáveis necessárias"""
    env_file = Path('.env')
    
    # Verifica se .env já existe
    if env_file.exists():
        print(f"✅ Arquivo .env já existe")
        with open(env_file, 'r') as f:
            content = f.read()
            print("Conteúdo atual:")
            print(content)
        return
    
    # Cria arquivo .env com configurações padrão
    env_content = """# Hephaestus Environment Variables
# Para uso com modelos OpenRouter
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Para uso com modelos Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Para uso com modelos OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Para uso com modelos Anthropic
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Configurações do sistema
HEPHAESTUS_DEBUG=true
HEPHAESTUS_LOG_LEVEL=INFO
HEPHAESTUS_EVOLUTION_ENABLED=true
HEPHAESTUS_AUTO_CORRECTION_ENABLED=true
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Arquivo .env criado com configurações padrão")
    print(f"📝 Edite o arquivo .env para adicionar suas chaves de API")
    print("\nVariáveis configuradas:")
    print("- OPENROUTER_API_KEY (para acesso a modelos via OpenRouter)")
    print("- GEMINI_API_KEY (para modelos Gemini)")
    print("- OPENAI_API_KEY (para modelos OpenAI)")
    print("- ANTHROPIC_API_KEY (para modelos Anthropic)")
    print("- Configurações do sistema Hephaestus")

if __name__ == "__main__":
    setup_environment() 