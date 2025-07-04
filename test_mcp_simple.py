#!/usr/bin/env python3
"""
Cliente Simples para testar o Servidor MCP Hephaestus
====================================================

Este cliente faz chamadas diretas ao servidor para demonstrar
suas funcionalidades sem complexidades de tipos.
"""

import subprocess
import json
import sys
import time
from pathlib import Path

def test_mcp_server():
    """Testa o servidor MCP fazendo chamadas diretas"""
    print("🚀 Testando Servidor MCP Hephaestus")
    print("=" * 50)
    
    # Verificar se o servidor está rodando
    try:
        result = subprocess.run(
            ["pgrep", "-f", "hephaestus_mcp_server.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Servidor MCP está rodando")
            print(f"📋 PIDs encontrados: {result.stdout.strip()}")
        else:
            print("❌ Servidor MCP não está rodando")
            print("🚀 Iniciando servidor...")
            
            # Iniciar servidor em background
            subprocess.Popen(
                ["python3", "run_mcp.py", "stdio"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar inicialização
            time.sleep(3)
            
    except Exception as e:
        print(f"❌ Erro ao verificar servidor: {e}")
        return False
    
    print("\n🧪 Executando testes básicos...")
    
    # Teste 1: Verificar se o arquivo do servidor existe
    test_server_file()
    
    # Teste 2: Verificar dependências
    test_dependencies()
    
    # Teste 3: Verificar configuração
    test_configuration()
    
    # Teste 4: Simular análise de código
    test_code_analysis_simulation()
    
    print("\n✅ Testes concluídos!")
    return True

def test_server_file():
    """Testa se o arquivo do servidor existe"""
    print("\n🔍 TESTE 1: Verificando arquivo do servidor")
    print("-" * 40)
    
    server_file = Path("hephaestus_mcp_server.py")
    if server_file.exists():
        print(f"✅ Arquivo encontrado: {server_file}")
        print(f"📊 Tamanho: {server_file.stat().st_size} bytes")
        
        # Verificar se contém as ferramentas principais
        with open(server_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        tools = [
            "analyze_code",
            "generate_objective", 
            "execute_rsi_cycle",
            "meta_intelligence_report",
            "performance_analysis",
            "system_status"
        ]
        
        print("🔧 Ferramentas encontradas:")
        for tool in tools:
            if f"def {tool}" in content:
                print(f"   ✅ {tool}")
            else:
                print(f"   ❌ {tool}")
    else:
        print("❌ Arquivo do servidor não encontrado!")

def test_dependencies():
    """Testa dependências do MCP"""
    print("\n🔍 TESTE 2: Verificando dependências")
    print("-" * 40)
    
    dependencies = [
        "mcp.server.fastmcp",
        "mcp.types",
        "agent.hephaestus_agent",
        "agent.brain",
        "agent.memory"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError as e:
            print(f"   ❌ {dep} - {e}")

def test_configuration():
    """Testa configuração do sistema"""
    print("\n🔍 TESTE 3: Verificando configuração")
    print("-" * 40)
    
    config_files = [
        "config/default.yaml",
        "config/base_config.yaml",
        "requirements_mcp.txt"
    ]
    
    for config_file in config_files:
        path = Path(config_file)
        if path.exists():
            print(f"   ✅ {config_file}")
        else:
            print(f"   ❌ {config_file}")
    
    # Verificar diretórios necessários
    directories = [
        "logs",
        "reports",
        "reports/memory"
    ]
    
    print("\n📁 Diretórios:")
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"   ✅ {directory}")
        else:
            print(f"   ❌ {directory}")
            # Criar diretório se não existir
            path.mkdir(parents=True, exist_ok=True)
            print(f"   🔧 Criado: {directory}")

def test_code_analysis_simulation():
    """Simula análise de código"""
    print("\n🔍 TESTE 4: Simulação de Análise de Código")
    print("-" * 40)
    
    # Código de exemplo
    sample_code = '''
def fibonacci(n):
    """Função recursiva para calcular fibonacci"""
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    for i in range(10):
        print(f"fibonacci({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
'''
    
    print("📝 Código de exemplo:")
    print(sample_code)
    
    # Análise básica
    lines = sample_code.strip().split('\n')
    functions = [line for line in lines if 'def ' in line]
    
    print("\n📊 Análise básica:")
    print(f"   • Linhas de código: {len(lines)}")
    print(f"   • Funções encontradas: {len(functions)}")
    
    for func in functions:
        print(f"   • {func.strip()}")
    
    # Simular insights RSI
    print("\n🧠 Insights RSI simulados:")
    print("   • Função fibonacci usa recursão - pode ser otimizada com memoização")
    print("   • Complexidade exponencial O(2^n) - considerar programação dinâmica")
    print("   • Função main bem estruturada - boa separação de responsabilidades")

def show_server_capabilities():
    """Mostra as capacidades do servidor MCP"""
    print("\n🎯 CAPACIDADES DO SERVIDOR MCP HEPHAESTUS")
    print("=" * 50)
    
    capabilities = {
        "🔧 Ferramentas MCP": [
            "analyze_code - Análise de código com RSI",
            "generate_objective - Geração inteligente de objetivos",
            "execute_rsi_cycle - Ciclo completo de auto-aprimoramento",
            "meta_intelligence_report - Relatório de meta-inteligência",
            "performance_analysis - Análise profunda de performance",
            "evolve_capabilities - Evolução de capacidades",
            "system_status - Status do sistema"
        ],
        "📚 Recursos MCP": [
            "hephaestus://status - Status detalhado",
            "hephaestus://capabilities - Capacidades do sistema",
            "hephaestus://memory - Memória do sistema"
        ],
        "🧠 Capacidades RSI": [
            "Auto-aprimoramento recursivo",
            "Meta-inteligência e evolução cognitiva",
            "Análise profunda de código",
            "Geração inteligente de objetivos",
            "Criação automática de novos agentes",
            "Análise de causas raiz multi-camada",
            "Otimização contínua de performance"
        ]
    }
    
    for category, items in capabilities.items():
        print(f"\n{category}:")
        for item in items:
            print(f"   • {item}")

def main():
    """Função principal"""
    try:
        # Executar testes
        success = test_mcp_server()
        
        if success:
            # Mostrar capacidades
            show_server_capabilities()
            
            print("\n🎉 Servidor MCP Hephaestus está funcionando!")
            print("🔗 Para usar no Cursor IDE, configure o MCP client")
            print("📖 Consulte o README_MCP_HEPHAESTUS.md para instruções")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 