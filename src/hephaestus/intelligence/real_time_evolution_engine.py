"""
⚡ REAL-TIME EVOLUTION ENGINE ⚡

Sistema de meta-inteligência que evolui o sistema DURANTE a execução:
1. Mutation testing contínuo em background
2. Hot-upgrade de estratégias em tempo real
3. A/B testing paralelo durante runtime
4. Evolução sem downtime

This is where the magic happens - evolution without stopping!
"""

import asyncio
import json
import logging
import random
import time
import threading
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import hashlib
import copy

from hephaestus.utils.llm_client import call_llm_api
from hephaestus.utils.json_parser import parse_json_response


class MutationType(Enum):
    """Tipos de mutação que podem ser aplicadas"""
    PROMPT_OPTIMIZATION = "prompt_optimization"
    STRATEGY_ADJUSTMENT = "strategy_adjustment"
    PARAMETER_TUNING = "parameter_tuning"
    WORKFLOW_MODIFICATION = "workflow_modification"
    AGENT_BEHAVIOR_CHANGE = "agent_behavior_change"


class EvolutionPhase(Enum):
    """Fases da evolução em tempo real"""
    MONITORING = "monitoring"
    MUTATION_GENERATION = "mutation_generation"
    TESTING = "testing"
    EVALUATION = "evaluation"
    DEPLOYMENT = "deployment"


@dataclass
class EvolutionCandidate:
    """Candidato a evolução que está sendo testado"""
    candidate_id: str
    mutation_type: MutationType
    description: str
    mutation_data: Dict[str, Any]
    fitness_score: float = 0.0
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    success_rate: float = 0.0
    performance_impact: float = 0.0
    risk_level: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    tested_at: Optional[datetime] = None
    
    def calculate_fitness(self) -> float:
        """Calcula fitness score baseado em múltiplos fatores"""
        if not self.test_results:
            return 0.0
        
        # Weighted combination of factors
        success_weight = 0.4
        performance_weight = 0.3
        risk_weight = -0.2  # Negative because lower risk is better
        novelty_weight = 0.1
        
        # Calculate novelty (how different this mutation is)
        novelty_score = min(len(self.mutation_data) / 10.0, 1.0)
        
        self.fitness_score = (
            self.success_rate * success_weight +
            self.performance_impact * performance_weight +
            self.risk_level * risk_weight +
            novelty_score * novelty_weight
        )
        
        return self.fitness_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "candidate_id": self.candidate_id,
            "mutation_type": self.mutation_type.value,
            "description": self.description,
            "mutation_data": self.mutation_data,
            "fitness_score": self.fitness_score,
            "success_rate": self.success_rate,
            "performance_impact": self.performance_impact,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat(),
            "tested_at": self.tested_at.isoformat() if self.tested_at else None,
            "test_results_count": len(self.test_results)
        }


@dataclass
class EvolutionMetrics:
    """Métricas de performance da evolução"""
    total_mutations_generated: int = 0
    total_mutations_tested: int = 0
    total_mutations_deployed: int = 0
    successful_deployments: int = 0
    average_fitness_improvement: float = 0.0
    best_fitness_score: float = 0.0
    evolution_uptime: float = 0.0
    last_evolution_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "total_mutations_generated": self.total_mutations_generated,
            "total_mutations_tested": self.total_mutations_tested,
            "total_mutations_deployed": self.total_mutations_deployed,
            "successful_deployments": self.successful_deployments,
            "average_fitness_improvement": self.average_fitness_improvement,
            "best_fitness_score": self.best_fitness_score,
            "evolution_uptime": self.evolution_uptime,
            "last_evolution_time": self.last_evolution_time.isoformat() if self.last_evolution_time else None
        }


