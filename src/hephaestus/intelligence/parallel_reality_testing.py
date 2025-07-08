"""
⚡ PARALLEL REALITY TESTING SYSTEM ⚡

Sistema que testa múltiplas estratégias simultaneamente em ambientes isolados,
permitindo comparação direta e seleção automática da melhor abordagem.

É como ter múltiplas "realidades paralelas" onde cada uma testa uma estratégia diferente,
e depois escolhemos automaticamente a que teve melhor performance.
"""

import asyncio
import logging
import os
import time
import json
import threading
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from enum import Enum
import tempfile
import shutil
import subprocess
import copy
import hashlib
import uuid

from hephaestus.utils.config_loader import load_config
from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response


class TestEnvironmentType(Enum):
    """Tipos de ambiente de teste"""
    SANDBOX = "sandbox"
    MEMORY_ISOLATED = "memory_isolated"
    CONFIG_ISOLATED = "config_isolated"
    FULL_ISOLATION = "full_isolation"


class StrategyType(Enum):
    """Tipos de estratégias que podem ser testadas"""
    PROMPT_VARIANT = "prompt_variant"
    PARAMETER_COMBINATION = "parameter_combination"
    WORKFLOW_APPROACH = "workflow_approach"
    AGENT_CONFIGURATION = "agent_configuration"
    HYBRID_STRATEGY = "hybrid_strategy"


@dataclass
class TestStrategy:
    """Representa uma estratégia a ser testada"""
    strategy_id: str
    strategy_type: StrategyType
    name: str
    description: str
    parameters: Dict[str, Any]
    expected_benefits: List[str]
    risk_level: float
    test_duration: int = 60  # seconds
    environment_type: TestEnvironmentType = TestEnvironmentType.SANDBOX
    
    def __post_init__(self):
        if not self.strategy_id:
            self.strategy_id = f"{self.strategy_type.value}_{uuid.uuid4().hex[:8]}"


@dataclass
class TestResult:
    """Resultado de um teste de estratégia"""
    strategy_id: str
    success: bool
    performance_metrics: Dict[str, float]
    execution_time: float
    error_count: int
    success_rate: float
    resource_usage: Dict[str, float]
    fitness_score: float
    detailed_log: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def calculate_fitness(self) -> float:
        """Calcula score de fitness baseado em todas as métricas"""
        try:
            # Pesos para diferentes métricas
            weights = {
                "success_rate": 0.4,
                "execution_time": -0.2,  # Negativo porque menor é melhor
                "error_count": -0.3,     # Negativo porque menor é melhor
                "resource_usage": -0.1   # Negativo porque menor é melhor
            }
            
            # Normalizar métricas
            normalized_success_rate = self.success_rate
            normalized_execution_time = max(0, 1 - (self.execution_time / 300))  # Normalizar para 5 minutos
            normalized_error_count = max(0, 1 - (self.error_count / 10))  # Normalizar para até 10 erros
            avg_resource_usage = sum(self.resource_usage.values()) / max(len(self.resource_usage), 1)
            normalized_resource_usage = max(0, 1 - avg_resource_usage)
            
            # Calcular fitness
            fitness = (
                weights["success_rate"] * normalized_success_rate +
                weights["execution_time"] * normalized_execution_time +
                weights["error_count"] * normalized_error_count +
                weights["resource_usage"] * normalized_resource_usage
            )
            
            self.fitness_score = max(0, min(1, fitness))
            return self.fitness_score
            
        except Exception:
            self.fitness_score = 0.0
            return 0.0


