# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    AGENTS.md
    main.py
    requirements.txt
    agent/
        brain.py
        __init__.py
        project_scanner.py.bak
        file_manager.py
        code_validator.py
        tool_executor.py
        project_scanner.py

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Módulo: `main.py`

### Módulo: `agent/brain.py`
- **Função:** `get_ai_suggestion(api_key: str, model_list: List[str], project_snapshot: str, objective: str, base_url: str='https://openrouter.ai/api/v1')`
  - *Obtém sugestões de LLMs via OpenRouter API usando lista de fallback.*

### Módulo: `agent/__init__.py`

### Módulo: `agent/file_manager.py`
- **Função:** `apply_changes(files_to_update: List[Dict[str, str]])`
  - *Aplica as mudanças sugeridas pela IA nos arquivos do projeto, com backup seguro.*

### Módulo: `agent/code_validator.py`
- **Função:** `validate_python_code(code_string: str)`
  - *Valida se o código Python é sintaticamente correto usando py_compile.*

### Módulo: `agent/tool_executor.py`
- **Função:** `run_pytest(test_dir: str='tests/')`
  - *Executa testes pytest no diretório especificado e retorna resultados.*

### Módulo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md')`

## 3. FOCO DA TAREFA (CÓDIGO-FONTE COMPLETO)
