# Plano de Modularização e Refatoração Arquitetural

## 🎯 **Visão Geral**

Este plano combina **consolidação + modularização + desacoplamento** para transformar o Hephaestus em um sistema mais limpo, modular e reutilizável.

## 📊 **Análise de Dependências**

### **Padrões Identificados**

#### 1. **Inicialização de Agentes (Repetida 15+ vezes)**
```python
# Padrão atual em cada agent:
def __init__(self, model_config: Dict[str, str], logger: logging.Logger):
    self.model_config = model_config
    self.logger = logger
```

#### 2. **Chamadas LLM (Repetidas 25+ vezes)**
```python
# Padrão atual espalhado:
response, error = call_llm_api(
    model_config=self.model_config,
    prompt=prompt,
    temperature=0.4,
    logger=self.logger
)
if error:
    self.logger.error(f"Error: {error}")
    return None, error
```

#### 3. **JSON Parsing (Inconsistente)**
```python
# Alguns usam json_parser.py, outros fazem direto
# Necessário padronizar
```

#### 4. **Logging Setup (65+ arquivos)**
```python
# Padrão repetido:
import logging
self.logger = logger  # ou logging.getLogger(__name__)
```

## 🚀 **Plano de Modularização**

### **FASE 1: Shared Utilities (Base Foundation)**

#### 1.1 Criar Agent Factory & Base Mixins
```python
# src/hephaestus/utils/agent_factory.py
class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, **kwargs) -> BaseAgent:
        # Centralizar criação com dependency injection
        
    @staticmethod
    def inject_dependencies(agent: BaseAgent, config: Dict, logger: logging.Logger):
        # Injeção padronizada de dependências

# src/hephaestus/agents/mixins.py
class ConfigMixin:
    def get_agent_config(self) -> Dict[str, Any]:
        return ConfigManager.get_agent_config(self.__class__.__name__)

class LoggerMixin:
    def setup_logger(self, name: str, parent_logger=None):
        self.logger = LoggerFactory.get_component_logger(name, parent_logger)

class MetricsMixin:
    def record_metric(self, metric_name: str, value: Any, tags: Dict = None):
        MetricsCollector.record(self.__class__.__name__, metric_name, value, tags)

class CacheMixin:
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        return CacheManager.get(f"{self.__class__.__name__}:{cache_key}")
```

#### 1.2 LLM Call Manager (Shared Utils)
```python
# src/hephaestus/utils/llm_manager.py
class LLMCallManager:
    def __init__(self, model_config: Dict, logger: logging.Logger):
        self.model_config = model_config
        self.logger = logger
        self.metrics = MetricsCollector()
    
    async def safe_call_with_retry(self, 
                                 prompt: str, 
                                 temperature: float = 0.4,
                                 max_retries: int = 3,
                                 fallback_models: List[str] = None) -> Tuple[Optional[str], Optional[str]]:
        # Retry logic + metrics + error handling padronizados
        
    def call_with_json_response(self, prompt: str, **kwargs) -> Tuple[Optional[Dict], Optional[str]]:
        # JSON parsing integrado
        
    @contextmanager
    def call_context(self, operation_name: str):
        # Context manager para métricas automáticas

# Decorators para simplificar uso:
@llm_call_with_metrics
@llm_call_with_retry(max_retries=3)
def agent_method(self, prompt: str):
    # Automatically handles LLM calls with metrics and retry
```

#### 1.3 Configuration Manager (Desacoplamento)
```python
# src/hephaestus/utils/config_manager.py
class ConfigManager:
    _instance = None
    _config_cache = {}
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Dict[str, Any]:
        # Agent-specific config access with caching
        
    @classmethod
    def get_model_config(cls, model_type: str) -> Dict[str, Any]:
        # Model config with fallbacks
        
    @classmethod
    def get_service_config(cls, service_name: str) -> Dict[str, Any]:
        # Service configuration
        
    @classmethod
    def reload_config(cls):
        # Hot reload support

# Usage:
config = ConfigManager.get_agent_config("ArchitectAgent")
```

