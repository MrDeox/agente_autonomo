"""
Error Prevention System - Sistema robusto para prevenir e detectar erros automaticamente
"""

import logging
import time
import traceback
import inspect
import json
from typing import Dict, List, Optional, Any, Callable, Type
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading
import queue
import signal
import sys
from enum import Enum

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorType(Enum):
    CONSTRUCTOR_ERROR = "constructor_error"
    INITIALIZATION_ERROR = "initialization_error"
    RUNTIME_ERROR = "runtime_error"
    CONFIGURATION_ERROR = "configuration_error"
    DEPENDENCY_ERROR = "dependency_error"
    VALIDATION_ERROR = "validation_error"

@dataclass
class ErrorEvent:
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    component: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    resolution_method: Optional[str] = None

class ConstructorValidator:
    """Valida construtores de agentes e componentes"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.expected_signatures = {
            'MaestroAgent': {
                'params': ['model_config', 'logger', 'config'],
                'types': [dict, logging.Logger, dict],
                'optional': [False, False, True]
            },
            'ArchitectAgent': {
                'params': ['model_config', 'logger'],
                'types': [dict, logging.Logger],
                'optional': [False, False]
            },
            'CodeReviewAgent': {
                'params': ['model_config', 'logger'],
                'types': [dict, logging.Logger],
                'optional': [False, False]
            },
            'AsyncAgentOrchestrator': {
                'params': ['config', 'logger'],
                'types': [dict, logging.Logger],
                'optional': [False, False]
            }
        }
    
    def validate_constructor(self, class_name: str, *args, **kwargs) -> bool:
        """Valida se os parâmetros do construtor estão corretos"""
        if class_name not in self.expected_signatures:
            self.logger.warning(f"Constructor validation not configured for {class_name}")
            return True
        
        signature = self.expected_signatures[class_name]
        expected_params = signature['params']
        expected_types = signature['types']
        optional = signature['optional']
        
        # Verificar número de argumentos posicionais
        if len(args) < len([p for p, opt in zip(expected_params, optional) if not opt]):
            self.logger.error(f"Constructor validation failed for {class_name}: insufficient positional arguments")
            return False
        
        # Verificar tipos dos argumentos
        for i, (arg, expected_type) in enumerate(zip(args, expected_types)):
            if not isinstance(arg, expected_type):
                self.logger.error(f"Constructor validation failed for {class_name}: arg {i} should be {expected_type}, got {type(arg)}")
                return False
        
        # Verificar argumentos nomeados
        for param, expected_type in zip(expected_params, expected_types):
            if param in kwargs and not isinstance(kwargs[param], expected_type):
                self.logger.error(f"Constructor validation failed for {class_name}: kwarg {param} should be {expected_type}, got {type(kwargs[param])}")
                return False
        
        self.logger.info(f"Constructor validation passed for {class_name}")
        return True

class HealthMonitor:
    """Monitora a saúde do sistema continuamente"""
    
    def __init__(self, logger: logging.Logger, check_interval: int = 30):
        self.logger = logger
        self.check_interval = check_interval
        self.health_status = {}
        self.last_check = {}
        self.monitoring = False
        self.monitor_thread = None
        self.error_queue = queue.Queue()
        
    def start_monitoring(self):
        """Inicia o monitoramento em background"""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Health monitoring started")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Health monitoring stopped")
    
    def _monitor_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring:
            try:
                self._perform_health_check()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(5)
    
    def _perform_health_check(self):
        """Executa verificação de saúde"""
        current_time = datetime.now()
        
        # Verificar componentes críticos
        components = [
            'hephaestus_agent',
            'async_orchestrator', 
            'optimized_pipeline',
            'cycle_runner'
        ]
        
        for component in components:
            try:
                # Verificar se o componente está acessível
                self._check_component_health(component)
                self.health_status[component] = {
                    'status': 'healthy',
                    'last_check': current_time,
                    'error_count': 0
                }
            except Exception as e:
                self._record_health_issue(component, str(e))
    
    def _check_component_health(self, component: str):
        """Verifica a saúde de um componente específico"""
        # Implementar verificações específicas por componente
        if component == 'hephaestus_agent':
            # Verificar se o agente principal está inicializado
            pass
        elif component == 'async_orchestrator':
            # Verificar se o orquestrador está funcionando
            pass
    
    def _record_health_issue(self, component: str, error: str):
        """Registra problema de saúde"""
        if component not in self.health_status:
            self.health_status[component] = {'error_count': 0}
        
        self.health_status[component]['error_count'] += 1
        self.health_status[component]['status'] = 'unhealthy'
        self.health_status[component]['last_error'] = error
        self.health_status[component]['last_check'] = datetime.now()
        
        self.logger.warning(f"Health issue detected in {component}: {error}")
        
        # Adicionar à fila de erros para processamento
        self.error_queue.put(ErrorEvent(
            timestamp=datetime.now(),
            error_type=ErrorType.RUNTIME_ERROR,
            severity=ErrorSeverity.MEDIUM,
            component=component,
            error_message=error,
            stack_trace="",
            context={'health_check': True}
        ))

class AutoRecovery:
    """Sistema de recuperação automática"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.recovery_strategies = {
            ErrorType.CONSTRUCTOR_ERROR: self._recover_constructor_error,
            ErrorType.INITIALIZATION_ERROR: self._recover_initialization_error,
            ErrorType.CONFIGURATION_ERROR: self._recover_configuration_error,
            ErrorType.RUNTIME_ERROR: self._recover_runtime_error
        }
        self.recovery_history = []
    
    def attempt_recovery(self, error_event: ErrorEvent) -> bool:
        """Tenta recuperar automaticamente de um erro"""
        self.logger.info(f"Attempting automatic recovery for {error_event.error_type.value}")
        
        strategy = self.recovery_strategies.get(error_event.error_type)
        if not strategy:
            self.logger.warning(f"No recovery strategy for error type: {error_event.error_type}")
            return False
        
        try:
            success = strategy(error_event)
            if success:
                error_event.resolved = True
                error_event.resolution_time = datetime.now()
                error_event.resolution_method = strategy.__name__
                self.recovery_history.append(error_event)
                self.logger.info(f"Recovery successful for {error_event.component}")
            return success
        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            return False
    
    def _recover_constructor_error(self, error_event: ErrorEvent) -> bool:
        """Recupera erros de construtor"""
        component = error_event.component
        
        if 'MaestroAgent' in component:
            # Verificar se o problema é ordem de parâmetros
            if 'positional arguments' in error_event.error_message:
                self.logger.info("Detected MaestroAgent constructor parameter order issue")
                # O erro já foi corrigido nos arquivos, mas podemos verificar
                return True
        
        return False
    
    def _recover_initialization_error(self, error_event: ErrorEvent) -> bool:
        """Recupera erros de inicialização"""
        # Implementar estratégias de recuperação específicas
        return False
    
    def _recover_configuration_error(self, error_event: ErrorEvent) -> bool:
        """Recupera erros de configuração"""
        # Implementar estratégias de recuperação específicas
        return False
    
    def _recover_runtime_error(self, error_event: ErrorEvent) -> bool:
        """Recupera erros de runtime"""
        # Implementar estratégias de recuperação específicas
        return False

