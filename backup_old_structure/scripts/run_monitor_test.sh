#!/bin/bash

# Script para executar testes do monitor autônomo
echo "🧪 Executando testes do Monitor Autônomo..."
echo "=========================================="

# Navegar para o diretório do projeto
cd /home/arthur/projects/agente_autonomo

# Executar o teste com poetry
poetry run python scripts/test_autonomous_monitor.py

# Verificar o resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Testes concluídos com sucesso!"
else
    echo ""
    echo "❌ Alguns testes falharam. Verifique os logs."
fi 