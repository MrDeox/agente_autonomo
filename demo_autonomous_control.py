"""
Demonstração de controle autônomo do Hephaestus
Simula como uma IA controlaria o sistema via MCP
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Set API key
# Load API key from .env file
from dotenv import load_dotenv
load_dotenv()

# Verify API key is loaded
if not os.getenv('OPENROUTER_API_KEY'):
    print("❌ OPENROUTER_API_KEY not found in .env file!")
    sys.exit(1)

async def simulate_ai_control():
    """Simula como uma IA controlaria o Hephaestus através do MCP."""
    
    print("🤖 SIMULAÇÃO: IA CONTROLANDO HEPHAESTUS AUTONOMAMENTE")
    print("=" * 70)
    
    # Import MCP server functions
    sys.path.append('.')
    from hephaestus_mcp_server import initialize_components, get_enhanced_agent
    
    # Initialize system
    print("🔧 Inicializando componentes...")
    await initialize_components()
    print("✅ Sistema inicializado")
    
    # Simulate AI decision making process
    print("\n🧠 IA ANALISANDO SISTEMA E TOMANDO DECISÕES...")
    
    # Step 1: Get system status
    print("\n1️⃣ OBTENDO STATUS DO SISTEMA")
    maestro = get_enhanced_agent("maestro")
    bug_hunter = get_enhanced_agent("bug_hunter")
    organizer = get_enhanced_agent("organizer")
    
    print(f"   ✅ Maestro: {'Ativo' if maestro else 'Inativo'}")
    print(f"   ✅ Bug Hunter: {'Ativo' if bug_hunter else 'Inativo'}")
    print(f"   ✅ Organizer: {'Ativo' if organizer else 'Inativo'}")
    
    # Step 2: Run bug scan (AI decides this is priority)
    print("\n2️⃣ IA DECIDE: ESCANEAR BUGS PRIMEIRO")
    if bug_hunter:
        scan_result = await bug_hunter.scan_for_bugs()
        bugs_found = scan_result.get('bugs_found', 0)
        print(f"   🐛 {bugs_found} bugs detectados")
        
        if bugs_found > 500:
            print("   🤖 IA DECISÃO: Muitos bugs! Precisa de atenção")
            
            # Get bug dashboard for analysis
            dashboard = bug_hunter.get_bug_dashboard()
            severity_info = dashboard.get('bugs_by_severity', {})
            print(f"   📊 Severidade: H:{severity_info.get('high', 0)} M:{severity_info.get('medium', 0)} L:{severity_info.get('low', 0)}")
    
    # Step 3: Analyze project structure (AI decides next priority)
    print("\n3️⃣ IA DECIDE: ANALISAR ESTRUTURA DO PROJETO")
    if organizer:
        analysis = await organizer.analyze_project_structure()
        files_analyzed = analysis.get('files_analyzed', 0)
        print(f"   📁 {files_analyzed} arquivos analisados")
        
        # Get health score
        dashboard = organizer.get_organization_dashboard()
        health = dashboard.get('structure_health', {})
        score = health.get('score', 0)
        status = health.get('status', 'unknown')
        
        print(f"   📊 Saúde estrutural: {score:.1f}% ({status})")
        
        if score < 70:
            print("   🤖 IA DECISÃO: Estrutura precisa de reorganização")
            
            # Create organization plan
            plan_result = await organizer.create_organization_plan()
            movements = plan_result.get('file_movements', 0)
            print(f"   📋 Plano criado: {movements} movimentações planejadas")
    
    # Step 4: Strategic execution (AI orchestrates)
    print("\n4️⃣ IA DECIDE: EXECUTAR ESTRATÉGIA DE MELHORIA")
    if maestro:
        # AI submits improvement objective
        objective = "Optimize codebase structure and reduce technical debt based on analysis"
        print(f"   🎯 Objetivo: {objective}")
        
        success, error = await maestro.execute(objective)
        if success:
            print("   ✅ Estratégia executada com sucesso")
            
            # Get strategy insights
            strategy_dashboard = maestro.get_strategy_dashboard()
            strategies = strategy_dashboard.get('total_strategies', 0)
            top_strategy = strategy_dashboard.get('top_strategy', ['unknown', 0])
            
            print(f"   📊 {strategies} estratégias disponíveis")
            print(f"   🏆 Top estratégia: {top_strategy[0] if top_strategy else 'none'}")
        else:
            print(f"   ⚠️ Estratégia falhou: {error}")
    
    # Step 5: AI makes final recommendations
    print("\n5️⃣ IA GERANDO RECOMENDAÇÕES FINAIS")
    
    recommendations = []
    
    if bugs_found > 500:
        recommendations.append("🐛 Prioridade ALTA: Implementar auto-fix para bugs de baixa severidade")
    
    if score < 70:
        recommendations.append("📁 Prioridade MÉDIA: Executar plano de reorganização estrutural")
    
    recommendations.append("🔄 Implementar ciclo de auto-evolução contínua")
    recommendations.append("📊 Expandir sistema de métricas para feedback mais detalhado")
    
    print("\n🤖 RECOMENDAÇÕES DA IA:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Step 6: Show autonomous capabilities
    print("\n6️⃣ CAPACIDADES AUTÔNOMAS DEMONSTRADAS")
    capabilities = [
        "✅ Análise automática de bugs e classificação por severidade",
        "✅ Avaliação estrutural do projeto com scoring quantitativo", 
        "✅ Seleção de estratégias baseada em dados históricos",
        "✅ Geração de planos de ação com análise de risco",
        "✅ Tomada de decisões baseada em métricas objetivas",
        "✅ Recomendações priorizadas por impacto vs esforço"
    ]
    
    for cap in capabilities:
        print(f"   {cap}")
    
    return True

async def demonstrate_mcp_tools():
    """Demonstra as ferramentas MCP disponíveis para controle por IA."""
    
    print("\n\n🛠️ FERRAMENTAS MCP PARA CONTROLE POR IA")
    print("=" * 70)
    
    tools = [
        {
            "name": "submit_objective",
            "description": "IA pode submeter qualquer objetivo para execução",
            "example": "submit_objective('Improve system performance by 20%')"
        },
        {
            "name": "get_system_status", 
            "description": "IA obtém status completo em tempo real",
            "example": "get_system_status() -> {health: 85%, agents: 3, alerts: 2}"
        },
        {
            "name": "run_validation",
            "description": "IA executa validações específicas ou completas",
            "example": "run_validation('security') -> {passed: 45, failed: 3}"
        },
        {
            "name": "scan_for_bugs",
            "description": "IA detecta e opcionalmente corrige bugs automaticamente",
            "example": "scan_for_bugs(auto_fix=True) -> {fixed: 12, failed: 1}"
        },
        {
            "name": "analyze_project_structure",
            "description": "IA analisa e reorganiza estrutura do projeto",
            "example": "analyze_project_structure(create_plan=True) -> {health: 67%}"
        },
        {
            "name": "execute_strategy",
            "description": "IA executa estratégias específicas via Maestro",
            "example": "execute_strategy('parallel_processing', 'optimize db')"
        },
        {
            "name": "get_metrics_dashboard",
            "description": "IA acessa métricas detalhadas para tomada de decisão",
            "example": "get_metrics_dashboard() -> {performance_data, trends}"
        },
        {
            "name": "emergency_stop",
            "description": "IA pode parar sistema em caso de problemas críticos",
            "example": "emergency_stop() -> {stopped: true, timestamp: now}"
        }
    ]
    
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. 🔧 {tool['name']}")
        print(f"   📝 {tool['description']}")
        print(f"   💡 Exemplo: {tool['example']}")
    
    print(f"\n🎯 TOTAL: {len(tools)} ferramentas para controle autônomo completo!")

async def show_evolution_potential():
    """Mostra o potencial de evolução autônoma."""
    
    print("\n\n🧬 POTENCIAL DE EVOLUÇÃO AUTÔNOMA")
    print("=" * 70)
    
    evolution_scenarios = [
        {
            "trigger": "Bug detectado com alta frequência",
            "ai_action": "Auto-cria regra de prevenção e aplica fix automático",
            "learning": "Sistema aprende padrões de bugs e previne futuros"
        },
        {
            "trigger": "Performance abaixo do threshold",
            "ai_action": "Analisa bottlenecks e otimiza código automaticamente", 
            "learning": "Desenvolve estratégias de otimização personalizadas"
        },
        {
            "trigger": "Estrutura do projeto desorganizada",
            "ai_action": "Reorganiza arquivos e refatora código automaticamente",
            "learning": "Evolui padrões de organização baseado em best practices"
        },
        {
            "trigger": "Novos requisitos ou objetivos",
            "ai_action": "Planeja e implementa features autonomamente",
            "learning": "Melhora capacidade de planejamento e execução"
        },
        {
            "trigger": "Feedback de métricas negativo",
            "ai_action": "Ajusta estratégias e parâmetros automaticamente",
            "learning": "Refina processo de tomada de decisão"
        }
    ]
    
    print("🔄 CENÁRIOS DE AUTO-EVOLUÇÃO:")
    
    for i, scenario in enumerate(evolution_scenarios, 1):
        print(f"\n{i}. 🎯 {scenario['trigger']}")
        print(f"   ⚡ Ação IA: {scenario['ai_action']}")
        print(f"   🧠 Aprendizado: {scenario['learning']}")
    
    print("\n🚀 RESULTADO: Sistema que melhora continuamente sem intervenção humana!")

async def main():
    """Função principal da demonstração."""
    
    print("🔥 DEMONSTRAÇÃO DE AUTONOMIA COMPLETA - HEPHAESTUS")
    print("=" * 80)
    print("🤖 Simulando como uma IA controlaria o sistema completamente")
    print("🎯 Objetivo: Mostrar capacidades de evolução autônoma")
    print("")
    
    # Run simulation
    success = await simulate_ai_control()
    
    if success:
        # Show MCP tools
        await demonstrate_mcp_tools()
        
        # Show evolution potential
        await show_evolution_potential()
        
        print("\n" + "=" * 80)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("✅ Hephaestus está pronto para controle autônomo completo")
        print("🧠 IA pode controlar todos os aspectos do sistema")
        print("🔄 Sistema pode evoluir continuamente sem intervenção")
        print("")
        print("🚀 PRÓXIMOS PASSOS:")
        print("1. Configure MCP no seu cliente IA (Claude, etc.)")
        print("2. Conecte e comece a controlar o Hephaestus")
        print("3. Observe a evolução autônoma em tempo real")
        print("4. O sistema vai aprender e melhorar sozinho!")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())