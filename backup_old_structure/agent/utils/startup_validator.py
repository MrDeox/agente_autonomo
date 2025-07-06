"""
Startup Validator - Sistema de validação de startup para garantir que tudo funcione corretamente
"""

import logging
import time
import traceback
import importlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import inspect
import os

@dataclass
class ValidationResult:
    component: str
    status: bool
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0

class StartupValidator:
    """Valida todos os componentes críticos antes do startup"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.validation_results = []
        self.critical_components = [
            'MaestroAgent',
            'ArchitectAgent', 
            'CodeReviewAgent',
            'AsyncAgentOrchestrator',
            'OptimizedPipeline'
        ]
    
    def validate_all(self, config: Dict[str, Any]) -> bool:
        """Executa todas as validações críticas"""
        self.logger.info("🔍 Iniciando validação completa do sistema...")
        
        start_time = time.time()
        
        # Validações em ordem de dependência
        validations = [
            self._validate_config,
            self._validate_imports,
            self._validate_agent_constructors,
            self._validate_dependencies,
            self._validate_file_permissions,
            self._validate_network_connectivity
        ]
        
        all_passed = True
        
        for validation in validations:
            try:
                result = validation(config)
                self.validation_results.append(result)
                
                if not result.status:
                    all_passed = False
                    self.logger.error(f"❌ Validação falhou: {result.component} - {result.error_message}")
                else:
                    self.logger.info(f"✅ {result.component}: OK ({result.execution_time:.2f}s)")
                    
            except Exception as e:
                error_result = ValidationResult(
                    component=validation.__name__,
                    status=False,
                    error_message=str(e),
                    execution_time=0.0
                )
                self.validation_results.append(error_result)
                all_passed = False
                self.logger.error(f"❌ Erro na validação {validation.__name__}: {e}")
        
        total_time = time.time() - start_time
        
        if all_passed:
            self.logger.info(f"🎉 Todas as validações passaram! Tempo total: {total_time:.2f}s")
        else:
            self.logger.error(f"💥 Validações falharam! Tempo total: {total_time:.2f}s")
            self._generate_failure_report()
        
        return all_passed
    
    def _validate_config(self, config: Dict[str, Any]) -> ValidationResult:
        """Valida configuração básica"""
        start_time = time.time()
        
        required_keys = [
            'models',
            'validation_strategies',
            'memory_file_path'
        ]
        
        missing_keys = []
        for key in required_keys:
            if key not in config:
                missing_keys.append(key)
        
        if missing_keys:
            return ValidationResult(
                component="Config Validation",
                status=False,
                error_message=f"Missing required config keys: {missing_keys}",
                execution_time=time.time() - start_time
            )
        
        # Validar modelos
        models = config.get('models', {})
        required_models = ['architect_default', 'maestro_default']
        
        missing_models = []
        for model in required_models:
            if model not in models:
                missing_models.append(model)
        
        if missing_models:
            return ValidationResult(
                component="Config Validation",
                status=False,
                error_message=f"Missing required models: {missing_models}",
                execution_time=time.time() - start_time
            )
        
        return ValidationResult(
            component="Config Validation",
            status=True,
            execution_time=time.time() - start_time
        )
    
    def _validate_imports(self, config: Dict[str, Any]) -> ValidationResult:
        """Valida se todos os imports necessários funcionam"""
        start_time = time.time()
        
        required_modules = [
            'agent.agents.maestro_agent',
            'agent.agents.architect_agent',
            'agent.agents.code_review_agent',
            'agent.async_orchestrator',
            'agent.optimized_pipeline',
            'agent.utils.llm_client',
            'agent.patch_applicator'
        ]
        
        failed_imports = []
        
        for module_name in required_modules:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                failed_imports.append(f"{module_name}: {e}")
        
        if failed_imports:
            return ValidationResult(
                component="Import Validation",
                status=False,
                error_message=f"Failed imports: {failed_imports}",
                execution_time=time.time() - start_time
            )
        
        return ValidationResult(
            component="Import Validation",
            status=True,
            execution_time=time.time() - start_time
        )
    
    def _validate_agent_constructors(self, config: Dict[str, Any]) -> ValidationResult:
        """Valida se os construtores dos agentes funcionam corretamente"""
        start_time = time.time()
        
        try:
            from agent.agents.maestro_agent import MaestroAgent
            from agent.agents.architect_agent import ArchitectAgent
            from agent.agents.code_review_agent import CodeReviewAgent
            
            # Testar construtor do MaestroAgent
            test_logger = logging.getLogger("test")
            test_config = config.copy()
            
            maestro = MaestroAgent(
                model_config=config.get("models", {}).get("maestro_default", "gpt-4"),
                logger=test_logger,
                config=test_config
            )
            
            architect = ArchitectAgent(
                model_config=config.get("models", {}).get("architect_default", "gpt-4"),
                logger=test_logger
            )
            
            code_reviewer = CodeReviewAgent(
                model_config=config.get("models", {}).get("code_review_default", "gpt-4"),
                logger=test_logger
            )
            
            return ValidationResult(
                component="Agent Constructor Validation",
                status=True,
                details={
                    "maestro_created": True,
                    "architect_created": True,
                    "code_reviewer_created": True
                },
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                component="Agent Constructor Validation",
                status=False,
                error_message=f"Constructor validation failed: {str(e)}",
                details={"traceback": traceback.format_exc()},
                execution_time=time.time() - start_time
            )
    
    def _validate_dependencies(self, config: Dict[str, Any]) -> ValidationResult:
        """Valida dependências do sistema"""
        start_time = time.time()
        
        # Verificar se diretórios necessários existem
        required_dirs = [
            "logs",
            "reports",
            "config"
        ]
        
        missing_dirs = []
        for dir_name in required_dirs:
            if not Path(dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return ValidationResult(
                component="Dependency Validation",
                status=False,
                error_message=f"Missing required directories: {missing_dirs}",
                execution_time=time.time() - start_time
            )
        
        # Verificar se arquivos de configuração existem
        config_files = [
            "config/base_config.yaml",
            "config/default.yaml"
        ]
        
        missing_files = []
        for file_path in config_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return ValidationResult(
                component="Dependency Validation",
                status=False,
                error_message=f"Missing required files: {missing_files}",
                execution_time=time.time() - start_time
            )
        
        return ValidationResult(
            component="Dependency Validation",
            status=True,
            execution_time=time.time() - start_time
        )
    
    def _validate_file_permissions(self, config: Dict[str, Any]) -> ValidationResult:
        """Valida permissões de arquivo"""
        start_time = time.time()
        
        # Verificar se podemos escrever nos diretórios necessários
        writable_dirs = [
            "logs",
            "reports"
        ]
        
        unwritable_dirs = []
        for dir_name in writable_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception:
                    unwritable_dirs.append(dir_name)
            elif not os.access(dir_path, os.W_OK):
                unwritable_dirs.append(dir_name)
        
        if unwritable_dirs:
            return ValidationResult(
                component="File Permission Validation",
                status=False,
                error_message=f"Cannot write to directories: {unwritable_dirs}",
                execution_time=time.time() - start_time
            )
        
        return ValidationResult(
            component="File Permission Validation",
            status=True,
            execution_time=time.time() - start_time
        )
    
    def _validate_network_connectivity(self, config: Dict[str, Any]) -> ValidationResult:
        """Valida conectividade de rede básica"""
        start_time = time.time()
        
        try:
            import socket
            import urllib.request
            
            # Testar conectividade básica
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            
            # Testar acesso a um serviço externo
            urllib.request.urlopen("https://httpbin.org/get", timeout=10)
            
            return ValidationResult(
                component="Network Connectivity Validation",
                status=True,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            return ValidationResult(
                component="Network Connectivity Validation",
                status=False,
                error_message=f"Network connectivity failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _generate_failure_report(self):
        """Gera relatório detalhado de falhas"""
        failed_validations = [r for r in self.validation_results if not r.status]
        
        report = []
        report.append("=" * 60)
        report.append("STARTUP VALIDATION FAILURE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now()}")
        report.append(f"Total validations: {len(self.validation_results)}")
        report.append(f"Failed validations: {len(failed_validations)}")
        report.append("")
        
        for result in failed_validations:
            report.append(f"❌ {result.component}")
            report.append(f"   Error: {result.error_message}")
            if result.details:
                report.append(f"   Details: {result.details}")
            report.append("")
        
        report.append("RECOMMENDED ACTIONS:")
        report.append("1. Check configuration files")
        report.append("2. Verify all dependencies are installed")
        report.append("3. Ensure proper file permissions")
        report.append("4. Check network connectivity")
        report.append("5. Review error logs for details")
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        
        # Salvar relatório
        report_path = Path("logs/startup_validation_failure.txt")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        self.logger.error(f"Startup validation failure report saved to: {report_path}")
        self.logger.error(report_text)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna resumo das validações"""
        total = len(self.validation_results)
        passed = len([r for r in self.validation_results if r.status])
        failed = total - passed
        
        return {
            'total_validations': total,
            'passed_validations': passed,
            'failed_validations': failed,
            'success_rate': passed / total if total > 0 else 0.0,
            'failed_components': [r.component for r in self.validation_results if not r.status],
            'execution_time': sum(r.execution_time for r in self.validation_results)
        }

# Decorator para validar startup automaticamente
def validate_startup(config: Dict[str, Any]):
    """Decorator para validar startup antes de executar uma função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("startup_validator")
            validator = StartupValidator(logger)
            
            if not validator.validate_all(config):
                raise RuntimeError("Startup validation failed. Check logs for details.")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator 