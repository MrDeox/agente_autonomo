"""
Autonomous Monitor Agent - Agente que monitora e resolve problemas automaticamente
"""

import asyncio
import logging
import time
import subprocess
import psutil
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
import signal
import sys

from ..utils.advanced_logging import setup_advanced_logging
import logging


@dataclass
class SystemHealth:
    """Dados de saúde do sistema"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    server_status: str
    pipeline_status: str
    last_commit: Optional[str]
    error_count: int
    uptime: float
    timestamp: datetime


@dataclass
class Issue:
    """Problema detectado"""
    id: str
    type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    detected_at: datetime
    resolved: bool = False
    resolution: Optional[str] = None
    resolution_time: Optional[datetime] = None


class AutonomousMonitorAgent:
    """
    Agente autônomo que monitora o sistema Hephaestus continuamente
    e resolve problemas automaticamente
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = setup_advanced_logging("autonomous_monitor", level=logging.INFO)
        
        # Configurações de monitoramento
        self.monitor_interval = self.config.get('monitor_interval', 30)  # segundos
        self.health_check_interval = self.config.get('health_check_interval', 60)
        self.max_retries = self.config.get('max_retries', 3)
        self.auto_fix_enabled = self.config.get('auto_fix_enabled', True)
        
        # Estado do monitoramento
        self.is_running = False
        self.health_history: List[SystemHealth] = []
        self.issues: List[Issue] = []
        self.last_health_check = None
        self.start_time = datetime.now()
        
        # Métricas
        self.total_issues_detected = 0
        self.total_issues_resolved = 0
        self.system_restarts = 0
        
        self.logger.info("AutonomousMonitorAgent inicializado")
    
    async def start_monitoring(self):
        """Inicia o monitoramento autônomo"""
        self.is_running = True
        self.logger.info("🚀 Iniciando monitoramento autônomo do sistema")
        
        # Inicia tarefas de monitoramento
        tasks = [
            asyncio.create_task(self._continuous_monitoring()),
            asyncio.create_task(self._health_checker()),
            asyncio.create_task(self._issue_resolver()),
            asyncio.create_task(self._performance_analyzer()),
            asyncio.create_task(self._commit_monitor())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Erro no monitoramento: {e}")
            await self._handle_critical_error(e)
    
    async def _continuous_monitoring(self):
        """Monitoramento contínuo do sistema"""
        while self.is_running:
            try:
                health = await self._check_system_health()
                self.health_history.append(health)
                
                # Mantém apenas os últimos 100 registros
                if len(self.health_history) > 100:
                    self.health_history = self.health_history[-100:]
                
                # Detecta problemas
                await self._detect_issues(health)
                
                # Log de status
                if health.error_count > 0:
                    self.logger.warning(f"⚠️  {health.error_count} erros detectados")
                
                await asyncio.sleep(self.monitor_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitoramento contínuo: {e}")
                await asyncio.sleep(5)
    
    async def _check_system_health(self) -> SystemHealth:
        """Verifica a saúde do sistema"""
        try:
            # Métricas do sistema
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Status do servidor
            server_status = await self._check_server_status()
            
            # Status do pipeline
            pipeline_status = await self._check_pipeline_status()
            
            # Último commit
            last_commit = await self._get_last_commit()
            
            # Contagem de erros
            error_count = len([i for i in self.issues if not i.resolved])
            
            # Uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            return SystemHealth(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                server_status=server_status,
                pipeline_status=pipeline_status,
                last_commit=last_commit,
                error_count=error_count,
                uptime=uptime,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde do sistema: {e}")
            return SystemHealth(
                cpu_usage=0,
                memory_usage=0,
                disk_usage=0,
                server_status="error",
                pipeline_status="error",
                last_commit=None,
                error_count=len(self.issues) + 1,
                uptime=(datetime.now() - self.start_time).total_seconds(),
                timestamp=datetime.now()
            )
    
    async def _check_server_status(self) -> str:
        """Verifica status do servidor HTTP"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                return "healthy"
            else:
                return "unhealthy"
        except:
            return "down"
    
    async def _check_pipeline_status(self) -> str:
        """Verifica status do pipeline otimizado"""
        try:
            # Verifica se o processo principal está rodando
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'python' in proc.info['name'] and 'main.py' in ' '.join(proc.info['cmdline'] or []):
                    return "running"
            return "stopped"
        except:
            return "unknown"
    
    async def _get_last_commit(self) -> Optional[str]:
        """Obtém o último commit"""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H %s'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None
    
    async def _detect_issues(self, health: SystemHealth):
        """Detecta problemas baseado na saúde do sistema"""
        issues = []
        
        # CPU alto
        if health.cpu_usage > 90:
            issues.append(Issue(
                id=f"cpu_high_{int(time.time())}",
                type="performance",
                severity="medium",
                description=f"CPU usage muito alto: {health.cpu_usage}%",
                detected_at=datetime.now()
            ))
        
        # Memória alta
        if health.memory_usage > 85:
            issues.append(Issue(
                id=f"memory_high_{int(time.time())}",
                type="performance",
                severity="high",
                description=f"Uso de memória muito alto: {health.memory_usage}%",
                detected_at=datetime.now()
            ))
        
        # Servidor down
        if health.server_status == "down":
            issues.append(Issue(
                id=f"server_down_{int(time.time())}",
                type="service",
                severity="critical",
                description="Servidor HTTP não está respondendo",
                detected_at=datetime.now()
            ))
        
        # Pipeline parado
        if health.pipeline_status == "stopped":
            issues.append(Issue(
                id=f"pipeline_stopped_{int(time.time())}",
                type="service",
                severity="high",
                description="Pipeline otimizado parou de funcionar",
                detected_at=datetime.now()
            ))
        
        # Sem commits recentes (mais de 1 hora)
        if health.last_commit:
            # Extrai timestamp do commit
            try:
                commit_time = subprocess.run(
                    ['git', 'log', '-1', '--format=%ct'],
                    capture_output=True, text=True, timeout=10
                )
                if commit_time.returncode == 0:
                    commit_timestamp = int(commit_time.stdout.strip())
                    commit_datetime = datetime.fromtimestamp(commit_timestamp)
                    if datetime.now() - commit_datetime > timedelta(hours=1):
                        issues.append(Issue(
                            id=f"no_recent_commits_{int(time.time())}",
                            type="workflow",
                            severity="medium",
                            description="Nenhum commit nas últimas horas",
                            detected_at=datetime.now()
                        ))
            except:
                pass
        
        # Adiciona novos problemas
        for issue in issues:
            if not any(i.id == issue.id for i in self.issues):
                self.issues.append(issue)
                self.total_issues_detected += 1
                self.logger.warning(f"🚨 Problema detectado: {issue.description}")
    
    async def _issue_resolver(self):
        """Resolve problemas automaticamente"""
        while self.is_running:
            try:
                unresolved_issues = [i for i in self.issues if not i.resolved]
                
                for issue in unresolved_issues:
                    if self.auto_fix_enabled:
                        await self._resolve_issue(issue)
                
                await asyncio.sleep(10)  # Verifica a cada 10 segundos
                
            except Exception as e:
                self.logger.error(f"Erro no resolvedor de problemas: {e}")
                await asyncio.sleep(5)
    
    async def _resolve_issue(self, issue: Issue):
        """Tenta resolver um problema específico"""
        try:
            self.logger.info(f"🔧 Tentando resolver: {issue.description}")
            
            if issue.type == "service" and issue.severity == "critical":
                # Reinicia o servidor
                await self._restart_server()
                issue.resolved = True
                issue.resolution = "Servidor reiniciado automaticamente"
                
            elif issue.type == "service" and "pipeline" in issue.description.lower():
                # Reinicia o pipeline
                await self._restart_pipeline()
                issue.resolved = True
                issue.resolution = "Pipeline reiniciado automaticamente"
                
            elif issue.type == "performance" and "memory" in issue.description.lower():
                # Limpa cache e libera memória
                await self._cleanup_memory()
                issue.resolved = True
                issue.resolution = "Memória limpa automaticamente"
                
            elif issue.type == "workflow" and "commit" in issue.description.lower():
                # Força execução do pipeline
                await self._force_pipeline_execution()
                issue.resolved = True
                issue.resolution = "Pipeline forçado a executar"
            
            if issue.resolved:
                issue.resolution_time = datetime.now()
                self.total_issues_resolved += 1
                self.logger.info(f"✅ Problema resolvido: {issue.resolution}")
                
        except Exception as e:
            self.logger.error(f"Erro ao resolver problema {issue.id}: {e}")
    
    async def _restart_server(self):
        """Reinicia o servidor"""
        try:
            self.logger.info("🔄 Reiniciando servidor...")
            
            # Mata processos existentes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'python' in proc.info['name'] and 'main.py' in ' '.join(proc.info['cmdline'] or []):
                    proc.terminate()
                    proc.wait(timeout=10)
            
            # Reinicia o servidor
            subprocess.Popen(['python', 'main.py'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            
            self.system_restarts += 1
            await asyncio.sleep(10)  # Aguarda inicialização
            
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar servidor: {e}")
    
    async def _restart_pipeline(self):
        """Reinicia o pipeline"""
        try:
            self.logger.info("🔄 Reiniciando pipeline...")
            
            # Força execução do pipeline
            await self._force_pipeline_execution()
            
        except Exception as e:
            self.logger.error(f"Erro ao reiniciar pipeline: {e}")
    
    async def _cleanup_memory(self):
        """Limpa memória"""
        try:
            import gc
            gc.collect()
            
            # Limpa logs antigos se necessário
            log_dir = "logs"
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    file_path = os.path.join(log_dir, file)
                    if os.path.isfile(file_path):
                        # Remove arquivos de log com mais de 7 dias
                        if time.time() - os.path.getmtime(file_path) > 7 * 24 * 3600:
                            os.remove(file_path)
            
            self.logger.info("🧹 Memória limpa")
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar memória: {e}")
    
    async def _force_pipeline_execution(self):
        """Força execução do pipeline"""
        try:
            self.logger.info("⚡ Forçando execução do pipeline...")
            
            # Envia sinal para executar pipeline
            response = requests.post("http://localhost:8000/execute-pipeline", 
                                   json={"force": True}, timeout=30)
            
            if response.status_code == 200:
                self.logger.info("✅ Pipeline executado com sucesso")
            else:
                self.logger.warning("⚠️ Pipeline não executado")
                
        except Exception as e:
            self.logger.error(f"Erro ao forçar pipeline: {e}")
    
    async def _health_checker(self):
        """Verificação periódica de saúde"""
        while self.is_running:
            try:
                health = await self._check_system_health()
                
                # Log de saúde a cada hora
                if not self.last_health_check or \
                   (datetime.now() - self.last_health_check).seconds > 3600:
                    
                    self.logger.info(f"📊 Status do Sistema:")
                    self.logger.info(f"   CPU: {health.cpu_usage:.1f}%")
                    self.logger.info(f"   Memória: {health.memory_usage:.1f}%")
                    self.logger.info(f"   Disco: {health.disk_usage:.1f}%")
                    self.logger.info(f"   Servidor: {health.server_status}")
                    self.logger.info(f"   Pipeline: {health.pipeline_status}")
                    self.logger.info(f"   Problemas: {health.error_count}")
                    self.logger.info(f"   Uptime: {health.uptime/3600:.1f}h")
                    
                    self.last_health_check = datetime.now()
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no health checker: {e}")
                await asyncio.sleep(30)
    
    async def _performance_analyzer(self):
        """Analisa performance e otimiza automaticamente"""
        while self.is_running:
            try:
                if len(self.health_history) >= 10:
                    recent_health = self.health_history[-10:]
                    
                    avg_cpu = sum(h.cpu_usage for h in recent_health) / len(recent_health)
                    avg_memory = sum(h.memory_usage for h in recent_health) / len(recent_health)
                    
                    # Se performance está degradada, tenta otimizar
                    if avg_cpu > 80 or avg_memory > 80:
                        await self._optimize_performance()
                
                await asyncio.sleep(300)  # Verifica a cada 5 minutos
                
            except Exception as e:
                self.logger.error(f"Erro no analisador de performance: {e}")
                await asyncio.sleep(60)
    
    async def _optimize_performance(self):
        """Otimiza performance do sistema"""
        try:
            self.logger.info("⚡ Otimizando performance...")
            
            # Limpa cache
            await self._cleanup_memory()
            
            # Reduz frequência de monitoramento temporariamente
            original_interval = self.monitor_interval
            self.monitor_interval = min(60, self.monitor_interval * 2)
            
            await asyncio.sleep(60)
            
            # Restaura frequência
            self.monitor_interval = original_interval
            
            self.logger.info("✅ Performance otimizada")
            
        except Exception as e:
            self.logger.error(f"Erro ao otimizar performance: {e}")
    
    async def _commit_monitor(self):
        """Monitora commits e garante que o sistema está funcionando"""
        while self.is_running:
            try:
                last_commit = await self._get_last_commit()
                
                if last_commit:
                    # Verifica se houve commits recentes
                    commit_time = subprocess.run(
                        ['git', 'log', '-1', '--format=%ct'],
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if commit_time.returncode == 0:
                        commit_timestamp = int(commit_time.stdout.strip())
                        commit_datetime = datetime.fromtimestamp(commit_timestamp)
                        
                        # Se não há commits nas últimas 2 horas, força execução
                        if datetime.now() - commit_datetime > timedelta(hours=2):
                            self.logger.warning("⏰ Sem commits recentes, forçando execução...")
                            await self._force_pipeline_execution()
                
                await asyncio.sleep(1800)  # Verifica a cada 30 minutos
                
            except Exception as e:
                self.logger.error(f"Erro no monitor de commits: {e}")
                await asyncio.sleep(300)
    
    async def _handle_critical_error(self, error: Exception):
        """Lida com erros críticos"""
        self.logger.critical(f"🚨 ERRO CRÍTICO NO MONITOR: {error}")
        
        # Tenta reiniciar o monitor
        try:
            self.logger.info("🔄 Reiniciando monitor autônomo...")
            await asyncio.sleep(10)
            await self.start_monitoring()
        except Exception as e:
            self.logger.critical(f"Falha ao reiniciar monitor: {e}")
    
    def get_status_report(self) -> Dict[str, Any]:
        """Gera relatório de status"""
        current_health = self.health_history[-1] if self.health_history else None
        
        return {
            "status": "running" if self.is_running else "stopped",
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "current_health": {
                "cpu_usage": current_health.cpu_usage if current_health else 0,
                "memory_usage": current_health.memory_usage if current_health else 0,
                "server_status": current_health.server_status if current_health else "unknown",
                "pipeline_status": current_health.pipeline_status if current_health else "unknown",
                "error_count": current_health.error_count if current_health else 0
            },
            "metrics": {
                "total_issues_detected": self.total_issues_detected,
                "total_issues_resolved": self.total_issues_resolved,
                "system_restarts": self.system_restarts,
                "unresolved_issues": len([i for i in self.issues if not i.resolved])
            },
            "recent_issues": [
                {
                    "id": i.id,
                    "type": i.type,
                    "severity": i.severity,
                    "description": i.description,
                    "detected_at": i.detected_at.isoformat(),
                    "resolved": i.resolved,
                    "resolution": i.resolution
                }
                for i in self.issues[-5:]  # Últimos 5 problemas
            ]
        }
    
    def get_current_issues(self) -> List[Dict[str, Any]]:
        """Retorna issues atuais não resolvidos"""
        return [
            {
                "id": issue.id,
                "type": issue.type,
                "severity": issue.severity,
                "description": issue.description,
                "detected_at": issue.detected_at.isoformat(),
                "resolved": issue.resolved,
                "resolution": issue.resolution,
                "resolution_time": issue.resolution_time.isoformat() if issue.resolution_time else None
            }
            for issue in self.issues if not issue.resolved
        ]
    
    async def stop(self):
        """Para o monitoramento"""
        self.is_running = False
        self.logger.info("🛑 Monitoramento autônomo parado")


# Função para iniciar o monitor autônomo
async def start_autonomous_monitor(config: Optional[Dict[str, Any]] = None):
    """Inicia o monitor autônomo"""
    monitor = AutonomousMonitorAgent(config)
    await monitor.start_monitoring()
    return monitor


if __name__ == "__main__":
    # Teste standalone
    async def test_monitor():
        monitor = AutonomousMonitorAgent()
        await monitor.start_monitoring()
    
    asyncio.run(test_monitor()) 