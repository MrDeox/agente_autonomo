#!/usr/bin/env python3
"""
Teste direto da configuração MCP do Cursor
==========================================

Este script testa se o arquivo mcp.json do Cursor está correto
e se o servidor MCP está respondendo adequadamente.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def test_mcp_config():
    """Testa a configuração MCP do Cursor"""
    print("🧪 Testando Configuração MCP do Cursor")
    print("=" * 50)
    
    # 1. Verificar se o arquivo mcp.json existe
    mcp_file = Path.home() / ".cursor" / "mcp.json"
    print(f"📁 Verificando arquivo: {mcp_file}")
    
    if not mcp_file.exists():
        print("❌ Arquivo mcp.json não encontrado!")
        return False
    
    print("✅ Arquivo mcp.json encontrado")
    
    # 2. Verificar se o JSON é válido
    try:
        with open(mcp_file, 'r') as f:
            config = json.load(f)
        print("✅ JSON válido")
    except json.JSONDecodeError as e:
        print(f"❌ JSON inválido: {e}")
        return False
    
    # 3. Verificar estrutura da configuração
    print("\n📋 Verificando estrutura da configuração:")
    
    if "mcpServers" not in config:
        print("❌ Chave 'mcpServers' não encontrada")
        return False
    
    print("✅ Chave 'mcpServers' encontrada")
    
    if "hephaestus" not in config["mcpServers"]:
        print("❌ Servidor 'hephaestus' não configurado")
        return False
    
    print("✅ Servidor 'hephaestus' configurado")
    
    heph_config = config["mcpServers"]["hephaestus"]
    
    # Verificar campos obrigatórios
    required_fields = ["command", "args"]
    for field in required_fields:
        if field not in heph_config:
            print(f"❌ Campo obrigatório '{field}' não encontrado")
            return False
        print(f"✅ Campo '{field}' encontrado")
    
    # 4. Verificar se o comando existe
    command = heph_config["command"]
    print(f"\n🔍 Verificando comando: {command}")
    
    try:
        result = subprocess.run([command, "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Comando '{command}' funciona")
        else:
            print(f"⚠️ Comando '{command}' existe mas pode ter problemas")
    except FileNotFoundError:
        print(f"❌ Comando '{command}' não encontrado")
        return False
    
    # 5. Verificar se o arquivo do servidor existe
    args = heph_config["args"]
    if len(args) > 0:
        server_file = args[0]
        print(f"\n📄 Verificando arquivo do servidor: {server_file}")
        
        if not Path(server_file).exists():
            print(f"❌ Arquivo do servidor não encontrado: {server_file}")
            return False
        
        print("✅ Arquivo do servidor encontrado")
    
    # 6. Verificar diretório de trabalho
    if "cwd" in heph_config:
        cwd = heph_config["cwd"]
        print(f"\n📁 Verificando diretório de trabalho: {cwd}")
        
        if not Path(cwd).exists():
            print(f"❌ Diretório de trabalho não encontrado: {cwd}")
            return False
        
        print("✅ Diretório de trabalho encontrado")
    
    # 7. Verificar variáveis de ambiente
    if "env" in heph_config:
        print(f"\n🌍 Variáveis de ambiente configuradas:")
        for key, value in heph_config["env"].items():
            print(f"   • {key}={value}")
    
    # 8. Testar execução do servidor
    print(f"\n🚀 Testando execução do servidor...")
    
    try:
        # Construir comando completo
        full_command = [command] + args
        
        # Configurar ambiente
        env = os.environ.copy()
        if "env" in heph_config:
            env.update(heph_config["env"])
        
        # Configurar diretório de trabalho
        cwd = heph_config.get("cwd", None)
        
        # Executar comando por 3 segundos para ver se inicia
        print(f"   Comando: {' '.join(full_command)}")
        print(f"   Diretório: {cwd}")
        
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=cwd
        )
        
        # Aguardar 3 segundos
        try:
            stdout, stderr = process.communicate(timeout=3)
            print("⚠️ Processo terminou rapidamente")
            if stdout:
                print(f"   STDOUT: {stdout[:200]}...")
            if stderr:
                print(f"   STDERR: {stderr[:200]}...")
        except subprocess.TimeoutExpired:
            print("✅ Servidor iniciou e está rodando")
            process.terminate()
            process.wait()
        
    except Exception as e:
        print(f"❌ Erro ao testar servidor: {e}")
        return False
    
    # 9. Mostrar configuração final
    print(f"\n📋 Configuração Final:")
    print(json.dumps(config, indent=2))
    
    print(f"\n🎉 Configuração MCP parece estar correta!")
    print(f"\n📝 Próximos passos:")
    print(f"   1. Reinicie o Cursor IDE")
    print(f"   2. Abra o chat do Cursor")
    print(f"   3. Digite '@' para ver servidores disponíveis")
    print(f"   4. Selecione '@hephaestus'")
    print(f"   5. Teste: '@hephaestus system_status'")
    
    return True

if __name__ == "__main__":
    success = test_mcp_config()
    sys.exit(0 if success else 1) 