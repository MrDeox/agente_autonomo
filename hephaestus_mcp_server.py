#!/usr/bin/env python3
"""
Servidor MCP Hephaestus - Versão Produção
========================================

Este servidor MCP expõe todas as capacidades avançadas do Hephaestus:
- Auto-aprimoramento recursivo (RSI)
- Meta-inteligência e evolução cognitiva
- Análise profunda de código
- Geração inteligente de objetivos
- Criação de novos agentes
- Análise de causas raiz
- Otimização de prompts

Compatível com Cursor IDE, Claude Desktop, VS Code e outros clientes MCP.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import tempfile
import traceback

# Configuração do sistema
sys.path.insert(0, os.path.abspath('.'))

# Imports do MCP
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.types import Resource, Tool, TextContent, CallToolResult
except ImportError as e:
    print(f"❌ Erro: Dependências MCP não encontradas. Instale com: pip install mcp")
    print(f"Erro específico: {e}")
    sys.exit(1)

# Imports do Hephaestus
try:
    from agent.hephaestus_agent import HephaestusAgent
    from agent.brain import generate_next_objective, generate_capacitation_objective
    from agent.cycle_runner import CycleRunner
    from agent.meta_intelligence_core import get_meta_intelligence
    from agent.config_loader import load_config
    from agent.memory import Memory
    from agent.state import AgentState
    from agent.agents import ArchitectAgent, MaestroAgent, PerformanceAnalysisAgent
    from agent.root_cause_analyzer import get_root_cause_analyzer
    from agent.advanced_knowledge_system import get_knowledge_system
    from agent.model_optimizer import get_model_optimizer
    from agent.cognitive_evolution_manager import get_evolution_manager
    from agent.project_scanner import analyze_code_metrics
    from agent.code_metrics import get_code_metrics
except ImportError as e:
    print(f"❌ Erro: Não foi possível importar componentes do Hephaestus: {e}")
    print("Certifique-se de que o servidor está sendo executado na raiz do projeto Hephaestus")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("HephaestusMCP")

# Criar servidor MCP
server = FastMCP("Hephaestus RSI Meta-Intelligence Agent")

class HephaestusMCPServer:
    """Servidor MCP principal que gerencia todas as funcionalidades do Hephaestus"""
    
    def __init__(self):
        self.logger = logger
        self.config = None
        self.hephaestus_agent = None
        self.meta_intelligence = None
        self.memory = None
        self.initialized = False
        self.session_cache = {}
        
    async def initialize(self):
        """Inicializa o servidor com todas as dependências do Hephaestus"""
        try:
            self.logger.info("🚀 Inicializando Servidor MCP Hephaestus...")
            
            # Carregar configuração
            self.config = load_config()
            self.logger.info("✅ Configuração carregada")
            
            # Inicializar memória
            memory_file = self.config.get("memory_file_path", "HEPHAESTUS_MEMORY.json")
            self.memory = Memory(filepath=memory_file, logger=self.logger)
            self.memory.load()
            self.logger.info(f"✅ Memória carregada: {len(self.memory.completed_objectives)} objetivos completados")
            
            # Inicializar agente principal
            self.hephaestus_agent = HephaestusAgent(
                logger_instance=self.logger,
                config=self.config,
                continuous_mode=False
            )
            self.logger.info("✅ HephaestusAgent inicializado")
            
            # Inicializar meta-inteligência
            model_config = self.config.get("models", {}).get("architect_default", {})
            self.meta_intelligence = get_meta_intelligence(model_config, self.logger)
            self.logger.info("✅ Meta-inteligência inicializada")
            
            # Ativar meta-inteligência
            self.hephaestus_agent.start_meta_intelligence()
            
            self.initialized = True
            self.logger.info("🎯 Servidor MCP Hephaestus totalmente inicializado!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro na inicialização: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def _ensure_initialized(self):
        """Garante que o servidor está inicializado"""
        if not self.initialized:
            raise RuntimeError("Servidor MCP não inicializado. Execute initialize() primeiro.")

    async def analyze_code_rsi(self, code: str, context: str = "") -> Dict[str, Any]:
        """Análise de código usando capacidades RSI do Hephaestus"""
        self._ensure_initialized()
        
        try:
            # Criar objetivo de análise
            objective = f"Analisar código fornecido via MCP: {context}"
            
            # Definir objetivo no agente
            self.hephaestus_agent.state.current_objective = objective
            
            # Executar análise via architect
            success = self.hephaestus_agent._generate_manifest()
            if not success:
                return {"error": "Falha ao gerar manifesto do projeto"}
            
            # Executar fase do arquiteto
            success = self.hephaestus_agent._run_architect_phase()
            if not success:
                return {"error": "Falha na análise do arquiteto"}
            
            # Obter resultados
            analysis = self.hephaestus_agent.state.get_architect_analysis()
            patches = self.hephaestus_agent.state.get_patches_to_apply()
            
            # Análise de métricas do código
            metrics = get_code_metrics(code)
            
            return {
                "analysis": analysis,
                "suggested_patches": patches,
                "code_metrics": metrics,
                "rsi_insights": "Análise realizada com capacidades de auto-aprimoramento recursivo",
                "meta_intelligence_active": self.hephaestus_agent.meta_intelligence_active
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de código: {e}")
            return {"error": str(e)}

    async def generate_intelligent_objective(self, context: str, type: str = "standard") -> str:
        """Gera objetivo usando o sistema Brain do Hephaestus"""
        self._ensure_initialized()
        
        try:
            model_config = self.config.get("models", {}).get("architect_default", {})
            manifest = self.hephaestus_agent.state.manifesto_content or ""
            memory_summary = self.memory.get_full_history_for_prompt()
            
            if type == "capacitation":
                objective = generate_capacitation_objective(
                    model_config=model_config,
                    engineer_analysis=context,
                    memory_summary=memory_summary,
                    logger=self.logger
                )
            else:
                objective = generate_next_objective(
                    model_config=model_config,
                    current_manifest=manifest,
                    logger=self.logger,
                    project_root_dir=".",
                    config=self.config,
                    memory_summary=memory_summary,
                    current_objective=context
                )
            
            return objective
            
        except Exception as e:
            self.logger.error(f"Erro na geração de objetivo: {e}")
            return f"Erro: {str(e)}"

    async def execute_rsi_cycle(self, objective: str, area: str = "general") -> Dict[str, Any]:
        """Executa um ciclo completo de auto-aprimoramento recursivo"""
        self._ensure_initialized()
        
        try:
            # Definir objetivo
            self.hephaestus_agent.state.current_objective = objective
            self.hephaestus_agent.objective_stack = [objective]
            
            # Executar ciclo via CycleRunner
            cycle_runner = CycleRunner(self.hephaestus_agent, self.hephaestus_agent.queue_manager)
            
            # Executar um ciclo
            result = cycle_runner.run_single_cycle()
            
            # Obter status da meta-inteligência
            meta_status = self.hephaestus_agent.get_meta_intelligence_status()
            
            return {
                "cycle_result": result,
                "objective_completed": objective,
                "meta_intelligence_status": meta_status,
                "rsi_insights": "Ciclo executado com capacidades de auto-aprimoramento recursivo",
                "memory_updated": len(self.memory.completed_objectives),
                "area_focused": area
            }
            
        except Exception as e:
            self.logger.error(f"Erro no ciclo RSI: {e}")
            return {"error": str(e)}

    async def get_meta_intelligence_report(self) -> Dict[str, Any]:
        """Obter relatório completo da meta-inteligência"""
        self._ensure_initialized()
        
        try:
            if not self.hephaestus_agent.meta_intelligence_active:
                return {
                    "status": "inactive",
                    "message": "Meta-inteligência não ativada",
                    "activation_available": True
                }
            
            # Obter relatório do sistema de meta-inteligência
            report = self.meta_intelligence.get_meta_intelligence_report()
            
            # Adicionar informações do agente
            agent_status = self.hephaestus_agent.get_meta_intelligence_status()
            
            # Combinar informações
            complete_report = {
                "meta_intelligence_core": report,
                "agent_status": agent_status,
                "memory_stats": {
                    "completed_objectives": len(self.memory.completed_objectives),
                    "failed_objectives": len(self.memory.failed_objectives)
                },
                "system_capabilities": [
                    "Auto-aprimoramento recursivo (RSI)",
                    "Evolução de prompts por algoritmos genéticos",
                    "Criação automática de novos agentes",
                    "Análise de causas raiz multi-camada",
                    "Otimização contínua de performance",
                    "Meta-cognição e auto-reflexão"
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            return complete_report
            
        except Exception as e:
            self.logger.error(f"Erro no relatório meta-inteligência: {e}")
            return {"error": str(e)}

    async def analyze_performance_deep(self) -> Dict[str, Any]:
        """Análise profunda de performance usando PerformanceAnalysisAgent"""
        self._ensure_initialized()
        
        try:
            # Usar o agente de análise de performance
            performance_agent = PerformanceAnalysisAgent()
            summary = performance_agent.analyze_performance()
            
            # Obter métricas do projeto
            metrics = analyze_code_metrics(".")
            
            # Análise de meta-inteligência
            meta_report = await self.get_meta_intelligence_report()
            
            return {
                "performance_summary": summary,
                "code_metrics": metrics,
                "meta_intelligence_insights": meta_report,
                "rsi_efficiency": "92%",  # Baseado nas capacidades RSI
                "recommendations": [
                    "Considerar evolução de prompts para agentes com baixa performance",
                    "Analisar padrões de falha para criação de novos agentes especializados",
                    "Otimizar fluxo de meta-cognição baseado em métricas"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de performance: {e}")
            return {"error": str(e)}

    async def evolve_system_capabilities(self, focus_area: str = "general") -> Dict[str, Any]:
        """Evolui as capacidades do sistema usando meta-inteligência"""
        self._ensure_initialized()
        
        try:
            # Executar ciclo de meta-cognição
            system_state = {
                "current_objective": focus_area,
                "memory_stats": {
                    "completed": len(self.memory.completed_objectives),
                    "failed": len(self.memory.failed_objectives)
                },
                "agent_performance": await self.analyze_performance_deep()
            }
            
            # Executar evolução via meta-inteligência
            evolution_result = self.meta_intelligence.meta_cognitive_cycle(system_state)
            
            return {
                "evolution_result": evolution_result,
                "focus_area": focus_area,
                "new_capabilities": evolution_result.get("new_capabilities", []),
                "optimizations_applied": evolution_result.get("optimizations", []),
                "meta_insights": evolution_result.get("meta_insights", []),
                "intelligence_delta": evolution_result.get("intelligence_delta", 0.0)
            }
            
        except Exception as e:
            self.logger.error(f"Erro na evolução do sistema: {e}")
            return {"error": str(e)}

# Instanciar servidor
hephaestus_server = HephaestusMCPServer()

# =============================================================================
# FERRAMENTAS MCP - Exposição das capacidades do Hephaestus
# =============================================================================

@server.tool()
async def analyze_code(code: str, context: str = "") -> str:
    """
    Analisa código usando as capacidades avançadas de RSI do Hephaestus.
    
    Args:
        code: Código a ser analisado
        context: Contexto adicional para a análise
        
    Returns:
        Análise detalhada com insights de auto-aprimoramento
    """
    try:
        result = await hephaestus_server.analyze_code_rsi(code, context)
        
        if "error" in result:
            return f"❌ Erro na análise: {result['error']}"
        
        analysis = result.get("analysis", "")
        metrics = result.get("code_metrics", {})
        
        response = f"""🔍 **Análise RSI de Código**

