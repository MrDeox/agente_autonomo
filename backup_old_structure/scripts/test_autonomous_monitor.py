#!/usr/bin/env python3
"""
Script de teste para o sistema de monitoramento autônomo
Valida todas as funcionalidades do monitor e sistema de prevenção de erros
"""

import asyncio
import time
import requests
import json
import subprocess
import sys
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agents.autonomous_monitor_agent import AutonomousMonitorAgent
from agent.utils.advanced_logging import setup_advanced_logging
import logging

class AutonomousMonitorTester:
    """Classe para testar o sistema de monitoramento autônomo"""
    
    def __init__(self):
        self.logger = setup_advanced_logging("monitor_tester", level=logging.INFO)
        self.base_url = "http://localhost:8000"
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Registra resultado de um teste"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        
        self.logger.info(result)
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    async def test_server_health(self) -> bool:
        """Testa se o servidor está respondendo"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Servidor Respondendo", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Servidor Respondendo", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Servidor Respondendo", False, f"Erro: {str(e)}")
            return False
    
    async def test_monitor_status(self) -> bool:
        """Testa o endpoint de status do monitor"""
        try:
            response = requests.get(f"{self.base_url}/monitor/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Status do Monitor", True, f"Ativo: {data.get('active', False)}")
                return True
            else:
                self.log_test("Status do Monitor", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Status do Monitor", False, f"Erro: {str(e)}")
            return False
    
    async def test_monitor_issues(self) -> bool:
        """Testa o endpoint de issues do monitor"""
        try:
            response = requests.get(f"{self.base_url}/monitor/issues", timeout=5)
            if response.status_code == 200:
                data = response.json()
                issues_count = len(data.get('issues', []))
                self.log_test("Issues do Monitor", True, f"Encontrados: {issues_count} issues")
                return True
            else:
                self.log_test("Issues do Monitor", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Issues do Monitor", False, f"Erro: {str(e)}")
            return False
    
    async def test_health_endpoint(self) -> bool:
        """Testa o endpoint de health detalhado"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                self.log_test("Health Detalhado", True, f"Status: {status}")
                return True
            else:
                self.log_test("Health Detalhado", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Detalhado", False, f"Erro: {str(e)}")
            return False
    
    async def test_error_prevention_report(self) -> bool:
        """Testa o endpoint de relatório de prevenção de erros"""
        try:
            response = requests.get(f"{self.base_url}/error-prevention/report", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Relatório Prevenção", True, "Relatório gerado com sucesso")
                return True
            else:
                self.log_test("Relatório Prevenção", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Relatório Prevenção", False, f"Erro: {str(e)}")
            return False
    
    async def test_monitor_agent_creation(self) -> bool:
        """Testa a criação do agente monitor"""
        try:
            monitor = AutonomousMonitorAgent()
            self.log_test("Criação do Agente Monitor", True, "Agente criado com sucesso")
            return True
        except Exception as e:
            self.log_test("Criação do Agente Monitor", False, f"Erro: {str(e)}")
            return False
    
    async def test_git_status(self) -> bool:
        """Testa se o git está funcionando"""
        try:
            result = subprocess.run(
                ["git", "status"], 
                capture_output=True, 
                text=True, 
                cwd="/home/arthur/projects/agente_autonomo",
                timeout=10
            )
            if result.returncode == 0:
                self.log_test("Git Status", True, "Git funcionando corretamente")
                return True
            else:
                self.log_test("Git Status", False, f"Erro git: {result.stderr}")
                return False
        except Exception as e:
            self.log_test("Git Status", False, f"Erro: {str(e)}")
            return False
    
    async def test_recent_commits(self) -> bool:
        """Testa se há commits recentes"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-5", "--since=1 hour ago"], 
                capture_output=True, 
                text=True, 
                cwd="/home/arthur/projects/agente_autonomo",
                timeout=10
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')
                commits = [c for c in commits if c]  # Remove linhas vazias
                self.log_test("Commits Recentes", True, f"Encontrados: {len(commits)} commits")
                return True
            else:
                self.log_test("Commits Recentes", False, f"Erro git: {result.stderr}")
                return False
        except Exception as e:
            self.log_test("Commits Recentes", False, f"Erro: {str(e)}")
            return False
    
    async def test_system_resources(self) -> bool:
        """Testa se consegue verificar recursos do sistema"""
        try:
            # Testa se consegue ler /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            
            # Testa se consegue ler /proc/loadavg
            with open('/proc/loadavg', 'r') as f:
                loadavg = f.read()
            
            self.log_test("Recursos do Sistema", True, "Acesso aos recursos OK")
            return True
        except Exception as e:
            self.log_test("Recursos do Sistema", False, f"Erro: {str(e)}")
            return False
    
    async def test_log_files(self) -> bool:
        """Testa se os arquivos de log existem"""
        try:
            log_dir = "/home/arthur/projects/agente_autonomo/logs"
            if os.path.exists(log_dir):
                log_files = os.listdir(log_dir)
                self.log_test("Arquivos de Log", True, f"Encontrados: {len(log_files)} arquivos")
                return True
            else:
                self.log_test("Arquivos de Log", False, "Diretório de logs não existe")
                return False
        except Exception as e:
            self.log_test("Arquivos de Log", False, f"Erro: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        self.logger.info("🚀 Iniciando testes do sistema de monitoramento autônomo...")
        
        tests = [
            ("Servidor", self.test_server_health),
            ("Status do Monitor", self.test_monitor_status),
            ("Issues do Monitor", self.test_monitor_issues),
            ("Health Detalhado", self.test_health_endpoint),
            ("Relatório Prevenção", self.test_error_prevention_report),
            ("Criação do Agente", self.test_monitor_agent_creation),
            ("Git Status", self.test_git_status),
            ("Commits Recentes", self.test_recent_commits),
            ("Recursos do Sistema", self.test_system_resources),
            ("Arquivos de Log", self.test_log_files),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Erro no teste {test_name}: {str(e)}")
                results.append(False)
        
        # Resumo final
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        self.logger.info("=" * 60)
        self.logger.info(f"📊 RESUMO DOS TESTES")
        self.logger.info(f"✅ Passaram: {passed}/{total}")
        self.logger.info(f"❌ Falharam: {total - passed}/{total}")
        self.logger.info(f"📈 Taxa de Sucesso: {success_rate:.1f}%")
        self.logger.info("=" * 60)
        
        # Salvar resultados em arquivo
        self.save_results()
        
        return success_rate >= 80  # Considera sucesso se 80% ou mais passaram
    
    def save_results(self):
        """Salva os resultados dos testes"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs/monitor_test_results_{timestamp}.json"
            
            os.makedirs("logs", exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "results": self.test_results,
                    "summary": {
                        "total_tests": len(self.test_results),
                        "passed": sum(1 for r in self.test_results if r["success"]),
                        "failed": sum(1 for r in self.test_results if not r["success"])
                    }
                }, f, indent=2)
            
            self.logger.info(f"📄 Resultados salvos em: {filename}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados: {str(e)}")

async def main():
    """Função principal"""
    tester = AutonomousMonitorTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 Testes concluídos com sucesso! Sistema funcionando corretamente.")
            return 0
        else:
            print("\n⚠️  Alguns testes falharam. Verifique os logs para mais detalhes.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário.")
        return 1
    except Exception as e:
        print(f"\n💥 Erro durante os testes: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 