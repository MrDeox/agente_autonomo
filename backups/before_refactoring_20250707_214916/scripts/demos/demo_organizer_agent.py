#!/usr/bin/env python3
"""
Demonstração do OrganizerAgent - Agente Organizador do Projeto Hephaestus

Este script demonstra as capacidades do OrganizerAgent para:
- Analisar a estrutura atual do projeto
- Gerar planos de reorganização inteligentes
- Executar reorganizações de forma segura
- Gerar relatórios detalhados

Uso:
    python demo_organizer_agent.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from agent.hephaestus_agent import HephaestusAgent
from agent.config_loader import load_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OrganizerAgentDemo:
    """Demonstração do OrganizerAgent"""
    
    def __init__(self):
        self.config = load_config()
        self.hephaestus_agent = None
        
    async def setup(self):
        """Configura o agente para demonstração"""
        logger.info("🚀 Configurando OrganizerAgent para demonstração...")
        
        # Criar instância do HephaestusAgent
        self.hephaestus_agent = HephaestusAgent(
            logger_instance=logger,
            config=self.config,
            continuous_mode=False
        )
        
        logger.info("✅ OrganizerAgent configurado com sucesso!")
    
    async def demo_analyze_structure(self):
        """Demonstra análise da estrutura atual"""
        logger.info("\n" + "="*60)
        logger.info("🔍 DEMONSTRAÇÃO: Análise da Estrutura Atual")
        logger.info("="*60)
        
        try:
            result = await self.hephaestus_agent.analyze_project_structure()
            
            if result["success"]:
                analysis = result["analysis"]
                
                # Estatísticas principais
                stats = analysis["statistics"]
                logger.info(f"📊 ESTATÍSTICAS GERAIS:")
                logger.info(f"   • Total de arquivos: {stats['total_files']}")
                logger.info(f"   • Total de linhas: {stats['total_lines']:,}")
                logger.info(f"   • Tamanho total: {stats['total_size_mb']:.2f} MB")
                logger.info(f"   • Diretórios: {stats['directories_count']}")
                logger.info(f"   • Problemas identificados: {stats['problems_count']}")
                
                # Distribuição por tipo
                logger.info(f"\n📁 DISTRIBUIÇÃO POR TIPO:")
                for file_type, count in stats["file_types"].items():
                    percentage = (count / stats["total_files"]) * 100
                    logger.info(f"   • {file_type}: {count} arquivos ({percentage:.1f}%)")
                
                # Problemas identificados
                if analysis["problems"]:
                    logger.info(f"\n⚠️ PROBLEMAS IDENTIFICADOS:")
                    for i, problem in enumerate(analysis["problems"], 1):
                        logger.info(f"   {i}. {problem}")
                else:
                    logger.info(f"\n✅ Nenhum problema estrutural identificado!")
                
                # Análise de complexidade
                complexity = analysis["complexity_analysis"]
                logger.info(f"\n🧠 ANÁLISE DE COMPLEXIDADE:")
                logger.info(f"   • Score médio de complexidade: {stats['avg_complexity']:.2f}")
                logger.info(f"   • Score médio de importância: {stats['avg_importance']:.2f}")
                
                if complexity["most_complex_files"]:
                    logger.info(f"   • Arquivos mais complexos:")
                    for file_info in complexity["most_complex_files"][:3]:
                        logger.info(f"     - {file_info['path']} (score: {file_info['score']:.2f})")
                
            else:
                logger.error(f"❌ Erro na análise: {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"❌ Erro durante demonstração: {e}")
    
    async def demo_generate_plan(self):
        """Demonstra geração de plano de reorganização"""
        logger.info("\n" + "="*60)
        logger.info("📋 DEMONSTRAÇÃO: Geração de Plano de Reorganização")
        logger.info("="*60)
        
        try:
            result = await self.hephaestus_agent.generate_organization_plan()
            
            if result["success"]:
                plan = result["plan"]
                
                logger.info(f"📋 PLANO DE REORGANIZAÇÃO GERADO:")
                logger.info(f"   • Arquivos a mover: {len(plan['file_movements'])}")
                logger.info(f"   • Novos diretórios: {len(plan['new_directories'])}")
                logger.info(f"   • Ações de limpeza: {len(plan['cleanup_actions'])}")
                
                # Passos de execução
                logger.info(f"\n🔄 PASSOS DE EXECUÇÃO:")
                for i, step in enumerate(plan["execution_steps"], 1):
                    logger.info(f"   {i}. {step}")
                
                # Impacto estimado
                impact = plan["estimated_impact"]
                logger.info(f"\n📈 IMPACTO ESTIMADO:")
                logger.info(f"   • Arquivos afetados: {impact['files_affected_percentage']:.1f}%")
                logger.info(f"   • Redução de complexidade: {impact['complexity_reduction']:.1%}")
                logger.info(f"   • Melhoria de manutenibilidade: {impact['maintainability_improvement']:.1%}")
                logger.info(f"   • Melhoria da experiência do desenvolvedor: {impact['developer_experience_improvement']:.1%}")
                logger.info(f"   • Nível de risco: {impact['risk_level']:.1%}")
                
                # Exemplos de movimentos
                if plan["file_movements"]:
                    logger.info(f"\n📦 EXEMPLOS DE MOVIMENTOS:")
                    for movement in plan["file_movements"][:5]:  # Primeiros 5
                        logger.info(f"   • {movement['source']} → {movement['target']}")
                        logger.info(f"     Razão: {movement['reason']}")
                    
                    if len(plan["file_movements"]) > 5:
                        logger.info(f"   ... e mais {len(plan['file_movements']) - 5} movimentos")
                
                # Novos diretórios
                if plan["new_directories"]:
                    logger.info(f"\n📁 NOVOS DIRETÓRIOS PROPOSTOS:")
                    for dir_path in plan["new_directories"][:10]:  # Primeiros 10
                        logger.info(f"   • {dir_path}")
                    
                    if len(plan["new_directories"]) > 10:
                        logger.info(f"   ... e mais {len(plan['new_directories']) - 10} diretórios")
                
            else:
                logger.error(f"❌ Erro na geração do plano: {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"❌ Erro durante demonstração: {e}")
    
    async def demo_execute_plan_dry_run(self):
        """Demonstra execução do plano em modo dry run"""
        logger.info("\n" + "="*60)
        logger.info("🧪 DEMONSTRAÇÃO: Execução do Plano (Dry Run)")
        logger.info("="*60)
        
        try:
            result = await self.hephaestus_agent.execute_organization_plan(dry_run=True)
            
            if result["success"]:
                execution_result = result["result"]
                
                logger.info(f"✅ DRY RUN CONCLUÍDO COM SUCESSO!")
                logger.info(f"   • Tempo de execução: {execution_result['execution_time']:.2f}s")
                logger.info(f"   • Arquivos movidos: {len(execution_result['moved_files'])}")
                logger.info(f"   • Diretórios criados: {len(execution_result['created_directories'])}")
                logger.info(f"   • Erros: {len(execution_result['errors'])}")
                logger.info(f"   • Avisos: {len(execution_result['warnings'])}")
                
                # Mostrar alguns avisos (simulações)
                if execution_result["warnings"]:
                    logger.info(f"\n⚠️ AVISOS DO DRY RUN:")
                    for warning in execution_result["warnings"][:5]:
                        logger.info(f"   • {warning}")
                
                # Mostrar erros se houver
                if execution_result["errors"]:
                    logger.info(f"\n❌ ERROS IDENTIFICADOS:")
                    for error in execution_result["errors"]:
                        logger.info(f"   • {error}")
                
                logger.info(f"\n💡 O dry run simula todas as operações sem fazer mudanças reais.")
                logger.info(f"   Para executar a reorganização real, use dry_run=False")
                
            else:
                logger.error(f"❌ Erro na execução do dry run: {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"❌ Erro durante demonstração: {e}")
    
    async def demo_generate_report(self):
        """Demonstra geração de relatório completo"""
        logger.info("\n" + "="*60)
        logger.info("📊 DEMONSTRAÇÃO: Relatório Completo de Organização")
        logger.info("="*60)
        
        try:
            result = await self.hephaestus_agent.get_organization_report()
            
            if result["success"]:
                report = result["report"]
                
                # Estado atual
                current = report["current_state"]
                logger.info(f"📊 ESTADO ATUAL:")
                logger.info(f"   • Total de arquivos: {current['total_files']}")
                logger.info(f"   • Total de linhas: {current['total_lines']:,}")
                logger.info(f"   • Score de complexidade: {current['complexity_score']:.2f}")
                logger.info(f"   • Problemas identificados: {len(current['problems'])}")
                
                # Mudanças propostas
                changes = report["proposed_changes"]
                logger.info(f"\n🔄 MUDANÇAS PROPOSTAS:")
                logger.info(f"   • Arquivos a mover: {changes['files_to_move']}")
                logger.info(f"   • Novos diretórios: {changes['new_directories']}")
                logger.info(f"   • Ações de limpeza: {changes['cleanup_actions']}")
                
                # Benefícios
                benefits = report["benefits"]
                logger.info(f"\n✅ BENEFÍCIOS ESPERADOS:")
                for benefit, description in benefits.items():
                    logger.info(f"   • {benefit.replace('_', ' ').title()}: {description}")
                
                # Riscos
                risks = report["risks"]
                logger.info(f"\n⚠️ RISCOS IDENTIFICADOS:")
                for risk, description in risks.items():
                    logger.info(f"   • {risk.replace('_', ' ').title()}: {description}")
                
                # Recomendações
                recommendations = report["recommendations"]
                logger.info(f"\n💡 RECOMENDAÇÕES:")
                for i, recommendation in enumerate(recommendations, 1):
                    logger.info(f"   {i}. {recommendation}")
                
            else:
                logger.error(f"❌ Erro na geração do relatório: {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"❌ Erro durante demonstração: {e}")
    
    async def demo_show_ideal_structure(self):
        """Demonstra a estrutura ideal proposta"""
        logger.info("\n" + "="*60)
        logger.info("🏗️ DEMONSTRAÇÃO: Estrutura Ideal Proposta")
        logger.info("="*60)
        
        try:
            # Acessar diretamente o organizer para mostrar a estrutura ideal
            organizer = self.hephaestus_agent.organizer
            
            logger.info("📁 ESTRUTURA IDEAL DO PROJETO:")
            logger.info("")
            
            for dir_name, dir_structure in organizer.ideal_structure.items():
                logger.info(f"📂 {dir_name}/")
                logger.info(f"   Propósito: {dir_structure.purpose}")
                
                if dir_structure.rules:
                    logger.info(f"   Regras:")
                    for rule in dir_structure.rules:
                        logger.info(f"     • {rule}")
                
                logger.info("")
            
            logger.info("💡 Esta estrutura segue as melhores práticas de organização de projetos Python")
            logger.info("   e facilita a manutenção, navegação e colaboração entre desenvolvedores.")
            
        except Exception as e:
            logger.error(f"❌ Erro durante demonstração: {e}")
    
    async def run_full_demo(self):
        """Executa a demonstração completa"""
        logger.info("🎯 INICIANDO DEMONSTRAÇÃO COMPLETA DO ORGANIZER AGENT")
        logger.info("="*80)
        
        # Setup
        await self.setup()
        
        # Demonstrações
        await self.demo_analyze_structure()
        await self.demo_generate_plan()
        await self.demo_execute_plan_dry_run()
        await self.demo_generate_report()
        await self.demo_show_ideal_structure()
        
        logger.info("\n" + "="*80)
        logger.info("🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        logger.info("="*80)
        logger.info("")
        logger.info("📚 PRÓXIMOS PASSOS:")
        logger.info("   1. Acesse a API em http://localhost:8000/docs")
        logger.info("   2. Teste os endpoints do OrganizerAgent:")
        logger.info("      • GET /api/organizer/analyze-structure")
        logger.info("      • GET /api/organizer/generate-plan")
        logger.info("      • POST /api/organizer/execute-plan")
        logger.info("      • GET /api/organizer/report")
        logger.info("")
        logger.info("   3. Para executar uma reorganização real:")
        logger.info("      • Faça backup do projeto")
        logger.info("      • Use dry_run=False no endpoint execute-plan")
        logger.info("      • Monitore os logs para acompanhar o progresso")
        logger.info("")
        logger.info("🔧 O OrganizerAgent está pronto para reorganizar seu projeto!")
        logger.info("   Ele analisa, planeja e executa reorganizações de forma inteligente e segura.")

async def main():
    """Função principal"""
    demo = OrganizerAgentDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⏹️ Demonstração interrompida pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal na demonstração: {e}")
        sys.exit(1) 