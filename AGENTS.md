# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    hephaestus.log
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
        code_validator.py.bak
        code_validator.py
        patch_applicator.py
        tool_executor.py
        project_scanner.py
    tests/
        __init__.py
        test_hephaestus.py

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Módulo: `main.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Módulo: `agent/brain.py`
- **Função:** `_call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: Any)`
  - *Função auxiliar para fazer chamadas à API LLM.*
- **Função:** `get_action_plan(api_key: str, model: str, objective: str, manifest: str, logger: Any, base_url: str='https://openrouter.ai/api/v1')`
  - *Fase 2 (Arquiteto): Pega o objetivo e o manifesto, e retorna um plano de patches em JSON.*
- **Função:** `generate_next_objective(api_key: str, model: str, current_manifest: str, logger: Any, base_url: str='https://openrouter.ai/api/v1')`
  - *Gera o próximo objetivo evolutivo usando um modelo leve.*
- **Função:** `generate_capacitation_objective(api_key: str, model: str, engineer_analysis: str, base_url: str='https://openrouter.ai/api/v1')`
  - *Gera um objetivo para criar novas capacidades necessárias.*
- **Função:** `get_maestro_decision(api_key: str, model_list: List[str], engineer_response: Dict[str, Any], config: Dict[str, Any], base_url: str='https://openrouter.ai/api/v1')`
  - *Consulta a LLM para decidir qual estratégia de validação adotar.*

### Módulo: `agent/__init__.py`

### Módulo: `agent/code_validator.py`
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger)`
  - *Valida se o código Python em um arquivo é sintaticamente correto usando py_compile.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Módulo: `agent/patch_applicator.py`
- **Função:** `apply_patches(instructions: list[dict], logger: logging.Logger, base_path: str='.')`
  - *Aplica uma lista de instruções de patch aos arquivos.*

### Módulo: `agent/tool_executor.py`
- **Função:** `run_pytest(test_dir: str='tests/')`
  - *Executa testes pytest no diretório especificado e retorna resultados.*
- **Função:** `check_file_existence(file_paths: list[str])`
  - *Verifica se todos os arquivos especificados existem.*
- **Função:** `run_in_sandbox(temp_dir_path: str, objective: str)`
  - *Executa o main.py de um diretório isolado monitorando tempo e memória.*

### Módulo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md')`

### Módulo: `tests/__init__.py`

### Módulo: `tests/test_hephaestus.py`
- **Função:** `test_dummy()`

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
