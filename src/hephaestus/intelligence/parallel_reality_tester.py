"""
🧪 PARALLEL REALITY TESTING SYSTEM
Sistema revolucionário que executa múltiplas estratégias simultaneamente
e escolhe a melhor em tempo real - a 3ª meta-funcionalidade!
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import threading
import copy

class RealityTestStatus(Enum):
    """Status de um teste de realidade paralela"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED_EARLY = "terminated_early"
    WINNER = "winner"

class StrategyType(Enum):
    """Tipos de estratégias que podem ser testadas"""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    EXPERIMENTAL = "experimental"
    OPTIMIZED = "optimized"

@dataclass
class RealityTest:
    """Representa um teste de realidade (estratégia sendo executada)"""
    test_id: str
    strategy_name: str
    strategy_type: StrategyType
    strategy_config: Dict[str, Any]
    status: RealityTestStatus = RealityTestStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: float = 0.0
    success_probability: float = 0.0
    quality_score: float = 0.0
    efficiency_score: float = 0.0
    risk_score: float = 0.0
    composite_score: float = 0.0
    intermediate_results: List[Dict[str, Any]] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    resource_usage: Dict[str, float] = field(default_factory=dict)
    
    def calculate_composite_score(self) -> float:
        """Calcula score composto baseado em múltiplos fatores"""
        # Weighted scoring (ajustável baseado no contexto)
        success_weight = 0.4
        quality_weight = 0.3
        efficiency_weight = 0.2
        risk_weight = -0.1  # Negative because lower risk is better
        
        self.composite_score = (
            self.success_probability * success_weight +
            self.quality_score * quality_weight +
            self.efficiency_score * efficiency_weight +
            self.risk_score * risk_weight
        )
        
        return self.composite_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "test_id": self.test_id,
            "strategy_name": self.strategy_name,
            "strategy_type": self.strategy_type.value,
            "strategy_config": self.strategy_config,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "execution_time": self.execution_time,
            "success_probability": self.success_probability,
            "quality_score": self.quality_score,
            "efficiency_score": self.efficiency_score,
            "risk_score": self.risk_score,
            "composite_score": self.composite_score,
            "intermediate_results": self.intermediate_results,
            "error_messages": self.error_messages,
            "resource_usage": self.resource_usage
        }

@dataclass 
class ParallelTestSession:
    """Sessão de teste paralelo com múltiplas realidades"""
    session_id: str
    objective: str
    reality_tests: List[RealityTest] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    winner_test_id: Optional[str] = None
    session_status: str = "active"
    comparison_matrix: Dict[str, Any] = field(default_factory=dict)
    learning_insights: List[str] = field(default_factory=list)

