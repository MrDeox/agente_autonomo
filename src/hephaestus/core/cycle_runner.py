from __future__ import annotations

import csv
import json
import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Any
from pathlib import Path

from hephaestus.utils.project_scanner import update_project_manifest
from hephaestus.core.objective_generator import generate_next_objective
from hephaestus.intelligence.predictive_failure_engine import get_predictive_failure_engine
from hephaestus.core.brain import (
    generate_capacitation_objective,
    generate_commit_message,
)
from hephaestus.utils.tool_executor import run_git_command, list_available_models
from hephaestus.agents import LinterAgent
# TODO: Add these agents to the new structure
# from hephaestus.agents.prompt_optimizer import PromptOptimizer
# from hephaestus.agents.error_analyzer import ErrorAnalysisAgent
from hephaestus.services.validation import get_validation_step
from hephaestus.services.orchestration.async_orchestrator import AgentTask, AgentType, AgentResult

if TYPE_CHECKING:
    from hephaestus.core.agent import HephaestusAgent

from hephaestus.utils.queue_manager import QueueManager

class CycleRunner:
    """Manages the main asynchronous execution loop of the Hephaestus agent."""

    def __init__(self, agent: "HephaestusAgent", queue_manager: QueueManager):
        self.agent = agent
        self.queue_manager = queue_manager
        self.cycle_count = 0

    async def _get_next_objective(self) -> Optional[Any]:
        """Gets the next objective. Returns objective data or None to stop."""
        if self.agent.objective_stack:
            return self.agent.objective_stack.pop()

        if not self.queue_manager.is_empty():
            objective_data = self.queue_manager.get_objective()
            self.agent.logger.info(f"Objective transferred from queue to stack: {objective_data}")
            return objective_data

        if self.agent.continuous_mode:
            self.agent.logger.info("Continuous mode: Generating new objective.")
            # Assuming generate_next_objective is a blocking, CPU/IO-bound function
            loop = asyncio.get_running_loop()
            new_objective = await loop.run_in_executor(
                None,  # Use default executor
                generate_next_objective,
                self.agent.config.get("models", {}).get("objective_generator"),
                self.agent.state.manifesto_content or "",
                self.agent.logger,
                ".",
                self.agent.config,
                self.agent.memory,
                self.agent.model_optimizer
            )
            self.agent.logger.info(f"New objective for continuous mode: {new_objective}")
            delay = self.agent.config.get("continuous_mode_delay_seconds", 5)
            await asyncio.sleep(delay)
            return new_objective

        self.agent.logger.info("Objective stack empty, continuous mode disabled. Shutting down.")
        return None

    def _is_degenerative_loop(self, objective: str) -> bool:
        """Checks if the objective has failed too many times consecutively."""
        threshold = self.agent.config.get("degenerative_loop_threshold", 3)
        # Check for any degenerative failure pattern by looking at recent failures
        # We'll check for the most common failure reasons
        common_failure_reasons = ["ARCHITECT_PHASE_FAILED", "MAESTRO_PHASE_FAILED", "VALIDATION_FAILED", "TIMEOUT"]
        
        for reason in common_failure_reasons:
            if self.agent.memory.has_degenerative_failure_pattern(objective, reason, threshold=threshold):
                return True
        
        # Also check for generic pattern with empty reason
        return self.agent.memory.has_degenerative_failure_pattern(objective, "GENERAL_FAILURE", threshold=threshold)

    async def _run_special_task(self, task_data: dict):
        """Dispatches and runs special tasks like log analysis, linting, etc."""
        task_type = task_data.get("task_type")
        self.agent.logger.info(f"Handling special task: {task_type}")
        
        # This can be expanded to a more formal dispatcher pattern
        if task_type == "log_analysis":
            await self._run_log_analysis_task(task_data)
        elif task_type == "linter":
            await self._run_linter_task()
        # Add other special tasks here
        else:
            self.agent.logger.warning(f"Unknown special task type: {task_type}")

    async def _run_log_analysis_task(self, task_data: dict):
        """Runs a log analysis task using the orchestrator."""
        log_task = AgentTask(
            agent_type=AgentType.LOG_ANALYSIS,
            task_id=f"log_analysis_{int(datetime.now().timestamp())}",
            objective=task_data.get("objective", "Analyze system logs"),
            context=task_data.get("context", {})
        )
        await self.agent.async_orchestrator.submit_parallel_tasks([log_task])
        result = self.agent.async_orchestrator.completed_tasks.get(log_task.task_id)
        if result and result.success and result.result.get("suggested_objective"):
            new_obj = result.result["suggested_objective"]
            self.agent.logger.info(f"Log Analysis suggested new objective: {new_obj}")
            self.queue_manager.put_objective(new_obj)

    async def _run_linter_task(self):
        """Runs the linter agent to find and queue a new objective."""
        linter = LinterAgent(self.agent.logger.getChild("LinterAgent"))
        # Assuming run_linter_and_propose_objective is sync/blocking
        loop = asyncio.get_running_loop()
        new_objective = await loop.run_in_executor(None, linter.run_linter_and_propose_objective)
        if new_objective:
            self.agent.logger.info("Linter Agent proposed a new objective.")
            self.queue_manager.put_objective(new_objective)

    async def _run_single_cycle(self, current_objective: Any):
        """Executes the full logic for a single evolutionary cycle using a staged async pipeline."""
        if isinstance(current_objective, dict) and "task_type" in current_objective:
            await self._run_special_task(current_objective)
            return

        objective_str = str(current_objective)
        self.agent._reset_cycle_state()
        self.agent.state.current_objective = objective_str
        
        # 🔮 Track cycle start time for learning
        self.agent.state.cycle_start_time = datetime.now()

        if not self.agent._generate_manifest():
            self._handle_cycle_failure(objective_str, "MANIFEST_GENERATION_FAILED", "Could not generate project manifest.")
            return

        if not self.agent._gather_information_phase():
            self._handle_cycle_failure(objective_str, "INFORMATION_GATHERING_FAILED", "Could not read file context.")
            return

        try:
            # Stage 1: Parallel execution of Architect and Bug Hunter
            architect_result = await self._run_architect_stage(objective_str)
            if not architect_result or not architect_result.success:
                reason = architect_result.error_message if architect_result else "Architect task failed to produce a result."
                self._handle_cycle_failure(objective_str, "ARCHITECT_PHASE_FAILED", reason)
                return

            action_plan = architect_result.result
            self.agent.state.action_plan_data = action_plan

            # Stage 2: Parallel execution of Code Review and Maestro
            maestro_result, review_result = await self._run_strategy_stage(objective_str, action_plan)
            
            if review_result and not review_result.success:
                self.agent.logger.warning(f"Code review failed: {review_result.error_message}. Proceeding with Maestro's strategy but this is a risk.")

            if not maestro_result or not maestro_result.success:
                reason = maestro_result.error_message if maestro_result else "Maestro task failed to produce a result."
                self._handle_cycle_failure(objective_str, "MAESTRO_PHASE_FAILED", reason)
                return

            self.agent.state.strategy_key = maestro_result.result.get("strategy")

            # Stage 3: Synchronous validation and application logic
            self._run_validation_and_application(objective_str)

        except Exception as e:
            self.agent.logger.error(f"Asynchronous pipeline execution failed: {e}", exc_info=True)
            self._handle_cycle_failure(objective_str, "ASYNC_PIPELINE_ERROR", str(e))

    async def _run_architect_stage(self, objective: str) -> Optional[AgentResult]:
        """Runs the architect and bug hunter tasks in parallel."""
        self.agent.logger.info("Pipeline Stage 1: Running Architect and Bug Hunter.")
        base_context = {
            "manifest": self.agent.state.manifesto_content or "",
            "file_content_context": getattr(self.agent.state, 'file_content_context', ''),
            "memory_summary": self.agent.memory.get_full_history_for_prompt(),
            "project_path": "."
        }
        
        architect_task = AgentTask(
            agent_type=AgentType.ARCHITECT,
            task_id=f"architect_{self.cycle_count}",
            objective=f"Generate solution patches for: {objective}",
            context=base_context, priority=10
        )
        bug_hunter_task = AgentTask(
            agent_type=AgentType.BUG_HUNTER,
            task_id=f"bug_hunter_{self.cycle_count}",
            objective=f"Proactively hunt for bugs related to: {objective}",
            context=base_context, priority=8
        )

        await self.agent.async_orchestrator.submit_parallel_tasks([architect_task, bug_hunter_task])
        return self.agent.async_orchestrator.completed_tasks.get(architect_task.task_id)

    async def _run_strategy_stage(self, objective: str, action_plan: dict) -> tuple[Optional[AgentResult], Optional[AgentResult]]:
        """Runs the code review and maestro tasks in parallel."""
        self.agent.logger.info("Pipeline Stage 2: Running Code Review and Maestro.")
        review_context = {"patches_to_apply": action_plan.get("patches", [])}
        maestro_context = {"action_plan_data": action_plan, "memory_summary": self.agent.memory.get_full_history_for_prompt()}

        code_review_task = AgentTask(
            agent_type=AgentType.CODE_REVIEW,
            task_id=f"code_review_{self.cycle_count}",
            objective=f"Review patches for: {objective}",
            context=review_context, priority=9
        )
        maestro_task = AgentTask(
            agent_type=AgentType.MAESTRO,
            task_id=f"maestro_{self.cycle_count}",
            objective=f"Choose strategy for: {objective}",
            context=maestro_context, priority=8
        )

        await self.agent.async_orchestrator.submit_parallel_tasks([code_review_task, maestro_task])
        maestro_result = self.agent.async_orchestrator.completed_tasks.get(maestro_task.task_id)
        review_result = self.agent.async_orchestrator.completed_tasks.get(code_review_task.task_id)
        return maestro_result, review_result

    def _run_validation_and_application(self, current_objective: str):
        """Handles the strategy validation, retries, and application logic. This part remains synchronous."""
        max_retries = self.agent.config.get("validation_retries", 1)
        for attempt in range(max_retries):
            if self.agent.state.strategy_key == "CAPACITATION_REQUIRED":
                self._handle_capacitation_request(current_objective)
                return

            self.agent._execute_validation_strategy()
            success, reason, context = self.agent.state.validation_result

            if success:
                self.agent.logger.info(f"SUCCESS IN VALIDATION/APPLICATION! Reason: {reason}")
                self._handle_cycle_success(reason, context)
                return

            self.agent.logger.warning(f"Strategy '{self.agent.state.strategy_key}' failed. Reason: {reason}")
            # In a fully async model, re-running maestro would be another async stage.
            # For now, we fail fast if the chosen strategy doesn't work.
            break
        
        # If loop finishes without success
        reason, context = self.agent.state.validation_result
        self._handle_cycle_failure(current_objective, reason, context)

    def _handle_capacitation_request(self, current_objective: str):
        """Generates and stacks a new capacitation objective."""
        self.agent.objective_stack.append(current_objective)
        architect_analysis = self.agent.state.get_architect_analysis()
        model_config = self.agent.config.get("models", {}).get("capacitation_generator")
        capacitation_objective = generate_capacitation_objective(
            model_config=model_config,
            engineer_analysis=architect_analysis or "Analysis not available",
            logger=self.agent.logger,
            memory_summary=self.agent.memory.get_full_history_for_prompt(),
        )
        self.agent.logger.info(f"Generated new capacitation objective: {capacitation_objective}")
        self.agent.objective_stack.append(capacitation_objective)

    def _handle_cycle_success(self, reason: str, details: str):
        """Logic for a successful cycle: sanity checks, commits, and logging."""
        if not reason.startswith("APPLIED_AND_VALIDATED"):
            self.agent.logger.info(f"Cycle completed with status: {reason}. No code changes promoted.")
            return

        sanity_check_success, sanity_check_tool, sanity_details = self._run_sanity_check()
        if not sanity_check_success:
            self.agent.logger.error(f"SANITY CHECK FAILED ({sanity_check_tool})! Details: {sanity_details}")
            self._rollback_changes()
            self._handle_cycle_failure(self.agent.state.current_objective, f"REGRESSION_DETECTED_BY_{sanity_check_tool.upper()}", sanity_details)
            return

        self.agent.logger.info(f"SANITY CHECK ({sanity_check_tool}): SUCCESS!")
        if sanity_check_tool != "skip_sanity_check":
            self._commit_changes()

        self.agent.memory.add_completed_objective(
            objective=self.agent.state.current_objective,
            strategy=self.agent.state.strategy_key,
            details=f"Applied. Sanity ({sanity_check_tool}): OK. Details: {details}",
        )
        
        # 🔮 PREDICTIVE FAILURE ENGINE LEARNING
        self._learn_from_success()

    def _run_sanity_check(self) -> tuple[bool, str, str]:
        """Runs the configured sanity check step."""
        strategy_config = self.agent.config.get("validation_strategies", {}).get(self.agent.state.strategy_key, {})
        tool_name = strategy_config.get("sanity_check_step", "run_pytest")
        try:
            validation_step_class = get_validation_step(tool_name)
            step_instance = validation_step_class(logger=self.agent.logger, base_path=Path("."), patches_to_apply=self.agent.state.get_patches_to_apply(), use_sandbox=False)
            return step_instance.execute()
        except Exception as e:
            return False, tool_name, str(e)

    def _rollback_changes(self):
        """Rolls back changes in the working directory."""
        self.agent.logger.info("Rolling back changes...")
        run_git_command(['git', 'checkout', '--', '.'])

    def _commit_changes(self):
        """Commits the validated changes."""
        self.agent.logger.info("Initiating auto-commit...")
        update_project_manifest(root_dir=".", target_files=[])
        with open("docs/ARCHITECTURE.md", "r", encoding="utf-8") as f:
            self.agent.state.manifesto_content = f.read()
        analysis_summary = self.agent.state.get_architect_analysis() or "N/A"
        commit_message = generate_commit_message(analysis_summary, self.agent.state.current_objective, self.agent.logger)
        run_git_command(['git', 'add', '.'])
        run_git_command(['git', 'commit', '-m', commit_message])
        self.agent.logger.info("--- AUTO-COMMIT SUCCESSFUL ---")

    def _handle_cycle_failure(self, objective: str, reason: str, context: str):
        """Handles the logic for a failed cycle."""
        self.agent.logger.warning(f"CYCLE FAILED! Reason: {reason}\nContext: {context}")
        self.agent.memory.add_failed_objective(objective, reason, context)
        
        # 🔮 PREDICTIVE FAILURE ENGINE LEARNING
        self._learn_from_failure(objective, reason, context)

        if self._is_degenerative_loop(objective):
            self._optimize_failed_prompt(objective, reason, context)
            return

        correctable_reasons = self.agent.config.get("correctable_failure_reasons", [])
        if reason in correctable_reasons or reason.startswith("REGRESSION_DETECTED_BY_"):
            self._run_error_analysis(objective, reason, context)

    def _optimize_failed_prompt(self, objective: str, reason: str, context: str):
        """Tries to optimize the prompt for a repeatedly failing objective."""
        self.agent.logger.info(f"Optimizing prompt for objective that failed repeatedly: '{objective}'")
        # TODO: Implement PromptOptimizer in new structure
        # optimizer = PromptOptimizer(model_config=self.agent.config.get("models", {}).get("prompt_optimizer"), logger=self.agent.logger.getChild("PromptOptimizer"))
        # optimized_objective = optimizer.optimize_prompt(original_prompt=objective, failure_context=f"Reason: {reason}. Details: {context}")
        # if optimized_objective:
        #     self.agent.objective_stack.append(optimized_objective)
        self.agent.logger.warning("Prompt optimization disabled - PromptOptimizer not implemented in new structure")

    def _run_error_analysis(self, objective: str, reason: str, context: str):
        """Runs the ErrorAnalysisAgent to get a corrective objective."""
        self.agent.logger.info(f"Initiating ErrorAnalysisAgent for correctable failure: {reason}")
        # TODO: Implement ErrorAnalysisAgent in new structure
        # error_analyzer = ErrorAnalysisAgent(model_config=self.agent.config.get("models", {}).get("error_analyzer"), logger=self.agent.logger.getChild("ErrorAnalysisAgent"))
        # patches_json = json.dumps(self.agent.state.get_patches_to_apply(), indent=2)
        # analysis_result = error_analyzer.analyze_error(failed_objective=objective, error_reason=reason, error_context=context, original_patches=patches_json, capabilities_content=self.agent.state.manifesto_content or "")
        # if correction_prompt := analysis_result.get("suggested_prompt"):
        #     self.agent.objective_stack.append(objective) # Re-add original
        #     self.agent.objective_stack.append(correction_prompt)
        self.agent.logger.warning("Error analysis disabled - ErrorAnalysisAgent not implemented in new structure")

    async def run(self) -> None:
        """Execute the main evolution loop."""
        self.agent.logger.info(f"Starting HephaestusAgent. Continuous Mode: {'ON' if self.agent.continuous_mode else 'OFF'}.")
        while True:
            if self.agent.objective_stack_depth_for_testing is not None and self.cycle_count >= self.agent.objective_stack_depth_for_testing:
                self.agent.logger.info("Execution cycle limit reached. Shutting down.")
                break

            current_objective = await self._get_next_objective()
            if not current_objective:
                break

            self.cycle_count += 1
            self.agent.logger.info(f"\n\n{'='*20} START CYCLE #{self.cycle_count} {'='*20}")
            self.agent.logger.info(f"OBJECTIVE: {current_objective}\n")

            if self._is_degenerative_loop(str(current_objective)):
                self.agent.logger.error(f'Degenerative loop detected for objective. Discarding.')
                self._handle_cycle_failure(str(current_objective), "DEGENERATIVE_LOOP_DETECTED", "Objective failed too many times consecutively.")
                continue

            start_time = datetime.now()
            try:
                await self._run_single_cycle(current_objective)
            except Exception as e:
                self.agent.logger.critical(f"UNHANDLED EXCEPTION in cycle: {e}", exc_info=True)
                self._handle_cycle_failure(str(current_objective), "UNHANDLED_CYCLE_EXCEPTION", str(e))
            finally:
                self._log_cycle_completion(str(current_objective), start_time, datetime.now())
                self.agent.memory.save()
                await asyncio.sleep(self.agent.config.get("cycle_delay_seconds", 1))

        self.agent.logger.info(f"{'='*20} END OF HEPHAESTUS EXECUTION {'='*20}")
    
    def _learn_from_success(self):
        """Ensina o Predictive Failure Engine sobre sucessos"""
        try:
            predictive_engine = get_predictive_failure_engine(
                config=self.agent.config,
                logger=self.agent.logger,
                memory_path=self.agent.memory.filepath
            )
            
            # Calculate execution time (simplified)
            execution_time = 0.0
            if hasattr(self.agent.state, 'cycle_start_time'):
                execution_time = (datetime.now() - self.agent.state.cycle_start_time).total_seconds()
            
            predictive_engine.learn_from_execution(
                objective=self.agent.state.current_objective,
                success=True,
                execution_time=execution_time
            )
            
            self.agent.logger.info("🎓 Predictive engine learned from success")
            
        except Exception as e:
            self.agent.logger.warning(f"Error learning from success: {e}")
    
    def _learn_from_failure(self, objective: str, reason: str, context: str):
        """Ensina o Predictive Failure Engine sobre falhas"""
        try:
            predictive_engine = get_predictive_failure_engine(
                config=self.agent.config,
                logger=self.agent.logger,
                memory_path=self.agent.memory.filepath
            )
            
            # Calculate execution time (simplified)
            execution_time = 0.0
            if hasattr(self.agent.state, 'cycle_start_time'):
                execution_time = (datetime.now() - self.agent.state.cycle_start_time).total_seconds()
            
            predictive_engine.learn_from_execution(
                objective=objective,
                success=False,
                failure_reason=reason,
                execution_time=execution_time
            )
            
            self.agent.logger.info("🎓 Predictive engine learned from failure")
            
        except Exception as e:
            self.agent.logger.warning(f"Error learning from failure: {e}")

    def _log_cycle_completion(self, objective: str, start_time: datetime, end_time: datetime):
        """Logs the final status of the completed cycle."""
        duration = (end_time - start_time).total_seconds()
        success, reason, context = self.agent.state.validation_result
        log_entry = [self.cycle_count, objective, "success" if success else "failure", round(duration, 2), "", self.agent.state.strategy_key or "N/A", start_time.isoformat(), end_time.isoformat(), reason, context]
        try:
            with open(self.agent.evolution_log_file, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(log_entry)
        except IOError as e:
            self.agent.logger.error(f"Failed to write to evolution log: {e}")