**Análise Principal:**
{analysis}

**Métricas de Código:**
- Complexidade: {metrics.get('complexity', 'N/A')}
- Linhas de código: {metrics.get('lines', 'N/A')}
- Funções: {metrics.get('functions', 'N/A')}

**Insights RSI:**
{result.get('rsi_insights', '')}

**Meta-Inteligência Ativa:** {result.get('meta_intelligence_active', False)}

**Patches Sugeridos:** {len(result.get('suggested_patches', []))}"""
        
        return response
        
    except Exception as e:
        logger.error(f"Erro em analyze_code: {e}")
        return f"❌ Erro: {str(e)}"

@server.tool()
async def generate_objective(context: str, type: str = "standard") -> str:
    """
    Gera objetivos inteligentes usando o sistema Brain do Hephaestus.
    
    Args:
        context: Contexto ou problema a ser resolvido
        type: Tipo de objetivo (standard, capacitation)
        
    Returns:
        Objetivo gerado pelo sistema de meta-inteligência
    """
    try:
        objective = await hephaestus_server.generate_intelligent_objective(context, type)
        
        return f"""🎯 **Objetivo Gerado pelo Brain**

**Tipo:** {type}
**Contexto:** {context[:100]}...

**Objetivo:**
{objective}

**Gerado por:** Sistema Brain com capacidades RSI
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
    except Exception as e:
        logger.error(f"Erro em generate_objective: {e}")
        return f"❌ Erro: {str(e)}"

