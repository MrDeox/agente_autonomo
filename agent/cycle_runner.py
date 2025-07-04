from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from typing import TYPE_CHECKING

from agent.project_scanner import update_project_manifest
from agent.brain import (
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message,
)
from agent.tool_executor import run_pytest, check_file_existence, run_git_command
from agent.agents import ErrorAnalysisAgent # Import ErrorAnalysisAgent from new location

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from agent.hephaestus_agent import HephaestusAgent


from agent.queue_manager import QueueManager # Import QueueManager


class CycleRunner:
    """Manages the main execution loop of the Hephaestus agent."""

    def __init__(self, agent: "HephaestusAgent", queue_manager: QueueManager):
        self.agent = agent
        self.queue_manager = queue_manager
        self.cycle_count = 0

    def run(self) -> None:
        """Execute the main evolution loop for the given agent."""
        if not self.agent.objective_stack:
            self.agent.logger.info("Gerando objetivo inicial...")
            model_config = self.agent.config.get("models", {}).get("objective_generator")
            initial_objective = generate_next_objective(
                model_config=model_config,
                current_manifest="",
                logger=self.agent.logger,
                project_root_dir=".",
                config=self.agent.config,
                memory_summary=self.agent.memory.get_full_history_for_prompt(),
            )
            self.agent.objective_stack.append(initial_objective)
            self.agent.logger.info(f"Objetivo inicial: {initial_objective}")

        self.agent.logger.info(
            f"Iniciando HephaestusAgent. Modo Contínuo: {'ATIVADO' if self.agent.continuous_mode else 'DESATIVADO'}."
        )
        if self.agent.objective_stack_depth_for_testing is not None:
            self.agent.logger.info(
                f"Limite máximo de ciclos de execução definido para: {self.agent.objective_stack_depth_for_testing}."
            )

        while True:
            timestamp_inicio_ciclo = datetime.now()
            ciclo_status_final = "falha"
            razao_final = "ciclo_interrompido_prematuramente"
            contexto_final = "N/A"
            estrategia_final = ""
            objetivo_do_ciclo = ""

            if self.queue_manager.is_empty():
                if self.agent.continuous_mode:
                    self.agent.logger.info(f"\n{'='*20} MODO CONTÍNUO {'='*20}\nFila de objetivos vazia. Gerando novo objetivo...")
                    model_config = self.agent.config.get("models", {}).get("objective_generator")
                    new_objective = generate_next_objective(
                        model_config=model_config,
                        current_manifest=self.agent.state.manifesto_content if self.agent.state.manifesto_content else "",
                        logger=self.agent.logger,
                        project_root_dir=".",
                        config=self.agent.config,
                        memory_summary=self.agent.memory.get_full_history_for_prompt(),
                        current_objective=None, # No current objective for the new generation
                    )
                    self.queue_manager.put_objective(new_objective)
                    self.agent.logger.info(f"Novo objetivo gerado para modo contínuo e adicionado à fila: {new_objective}")

                    continuous_delay = self.agent.config.get("continuous_mode_delay_seconds", 5)
                    self.agent.logger.info(f"Aguardando {continuous_delay} segundos antes do próximo ciclo contínuo...")
                    time.sleep(continuous_delay)
                else:
                    self.agent.logger.info("Fila de objetivos vazia e modo contínuo desativado. Encerrando agente.")
                    break

            if self.agent.objective_stack_depth_for_testing is not None and self.cycle_count >= self.agent.objective_stack_depth_for_testing:
                self.agent.logger.info(
                    f"Limite de ciclos de execução ({self.agent.objective_stack_depth_for_testing}) atingido. Encerrando."
                )
                break

            if not self.agent.objective_stack:
                self.agent.logger.info("Fila de objetivos vazia. Verificando modo contínuo.")
                if not self.agent.continuous_mode:
                    break
                else:
                    # Lógica para modo contínuo
                    pass # A lógica de modo contínuo já está sendo tratada acima

            self.cycle_count += 1
            
            # Verificação segura antes do pop
            if not self.agent.objective_stack:
                self.agent.logger.info("Fila de objetivos vazia no momento do pop. Verificando modo contínuo.")
                if not self.agent.continuous_mode:
                    break
                else:
                    # Gerar novo objetivo para modo contínuo
                    self.agent.logger.info("Gerando novo objetivo para modo contínuo...")
                    model_config = self.agent.config.get("models", {}).get("objective_generator")
                    new_objective = generate_next_objective(
                        model_config=model_config,
                        current_manifest=self.agent.state.manifesto_content if self.agent.state.manifesto_content else "",
                        logger=self.agent.logger,
                        project_root_dir=".",
                        config=self.agent.config,
                        memory_summary=self.agent.memory.get_full_history_for_prompt(),
                    )
                    self.agent.objective_stack.append(new_objective)
                    self.agent.logger.info(f"Novo objetivo gerado: {new_objective}")
            
            current_objective = self.agent.objective_stack.pop()
            self.agent.logger.info(f"\n\n{'='*20} INÍCIO DO CICLO DE EVOLUÇÃO (Ciclo #{self.cycle_count}) {'='*20}")
            self.agent.logger.info(f"OBJETIVO ATUAL: {current_objective}\n")

            failure_count = 0
            for log_entry in reversed(self.agent.memory.recent_objectives_log):
                if log_entry["objective"] == current_objective and log_entry["status"] == "failure":
                    failure_count += 1
                elif log_entry["objective"] == current_objective and log_entry["status"] == "success":
                    break
                if failure_count >= self.agent.config.get("degenerative_loop_threshold", 3):
                    break

            if failure_count >= self.agent.config.get("degenerative_loop_threshold", 3):
                self.agent.logger.error(
                    f"Loop degenerativo detectado para o objetivo: \"{current_objective}\". Ocorreram {failure_count} falhas consecutivas."
                )
                self.agent.memory.add_failed_objective(
                    objective=current_objective,
                    reason="DEGENERATIVE_LOOP_DETECTED",
                    details=f"O objetivo falhou {failure_count} vezes consecutivas. Pausando processamento deste objetivo.",
                )
                self.agent.logger.warning(
                    f"O objetivo \"{current_objective}\" será descartado devido a loop degenerativo."
                )
                continue

            try:
                self.agent._reset_cycle_state()
                self.agent.state.current_objective = current_objective

                if not self.agent._generate_manifest():
                    self.agent.logger.error("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                    break
                if not self.agent._run_architect_phase():
                    self.agent.logger.warning(
                        "Falha na fase do Arquiteto. Pulando para o próximo objetivo se houver."
                    )
                    self.agent.memory.add_failed_objective(current_objective, "ARCHITECT_PHASE_FAILED", "ArchitectAgent could not generate a plan.")
                    if not self.agent.objective_stack and not self.agent.continuous_mode:
                        break
                    continue

                # Check if current_objective is an auto-correction task
                # If so, set strategy to AUTO_CORRECTION_STRATEGY and skip Maestro phase
                is_correction_objective = False
                correction_prefixes = [
                    "[AUTOMATIC CORRECTION TASK]",
                    "[CORRECTION TASK - SYNTAX]",
                    "[CORRECTION TASK - TEST]",
                    "[CORRECTION TASK - LOGIC]", # Added for completeness, though ErrorAnalysisAgent might suggest NEW_OBJECTIVE for pure logic
                    "[REVISED OBJECTIVE", # Broader category for revised objectives from ErrorAnalysisAgent
                    "[MODIFIED OBJECTIVE"
                ]
                for prefix in correction_prefixes:
                    if current_objective.startswith(prefix):
                        is_correction_objective = True
                        break

                if is_correction_objective:
                    self.agent.logger.info(f"Objetivo de correção detectado: '{current_objective[:100]}...'. Usando AUTO_CORRECTION_STRATEGY.")
                    self.agent.state.strategy_key = "AUTO_CORRECTION_STRATEGY"
                    # Ensure AUTO_CORRECTION_STRATEGY is valid
                    if "AUTO_CORRECTION_STRATEGY" not in self.agent.config.get("validation_strategies", {}):
                        self.agent.logger.error("CRITICAL: AUTO_CORRECTION_STRATEGY não definida no hephaestus_config.json. Falhando o ciclo.")
                        self.agent.memory.add_failed_objective(current_objective, "CONFIG_ERROR", "AUTO_CORRECTION_STRATEGY missing.")
                        # Potentially break or continue to next objective if stack not empty
                        if not self.agent.objective_stack and not self.agent.continuous_mode:
                            break
                        continue
                else:
                    # Normal flow: run Maestro phase
                    if not self.agent._run_maestro_phase():
                        self.agent.logger.warning("Falha na fase do Maestro. Pulando para o próximo objetivo se houver.")
                        self.agent.memory.add_failed_objective(current_objective, "MAESTRO_PHASE_FAILED", "MaestroAgent could not decide on a strategy.")
                        if not self.agent.objective_stack and not self.agent.continuous_mode:
                            break
                        continue

                if self.agent.state.strategy_key == "CAPACITATION_REQUIRED":
                    self.agent.logger.info("Maestro identificou a necessidade de uma nova capacidade.")
                    self.agent.objective_stack.append(current_objective)
                    architect_analysis = self.agent.state.get_architect_analysis()
                    model_config = self.agent.config.get("models", {}).get("capacitation_generator")
                    capacitation_objective = generate_capacitation_objective(
                        model_config=model_config,
                        engineer_analysis=architect_analysis or "Analysis not available",
                        logger=self.agent.logger,
                        memory_summary=self.agent.memory.get_full_history_for_prompt(),
                    )
                    self.agent.logger.info(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                    self.agent.objective_stack.append(capacitation_objective)
                    continue

                self.agent._execute_validation_strategy()
                success, reason, context = self.agent.state.validation_result

                if success:
                    self.agent.logger.info(f"\nSUCESSO NA VALIDAÇÃO/APLICAÇÃO! Razão: {reason}")
                    if reason.startswith("APPLIED_AND_VALIDATED"):
                        self.agent.logger.info("--- INICIANDO VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ---")
                        current_strategy_key_for_sanity = self.agent.state.strategy_key
                        strategy_config_sanity = self.agent.config.get("validation_strategies", {}).get(current_strategy_key_for_sanity, {})
                        sanity_check_tool_name = strategy_config_sanity.get("sanity_check_step", "run_pytest")

                        sanity_check_success = True
                        sanity_check_details = "Nenhuma verificação de sanidade configurada ou executada."

                        if sanity_check_tool_name == "run_pytest":
                            self.agent.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                            sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/', cwd=".")
                        elif sanity_check_tool_name == "check_file_existence":
                            self.agent.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                            files_to_check = list(self.agent.state.applied_files_report.keys()) if self.agent.state.applied_files_report else []
                            if files_to_check:
                                sanity_check_success, sanity_check_details = check_file_existence(files_to_check)
                            else:
                                sanity_check_success = True
                                sanity_check_details = "Nenhum arquivo aplicado para verificar na sanidade."
                        elif sanity_check_tool_name == "skip_sanity_check":
                            sanity_check_success = True
                            sanity_check_details = "Verificação de sanidade pulada conforme configuração."
                        else:
                            sanity_check_success = False
                            sanity_check_details = f"Ferramenta de sanidade desconhecida: {sanity_check_tool_name}"

                        if not sanity_check_success:
                            self.agent.logger.error(
                                f"FALHA NA SANIDADE PÓS-APLICAÇÃO({sanity_check_tool_name})! Detalhes: {sanity_check_details}"
                            )
                            self.agent.logger.info("Tentando reverter o último commit devido à falha na sanidade...")
                            revert_cmd = ['git', 'reset', '--hard']
                            run_git_command(['git', 'checkout', '--', '.'])
                            rollback_success, rollback_output = run_git_command(revert_cmd)

                            if rollback_success:
                                self.agent.logger.info(
                                    f"Rollback das alterações no diretório de trabalho bem-sucedido. Output: {rollback_output}"
                                )
                            else:
                                self.agent.logger.error(
                                    f"FALHA AO TENTAR REVERTER ALTERAÇÕES NO DIRETÓRIO DE TRABALHO! Output: {rollback_output}"
                                )

                            reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}_AND_ROLLED_BACK"
                            context = (
                                f"Sanity check failed: {sanity_check_details}. Rollback of working directory changes attempted (Success: {rollback_success})."
                            )
                            success = False
                        else:
                            self.agent.logger.info(f"SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                            if sanity_check_tool_name != "skip_sanity_check":
                                self.agent.logger.info("Ressincronizando manifesto e iniciando auto-commit...")
                                update_project_manifest(root_dir=".", target_files=[])
                                with open("AGENTS.md", "r", encoding="utf-8") as f:
                                    self.agent.state.manifesto_content = f.read()

                                analysis_summary_for_commit = self.agent.state.get_architect_analysis() or "N/A"
                                model_config = self.agent.config.get("models", {}).get("commit_message_generator", self.agent.config.get("models", {}).get("architect_default"))
                                commit_message = generate_commit_message(
                                    model_config,
                                    analysis_summary_for_commit,
                                    self.agent.state.current_objective or "N/A",
                                    self.agent.logger,
                                )

                                run_git_command(['git', 'add', '.'])
                                commit_success_git, commit_output_git = run_git_command(['git', 'commit', '-m', commit_message])
                                if not commit_success_git:
                                    self.agent.logger.error(
                                        f"FALHA CRÍTICA no git commit: {commit_output_git}. Alterações podem não ter sido salvas permanentemente."
                                    )
                                    reason = "COMMIT_FAILED_POST_SANITY"
                                    context = f"Commit failed: {commit_output_git}"
                                    success = False
                                else:
                                    self.agent.logger.info("--- AUTO-COMMIT REALIZADO COM SUCESSO ---")
                            if success and self.agent.objective_stack_depth_for_testing is None:
                                self.agent.logger.info("Gerando próximo objetivo evolutivo...")
                                model_config = self.agent.config.get("models", {}).get("objective_generator")
                                next_obj = generate_next_objective(
                                    model_config=model_config,
                                    current_manifest=self.agent.state.manifesto_content or "",
                                    logger=self.agent.logger,
                                    project_root_dir=".",
                                    config=self.agent.config,
                                    memory_summary=self.agent.memory.get_full_history_for_prompt(),
                                )
                                self.agent.objective_stack.append(next_obj)
                                self.agent.logger.info(f"Próximo objetivo: {next_obj}")

                        if success and self.agent.objective_stack_depth_for_testing is None:
                            self.agent.memory.add_completed_objective(
                                objective=self.agent.state.current_objective or "N/A",
                                strategy=self.agent.state.strategy_key or "N/A",
                                details=f"Applied. Sanity ({sanity_check_tool_name}): OK. Details: {sanity_check_details}",
                            )
                            if self.agent.state.current_objective and self.agent.state.current_objective.startswith("[TAREFA DE CAPACITAÇÃO]"):
                                self.agent.memory.add_capability(
                                    capability_description=f"Capacitation task completed and validated: {self.agent.state.current_objective}",
                                    related_objective=self.agent.state.current_objective,
                                )
                    elif reason in ["DISCARDED", "VALIDATION_SUCCESS_NO_CHANGES", "STRATEGY_COMPLETED_NO_EXPLICIT_FAILURE"]:
                        self.agent.logger.info(
                            f"Ciclo concluído com status: {reason}. Nenhuma alteração no código foi promovida. Gerando próximo objetivo evolutivo..."
                        )
                        if self.agent.objective_stack_depth_for_testing is None:
                            if reason != "DISCARDED":
                                self.agent.memory.add_completed_objective(
                                    objective=self.agent.state.current_objective or "N/A",
                                    strategy=self.agent.state.strategy_key or "N/A",
                                    details=f"Strategy '{self.agent.state.strategy_key}' completed. Status: {reason}.",
                                )
                            model_config = self.agent.config.get("models", {}).get("objective_generator")
                            next_obj = generate_next_objective(
                                model_config=model_config,
                                current_manifest=self.agent.state.manifesto_content or "",
                                logger=self.agent.logger,
                                project_root_dir=".",
                                config=self.agent.config,
                                memory_summary=self.agent.memory.get_full_history_for_prompt(),
                                current_objective=current_objective,
                            )
                            self.agent.objective_stack.append(next_obj)
                            self.agent.logger.info(f"Próximo objetivo: {next_obj}")

                if not success:
                    self.agent.logger.warning(
                        f"\nFALHA NO CICLO! Razão Final: {reason}\nContexto Final: {context}"
                    )
                    if self.agent.objective_stack_depth_for_testing is None:
                        self.agent.memory.add_failed_objective(
                            objective=self.agent.state.current_objective or "N/A",
                            reason=reason,
                            details=context,
                        )

                    correctable_failure_reasons = {
                        "PATCH_APPLICATION_FAILED",
                        "SYNTAX_VALIDATION_FAILED",
                        "JSON_SYNTAX_VALIDATION_FAILED",
                        "PYTEST_VALIDATION_FAILED",
                        "BENCHMARK_VALIDATION_FAILED",
                        "PROMOTION_FAILED",
                        "APPLY_PATCHES_TO_DISK_FAILED_IN_SANDBOX",
                        "VALIDATE_SYNTAX_FAILED_IN_SANDBOX",
                        "VALIDATE_JSON_SYNTAX_FAILED_IN_SANDBOX",
                        "RUN_PYTEST_VALIDATION_FAILED_IN_SANDBOX",
                        "RUN_BENCHMARK_VALIDATION_FAILED_IN_SANDBOX",
                        "COMMIT_FAILED_POST_SANITY",
                    }
                    if 'sanity_check_tool_name' in locals() and sanity_check_tool_name != "skip_sanity_check" and reason.startswith("REGRESSION_DETECTED_BY_"):
                        correctable_failure_reasons.add(reason)

                    if reason in correctable_failure_reasons and self.agent.objective_stack_depth_for_testing is None:
                        self.agent.logger.warning(
                            f"Falha corrigível ({reason}). Iniciando ErrorAnalysisAgent."
                        )

                        model_config = self.agent.config.get("models", {}).get("error_analyzer")
                        error_analyzer = ErrorAnalysisAgent(
                            model_config=model_config,
                            logger=self.agent.logger.getChild("ErrorAnalysisAgent")
                        )

                        original_patches_json = json.dumps(self.agent.state.get_patches_to_apply(), indent=2) if self.agent.state.action_plan_data else "N/A"

                        # TODO: Consider passing failed_code_snippet and test_output if available/relevant
                        # For now, error_context might contain some of this.
                        # Ler capabilities e roadmap para passar ao ErrorAnalysisAgent
                        capabilities_content_for_error_analysis = self.agent.state.manifesto_content # Usar manifesto atual como fallback se CAPABILITIES.md falhar
                        try:
                            with open("CAPABILITIES.md", "r", encoding="utf-8") as f:
                                capabilities_content_for_error_analysis = f.read()
                        except Exception:
                            self.agent.logger.warning("Não foi possível ler CAPABILITIES.md para ErrorAnalysisAgent, usando manifesto atual.")

                        roadmap_content_for_error_analysis = "" # Default para string vazia se não encontrado
                        try:
                            with open("ROADMAP.md", "r", encoding="utf-8") as f:
                                roadmap_content_for_error_analysis = f.read()
                        except Exception:
                            self.agent.logger.warning("Não foi possível ler ROADMAP.md para ErrorAnalysisAgent.")

                        analysis_result = error_analyzer.analyze_error(
                            failed_objective=current_objective,
                            error_reason=reason,
                            error_context=context,
                            original_patches=original_patches_json,
                            capabilities_content=capabilities_content_for_error_analysis,
                            roadmap_content=roadmap_content_for_error_analysis
                        )

                        self.agent.logger.info(f"ErrorAnalysisAgent resultado: Classificação='{analysis_result['classification']}', Tipo de Sugestão='{analysis_result['suggestion_type']}'")
                        self.agent.logger.debug(f"ErrorAnalysisAgent - Detalhes da Análise: {analysis_result['details']}")
                        self.agent.logger.debug(f"ErrorAnalysisAgent - Prompt Sugerido: {analysis_result['suggested_prompt']}")

                        correction_prompt = analysis_result.get("suggested_prompt")
                        suggestion_type = analysis_result.get("suggestion_type")

                        if correction_prompt and suggestion_type not in ["LOG_FOR_REVIEW", None]:
                            # Re-add original objective to try again with the new correction task
                            self.agent.objective_stack.append(current_objective)
                            self.agent.objective_stack.append(correction_prompt)

                            log_message = f"Novo objetivo de correção gerado pelo ErrorAnalysisAgent e adicionado à pilha: '{correction_prompt[:100]}...'"

                            # Add TEST_FIX_IN_PROGRESS flag if ErrorAnalysisAgent classified it as such (implicitly or explicitly)
                            # For now, we rely on the ErrorAnalysisAgent's prompt to contain necessary context.
                            # If a more explicit flag is needed for MaestroAgent, ErrorAnalysisAgent should provide it.
                            is_test_failure_flag = analysis_result['classification'] == "TEST_FAILURE"
                            if is_test_failure_flag: # This flag is used by MaestroAgent in current code, let's keep it if test failure
                                 if "[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS" not in correction_prompt:
                                     # The ErrorAnalysisAgent should ideally include this in its suggested_prompt if needed.
                                     # However, to maintain compatibility with existing Maestro logic, we can check here.
                                     # A better approach would be for ErrorAnalysisAgent to return a specific flag or ensure its prompt is complete.
                                     self.agent.logger.info("ErrorAnalysisAgent classificou como TEST_FAILURE, mas o prompt não contém TEST_FIX_IN_PROGRESS. Isso pode ser necessário para o Maestro.")


                            self.agent.logger.info(log_message)

                            # Future: If suggestion_type is NEW_OBJECTIVE, we might not re-add `current_objective`.
                            # The `correction_prompt` itself would be the new high-level objective.
                            # This depends on how ErrorAnalysisAgent is designed to formulate `suggested_prompt` for NEW_OBJECTIVE.
                            # Current ErrorAnalysisAgent prompt implies `suggested_prompt` is always for Architect or a modified objective.

                        elif suggestion_type == "LOG_FOR_REVIEW":
                            self.agent.logger.error(
                                f"ErrorAnalysisAgent recomendou LOG_FOR_REVIEW para o objetivo '{current_objective}'. Detalhes: {analysis_result.get('details')}"
                            )
                            # The objective already failed and was logged by memory.add_failed_objective.
                            # No further automatic correction attempt will be made for this specific failure instance.
                        else:
                            self.agent.logger.error(
                                f"ErrorAnalysisAgent não forneceu um prompt de correção acionável para o objetivo '{current_objective}'. Detalhes: {analysis_result.get('details')}"
                            )
                    else:
                        self.agent.logger.error(
                            f"Falha não listada como corrigível ({reason}) ou erro desconhecido. Não será gerado objetivo de correção automático. Verifique os logs."
                        )
            finally:
                self.agent.memory.save()
                self.agent.logger.info(
                    f"Memória salva em {self.agent.memory.filepath} ({len(self.agent.memory.completed_objectives)} completed, {len(self.agent.memory.failed_objectives)} failed)"
                )

                if self.agent.objective_stack_depth_for_testing is not None:
                    self.agent.objective_stack.clear()

                timestamp_fim_ciclo = datetime.now()
                tempo_gasto_segundos = (timestamp_fim_ciclo - timestamp_inicio_ciclo).total_seconds()

                if 'success' in locals() and isinstance(success, bool):
                    ciclo_status_final = "sucesso" if success else "falha"

                if self.agent.state.validation_result:
                    _, razao_final_state, contexto_final_state = self.agent.state.validation_result
                    if razao_final_state:
                        razao_final = razao_final_state
                    if contexto_final_state:
                        contexto_final = contexto_final_state

                if self.agent.state.strategy_key:
                    estrategia_final = self.agent.state.strategy_key
                objetivo_do_ciclo = self.agent.state.current_objective or current_objective

                log_entry_evolution = [
                    self.cycle_count,
                    objetivo_do_ciclo,
                    ciclo_status_final,
                    round(tempo_gasto_segundos, 2),
                    "",
                    estrategia_final,
                    timestamp_inicio_ciclo.isoformat(),
                    timestamp_fim_ciclo.isoformat(),
                    razao_final,
                    contexto_final,
                ]
                try:
                    with open(self.agent.evolution_log_file, 'a', newline='', encoding='utf-8') as f:
                        csv.writer(f).writerow(log_entry_evolution)
                except IOError as e:
                    self.agent.logger.error(f"Não foi possível escrever no arquivo de log de evolução {self.agent.evolution_log_file}: {e}")
                except Exception as e:
                    self.agent.logger.error(f"Erro inesperado ao tentar escrever no log de evolução: {e}", exc_info=True)

                self.agent.logger.info(f"{'='*20} FIM DO CICLO DE EVOLUÇÃO {'='*20}")
                time.sleep(self.agent.config.get("cycle_delay_seconds", 1))


def run_cycles(agent: "HephaestusAgent", queue_manager: QueueManager) -> None:
    """Execute the main evolution loop for the given agent."""
    cycle_runner = CycleRunner(agent, queue_manager)
    cycle_runner.run()