#### 1.4 Logger Factory (Padronização)
```python
# src/hephaestus/utils/logger_factory.py
class LoggerFactory:
    @staticmethod
    def get_component_logger(component_name: str, 
                           parent_logger: Optional[logging.Logger] = None) -> logging.Logger:
        # Padronizar criação de loggers com formatting consistente
        
    @staticmethod
    def setup_file_handler(logger: logging.Logger, 
                          log_file: str, 
                          level: int = logging.INFO):
        # File handler padrão
        
    @staticmethod
    def get_agent_logger(agent_name: str) -> logging.Logger:
        # Logger específico para agents com prefixo padrão
```

### **FASE 2: Service Layer (Dependency Injection)**

#### 2.1 Service Locator Pattern
```python
# src/hephaestus/services/service_locator.py
class ServiceLocator:
    _services = {}
    
    @classmethod
    def register_service(cls, interface: Type, implementation: Any):
        cls._services[interface] = implementation
    
    @classmethod
    def get_service(cls, interface: Type) -> Any:
        return cls._services.get(interface)
    
    @classmethod
    def inject_dependencies(cls, instance: Any):
        # Auto-inject based on type hints

# Usage in agents:
class ArchitectAgent(BaseAgent, ConfigMixin, LoggerMixin):
    def __init__(self):
        self.llm_manager: LLMCallManager = ServiceLocator.get_service(LLMCallManager)
        self.memory: Memory = ServiceLocator.get_service(Memory)
```

#### 2.2 Enhanced Interfaces
```python
# src/hephaestus/services/interfaces.py
from abc import ABC, abstractmethod
from typing import Protocol

class AgentInterface(Protocol):
    def execute(self, objective: str) -> Tuple[bool, Optional[str]]:
        ...
    
    def get_capabilities(self) -> List[str]:
        ...
    
    def get_metrics(self) -> Dict[str, Any]:
        ...

class ServiceInterface(ABC):
    @abstractmethod
    async def initialize(self) -> bool:
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthStatus:
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        pass

class CacheInterface(Protocol):
    def get(self, key: str) -> Optional[Any]:
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        ...
```

#### 2.3 Metrics & Observability
```python
# src/hephaestus/utils/metrics_collector.py
class MetricsCollector:
    def __init__(self):
        self.metrics_store = defaultdict(list)
    
    def record_agent_performance(self, 
                               agent_name: str,
                               operation: str, 
                               duration: float,
                               success: bool,
                               metadata: Dict = None):
        # Métricas padronizadas para todos os agents
        
    def record_llm_call(self,
                       model: str,
                       prompt_tokens: int,
                       completion_tokens: int,
                       duration: float,
                       success: bool):
        # Métricas específicas para LLM calls
        
    def get_agent_dashboard(self, agent_name: str) -> Dict[str, Any]:
        # Dashboard de métricas por agent
        
    def export_metrics(self, format: str = "json") -> str:
        # Export para monitoring systems
```

### **FASE 3: Refatoração de Agents (Modular Architecture)**

#### 3.1 Enhanced Base Agent
```python
# src/hephaestus/agents/enhanced_base.py
class EnhancedBaseAgent(BaseAgent, ConfigMixin, LoggerMixin, MetricsMixin, CacheMixin):
    def __init__(self, agent_name: str):
        super().__init__(agent_name)
        
        # Dependency injection automática
        ServiceLocator.inject_dependencies(self)
        
        # Setup automático de logger
        self.setup_logger(agent_name)
        
        # Config automático
        self.config = self.get_agent_config()
        
    @property
    def llm_manager(self) -> LLMCallManager:
        return ServiceLocator.get_service(LLMCallManager)
    
    @llm_call_with_metrics
    async def llm_call(self, prompt: str, **kwargs) -> Tuple[Optional[str], Optional[str]]:
        return await self.llm_manager.safe_call_with_retry(prompt, **kwargs)
    
    @llm_call_with_metrics  
    async def llm_call_json(self, prompt: str, **kwargs) -> Tuple[Optional[Dict], Optional[str]]:
        return await self.llm_manager.call_with_json_response(prompt, **kwargs)
```