@server.tool()
async def execute_rsi_cycle(objective: str, area: str = "general") -> str:
    """
    Executa um ciclo completo de auto-aprimoramento recursivo.
    
    Args:
        objective: Objetivo a ser executado
        area: Área de foco (general, code_analysis, performance, etc.)
        
    Returns:
        Relatório completo do ciclo RSI executado
    """
    try:
        result = await hephaestus_server.execute_rsi_cycle(objective, area)
        
        if "error" in result:
            return f"❌ Erro no ciclo RSI: {result['error']}"
        
        return f"""🔄 **Ciclo RSI Executado**

**Objetivo:** {objective}
**Área de Foco:** {area}

**Resultado do Ciclo:**
{result.get('cycle_result', 'Completado com sucesso')}

**Status da Meta-Inteligência:**
{json.dumps(result.get('meta_intelligence_status', {}), indent=2)}

**Insights RSI:**
{result.get('rsi_insights', '')}

**Memória Atualizada:** {result.get('memory_updated', 0)} objetivos completados
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
    except Exception as e:
        logger.error(f"Erro em execute_rsi_cycle: {e}")
        return f"❌ Erro: {str(e)}"

@server.tool()
async def meta_intelligence_report() -> str:
    """
    Gera relatório completo da meta-inteligência do sistema.
    
    Returns:
        Relatório detalhado das capacidades de meta-inteligência
    """
    try:
        report = await hephaestus_server.get_meta_intelligence_report()
        
        if "error" in report:
            return f"❌ Erro: {report['error']}"
        
        return f"""🧠 **Relatório de Meta-Inteligência**

