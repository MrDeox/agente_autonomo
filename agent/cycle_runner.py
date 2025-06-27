from __future__ import annotations

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

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from main import HephaestusAgent


def run_cycles(agent: "HephaestusAgent") -> None:
    """Execute the main evolution loop for the given agent."""
    if not agent.objective_stack:
        agent.logger.info("Gerando objetivo inicial...")
        initial_objective_model = agent.config.get("models", {}).get("objective_generator", agent.light_model)
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

            if not agent._generate_manifest():
                agent.logger.error("Falha crítica ao gerar manifesto. Encerrando ciclo.")
                break
            if not agent._run_architect_phase():
                agent.logger.warning(
                    "Falha na fase do Arquiteto. Pulando para o próximo objetivo se houver."
                )
                agent.memory.add_failed_objective(current_objective, "ARCHITECT_PHASE_FAILED", "ArchitectAgent could not generate a plan.")
                if not agent.objective_stack and not agent.continuous_mode:
                    break
                continue
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
                        if success:
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

                    if success:
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
                agent.memory.add_failed_objective(objective=agent.state.current_objective or "N/A", reason=reason, details=context)

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

                if reason in correctable_failure_reasons:
                    agent.logger.warning(
                        f"Falha corrigível ({reason}). Gerando objetivo de correção."
                    )
                    agent.objective_stack.append(current_objective)

                    original_patches_json = json.dumps(agent.state.get_patches_to_apply(), indent=2) if agent.state.action_plan_data else "N/A"
                    correction_details = f"FAILURE REASON: {reason}\nFAILURE DETAILS: {context}"
                    is_test_failure_flag = "PYTEST_FAILURE" in reason.upper() or "REGRESSION_DETECTED_BY_RUN_PYTEST" in reason.upper()

                    correction_prompt = f"""[AUTOMATIC CORRECTION TASK]
ORIGINAL OBJECTIVE THAT FAILED: {current_objective}
{correction_details}
ORIGINAL PATCHES INVOLVED: {original_patches_json}
Your mission is to analyze the failure and generate NEW patches to CORRECT the problem and achieve the ORIGINAL OBJECTIVE.
If the problem was in the patches, correct them. If it was in validation or sanity checks, adjust the patches to pass.
"""
                    if is_test_failure_flag:
                        correction_prompt += "\n[CONTEXT_FLAG] TEST_FIX_IN_PROGRESS"

                    agent.objective_stack.append(correction_prompt)
                    agent.logger.info(
                        f"Gerado novo objetivo de correção e adicionado à pilha. {'(TEST_FIX_IN_PROGRESS)' if is_test_failure_flag else ''}"
                    )
                else:
                    agent.logger.error(
                        f"Falha não listada como corrigível ou desconhecida ({reason}). Não será gerado objetivo de correção automático. Verifique os logs."
                    )
        finally:
            agent.memory.save()
            agent.logger.info(
                f"Memória salva em {agent.memory.filepath} ({len(agent.memory.completed_objectives)} completed, {len(agent.memory.failed_objectives)} failed)"
            )

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