#### 3.2 Refatorar Agents Existentes
```python
# src/hephaestus/agents/architect.py (REFATORADO)
class ArchitectAgent(EnhancedBaseAgent):
    def __init__(self):
        super().__init__("ArchitectAgent")
    
    async def plan_action(self, objective: str, manifest: str, file_content_context: str = "") -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        prompt = self._build_plan_prompt(objective, manifest, file_content_context)
        
        # LLM call simplificado com métricas automáticas
        return await self.llm_call_json(prompt, temperature=0.4)
    
    def _build_plan_prompt(self, objective: str, manifest: str, context: str) -> str:
        # Separar lógica de prompt building
        return self.prompt_builder.build_architect_prompt(objective, manifest, context)

# Similar para MaestroAgent, BugHunterAgent, etc.
```

### **FASE 4: Consolidação com Modularização**

#### 4.1 Unified Monitoring System
```python
# src/hephaestus/services/monitoring/unified_monitor.py
class UnifiedMonitoringSystem(ServiceInterface):
    def __init__(self):
        self.cycle_monitor = CycleMonitor()
        self.autonomous_monitor = AutonomousMonitor()
        self.evolution_monitor = EvolutionMonitor()
        self.performance_monitor = PerformanceMonitor()
    
    async def start_monitoring(self, 
                             modes: List[str] = None,
                             config: Dict = None):
        # Start specific monitoring modes
        
    def get_unified_dashboard(self) -> Dict[str, Any]:
        # Combined dashboard from all monitors
        
    def subscribe_to_events(self, event_type: str, callback: Callable):
        # Event-driven monitoring

# Substitui:
# - cycle_monitor_agent.py
# - autonomous_monitor_agent.py  
# - monitor_evolution.py
```

#### 4.2 Unified Validation System
```python
# src/hephaestus/services/validation/unified_validator.py
class UnifiedValidationSystem(ServiceInterface):
    def __init__(self):
        self.syntax_validator = SyntaxValidator()
        self.pytest_validator = PytestValidator()
        self.json_validator = JsonValidator()
        self.startup_validator = StartupValidator()
    
    async def validate_all(self, context: ValidationContext) -> ValidationResult:
        # Run all applicable validators
        
    def get_validator_for_file(self, file_path: str) -> List[ValidatorInterface]:
        # Return appropriate validators for file type
        
    def register_custom_validator(self, validator: ValidatorInterface):
        # Plugin system for custom validators

# Substitui/consolida:
# - src/hephaestus/services/validation/* (múltiplos)
# - src/hephaestus/api/rest/validation.py
# - system_validation.py
```

#### 4.3 Agent Coordination System
```python
# src/hephaestus/services/coordination/agent_coordinator.py
class AgentCoordinationSystem(ServiceInterface):
    def __init__(self):
        self.swarm_coordinator = SwarmCoordinator()
        self.expansion_coordinator = ExpansionCoordinator()
        self.task_orchestrator = TaskOrchestrator()
    
    async def coordinate_agents(self, 
                              task: CoordinationTask,
                              strategy: CoordinationStrategy) -> CoordinationResult:
        # Unified agent coordination
        
    def create_new_agent(self, agent_spec: AgentSpecification) -> BaseAgent:
        # Dynamic agent creation
        
    def balance_workload(self, agents: List[BaseAgent]) -> WorkloadPlan:
        # Intelligent workload distribution

# Substitui/mescla:
# - swarm_coordinator_agent.py
# - agent_expansion_coordinator.py
```

## 📋 **Implementação Prática**