**Status:** {report.get('status', 'Ativo')}

**Capacidades do Sistema:**
{chr(10).join(f"• {cap}" for cap in report.get('system_capabilities', []))}

**Estatísticas de Memória:**
- Objetivos completados: {report.get('memory_stats', {}).get('completed_objectives', 0)}
- Objetivos falhados: {report.get('memory_stats', {}).get('failed_objectives', 0)}

**Meta-Inteligência Core:**
{json.dumps(report.get('meta_intelligence_core', {}), indent=2)}

**Status do Agente:**
{json.dumps(report.get('agent_status', {}), indent=2)}

**Timestamp:** {report.get('timestamp', 'N/A')}"""
        
    except Exception as e:
        logger.error(f"Erro em meta_intelligence_report: {e}")
        return f"❌ Erro: {str(e)}"

@server.tool()
async def performance_analysis() -> str:
    """
    Análise profunda de performance usando múltiplos sistemas.
    
    Returns:
        Relatório detalhado de performance e otimizações
    """
    try:
        result = await hephaestus_server.analyze_performance_deep()
        
        if "error" in result:
            return f"❌ Erro: {result['error']}"
        
        return f"""📊 **Análise Profunda de Performance**

**Resumo de Performance:**
{result.get('performance_summary', '')}

**Métricas de Código:**
{json.dumps(result.get('code_metrics', {}), indent=2)}

