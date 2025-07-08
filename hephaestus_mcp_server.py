"""
Hephaestus MCP Server - Controle total via MCP para IAs (Claude, etc.)
Permite que qualquer IA controle o Hephaestus diretamente via MCP
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("❌ MCP not installed. Install with: pip install mcp")
    print("📝 Note: This is for AI control via MCP protocol")
    sys.exit(1)

# Global components - will be lazy loaded
dashboard = None
validator = None
logger = None
enhanced_agents = {}

async def initialize_components():
    """Initialize Hephaestus components on-demand."""
    global dashboard, validator, logger
    
    if logger is None:
        from hephaestus.utils.logger_factory import LoggerFactory
        logger = LoggerFactory.get_component_logger("HephaestusMCP")
        logger.info("🔥 Initializing Hephaestus MCP Server...")
    
    try:
        if dashboard is None:
            from hephaestus.monitoring import get_unified_dashboard
            dashboard = get_unified_dashboard()
            await dashboard.start_monitoring()
        
        if validator is None:
            from hephaestus.validation import get_unified_validator
            validator = get_unified_validator()
        
        logger.info("✅ Hephaestus MCP components initialized")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {e}")
        return False

def get_enhanced_agent(agent_type: str):
    """Get or create enhanced agent instances."""
    global enhanced_agents
    
    if agent_type not in enhanced_agents:
        try:
            if agent_type == "maestro":
                from hephaestus.agents.maestro_enhanced import MaestroAgentEnhanced
                enhanced_agents[agent_type] = MaestroAgentEnhanced()
            elif agent_type == "bug_hunter":
                from hephaestus.agents.bug_hunter_enhanced import BugHunterAgentEnhanced
                enhanced_agents[agent_type] = BugHunterAgentEnhanced()
            elif agent_type == "organizer":
                from hephaestus.agents.organizer_enhanced import OrganizerAgentEnhanced
                enhanced_agents[agent_type] = OrganizerAgentEnhanced()
            else:
                return None
        except Exception as e:
            if logger:
                logger.error(f"Failed to create {agent_type} agent: {e}")
            return None
    
    return enhanced_agents.get(agent_type)

# Create MCP server
server = Server("hephaestus")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """Lista todas as ferramentas disponíveis para controlar o Hephaestus."""
    return [
        types.Tool(
            name="submit_objective",
            description="Submete um objetivo para o Hephaestus executar autonomamente",
            inputSchema={
                "type": "object",
                "properties": {
                    "objective": {
                        "type": "string",
                        "description": "O objetivo para o Hephaestus executar"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "description": "Nível de prioridade do objetivo",
                        "default": "medium"
                    }
                },
                "required": ["objective"]
            }
        ),
        types.Tool(
            name="get_system_status",
            description="Obtém status completo do sistema e métricas de saúde",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="run_validation",
            description="Executa validações do sistema (código, config, segurança, etc)",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope": {
                        "type": "string",
                        "enum": ["full", "code", "config", "agents", "security"],
                        "description": "Escopo da validação",
                        "default": "full"
                    }
                }
            }
        ),
        types.Tool(
            name="scan_for_bugs",
            description="Executa Bug Hunter para encontrar e opcionalmente corrigir bugs",
            inputSchema={
                "type": "object",
                "properties": {
                    "auto_fix": {
                        "type": "boolean",
                        "description": "Se deve corrigir bugs automaticamente",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="analyze_project_structure",
            description="Analisa estrutura do projeto e gera recomendações de organização",
            inputSchema={
                "type": "object",
                "properties": {
                    "create_plan": {
                        "type": "boolean",
                        "description": "Se deve criar plano de reorganização",
                        "default": True
                    }
                }
            }
        ),
        types.Tool(
            name="execute_strategy",
            description="Executa estratégia específica via Maestro agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "objective": {
                        "type": "string",
                        "description": "Objetivo para executar"
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["direct_execution", "parallel_processing", "meta_cognitive", "sequential_planning"],
                        "description": "Estratégia a usar",
                        "default": "direct_execution"
                    }
                },
                "required": ["objective"]
            }
        ),
        types.Tool(
            name="get_metrics_dashboard",
            description="Obtém dashboard completo de métricas e performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {
                        "type": "string",
                        "description": "Nome específico do agente (opcional)"
                    }
                }
            }
        ),
        types.Tool(
            name="get_agent_capabilities",
            description="Lista capacidades de todos os agentes enhanced",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="emergency_stop",
            description="Para todas as operações do Hephaestus imediatamente",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Processa chamadas de ferramentas das IAs."""
    
    # Initialize components if needed
    await initialize_components()
    
    try:
        if name == "submit_objective":
            objective = arguments["objective"]
            priority = arguments.get("priority", "medium")
            
            logger.info(f"🎯 Submitting objective: {objective}")
            
            # Usar Maestro para processar objetivo
            maestro = get_enhanced_agent("maestro")
            if maestro:
                success, error = await maestro.execute(objective)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success" if success else "failed",
                        "objective": objective,
                        "priority": priority,
                        "success": success,
                        "error": error,
                        "message": f"Objective {'completed' if success else 'failed'}: {objective}"
                    }, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "error",
                        "message": "Maestro agent not available"
                    }, indent=2)
                )]
        
        elif name == "get_system_status":
            logger.info("📊 Getting system status")
            
            # Get comprehensive status
            dashboard_data = dashboard.get_system_summary() if dashboard else {"status": "not_available"}
            validation_summary = validator.get_validation_summary() if validator else {"status": "not_available"}
            
            status = {
                "system_health": dashboard_data,
                "validation_status": validation_summary,
                "enhanced_agents": {
                    name: "active" if agent else "inactive"
                    for name, agent in enhanced_agents.items()
                },
                "mcp_status": "active",
                "timestamp": "now"
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(status, indent=2)
            )]
        
        elif name == "run_validation":
            scope = arguments.get("scope", "full")
            logger.info(f"✅ Running {scope} validation")
            
            if validator:
                result = await validator.validate_system(scope)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "validation_scope": scope,
                        "overall_status": result.overall_status,
                        "passed": result.passed,
                        "failed": result.failed,
                        "warnings": result.warnings,
                        "execution_time": result.execution_time,
                        "critical_issues": len([r for r in result.results if r.status == "failed" and r.severity == "critical"]),
                        "summary": f"Validation {result.overall_status}: {result.passed} passed, {result.failed} failed, {result.warnings} warnings"
                    }, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "Validator not available"}, indent=2)
                )]
        
        elif name == "scan_for_bugs":
            auto_fix = arguments.get("auto_fix", False)
            logger.info(f"🐛 Running bug scan (auto_fix: {auto_fix})")
            
            bug_hunter = get_enhanced_agent("bug_hunter")
            if bug_hunter:
                # Run scan
                scan_result = await bug_hunter.scan_for_bugs()
                
                result = {
                    "scan_completed": True,
                    "bugs_found": scan_result.get("bugs_found", 0),
                    "files_scanned": scan_result.get("files_scanned", 0),
                    "high_severity": scan_result.get("high_severity", 0),
                    "medium_severity": scan_result.get("medium_severity", 0),
                    "low_severity": scan_result.get("low_severity", 0)
                }
                
                # Auto-fix if requested
                if auto_fix and scan_result.get("bugs_found", 0) > 0:
                    fix_result = await bug_hunter.fix_detected_bugs()
                    result["auto_fix_applied"] = True
                    result["fixes_applied"] = fix_result.get("fixed_count", 0)
                    result["fixes_failed"] = fix_result.get("failed_count", 0)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "Bug Hunter agent not available"}, indent=2)
                )]
        
        elif name == "analyze_project_structure":
            create_plan = arguments.get("create_plan", True)
            logger.info(f"📁 Analyzing project structure (create_plan: {create_plan})")
            
            organizer = get_enhanced_agent("organizer")
            if organizer:
                # Run analysis
                analysis = await organizer.analyze_project_structure()
                
                result = {
                    "analysis_completed": True,
                    "files_analyzed": analysis.get("files_analyzed", 0),
                    "structure_issues": analysis.get("structure_issues", []),
                    "recommendations": analysis.get("recommendations", []),
                    "health_score": organizer.get_organization_dashboard().get("structure_health", {}).get("score", 0)
                }
                
                # Create plan if requested
                if create_plan:
                    plan_result = await organizer.create_organization_plan()
                    result["organization_plan"] = {
                        "plan_created": plan_result.get("plan_created", False),
                        "file_movements": plan_result.get("file_movements", 0),
                        "new_directories": plan_result.get("new_directories", 0),
                        "risk_level": plan_result.get("risk_level", "unknown")
                    }
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "Organizer agent not available"}, indent=2)
                )]
        
        elif name == "execute_strategy":
            objective = arguments["objective"]
            strategy = arguments.get("strategy", "direct_execution")
            logger.info(f"🎭 Executing strategy: {strategy} for: {objective}")
            
            maestro = get_enhanced_agent("maestro")
            if maestro:
                # Set strategy and execute
                success, error = await maestro.execute(f"Use {strategy} strategy for: {objective}")
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "strategy": strategy,
                        "objective": objective,
                        "success": success,
                        "error": error,
                        "strategy_dashboard": maestro.get_strategy_dashboard()
                    }, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "Maestro agent not available"}, indent=2)
                )]
        
        elif name == "get_metrics_dashboard":
            agent_name = arguments.get("agent_name")
            logger.info(f"📊 Getting metrics for: {agent_name or 'all'}")
            
            if dashboard:
                if agent_name:
                    metrics = dashboard.get_agent_dashboard(agent_name)
                else:
                    metrics = dashboard.get_dashboard_data()
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(metrics, indent=2)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": "Dashboard not available"}, indent=2)
                )]
        
        elif name == "get_agent_capabilities":
            logger.info("🤖 Getting agent capabilities")
            
            capabilities = {}
            
            # Check each enhanced agent
            for agent_type in ["maestro", "bug_hunter", "organizer"]:
                agent = get_enhanced_agent(agent_type)
                if agent:
                    if hasattr(agent, 'get_default_capabilities'):
                        caps = agent.get_default_capabilities()
                        capabilities[agent_type] = [cap.value if hasattr(cap, 'value') else str(cap) for cap in caps]
                    else:
                        capabilities[agent_type] = ["available"]
                else:
                    capabilities[agent_type] = ["not_available"]
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "enhanced_agents": capabilities,
                    "total_agents": len([a for a in enhanced_agents.values() if a is not None]),
                    "mcp_tools_available": len(await handle_list_tools())
                }, indent=2)
            )]
        
        elif name == "emergency_stop":
            logger.info("🚨 Emergency stop requested")
            
            # Stop monitoring
            if dashboard:
                await dashboard.stop_monitoring()
            
            # Clear agents
            enhanced_agents.clear()
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "emergency_stop": True,
                    "message": "All Hephaestus operations stopped via MCP",
                    "timestamp": "now"
                }, indent=2)
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Unknown tool: {name}",
                    "available_tools": [tool.name for tool in await handle_list_tools()]
                }, indent=2)
            )]
    
    except Exception as e:
        if logger:
            logger.error(f"❌ Error in tool {name}: {e}")
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "tool": name,
                "arguments": arguments
            }, indent=2)
        )]

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """Lista recursos disponíveis."""
    return [
        types.Resource(
            uri="hephaestus://config",
            name="Configuração do Hephaestus",
            description="Configuração atual do sistema",
            mimeType="application/json"
        ),
        types.Resource(
            uri="hephaestus://status",
            name="Status do Sistema",
            description="Status completo em tempo real",
            mimeType="application/json"
        ),
        types.Resource(
            uri="hephaestus://metrics",
            name="Métricas do Sistema",
            description="Métricas de performance",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Lê recursos do sistema."""
    await initialize_components()
    
    if uri == "hephaestus://config":
        try:
            from hephaestus.utils.config_manager import ConfigManager
            config = ConfigManager.get_full_config()
            return json.dumps(config, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Could not read config: {e}"})
    
    elif uri == "hephaestus://status":
        try:
            status = {
                "dashboard": dashboard.get_system_summary() if dashboard else None,
                "validation": validator.get_validation_summary() if validator else None,
                "agents": {name: "active" for name in enhanced_agents.keys()},
                "mcp_server": "active"
            }
            return json.dumps(status, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Could not read status: {e}"})
    
    elif uri == "hephaestus://metrics":
        try:
            if dashboard:
                metrics = dashboard.get_dashboard_data()
                return json.dumps(metrics, indent=2)
            else:
                return json.dumps({"error": "Dashboard not available"})
        except Exception as e:
            return json.dumps({"error": f"Could not read metrics: {e}"})
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

async def main():
    """Função principal do MCP server."""
    print("🔥 Hephaestus MCP Server - Controle por IA")
    print("=" * 60)
    print("🤖 Este servidor permite que IAs controlem o Hephaestus diretamente")
    print("🛠️  Ferramentas disponíveis:")
    print("   • submit_objective - Submeter objetivos")
    print("   • get_system_status - Status do sistema")
    print("   • run_validation - Executar validações")
    print("   • scan_for_bugs - Procurar e corrigir bugs")
    print("   • analyze_project_structure - Analisar estrutura")
    print("   • execute_strategy - Executar estratégias")
    print("   • get_metrics_dashboard - Obter métricas")
    print("   • emergency_stop - Parada de emergência")
    print("")
    print("🔌 Conecte sua IA cliente a este servidor MCP!")
    print("📖 Uso com Claude: Adicione nas configurações do MCP")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hephaestus",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())