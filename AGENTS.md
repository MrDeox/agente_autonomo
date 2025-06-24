# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    hephaestus.log
    example_config.json
    AGENTS.md
    HEPHAESTUS_MEMORY.json
    main.py
    hephaestus_config.json
    requirements.txt
    MANIFESTO.md
    evolution_log.csv
    ISSUES.md
    agent/
        deep_validator.py
        brain.py
        __init__.py
        code_validator.py
        agents.py
        patch_applicator.py
        memory.py
        tool_executor.py
        project_scanner.py
        state.py

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Arquivo: `main.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Arquivo: `agent/deep_validator.py`
- **Função:** `analyze_complexity(code_string: str)`
  - *Analyzes the cyclomatic complexity and other metrics of the given Python code string using Radon.*
- **Função:** `detect_code_duplication(code_string: str, min_lines: int=5)`
  - *Detects duplicated code blocks in the given Python code string.*
- **Função:** `calculate_quality_score(complexity_report: dict, duplication_report: list)`
  - *Calculates a quality score based on complexity, duplication, and other code metrics.*
- **Função:** `_get_code_lines(code_string: str, strip_comments_blanks: bool=True)`
  - *Returns a list of (original_line_number, line_content) tuples.*
- **Função:** `_find_duplicates_for_block(block_to_check: list[str], all_lines: list[tuple[int, str]], start_index: int, min_lines: int)`
  - *Finds occurrences of block_to_check in all_lines, starting after start_index.*
- **Função:** `detect_code_duplication(code_string: str, min_lines: int=4, strip_comments_and_blanks: bool=True)`
  - *Detects duplicated code blocks in the given Python code string.*

### Arquivo: `agent/brain.py`
- **Função:** `_call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: Any)`
  - *Função auxiliar para fazer chamadas à API LLM.*
- **Função:** `generate_next_objective(api_key: str, model: str, current_manifest: str, logger: Any, project_root_dir: str, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None)`
  - *Gera o próximo objetivo evolutivo usando um modelo leve e análise de código.*
- **Função:** `generate_capacitation_objective(api_key: str, model: str, engineer_analysis: str, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None, logger: Optional[Any]=None)`
  - *Gera um objetivo para criar novas capacidades necessárias.*
- **Função:** `generate_commit_message(api_key: str, model: str, analysis_summary: str, objective: str, logger: Any, base_url: str='https://openrouter.ai/api/v1')`
  - *Gera uma mensagem de commit concisa e informativa usando um LLM.*

### Arquivo: `agent/__init__.py`

### Arquivo: `agent/code_validator.py`
- **Função:** `perform_deep_validation(file_path: Path, logger: logging.Logger)`
  - *Realiza uma análise profunda da qualidade do código Python.*
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool=True)`
  - *Valida se o código Python em um arquivo é sintaticamente correto e, opcionalmente, realiza uma análise profunda.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Arquivo: `agent/agents.py`
- **Função:** `parse_json_response(raw_str: str, logger: Any)`
  - *Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.*
- **Função:** `_call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: Any)`
  - *Função auxiliar para fazer chamadas à API LLM.*
- **Classe:** `ArchitectAgent`
- **Classe:** `MaestroAgent`

### Arquivo: `agent/patch_applicator.py`
- **Função:** `apply_patches(instructions: list[dict], logger: logging.Logger, base_path: str='.')`
  - *Aplica uma lista de instruções de patch aos arquivos.*

### Arquivo: `agent/memory.py`
- **Classe:** `Memory`
  - *Manages persistent memory for the Hephaestus agent, storing historical data*

### Arquivo: `agent/tool_executor.py`
- **Função:** `run_pytest(test_dir: str='tests/', cwd: str | Path | None=None)`
  - *Executa testes pytest no diretório especificado e retorna resultados.*
- **Função:** `check_file_existence(file_paths: list[str])`
  - *Verifica se todos os arquivos especificados existem.*
- **Função:** `run_in_sandbox(temp_dir_path: str, objective: str)`
  - *Executa o main.py de um diretório isolado monitorando tempo e memória.*
- **Função:** `run_git_command(command: list[str])`
  - *Executa um comando Git e retorna o status e a saída.*

### Arquivo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md', excluded_dir_patterns: Optional[List[str]]=None)`
- **Função:** `analyze_code_metrics(root_dir: str, excluded_dir_patterns: Optional[List[str]]=None, file_loc_threshold: int=300, func_loc_threshold: int=50, func_cc_threshold: int=10)`
  - *Analisa arquivos Python em um diretório para métricas de código como LOC e Complexidade Ciclomática.*

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
