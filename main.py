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


class HephaestusAgent:
    """Classe principal que encapsula a lógica do agente autônomo."""

    def __init__(self, initial_objective: str):
        """Inicializa o agente com objetivo e configuração.
        
        Args:
            initial_objective: Objetivo inicial para o ciclo de evolução
        """
        self.current_objective = initial_objective
        self.config = self.load_config()
        self.state = {
            "manifesto_content": "",
            "parsed_json": None,
            "files_to_update": [],
            "test_code": "",
            "model_used": None
        }

    @staticmethod
    def load_config() -> dict:
        """Carrega o arquivo de configuração do agente.
        
        Returns:
            Dicionário com a configuração carregada
        """
        with open("hephaestus_config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _generate_manifest(self) -> None:
        """Gera o manifesto do projeto atualizando AGENTS.md."""
        target_files = []
        if "project_scanner.py" in self.current_objective:
            target_files.append("agent/project_scanner.py")
        
        print("Gerando manifesto do projeto (AGENTS.md)...")
        update_project_manifest(root_dir=".", target_files=target_files)
        
        with open("AGENTS.md", "r", encoding="utf-8") as f:
            self.state["manifesto_content"] = f.read()
        
        print("\n--- MANIFESTO GERADO (PRIMEIROS 1000 CARACTERES) ---")
        print(f"Tamanho total do manifesto: {len(self.state['manifesto_content'])} caracteres")
        print(self.state["manifesto_content"][:1000] + "...")

    def _run_engineer_phase(self) -> bool:
        """Executa a fase de engenharia com sugestão da IA.
        
        Returns:
            True se a fase foi bem sucedida, False caso contrário
        """
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return False

        MODEL_FALLBACK_LIST = ["deepseek/deepseek-r1-0528:free", "mistralai/devstral-small:free"]
        print("\nSolicitando análise da IA (Engenheiro)...")
        
        attempt_logs = get_ai_suggestion(
            api_key=api_key,
            model_list=MODEL_FALLBACK_LIST,
            project_snapshot=self.state["manifesto_content"],
            objective=self.current_objective,
        )
        
        successful_attempt = next((a for a in attempt_logs if a["success"]), None)
        if not successful_attempt:
            return False

        parsed_json = successful_attempt["parsed_json"]
        if parsed_json is None:
            return False

        self.state["parsed_json"] = parsed_json
        self.state["model_used"] = successful_attempt["model"]
        self.state["files_to_update"] = parsed_json.get("files_to_update", [])
        self.state["test_code"] = (parsed_json.get("validation_pytest_code") or "").strip()

        print("\n--- ANÁLISE DA IA ---")
        print(parsed_json.get("analysis_summary", ""))
        print(f"(Modelo usado: {self.state['model_used']})")
        return True

    def _run_maestro_phase(self) -> str:
        """Executa a fase de decisão do maestro.
        
        Returns:
            Chave da estratégia selecionada ou string vazia em caso de falha
        """
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            return ""

        MODEL_FALLBACK_LIST = ["deepseek/deepseek-r1-0528:free", "mistralai/devstral-small:free"]
        
        maestro_logs = get_maestro_decision(
            api_key=api_key,
            model_list=MODEL_FALLBACK_LIST,
            engineer_response=self.state["parsed_json"],
            config=self.config,
        )
        
        maestro_attempt = next((a for a in maestro_logs if a["success"]), None)
        if not maestro_attempt:
            return ""

        decision = maestro_attempt["parsed_json"]
        strategy_key = (decision.get("strategy_key") or "").strip()
        strategies = self.config.get("validation_strategies", {})
        
        if strategy_key not in strategies:
            return ""

        print(f"Estratégia escolhida pelo Maestro: {strategy_key}")
        return strategy_key

    def _execute_validation_strategy(self, strategy_key: str, benchmark_mode: bool = False) -> tuple[bool, str, str]:
        """Executa os passos de validação conforme a estratégia escolhida.
        
        Args:
            strategy_key: Chave da estratégia a ser executada
            benchmark_mode: Se True, executa apenas benchmark
            
        Returns:
            Tupla (success, reason, context) indicando resultado
        """
        strategies = self.config.get("validation_strategies", {})
        steps = strategies.get(strategy_key, {}).get("steps", [])
        
        for step_name in steps:
            if benchmark_mode and step_name in {"run_benchmark_validation", "apply_changes"}:
                return True, "BENCHMARK_ONLY", "Benchmark executado"

            if step_name == "validate_syntax":
                for file_update in self.state["files_to_update"]:
                    is_valid, error = validate_python_code(file_update["new_content"])
                    if not is_valid:
                        context = f"Arquivo alvo: {file_update['file_path']}\nErro: {error}"
                        return False, "SYNTAX_ERROR", context

            elif step_name == "run_pytest_validation":
                if not self.state["test_code"]:
                    continue
                    
                print("\n--- EXECUTANDO TESTES DE VALIDAÇÃO GERADOS PELA IA ---")
                temp_test_path = "tests/test_generated_by_agent.py"
                try:
                    os.makedirs("tests", exist_ok=True)
                    with open(temp_test_path, "w", encoding="utf-8") as test_file:
                        test_file.write(self.state["test_code"])
                    
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
                    
                    metrics_a = run_in_sandbox(str(temp_a), self.current_objective)
                    self._apply_changes_in_dir(self.state.get("files_to_update", []), temp_b)
                    metrics_b = run_in_sandbox(str(temp_b), self.current_objective)
                
                approved = self._evaluate_benchmark(metrics_a, metrics_b)
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
                report = apply_changes(self.state.get("files_to_update", []))
                self.state["apply_report"] = report
                if report["status"] != "success" and report.get("errors"):
                    return False, "APPLY_FAILED", "\n".join(report["errors"])

            else:
                return False, "UNKNOWN_STEP", f"Passo não reconhecido: {step_name}"

        if strategy_key != "DISCARD":
            update_project_manifest(root_dir=".", target_files=[])
            return True, "APPLIED", "Mudança aplicada com sucesso."
        return True, "DISCARDED", "Mudança descartada"

    def _apply_changes_in_dir(self, files_to_update, base_dir: Path) -> None:
        """Aplica mudanças em arquivos dentro de um diretório específico."""
        for item in files_to_update:
            rel_path = Path(item.get("file_path"))
            new_content = item.get("new_content", "")
            target = base_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(new_content)

    def _evaluate_benchmark(self, metrics_a: dict, metrics_b: dict) -> bool:
        """Avalia se a versão B é aceitável em relação à versão A."""
        if metrics_b.get("exit_code") != 0:
            return False
        if metrics_b.get("execution_time", 0) > metrics_a.get("execution_time", 0) * 1.2:
            return False
        return True

    def run(self, benchmark_mode: bool = False) -> None:
        """Executa o ciclo de evolução com capacidade de auto-correção.
        
        Args:
            benchmark_mode: Se True, executa apenas benchmark
        """
        if benchmark_mode:
            self._generate_manifest()
            self._run_engineer_phase()
            strategy_key = self._run_maestro_phase()
            self._execute_validation_strategy(strategy_key, benchmark_mode=True)
            return

        while True:
            self.config = self.load_config()
            self._generate_manifest()
            
            if not self._run_engineer_phase():
                break
                
            strategy_key = self._run_maestro_phase()
            if not strategy_key:
                break
                
            success, reason, context = self._execute_validation_strategy(strategy_key)
            
            if success or reason == "USER_CANCELLED":
                break

            if reason in {"SYNTAX_ERROR", "PYTEST_FAILURE"}:
                previous_objective = self.current_objective
                self.current_objective = f"""
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


# Objetivo inicial de meta-nível utilizado para demonstrar a nova arquitetura
initial_objective = (
    "A estratégia 'SYNTAX_AND_BENCHMARK' é útil, mas incompleta. "
    "Uma mudança de performance também deveria ser validada funcionalmente. "
    "Sua tarefa é modificar o arquivo 'hephaestus_config.json' para que a estratégia 'SYNTAX_AND_BENCHMARK' também inclua o passo 'run_pytest_validation', executando-o antes do benchmark."
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("objective", nargs="?", default=initial_objective)
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()

    agent = HephaestusAgent(args.objective)
    agent.run(args.benchmark)
