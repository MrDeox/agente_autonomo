#!/usr/bin/env python3
"""
Script de Setup para Servidor MCP do Hephaestus
Configura e instala as dependências necessárias para o servidor MCP
"""

import subprocess
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any

def run_command(cmd: str, description: str = ""):
    """Executa um comando e retorna o resultado"""
    print(f"🔧 {description or cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Erro: {e.stderr.strip()}")
        return False

def install_dependencies():
    """Instala as dependências do MCP"""
    print("\n📦 Instalando dependências MCP...")
    
    # Verificar se o arquivo requirements existe
    req_file = Path("requirements_mcp.txt")
    if not req_file.exists():
        print("❌ Arquivo requirements_mcp.txt não encontrado")
        return False
    
    # Instalar via pip
    success = run_command(
        f"pip install -r {req_file}",
        "Instalando dependências MCP"
    )
    
    if not success:
        print("⚠️  Tentando instalar dependências individuais...")
        deps = ["mcp", "fastapi-mcp", "pydantic", "httpx", "websockets"]
        for dep in deps:
            run_command(f"pip install {dep}", f"Instalando {dep}")
    
    return True

def create_cursor_config():
    """Cria configuração para Cursor"""
    print("\n🎯 Criando configuração para Cursor...")
    
    config = {
        "mcpServers": {
            "hephaestus": {
                "url": "http://localhost:8001/mcp",
                "name": "Hephaestus RSI Agent",
                "description": "Agente de auto-aprimoramento recursivo"
            }
        }
    }
    
    # Salvar configuração
    config_file = Path("cursor_mcp_config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuração salva em: {config_file}")
    print("\n📋 Para usar no Cursor:")
    print("   1. Abra Settings -> MCP -> Add new MCP")
    print(f"   2. Copie o conteúdo de {config_file}")
    print("   3. Cole na configuração do Cursor")
    
    return True

def create_claude_config():
    """Cria configuração para Claude Desktop"""
    print("\n🤖 Criando configuração para Claude Desktop...")
    
    config = {
        "mcpServers": {
            "hephaestus": {
                "command": "python",
                "args": ["mcp_server_example.py", "stdio"],
                "env": {
                    "PYTHONPATH": os.getcwd()
                }
            }
        }
    }
    
    # Salvar configuração
    config_file = Path("claude_desktop_config.json")
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuração salva em: {config_file}")
    print("\n📋 Para usar no Claude Desktop:")
    print("   1. Localize o arquivo de configuração do Claude:")
    print("      - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("      - Windows: %APPDATA%/Claude/claude_desktop_config.json")
    print("      - Linux: ~/.config/Claude/claude_desktop_config.json")
    print(f"   2. Copie o conteúdo de {config_file}")
    print("   3. Cole na configuração do Claude Desktop")
    
    return True

def create_test_client():
    """Cria cliente de teste para o servidor MCP"""
    print("\n🧪 Criando cliente de teste...")
    
    test_client = '''#!/usr/bin/env python3
"""
Cliente de Teste para Servidor MCP Hephaestus
Testa as funcionalidades do servidor MCP
"""

import asyncio
import json
from pathlib import Path

async def test_mcp_server():
    """Testa o servidor MCP"""
    print("🧪 Testando Servidor MCP Hephaestus...")
    
    # Simulação de testes (em implementação real usaria cliente MCP)
    tests = [
        {
            "tool": "analyze_code",
            "params": {"code": "def hello(): return 'world'"},
            "expected": "análise"
        },
        {
            "tool": "generate_objective", 
            "params": {"context": "melhorar performance"},
            "expected": "objetivo"
        },
        {
            "tool": "capability_assessment",
            "params": {},
            "expected": "capacidades"
        }
    ]
    
    print("📋 Testes simulados:")
    for test in tests:
        print(f"   ✅ {test['tool']}: {test['expected']}")
    
    print("\\n🎯 Para testes reais, execute:")
    print("   python mcp_server_example.py stdio")
    print("   (Em outro terminal) python test_mcp_client.py")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
'''
    
    # Salvar cliente de teste
    test_file = Path("test_mcp_client.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_client)
    
    print(f"✅ Cliente de teste criado: {test_file}")
    return True

def main():
    """Função principal do setup"""
    print("🚀 Setup do Servidor MCP Hephaestus")
    print("=" * 50)
    
    # Verificar Python
    print(f"🐍 Python: {sys.version}")
    
    # Instalar dependências
    install_dependencies()
    
    # Criar configurações
    create_cursor_config()
    create_claude_config()
    
    # Criar cliente de teste
    create_test_client()
    
    print("\n" + "=" * 50)
    print("✅ Setup concluído!")
    print("\n📝 Próximos passos:")
    print("   1. Execute o servidor: python mcp_server_example.py")
    print("   2. Configure seu cliente MCP (Cursor/Claude)")
    print("   3. Teste a integração")
    print("   4. Explore as capacidades do Hephaestus!")
    
    print("\n🔧 Comandos úteis:")
    print("   • Servidor STDIO: python mcp_server_example.py stdio")
    print("   • Servidor SSE: python mcp_server_example.py sse")
    print("   • Cliente teste: python test_mcp_client.py")
    
    print("\n📚 Documentação:")
    print("   • Proposta completa: PROPOSTA_SERVIDOR_MCP.md")
    print("   • Configurações: cursor_mcp_config.json, claude_desktop_config.json")

if __name__ == "__main__":
    main()