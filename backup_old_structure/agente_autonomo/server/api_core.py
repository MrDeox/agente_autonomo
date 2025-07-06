"""
FastAPI core setup for Hephaestus MCP Server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hephaestus_mcp_server import HephaestusMCPServer

app = FastAPI(
    title="Hephaestus MCP Server",
    description="Meta-Cognitive Platform for Autonomous AI Agents",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância global do servidor
hephaestus_server = None

@app.on_event("startup")
async def startup_event():
    """Inicializa o servidor na startup"""
    global hephaestus_server
    try:
        hephaestus_server = HephaestusMCPServer()
        await hephaestus_server.initialize()
    except Exception as e:
        print(f"Erro ao inicializar servidor: {e}")

@app.get("/autonomous-monitor/status")
async def get_autonomous_monitor_status():
    """Retorna status do monitor autônomo"""
    try:
        if hephaestus_server and hephaestus_server.hephaestus_agent:
            if hasattr(hephaestus_server.hephaestus_agent, 'get_autonomous_monitor_status'):
                return hephaestus_server.hephaestus_agent.get_autonomous_monitor_status()
            else:
                return {"error": "Monitor autônomo não disponível"}
        else:
            return {"error": "Servidor não inicializado"}
    except Exception as e:
        return {"error": f"Erro ao obter status do monitor: {str(e)}"}

@app.post("/autonomous-monitor/restart")
async def restart_autonomous_monitor():
    """Reinicia o monitor autônomo"""
    try:
        if hephaestus_server and hephaestus_server.hephaestus_agent:
            if hasattr(hephaestus_server.hephaestus_agent, 'stop_autonomous_monitoring') and hasattr(hephaestus_server.hephaestus_agent, 'start_autonomous_monitoring'):
                await hephaestus_server.hephaestus_agent.stop_autonomous_monitoring()
                await asyncio.sleep(2)
                await hephaestus_server.hephaestus_agent.start_autonomous_monitoring()
                return {"message": "Monitor autônomo reiniciado com sucesso"}
            else:
                return {"error": "Monitor autônomo não disponível"}
        else:
            return {"error": "Servidor não inicializado"}
    except Exception as e:
        return {"error": f"Erro ao reiniciar monitor: {str(e)}"}

@app.get("/autonomous-monitor/issues")
async def get_autonomous_monitor_issues():
    """Retorna problemas detectados pelo monitor autônomo"""
    try:
        if hephaestus_server and hephaestus_server.hephaestus_agent:
            status = hephaestus_server.hephaestus_agent.get_autonomous_monitor_status()
            return {
                "total_issues": status.get("metrics", {}).get("total_issues_detected", 0),
                "resolved_issues": status.get("metrics", {}).get("total_issues_resolved", 0),
                "unresolved_issues": status.get("metrics", {}).get("unresolved_issues", 0),
                "recent_issues": status.get("recent_issues", [])
            }
        else:
            return {"error": "Servidor não inicializado"}
    except Exception as e:
        return {"error": f"Erro ao obter problemas: {str(e)}"}


@app.post("/api/activate-coverage")
async def activate_coverage():
    """Ativa o sistema de cobertura para aumentar cobertura total"""
    try:
        if hephaestus_server and hephaestus_server.hephaestus_agent:
            results = await hephaestus_server.hephaestus_agent.activate_coverage_system()
            
            return {
                "success": results["success"],
                "message": results["message"],
                "results": results.get("results", {}),
                "report_file": results.get("report_file", ""),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": "Servidor não inicializado"}
        
    except Exception as e:
        return {"error": f"Erro ao ativar sistema de cobertura: {str(e)}"}


@app.get("/api/coverage-status")
async def get_coverage_status():
    """Retorna status do ativador de cobertura"""
    try:
        if hephaestus_server and hephaestus_server.hephaestus_agent:
            status = hephaestus_server.hephaestus_agent.get_coverage_activator_status()
            
            return {
                "success": True,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": "Servidor não inicializado"}
        
    except Exception as e:
        return {"error": f"Erro ao obter status de cobertura: {str(e)}"}


@app.get("/api/coverage-report")
async def get_coverage_report():
    """Retorna relatório de cobertura atual"""
    try:
        if hephaestus_server and hephaestus_server.hephaestus_agent:
            report = hephaestus_server.hephaestus_agent.get_coverage_report()
            
            return {
                "success": True,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {"error": "Servidor não inicializado"}
        
    except Exception as e:
        return {"error": f"Erro ao obter relatório de cobertura: {str(e)}"}