class ParallelRealityTester:
    """
    Sistema de teste paralelo que executa múltiplas estratégias simultaneamente
    em ambientes isolados e seleciona automaticamente a melhor.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("ParallelRealityTester")
        
        # Configurações
        self.max_parallel_tests = config.get("parallel_testing", {}).get("max_parallel", 5)
        self.default_test_duration = config.get("parallel_testing", {}).get("test_duration", 60)
        self.auto_select_best = config.get("parallel_testing", {}).get("auto_select_best", True)
        self.isolation_level = config.get("parallel_testing", {}).get("isolation_level", "sandbox")
        
        # Estado interno
        self.active_tests: Dict[str, Future] = {}
        self.test_results: Dict[str, TestResult] = {}
        self.test_environments: Dict[str, Dict[str, Any]] = {}
        self.test_history: List[Dict[str, Any]] = []
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.max_parallel_tests)
        self.results_lock = threading.Lock()
        
        # Diretórios para isolamento
        self.test_dir = Path("data/parallel_tests")
        self.environments_dir = self.test_dir / "environments"
        self.results_dir = self.test_dir / "results"
        
        # Criar diretórios
        for directory in [self.test_dir, self.environments_dir, self.results_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("🧪 Parallel Reality Testing System initialized!")
    
    def test_strategies(self, strategies: List[TestStrategy], baseline_config: Dict[str, Any] = None) -> Dict[str, TestResult]:
        """
        Testa múltiplas estratégias em paralelo e retorna resultados
        """
        try:
            if not strategies:
                self.logger.warning("⚠️ No strategies provided for testing")
                return {}
            
            if len(strategies) > self.max_parallel_tests:
                self.logger.warning(f"⚠️ Too many strategies ({len(strategies)}), limiting to {self.max_parallel_tests}")
                strategies = strategies[:self.max_parallel_tests]
            
            self.logger.info(f"🚀 Starting parallel testing of {len(strategies)} strategies")
            
            # Usar configuração baseline ou padrão
            if baseline_config is None:
                baseline_config = self.config
            
            # Criar ambientes isolados para cada estratégia
            test_environments = {}
            for strategy in strategies:
                env_id = f"env_{strategy.strategy_id}"
                test_environments[env_id] = self._create_isolated_environment(strategy, baseline_config)
            
            # Executar testes em paralelo
            futures = {}
            for strategy in strategies:
                env_id = f"env_{strategy.strategy_id}"
                environment = test_environments[env_id]
                
                future = self.executor.submit(
                    self._run_strategy_test,
                    strategy,
                    environment,
                    baseline_config
                )
                futures[strategy.strategy_id] = future
                self.active_tests[strategy.strategy_id] = future
            
            # Aguardar resultados
            results = {}
            for strategy_id, future in futures.items():
                try:
                    result = future.result(timeout=self.default_test_duration + 30)  # Extra buffer
                    results[strategy_id] = result
                    
                    with self.results_lock:
                        self.test_results[strategy_id] = result
                    
                    self.logger.info(f"✅ Strategy {strategy_id} completed with fitness {result.fitness_score:.3f}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Strategy {strategy_id} failed: {e}")
                    # Criar resultado de falha
                    failed_result = TestResult(
                        strategy_id=strategy_id,
                        success=False,
                        performance_metrics={},
                        execution_time=float('inf'),
                        error_count=1,
                        success_rate=0.0,
                        resource_usage={},
                        fitness_score=0.0,
                        detailed_log=[f"Test failed: {str(e)}"],
                        warnings=[f"Test execution failed: {str(e)}"]
                    )
                    results[strategy_id] = failed_result
                
                finally:
                    # Limpar teste ativo
                    if strategy_id in self.active_tests:
                        del self.active_tests[strategy_id]
            
            # Limpar ambientes de teste
            self._cleanup_test_environments(test_environments)
            
            # Salvar histórico
            self._save_test_history(strategies, results)
            
            # Auto-selecionar melhor estratégia se configurado
            if self.auto_select_best and results:
                best_strategy = self._select_best_strategy(results)
                if best_strategy:
                    self.logger.info(f"🏆 Best strategy selected: {best_strategy['strategy_id']} (fitness: {best_strategy['fitness_score']:.3f})")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error in parallel strategy testing: {e}")
            return {}
    
    def _create_isolated_environment(self, strategy: TestStrategy, baseline_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria ambiente isolado para testar a estratégia
        """
        try:
            env_id = f"env_{strategy.strategy_id}"
            env_dir = self.environments_dir / env_id
            env_dir.mkdir(exist_ok=True)
            
            # Criar configuração isolada
            isolated_config = copy.deepcopy(baseline_config)
            
            # Aplicar parâmetros da estratégia
            if strategy.strategy_type == StrategyType.PARAMETER_COMBINATION:
                for param_path, value in strategy.parameters.items():
                    self._set_nested_config(isolated_config, param_path, value)
            
            elif strategy.strategy_type == StrategyType.AGENT_CONFIGURATION:
                if "agents" not in isolated_config:
                    isolated_config["agents"] = {}
                isolated_config["agents"].update(strategy.parameters)
            
            elif strategy.strategy_type == StrategyType.WORKFLOW_APPROACH:
                if "workflows" not in isolated_config:
                    isolated_config["workflows"] = {}
                isolated_config["workflows"].update(strategy.parameters)
            
            elif strategy.strategy_type == StrategyType.HYBRID_STRATEGY:
                # Aplicar múltiplas modificações
                for key, value in strategy.parameters.items():
                    if key.startswith("config."):
                        config_path = key[7:]  # Remove "config." prefix
                        self._set_nested_config(isolated_config, config_path, value)
                    else:
                        isolated_config[key] = value
            
            # Salvar configuração do ambiente
            config_file = env_dir / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(isolated_config, f, indent=2, ensure_ascii=False)
            
            # Criar estrutura de ambiente
            environment = {
                "env_id": env_id,
                "env_dir": str(env_dir),
                "config": isolated_config,
                "strategy": strategy,
                "created_at": datetime.now().isoformat(),
                "isolation_level": strategy.environment_type.value
            }
            
            self.test_environments[env_id] = environment
            
            return environment
            
        except Exception as e:
            self.logger.error(f"Error creating isolated environment: {e}")
            return {}
    
    def _run_strategy_test(self, strategy: TestStrategy, environment: Dict[str, Any], baseline_config: Dict[str, Any]) -> TestResult:
        """
        Executa teste de uma estratégia em ambiente isolado
        """
        start_time = time.time()
        detailed_log = []
        warnings = []
        
        try:
            detailed_log.append(f"Starting test for strategy {strategy.strategy_id}")
            detailed_log.append(f"Strategy type: {strategy.strategy_type.value}")
            detailed_log.append(f"Environment: {environment['env_id']}")
            
            # Métricas de performance
            performance_metrics = {}
            
            # Simular execução da estratégia
            if strategy.strategy_type == StrategyType.PROMPT_VARIANT:
                performance_metrics = self._test_prompt_variant(strategy, environment, detailed_log)
            
            elif strategy.strategy_type == StrategyType.PARAMETER_COMBINATION:
                performance_metrics = self._test_parameter_combination(strategy, environment, detailed_log)
            
            elif strategy.strategy_type == StrategyType.WORKFLOW_APPROACH:
                performance_metrics = self._test_workflow_approach(strategy, environment, detailed_log)
            
            elif strategy.strategy_type == StrategyType.AGENT_CONFIGURATION:
                performance_metrics = self._test_agent_configuration(strategy, environment, detailed_log)
            
            elif strategy.strategy_type == StrategyType.HYBRID_STRATEGY:
                performance_metrics = self._test_hybrid_strategy(strategy, environment, detailed_log)
            
            else:
                warnings.append(f"Unknown strategy type: {strategy.strategy_type}")
                performance_metrics = self._test_generic_strategy(strategy, environment, detailed_log)
            
            # Calcular métricas finais
            execution_time = time.time() - start_time
            success_rate = performance_metrics.get("success_rate", 0.0)
            error_count = performance_metrics.get("error_count", 0)
            
            # Métricas de uso de recursos
            resource_usage = {
                "cpu": performance_metrics.get("cpu_usage", 0.5),
                "memory": performance_metrics.get("memory_usage", 0.4),
                "disk": performance_metrics.get("disk_usage", 0.2)
            }
            
            # Criar resultado
            result = TestResult(
                strategy_id=strategy.strategy_id,
                success=success_rate > 0.5,
                performance_metrics=performance_metrics,
                execution_time=execution_time,
                error_count=error_count,
                success_rate=success_rate,
                resource_usage=resource_usage,
                fitness_score=0.0,  # Será calculado
                detailed_log=detailed_log,
                warnings=warnings
            )
            
            # Calcular fitness
            result.calculate_fitness()
            
            detailed_log.append(f"Test completed successfully in {execution_time:.2f}s")
            detailed_log.append(f"Final fitness score: {result.fitness_score:.3f}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            detailed_log.append(f"Test failed after {execution_time:.2f}s: {str(e)}")
            
            return TestResult(
                strategy_id=strategy.strategy_id,
                success=False,
                performance_metrics={},
                execution_time=execution_time,
                error_count=1,
                success_rate=0.0,
                resource_usage={},
                fitness_score=0.0,
                detailed_log=detailed_log,
                warnings=[f"Test execution failed: {str(e)}"]
            )
    
    def _test_prompt_variant(self, strategy: TestStrategy, environment: Dict[str, Any], log: List[str]) -> Dict[str, float]:
        """Testa variante de prompt"""
        try:
            log.append("Testing prompt variant...")
            
            # Simular teste de prompt
            prompt_text = strategy.parameters.get("prompt", "")
            target_agent = strategy.parameters.get("agent", "general")
            
            # Simular múltiplas execuções
            successes = 0
            total_tests = 10
            
            for i in range(total_tests):
                # Simular execução do prompt
                success = self._simulate_prompt_execution(prompt_text, target_agent)
                if success:
                    successes += 1
                time.sleep(0.1)  # Simular tempo de execução
            
            success_rate = successes / total_tests
            
            log.append(f"Prompt variant test: {successes}/{total_tests} successes")
            
            return {
                "success_rate": success_rate,
                "error_count": total_tests - successes,
                "cpu_usage": 0.3,
                "memory_usage": 0.2,
                "disk_usage": 0.1,
                "prompt_effectiveness": success_rate * 0.9 + 0.1
            }
            
        except Exception as e:
            log.append(f"Error in prompt variant test: {e}")
            return {"success_rate": 0.0, "error_count": 1}
    
    def _test_parameter_combination(self, strategy: TestStrategy, environment: Dict[str, Any], log: List[str]) -> Dict[str, float]:
        """Testa combinação de parâmetros"""
        try:
            log.append("Testing parameter combination...")
            
            # Simular teste de parâmetros
            params = strategy.parameters
            
            # Simular execução com diferentes parâmetros
            performance_score = 0.0
            error_count = 0
            
            for param_name, param_value in params.items():
                try:
                    # Simular aplicação do parâmetro
                    param_performance = self._simulate_parameter_performance(param_name, param_value)
                    performance_score += param_performance
                    time.sleep(0.05)  # Simular tempo de execução
                except Exception:
                    error_count += 1
            
            success_rate = max(0, min(1, performance_score / len(params)))
            
            log.append(f"Parameter combination test: {len(params)} parameters, {error_count} errors")
            
            return {
                "success_rate": success_rate,
                "error_count": error_count,
                "cpu_usage": 0.4,
                "memory_usage": 0.3,
                "disk_usage": 0.2,
                "parameter_optimization": success_rate
            }
            
        except Exception as e:
            log.append(f"Error in parameter combination test: {e}")
            return {"success_rate": 0.0, "error_count": 1}
    
    def _test_workflow_approach(self, strategy: TestStrategy, environment: Dict[str, Any], log: List[str]) -> Dict[str, float]:
        """Testa abordagem de workflow"""
        try:
            log.append("Testing workflow approach...")
            
            # Simular execução de workflow
            workflow_steps = strategy.parameters.get("steps", [])
            workflow_name = strategy.parameters.get("workflow", "default")
            
            successes = 0
            total_steps = len(workflow_steps)
            
            for i, step in enumerate(workflow_steps):
                try:
                    # Simular execução do step
                    success = self._simulate_workflow_step(step, workflow_name)
                    if success:
                        successes += 1
                    time.sleep(0.1)  # Simular tempo de execução
                except Exception:
                    pass
            
            success_rate = successes / max(total_steps, 1)
            
            log.append(f"Workflow approach test: {successes}/{total_steps} steps successful")
            
            return {
                "success_rate": success_rate,
                "error_count": total_steps - successes,
                "cpu_usage": 0.5,
                "memory_usage": 0.4,
                "disk_usage": 0.3,
                "workflow_efficiency": success_rate * 0.8 + 0.2
            }
            
        except Exception as e:
            log.append(f"Error in workflow approach test: {e}")
            return {"success_rate": 0.0, "error_count": 1}
    
    def _test_agent_configuration(self, strategy: TestStrategy, environment: Dict[str, Any], log: List[str]) -> Dict[str, float]:
        """Testa configuração de agente"""
        try:
            log.append("Testing agent configuration...")
            
            # Simular teste de configuração de agente
            agent_config = strategy.parameters
            
            # Simular múltiplas execuções
            successes = 0
            total_tests = 8
            
            for i in range(total_tests):
                try:
                    # Simular execução com configuração
                    success = self._simulate_agent_execution(agent_config)
                    if success:
                        successes += 1
                    time.sleep(0.15)  # Simular tempo de execução
                except Exception:
                    pass
            
            success_rate = successes / total_tests
            
            log.append(f"Agent configuration test: {successes}/{total_tests} executions successful")
            
            return {
                "success_rate": success_rate,
                "error_count": total_tests - successes,
                "cpu_usage": 0.6,
                "memory_usage": 0.5,
                "disk_usage": 0.2,
                "agent_effectiveness": success_rate * 0.9 + 0.1
            }
            
        except Exception as e:
            log.append(f"Error in agent configuration test: {e}")
            return {"success_rate": 0.0, "error_count": 1}
    
    def _test_hybrid_strategy(self, strategy: TestStrategy, environment: Dict[str, Any], log: List[str]) -> Dict[str, float]:
        """Testa estratégia híbrida"""
        try:
            log.append("Testing hybrid strategy...")
            
            # Simular teste de estratégia híbrida (combinação de múltiplas abordagens)
            components = strategy.parameters.get("components", [])
            
            overall_success = 0.0
            overall_errors = 0
            
            # Testar cada componente
            for component in components:
                try:
                    component_type = component.get("type", "unknown")
                    component_params = component.get("params", {})
                    
                    # Simular execução do componente
                    component_success = self._simulate_hybrid_component(component_type, component_params)
                    overall_success += component_success
                    
                    time.sleep(0.1)  # Simular tempo de execução
                    
                except Exception:
                    overall_errors += 1
            
            success_rate = overall_success / max(len(components), 1)
            
            log.append(f"Hybrid strategy test: {len(components)} components, {overall_errors} errors")
            
            return {
                "success_rate": success_rate,
                "error_count": overall_errors,
                "cpu_usage": 0.7,
                "memory_usage": 0.6,
                "disk_usage": 0.4,
                "hybrid_synergy": success_rate * 0.85 + 0.15
            }
            
        except Exception as e:
            log.append(f"Error in hybrid strategy test: {e}")
            return {"success_rate": 0.0, "error_count": 1}
    
    def _test_generic_strategy(self, strategy: TestStrategy, environment: Dict[str, Any], log: List[str]) -> Dict[str, float]:
        """Testa estratégia genérica"""
        try:
            log.append("Testing generic strategy...")
            
            # Simular teste genérico
            time.sleep(0.5)  # Simular tempo de execução
            
            # Gerar métricas aleatórias baseadas no risco
            import random
            base_success = 0.7 - (strategy.risk_level * 0.3)
            success_rate = max(0.1, min(0.9, base_success + random.uniform(-0.2, 0.2)))
            
            log.append(f"Generic strategy test completed")
            
            return {
                "success_rate": success_rate,
                "error_count": int((1 - success_rate) * 5),
                "cpu_usage": 0.5,
                "memory_usage": 0.4,
                "disk_usage": 0.3,
                "generic_effectiveness": success_rate
            }
            
        except Exception as e:
            log.append(f"Error in generic strategy test: {e}")
            return {"success_rate": 0.0, "error_count": 1}
    
    def _simulate_prompt_execution(self, prompt: str, agent: str) -> bool:
        """Simula execução de prompt"""
        import random
        # Simular baseado na qualidade do prompt
        quality_score = min(len(prompt) / 100, 1.0)  # Prompts maiores tendem a ser melhores
        return random.random() < (0.5 + quality_score * 0.3)
    
    def _simulate_parameter_performance(self, param_name: str, param_value: Any) -> float:
        """Simula performance de parâmetro"""
        import random
        # Simular baseado no tipo de parâmetro
        if isinstance(param_value, (int, float)):
            return random.uniform(0.4, 0.9)
        elif isinstance(param_value, str):
            return random.uniform(0.3, 0.8)
        else:
            return random.uniform(0.2, 0.7)
    
    def _simulate_workflow_step(self, step: Dict[str, Any], workflow_name: str) -> bool:
        """Simula execução de step de workflow"""
        import random
        # Simular baseado na complexidade do step
        complexity = len(str(step)) / 50
        return random.random() < (0.8 - complexity * 0.2)
    
    def _simulate_agent_execution(self, agent_config: Dict[str, Any]) -> bool:
        """Simula execução de agente"""
        import random
        # Simular baseado na configuração
        config_quality = min(len(agent_config) / 10, 1.0)
        return random.random() < (0.6 + config_quality * 0.2)
    
    def _simulate_hybrid_component(self, component_type: str, params: Dict[str, Any]) -> float:
        """Simula componente híbrido"""
        import random
        # Simular baseado no tipo de componente
        type_scores = {
            "prompt": 0.7,
            "parameter": 0.6,
            "workflow": 0.8,
            "agent": 0.75,
            "unknown": 0.5
        }
        base_score = type_scores.get(component_type, 0.5)
        return base_score + random.uniform(-0.2, 0.2)
    
    def _set_nested_config(self, config: Dict[str, Any], path: str, value: Any):
        """Define valor em configuração aninhada usando dot notation"""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _select_best_strategy(self, results: Dict[str, TestResult]) -> Optional[Dict[str, Any]]:
        """Seleciona a melhor estratégia baseada nos resultados"""
        try:
            if not results:
                return None
            
            # Filtrar apenas estratégias bem-sucedidas
            successful_results = {k: v for k, v in results.items() if v.success}
            
            if not successful_results:
                self.logger.warning("⚠️ No successful strategies found")
                return None
            
            # Encontrar a melhor baseada no fitness score
            best_strategy_id = max(successful_results.keys(), key=lambda k: successful_results[k].fitness_score)
            best_result = successful_results[best_strategy_id]
            
            return {
                "strategy_id": best_strategy_id,
                "fitness_score": best_result.fitness_score,
                "success_rate": best_result.success_rate,
                "execution_time": best_result.execution_time,
                "performance_metrics": best_result.performance_metrics
            }
            
        except Exception as e:
            self.logger.error(f"Error selecting best strategy: {e}")
            return None
    
    def _cleanup_test_environments(self, environments: Dict[str, Dict[str, Any]]):
        """Limpa ambientes de teste"""
        try:
            for env_id, environment in environments.items():
                env_dir = Path(environment["env_dir"])
                if env_dir.exists():
                    shutil.rmtree(env_dir)
                
                # Remover do cache
                if env_id in self.test_environments:
                    del self.test_environments[env_id]
            
            self.logger.debug(f"🧹 Cleaned up {len(environments)} test environments")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up test environments: {e}")
    
    def _save_test_history(self, strategies: List[TestStrategy], results: Dict[str, TestResult]):
        """Salva histórico de testes"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            history_file = self.results_dir / f"test_history_{timestamp}.json"
            
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "strategies": [
                    {
                        "strategy_id": s.strategy_id,
                        "strategy_type": s.strategy_type.value,
                        "name": s.name,
                        "description": s.description,
                        "parameters": s.parameters,
                        "risk_level": s.risk_level
                    }
                    for s in strategies
                ],
                "results": {
                    strategy_id: {
                        "success": result.success,
                        "fitness_score": result.fitness_score,
                        "execution_time": result.execution_time,
                        "success_rate": result.success_rate,
                        "error_count": result.error_count,
                        "performance_metrics": result.performance_metrics,
                        "warnings": result.warnings
                    }
                    for strategy_id, result in results.items()
                }
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_entry, f, indent=2, ensure_ascii=False)
            
            # Adicionar ao histórico em memória
            self.test_history.append(history_entry)
            
            # Manter apenas últimos 100 testes
            if len(self.test_history) > 100:
                self.test_history = self.test_history[-100:]
            
            self.logger.info(f"📊 Test history saved to {history_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving test history: {e}")
    
    def get_test_status(self) -> Dict[str, Any]:
        """Retorna status atual dos testes"""
        return {
            "active_tests": len(self.active_tests),
            "completed_tests": len(self.test_results),
            "test_history_count": len(self.test_history),
            "max_parallel_tests": self.max_parallel_tests,
            "active_test_ids": list(self.active_tests.keys()),
            "last_test_time": self.test_history[-1]["timestamp"] if self.test_history else None
        }
    
    def get_test_results(self, strategy_id: str = None) -> Dict[str, Any]:
        """Retorna resultados de testes"""
        with self.results_lock:
            if strategy_id:
                return {strategy_id: self.test_results.get(strategy_id, None)}
            else:
                return dict(self.test_results)
    
    def cancel_test(self, strategy_id: str) -> bool:
        """Cancela teste específico"""
        try:
            if strategy_id in self.active_tests:
                future = self.active_tests[strategy_id]
                future.cancel()
                del self.active_tests[strategy_id]
                self.logger.info(f"🚫 Test {strategy_id} cancelled")
                return True
            else:
                self.logger.warning(f"⚠️ Test {strategy_id} not found in active tests")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cancelling test {strategy_id}: {e}")
            return False
    
    def create_strategy_from_template(self, template_name: str, parameters: Dict[str, Any]) -> TestStrategy:
        """Cria estratégia a partir de template"""
        templates = {
            "prompt_optimization": TestStrategy(
                strategy_id="",
                strategy_type=StrategyType.PROMPT_VARIANT,
                name=f"Prompt Optimization - {parameters.get('agent', 'general')}",
                description="Optimize prompts for better performance",
                parameters=parameters,
                expected_benefits=["Better response quality", "Reduced errors"],
                risk_level=0.2
            ),
            "parameter_tuning": TestStrategy(
                strategy_id="",
                strategy_type=StrategyType.PARAMETER_COMBINATION,
                name="Parameter Tuning",
                description="Optimize system parameters",
                parameters=parameters,
                expected_benefits=["Better performance", "Resource optimization"],
                risk_level=0.3
            ),
            "workflow_enhancement": TestStrategy(
                strategy_id="",
                strategy_type=StrategyType.WORKFLOW_APPROACH,
                name="Workflow Enhancement",
                description="Improve workflow efficiency",
                parameters=parameters,
                expected_benefits=["Faster execution", "Better coordination"],
                risk_level=0.4
            ),
            "agent_optimization": TestStrategy(
                strategy_id="",
                strategy_type=StrategyType.AGENT_CONFIGURATION,
                name="Agent Optimization",
                description="Optimize agent configurations",
                parameters=parameters,
                expected_benefits=["Better agent performance", "Reduced conflicts"],
                risk_level=0.3
            ),
            "hybrid_approach": TestStrategy(
                strategy_id="",
                strategy_type=StrategyType.HYBRID_STRATEGY,
                name="Hybrid Approach",
                description="Combined optimization strategy",
                parameters=parameters,
                expected_benefits=["Comprehensive improvement", "Synergistic effects"],
                risk_level=0.5
            )
        }
        
        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        strategy = templates[template_name]
        strategy.strategy_id = f"{template_name}_{uuid.uuid4().hex[:8]}"
        
        return strategy


# Singleton instance
_parallel_tester = None

def get_parallel_reality_tester(config: Dict[str, Any], logger: logging.Logger) -> ParallelRealityTester:
    """Get singleton instance of Parallel Reality Tester"""
    global _parallel_tester
    if _parallel_tester is None:
        _parallel_tester = ParallelRealityTester(config, logger)
    return _parallel_tester 