#!/bin/bash
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
