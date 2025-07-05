"""
Optimized Pipeline for Hephaestus - Implements parallel processing, intelligent caching, and advanced monitoring
"""

import asyncio
import time
import hashlib
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor
import threading
import traceback

from agent.agents import ArchitectAgent, MaestroAgent, CodeReviewAgent
from agent.utils.intelligent_cache import IntelligentCache
from agent.patch_applicator import apply_patches
from agent.validation_steps import get_validation_step, ValidationStep


@dataclass
class PipelineStage:
    """Represents a stage in the optimized pipeline"""
    name: str
    dependencies: List[str]
    executor: Any
    timeout: float = 30.0
    parallel: bool = False


@dataclass
class PipelineResult:
    """Result of a pipeline execution"""
    success: bool
    stage_results: Dict[str, Any]
    total_time: float
    cache_hits: int
    cache_misses: int
    errors: List[str]


class PipelineCache:
    """Intelligent cache for pipeline operations"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = IntelligentCache(max_size=max_size, default_ttl=ttl)
        self.sandbox_cache = {}
        self.validation_cache = {}
        
    def get_sandbox_cache(self, objective_hash: str) -> Optional[str]:
        """Get cached sandbox for similar objectives"""
        return self.sandbox_cache.get(objective_hash)
    
    def set_sandbox_cache(self, objective_hash: str, sandbox_path: str):
        """Cache sandbox path for reuse"""
        self.sandbox_cache[objective_hash] = sandbox_path
    
    def get_validation_cache(self, patches_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached validation results"""
        return self.validation_cache.get(patches_hash)
    
    def set_validation_cache(self, patches_hash: str, result: Dict[str, Any]):
        """Cache validation results"""
        self.validation_cache[patches_hash] = result
    
    def get_model_cache(self, prompt_hash: str) -> Optional[str]:
        """Get cached LLM response"""
        return self.cache.get(prompt_hash)
    
    def set_model_cache(self, prompt_hash: str, response: str):
        """Cache LLM response"""
        self.cache.set(prompt_hash, response)


