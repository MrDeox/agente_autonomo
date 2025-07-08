"""
🐛 Bug Hunter Agent - Detecta e corrige bugs em paralelo
"""

import asyncio
import logging
import time
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor

from agent.utils.llm_client import call_llm_api, call_llm_api_async
from agent.utils.json_parser import parse_json_response


@dataclass
class BugReport:
    """Relatório de bug detectado"""
    bug_id: str
    file_path: str
    line_number: Optional[int]
    bug_type: str
    severity: str  # low, medium, high, critical
    description: str
    suggested_fix: str
    confidence: float  # 0.0 to 1.0
    detected_at: datetime
    status: str = "detected"  # detected, fixing, fixed, failed


@dataclass
class BugFix:
    """Correção de bug proposta"""
    bug_id: str
    file_path: str
    original_code: str
    fixed_code: str
    explanation: str
    test_commands: List[str]
    rollback_plan: str


class BugHunterAgent:
    """
    Agente especializado em detectar e corrigir bugs automaticamente.
    Opera em paralelo com outros agentes para máxima eficiência.
    """
    
    def __init__(self, model_config: Dict[str, str], config: Dict[str, Any], logger: logging.Logger):
        self.model_config = model_config
        self.config = config
        self.logger = logger.getChild("BugHunterAgent")
        
        # Estado do agente
        self.active_bugs: Dict[str, BugReport] = {}
        self.fixed_bugs: Dict[str, BugReport] = {}
        self.bug_patterns: Dict[str, Dict[str, Any]] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Configurações
        self.scan_interval = config.get("bug_hunter", {}).get("scan_interval", 30)  # segundos
        self.max_concurrent_fixes = config.get("bug_hunter", {}).get("max_concurrent_fixes", 3)
        self.auto_fix_enabled = config.get("bug_hunter", {}).get("auto_fix_enabled", True)
        
        # Estatísticas
        self.stats = {
            "bugs_detected": 0,
            "bugs_fixed": 0,
            "fix_attempts": 0,
            "success_rate": 0.0,
            "last_scan": None,
            "scan_count": 0
        }
        
        # Inicializar padrões de bug conhecidos
        self._initialize_bug_patterns()
        
        self.logger.info("🐛 Bug Hunter Agent initialized")
    
    def _initialize_bug_patterns(self):
        """Inicializa padrões de bugs conhecidos"""
        self.bug_patterns = {
            "syntax_error": {
                "patterns": [
                    r"SyntaxError:",
                    r"IndentationError:",
                    r"NameError:",
                    r"TypeError:",
                    r"AttributeError:"
                ],
                "severity": "high",
                "auto_fixable": True
            },
            "import_error": {
                "patterns": [
                    r"ModuleNotFoundError:",
                    r"ImportError:",
                    r"No module named"
                ],
                "severity": "medium",
                "auto_fixable": True
            },
            "runtime_error": {
                "patterns": [
                    r"RuntimeError:",
                    r"ValueError:",
                    r"KeyError:",
                    r"IndexError:"
                ],
                "severity": "medium",
                "auto_fixable": False
            },
            "performance_issue": {
                "patterns": [
                    r"timeout",
                    r"memory leak",
                    r"infinite loop",
                    r"deadlock"
                ],
                "severity": "medium",
                "auto_fixable": False
            },
            "security_vulnerability": {
                "patterns": [
                    r"sql injection",
                    r"xss",
                    r"path traversal",
                    r"command injection"
                ],
                "severity": "critical",
                "auto_fixable": False
            }
        }
    
    def start_monitoring(self) -> bool:
        """Inicia monitoramento contínuo de bugs"""
        if self.monitoring_active:
            self.logger.warning("Bug monitoring is already active")
            return False
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        self.logger.info("🔍 Bug Hunter monitoring started!")
        return True
    
    def stop_monitoring(self) -> bool:
        """Para o monitoramento de bugs"""
        if not self.monitoring_active:
            return False
        
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        self.logger.info("🔍 Bug Hunter monitoring stopped")
        return True
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        self.logger.info("🔍 Starting bug monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Executar scan completo
                self.scan_for_bugs()
                
                # Aguardar próximo scan
                time.sleep(self.scan_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def scan_for_bugs(self) -> List[BugReport]:
        """Executa scan completo em busca de bugs"""
        self.logger.debug("🔍 Starting comprehensive bug scan...")
        
        bugs_found = []
        
        try:
            # 1. Scan de sintaxe Python
            syntax_bugs = self._scan_syntax_errors()
            bugs_found.extend(syntax_bugs)
            
            # 2. Scan de imports
            import_bugs = self._scan_import_errors()
            bugs_found.extend(import_bugs)
            
            # 3. Scan de logs por erros
            log_bugs = self._scan_log_errors()
            bugs_found.extend(log_bugs)
            
            # 4. Scan de testes falhando
            test_bugs = self._scan_test_failures()
            bugs_found.extend(test_bugs)
            
            # 5. Scan de performance
            perf_bugs = self._scan_performance_issues()
            bugs_found.extend(perf_bugs)
            
            # Atualizar estatísticas
            self.stats["bugs_detected"] += len(bugs_found)
            self.stats["scan_count"] += 1
            self.stats["last_scan"] = datetime.now()
            
            # Adicionar bugs ativos
            for bug in bugs_found:
                self.active_bugs[bug.bug_id] = bug
            
            self.logger.info(f"🔍 Bug scan complete: {len(bugs_found)} bugs found")
            
            # Iniciar correções automáticas se habilitado
            if self.auto_fix_enabled and bugs_found:
                asyncio.create_task(self._auto_fix_bugs(bugs_found))
            
            return bugs_found
            
        except Exception as e:
            self.logger.error(f"Error during bug scan: {e}")
            return []
    
    def _scan_syntax_errors(self) -> List[BugReport]:
        """Scan por erros de sintaxe Python"""
        bugs = []
        
        try:
            # Executar py_compile para verificar sintaxe
            result = subprocess.run(
                ["python", "-m", "py_compile", "."],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Parsear erros de sintaxe
                for line in result.stderr.split('\n'):
                    if 'SyntaxError' in line or 'IndentationError' in line:
                        match = re.search(r'File "([^"]+)", line (\d+)', line)
                        if match:
                            file_path = match.group(1)
                            line_num = int(match.group(2))
                            
                            bug = BugReport(
                                bug_id=f"syntax_{file_path}_{line_num}_{int(time.time())}",
                                file_path=file_path,
                                line_number=line_num,
                                bug_type="syntax_error",
                                severity="high",
                                description=f"Syntax error in {file_path}:{line_num}",
                                suggested_fix="Review and fix syntax",
                                confidence=0.9,
                                detected_at=datetime.now()
                            )
                            bugs.append(bug)
            
        except Exception as e:
            self.logger.debug(f"Error scanning syntax: {e}")
        
        return bugs
    
    def _scan_import_errors(self) -> List[BugReport]:
        """Scan por erros de import"""
        bugs = []
        
        try:
            # Tentar importar módulos principais
            main_modules = ["agent", "tools", "tests"]
            
            for module in main_modules:
                try:
                    result = subprocess.run(
                        ["python", "-c", f"import {module}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode != 0:
                        bug = BugReport(
                            bug_id=f"import_{module}_{int(time.time())}",
                            file_path=f"{module}/__init__.py",
                            line_number=None,
                            bug_type="import_error",
                            severity="medium",
                            description=f"Import error in module {module}",
                            suggested_fix=f"Check dependencies for {module}",
                            confidence=0.8,
                            detected_at=datetime.now()
                        )
                        bugs.append(bug)
                        
                except Exception as e:
                    self.logger.debug(f"Error checking import for {module}: {e}")
        
        except Exception as e:
            self.logger.debug(f"Error scanning imports: {e}")
        
        return bugs
    
    def _scan_log_errors(self) -> List[BugReport]:
        """Scan por erros nos logs"""
        bugs = []
        
        try:
            log_files = list(Path("logs").glob("*.log"))
            
            for log_file in log_files[:5]:  # Limitar a 5 arquivos
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-100:]  # Últimas 100 linhas
                        
                        for line in lines:
                            for bug_type, pattern_info in self.bug_patterns.items():
                                for pattern in pattern_info["patterns"]:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        bug = BugReport(
                                            bug_id=f"log_{bug_type}_{int(time.time())}",
                                            file_path=str(log_file),
                                            line_number=None,
                                            bug_type=bug_type,
                                            severity=pattern_info["severity"],
                                            description=f"Error detected in logs: {line.strip()}",
                                            suggested_fix="Investigate and fix root cause",
                                            confidence=0.7,
                                            detected_at=datetime.now()
                                        )
                                        bugs.append(bug)
                                        break
                        
                except Exception as e:
                    self.logger.debug(f"Error reading log file {log_file}: {e}")
        
        except Exception as e:
            self.logger.debug(f"Error scanning logs: {e}")
        
        return bugs
    
    def _scan_test_failures(self) -> List[BugReport]:
        """Scan por falhas de teste"""
        bugs = []
        
        try:
            # Executar testes rápidos
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                # Parsear falhas de teste
                for line in result.stdout.split('\n'):
                    if 'FAILED' in line or 'ERROR' in line:
                        match = re.search(r'([^:]+)::([^:]+)', line)
                        if match:
                            test_file = match.group(1)
                            test_name = match.group(2)
                            
                            bug = BugReport(
                                bug_id=f"test_{test_file}_{test_name}_{int(time.time())}",
                                file_path=test_file,
                                line_number=None,
                                bug_type="test_failure",
                                severity="medium",
                                description=f"Test failure: {test_name}",
                                suggested_fix="Fix failing test",
                                confidence=0.9,
                                detected_at=datetime.now()
                            )
                            bugs.append(bug)
        
        except Exception as e:
            self.logger.debug(f"Error scanning tests: {e}")
        
        return bugs
    
    def _scan_performance_issues(self) -> List[BugReport]:
        """Scan por problemas de performance"""
        bugs = []
        
        try:
            # Verificar uso de memória e CPU
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'python' in line and 'uvicorn' in line:
                        # Verificar se processo está usando muita memória
                        parts = line.split()
                        if len(parts) > 5:
                            try:
                                memory_percent = float(parts[3])
                                if memory_percent > 80:  # Mais de 80% de memória
                                    bug = BugReport(
                                        bug_id=f"perf_memory_{int(time.time())}",
                                        file_path="system",
                                        line_number=None,
                                        bug_type="performance_issue",
                                        severity="medium",
                                        description=f"High memory usage: {memory_percent}%",
                                        suggested_fix="Optimize memory usage",
                                        confidence=0.6,
                                        detected_at=datetime.now()
                                    )
                                    bugs.append(bug)
                            except ValueError:
                                pass
        
        except Exception as e:
            self.logger.debug(f"Error scanning performance: {e}")
        
        return bugs
    
    async def _auto_fix_bugs(self, bugs: List[BugReport]):
        """Corrige bugs automaticamente"""
        self.logger.info(f"🔧 Starting auto-fix for {len(bugs)} bugs")
        
        # Limitar correções concorrentes
        semaphore = asyncio.Semaphore(self.max_concurrent_fixes)
        
        async def fix_bug(bug: BugReport):
            async with semaphore:
                return await self._fix_single_bug(bug)
        
        # Executar correções em paralelo
        tasks = [fix_bug(bug) for bug in bugs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Processar resultados
        fixed_count = 0
        for result in results:
            if isinstance(result, bool) and result:
                fixed_count += 1
        
        self.stats["bugs_fixed"] += fixed_count
        self.stats["fix_attempts"] += len(bugs)
        self.stats["success_rate"] = self.stats["bugs_fixed"] / max(self.stats["fix_attempts"], 1)
        
        self.logger.info(f"🔧 Auto-fix complete: {fixed_count}/{len(bugs)} bugs fixed")
    
    async def _fix_single_bug(self, bug: BugReport) -> bool:
        """Corrige um bug específico"""
        try:
            self.logger.info(f"🔧 Fixing bug: {bug.bug_id}")
            
            # Marcar como em correção
            bug.status = "fixing"
            
            # Gerar correção usando LLM
            fix = await self._generate_bug_fix(bug)
            
            if fix:
                # Aplicar correção
                success = await self._apply_bug_fix(fix)
                
                if success:
                    bug.status = "fixed"
                    self.fixed_bugs[bug.bug_id] = bug
                    if bug.bug_id in self.active_bugs:
                        del self.active_bugs[bug.bug_id]
                    
                    self.logger.info(f"✅ Bug fixed: {bug.bug_id}")
                    return True
                else:
                    bug.status = "failed"
                    self.logger.warning(f"❌ Failed to apply fix for: {bug.bug_id}")
            else:
                bug.status = "failed"
                self.logger.warning(f"❌ Could not generate fix for: {bug.bug_id}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error fixing bug {bug.bug_id}: {e}")
            bug.status = "failed"
            return False
    
    async def _generate_bug_fix(self, bug: BugReport) -> Optional[BugFix]:
        """Gera uma correção para um bug usando LLM (versão assíncrona)"""
        try:
            file_content = ""
            if Path(bug.file_path).exists():
                with open(bug.file_path, 'r') as f:
                    file_content = f.read()

            prompt = f"""
You are a bug fixing expert. Analyze this bug and provide a fix:

BUG REPORT:
- Type: {bug.bug_type}
- File: {bug.file_path}
- Line: {bug.line_number}
- Description: {bug.description}
- Severity: {bug.severity}

FILE CONTENT:
{file_content}

Generate a JSON response with the fix:
{{
    "original_code": "the problematic code",
    "fixed_code": "the corrected code", 
    "explanation": "why this fix works",
    "test_commands": ["commands to test the fix"],
    "rollback_plan": "how to undo if needed"
}}
"""

            # Chamada assíncrona à LLM
            response, error = await call_llm_api_async(
                self.model_config,
                prompt,
                0.3,
                self.logger
            )

            if error:
                self.logger.warning(f"LLM error generating fix: {error}")
                return None

            # Parsear resposta JSON
            parsed, parse_error = parse_json_response(response or '', self.logger)

            if parse_error:
                self.logger.warning(f"JSON parse error: {parse_error}")
                return None

            if parsed and "fixed_code" in parsed:
                return BugFix(
                    bug_id=bug.bug_id,
                    file_path=bug.file_path,
                    original_code=parsed.get("original_code", ""),
                    fixed_code=parsed.get("fixed_code", ""),
                    explanation=parsed.get("explanation", ""),
                    test_commands=parsed.get("test_commands", []),
                    rollback_plan=parsed.get("rollback_plan", "")
                )

            return None

        except Exception as e:
            self.logger.error(f"Error generating bug fix: {e}")
            return None
    
    async def _apply_bug_fix(self, fix: BugFix) -> bool:
        """Aplica correção de bug"""
        try:
            if not Path(fix.file_path).exists():
                self.logger.warning(f"File not found: {fix.file_path}")
                return False
            
            # Fazer backup
            backup_path = f"{fix.file_path}.bug_hunter_backup"
            with open(fix.file_path, 'r') as f:
                content = f.read()
            
            with open(backup_path, 'w') as f:
                f.write(content)
            
            # Aplicar correção
            if fix.original_code and fix.fixed_code:
                new_content = content.replace(fix.original_code, fix.fixed_code)
            else:
                # Se não há código específico, adicionar no final
                new_content = content + "\n\n# Bug fix applied by BugHunterAgent\n" + fix.fixed_code
            
            with open(fix.file_path, 'w') as f:
                f.write(new_content)
            
            # Executar testes se disponíveis
            if fix.test_commands:
                for cmd in fix.test_commands:
                    try:
                        result = subprocess.run(
                            cmd.split(),
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode != 0:
                            self.logger.warning(f"Test failed after fix: {cmd}")
                            # Rollback
                            with open(fix.file_path, 'w') as f:
                                f.write(content)
                            return False
                    except Exception as e:
                        self.logger.warning(f"Error running test {cmd}: {e}")
            
            self.logger.info(f"✅ Bug fix applied: {fix.bug_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying bug fix: {e}")
            return False
    
    def get_bug_report(self) -> Dict[str, Any]:
        """Retorna relatório completo de bugs"""
        return {
            "active_bugs": len(self.active_bugs),
            "fixed_bugs": len(self.fixed_bugs),
            "total_bugs_detected": self.stats["bugs_detected"],
            "success_rate": f"{self.stats['success_rate']:.1%}",
            "last_scan": self.stats["last_scan"].isoformat() if self.stats["last_scan"] else None,
            "scan_count": self.stats["scan_count"],
            "monitoring_active": self.monitoring_active,
            "auto_fix_enabled": self.auto_fix_enabled,
            "recent_bugs": [
                {
                    "id": bug.bug_id,
                    "type": bug.bug_type,
                    "severity": bug.severity,
                    "status": bug.status,
                    "file": bug.file_path,
                    "description": bug.description
                }
                for bug in list(self.active_bugs.values())[-10:]  # Últimos 10 bugs
            ]
        }
    
    def get_priority_bugs(self) -> List[BugReport]:
        """Retorna bugs de alta prioridade"""
        priority_bugs = []
        
        for bug in self.active_bugs.values():
            if bug.severity in ["high", "critical"]:
                priority_bugs.append(bug)
        
        # Ordenar por severidade e confiança
        priority_bugs.sort(key=lambda b: (b.severity == "critical", b.confidence), reverse=True)
        
        return priority_bugs
    
    def hunt_bugs(self, project_path: str = "", code_to_analyze: str = "") -> Dict[str, Any]:
        """
        Método principal chamado pelo orquestrador assíncrono.
        Executa caça de bugs e retorna relatório.
        """
        try:
            self.logger.info("🐛 Bug Hunter starting hunt...")
            
            # Executar scan completo
            bugs_found = self.scan_for_bugs()
            
            # Iniciar correções automáticas se habilitado
            if self.auto_fix_enabled and bugs_found:
                # Executar correções em thread separada para não bloquear
                threading.Thread(
                    target=self._run_auto_fix_async,
                    args=(bugs_found,),
                    daemon=True
                ).start()
            
            # Retornar relatório
            report = self.get_bug_report()
            report["hunt_completed"] = True
            report["bugs_found_this_hunt"] = len(bugs_found)
            
            self.logger.info(f"🐛 Bug hunt complete: {len(bugs_found)} bugs found")
            return report
            
        except Exception as e:
            self.logger.error(f"Error in bug hunt: {e}")
            return {
                "hunt_completed": False,
                "error": str(e),
                "bugs_found_this_hunt": 0
            }
    
    def _run_auto_fix_async(self, bugs: List[BugReport]):
        """Executa correções automáticas em thread separada"""
        try:
            # Criar loop de eventos para async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Executar correções
            loop.run_until_complete(self._auto_fix_bugs(bugs))
            
        except Exception as e:
            self.logger.error(f"Error in async auto-fix: {e}")
        finally:
            loop.close() 