### **Ordem de Execução Detalhada**

#### **FASE 1: Foundation (2-3 horas)**
1. Criar `utils/agent_factory.py`
2. Criar `utils/llm_manager.py` 
3. Criar `utils/config_manager.py`
4. Criar `utils/logger_factory.py`
5. Criar `utils/metrics_collector.py`
6. **Teste**: Verificar que imports funcionam

#### **FASE 2: Service Layer (2-3 horas)**
1. Criar `services/service_locator.py`
2. Criar `services/interfaces.py`
3. Implementar dependency injection
4. **Teste**: Criar agent simples com nova arquitetura

#### **FASE 3: Agent Refactoring (3-4 horas)**
1. Criar `agents/enhanced_base.py`
2. Refatorar `ArchitectAgent` (piloto)
3. Refatorar `MaestroAgent`
4. Refatorar demais agents
5. **Teste**: Verificar funcionalidade completa

#### **FASE 4: Consolidation (2-3 horas)**
1. Implementar `UnifiedMonitoringSystem`
2. Implementar `UnifiedValidationSystem`
3. Implementar `AgentCoordinationSystem`
4. Remover arquivos duplicados
5. **Teste**: Sistema completo

### **Scripts de Automação**

```bash
#!/bin/bash
# modularize_project.sh

echo "🚀 Iniciando modularização do projeto Hephaestus..."

# FASE 1: Create foundation
echo "📁 FASE 1: Criando foundation..."
mkdir -p src/hephaestus/utils/
mkdir -p src/hephaestus/services/{coordination,monitoring}
mkdir -p src/hephaestus/agents/mixins/

# Create factory files
touch src/hephaestus/utils/agent_factory.py
touch src/hephaestus/utils/llm_manager.py
touch src/hephaestus/utils/config_manager.py
touch src/hephaestus/utils/logger_factory.py
touch src/hephaestus/utils/metrics_collector.py

echo "✅ Foundation estrutura criada"

# Continue with implementation...
```

## 🎯 **Benefícios da Modularização**

### **Desenvolvimento**
- **DRY Principle**: Eliminar código duplicado
- **Single Responsibility**: Cada módulo tem uma responsabilidade
- **Dependency Injection**: Testabilidade e flexibilidade
- **Plugin Architecture**: Extensibilidade

### **Manutenção**
- **Centralized Logic**: LLM calls, logging, config em um lugar
- **Consistent Patterns**: Padrões uniformes em todo código
- **Easy Testing**: Mocking e unit tests simplificados
- **Hot Reload**: Mudanças sem restart completo

### **Performance**
- **Reduced Imports**: Menos dependências circulares
- **Lazy Loading**: Carregar apenas o necessário
- **Metrics-Driven**: Otimização baseada em dados
- **Caching**: Cache inteligente em múltiplos níveis

## ⚠️ **Riscos e Mitigações**

### **Riscos**
- **Over-engineering**: Complexidade desnecessária
- **Breaking Changes**: Quebrar funcionalidade existente
- **Learning Curve**: Time precisa entender nova arquitetura

### **Mitigações**
- **Implementação Gradual**: Fase por fase com testes
- **Backward Compatibility**: Manter APIs antigas temporariamente
- **Extensive Testing**: Teste cada fase antes de prosseguir
- **Documentation**: Documentar padrões e exemplos

## 🔄 **Próximos Passos**

1. **Revisar plano** - Confirmar prioridades e abordagem
2. **Create foundation** - FASE 1 (utils básicos)
3. **Pilot refactoring** - Um agent como prova de conceito
4. **Full migration** - Migrar todos os agents
5. **Consolidation** - Remover duplicatas e limpar

---

**Ready to start?** Sugiro começarmos pela **FASE 1** criando os utils fundamentais, depois fazer um **pilot** com o ArchitectAgent para validar a abordagem antes de migrar tudo.

**Qual fase quer começar primeiro?**