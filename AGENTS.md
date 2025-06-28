# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    hephaestus.log
    example_config.json
    AGENTS.md
    HEPHAESTUS_MEMORY.json
    main.py
    ROADMAP.md
    ANALISE_GERAL.md
    hephaestus_config.json
    requirements.txt
    MANIFESTO.md
    evolution_log.csv
    ISSUES.md
    agent/
        deep_validator.py
        brain.py
        __init__.py
        git_utils.py
        code_validator.py
        agents.py
        patch_applicator.py
        cycle_runner.py
        memory.py
        tool_executor.py
        project_scanner.py
        state.py
        validation_steps/
            pytest_validator.py
            self_improvement_validator.py
            __init__.py
            base.py
            patch_applicator.py
            syntax_validator.py
            pytest_new_file_validator.py
        scanner/
        utils/
            __init__.py
            llm_client.py
    hephaestus_agent/
        scanner/

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Arquivo: `main.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Arquivo: `agent/deep_validator.py`
- **Função:** `analyze_complexity(code_string: str)`
  - *Analyzes the cyclomatic complexity and other metrics of the given Python code string using Radon.*
- **Função:** `calculate_quality_score(complexity_report: dict, duplication_report: list)`
  - *Calculates a quality score based on complexity, duplication, and other code metrics.*
- **Função:** `_get_code_lines(code_string: str, strip_comments_blanks: bool=True)`
  - *Returns a list of (original_line_number, line_content) tuples.*
- **Função:** `_find_duplicates_for_block(block_to_check: list[str], all_lines: list[tuple[int, str]], start_index: int, min_lines: int)`
  - *Finds occurrences of block_to_check in all_lines, starting after start_index.*
- **Função:** `detect_code_duplication(code_string: str, min_lines: int=4, strip_comments_and_blanks: bool=True)`
  - *Detects duplicated code blocks in the given Python code string.*

### Arquivo: `agent/brain.py`
- **Função:** `generate_next_objective(api_key: str, model: str, current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None)`
  - *Generates the next evolutionary objective using a lightweight model and code analysis.*
- **Função:** `generate_capacitation_objective(api_key: str, model: str, engineer_analysis: str, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None, logger: Optional[logging.Logger]=None)`
  - *Generates an objective to create necessary new capabilities.*
- **Função:** `generate_commit_message(api_key: str, model: str, analysis_summary: str, objective: str, logger: logging.Logger, base_url: str='https://openrouter.ai/api/v1')`
  - *Generates a concise and informative commit message using an LLM.*

### Arquivo: `agent/__init__.py`

### Arquivo: `agent/git_utils.py`
- **Função:** `initialize_git_repository(logger: logging.Logger)`
  - *Ensure a git repository exists and is configured.*

### Arquivo: `agent/code_validator.py`
- **Função:** `perform_deep_validation(file_path: Path, logger: logging.Logger)`
  - *Realiza uma análise profunda da qualidade do código Python.*
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool=True)`
  - *Valida se o código Python em um arquivo é sintaticamente correto e, opcionalmente, realiza uma análise profunda.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Arquivo: `agent/agents.py`
- **Função:** `parse_json_response(raw_str: str, logger: logging.Logger)`
  - *Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.*
- **Classe:** `ArchitectAgent`
- **Classe:** `MaestroAgent`

### Arquivo: `agent/patch_applicator.py`
- **Função:** `_handle_insert(full_path: Path, lines: list[str], instruction: dict, logger: logging.Logger)`
  - *Apply an INSERT patch and return ``(success, updated_lines)``.*
- **Função:** `_handle_replace(full_path: Path, lines: list[str], instruction: dict, logger: logging.Logger)`
  - *Apply a REPLACE patch.*
- **Função:** `_handle_delete_block(full_path: Path, lines: list[str], instruction: dict, logger: logging.Logger)`
  - *Apply a DELETE_BLOCK patch.*
- **Função:** `apply_patches(instructions: list[dict], logger: logging.Logger, base_path: str='.')`
  - *Aplica uma lista de instruções de patch aos arquivos.*

### Arquivo: `agent/cycle_runner.py`
- **Função:** `run_cycles(agent: 'HephaestusAgent')`
  - *Execute the main evolution loop for the given agent.*

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
- **Função:** `web_search(query: str)`
  - *Realiza uma pesquisa na web usando a API DuckDuckGo e retorna os resultados.*

### Arquivo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md', excluded_dir_patterns: Optional[List[str]]=None)`
- **Função:** `analyze_code_metrics(root_dir: str, excluded_dir_patterns: Optional[List[str]]=None, file_loc_threshold: int=300, func_loc_threshold: int=50, func_cc_threshold: int=10)`
  - *Analisa arquivos Python em um diretório para métricas de código como LOC e Complexidade Ciclomática.*

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

### Arquivo: `agent/validation_steps/pytest_validator.py`
- **Classe:** `PytestValidator(ValidationStep)`
  - *Runs pytest as a validation step.*

### Arquivo: `agent/validation_steps/self_improvement_validator.py`
- **Classe:** `SelfImprovementValidator`

### Arquivo: `agent/validation_steps/__init__.py`
- **Função:** `get_validation_step(name: str)`

### Arquivo: `agent/validation_steps/base.py`
- **Classe:** `ValidationStep(ABC)`
  - *Abstract base class for a validation step.*

### Arquivo: `agent/validation_steps/patch_applicator.py`
- **Classe:** `PatchApplicatorStep(ValidationStep)`
  - *Applies patches to the specified base path.*

### Arquivo: `agent/validation_steps/syntax_validator.py`
- **Classe:** `SyntaxValidator(ValidationStep)`
  - *Validates the syntax of Python and JSON files.*

### Arquivo: `agent/validation_steps/pytest_new_file_validator.py`
- **Classe:** `PytestNewFileValidator(ValidationStep)`
  - *A validation step that runs pytest specifically on newly created test files.*

### Arquivo: `agent/utils/__init__.py`

### Arquivo: `agent/utils/llm_client.py`
- **Função:** `call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: logging.Logger)`
  - *Helper function to make calls to the LLM API.*

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
