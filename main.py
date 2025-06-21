from dotenv import load_dotenv
import os
import sys
from agent.project_scanner import update_project_manifest
from agent.brain import get_ai_suggestion
from agent.file_manager import apply_changes
from agent.code_validator import validate_python_code

if __name__ == "__main__":
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Obtém a chave da API
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Erro: Chave da API não encontrada. Defina OPENROUTER_API_KEY no arquivo .env")
        sys.exit(1)
    
    # Define o objetivo para a IA
    objective = (
        "Analise o arquivo project_scanner.py e "
        "sugira uma melhoria de performance ou clareza no código."
    )
    
    # Determina arquivos alvo com base no objetivo
    target_files = []
    if "project_scanner.py" in objective:
        target_files.append("agent/project_scanner.py")
    
    # Passo 1: Gerar manifesto do projeto (AGENTS.md)
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
    
    # Confirmação do usuário
    user_input = input("\nAplicar as mudanças? (s/n): ").strip().lower()
    
    if user_input == 's':
        print("\nAplicando mudanças...")
        report = apply_changes(parsed_json.get("files_to_update", []))
        
        print("\n--- RELATÓRIO DE MUDANÇAS ---")
        print(f"Status geral: {report['status']}")
        
        if report['changes']:
            print("\nArquivos modificados:")
            for change in report['changes']:
                print(f"- {change['file']} (backup: {change['backup']})")
                
        if report['errors']:
            print("\nErros encontrados:")
            for error in report['errors']:
                print(f"- {error}")
        
        # Ressincronização do manifesto após mudanças bem-sucedidas
        if report['status'] == 'success' and report['changes']:
            print("\nRessincronizando o manifesto do projeto após as mudanças...")
            update_project_manifest(root_dir=".", target_files=[])
            print("Manifesto AGENTS.md atualizado com o novo estado do projeto.")
    else:
        print("\nOperação cancelada pelo usuário.")