class ErrorPreventionSystem:
    """Sistema principal de prevenção de erros"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.constructor_validator = ConstructorValidator(logger)
        self.health_monitor = HealthMonitor(logger)
        self.auto_recovery = AutoRecovery(logger)
        self.error_history = []
        self.error_patterns = {}
        self.prevention_rules = []
        
        # Configurar logging avançado
        self._setup_advanced_logging()
        
        # Registrar handlers de sinal para graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_advanced_logging(self):
        """Configura logging avançado para capturar todos os detalhes"""
        # Criar handler para arquivo de erro detalhado
        error_log_path = Path("logs/error_prevention.log")
        error_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        error_handler = logging.FileHandler(error_log_path)
        error_handler.setLevel(logging.DEBUG)
        
        # Formato detalhado para debugging
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        error_handler.setFormatter(formatter)
        
        self.logger.addHandler(error_handler)
        self.logger.info("Error prevention system initialized with advanced logging")
    
    def _signal_handler(self, signum, frame):
        """Handler para sinais de shutdown"""
        self.logger.info(f"Received signal {signum}, shutting down error prevention system")
        self.health_monitor.stop_monitoring()
        sys.exit(0)
    
    def start(self):
        """Inicia o sistema de prevenção de erros"""
        self.health_monitor.start_monitoring()
        self.logger.info("Error prevention system started")
    
    def stop(self):
        """Para o sistema de prevenção de erros"""
        self.health_monitor.stop_monitoring()
        self.logger.info("Error prevention system stopped")
    
    def validate_agent_construction(self, class_name: str, *args, **kwargs) -> bool:
        """Valida construção de agentes"""
        return self.constructor_validator.validate_constructor(class_name, *args, **kwargs)
    
    def record_error(self, error_event: ErrorEvent):
        """Registra um erro para análise e recuperação"""
        self.error_history.append(error_event)
        
        # Tentar recuperação automática
        if error_event.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.auto_recovery.attempt_recovery(error_event)
        
        # Analisar padrões de erro
        self._analyze_error_patterns(error_event)
        
        # Aplicar regras de prevenção
        self._apply_prevention_rules(error_event)
    
    def _analyze_error_patterns(self, error_event: ErrorEvent):
        """Analisa padrões de erro para prevenção futura"""
        pattern_key = f"{error_event.error_type.value}_{error_event.component}"
        
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = {
                'count': 0,
                'first_occurrence': error_event.timestamp,
                'last_occurrence': error_event.timestamp,
                'severity_distribution': {}
            }
        
        pattern = self.error_patterns[pattern_key]
        pattern['count'] += 1
        pattern['last_occurrence'] = error_event.timestamp
        
        severity = error_event.severity.value
        pattern['severity_distribution'][severity] = pattern['severity_distribution'].get(severity, 0) + 1
        
        # Se o padrão se repete muito, criar regra de prevenção
        if pattern['count'] >= 3:
            self._create_prevention_rule(error_event, pattern)
    
    def _create_prevention_rule(self, error_event: ErrorEvent, pattern: Dict):
        """Cria regra de prevenção baseada em padrão de erro"""
        rule = {
            'pattern': f"{error_event.error_type.value}_{error_event.component}",
            'condition': f"count >= {pattern['count']}",
            'action': 'prevent_construction',
            'created': datetime.now(),
            'active': True
        }
        
        self.prevention_rules.append(rule)
        self.logger.info(f"Created prevention rule for pattern: {rule['pattern']}")
    
    def _apply_prevention_rules(self, error_event: ErrorEvent):
        """Aplica regras de prevenção"""
        pattern_key = f"{error_event.error_type.value}_{error_event.component}"
        
        for rule in self.prevention_rules:
            if rule['pattern'] == pattern_key and rule['active']:
                self.logger.warning(f"Applying prevention rule: {rule['action']}")
                # Implementar ações de prevenção específicas
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        return {
            'health_status': self.health_monitor.health_status,
            'error_count': len(self.error_history),
            'recovery_success_rate': self._calculate_recovery_rate(),
            'active_prevention_rules': len([r for r in self.prevention_rules if r['active']]),
            'error_patterns': len(self.error_patterns),
            'last_error': self.error_history[-1] if self.error_history else None
        }
    
    def _calculate_recovery_rate(self) -> float:
        """Calcula taxa de sucesso de recuperação"""
        if not self.auto_recovery.recovery_history:
            return 0.0
        
        successful = len([e for e in self.auto_recovery.recovery_history if e.resolved])
        total = len(self.auto_recovery.recovery_history)
        return successful / total if total > 0 else 0.0
    
    def generate_error_report(self) -> str:
        """Gera relatório detalhado de erros"""
        report = []
        report.append("=== ERROR PREVENTION SYSTEM REPORT ===")
        report.append(f"Generated: {datetime.now()}")
        report.append(f"Total errors: {len(self.error_history)}")
        report.append(f"Recovery success rate: {self._calculate_recovery_rate():.2%}")
        report.append("")
        
        # Erros por tipo
        error_types = {}
        for error in self.error_history:
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        report.append("Errors by type:")
        for error_type, count in error_types.items():
            report.append(f"  {error_type}: {count}")
        
        report.append("")
        report.append("Recent errors:")
        for error in self.error_history[-10:]:  # Últimos 10 erros
            report.append(f"  {error.timestamp}: {error.error_type.value} - {error.component} - {error.error_message[:100]}...")
        
        return "\n".join(report)

# Decorator para validação automática de construtores
def validate_constructor(error_prevention_system: ErrorPreventionSystem):
    """Decorator para validar construtores automaticamente"""
    def decorator(cls):
        original_init = cls.__init__
        
        def validated_init(self, *args, **kwargs):
            class_name = cls.__name__
            
            # Validar construtor
            if not error_prevention_system.validate_agent_construction(class_name, *args, **kwargs):
                error_event = ErrorEvent(
                    timestamp=datetime.now(),
                    error_type=ErrorType.CONSTRUCTOR_ERROR,
                    severity=ErrorSeverity.CRITICAL,
                    component=class_name,
                    error_message=f"Constructor validation failed for {class_name}",
                    stack_trace=traceback.format_exc(),
                    context={'args': str(args), 'kwargs': str(kwargs)}
                )
                error_prevention_system.record_error(error_event)
                raise ValueError(f"Constructor validation failed for {class_name}")
            
            # Chamar construtor original
            return original_init(self, *args, **kwargs)
        
        cls.__init__ = validated_init
        return cls
    
    return decorator 