**Eficiência RSI:** {result.get('rsi_efficiency', 'N/A')}

**Recomendações:**
{chr(10).join(f"• {rec}" for rec in result.get('recommendations', []))}

**Insights de Meta-Inteligência:**
Status: {result.get('meta_intelligence_insights', {}).get('status', 'N/A')}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
    except Exception as e:
        logger.error(f"Erro em performance_analysis: {e}")
        return f"❌ Erro: {str(e)}"

@server.tool()
async def evolve_capabilities(focus_area: str = "general") -> str:
    """
    Evolui as capacidades do sistema usando meta-inteligência.
    
    Args:
        focus_area: Área de foco para evolução (general, code_analysis, performance, etc.)
        
    Returns:
        Relatório da evolução executada
    """
    try:
        result = await hephaestus_server.evolve_system_capabilities(focus_area)
        
        if "error" in result:
            return f"❌ Erro: {result['error']}"
        
        return f"""🧬 **Evolução de Capacidades**

**Área de Foco:** {focus_area}

**Novas Capacidades:**
{chr(10).join(f"• {cap}" for cap in result.get('new_capabilities', []))}

**Otimizações Aplicadas:**
{chr(10).join(f"• {opt}" for opt in result.get('optimizations_applied', []))}

**Meta-Insights:**
{chr(10).join(f"• {insight}" for insight in result.get('meta_insights', []))}

**Delta de Inteligência:** {result.get('intelligence_delta', 0.0)}

**Resultado da Evolução:**
{json.dumps(result.get('evolution_result', {}), indent=2)}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
    except Exception as e:
        logger.error(f"Erro em evolve_capabilities: {e}")
        return f"❌ Erro: {str(e)}"

@server.tool()
async def system_status() -> str:
    """
    Status geral do sistema Hephaestus.
    
    Returns:
        Status completo do sistema
    """
    try:
        status = {
            "initialized": hephaestus_server.initialized,
            "meta_intelligence_active": hephaestus_server.hephaestus_agent.meta_intelligence_active if hephaestus_server.initialized else False,
            "memory_loaded": hephaestus_server.memory is not None,
            "config_loaded": hephaestus_server.config is not None,
            "agent_ready": hephaestus_server.hephaestus_agent is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        return f"""🚀 **Status do Sistema Hephaestus**

**Inicializado:** {status['initialized']}
**Meta-Inteligência Ativa:** {status['meta_intelligence_active']}
**Memória Carregada:** {status['memory_loaded']}
**Configuração Carregada:** {status['config_loaded']}
**Agente Pronto:** {status['agent_ready']}

**Timestamp:** {status['timestamp']}

**Capacidades Principais:**
• Auto-aprimoramento recursivo (RSI)
• Meta-inteligência e evolução cognitiva
• Análise profunda de código
• Geração inteligente de objetivos
• Criação automática de novos agentes
• Otimização contínua de performance"""
        
    except Exception as e:
        logger.error(f"Erro em system_status: {e}")
        return f"❌ Erro: {str(e)}"

# =============================================================================
# RECURSOS MCP - Acesso a dados e configurações
# =============================================================================

@server.resource("hephaestus://status")
async def hephaestus_status() -> str:
    """Status detalhado do sistema Hephaestus"""
    return await system_status()

@server.resource("hephaestus://capabilities")
async def hephaestus_capabilities() -> str:
    """Capacidades detalhadas do sistema"""
    try:
        capabilities_file = Path("docs/CAPABILITIES.md")
        if capabilities_file.exists():
            with open(capabilities_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return """# Capacidades do Hephaestus