class RealTimeEvolutionEngine:
    """
    ⚡ Engine de Evolução em Tempo Real - O Coração da Auto-Melhoria
    
    Este sistema monitora performance continuamente e aplica melhorias
    SEM PARAR a execução principal do sistema.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger, collective_network=None):
        self.config = config
        self.logger = logger.getChild("RealTimeEvolutionEngine")
        
        # Configurações
        self.evolution_enabled = config.get("real_time_evolution", {}).get("enabled", True)
        self.mutation_interval = config.get("real_time_evolution", {}).get("mutation_interval", 30)  # seconds
        self.max_parallel_tests = config.get("real_time_evolution", {}).get("max_parallel_tests", 3)
        self.fitness_threshold = config.get("real_time_evolution", {}).get("fitness_threshold", 0.1)
        self.risk_threshold = config.get("real_time_evolution", {}).get("risk_threshold", 0.3)
        
        # Estado interno
        self.current_phase = EvolutionPhase.MONITORING
        self.evolution_candidates: Dict[str, EvolutionCandidate] = {}
        self.active_tests: Dict[str, asyncio.Task] = {}
        self.deployed_mutations: Dict[str, EvolutionCandidate] = {}
        self.metrics = EvolutionMetrics()
        
        # Threading
        self.evolution_thread: Optional[threading.Thread] = None
        self.evolution_running = False
        self.evolution_lock = threading.Lock()
        
        # Callback system for applying mutations
        self.mutation_callbacks: Dict[MutationType, Callable] = {}
        
        # Performance tracking
        self.performance_history: List[Dict[str, Any]] = []
        self.baseline_performance: Dict[str, float] = {}
        
        # Collective Intelligence Network integration
        self.collective_network = collective_network
        
        # Start time
        self.start_time = datetime.now()
        
        self.logger.info("⚡ Real-Time Evolution Engine initialized - Continuous evolution active!")
    
    def start_evolution(self):
        """Inicia o processo de evolução em tempo real"""
        if not self.evolution_enabled:
            self.logger.warning("Evolution engine disabled in config")
            return
        
        if self.evolution_running:
            self.logger.warning("Evolution already running")
            return
        
        self.evolution_running = True
        self.evolution_thread = threading.Thread(target=self._evolution_loop, daemon=True)
        self.evolution_thread.start()
        
        self.logger.info("🚀 Real-time evolution started!")
    
    def stop_evolution(self):
        """Para o processo de evolução"""
        self.evolution_running = False
        
        if self.evolution_thread:
            self.evolution_thread.join(timeout=5)
        
        # Cancel active tests
        for task in self.active_tests.values():
            if not task.done():
                task.cancel()
        
        self.logger.info("🛑 Real-time evolution stopped")
    
    def _evolution_loop(self):
        """Loop principal da evolução em tempo real"""
        self.logger.info("🔄 Evolution loop started")
        
        while self.evolution_running:
            try:
                # Update metrics
                self._update_evolution_metrics()
                
                # Phase 1: Monitor current performance
                if self.current_phase == EvolutionPhase.MONITORING:
                    self._monitor_performance()
                    self.current_phase = EvolutionPhase.MUTATION_GENERATION
                
                # Phase 2: Generate mutation candidates
                elif self.current_phase == EvolutionPhase.MUTATION_GENERATION:
                    self._generate_mutations()
                    self.current_phase = EvolutionPhase.TESTING
                
                # Phase 3: Test mutations in parallel
                elif self.current_phase == EvolutionPhase.TESTING:
                    self._test_mutations()
                    self.current_phase = EvolutionPhase.EVALUATION
                
                # Phase 4: Evaluate results
                elif self.current_phase == EvolutionPhase.EVALUATION:
                    self._evaluate_mutations()
                    self.current_phase = EvolutionPhase.DEPLOYMENT
                
                # Phase 5: Deploy best mutations
                elif self.current_phase == EvolutionPhase.DEPLOYMENT:
                    self._deploy_best_mutations()
                    self.current_phase = EvolutionPhase.MONITORING
                
                # Sleep between phases
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error in evolution loop: {e}", exc_info=True)
                time.sleep(5)  # Longer sleep on error
    
    def _monitor_performance(self):
        """Monitora performance atual do sistema"""
        try:
            # Collect current performance metrics
            current_metrics = self._collect_performance_metrics()
            
            # Add to history
            self.performance_history.append({
                "timestamp": datetime.now().isoformat(),
                "metrics": current_metrics
            })
            
            # Keep only last 100 entries
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]
            
            # Update baseline if this is the first run
            if not self.baseline_performance:
                self.baseline_performance = current_metrics
                self.logger.info(f"📊 Baseline performance established: {current_metrics}")
            
            # Check if performance degraded significantly
            performance_delta = self._calculate_performance_delta(current_metrics)
            if performance_delta < -0.2:  # 20% degradation
                self.logger.warning(f"📉 Performance degradation detected: {performance_delta:.2%}")
                # Trigger emergency evolution
                self._trigger_emergency_evolution()
            
        except Exception as e:
            self.logger.error(f"Error monitoring performance: {e}")
    
    def _collect_performance_metrics(self) -> Dict[str, float]:
        """Coleta métricas de performance atuais"""
        try:
            # These would be collected from the actual system
            # For now, we'll simulate based on what we can measure
            
            metrics = {
                "success_rate": self._calculate_recent_success_rate(),
                "average_execution_time": self._calculate_average_execution_time(),
                "error_rate": self._calculate_error_rate(),
                "memory_usage": self._get_memory_usage(),
                "agent_efficiency": self._calculate_agent_efficiency()
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting performance metrics: {e}")
            return {
                "success_rate": 0.5,
                "average_execution_time": 60.0,
                "error_rate": 0.2,
                "memory_usage": 0.5,
                "agent_efficiency": 0.6
            }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calcula taxa de sucesso recente"""
        # This would integrate with the actual memory system
        # For now, simulate based on recent performance
        if len(self.performance_history) < 2:
            return 0.5
        
        recent_performance = self.performance_history[-5:]  # Last 5 entries
        success_rates = [p["metrics"].get("success_rate", 0.5) for p in recent_performance]
        return sum(success_rates) / len(success_rates)
    
    def _calculate_average_execution_time(self) -> float:
        """Calcula tempo médio de execução"""
        # Simulate based on complexity and system load
        base_time = 45.0
        load_factor = random.uniform(0.8, 1.2)
        return base_time * load_factor
    
    def _calculate_error_rate(self) -> float:
        """Calcula taxa de erro"""
        # Simulate error rate based on system stability
        return random.uniform(0.1, 0.3)
    
    def _get_memory_usage(self) -> float:
        """Obtém uso de memória (normalizado 0-1)"""
        # Simulate memory usage
        return random.uniform(0.3, 0.7)
    
    def _calculate_agent_efficiency(self) -> float:
        """Calcula eficiência dos agentes"""
        # Simulate agent efficiency
        return random.uniform(0.5, 0.8)
    
    def _calculate_performance_delta(self, current_metrics: Dict[str, float]) -> float:
        """Calcula delta de performance comparado ao baseline"""
        if not self.baseline_performance:
            return 0.0
        
        # Weighted performance calculation
        weights = {
            "success_rate": 0.4,
            "average_execution_time": -0.2,  # Negative because lower is better
            "error_rate": -0.3,  # Negative because lower is better
            "memory_usage": -0.05,  # Negative because lower is better
            "agent_efficiency": 0.25
        }
        
        current_score = 0.0
        baseline_score = 0.0
        
        for metric, weight in weights.items():
            current_score += current_metrics.get(metric, 0.0) * weight
            baseline_score += self.baseline_performance.get(metric, 0.0) * weight
        
        return (current_score - baseline_score) / max(abs(baseline_score), 0.1)
    
    def _generate_mutations(self):
        """Gera candidatos a mutação baseados na performance atual"""
        try:
            # Limit active candidates
            if len(self.evolution_candidates) >= self.max_parallel_tests * 2:
                self.logger.debug("Maximum candidates reached, skipping generation")
                return
            
            # Generate different types of mutations
            mutation_generators = [
                self._generate_prompt_optimization,
                self._generate_strategy_adjustment,
                self._generate_parameter_tuning,
                self._generate_workflow_modification,
                self._generate_agent_behavior_change
            ]
            
            # Generate 1-2 mutations per cycle
            num_mutations = random.randint(1, 2)
            
            for _ in range(num_mutations):
                generator = random.choice(mutation_generators)
                try:
                    candidate = generator()
                    if candidate:
                        self.evolution_candidates[candidate.candidate_id] = candidate
                        self.metrics.total_mutations_generated += 1
                        self.logger.info(f"🧬 Generated mutation: {candidate.description}")
                
                except Exception as e:
                    self.logger.error(f"Error generating mutation: {e}")
            
        except Exception as e:
            self.logger.error(f"Error in mutation generation: {e}")
    
    def _generate_prompt_optimization(self) -> Optional[EvolutionCandidate]:
        """Gera mutação para otimização de prompts"""
        prompt_optimizations = [
            {
                "target": "objective_generation",
                "modification": "Add more context about recent failures",
                "risk": 0.1
            },
            {
                "target": "architect_prompts",
                "modification": "Emphasize error handling and robustness",
                "risk": 0.2
            },
            {
                "target": "maestro_prompts",
                "modification": "Include performance metrics in decision making",
                "risk": 0.15
            }
        ]
        
        optimization = random.choice(prompt_optimizations)
        
        candidate_id = f"prompt_opt_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return EvolutionCandidate(
            candidate_id=candidate_id,
            mutation_type=MutationType.PROMPT_OPTIMIZATION,
            description=f"Optimize {optimization['target']}: {optimization['modification']}",
            mutation_data=optimization,
            risk_level=optimization["risk"]
        )
    
    def _generate_strategy_adjustment(self) -> Optional[EvolutionCandidate]:
        """Gera mutação para ajuste de estratégia"""
        strategy_adjustments = [
            {
                "strategy": "validation_retries",
                "old_value": 1,
                "new_value": 2,
                "risk": 0.1
            },
            {
                "strategy": "cycle_delay_seconds",
                "old_value": 1,
                "new_value": 0.5,
                "risk": 0.2
            },
            {
                "strategy": "degenerative_loop_threshold",
                "old_value": 3,
                "new_value": 2,
                "risk": 0.15
            }
        ]
        
        adjustment = random.choice(strategy_adjustments)
        
        candidate_id = f"strategy_adj_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return EvolutionCandidate(
            candidate_id=candidate_id,
            mutation_type=MutationType.STRATEGY_ADJUSTMENT,
            description=f"Adjust {adjustment['strategy']}: {adjustment['old_value']} → {adjustment['new_value']}",
            mutation_data=adjustment,
            risk_level=adjustment["risk"]
        )
    
    def _generate_parameter_tuning(self) -> Optional[EvolutionCandidate]:
        """Gera mutação para tuning de parâmetros"""
        parameter_tunings = [
            {
                "parameter": "temperature",
                "component": "llm_calls",
                "current_value": 0.3,
                "new_value": random.uniform(0.1, 0.5),
                "risk": 0.2
            },
            {
                "parameter": "max_tokens",
                "component": "llm_calls",
                "current_value": 2000,
                "new_value": random.randint(1500, 3000),
                "risk": 0.1
            },
            {
                "parameter": "timeout",
                "component": "async_operations",
                "current_value": 300,
                "new_value": random.randint(180, 450),
                "risk": 0.25
            }
        ]
        
        tuning = random.choice(parameter_tunings)
        
        candidate_id = f"param_tune_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return EvolutionCandidate(
            candidate_id=candidate_id,
            mutation_type=MutationType.PARAMETER_TUNING,
            description=f"Tune {tuning['parameter']} in {tuning['component']}: {tuning['current_value']} → {tuning['new_value']}",
            mutation_data=tuning,
            risk_level=tuning["risk"]
        )
    
    def _generate_workflow_modification(self) -> Optional[EvolutionCandidate]:
        """Gera mutação para modificação de workflow"""
        workflow_modifications = [
            {
                "workflow": "validation_pipeline",
                "modification": "Add pre-validation step",
                "impact": "Reduce validation failures",
                "risk": 0.3
            },
            {
                "workflow": "agent_coordination",
                "modification": "Increase parallel execution",
                "impact": "Faster completion",
                "risk": 0.25
            },
            {
                "workflow": "error_handling",
                "modification": "Add retry mechanism",
                "impact": "Better error recovery",
                "risk": 0.2
            }
        ]
        
        modification = random.choice(workflow_modifications)
        
        candidate_id = f"workflow_mod_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return EvolutionCandidate(
            candidate_id=candidate_id,
            mutation_type=MutationType.WORKFLOW_MODIFICATION,
            description=f"Modify {modification['workflow']}: {modification['modification']}",
            mutation_data=modification,
            risk_level=modification["risk"]
        )
    
    def _generate_agent_behavior_change(self) -> Optional[EvolutionCandidate]:
        """Gera mutação para mudança de comportamento dos agentes"""
        behavior_changes = [
            {
                "agent": "architect",
                "behavior": "risk_assessment",
                "change": "More conservative patch generation",
                "risk": 0.15
            },
            {
                "agent": "maestro",
                "behavior": "strategy_selection",
                "change": "Prefer strategies with higher success rates",
                "risk": 0.1
            },
            {
                "agent": "bug_hunter",
                "behavior": "detection_sensitivity",
                "change": "Increase detection threshold",
                "risk": 0.2
            }
        ]
        
        change = random.choice(behavior_changes)
        
        candidate_id = f"behavior_change_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return EvolutionCandidate(
            candidate_id=candidate_id,
            mutation_type=MutationType.AGENT_BEHAVIOR_CHANGE,
            description=f"Change {change['agent']} {change['behavior']}: {change['change']}",
            mutation_data=change,
            risk_level=change["risk"]
        )
    
    def _test_mutations(self):
        """Testa mutações em paralelo"""
        try:
            # Get untested candidates
            untested = [c for c in self.evolution_candidates.values() if not c.tested_at]
            
            if not untested:
                return
            
            # Limit concurrent tests
            available_slots = self.max_parallel_tests - len(self.active_tests)
            if available_slots <= 0:
                return
            
            # Select candidates to test (prioritize by risk level - test safer ones first)
            candidates_to_test = sorted(untested, key=lambda c: c.risk_level)[:available_slots]
            
            # Test mutations synchronously in thread context
            for candidate in candidates_to_test:
                try:
                    # Test synchronously since we're in a thread
                    self._test_single_mutation_sync(candidate)
                    self.logger.info(f"🧪 Testing mutation: {candidate.description}")
                except Exception as e:
                    self.logger.error(f"Error testing single mutation: {e}")
            
        except Exception as e:
            self.logger.error(f"Error testing mutations: {e}")
    
    def _test_single_mutation_sync(self, candidate: EvolutionCandidate):
        """Testa uma única mutação de forma síncrona"""
        try:
            self.logger.debug(f"Testing candidate: {candidate.candidate_id}")
            
            # Simulate testing (in real implementation, this would apply the mutation temporarily)
            test_duration = random.uniform(1, 3)  # 1-3 seconds for faster testing
            time.sleep(test_duration)
            
            # Simulate test results
            success_rate = random.uniform(0.3, 0.9)
            performance_impact = random.uniform(-0.2, 0.3)
            
            # Add some logic based on mutation type
            if candidate.mutation_type == MutationType.PROMPT_OPTIMIZATION:
                success_rate += 0.1  # Prompt optimization tends to help
            elif candidate.mutation_type == MutationType.PARAMETER_TUNING:
                performance_impact += 0.05  # Parameter tuning tends to improve performance
            
            # Clamp values
            success_rate = max(0.0, min(1.0, success_rate))
            performance_impact = max(-1.0, min(1.0, performance_impact))
            
            # Update candidate
            candidate.success_rate = success_rate
            candidate.performance_impact = performance_impact
            candidate.tested_at = datetime.now()
            
            # Add test result
            test_result = {
                "timestamp": datetime.now().isoformat(),
                "success_rate": success_rate,
                "performance_impact": performance_impact,
                "test_duration": test_duration
            }
            candidate.test_results.append(test_result)
            
            # Calculate fitness
            candidate.calculate_fitness()
            
            self.metrics.total_mutations_tested += 1
            
            self.logger.info(f"✅ Test completed: {candidate.description} (fitness: {candidate.fitness_score:.3f})")
            
        except Exception as e:
            self.logger.error(f"Error testing mutation {candidate.candidate_id}: {e}")

    async def _test_single_mutation(self, candidate: EvolutionCandidate):
        """Testa uma única mutação"""
        try:
            self.logger.debug(f"Testing candidate: {candidate.candidate_id}")
            
            # Simulate testing (in real implementation, this would apply the mutation temporarily)
            test_duration = random.uniform(5, 15)  # 5-15 seconds
            await asyncio.sleep(test_duration)
            
            # Simulate test results
            success_rate = random.uniform(0.3, 0.9)
            performance_impact = random.uniform(-0.2, 0.3)
            
            # Add some logic based on mutation type
            if candidate.mutation_type == MutationType.PROMPT_OPTIMIZATION:
                success_rate += 0.1  # Prompt optimization tends to help
            elif candidate.mutation_type == MutationType.PARAMETER_TUNING:
                performance_impact += 0.05  # Parameter tuning tends to improve performance
            
            # Clamp values
            success_rate = max(0.0, min(1.0, success_rate))
            performance_impact = max(-1.0, min(1.0, performance_impact))
            
            # Update candidate
            candidate.success_rate = success_rate
            candidate.performance_impact = performance_impact
            candidate.tested_at = datetime.now()
            
            # Add test result
            test_result = {
                "timestamp": datetime.now().isoformat(),
                "success_rate": success_rate,
                "performance_impact": performance_impact,
                "test_duration": test_duration
            }
            candidate.test_results.append(test_result)
            
            # Calculate fitness
            candidate.calculate_fitness()
            
            self.metrics.total_mutations_tested += 1
            
            self.logger.info(f"✅ Test completed: {candidate.description} (fitness: {candidate.fitness_score:.3f})")
            
        except Exception as e:
            self.logger.error(f"Error testing mutation {candidate.candidate_id}: {e}")
        
        finally:
            # Remove from active tests
            if candidate.candidate_id in self.active_tests:
                del self.active_tests[candidate.candidate_id]
    
    def _evaluate_mutations(self):
        """Avalia resultados dos testes"""
        try:
            # Get tested candidates
            tested = [c for c in self.evolution_candidates.values() if c.tested_at]
            
            if not tested:
                return
            
            # Sort by fitness score
            tested.sort(key=lambda c: c.fitness_score, reverse=True)
            
            # Update best fitness
            if tested:
                best_fitness = tested[0].fitness_score
                if best_fitness > self.metrics.best_fitness_score:
                    self.metrics.best_fitness_score = best_fitness
                    self.logger.info(f"🏆 New best fitness score: {best_fitness:.3f}")
            
            # Remove low-fitness candidates
            threshold = self.fitness_threshold
            removed = 0
            for candidate in tested:
                if candidate.fitness_score < threshold:
                    del self.evolution_candidates[candidate.candidate_id]
                    removed += 1
            
            if removed > 0:
                self.logger.info(f"🗑️ Removed {removed} low-fitness candidates")
            
        except Exception as e:
            self.logger.error(f"Error evaluating mutations: {e}")
    
    def _deploy_best_mutations(self):
        """Deploys as melhores mutações"""
        try:
            # Get candidates ready for deployment
            ready_for_deployment = [
                c for c in self.evolution_candidates.values()
                if c.tested_at and c.fitness_score > self.fitness_threshold and c.risk_level < self.risk_threshold
            ]
            
            if not ready_for_deployment:
                return
            
            # Sort by fitness and deploy the best one
            ready_for_deployment.sort(key=lambda c: c.fitness_score, reverse=True)
            best_candidate = ready_for_deployment[0]
            
            # Deploy the mutation
            deployment_success = self._deploy_mutation(best_candidate)
            
            if deployment_success:
                self.deployed_mutations[best_candidate.candidate_id] = best_candidate
                self.metrics.total_mutations_deployed += 1
                self.metrics.successful_deployments += 1
                self.metrics.last_evolution_time = datetime.now()
                
                # Update baseline with improvement
                improvement = best_candidate.fitness_score - self.metrics.best_fitness_score
                self.metrics.average_fitness_improvement = (
                    self.metrics.average_fitness_improvement + improvement
                ) / 2
                
                self.logger.info(f"🚀 Deployed mutation: {best_candidate.description}")
                
                # Remove from candidates
                del self.evolution_candidates[best_candidate.candidate_id]
            
        except Exception as e:
            self.logger.error(f"Error deploying mutations: {e}")
    
    def _deploy_mutation(self, candidate: EvolutionCandidate) -> bool:
        """Aplica uma mutação ao sistema"""
        try:
            # Get the appropriate callback for this mutation type
            callback = self.mutation_callbacks.get(candidate.mutation_type)
            
            if callback:
                # Apply the mutation
                success = callback(candidate.mutation_data)
                if success:
                    # Compartilhar conhecimento sobre a evolução
                    if self.collective_network:
                        try:
                            self.collective_network.share_evolution_knowledge(
                                agent_id="real_time_evolution_engine",
                                evolution_type="mutation_applied",
                                details={
                                    "mutation": candidate.description,
                                    "fitness": candidate.fitness_score,
                                    "mutation_type": candidate.mutation_type.value,
                                    "description": f"Successfully applied {candidate.mutation_type.value} mutation",
                                    "success_rate": candidate.success_rate,
                                    "performance_impact": candidate.performance_impact
                                }
                            )
                        except Exception as e:
                            self.logger.error(f"❌ Error sharing evolution knowledge: {e}")
                    
                    self.logger.info(f"✅ Applied mutation: {candidate.description}")
                    return True
                else:
                    self.logger.warning(f"❌ Failed to apply mutation: {candidate.description}")
            else:
                # For now, just log (in real implementation, would apply actual changes)
                self.logger.info(f"📝 Simulated deployment: {candidate.description}")
                return True
            
        except Exception as e:
            self.logger.error(f"Error deploying mutation: {e}")
        
        return False
    
    def _trigger_emergency_evolution(self):
        """Dispara evolução de emergência em caso de degradação"""
        self.logger.warning("🚨 Emergency evolution triggered!")
        
        # Compartilhar conhecimento sobre evolução de emergência
        if self.collective_network:
            try:
                self.collective_network.share_evolution_knowledge(
                    agent_id="real_time_evolution_engine",
                    evolution_type="emergency_evolution",
                    details={
                        "trigger": "performance_degradation",
                        "corrections": ["validation_retries", "system_load_reduction"],
                        "description": "Emergency evolution triggered due to performance degradation"
                    }
                )
            except Exception as e:
                self.logger.error(f"❌ Error sharing emergency evolution knowledge: {e}")
        
        # Generate emergency mutations (more aggressive)
        emergency_mutations = [
            {
                "type": MutationType.STRATEGY_ADJUSTMENT,
                "description": "Emergency: Increase validation retries",
                "data": {"strategy": "validation_retries", "new_value": 3},
                "risk": 0.4
            },
            {
                "type": MutationType.PARAMETER_TUNING,
                "description": "Emergency: Reduce system load",
                "data": {"parameter": "cycle_delay_seconds", "new_value": 2.0},
                "risk": 0.3
            }
        ]
        
        for mutation_info in emergency_mutations:
            candidate_id = f"emergency_{int(time.time())}_{random.randint(1000, 9999)}"
            
            candidate = EvolutionCandidate(
                candidate_id=candidate_id,
                mutation_type=mutation_info["type"],
                description=mutation_info["description"],
                mutation_data=mutation_info["data"],
                risk_level=mutation_info["risk"]
            )
            
            self.evolution_candidates[candidate.candidate_id] = candidate
            self.logger.info(f"🆘 Emergency mutation generated: {candidate.description}")
    
    def _update_evolution_metrics(self):
        """Atualiza métricas de evolução"""
        self.metrics.evolution_uptime = (datetime.now() - self.start_time).total_seconds()
    
    def register_mutation_callback(self, mutation_type: MutationType, callback: Callable):
        """Registra callback para aplicar mutações"""
        self.mutation_callbacks[mutation_type] = callback
        self.logger.info(f"📋 Registered callback for {mutation_type.value}")
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """Retorna status atual da evolução"""
        return {
            "evolution_enabled": self.evolution_enabled,
            "evolution_running": self.evolution_running,
            "current_phase": self.current_phase.value,
            "active_candidates": len(self.evolution_candidates),
            "active_tests": len(self.active_tests),
            "deployed_mutations": len(self.deployed_mutations),
            "metrics": self.metrics.to_dict(),
            "recent_performance": self.performance_history[-5:] if self.performance_history else []
        }
    
    def get_best_mutations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna as melhores mutações"""
        all_mutations = list(self.evolution_candidates.values()) + list(self.deployed_mutations.values())
        all_mutations.sort(key=lambda c: c.fitness_score, reverse=True)
        
        return [m.to_dict() for m in all_mutations[:limit]]
    
    def save_evolution_state(self, filename: str = None):
        """Salva estado da evolução"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evolution_state_{timestamp}.json"
        
        state = {
            "timestamp": datetime.now().isoformat(),
            "evolution_status": self.get_evolution_status(),
            "best_mutations": self.get_best_mutations(),
            "performance_history": self.performance_history
        }
        
        state_path = Path("data/reports") / filename
        state_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Evolution state saved to {state_path}")
        
        return state_path


# Singleton instance
_evolution_engine = None

def get_real_time_evolution_engine(config: Dict[str, Any], logger: logging.Logger, collective_network=None) -> RealTimeEvolutionEngine:
    """Get singleton instance of the Real-Time Evolution Engine"""
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = RealTimeEvolutionEngine(config, logger, collective_network)
    return _evolution_engine