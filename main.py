from dotenv import load_dotenv
import os
import sys
from agent.project_scanner import generate_project_snapshot
from agent.brain import get_ai_suggestion
from agent.file_manager import apply_changes

if __name__ == "__main__":
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Obtém a chave da API
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Erro: Chave da API não encontrada. Defina OPENROUTER_API_KEY no arquivo .env")
        sys.exit(1)
    
    # Gera o snapshot do projeto
    print("Gerando snapshot do projeto...")
    snapshot = generate_project_snapshot(root_dir=".", use_gitignore=True)
    
    # Define o objetivo para a IA
    objective = (
        "Analise o arquivo project_scanner.py e "
        "sugira uma melhoria de performance ou clareza no código."
    )
    
    # Obtém sugestão da IA
    print("\nSolicitando análise da IA...")
    model = "deepseek/deepseek-chat-v3-0324:free"
    suggestion = get_ai_suggestion(
        api_key=api_key,
        model=model,
        project_snapshot=snapshot,
        objective=objective
    )
    
    # Exibe os resultados
    print("\n--- SUGESTÃO DA IA ---")
    print(suggestion)
    
    # Confirmação do usuário
    user_input = input("\nAs sugestões parecem boas. Aplicar as mudanças? (s/n): ").strip().lower()
    
    if user_input == 's':
        print("\nAplicando mudanças...")
        report = apply_changes(suggestion)
        
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
    else:
        print("\nOperação cancelada pelo usuário.")
