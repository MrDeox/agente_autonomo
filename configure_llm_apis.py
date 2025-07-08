"""
Script para configurar LLM APIs para autonomia real do Hephaestus
"""

import json
import os
from pathlib import Path

def configure_openrouter_api():
    """Configura OpenRouter API (gratuita) para o sistema."""
    
    print("🔧 Configurando LLM APIs para autonomia real...")
    
    # Configuração otimizada com melhores modelos gratuitos OpenRouter
    config = {
        "llm": {
            "primary_model": "meta-llama/llama-3.1-8b-instruct:free",
            "fallback_models": [
                "google/gemma-2-9b-it:free",
                "microsoft/phi-3-mini-128k-instruct:free",
                "qwen/qwen-2-7b-instruct:free",
                "mistralai/mistral-7b-instruct:free"
            ],
            "api_provider": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "timeout": 60,
            "max_retries": 3,
            "retry_delay": 2.0
        },
        "models": {
            "architect_default": {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "temperature": 0.4,
                "max_tokens": 4096,
                "top_p": 0.9
            },
            "maestro_default": {
                "model": "google/gemma-2-9b-it:free", 
                "temperature": 0.3,
                "max_tokens": 2048,
                "top_p": 0.8
            },
            "bug_hunter_default": {
                "model": "microsoft/phi-3-mini-128k-instruct:free",
                "temperature": 0.2,
                "max_tokens": 3072,
                "top_p": 0.7
            },
            "brain_default": {
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "temperature": 0.5,
                "max_tokens": 4096,
                "top_p": 0.9
            },
            "organizer_default": {
                "model": "qwen/qwen-2-7b-instruct:free",
                "temperature": 0.3,
                "max_tokens": 3072,
                "top_p": 0.8
            }
        }
    }
    
    # Salvar configuração
    config_file = Path("hephaestus_config.json")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuração salva em: {config_file}")
    
    # Verificar se API key existe
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("\n🔑 CONFIGURAÇÃO DA API KEY:")
        print("1. Vá para: https://openrouter.ai/")
        print("2. Crie uma conta gratuita")
        print("3. Gere uma API key")
        print("4. Execute: export OPENROUTER_API_KEY='sua_key_aqui'")
        print("5. Ou adicione no .env: OPENROUTER_API_KEY=sua_key_aqui")
        
        # Criar .env template
        env_file = Path(".env")
        if not env_file.exists():
            with open(env_file, 'w') as f:
                f.write("# OpenRouter API Key para LLM calls\n")
                f.write("OPENROUTER_API_KEY=your_key_here\n")
                f.write("\n# Configurações opcionais\n")
                f.write("LOG_LEVEL=INFO\n")
                f.write("HEPHAESTUS_ENV=development\n")
            print(f"📄 Template .env criado em: {env_file}")
    else:
        print("✅ API Key encontrada!")
    
    return config

def test_llm_connection():
    """Testa a conexão com LLM."""
    print("\n🧪 Testando conexão LLM...")
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from hephaestus.utils.llm_client import call_llm_api
        
        # Teste simples
        response, error = call_llm_api(
            model_config={"model": "google/gemma-2-9b-it:free"},
            prompt="Respond with exactly: 'LLM connection working!'",
            temperature=0.1,
            max_tokens=50
        )
        
        if error:
            print(f"❌ Erro na conexão: {error}")
            return False
        elif response:
            print(f"✅ Conexão funcionando! Resposta: {response.strip()}")
            return True
        else:
            print("❌ Resposta vazia")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def create_startup_script():
    """Cria script para iniciar o sistema com autonomia real."""
    
    script_content = '''#!/bin/bash
# Script de inicialização do Hephaestus com autonomia real

echo "🔥 Iniciando Hephaestus com autonomia real..."

# Verificar API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ OPENROUTER_API_KEY não configurada!"
    echo "Execute: export OPENROUTER_API_KEY='sua_key'"
    exit 1
fi

echo "✅ API Key configurada"

# Iniciar sistema
echo "🚀 Iniciando sistema principal..."
poetry run python main.py &
MAIN_PID=$!

echo "📊 Iniciando dashboard..."
sleep 2
poetry run python -c "
import asyncio
from src.hephaestus.api.dashboard_server import start_dashboard
asyncio.run(start_dashboard())
" &
DASHBOARD_PID=$!

echo "🧠 Iniciando ciclo de auto-evolução..."
sleep 5
poetry run python -c "
import asyncio
from src.hephaestus.core.cycle_runner import CycleRunner
async def main():
    runner = CycleRunner()
    await runner.start_continuous_mode()
asyncio.run(main())
" &
CYCLE_PID=$!

echo "🎯 Sistema totalmente ativo!"
echo "📊 Dashboard: http://localhost:8080"
echo "🌐 API: http://localhost:8000"
echo ""
echo "Para parar tudo: kill $MAIN_PID $DASHBOARD_PID $CYCLE_PID"

# Aguardar
wait
'''
    
    script_file = Path("start_autonomous.sh")
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    os.chmod(script_file, 0o755)
    print(f"📜 Script de startup criado: {script_file}")
    print("Execute: ./start_autonomous.sh")

def main():
    """Configuração principal."""
    print("🤖 Configurador de Autonomia Real - Hephaestus")
    print("=" * 60)
    
    # 1. Configurar APIs
    config = configure_openrouter_api()
    
    # 2. Testar conexão (se API key existe)
    if os.getenv("OPENROUTER_API_KEY"):
        test_llm_connection()
    
    # 3. Criar script de startup
    create_startup_script()
    
    print("\n🎯 PRÓXIMOS PASSOS PARA AUTONOMIA REAL:")
    print("1. Configure a API key: export OPENROUTER_API_KEY='sua_key'")
    print("2. Execute: ./start_autonomous.sh")
    print("3. Acesse dashboard: http://localhost:8080")
    print("4. Submeta objetivo inicial via API ou CLI")
    print("5. Observe a evolução em tempo real!")
    
    print("\n✅ Configuração concluída!")

if __name__ == "__main__":
    main()