class OptimizedPipeline:
    """Optimized pipeline with parallel processing and intelligent caching"""
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.cache = PipelineCache()
        self.metrics = PipelineMetrics()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize agents
        self.architect = ArchitectAgent(
            model_config=config.get("models", {}).get("architect_default"),
            logger=logger.getChild("ArchitectAgent")
        )
        
        self.maestro = MaestroAgent(
            model_config=config.get("models", {}).get("maestro_default"),
            config=config,
            logger=logger.getChild("MaestroAgent")
        )
        
        self.code_reviewer = CodeReviewAgent(
            model_config=config.get("models", {}).get("code_review_default"),
            logger=logger.getChild("CodeReviewAgent")
        )
        
        # Define pipeline stages
        self.stages = self._define_pipeline_stages()
        
        self.logger.info("🚀 OptimizedPipeline initialized with parallel processing and intelligent caching")
    
    def _define_pipeline_stages(self) -> Dict[str, PipelineStage]:
        """Define the optimized pipeline stages"""
        return {
            "analysis": PipelineStage(
                name="analysis",
                dependencies=[],
                executor=self._run_parallel_analysis,
                timeout=45.0,
                parallel=True
            ),
            "decision": PipelineStage(
                name="decision",
                dependencies=["analysis"],
                executor=self._run_decision_phase,
                timeout=30.0,
                parallel=False
            ),
            "validation": PipelineStage(
                name="validation",
                dependencies=["decision"],
                executor=self._run_parallel_validation,
                timeout=60.0,
                parallel=True
            ),
            "application": PipelineStage(
                name="application",
                dependencies=["validation"],
                executor=self._run_application_phase,
                timeout=30.0,
                parallel=False
            )
        }
    
    async def execute_pipeline(self, objective: str, context: Dict[str, Any]) -> PipelineResult:
        """Execute the optimized pipeline"""
        start_time = time.time()
        stage_results = {}
        errors = []
        cache_hits = 0
        cache_misses = 0
        
        try:
            # Stage 1: Parallel Analysis
            self.logger.info("🔄 Stage 1: Parallel Analysis")
            analysis_result = await self._run_parallel_analysis(objective, context)
            stage_results["analysis"] = analysis_result
            
            if not analysis_result["success"]:
                errors.append(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
                return PipelineResult(False, stage_results, time.time() - start_time, cache_hits, cache_misses, errors)
            
            # Stage 2: Decision
            self.logger.info("🎯 Stage 2: Decision")
            decision_result = await self._run_decision_phase(objective, context, analysis_result)
            stage_results["decision"] = decision_result
            
            if not decision_result["success"]:
                errors.append(f"Decision failed: {decision_result.get('error', 'Unknown error')}")
                return PipelineResult(False, stage_results, time.time() - start_time, cache_hits, cache_misses, errors)
            
            # Stage 3: Parallel Validation
            self.logger.info("✅ Stage 3: Parallel Validation")
            validation_result = await self._run_parallel_validation(objective, context, decision_result)
            stage_results["validation"] = validation_result
            
            if not validation_result["success"]:
                errors.append(f"Validation failed: {validation_result.get('error', 'Unknown error')}")
                return PipelineResult(False, stage_results, time.time() - start_time, cache_hits, cache_misses, errors)
            
            # Stage 4: Application
            self.logger.info("🚀 Stage 4: Application")
            application_result = await self._run_application_phase(objective, context, validation_result)
            stage_results["application"] = application_result
            
            if not application_result["success"]:
                errors.append(f"Application failed: {application_result.get('error', 'Unknown error')}")
                return PipelineResult(False, stage_results, time.time() - start_time, cache_hits, cache_misses, errors)
            
            total_time = time.time() - start_time
            self.metrics.record_pipeline_execution(total_time, True)
            
            return PipelineResult(True, stage_results, total_time, cache_hits, cache_misses, errors)
            
        except Exception as e:
            total_time = time.time() - start_time
            errors.append(f"Pipeline execution failed: {str(e)}")
            self.metrics.record_pipeline_execution(total_time, False)
            return PipelineResult(False, stage_results, total_time, cache_hits, cache_misses, errors)
    
    async def _run_parallel_analysis(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run architect and code review in parallel"""
        start_time = time.time()
        
        try:
            # Check cache first
            objective_hash = hashlib.md5(objective.encode()).hexdigest()
            cached_result = self.cache.get_model_cache(objective_hash)
            
            if cached_result:
                self.logger.info("📦 Using cached analysis result")
                return {
                    "success": True,
                    "cached": True,
                    "result": json.loads(cached_result),
                    "execution_time": 0.1
                }
            
            # Run architect and code review in parallel
            loop = asyncio.get_event_loop()
            
            architect_task = loop.run_in_executor(
                self.executor,
                self._run_architect_sync,
                objective,
                context
            )
            
            code_review_task = loop.run_in_executor(
                self.executor,
                self._run_code_review_sync,
                objective,
                context
            )
            
            # Wait for both to complete
            architect_result, code_review_result = await asyncio.gather(
                architect_task, code_review_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(architect_result, Exception):
                return {"success": False, "error": f"Architect failed: {str(architect_result)}"}
            
            if isinstance(code_review_result, Exception):
                return {"success": False, "error": f"Code review failed: {str(code_review_result)}"}
            
            # Combine results
            combined_result = {
                "architect": architect_result,
                "code_review": code_review_result,
                "execution_time": time.time() - start_time
            }
            
            # Cache the result
            self.cache.set_model_cache(objective_hash, json.dumps(combined_result))
            
            return {
                "success": True,
                "cached": False,
                "result": combined_result,
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": time.time() - start_time}
    
    def _run_architect_sync(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous architect execution"""
        try:
            action_plan_data, error_msg = self.architect.plan_action(
                objective=objective,
                manifest=context.get("manifest", ""),
                file_content_context=context.get("file_content", "")
            )
            
            return {
                "success": bool(not error_msg and action_plan_data),
                "action_plan": action_plan_data,
                "error": error_msg
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_code_review_sync(self, objective: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous code review execution"""
        try:
            # This would be called after architect generates patches
            # For now, return a placeholder
            return {
                "success": True,
                "review_passed": True,
                "feedback": ""
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _run_decision_phase(self, objective: str, context: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run maestro decision phase"""
        start_time = time.time()
        
        try:
            action_plan_data = analysis_result["result"]["architect"]["action_plan"]
            
            # Run maestro with fallback
            loop = asyncio.get_event_loop()
            maestro_result = await loop.run_in_executor(
                self.executor,
                self._run_maestro_sync,
                action_plan_data,
                context
            )
            
            return {
                "success": maestro_result["success"],
                "strategy": maestro_result.get("strategy"),
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": time.time() - start_time}
    
    def _run_maestro_sync(self, action_plan_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous maestro execution with fallback"""
        try:
            maestro_logs = self.maestro.choose_strategy(
                action_plan_data=action_plan_data,
                memory_summary=context.get("memory_summary", ""),
                failed_strategy_context=context.get("failed_strategy_context")
            )
            
            # Find successful attempt
            successful_attempt = next((log for log in maestro_logs if log.get("success")), None)
            
            if successful_attempt:
                return {
                    "success": True,
                    "strategy": successful_attempt["parsed_json"]["strategy_key"],
                    "reasoning": successful_attempt["parsed_json"].get("reasoning", "")
                }
            else:
                return {
                    "success": False,
                    "error": "No successful strategy selection"
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _run_parallel_validation(self, objective: str, context: Dict[str, Any], decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run validation steps in parallel"""
        start_time = time.time()
        try:
            # Prepare validation steps
            steps = ["syntax", "json_syntax", "pytest", "benchmark"]
            patches = decision_result.get("patches", [])
            context = dict(context)
            context["patches"] = patches
            patches_hash = hashlib.md5(json.dumps(patches, sort_keys=True).encode()).hexdigest()
            cached_validation = self.cache.get_validation_cache(patches_hash)
            if cached_validation:
                self.logger.info("📦 Using cached validation result")
                return {
                    "success": True,
                    "cached": True,
                    "result": cached_validation,
                    "execution_time": 0.1
                }
            # Run validation steps in parallel
            loop = asyncio.get_event_loop()
            validation_tasks = []
            for step_name in steps:
                task = loop.run_in_executor(
                    self.executor,
                    self._run_validation_step_sync,
                    step_name,
                    context
                )
                validation_tasks.append((step_name, task))
            # Wait for all validations to complete
            validation_results = {}
            for step_name, task in validation_tasks:
                try:
                    result = await task
                    validation_results[step_name] = result
                except Exception as e:
                    tb = traceback.format_exc()
                    self.logger.error(f"Validation step '{step_name}' failed with exception: {e}\n{tb}")
                    validation_results[step_name] = {"success": False, "error": str(e), "traceback": tb}
            # Check if all validations passed
            all_passed = all(result.get("success", False) for result in validation_results.values())
            validation_result = {
                "all_passed": all_passed,
                "step_results": validation_results,
                "execution_time": time.time() - start_time
            }
            # Cache the result
            self.cache.set_validation_cache(patches_hash, validation_result)
            # Log all validation results
            for step, res in validation_results.items():
                if not res.get("success", True):
                    self.logger.error(f"Validation step '{step}' failed: {res}")
            return {
                "success": all_passed,
                "cached": False,
                "result": validation_result,
                "execution_time": time.time() - start_time
            }
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"Pipeline validation failed with exception: {e}\n{tb}")
            return {"success": False, "error": str(e), "traceback": tb, "execution_time": time.time() - start_time}
    
    def _run_validation_step_sync(self, step_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronous validation step execution"""
        try:
            validation_step_class: Any = get_validation_step(step_name)
            if validation_step_class:
                step_instance = validation_step_class(
                    logger=self.logger,
                    base_path=Path("."),
                    patches_to_apply=context.get("patches", []),
                    use_sandbox=False
                )
                
                success, reason, details = step_instance.execute()
                
                return {
                    "success": success,
                    "reason": reason,
                    "details": details
                }
            else:
                return {"success": False, "error": f"Validation step '{step_name}' not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _run_application_phase(self, objective: str, context: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run application phase"""
        start_time = time.time()
        
        try:
            if not validation_result["result"]["all_passed"]:
                return {"success": False, "error": "Validation failed", "execution_time": time.time() - start_time}
            
            # Apply patches
            loop = asyncio.get_event_loop()
            application_result = await loop.run_in_executor(
                self.executor,
                self._apply_patches_sync,
                context.get("patches", [])
            )
            
            return {
                "success": application_result["success"],
                "applied_files": application_result.get("applied_files", []),
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "execution_time": time.time() - start_time}
    
    def _apply_patches_sync(self, patches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronous patch application"""
        try:
            success = apply_patches(patches, self.logger)
            
            return {
                "success": success,
                "applied_files": [patch.get("file_path", "unknown") for patch in patches] if success else []
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics"""
        return self.metrics.get_metrics()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            "model_cache_size": len(self.cache.cache.cache),
            "sandbox_cache_size": len(self.cache.sandbox_cache),
            "validation_cache_size": len(self.cache.validation_cache),
            "total_cache_hits": self.metrics.cache_hits,
            "total_cache_misses": self.metrics.cache_misses,
            "cache_hit_rate": self.metrics.cache_hit_rate
        }


class PipelineMetrics:
    """Advanced metrics tracking for pipeline performance"""
    
    def __init__(self):
        self.execution_times = []
        self.success_count = 0
        self.failure_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.stage_times = {
            "analysis": [],
            "decision": [],
            "validation": [],
            "application": []
        }
        self.lock = threading.Lock()
    
    def record_pipeline_execution(self, execution_time: float, success: bool):
        """Record pipeline execution metrics"""
        with self.lock:
            self.execution_times.append(execution_time)
            if success:
                self.success_count += 1
            else:
                self.failure_count += 1
    
    def record_stage_execution(self, stage: str, execution_time: float):
        """Record stage execution time"""
        with self.lock:
            if stage in self.stage_times:
                self.stage_times[stage].append(execution_time)
    
    def record_cache_hit(self):
        """Record cache hit"""
        with self.lock:
            self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        with self.lock:
            self.cache_misses += 1
    
    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics"""
        with self.lock:
            total_executions = len(self.execution_times)
            avg_execution_time = sum(self.execution_times) / total_executions if total_executions > 0 else 0
            success_rate = self.success_count / total_executions if total_executions > 0 else 0
            
            stage_metrics = {}
            for stage, times in self.stage_times.items():
                stage_metrics[stage] = {
                    "avg_time": sum(times) / len(times) if times else 0,
                    "count": len(times),
                    "min_time": min(times) if times else 0,
                    "max_time": max(times) if times else 0
                }
            
            return {
                "total_executions": total_executions,
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "cache_hit_rate": self.cache_hit_rate,
                "stage_metrics": stage_metrics,
                "recent_executions": self.execution_times[-10:] if self.execution_times else []
            } 