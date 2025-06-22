# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    main.py.bak
    AGENTS.md
    main.py
    hephaestus_config.json
    requirements.txt
    hephaestus_config.json.bak
    agent/
        tool_executor.py.bak
        brain.py
        __init__.py
        project_scanner.py.bak
        file_manager.py
        code_validator.py.bak
        code_validator.py
        tool_executor.py
        project_scanner.py

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Módulo: `main.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Módulo: `agent/brain.py`
- **Função:** `get_ai_suggestion(api_key: str, model_list: List[str], project_snapshot: str, objective: str, base_url: str='https://openrouter.ai/api/v1')`
  - *Obtém sugestões de LLMs via OpenRouter API usando lista de fallback.*
- **Função:** `get_maestro_decision(api_key: str, model_list: List[str], engineer_response: Dict[str, Any], config: Dict[str, Any], base_url: str='https://openrouter.ai/api/v1')`
  - *Consulta a LLM para decidir qual estratégia de validação adotar.*

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
- **Função:** `run_in_sandbox(temp_dir_path: str, objective: str)`
  - *Executa o main.py de um diretório isolado monitorando tempo e memória.*

### Módulo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md')`

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