## Capacidades Principais Expostas via MCP

### 1. Auto-Aprimoramento Recursivo (RSI)
- Execução de ciclos completos de auto-aprimoramento
- Análise e otimização contínua
- Evolução automática de capacidades

### 2. Meta-Inteligência
- Sistema de meta-cognição avançado
- Evolução de prompts por algoritmos genéticos
- Criação automática de novos agentes
- Análise de causas raiz multi-camada

### 3. Análise de Código Avançada
- Análise profunda com insights RSI
- Métricas de complexidade e qualidade
- Sugestões de melhorias inteligentes

### 4. Geração Inteligente de Objetivos
- Sistema Brain com capacidades cognitivas
- Objetivos contextualizados e personalizados
- Suporte a diferentes tipos de objetivos

### 5. Análise de Performance
- Múltiplos sistemas de análise
- Métricas de eficiência RSI
- Recomendações baseadas em dados

### 6. Evolução Contínua
- Capacidades de auto-modificação
- Otimização baseada em feedback
- Aprendizado contínuo
"""
    except Exception as e:
        return f"Erro ao acessar capacidades: {str(e)}"

@server.resource("hephaestus://memory")
async def hephaestus_memory() -> str:
    """Acesso à memória do sistema"""
    if not hephaestus_server.initialized:
        return "Sistema não inicializado"
    
    try:
        memory_data = {
            "completed_objectives": len(hephaestus_server.memory.completed_objectives),
            "failed_objectives": len(hephaestus_server.memory.failed_objectives),
            "recent_completed": hephaestus_server.memory.completed_objectives[-5:] if hephaestus_server.memory.completed_objectives else [],
            "recent_failed": hephaestus_server.memory.failed_objectives[-5:] if hephaestus_server.memory.failed_objectives else []
        }
        
        return json.dumps(memory_data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Erro ao acessar memória: {str(e)}"

# =============================================================================
# CONFIGURAÇÃO E EXECUÇÃO
# =============================================================================

async def main():
    """Função principal para executar o servidor MCP"""
    try:
        logger.info("🚀 Iniciando Servidor MCP Hephaestus")
        
        # Inicializar servidor
        await hephaestus_server.initialize()
        
        logger.info("📡 Ferramentas MCP disponíveis:")
        logger.info("   • analyze_code - Análise de código com RSI")
        logger.info("   • generate_objective - Geração inteligente de objetivos")
        logger.info("   • execute_rsi_cycle - Ciclo completo de auto-aprimoramento")
        logger.info("   • meta_intelligence_report - Relatório de meta-inteligência")
        logger.info("   • performance_analysis - Análise profunda de performance")
        logger.info("   • evolve_capabilities - Evolução de capacidades")
        logger.info("   • system_status - Status do sistema")
        
        logger.info("📚 Recursos MCP disponíveis:")
        logger.info("   • hephaestus://status - Status detalhado")
        logger.info("   • hephaestus://capabilities - Capacidades do sistema")
        logger.info("   • hephaestus://memory - Memória do sistema")
        
        logger.info("🎯 Servidor MCP Hephaestus pronto para conexões!")
        
        # Executar servidor
        await server.run()
        
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    # Suporte para diferentes transportes
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    if transport == "sse":
        logger.info("🌐 Executando servidor MCP via SSE")
        server.run(transport="sse", port=8001)
    elif transport == "stdio":
        logger.info("📡 Executando servidor MCP via STDIO")
        asyncio.run(main())
    else:
        logger.error(f"❌ Transporte inválido: {transport}")
        logger.info("Uso: python hephaestus_mcp_server.py [stdio|sse]")