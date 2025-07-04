#!/usr/bin/env python3
"""
Cliente de teste para o Servidor MCP Hephaestus
===============================================

Este cliente demonstra como usar as funcionalidades do servidor MCP
para análise de código, geração de objetivos e auto-aprimoramento.
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any, List
from pathlib import Path

# Importar cliente MCP
try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
    from mcp.types import CallToolResult, ListToolsResult, ListResourcesResult
except ImportError as e:
    print(f"❌ Erro: Dependências MCP não encontradas: {e}")
    print("Instale com: pip install mcp")
    sys.exit(1)

class HephaestusMCPClient:
    """Cliente para testar o servidor MCP Hephaestus"""
    
    def __init__(self):
        self.session = None
        self.tools = []
        self.resources = []
        
    async def connect(self):
        """Conecta ao servidor MCP"""
        try:
            print("🔗 Conectando ao servidor MCP Hephaestus...")
            
            # Configurar parâmetros do servidor
            server_params = StdioServerParameters(
                command="python3",
                args=["hephaestus_mcp_server.py", "stdio"],
                env=None
            )
            
            # Conectar via stdio
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # Listar ferramentas disponíveis
                    print("📋 Listando ferramentas disponíveis...")
                    tools_result = await session.list_tools()
                    self.tools = tools_result.tools
                    
                    print(f"✅ Encontradas {len(self.tools)} ferramentas:")
                    for tool in self.tools:
                        print(f"   • {tool.name} - {tool.description}")
                    
                    # Listar recursos disponíveis
                    print("\n📚 Listando recursos disponíveis...")
                    resources_result = await session.list_resources()
                    self.resources = resources_result.resources
                    
                    print(f"✅ Encontrados {len(self.resources)} recursos:")
                    for resource in self.resources:
                        print(f"   • {resource.uri} - {resource.description}")
                    
                    # Executar testes
                    await self.run_tests()
                    
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chama uma ferramenta do servidor MCP"""
        try:
            print(f"\n🔧 Chamando ferramenta: {tool_name}")
            print(f"📝 Argumentos: {json.dumps(arguments, indent=2)}")
            
            if self.session:
                result = await self.session.call_tool(tool_name, arguments)
                
                print(f"✅ Resultado recebido:")
                if hasattr(result, 'content') and result.content:
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(content.text)
                
                return result
            else:
                print("❌ Sessão não inicializada")
                return {"error": "Sessão não inicializada"}
            
        except Exception as e:
            print(f"❌ Erro ao chamar ferramenta {tool_name}: {e}")
            return {"error": str(e)}
    
    async def read_resource(self, uri: str) -> str:
        """Lê um recurso do servidor MCP"""
        try:
            print(f"\n📖 Lendo recurso: {uri}")
            
            result = await self.session.read_resource(uri)
            
            print(f"✅ Recurso lido com sucesso:")
            if hasattr(result, 'contents') and result.contents:
                for content in result.contents:
                    if hasattr(content, 'text'):
                        return content.text
            
            return ""
            
        except Exception as e:
            print(f"❌ Erro ao ler recurso {uri}: {e}")
            return f"Erro: {str(e)}"
    
    async def run_tests(self):
        """Executa testes das funcionalidades do servidor"""
        print("\n" + "="*60)
        print("🧪 INICIANDO TESTES DO SERVIDOR MCP HEPHAESTUS")
        print("="*60)
        
        # Teste 1: Status do sistema
        await self.test_system_status()
        
        # Teste 2: Análise de código
        await self.test_code_analysis()
        
        # Teste 3: Geração de objetivos
        await self.test_objective_generation()
        
        # Teste 4: Relatório de meta-inteligência
        await self.test_meta_intelligence()
        
        # Teste 5: Análise de performance
        await self.test_performance_analysis()
        
        # Teste 6: Leitura de recursos
        await self.test_resources()
        
        print("\n" + "="*60)
        print("✅ TESTES CONCLUÍDOS")
        print("="*60)
    
    async def test_system_status(self):
        """Testa o status do sistema"""
        print("\n🔍 TESTE 1: Status do Sistema")
        print("-" * 40)
        
        await self.call_tool("system_status", {})
    
    async def test_code_analysis(self):
        """Testa análise de código"""
        print("\n🔍 TESTE 2: Análise de Código")
        print("-" * 40)
        
        # Código de exemplo para análise
        sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    for i in range(10):
        print(f"fibonacci({i}) = {fibonacci(i)}")

if __name__ == "__main__":
    main()
"""
        
        await self.call_tool("analyze_code", {
            "code": sample_code,
            "context": "Análise de função fibonacci recursiva"
        })
    
    async def test_objective_generation(self):
        """Testa geração de objetivos"""
        print("\n🔍 TESTE 3: Geração de Objetivos")
        print("-" * 40)
        
        await self.call_tool("generate_objective", {
            "context": "Otimizar performance de algoritmos recursivos",
            "type": "standard"
        })
    
    async def test_meta_intelligence(self):
        """Testa relatório de meta-inteligência"""
        print("\n🔍 TESTE 4: Relatório de Meta-Inteligência")
        print("-" * 40)
        
        await self.call_tool("meta_intelligence_report", {})
    
    async def test_performance_analysis(self):
        """Testa análise de performance"""
        print("\n🔍 TESTE 5: Análise de Performance")
        print("-" * 40)
        
        await self.call_tool("performance_analysis", {})
    
    async def test_resources(self):
        """Testa leitura de recursos"""
        print("\n🔍 TESTE 6: Leitura de Recursos")
        print("-" * 40)
        
        for resource in self.resources:
            content = await self.read_resource(resource.uri)
            print(f"📄 Recurso {resource.uri}:")
            print(f"   Tamanho: {len(content)} caracteres")
            if content and not content.startswith("Erro:"):
                # Mostrar apenas os primeiros 200 caracteres
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   Preview: {preview}")
            print()

async def main():
    """Função principal"""
    print("🚀 Cliente de Teste MCP Hephaestus")
    print("=" * 50)
    
    client = HephaestusMCPClient()
    
    try:
        await client.connect()
    except KeyboardInterrupt:
        print("\n🛑 Teste interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 