#!/bin/bash

# 🚀 Script para iniciar o Servidor MCP Hephaestus
# Versão melhorada com verificações e tratamento de erros
# Uso: ./start_mcp_server.sh

echo "🚀 Iniciando Servidor MCP Hephaestus..."
echo "=================================="

# Verificar se estamos no diretório correto
if [ ! -f "hephaestus_mcp_server.py" ]; then
    echo "❌ Erro: Arquivo hephaestus_mcp_server.py não encontrado!"
    echo "Execute este script na raiz do projeto Hephaestus"
    exit 1
fi

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: Python3 não encontrado!"
    echo "Instale Python 3.8+ para continuar"
    exit 1
fi

# Verificar se as dependências MCP estão instaladas
echo "🔍 Verificando dependências MCP..."
if ! python3 -c "import mcp.server.fastmcp" 2>/dev/null; then
    echo "❌ Dependências MCP não encontradas!"
    echo "Instalando dependências MCP..."
    pip install mcp fastmcp
    if [ $? -ne 0 ]; then
        echo "❌ Falha ao instalar dependências MCP"
        exit 1
    fi
fi

# Verificar se as dependências do projeto estão instaladas
echo "🔍 Verificando dependências do projeto..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "requirements_mcp.txt" ]; then
    pip install -r requirements_mcp.txt
fi

# Criar diretórios necessários
echo "📁 Criando diretórios necessários..."
mkdir -p logs
mkdir -p reports/memory

# Configurar variáveis de ambiente se necessário
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Função para limpar processos em caso de interrupção
cleanup() {
    echo ""
    echo "🛑 Interrompendo servidor MCP..."
    # Matar processos do servidor se estiverem rodando
    pkill -f "hephaestus_mcp_server.py" 2>/dev/null
    exit 0
}

# Configurar trap para limpeza
trap cleanup SIGINT SIGTERM

echo "🎯 Configuração completa!"
echo "📡 Iniciando servidor MCP via STDIO..."
echo "🔄 Para parar o servidor, pressione Ctrl+C"
echo "=================================="

# Executar o servidor com tratamento de erros
while true; do
    python3 hephaestus_mcp_server.py stdio
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Servidor finalizado normalmente"
        break
    else
        echo "❌ Servidor falhou com código $exit_code"
        echo "🔄 Tentando reiniciar em 5 segundos..."
        sleep 5
    fi
done

echo "🏁 Servidor MCP Hephaestus finalizado"

# Verificar se já está rodando
if pgrep -f "hephaestus_mcp_server.py" > /dev/null; then
    echo "⚠️  Servidor já está rodando!"
    echo "🔍 Processos encontrados:"
    ps aux | grep hephaestus_mcp_server | grep -v grep
    echo ""
    echo "Para parar o servidor, use: ./stop_mcp_server.sh"
    exit 1
fi

echo "✅ Servidor iniciado!"
echo "🆔 PID: $SERVER_PID"
echo "📄 Logs: mcp_server.log"
echo ""

# Aguardar um pouco para verificar se iniciou corretamente
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    echo "🎉 Servidor MCP Hephaestus funcionando!"
    echo ""
    echo "📋 PRÓXIMOS PASSOS:"
    echo "1. 🎯 Configure o Cursor IDE com: cursor_mcp_config.json"
    echo "2. 🔄 Reinicie o Cursor IDE"
    echo "3. 💬 No chat, digite: @hephaestus system_status"
    echo ""
    echo "🛠️  FERRAMENTAS DISPONÍVEIS:"
    echo "   • @hephaestus analyze_code"
    echo "   • @hephaestus generate_objective"
    echo "   • @hephaestus execute_rsi_cycle"
    echo "   • @hephaestus meta_intelligence_report"
    echo "   • @hephaestus performance_analysis"
    echo "   • @hephaestus evolve_capabilities"
    echo "   • @hephaestus system_status"
    echo ""
    echo "📚 Para mais detalhes: GUIA_CONFIGURACAO_CURSOR.md"
    echo "🛑 Para parar: ./stop_mcp_server.sh"
else
    echo "❌ Erro ao iniciar servidor!"
    echo "📄 Verifique os logs: cat mcp_server.log"
    exit 1
fi 