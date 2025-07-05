from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Any
from pathlib import Path
import asyncio

from agent.project_scanner import update_project_manifest
from agent.objective_generator import generate_next_objective
from agent.brain import (
    generate_capacitation_objective,
    generate_commit_message,
)
from agent.tool_executor import run_pytest, check_file_existence, run_git_command, list_available_models
from agent.agents import ErrorAnalysisAgent, PromptOptimizer, ModelSommelierAgent
from agent.agents.debt_hunter_agent import DebtHunterAgent
from agent.agents.linter_agent import LinterAgent
from agent.validation_steps import get_validation_step

if TYPE_CHECKING:
    from agent.hephaestus_agent import HephaestusAgent

from agent.queue_manager import QueueManager

class CycleRunner:
    """Manages the main execution loop of the Hephaestus agent."""

    def __init__(self, agent: "HephaestusAgent", queue_manager: QueueManager):
        self.agent = agent
        self.queue_manager = queue_manager
        self.cycle_count = 0

    def _get_next_objective(self) -> Optional[str]:
        """
        Gets the next objective from the stack, queue, or by generating a new one.
        Returns the objective string or None if the agent should stop.
        """
        if self.agent.objective_stack:
            return self.agent.objective_stack.pop()

        if not self.queue_manager.is_empty():
            objective_data = self.queue_manager.get_objective()
            
            # Handle enhanced objective format from API
            if isinstance(objective_data, dict):
                objective_str = objective_data.get("objective", str(objective_data))
                self.agent.logger.info(f"Objective transferred from queue to stack: {objective_str}")
                self.agent.logger.debug(f"Objective metadata: {objective_data}")
                return objective_str
            else:
                # Handle simple string objective
                self.agent.logger.info(f"Objective transferred from queue to stack: {objective_data}")
                return objective_data

        if self.agent.continuous_mode:
            self.agent.logger.info(f"\\n{'='*20} CONTINUOUS MODE {'='*20}\\nObjective stack empty. Generating new objective...")
            model_config = self.agent.config.get("models", {}).get("objective_generator")
            new_objective = generate_next_objective(
                model_config=model_config,
                current_manifest=self.agent.state.manifesto_content or "",
                logger=self.agent.logger,
                project_root_dir=".",
                config=self.agent.config,
                memory=self.agent.memory,
                model_optimizer=self.agent.model_optimizer
            )
            self.agent.logger.info(f"New objective generated for continuous mode: {new_objective}")
            
            continuous_delay = self.agent.config.get("continuous_mode_delay_seconds", 5)
            self.agent.logger.info(f"Waiting {continuous_delay} seconds before next continuous cycle...")
            time.sleep(continuous_delay)
            return new_objective

        self.agent.logger.info("Objective stack empty and continuous mode disabled. Shutting down agent.")
        return None

    def _is_degenerative_loop(self, objective: str) -> bool:
        """Checks if the objective has failed too many times consecutively."""
        failure_count = 0
        threshold = self.agent.config.get("degenerative_loop_threshold", 3)
        for log_entry in reversed(self.agent.memory.recent_objectives_log):
            if log_entry["objective"] == objective:
                if log_entry["status"] == "failure":
                    failure_count += 1
                else: # Success breaks the consecutive chain
                    return False 
            if failure_count >= threshold:
                return True
        return failure_count >= threshold

    def _execute_phase_and_handle_failure(self, phase_func, failure_reason, failure_details) -> bool:
        """Executes a phase function and handles its failure."""
        if not phase_func():
            self.agent.logger.warning(f"{failure_reason}. Skipping to next objective if any.")
            if self.agent.state.current_objective:
                self.agent.memory.add_failed_objective(
                    self.agent.state.current_objective,
                    failure_reason,
                    failure_details
                )
            return False
        return True

    def _run_single_cycle(self, current_objective: Any):
        """Executes the full logic for a single evolutionary cycle."""
        
        # Handle special task types that are passed as dictionaries
        if isinstance(current_objective, dict):
            if current_objective.get("is_log_analysis_task"):
                self.agent.logger.info("Handling special task: Log Analysis.")
                self._run_log_analysis_task(current_objective)
                return
            if current_objective.get("is_debt_hunter_task"):
                self.agent.logger.info("Handling special task: Debt Hunter.")
                self._run_debt_hunter_task()
                return
            if current_objective.get("is_model_sommelier_task"):
                self.agent.logger.info("Handling special task: Model Sommelier.")
                self._run_model_sommelier_task()
                return
            if current_objective.get("is_linter_task"):
                self.agent.logger.info("Handling special task: Linter.")
                self._run_linter_task()
                return
        
        # Standard objectives are strings
        objective_str = str(current_objective)

        self.agent._reset_cycle_state()
        self.agent.state.current_objective = objective_str

        if not self._execute_phase_and_handle_failure(self.agent._generate_manifest, "MANIFEST_GENERATION_FAILED", "Could not generate project manifest."):
            return

        if not self._execute_phase_and_handle_failure(self.agent._gather_information_phase, "INFORMATION_GATHERING_FAILED", "Could not read file context for the objective."):
            return

        # Use optimized pipeline if available
        if hasattr(self.agent, 'use_optimized_pipeline') and self.agent.use_optimized_pipeline and self.agent.optimized_pipeline:
            try:
                self.agent.logger.info("🚀 Using optimized pipeline for cycle execution")
                
                # Prepare context for optimized pipeline
                context = {
                    "manifest": self.agent.state.manifesto_content or "",
                    "file_content": getattr(self.agent.state, 'file_content_context', ''),
                    "memory_summary": self.agent.memory.get_full_history_for_prompt(),
                    "patches": self.agent.state.get_patches_to_apply() if hasattr(self.agent.state, 'get_patches_to_apply') else []
                }
                
                # If no patches in state, try to get from action plan
                if not context["patches"] and hasattr(self.agent.state, 'action_plan_data') and self.agent.state.action_plan_data:
                    action_plan = self.agent.state.action_plan_data
                    if isinstance(action_plan, dict) and "patches" in action_plan:
                        context["patches"] = action_plan["patches"]
                        self.agent.logger.info(f"📦 Found {len(context['patches'])} patches in action plan")
                
                # Execute optimized pipeline
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    pipeline_result = loop.run_until_complete(
                        self.agent.optimized_pipeline.execute_pipeline(objective_str, context)
                    )
                    
                    if pipeline_result.success:
                        self.agent.state.validation_result = (True, "OPTIMIZED_PIPELINE_SUCCESS", "Pipeline completed successfully")
                        self._handle_cycle_success("OPTIMIZED_PIPELINE_COMPLETED", f"Pipeline completed in {pipeline_result.total_time:.2f}s")
                    else:
                        error_msg = "; ".join(pipeline_result.errors)
                        self.agent.state.validation_result = (False, "OPTIMIZED_PIPELINE_FAILED", error_msg)
                        self._handle_cycle_failure(objective_str, "OPTIMIZED_PIPELINE_FAILED", error_msg)
                        
                finally:
                    loop.close()
                    
                return
                
            except Exception as e:
                self.agent.logger.warning(f"Optimized pipeline failed, falling back to standard pipeline: {e}")
                # Fall back to standard pipeline
                pass

        # Standard pipeline (fallback)
        self.agent.logger.info("🔄 Using standard pipeline for cycle execution")
        
        if not self._execute_phase_and_handle_failure(self.agent._run_architect_phase, "ARCHITECT_PHASE_FAILED", "ArchitectAgent could not generate a plan."):
            return

        if not self._execute_phase_and_handle_failure(self.agent._run_code_review_phase, "CODE_REVIEW_FAILED", "CodeReviewAgent rejected the plan and architect failed to create a new one."):
            return

        is_correction_objective = any(objective_str.startswith(p) for p in ["[AUTOMATIC CORRECTION TASK]", "[CORRECTION TASK", "[REVISED OBJECTIVE", "[MODIFIED OBJECTIVE"])
        if is_correction_objective:
            self.agent.logger.info(f"Correction objective detected. Using AUTO_CORRECTION_STRATEGY.")
            self.agent.state.strategy_key = "AUTO_CORRECTION_STRATEGY"
            if "AUTO_CORRECTION_STRATEGY" not in self.agent.config.get("validation_strategies", {}):
                 self.agent.memory.add_failed_objective(objective_str, "CONFIG_ERROR", "AUTO_CORRECTION_STRATEGY missing.")
                 return
        else:
            if not self._execute_phase_and_handle_failure(self.agent._run_maestro_phase, "MAESTRO_PHASE_FAILED", "MaestroAgent could not decide on a strategy."):
                return

        self._run_validation_and_application(objective_str)

    def _run_log_analysis_task(self, task_data: dict):
        """Runs a log analysis task using the orchestrator."""
        from agent.async_orchestrator import AgentTask, AgentType
        
        details = task_data.get("task_details", {})
        context = details.get("context", {})

        log_task = AgentTask(
            agent_type=AgentType.LOG_ANALYSIS,
            task_id=f"log_analysis_{int(time.time())}",
            objective=task_data.get("objective"),
            context=context
        )

        async def run_task():
            results = await self.agent.async_orchestrator.submit_parallel_tasks([log_task])
            self.agent.logger.info(f"Log analysis task completed with result: {results}")
            # Here you could add logic to process the result, e.g., queue a new objective
            if results and self.agent.async_orchestrator.completed_tasks:
                task_result = self.agent.async_orchestrator.completed_tasks.get(results[0])
                if task_result and task_result.success:
                    analysis_output = task_result.result
                    suggested_objective = analysis_output.get("suggested_objective")
                    if suggested_objective:
                        self.agent.logger.info(f"Log Analysis suggested a new objective: {suggested_objective}")
                        self.queue_manager.put_objective(suggested_objective)

        # Run the async function in the current thread's event loop
        # Since CycleRunner runs in a sync thread, we need to manage the loop.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # No running loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(run_task())

    def _run_validation_and_application(self, current_objective: str):
        """Handles the strategy validation, retries, and application logic."""
        max_retries = 2
        success = False
        reason, context = "", ""

        for attempt in range(max_retries):
            if self.agent.state.strategy_key == "CAPACITATION_REQUIRED":
                self.agent.logger.info("Maestro identified a need for new capabilities.")
                self._handle_capacitation_request(current_objective)
                return # End cycle here, new objective is on the stack

            self.agent._execute_validation_strategy()
            success, reason, context = self.agent.state.validation_result

            if success:
                self.agent.logger.info(f"\\nSUCCESS IN VALIDATION/APPLICATION! Reason: {reason}")
                self._handle_cycle_success(reason, context)
                return

            self.agent.logger.warning(f"Strategy '{self.agent.state.strategy_key}' failed (Attempt {attempt + 1}/{max_retries}). Reason: {reason}")
            if attempt < max_retries - 1:
                if not self._rerun_maestro_on_failure(reason, context):
                    break # Maestro failed to give a new strategy
            else:
                self.agent.logger.error(f"Max retries reached. Final failure reason: {reason}")
        
        # If loop finishes without success
        if self.agent.state.current_objective:
            self._handle_cycle_failure(self.agent.state.current_objective, reason, context)

    def _rerun_maestro_on_failure(self, reason: str, context: str) -> bool:
        """Asks Maestro for a new strategy after a failure."""
        self.agent.logger.info("Requesting a new strategy from MaestroAgent.")
        failed_context = {"strategy": self.agent.state.strategy_key, "reason": reason, "details": context}
        return self.agent._run_maestro_phase(failed_strategy_context=failed_context)

    def _handle_capacitation_request(self, current_objective: str):
        """Generates and stacks a new capacitation objective."""
        self.agent.objective_stack.append(current_objective) # Re-stack original objective
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
            return # No further action needed

        sanity_check_success, sanity_check_tool, sanity_details = self._run_sanity_check()
        if not sanity_check_success:
            self.agent.logger.error(f"SANITY CHECK FAILED ({sanity_check_tool})! Details: {sanity_details}")
            self._rollback_changes()
            if self.agent.state.current_objective:
                self._handle_cycle_failure(
                    self.agent.state.current_objective,
                    f"REGRESSION_DETECTED_BY_{sanity_check_tool.upper()}",
                    sanity_details
                )
            return

        self.agent.logger.info(f"SANITY CHECK ({sanity_check_tool}): SUCCESS!")
        if sanity_check_tool != "skip_sanity_check":
            self._commit_changes()

        if self.agent.state.current_objective and self.agent.state.strategy_key:
            self.agent.memory.add_completed_objective(
                objective=self.agent.state.current_objective,
                strategy=self.agent.state.strategy_key,
                details=f"Applied. Sanity ({sanity_check_tool}): OK. Details: {details}",
            )

    def _run_sanity_check(self) -> tuple[bool, str, str]:
        """Runs the configured sanity check step and returns success, tool name, and details."""
        strategy_config = self.agent.config.get("validation_strategies", {}).get(self.agent.state.strategy_key, {})
        tool_name = strategy_config.get("sanity_check_step", "run_pytest")
        self.agent.logger.info(f"--- INITIATING POST-APPLICATION SANITY CHECK: {tool_name} ---")

        try:
            # Use the factory to get the validation step class
            validation_step_class = get_validation_step(tool_name)
            step_instance = validation_step_class(
                logger=self.agent.logger,
                base_path=Path("."), # Sanity check runs on the real project root
                patches_to_apply=self.agent.state.get_patches_to_apply(),
                use_sandbox=False, # Sanity check is post-sandbox
            )
            success, reason, details = step_instance.execute()
            return success, tool_name, details
        except (KeyError, ValueError):
             return False, tool_name, f"Unknown sanity check tool: {tool_name}"
        except Exception as e:
            self.agent.logger.error(f"An unexpected error occurred during sanity check '{tool_name}': {e}", exc_info=True)
            return False, tool_name, f"Unexpected error during sanity check: {e}"

    def _rollback_changes(self):
        """Safely rolls back changes in the working directory."""
        self.agent.logger.info("Rolling back changes in the working directory...")
        success, output = run_git_command(['git', 'checkout', '--', '.'])
        if not success:
            self.agent.logger.error(f"FAILED TO ROLLBACK CHANGES! Manual intervention may be required. Output: {output}")

    def _commit_changes(self):
        """Commits the validated changes to the repository."""
        self.agent.logger.info("Resynchronizing manifest and initiating auto-commit...")
        update_project_manifest(root_dir=".", target_files=[])
        with open("docs/ARCHITECTURE.md", "r", encoding="utf-8") as f:
            self.agent.state.manifesto_content = f.read()

        analysis_summary = self.agent.state.get_architect_analysis() or "N/A"
        if self.agent.state.current_objective:
            commit_message = generate_commit_message(analysis_summary, self.agent.state.current_objective, self.agent.logger)
            run_git_command(['git', 'add', '.'])
            commit_success, commit_output = run_git_command(['git', 'commit', '-m', commit_message])
            if not commit_success:
                self.agent.logger.error(f"CRITICAL COMMIT FAILURE: {commit_output}. Changes may not be saved.")
            else:
                self.agent.logger.info("--- AUTO-COMMIT SUCCESSFUL ---")

    def _handle_cycle_failure(self, objective: str, reason: str, context: str):
        """Handles the logic for a failed cycle, including error analysis."""
        self.agent.logger.warning(f"\\nCYCLE FAILED! Reason: {reason}\\nContext: {context}")
        self.agent.memory.add_failed_objective(objective, reason, context)

        # Check for degenerative failure pattern optimization
        if self.agent.memory.has_degenerative_failure_pattern(objective, reason):
            self._optimize_failed_prompt(objective, reason, context)
            return # Optimization attempt counts as the recovery action

        # Check for correctable failures
        correctable_reasons = {
            "PATCH_APPLICATION_FAILED", "SYNTAX_VALIDATION_FAILED", "JSON_SYNTAX_VALIDATION_FAILED",
            "PYTEST_VALIDATION_FAILED", "BENCHMARK_VALIDATION_FAILED", "PROMOTION_FAILED",
            "APPLY_PATCHES_TO_DISK_FAILED_IN_SANDBOX", "VALIDATE_SYNTAX_FAILED_IN_SANDBOX",
            "VALIDATE_JSON_SYNTAX_FAILED_IN_SANDBOX", "RUN_PYTEST_VALIDATION_FAILED_IN_SANDBOX",
            "RUN_BENCHMARK_VALIDATION_FAILED_IN_SANDBOX", "COMMIT_FAILED_POST_SANITY",
        }
        if reason.startswith("REGRESSION_DETECTED_BY_"):
            correctable_reasons.add(reason)

        if reason in correctable_reasons:
            self._run_error_analysis(objective, reason, context)

    def _optimize_failed_prompt(self, objective: str, reason: str, context: str):
        """Tries to optimize the prompt for a repeatedly failing objective."""
        self.agent.logger.warning(f"Optimizing prompt for objective that failed repeatedly: '{objective}'")
        model_config = self.agent.config.get("models", {}).get("prompt_optimizer")
        optimizer = PromptOptimizer(model_config=model_config, logger=self.agent.logger.getChild("PromptOptimizer"))
        
        optimized_objective = optimizer.optimize_prompt(
            original_prompt=objective,
            failure_context=f"The objective failed multiple times with the reason: {reason}. Details: {context}"
        )
        
        if optimized_objective:
            self.agent.logger.info(f"New optimized objective generated: {optimized_objective}")
            self.agent.objective_stack.append(optimized_objective)
        else:
            self.agent.logger.error("Failed to optimize the prompt. The objective will be discarded for now.")

    def _run_error_analysis(self, objective: str, reason: str, context: str):
        """Runs the ErrorAnalysisAgent to get a corrective objective."""
        self.agent.logger.info(f"Correctable failure ({reason}). Initiating ErrorAnalysisAgent.")
        model_config = self.agent.config.get("models", {}).get("error_analyzer")
        error_analyzer = ErrorAnalysisAgent(model_config=model_config, logger=self.agent.logger.getChild("ErrorAnalysisAgent"))
        
        patches_json = json.dumps(self.agent.state.get_patches_to_apply(), indent=2) if self.agent.state.action_plan_data else "N/A"

        # Pass the detailed error context from the validation step to the analyzer
        error_context_details = f"Validation failed with reason '{reason}'.\\n"
        error_context_details += "Error output or details:\\n"
        error_context_details += f"{context}"

        analysis_result = error_analyzer.analyze_error(
            failed_objective=objective,
            error_reason=reason,
            error_context=error_context_details, # Pass the detailed context
            original_patches=patches_json,
            capabilities_content=self.agent.state.manifesto_content or "",
            roadmap_content=""
        )
        
        correction_prompt = analysis_result.get("suggested_prompt")
        suggestion_type = analysis_result.get("suggestion_type")

        if correction_prompt and suggestion_type not in ["LOG_FOR_REVIEW", None]:
            self.agent.objective_stack.append(objective) # Re-add original objective
            self.agent.objective_stack.append(correction_prompt)
            self.agent.logger.info(f"New correction objective added to stack: '{correction_prompt[:100]}...'")

    def _run_model_sommelier_task(self):
        """Runs the model sommelier agent to propose a model optimization."""
        model_config = self.agent.config.get("models", {}).get("sommelier_default", self.agent.config.get("models", {}).get("architect_default"))
        
        sommelier = ModelSommelierAgent(
            model_config=model_config,
            config=self.agent.config,
            logger=self.agent.logger.getChild("ModelSommelierAgent")
        )

        # The Sommelier needs the performance summary
        agent_perf_summary = self.agent.model_optimizer.get_agent_performance_summary()
        
        # And the list of available models
        success, available_models = list_available_models()
        if not success:
            self.agent.logger.error("Could not retrieve available models for Model Sommelier.")
            available_models = []

        new_objective = sommelier.propose_model_optimization(
            agent_performance_summary=agent_perf_summary,
            available_models=available_models
        )
        
        if new_objective:
            self.agent.logger.info(f"Model Sommelier proposed a new objective: {new_objective}")
            self.queue_manager.put_objective(new_objective)
        else:
            self.agent.logger.info("Model Sommelier did not propose any optimization in this cycle.")

    def _run_linter_task(self):
        """Runs the linter agent to find and queue a new objective."""
        linter = LinterAgent(self.agent.logger.getChild("LinterAgent"))
        new_objective = linter.run_linter_and_propose_objective()
        
        if new_objective:
            self.agent.logger.info(f"Linter Agent found fixes and proposed a new objective.")
            self.queue_manager.put_objective(new_objective)
        else:
            self.agent.logger.info("Linter Agent cycle complete. No new objective proposed.")

    def _run_debt_hunter_task(self):
        """Runs the debt hunter agent to find and queue a new objective."""
        model_config = self.agent.config.get("models", {}).get("debt_hunter_default", self.agent.config.get("models", {}).get("architect_default"))
        # ... existing code ...

    def run(self) -> None:
        """Execute the main evolution loop for the given agent."""
        # Initial objective generation if needed, regardless of continuous mode.
        if not self.agent.objective_stack:
            self.agent.logger.info("Objective stack is empty. Generating initial objective...")
            model_config = self.agent.config.get("models", {}).get("objective_generator")
            initial_objective = generate_next_objective(
                model_config=model_config,
                current_manifest=self.agent.state.manifesto_content or "",
                logger=self.agent.logger,
                project_root_dir=".",
                config=self.agent.config,
                memory=self.agent.memory,
                model_optimizer=self.agent.model_optimizer
            )
            if initial_objective:
                self.agent.objective_stack.append(initial_objective)
                self.agent.logger.info(f"Initial objective: {initial_objective}")

        self.agent.logger.info(f"Starting HephaestusAgent. Continuous Mode: {'ON' if self.agent.continuous_mode else 'OFF'}.")
        if self.agent.objective_stack_depth_for_testing is not None:
            self.agent.logger.info(f"Max execution cycles set to: {self.agent.objective_stack_depth_for_testing}.")

        while True:
            if self.agent.objective_stack_depth_for_testing is not None and self.cycle_count >= self.agent.objective_stack_depth_for_testing:
                self.agent.logger.info(f"Execution cycle limit ({self.agent.objective_stack_depth_for_testing}) reached. Shutting down.")
                break

            current_objective = self._get_next_objective()
            if not current_objective:
                break

            self.cycle_count += 1
            self.agent.logger.info(f"\\n\\n{'='*20} START OF EVOLUTION CYCLE (Cycle #{self.cycle_count}) {'='*20}")
            self.agent.logger.info(f"CURRENT OBJECTIVE: {current_objective}\\n")

            if self._is_degenerative_loop(current_objective):
                self.agent.logger.error(f'Degenerative loop detected for objective: "{current_objective}". Discarding.')
                self.agent.memory.add_failed_objective(current_objective, "DEGENERATIVE_LOOP_DETECTED", "Objective failed too many times consecutively.")
                continue

            start_time = datetime.now()
            try:
                self._run_single_cycle(current_objective)
            except Exception as e:
                self.agent.logger.critical(f"UNHANDLED EXCEPTION in cycle runner: {e}", exc_info=True)
                if current_objective:
                    self.agent.memory.add_failed_objective(current_objective, "UNHANDLED_CYCLE_EXCEPTION", str(e))
            finally:
                end_time = datetime.now()
                self._log_cycle_completion(current_objective, start_time, end_time)
                self.agent.memory.save()
                self.agent.logger.info(f"Memory saved ({len(self.agent.memory.completed_objectives)} completed, {len(self.agent.memory.failed_objectives)} failed)")
                time.sleep(self.agent.config.get("cycle_delay_seconds", 1))

        self.agent.logger.info(f"{'='*20} END OF HEPHAESTUS EXECUTION {'='*20}")

    def _log_cycle_completion(self, objective: str, start_time: datetime, end_time: datetime):
        """Logs the final status of the completed cycle to the evolution log."""
        duration = (end_time - start_time).total_seconds()
        
        # Determine final status from agent state
        success, reason, context = self.agent.state.validation_result
        status_str = "success" if success else "failure"
        strategy = self.agent.state.strategy_key or "N/A"

        log_entry = [
            self.cycle_count,
            objective,
            status_str,
            round(duration, 2),
            "",  # quality_score placeholder
            strategy,
            start_time.isoformat(),
            end_time.isoformat(),
            reason,
            context,
        ]

        try:
            log_file = self.agent.evolution_log_file
            with open(log_file, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(log_entry)
        except IOError as e:
            self.agent.logger.error(f"Failed to write to evolution log {log_file}: {e}")
        except Exception as e:
            self.agent.logger.error(f"Unexpected error writing to evolution log: {e}", exc_info=True)