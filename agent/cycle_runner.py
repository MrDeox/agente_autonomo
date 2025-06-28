from __future__ import annotations

import csv
import json
import time
import asyncio # Added for PoC
from datetime import datetime
from typing import TYPE_CHECKING

from agent.project_scanner import update_project_manifest
from agent.brain import (
    generate_next_objective, # This would need to become async
    generate_capacitation_objective, # This would need to become async
    generate_commit_message, # This would need to become async
)
from agent.tool_executor import run_pytest, check_file_existence, run_git_command # These would need to become async for a full solution
from agent.error_analyzer import ErrorAnalysisAgent

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from main import HephaestusAgent


# For a full async implementation, run_cycles itself would become async
# async def run_cycles(agent: "HephaestusAgent") -> None:
# However, for this PoC, we'll keep it sync and use asyncio.run() for specific calls.

def run_cycles(agent: "HephaestusAgent") -> None:
    """Execute the main evolution loop for the given agent."""
    if not agent.objective_stack:
        agent.logger.info("Gerando objetivo inicial...")
        initial_objective_model = agent.config.get("models", {}).get("objective_generator", agent.light_model)

        # In a full async implementation, this would be:
        # initial_objective = await generate_next_objective(...)
        # For PoC, if generate_next_objective were async, we'd do:
        # initial_objective = asyncio.run(generate_next_objective(...))
        # But since generate_next_objective is not yet converted in this PoC scope, we keep it sync.
        initial_objective = generate_next_objective(
            api_key=agent.api_key,
            model=initial_objective_model,
            current_manifest="",
            logger=agent.logger,
            project_root_dir=".",
            config=agent.config,
            memory_summary=agent.memory.get_full_history_for_prompt(),
        )
        agent.objective_stack.append(initial_objective)
        agent.logger.info(f"Objetivo inicial: {initial_objective}")

    cycle_count = 0
    agent.logger.info(
        f"Iniciando HephaestusAgent. Modo Contínuo: {'ATIVADO' if agent.continuous_mode else 'DESATIVADO'}."
    )
    if agent.objective_stack_depth_for_testing is not None:
        agent.logger.info(
            f"Limite máximo de ciclos de execução definido para: {agent.objective_stack_depth_for_testing}."
        )

    while True:
        timestamp_inicio_ciclo = datetime.now()
        ciclo_status_final = "falha"
        razao_final = "ciclo_interrompido_prematuramente"
        contexto_final = "N/A"
        estrategia_final = ""
        objetivo_do_ciclo = ""

        if not agent.objective_stack:
            if agent.continuous_mode:
                agent.logger.info(f"\n{'='*20} MODO CONTÍNUO {'='*20}\nPilha de objetivos vazia. Gerando novo objetivo...")
                continuous_objective_model = agent.config.get("models", {}).get("objective_generator", agent.light_model)
                new_objective = generate_next_objective(
                    api_key=agent.api_key,
                    model=continuous_objective_model,
                    current_manifest=agent.state.manifesto_content if agent.state.manifesto_content else "",
                    logger=agent.logger,
                    project_root_dir=".",
                    config=agent.config,
                    memory_summary=agent.memory.get_full_history_for_prompt(),
                )
                agent.objective_stack.append(new_objective)
                agent.logger.info(f"Novo objetivo gerado para modo contínuo: {new_objective}")

                continuous_delay = agent.config.get("continuous_mode_delay_seconds", 5)
                agent.logger.info(f"Aguardando {continuous_delay} segundos antes do próximo ciclo contínuo...")
                time.sleep(continuous_delay)
            else:
                agent.logger.info("Pilha de objetivos vazia e modo contínuo desativado. Encerrando agente.")
                break

        if agent.objective_stack_depth_for_testing is not None and cycle_count >= agent.objective_stack_depth_for_testing:
            agent.logger.info(
                f"Limite de ciclos de execução ({agent.objective_stack_depth_for_testing}) atingido. Encerrando."
            )
            break

        cycle_count += 1
        current_objective = agent.objective_stack.pop()
        agent.logger.info(f"\n\n{'='*20} INÍCIO DO CICLO DE EVOLUÇÃO (Ciclo #{cycle_count}) {'='*20}")
        agent.logger.info(f"OBJETIVO ATUAL: {current_objective}\n")

        failure_count = 0
        for log_entry in reversed(agent.memory.recent_objectives_log):
            if log_entry["objective"] == current_objective and log_entry["status"] == "failure":
                failure_count += 1
            elif log_entry["objective"] == current_objective and log_entry["status"] == "success":
                break
            if failure_count >= agent.config.get("degenerative_loop_threshold", 3):
                break

        if failure_count >= agent.config.get("degenerative_loop_threshold", 3):
            agent.logger.error(
                f"Loop degenerativo detectado para o objetivo: \"{current_objective}\". Ocorreram {failure_count} falhas consecutivas."
            )
            agent.memory.add_failed_objective(
                objective=current_objective,
                reason="DEGENERATIVE_LOOP_DETECTED",
                details=f"O objetivo falhou {failure_count} vezes consecutivas. Pausando processamento deste objetivo.",
            )
            agent.logger.warning(
                f"O objetivo \"{current_objective}\" será descartado devido a loop degenerativo."
            )
            continue

        try:
            agent._reset_cycle_state()
            agent.state.current_objective = current_objective

            if not agent._generate_manifest(): # This could be async if file I/O is async
                agent.logger.error("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                break

            # --- PoC Change: Calling architect_phase with asyncio.run ---
            # In a full async implementation, agent._run_architect_phase itself would be async
            # and would be awaited here if run_cycles were async.
            # For PoC, we assume _run_architect_phase is modified to call the async plan_action
            # and needs to be run via asyncio.run() from this synchronous context.
            # This is a simplified demonstration. The HephaestusAgent class's _run_architect_phase
            # would need internal changes to call `asyncio.run(self.architect_agent.plan_action(...))`
            # or `await self.architect_agent.plan_action(...)` if _run_architect_phase itself becomes async.

            # Let's simulate the call pattern assuming agent._run_architect_phase() handles the asyncio.run() internally for PoC
            # Or, more directly for this PoC, let's modify how it's called IF _run_architect_phase was made async:
            # success_architect = asyncio.run(agent._run_architect_phase())
            # However, _run_architect_phase is part of the HephaestusAgent class, which is not being modified here.
            # So, the change should be *inside* _run_architect_phase in HephaestusAgent.
            # For this file, the call remains agent._run_architect_phase().
            # The actual `asyncio.run` would be inside `HephaestusAgent._run_architect_phase`
            # when it calls `self.architect_agent.plan_action`.

            # To make the PoC work without modifying HephaestusAgent here,
            # we'd conceptually assume _run_architect_phase in HephaestusAgent now looks like:
            #
            # def _run_architect_phase(self) -> bool:
            #     # ... other sync code ...
            #     action_plan_data, error = asyncio.run(self.architect_agent.plan_action(objective, manifest_content))
            #     # ... rest of the logic ...
            #
            # No change to the direct call here in cycle_runner.py is needed for this PoC structure,
            # as the async execution is encapsulated within the called method.
            if not agent._run_architect_phase():
                agent.logger.warning(
                    "Falha na fase do Arquiteto. Pulando para o próximo objetivo se houver."
                )
                agent.memory.add_failed_objective(current_objective, "ARCHITECT_PHASE_FAILED", "ArchitectAgent could not generate a plan.")
                if not agent.objective_stack and not agent.continuous_mode:
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
                agent.logger.info(f"Objetivo de correção detectado: '{current_objective[:100]}...'. Usando AUTO_CORRECTION_STRATEGY.")
                agent.state.strategy_key = "AUTO_CORRECTION_STRATEGY"
                # Ensure AUTO_CORRECTION_STRATEGY is valid
                if "AUTO_CORRECTION_STRATEGY" not in agent.config.get("validation_strategies", {}):
                    agent.logger.error("CRITICAL: AUTO_CORRECTION_STRATEGY não definida no hephaestus_config.json. Falhando o ciclo.")
                    agent.memory.add_failed_objective(current_objective, "CONFIG_ERROR", "AUTO_CORRECTION_STRATEGY missing.")
                    # Potentially break or continue to next objective if stack not empty
                    if not agent.objective_stack and not agent.continuous_mode:
                        break
                    continue
            else:
                # Normal flow: run Maestro phase
                if not agent._run_maestro_phase():
                    agent.logger.warning("Falha na fase do Maestro. Pulando para o próximo objetivo se houver.")
                    agent.memory.add_failed_objective(current_objective, "MAESTRO_PHASE_FAILED", "MaestroAgent could not decide on a strategy.")
                    if not agent.objective_stack and not agent.continuous_mode:
                        break
                    continue

            if agent.state.strategy_key == "CAPACITATION_REQUIRED":
                agent.logger.info("Maestro identificou a necessidade de uma nova capacidade.")
                agent.objective_stack.append(current_objective)
                architect_analysis = agent.state.get_architect_analysis()
                capacitation_objective_model = agent.config.get("models", {}).get("capacitation_generator", agent.light_model)
                capacitation_objective = generate_capacitation_objective(
                    api_key=agent.api_key,
                    model=capacitation_objective_model,
                    engineer_analysis=architect_analysis or "Analysis not available",
                    logger=agent.logger,
                    memory_summary=agent.memory.get_full_history_for_prompt(),
                )
                agent.logger.info(f"Gerado novo objetivo de capacitação: {capacitation_objective}")
                agent.objective_stack.append(capacitation_objective)
                continue

            agent._execute_validation_strategy()
            success, reason, context = agent.state.validation_result

            if success:
                agent.logger.info(f"\nSUCESSO NA VALIDAÇÃO/APLICAÇÃO! Razão: {reason}")
                if reason.startswith("APPLIED_AND_VALIDATED"):
                    agent.logger.info("--- INICIANDO VERIFICAÇÃO DE SANIDADE PÓS-APLICAÇÃO ---")
                    current_strategy_key_for_sanity = agent.state.strategy_key
                    strategy_config_sanity = agent.config.get("validation_strategies", {}).get(current_strategy_key_for_sanity, {})
                    sanity_check_tool_name = strategy_config_sanity.get("sanity_check_step", "run_pytest")

                    sanity_check_success = True
                    sanity_check_details = "Nenhuma verificação de sanidade configurada ou executada."

                    if sanity_check_tool_name == "run_pytest":
                        agent.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                        sanity_check_success, sanity_check_details = run_pytest(test_dir='tests/', cwd=".")
                    elif sanity_check_tool_name == "check_file_existence":
                        agent.logger.info(f"Executando sanidade ({sanity_check_tool_name}) no projeto real.")
                        files_to_check = list(agent.state.applied_files_report.keys()) if agent.state.applied_files_report else []
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
                        agent.logger.error(
                            f"FALHA NA SANIDADE PÓS-APLICAÇÃO({sanity_check_tool_name})! Detalhes: {sanity_check_details}"
                        )
                        agent.logger.info("Tentando reverter o último commit devido à falha na sanidade...")
                        revert_cmd = ['git', 'reset', '--hard']
                        run_git_command(['git', 'checkout', '--', '.'])
                        rollback_success, rollback_output = run_git_command(revert_cmd)

                        if rollback_success:
                            agent.logger.info(
                                f"Rollback das alterações no diretório de trabalho bem-sucedido. Output: {rollback_output}"
                            )
                        else:
                            agent.logger.error(
                                f"FALHA AO TENTAR REVERTER ALTERAÇÕES NO DIRETÓRIO DE TRABALHO! Output: {rollback_output}"
                            )

                        reason = f"REGRESSION_DETECTED_BY_{sanity_check_tool_name.upper()}_AND_ROLLED_BACK"
                        context = (
                            f"Sanity check failed: {sanity_check_details}. Rollback of working directory changes attempted (Success: {rollback_success})."
                        )
                        success = False
                    else:
                        agent.logger.info(f"SANIDADE PÓS-APLICAÇÃO ({sanity_check_tool_name}): SUCESSO!")
                        if sanity_check_tool_name != "skip_sanity_check":
                            agent.logger.info("Ressincronizando manifesto e iniciando auto-commit...")
                            update_project_manifest(root_dir=".", target_files=[])
                            with open("AGENTS.md", "r", encoding="utf-8") as f:
                                agent.state.manifesto_content = f.read()

                            analysis_summary_for_commit = agent.state.get_architect_analysis() or "N/A"
                            commit_model_for_msg = agent.config.get("models", {}).get("commit_message_generator", agent.light_model)
                            commit_message = generate_commit_message(
                                agent.api_key,
                                commit_model_for_msg,
                                analysis_summary_for_commit,
                                agent.state.current_objective or "N/A",
                                agent.logger,
                            )

                            run_git_command(['git', 'add', '.'])
                            commit_success_git, commit_output_git = run_git_command(['git', 'commit', '-m', commit_message])
                            if not commit_success_git:
                                agent.logger.error(
                                    f"FALHA CRÍTICA no git commit: {commit_output_git}. Alterações podem não ter sido salvas permanentemente."
                                )
                                reason = "COMMIT_FAILED_POST_SANITY"
                                context = f"Commit failed: {commit_output_git}"
                                success = False
                            else:
                                agent.logger.info("--- AUTO-COMMIT REALIZADO COM SUCESSO ---")
                        if success and agent.objective_stack_depth_for_testing is None:
                            agent.logger.info("Gerando próximo objetivo evolutivo...")
                            obj_gen_model = agent.config.get("models", {}).get("objective_generator", agent.light_model)
                            next_obj = generate_next_objective(
                                api_key=agent.api_key,
                                model=obj_gen_model,
                                current_manifest=agent.state.manifesto_content or "",
                                logger=agent.logger,
                                project_root_dir=".",
                                config=agent.config,
                                memory_summary=agent.memory.get_full_history_for_prompt(),
                            )
                            agent.objective_stack.append(next_obj)
                            agent.logger.info(f"Próximo objetivo: {next_obj}")

                    if success and agent.objective_stack_depth_for_testing is None:
                        agent.memory.add_completed_objective(
                            objective=agent.state.current_objective or "N/A",
                            strategy=agent.state.strategy_key or "N/A",
                            details=f"Applied. Sanity ({sanity_check_tool_name}): OK. Details: {sanity_check_details}",
                        )
                        if agent.state.current_objective and agent.state.current_objective.startswith("[TAREFA DE CAPACITAÇÃO]"):
                            agent.memory.add_capability(
                                capability_description=f"Capacitation task completed and validated: {agent.state.current_objective}",
                                related_objective=agent.state.current_objective,
                            )
                elif reason in ["DISCARDED", "VALIDATION_SUCCESS_NO_CHANGES", "STRATEGY_COMPLETED_NO_EXPLICIT_FAILURE"]:
                    agent.logger.info(
                        f"Ciclo concluído com status: {reason}. Nenhuma alteração no código foi promovida. Gerando próximo objetivo evolutivo..."
                    )
                    if agent.objective_stack_depth_for_testing is None:
                        if reason != "DISCARDED":
                            agent.memory.add_completed_objective(
                                objective=agent.state.current_objective or "N/A",
                                strategy=agent.state.strategy_key or "N/A",
                                details=f"Strategy '{agent.state.strategy_key}' completed. Status: {reason}.",
                            )
                        obj_gen_model = agent.config.get("models", {}).get("objective_generator", agent.light_model)
                        next_obj = generate_next_objective(
                            api_key=agent.api_key,
                            model=obj_gen_model,
                            current_manifest=agent.state.manifesto_content or "",
                            logger=agent.logger,
                            project_root_dir=".",
                            config=agent.config,
                            memory_summary=agent.memory.get_full_history_for_prompt(),
                        )
                        agent.objective_stack.append(next_obj)
                        agent.logger.info(f"Próximo objetivo: {next_obj}")

            if not success:
                agent.logger.warning(
                    f"\nFALHA NO CICLO! Razão Final: {reason}\nContexto Final: {context}"
                )
                if agent.objective_stack_depth_for_testing is None:
                    agent.memory.add_failed_objective(
                        objective=agent.state.current_objective or "N/A",
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

                if reason in correctable_failure_reasons and agent.objective_stack_depth_for_testing is None:
                    agent.logger.warning(
                        f"Falha corrigível ({reason}). Iniciando ErrorAnalysisAgent."
                    )

                    error_analyzer_model = agent.config.get("models", {}).get("error_analyzer", agent.light_model)
                    error_analyzer = ErrorAnalysisAgent(
                        api_key=agent.api_key,
                        model=error_analyzer_model,
                        logger=agent.logger.getChild("ErrorAnalysisAgent")
                    )

                    original_patches_json = json.dumps(agent.state.get_patches_to_apply(), indent=2) if agent.state.action_plan_data else "N/A"

                    # TODO: Consider passing failed_code_snippet and test_output if available/relevant
                    # For now, error_context might contain some of this.
                    analysis_result = error_analyzer.analyze_error(
                        failed_objective=current_objective,
                        error_reason=reason,
                        error_context=context,
                        original_patches=original_patches_json
                    )

                    agent.logger.info(f"ErrorAnalysisAgent resultado: Classificação='{analysis_result['classification']}', Tipo de Sugestão='{analysis_result['suggestion_type']}'")
                    agent.logger.debug(f"ErrorAnalysisAgent - Detalhes da Análise: {analysis_result['details']}")
                    agent.logger.debug(f"ErrorAnalysisAgent - Prompt Sugerido: {analysis_result['suggested_prompt']}")

                    correction_prompt = analysis_result.get("suggested_prompt")
                    suggestion_type = analysis_result.get("suggestion_type")

                    if correction_prompt and suggestion_type not in ["LOG_FOR_REVIEW", None]:
                        # Re-add original objective to try again with the new correction task
                        agent.objective_stack.append(current_objective)
                        agent.objective_stack.append(correction_prompt)

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
                                 agent.logger.info("ErrorAnalysisAgent classificou como TEST_FAILURE, mas o prompt não contém TEST_FIX_IN_PROGRESS. Isso pode ser necessário para o Maestro.")


                        agent.logger.info(log_message)

                        # Future: If suggestion_type is NEW_OBJECTIVE, we might not re-add `current_objective`.
                        # The `correction_prompt` itself would be the new high-level objective.
                        # This depends on how ErrorAnalysisAgent is designed to formulate `suggested_prompt` for NEW_OBJECTIVE.
                        # Current ErrorAnalysisAgent prompt implies `suggested_prompt` is always for Architect or a modified objective.

                    elif suggestion_type == "LOG_FOR_REVIEW":
                        agent.logger.error(
                            f"ErrorAnalysisAgent recomendou LOG_FOR_REVIEW para o objetivo '{current_objective}'. Detalhes: {analysis_result.get('details')}"
                        )
                        # The objective already failed and was logged by memory.add_failed_objective.
                        # No further automatic correction attempt will be made for this specific failure instance.
                    else:
                        agent.logger.error(
                            f"ErrorAnalysisAgent não forneceu um prompt de correção acionável para o objetivo '{current_objective}'. Detalhes: {analysis_result.get('details')}"
                        )
                else:
                    agent.logger.error(
                        f"Falha não listada como corrigível ({reason}) ou erro desconhecido. Não será gerado objetivo de correção automático. Verifique os logs."
                    )
        finally:
            agent.memory.save()
            agent.logger.info(
                f"Memória salva em {agent.memory.filepath} ({len(agent.memory.completed_objectives)} completed, {len(agent.memory.failed_objectives)} failed)"
            )

            if agent.objective_stack_depth_for_testing is not None:
                agent.objective_stack.clear()

            timestamp_fim_ciclo = datetime.now()
            tempo_gasto_segundos = (timestamp_fim_ciclo - timestamp_inicio_ciclo).total_seconds()

            if 'success' in locals() and isinstance(success, bool):
                ciclo_status_final = "sucesso" if success else "falha"

            if agent.state.validation_result:
                _, razao_final_state, contexto_final_state = agent.state.validation_result
                if razao_final_state:
                    razao_final = razao_final_state
                if contexto_final_state:
                    contexto_final = contexto_final_state

            if agent.state.strategy_key:
                estrategia_final = agent.state.strategy_key
            objetivo_do_ciclo = agent.state.current_objective or current_objective

            log_entry_evolution = [
                cycle_count,
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
                with open(agent.evolution_log_file, 'a', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(log_entry_evolution)
            except IOError as e:
                agent.logger.error(f"Não foi possível escrever no arquivo de log de evolução {agent.evolution_log_file}: {e}")
            except Exception as e:
                agent.logger.error(f"Erro inesperado ao tentar escrever no log de evolução: {e}", exc_info=True)

            agent.logger.info(f"{'='*20} FIM DO CICLO DE EVOLUÇÃO {'='*20}")
            time.sleep(agent.config.get("cycle_delay_seconds", 1))
