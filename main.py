from dotenv import load_dotenv
import os
import sys
import argparse
import shutil
import tempfile
from pathlib import Path

from agent.project_scanner import update_project_manifest
from agent.brain import get_ai_suggestion
from agent.file_manager import apply_changes
from agent.code_validator import validate_python_code
from agent.tool_executor import run_in_sandbox


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
    if metrics_b.get("exit_code") != 0:
        return False
    if metrics_b.get("execution_time", 0) > metrics_a.get("execution_time", 0) * 1.2:
        return False
    return True


def main(objective: str, benchmark_mode: bool = False) -> None:
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Erro: Chave da API não encontrada. Defina OPENROUTER_API_KEY no arquivo .env")
        sys.exit(1)

    target_files = []
    if "project_scanner.py" in objective:
        target_files.append("agent/project_scanner.py")

    print("Gerando manifesto do projeto (AGENTS.md)...")
    update_project_manifest(root_dir=".", target_files=target_files)
    
    # Passo 2: Carregar manifesto para contexto
    print("Carregando manifesto...")
    with open("AGENTS.md", "r", encoding="utf-8") as f:
        manifesto_content = f.read()
    
    # Exibe preview do manifesto
    print("\n--- MANIFESTO GERADO (PRIMEIROS 1000 CARACTERES) ---")
    print(f"Tamanho total do manifesto: {len(manifesto_content)} caracteres")
    print(manifesto_content[:1000] + "...")
    
    # Define lista de fallback de modelos
    MODEL_FALLBACK_LIST = [
        "deepseek/deepseek-r1-0528:free",
        "mistralai/devstral-small:free"
    ]
    
    # Obtém sugestão da IA com fallback
    print("\nSolicitando análise da IA...")
    attempt_logs = get_ai_suggestion(
        api_key=api_key,
        model_list=MODEL_FALLBACK_LIST,
        project_snapshot=manifesto_content,
        objective=objective
    )

    # Processa os logs para encontrar a primeira tentativa bem-sucedida
    successful_attempt = None
    for attempt in attempt_logs:
        if attempt["success"]:
            successful_attempt = attempt
            break

    # Trata cenários de sucesso/falha
    if successful_attempt:
        parsed_json = successful_attempt["parsed_json"]
        model_used = successful_attempt["model"]
        print(f"Resposta válida obtida do modelo: {model_used}")
    else:
        print("\n!! FALHA CRÍTICA DE COMUNICAÇÃO !!")
        print("Todos os modelos da lista falharam. Exibindo logs de cada tentativa:")
        for i, attempt in enumerate(attempt_logs):
            print(f"\n--- TENTATIVA {i+1}: MODELO {attempt['model']} ---")
            print(f"Resposta Bruta Recebida:\n{attempt['raw_response']}")
            print("--------------------------------------------------")
        sys.exit(1)

    # Verificação crítica da resposta da IA
    if parsed_json is None:
        print("\n!! ERRO CRÍTICO NO PROCESSAMENTO DA RESPOSTA DA IA !!")
        print("A resposta foi marcada como sucesso mas o conteúdo é inválido.")
        print("Exibindo resposta bruta para debug:")
        print(successful_attempt["raw_response"])
        sys.exit(1)
        
    # Validação de sintaxe do código gerado
    files_to_update = parsed_json.get("files_to_update", [])
    for file_update in files_to_update:
        is_valid, error = validate_python_code(file_update['new_content'])
        if not is_valid:
            print(f"\n!! ERRO DE SINTAXE DETECTADO NA SUGESTÃO DA IA !!")
            print(f"Arquivo alvo: {file_update['file_path']}")
            print(f"Erro: {error}")
            print("Ciclo de modificação abortado para garantir a integridade do projeto.")
            sys.exit(1)

    # Novo passo: Validação com testes pytest
    test_code = parsed_json.get("validation_pytest_code", "") or ""
    test_code = test_code.strip()
    temp_test_path = "tests/test_generated_by_agent.py"
    
    if test_code:
        print("\n--- EXECUTANDO TESTES DE VALIDAÇÃO GERADOS PELA IA ---")
        
        try:
            # Garante que o diretório de testes existe
            os.makedirs("tests", exist_ok=True)
            
            # Escreve o código de teste temporário
            with open(temp_test_path, "w", encoding="utf-8") as test_file:
                test_file.write(test_code)
            
            # Executa os testes
            from agent.tool_executor import run_pytest
            tests_passed, pytest_output = run_pytest()
            
            if tests_passed:
                print("✔ Testes de validação passaram com sucesso!")
            else:
                print("\n!! FALHA NOS TESTES DE VALIDAÇÃO !!")
                print("A execução dos testes gerados pela IA falhou:")
                print(pytest_output)
                print("Abortando a aplicação das mudanças.")
                sys.exit(1)
        except Exception as e:
            print(f"\n!! ERRO DURANTE A EXECUÇÃO DOS TESTES: {str(e)} !!")
            print("Abortando a aplicação das mudanças.")
            sys.exit(1)
        finally:
            # Limpeza: Remove arquivo de teste temporário
            if os.path.exists(temp_test_path):
                os.remove(temp_test_path)
    
    # Exibe a análise da IA
    print("\n--- ANÁLISE DA IA ---")
    print(parsed_json.get("analysis_summary", ""))
    print(f"(Modelo usado: {model_used})")

    if benchmark_mode:
        return

    print("\nExecutando benchmark A/B para validar a mudança...")

    with tempfile.TemporaryDirectory() as bench_dir:
        temp_a = Path(bench_dir) / "temp_A"
        temp_b = Path(bench_dir) / "temp_B"

        shutil.copytree(Path('.'), temp_a, dirs_exist_ok=True)
        shutil.copytree(Path('.'), temp_b, dirs_exist_ok=True)

        metrics_a = run_in_sandbox(str(temp_a), objective)

        apply_changes_in_dir(files_to_update, temp_b)
        metrics_b = run_in_sandbox(str(temp_b), objective)

    approved = evaluate_benchmark(metrics_a, metrics_b)

    print("\n--- RESULTADO DO BENCHMARK ---")
    print(f"Versão A - tempo: {metrics_a['execution_time']:.2f}s, pico memoria: {metrics_a['peak_memory_mb']:.2f}MB, exit: {metrics_a['exit_code']}")
    print(f"Versão B - tempo: {metrics_b['execution_time']:.2f}s, pico memoria: {metrics_b['peak_memory_mb']:.2f}MB, exit: {metrics_b['exit_code']}")

    if approved:
        print("Mudança aprovada pelo benchmark. Aplicando...")
        report = apply_changes(files_to_update)
        if report['status'] == 'success' and report['changes']:
            update_project_manifest(root_dir=".", target_files=[])
        print("Aplicação concluída.")
    else:
        print("Mudança rejeitada pelo benchmark. Nenhum arquivo foi alterado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("objective", nargs="?", default="Analise o arquivo project_scanner.py e sugira uma melhoria de performance ou clareza no código.")
    parser.add_argument("--benchmark", action="store_true")
    args = parser.parse_args()

    main(args.objective, args.benchmark)
