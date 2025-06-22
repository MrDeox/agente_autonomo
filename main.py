import argparse
import json
import os
import shutil
import tempfile
from pathlib import Path
from dotenv import load_dotenv

from agent.project_scanner import update_project_manifest
from agent.brain import get_ai_suggestion, get_maestro_decision
from agent.file_manager import apply_changes
from agent.code_validator import validate_python_code
from agent.tool_executor import run_in_sandbox


# Objetivo inicial de meta-nível utilizado para demonstrar a nova arquitetura
initial_objective = (
    "A estratégia 'SYNTAX_AND_BENCHMARK' é útil, mas incompleta. "
    "Uma mudança de performance também deveria ser validada funcionalmente. "
    "Sua tarefa é modificar o arquivo 'hephaestus_config.json' para que a estratégia 'SYNTAX_AND_BENCHMARK' também inclua o passo 'run_pytest_validation', executando-o antes do benchmark."
)


def load_config() -> dict:
    """Carrega o arquivo de configuração do agente."""
    with open("hephaestus_config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def apply_changes_in_dir(files_to_update, base_dir: Path) -> None:
    """Aplica mudanças em arquivos dentro de um diretório específico."""
    for item in files_to_update:
        rel_path = Path(item.get("file_path"))
        new_content = item.get("new_content", "")
        target = base_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(new_content)


def evaluate_benchmark(metrics_a: dict, metrics_b: dict) -> bool:
    """Avalia se a versão B é aceitável em relação à versão A."""
    if metrics_b.get("exit_code") != 0:
        return False
    if metrics_b.get("execution_time", 0) > metrics_a.get("execution_time", 0) * 1.2:
        return False
    return True


def run_evolution_cycle(objective: str, config: dict, benchmark_mode: bool = False) -> tuple[bool, str, str]:
    """Executa um ciclo de evolução único com base na estratégia escolhida."""

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False, "MISSING_API_KEY", "OPENROUTER_API_KEY não encontrado"

    state: dict = {"objective": objective}

    # Passo 1: gerar manifesto
    target_files: list[str] = []
    if "project_scanner.py" in objective:
        target_files.append("agent/project_scanner.py")
    print("Gerando manifesto do projeto (AGENTS.md)...")
    update_project_manifest(root_dir=".", target_files=target_files)
    with open("AGENTS.md", "r", encoding="utf-8") as f:
        state["manifesto_content"] = f.read()
    print("\n--- MANIFESTO GERADO (PRIMEIROS 1000 CARACTERES) ---")
    print(f"Tamanho total do manifesto: {len(state['manifesto_content'])} caracteres")
    print(state["manifesto_content"][:1000] + "...")

    # Passo 2: Engenheiro sugere mudança
    MODEL_FALLBACK_LIST = ["deepseek/deepseek-r1-0528:free", "mistralai/devstral-small:free"]
    print("\nSolicitando análise da IA (Engenheiro)...")
    attempt_logs = get_ai_suggestion(
        api_key=api_key,
        model_list=MODEL_FALLBACK_LIST,
        project_snapshot=state.get("manifesto_content", ""),
        objective=objective,
    )
    successful_attempt = next((a for a in attempt_logs if a["success"]), None)
    if not successful_attempt:
        log = "\n".join([f"Modelo {a['model']} -> {a['raw_response']}" for a in attempt_logs])
        return False, "LLM_COMMUNICATION_FAILED", log

    parsed_json = successful_attempt["parsed_json"]
    if parsed_json is None:
        return False, "INVALID_JSON", successful_attempt["raw_response"]
    state["parsed_json"] = parsed_json
    state["model_used"] = successful_attempt["model"]
    print("\n--- ANÁLISE DA IA ---")
    print(parsed_json.get("analysis_summary", ""))
    print(f"(Modelo usado: {state['model_used']})")

    # Passo 3: Maestro escolhe estratégia
    maestro_logs = get_maestro_decision(
        api_key=api_key,
        model_list=MODEL_FALLBACK_LIST,
        engineer_response=parsed_json,
        config=config,
    )
    maestro_attempt = next((a for a in maestro_logs if a["success"]), None)
    if not maestro_attempt:
        log = "\n".join([f"Modelo {a['model']} -> {a['raw_response']}" for a in maestro_logs])
        return False, "MAESTRO_FAILED", log
    decision = maestro_attempt["parsed_json"]
    strategy_key = (decision.get("strategy_key") or "").strip()
    strategies = config.get("validation_strategies", {})
    if strategy_key not in strategies:
        return False, "INVALID_STRATEGY", maestro_attempt["raw_response"]

    print(f"Estratégia escolhida pelo Maestro: {strategy_key}")

    # Preparar arquivos sugeridos
    state["files_to_update"] = parsed_json.get("files_to_update", [])
    state["test_code"] = (parsed_json.get("validation_pytest_code") or "").strip()

    # Executa passos definidos pela estratégia
    for step_name in strategies[strategy_key].get("steps", []):
        if benchmark_mode and step_name in {"run_benchmark_validation", "apply_changes"}:
            return True, "BENCHMARK_ONLY", "Benchmark executado"

        if step_name == "validate_syntax":
            for file_update in state["files_to_update"]:
                is_valid, error = validate_python_code(file_update["new_content"])
                if not is_valid:
                    context = f"Arquivo alvo: {file_update['file_path']}\nErro: {error}"
                    return False, "SYNTAX_ERROR", context

        elif step_name == "run_pytest_validation":
            test_code = state.get("test_code", "")
            temp_test_path = "tests/test_generated_by_agent.py"
            if test_code:
                print("\n--- EXECUTANDO TESTES DE VALIDAÇÃO GERADOS PELA IA ---")
                try:
                    os.makedirs("tests", exist_ok=True)
                    with open(temp_test_path, "w", encoding="utf-8") as test_file:
                        test_file.write(test_code)
                    from agent.tool_executor import run_pytest
                    tests_passed, pytest_output = run_pytest()
                    if not tests_passed:
                        return False, "PYTEST_FAILURE", pytest_output
                    print("✔ Testes de validação passaram com sucesso!")
                except Exception as e:
                    return False, "PYTEST_FAILURE", str(e)
                finally:
                    if os.path.exists(temp_test_path):
                        os.remove(temp_test_path)

        elif step_name == "run_benchmark_validation":
            print("\nExecutando benchmark A/B para validar a mudança...")
            with tempfile.TemporaryDirectory() as bench_dir:
                temp_a = Path(bench_dir) / "temp_A"
                temp_b = Path(bench_dir) / "temp_B"
                shutil.copytree(Path("."), temp_a, dirs_exist_ok=True)
                shutil.copytree(Path("."), temp_b, dirs_exist_ok=True)
                metrics_a = run_in_sandbox(str(temp_a), objective)
                apply_changes_in_dir(state.get("files_to_update", []), temp_b)
                metrics_b = run_in_sandbox(str(temp_b), objective)
            approved = evaluate_benchmark(metrics_a, metrics_b)
            print("\n--- RESULTADO DO BENCHMARK ---")
            print(
                f"Versão A - tempo: {metrics_a['execution_time']:.2f}s, pico memoria: {metrics_a['peak_memory_mb']:.2f}MB, exit: {metrics_a['exit_code']}"
            )
            print(
                f"Versão B - tempo: {metrics_b['execution_time']:.2f}s, pico memoria: {metrics_b['peak_memory_mb']:.2f}MB, exit: {metrics_b['exit_code']}"
            )
            if not approved:
                return False, "BENCHMARK_REJECTED", "Mudança rejeitada pelo benchmark."

        elif step_name == "apply_changes":
            print("Mudança aprovada. Aplicando...")
            report = apply_changes(state.get("files_to_update", []))
            state["apply_report"] = report
            if report["status"] != "success" and report.get("errors"):
                return False, "APPLY_FAILED", "\n".join(report["errors"])

        else:
            return False, "UNKNOWN_STEP", f"Passo não reconhecido: {step_name}"

    if strategy_key != "DISCARD":
        update_project_manifest(root_dir=".", target_files=[])
        return True, "APPLIED", "Mudança aplicada com sucesso."
    else:
        return True, "DISCARDED", "Mudança descartada"


def main(initial_objective: str, benchmark_mode: bool = False) -> None:
    """Controla o loop de evolução com capacidade de auto-correção."""
    config = load_config()

    if benchmark_mode:
        run_evolution_cycle(initial_objective, config, benchmark_mode=True)
        return

    current_objective = initial_objective

    while True:
        config = load_config()
        success, reason, context = run_evolution_cycle(current_objective, config)

        if success or reason == "USER_CANCELLED":
            break

        if reason in {"SYNTAX_ERROR", "PYTEST_FAILURE"}:
            previous_objective = current_objective
            current_objective = f"""
[TAREFA DE CORREÇÃO]
A tentativa anterior de alcançar o objetivo falhou durante a fase de validação.
OBJETIVO ORIGINAL:
{previous_objective}
FALHA ENCONTRADA: {reason}
DETALHES DO ERRO:
{context}

Sua nova missão é analisar o erro acima, entender por que a modificação anterior falhou, e propor uma nova versão do código que alcance o objetivo original E corrija esta falha.
"""
            continue
        else:
            break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("objective", nargs="?", default=initial_objective)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()

    main(args.objective, args.benchmark)