class ParallelRealityTester:
    """
    🧪 Parallel Reality Testing System
    
    Sistema que executa múltiplas estratégias simultaneamente para o mesmo objetivo
    e escolhe dinamicamente a melhor baseada em performance em tempo real.
    
    Features:
    - Execução paralela de 2-5 estratégias diferentes
    - Comparação A/B em tempo real
    - Early termination de estratégias failing
    - Dynamic winner selection
    - Learning from strategy comparisons
    - Resource usage optimization
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger.getChild("ParallelRealityTester")
        
        # Configuration
        self.max_parallel_tests = config.get("parallel_reality", {}).get("max_parallel_tests", 3)
        self.early_termination_threshold = config.get("parallel_reality", {}).get("early_termination_threshold", 0.2)
        self.winner_selection_interval = config.get("parallel_reality", {}).get("winner_selection_interval", 30)  # seconds
        self.min_execution_time = config.get("parallel_reality", {}).get("min_execution_time", 10)  # seconds
        self.max_session_time = config.get("parallel_reality", {}).get("max_session_time", 300)  # 5 minutes
        
        # State
        self.active_sessions: Dict[str, ParallelTestSession] = {}
        self.strategy_performance_history: Dict[str, List[float]] = {}
        self.comparison_history: List[Dict[str, Any]] = []
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=self.max_parallel_tests)
        self.monitoring_thread = None
        self.should_stop = threading.Event()
        
        # Strategy generators
        self.strategy_generators = {
            StrategyType.CONSERVATIVE: self._generate_conservative_strategy,
            StrategyType.AGGRESSIVE: self._generate_aggressive_strategy,
            StrategyType.BALANCED: self._generate_balanced_strategy,
            StrategyType.EXPERIMENTAL: self._generate_experimental_strategy,
            StrategyType.OPTIMIZED: self._generate_optimized_strategy
        }
        
        # Load existing data
        self._load_historical_data()
        
        # Start monitoring
        self._start_monitoring()
        
        self.logger.info("🧪 Parallel Reality Testing System initialized!")
        self.logger.info(f"📊 Max parallel tests: {self.max_parallel_tests}")
        self.logger.info(f"⏱️ Winner selection interval: {self.winner_selection_interval}s")
    
    async def test_multiple_realities(self, objective: str, context: Dict[str, Any] = None) -> Tuple[RealityTest, ParallelTestSession]:
        """
        🚀 CORE FUNCTION: Executa múltiplas estratégias em paralelo
        
        Returns:
            Tuple[RealityTest, ParallelTestSession]: (winning_test, session_data)
        """
        self.logger.info(f"🧪 Starting parallel reality testing for: {objective[:100]}...")
        
        # Create session
        session = ParallelTestSession(
            session_id=str(uuid.uuid4()),
            objective=objective,
            start_time=datetime.now()
        )
        
        # Generate multiple strategies
        strategies = self._generate_test_strategies(objective, context or {})
        
        # Create reality tests
        for strategy_name, strategy_config in strategies.items():
            test = RealityTest(
                test_id=str(uuid.uuid4()),
                strategy_name=strategy_name,
                strategy_type=strategy_config.get("type", StrategyType.BALANCED),
                strategy_config=strategy_config
            )
            session.reality_tests.append(test)
        
        # Store session
        self.active_sessions[session.session_id] = session
        
        self.logger.info(f"🎯 Generated {len(strategies)} parallel strategies:")
        for test in session.reality_tests:
            self.logger.info(f"  - {test.strategy_name} ({test.strategy_type.value})")
        
        # Execute tests in parallel
        winner_test = await self._execute_parallel_tests(session)
        
        # Finalize session
        session.end_time = datetime.now()
        session.winner_test_id = winner_test.test_id if winner_test else None
        session.session_status = "completed"
        
        # Learn from comparison
        self._learn_from_session(session)
        
        # Save results
        self._save_session_results(session)
        
        self.logger.info(f"🏆 Winner: {winner_test.strategy_name if winner_test else 'None'} (score: {winner_test.composite_score if winner_test else 0:.3f})")
        
        return winner_test, session
    
    def _generate_test_strategies(self, objective: str, context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Gera múltiplas estratégias para testar"""
        strategies = {}
        
        # Determine which strategies to generate based on objective complexity
        complexity_score = self._assess_objective_complexity(objective)
        
        if complexity_score > 0.7:
            # High complexity - use conservative + balanced + experimental
            strategy_types = [StrategyType.CONSERVATIVE, StrategyType.BALANCED, StrategyType.EXPERIMENTAL]
        elif complexity_score > 0.4:
            # Medium complexity - use balanced + aggressive + optimized
            strategy_types = [StrategyType.BALANCED, StrategyType.AGGRESSIVE, StrategyType.OPTIMIZED]
        else:
            # Low complexity - use aggressive + optimized + experimental
            strategy_types = [StrategyType.AGGRESSIVE, StrategyType.OPTIMIZED, StrategyType.EXPERIMENTAL]
        
        # Generate strategies
        for strategy_type in strategy_types[:self.max_parallel_tests]:
            strategy_config = self.strategy_generators[strategy_type](objective, context)
            strategy_name = f"{strategy_type.value}_{int(time.time() * 1000) % 10000}"
            strategies[strategy_name] = strategy_config
        
        return strategies
    
    def _generate_conservative_strategy(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia conservadora - foca em estabilidade"""
        return {
            "type": StrategyType.CONSERVATIVE,
            "approach": "incremental",
            "validation_level": "high",
            "risk_tolerance": "low",
            "timeout_multiplier": 1.5,
            "retry_attempts": 3,
            "rollback_enabled": True,
            "test_coverage_required": 0.8,
            "parameters": {
                "max_changes_per_iteration": 1,
                "validation_intensity": "high",
                "safety_checks": "enabled",
                "backup_before_changes": True
            }
        }
    
    def _generate_aggressive_strategy(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia agressiva - foca em velocidade"""
        return {
            "type": StrategyType.AGGRESSIVE,
            "approach": "rapid",
            "validation_level": "medium",
            "risk_tolerance": "high",
            "timeout_multiplier": 0.7,
            "retry_attempts": 1,
            "rollback_enabled": False,
            "test_coverage_required": 0.5,
            "parameters": {
                "max_changes_per_iteration": 5,
                "validation_intensity": "medium",
                "safety_checks": "minimal",
                "parallel_execution": True
            }
        }
    
    def _generate_balanced_strategy(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia balanceada - meio termo"""
        return {
            "type": StrategyType.BALANCED,
            "approach": "moderate",
            "validation_level": "medium",
            "risk_tolerance": "medium",
            "timeout_multiplier": 1.0,
            "retry_attempts": 2,
            "rollback_enabled": True,
            "test_coverage_required": 0.65,
            "parameters": {
                "max_changes_per_iteration": 3,
                "validation_intensity": "medium",
                "safety_checks": "standard",
                "adaptive_timeout": True
            }
        }
    
    def _generate_experimental_strategy(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia experimental - testa abordagens inovadoras"""
        return {
            "type": StrategyType.EXPERIMENTAL,
            "approach": "innovative",
            "validation_level": "medium",
            "risk_tolerance": "high",
            "timeout_multiplier": 1.2,
            "retry_attempts": 2,
            "rollback_enabled": True,
            "test_coverage_required": 0.6,
            "parameters": {
                "max_changes_per_iteration": 4,
                "validation_intensity": "medium",
                "safety_checks": "standard",
                "novel_approaches": True,
                "creativity_boost": True
            }
        }
    
    def _generate_optimized_strategy(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégia otimizada baseada em performance histórica"""
        # Get best performing parameters from history
        best_params = self._get_best_historical_parameters()
        
        return {
            "type": StrategyType.OPTIMIZED,
            "approach": "data_driven",
            "validation_level": "adaptive",
            "risk_tolerance": "calculated",
            "timeout_multiplier": best_params.get("timeout_multiplier", 1.0),
            "retry_attempts": best_params.get("retry_attempts", 2),
            "rollback_enabled": True,
            "test_coverage_required": best_params.get("test_coverage", 0.7),
            "parameters": {
                "max_changes_per_iteration": best_params.get("max_changes", 3),
                "validation_intensity": best_params.get("validation_intensity", "medium"),
                "safety_checks": "intelligent",
                "performance_optimized": True,
                "historical_data_driven": True
            }
        }
    
    async def _execute_parallel_tests(self, session: ParallelTestSession) -> Optional[RealityTest]:
        """Executa testes em paralelo e monitora performance"""
        
        # Start all tests
        test_futures = {}
        for test in session.reality_tests:
            future = self.executor.submit(self._execute_single_test, test, session.objective)
            test_futures[future] = test
            test.status = RealityTestStatus.RUNNING
            test.start_time = datetime.now()
        
        self.logger.info(f"🚀 Started {len(test_futures)} parallel reality tests")
        
        # Monitor progress and select winner
        winner_test = None
        session_start = time.time()
        
        while test_futures and (time.time() - session_start) < self.max_session_time:
            # Check for completed tests
            for future in as_completed(test_futures.keys(), timeout=1):
                test = test_futures[future]
                try:
                    result = future.result()
                    test.status = RealityTestStatus.COMPLETED
                    test.end_time = datetime.now()
                    test.execution_time = (test.end_time - test.start_time).total_seconds()
                    
                    # Update test scores based on result
                    self._update_test_scores(test, result)
                    
                    self.logger.info(f"✅ Test completed: {test.strategy_name} (score: {test.composite_score:.3f})")
                    
                except Exception as e:
                    test.status = RealityTestStatus.FAILED
                    test.error_messages.append(str(e))
                    self.logger.warning(f"❌ Test failed: {test.strategy_name} - {e}")
                
                del test_futures[future]
            
            # Check if we should terminate early based on clear winner
            if self._should_terminate_early(session):
                self.logger.info("🏁 Early termination triggered - clear winner detected")
                break
            
            # Check for winner every interval
            current_winner = self._get_current_winner(session)
            if current_winner and current_winner != winner_test:
                winner_test = current_winner
                self.logger.info(f"🏆 New leader: {winner_test.strategy_name} (score: {winner_test.composite_score:.3f})")
            
            await asyncio.sleep(1)  # Small delay to prevent busy waiting
        
        # Cancel remaining tests if we terminated early
        for future in test_futures.keys():
            future.cancel()
            test_futures[future].status = RealityTestStatus.TERMINATED_EARLY
        
        # Select final winner
        final_winner = self._get_current_winner(session)
        if final_winner:
            final_winner.status = RealityTestStatus.WINNER
        
        return final_winner
    
    def _execute_single_test(self, test: RealityTest, objective: str) -> Dict[str, Any]:
        """Executa um teste individual (mock implementation)"""
        try:
            # Simulate execution time based on strategy
            base_time = 5 + (hash(objective) % 10)
            time_multiplier = test.strategy_config.get("timeout_multiplier", 1.0)
            execution_time = base_time * time_multiplier
            
            # Simulate progress
            for i in range(int(execution_time)):
                if self.should_stop.is_set():
                    break
                
                time.sleep(1)
                
                # Add intermediate result
                progress = (i + 1) / execution_time
                test.intermediate_results.append({
                    "timestamp": datetime.now().isoformat(),
                    "progress": progress,
                    "status": "executing",
                    "partial_score": progress * 0.8
                })
            
            # Simulate final result based on strategy characteristics
            strategy_type = test.strategy_type
            success_base = {
                StrategyType.CONSERVATIVE: 0.8,
                StrategyType.AGGRESSIVE: 0.6,
                StrategyType.BALANCED: 0.75,
                StrategyType.EXPERIMENTAL: 0.65,
                StrategyType.OPTIMIZED: 0.85
            }.get(strategy_type, 0.7)
            
            # Add some randomness
            import random
            success_probability = min(1.0, success_base + random.uniform(-0.2, 0.2))
            
            return {
                "success": success_probability > 0.5,
                "success_probability": success_probability,
                "quality_score": success_probability * 0.9,
                "efficiency_score": 1.0 / time_multiplier * 0.8,
                "execution_time": execution_time,
                "resource_usage": {
                    "cpu": random.uniform(0.1, 0.8),
                    "memory": random.uniform(0.1, 0.6),
                    "io": random.uniform(0.1, 0.4)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error executing test {test.test_id}: {e}")
            raise
    
    def _update_test_scores(self, test: RealityTest, result: Dict[str, Any]):
        """Atualiza scores do teste baseado no resultado"""
        test.success_probability = result.get("success_probability", 0.0)
        test.quality_score = result.get("quality_score", 0.0)
        test.efficiency_score = result.get("efficiency_score", 0.0)
        test.risk_score = 1.0 - test.success_probability  # Higher failure = higher risk
        test.resource_usage = result.get("resource_usage", {})
        
        # Calculate composite score
        test.calculate_composite_score()
    
    def _should_terminate_early(self, session: ParallelTestSession) -> bool:
        """Determina se deve terminar testes antecipadamente"""
        completed_tests = [t for t in session.reality_tests if t.status == RealityTestStatus.COMPLETED]
        
        if len(completed_tests) < 2:
            return False
        
        # Check if there's a clear winner (score difference > threshold)
        scores = [t.composite_score for t in completed_tests]
        if len(scores) >= 2:
            best_score = max(scores)
            second_best = sorted(scores, reverse=True)[1]
            
            if best_score - second_best > self.early_termination_threshold:
                return True
        
        return False
    
    def _get_current_winner(self, session: ParallelTestSession) -> Optional[RealityTest]:
        """Obtém o teste com melhor performance atual"""
        completed_tests = [t for t in session.reality_tests if t.status in [RealityTestStatus.COMPLETED, RealityTestStatus.RUNNING]]
        
        if not completed_tests:
            return None
        
        # Find test with highest composite score
        best_test = max(completed_tests, key=lambda t: t.composite_score)
        return best_test
    
    def _assess_objective_complexity(self, objective: str) -> float:
        """Avalia complexidade do objetivo (0.0 = simples, 1.0 = muito complexo)"""
        complexity_indicators = [
            ("refactor", 0.3),
            ("complex", 0.2),
            ("multiple", 0.2),
            ("comprehensive", 0.3),
            ("large", 0.2),
            ("split", 0.2),
            ("modularize", 0.3),
            ("parallel", 0.2),
            ("concurrent", 0.3),
            ("async", 0.2)
        ]
        
        objective_lower = objective.lower()
        complexity = 0.0
        
        for indicator, weight in complexity_indicators:
            if indicator in objective_lower:
                complexity += weight
        
        # Length-based complexity
        if len(objective) > 200:
            complexity += 0.2
        elif len(objective) > 100:
            complexity += 0.1
        
        return min(1.0, complexity)
    
    def _get_best_historical_parameters(self) -> Dict[str, Any]:
        """Obtém melhores parâmetros baseado em histórico"""
        # Default parameters if no history
        defaults = {
            "timeout_multiplier": 1.0,
            "retry_attempts": 2,
            "test_coverage": 0.7,
            "max_changes": 3,
            "validation_intensity": "medium"
        }
        
        # TODO: Implement actual historical analysis
        return defaults
    
    def _learn_from_session(self, session: ParallelTestSession):
        """Aprende com a sessão de teste para melhorar futuras decisões"""
        learning_insights = []
        
        # Analyze strategy performance
        strategy_scores = {}
        for test in session.reality_tests:
            strategy_type = test.strategy_type.value
            if strategy_type not in strategy_scores:
                strategy_scores[strategy_type] = []
            strategy_scores[strategy_type].append(test.composite_score)
        
        # Find best performing strategy type
        avg_scores = {k: sum(v)/len(v) for k, v in strategy_scores.items()}
        best_strategy = max(avg_scores, key=avg_scores.get)
        
        learning_insights.append(f"Best strategy type: {best_strategy} (avg score: {avg_scores[best_strategy]:.3f})")
        
        # Update strategy performance history
        for strategy_type, scores in strategy_scores.items():
            if strategy_type not in self.strategy_performance_history:
                self.strategy_performance_history[strategy_type] = []
            self.strategy_performance_history[strategy_type].extend(scores)
            
            # Keep only recent history (last 100 results)
            self.strategy_performance_history[strategy_type] = self.strategy_performance_history[strategy_type][-100:]
        
        session.learning_insights = learning_insights
        
        self.logger.info(f"📚 Learning insights: {'; '.join(learning_insights)}")
    
    def _save_session_results(self, session: ParallelTestSession):
        """Salva resultados da sessão"""
        try:
            results_dir = Path("data/parallel_tests/results")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            session_file = results_dir / f"session_{session.session_id}.json"
            
            session_data = {
                "session_id": session.session_id,
                "objective": session.objective,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "winner_test_id": session.winner_test_id,
                "session_status": session.session_status,
                "reality_tests": [test.to_dict() for test in session.reality_tests],
                "learning_insights": session.learning_insights,
                "comparison_matrix": session.comparison_matrix
            }
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"💾 Session results saved: {session_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save session results: {e}")
    
    def _load_historical_data(self):
        """Carrega dados históricos de performance"""
        try:
            history_file = Path("data/parallel_tests/strategy_performance_history.json")
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.strategy_performance_history = data.get("strategy_performance_history", {})
                    self.comparison_history = data.get("comparison_history", [])
                
                self.logger.info(f"📂 Loaded historical data: {len(self.strategy_performance_history)} strategy types")
        except Exception as e:
            self.logger.warning(f"Could not load historical data: {e}")
    
    def _start_monitoring(self):
        """Inicia thread de monitoramento"""
        if self.monitoring_thread is None or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
    
    def _monitoring_loop(self):
        """Loop de monitoramento em background"""
        while not self.should_stop.wait(30):  # Check every 30 seconds
            try:
                # Clean up old sessions
                self._cleanup_old_sessions()
                
                # Save performance history
                self._save_performance_history()
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    def _cleanup_old_sessions(self):
        """Remove sessões antigas da memória"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=1)  # Keep sessions for 1 hour
        
        sessions_to_remove = []
        for session_id, session in self.active_sessions.items():
            if session.end_time and session.end_time < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
        
        if sessions_to_remove:
            self.logger.debug(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")
    
    def _save_performance_history(self):
        """Salva histórico de performance"""
        try:
            history_file = Path("data/parallel_tests/strategy_performance_history.json")
            history_file.parent.mkdir(parents=True, exist_ok=True)
            
            history_data = {
                "strategy_performance_history": self.strategy_performance_history,
                "comparison_history": self.comparison_history[-100:],  # Keep last 100
                "last_updated": datetime.now().isoformat()
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save performance history: {e}")
    
    def get_strategy_performance_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance das estratégias"""
        summary = {}
        
        for strategy_type, scores in self.strategy_performance_history.items():
            if scores:
                summary[strategy_type] = {
                    "average_score": sum(scores) / len(scores),
                    "best_score": max(scores),
                    "worst_score": min(scores),
                    "total_tests": len(scores),
                    "recent_trend": "improving" if len(scores) >= 5 and scores[-5:] > scores[:-5] else "stable"
                }
        
        return summary
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status do sistema"""
        return {
            "active_sessions": len(self.active_sessions),
            "strategy_types_tested": len(self.strategy_performance_history),
            "total_comparisons": len(self.comparison_history),
            "max_parallel_tests": self.max_parallel_tests,
            "early_termination_threshold": self.early_termination_threshold,
            "monitoring_active": self.monitoring_thread.is_alive() if self.monitoring_thread else False
        }
    
    def shutdown(self):
        """Encerra o sistema gracefully"""
        self.logger.info("🛑 Shutting down Parallel Reality Testing System...")
        
        self.should_stop.set()
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.executor.shutdown(wait=True)
        
        # Save final state
        self._save_performance_history()
        
        self.logger.info("✅ Parallel Reality Testing System shutdown complete")

# Singleton instance
_parallel_reality_tester = None

def get_parallel_reality_tester(config: Dict[str, Any], logger: logging.Logger) -> ParallelRealityTester:
    """Get singleton instance of ParallelRealityTester"""
    global _parallel_reality_tester
    if _parallel_reality_tester is None:
        _parallel_reality_tester = ParallelRealityTester(config, logger)
    return _parallel_reality_tester