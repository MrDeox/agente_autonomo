# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    hephaestus.log
    AGENTS.md
    CONTRIBUTING.md
    HEPHAESTUS_MEMORY.json
    main.py
    ROADMAP.md
    requirements.txt
    MANIFESTO.md
    evolution_log.csv
    CODE_OF_CONDUCT.md
    ANALISE_PERFORMANCE_HEPHAESTUS.md
    ISSUES.md
    CAPABILITIES.md
    app.py # Novo: Aplicação FastAPI
    config/
        default.yaml
        base_config.yaml
        example_config.yaml
        models/
            main.yaml
        validation_strategies/
            main.yaml
    agent/
        __init__.py
        brain.py
        code_metrics.py # Renomeado de deep_validator.py
        code_validator.py
        config_loader.py
        cycle_runner.py
        git_utils.py
        hephaestus_agent.py
        memory.py
        patch_applicator.py
        project_scanner.py
        prompt_builder.py # Novo
        queue_manager.py
        state.py
        tool_executor.py
        agents/ # Novo pacote para agentes especializados
            __init__.py
            architect_agent.py
            maestro_agent.py
            error_analyzer.py # Movido
            error_correction.py # Movido
            performance_analyzer.py # Movido
        utils/
            __init__.py
            json_parser.py # Novo
            llm_client.py
        validation_steps/
            pytest_validator.py
            __init__.py
            base.py
            patch_applicator.py
            syntax_validator.py
            pytest_new_file_validator.py
            # Outros validadores podem ser adicionados aqui conforme necessário.
        # A listagem do scanner/ foi removida pois o diretório está vazio ou não é relevante para interfaces.
        # A listagem duplicada de utils/ foi removida. utils/ é listado acima com seu conteúdo.

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Arquivo: `app.py`
- **Função:** `submit_objective(obj: Objective)`
  - *Endpoint para submeter novos objetivos ao agente.*
- **Função:** `get_status()`
  - *Endpoint para verificar o status do servidor e da fila.*

### Arquivo: `agent/hephaestus_agent.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo. Movida de `main.py`.*

### Arquivo: `agent/queue_manager.py`
- **Classe:** `QueueManager`
  - *Gerencia uma fila de objetivos para processamento assíncrono.*

### Arquivo: `agent/config_loader.py`
- **Função:** `load_config()`
  - *Carrega a configuração do agente utilizando Hydra. As configurações são definidas em arquivos YAML dentro do diretório `config/` (iniciando por `default.yaml`). Não há mais fallback para arquivos JSON.*

### Arquivo: `agent/code_metrics.py`
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
- **Função:** `generate_next_objective(model_config: Dict[str, str], current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, memory_summary: Optional[str]=None, current_objective: Optional[str]=None)`
  - *Gera o próximo objetivo evolutivo usando um modelo de LLM e análise de código. A construção detalhada dos prompts é delegada ao módulo `agent.prompt_builder`. Aprimorado para meta-análise e otimização de prompts.*
- **Função:** `generate_capacitation_objective(model_config: Dict[str, str], engineer_analysis: str, memory_summary: Optional[str]=None, logger: Optional[logging.Logger]=None)`
  - *Generates an objective to create necessary new capabilities.*
- **Função:** `generate_commit_message(model_config: Dict[str, str], analysis_summary: str, objective: str, logger: logging.Logger)`
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

# A seção para o antigo agent/agents.py foi removida.
# ArchitectAgent e MaestroAgent serão documentados em seus novos arquivos.
# parse_json_response será documentado em agent/utils/json_parser.py.

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
- **Função:** `run_cycles(agent: 'HephaestusAgent', queue_manager: QueueManager)`
  - *Execute o loop principal de evolução para o agente, processando objetivos da fila.*

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

### Arquivo: `agent/agents/architect_agent.py`
- **Classe:** `ArchitectAgent`
  - `__init__(self, model_config: Dict[str, str], logger: logging.Logger)`
  - `plan_action(self, objective: str, manifest: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]`
    - *Gera um plano de patches JSON com base no objetivo e no manifesto do projeto.*

### Arquivo: `agent/agents/error_analyzer.py`
- **Classe:** `ErrorAnalysisAgent`
  - `__init__(self, model_config: Dict[str, str], logger: logging.Logger)`
  - `analyze_error(self, failed_objective: str, error_reason: str, error_context: str, original_patches: Optional[str] = None, failed_code_snippet: Optional[str] = None, test_output: Optional[str] = None) -> Dict[str, Any]`
    - *Analisa uma falha e sugere um curso de ação, retornando um dicionário com classificação, tipo de sugestão, prompt sugerido e detalhes.*

### Arquivo: `agent/agents/error_correction.py`
- **Classe:** `ErrorCorrectionAgent`
  - `__init__(self, api_key: str, model: str, logger)` # Assinatura do construtor como no código
  - `generate_fix(self, error_context: Dict[str, Any]) -> Tuple[str, str]`
    - *Gera uma ação corretiva (patch ou novo objetivo) com base no contexto do erro.*

### Arquivo: `agent/agents/maestro_agent.py`
- **Classe:** `MaestroAgent`
  - `__init__(self, model_config: Dict[str, str], config: Dict[str, Any], logger: logging.Logger)`
  - `choose_strategy(self, action_plan_data: Dict[str, Any], memory_summary: Optional[str] = None) -> List[Dict[str, Any]]`
    - *Analisa o plano de patches e o histórico para decidir a melhor estratégia de validação ou se é necessária capacitação.*

### Arquivo: `agent/agents/performance_analyzer.py`
- **Classe:** `PerformanceAnalysisAgent`
  - `__init__(self, evolution_log_path="evolution_log.csv")`
  - `analyze_performance(self) -> str`
    - *Analisa o log de evolução para gerar um resumo de performance.*

### Arquivo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md', excluded_dir_patterns: Optional[List[str]]=None)`
- **Função:** `analyze_code_metrics(root_dir: str, excluded_dir_patterns: Optional[List[str]]=None, file_loc_threshold: int=300, func_loc_threshold: int=50, func_cc_threshold: int=10)`
  - *Analisa arquivos Python em um diretório para métricas de código como LOC e Complexidade Ciclomática.*

### Arquivo: `agent/prompt_builder.py`
- **Função:** `build_memory_context_section(memory_summary: Optional[str]) -> str`
  - *Constrói a seção de contexto da memória para os prompts.*
- **Função:** `build_initial_objective_prompt(memory_context_section: str) -> str`
  - *Constrói o prompt para gerar o objetivo inicial.*
- **Função:** `build_meta_analysis_objective_prompt(current_objective: str, original_failed_objective: str, error_reason_for_meta: str, performance_summary_str: str, memory_context_section: str) -> str`
  - *Constrói o prompt para gerar um objetivo estratégico após uma meta-análise de falha.*
- **Função:** `build_standard_objective_prompt(memory_context_section: str, performance_summary_str: str, code_analysis_summary_str: str, current_manifest: str) -> str`
  - *Constrói o prompt padrão para gerar o próximo objetivo estratégico.*

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

# Entrada duplicada para agent/error_analyzer.py removida. A correta está sob agent/agents/.

### Arquivo: `agent/validation_steps/pytest_validator.py`
- **Classe:** `PytestValidator(ValidationStep)`
  - *Runs pytest as a validation step.*

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

### Arquivo: `agent/utils/json_parser.py`
- **Função:** `parse_json_response(raw_str: str, logger: logging.Logger)`
  - *Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.*

### Arquivo: `agent/utils/llm_client.py`
- **Função:** `call_gemini_api(model: str, prompt: str, temperature: float, logger: logging.Logger)`
  - *Calls the Google Gemini API.*
- **Função:** `call_openrouter_api(model: str, prompt: str, temperature: float, logger: logging.Logger)`
  - *Calls a generic OpenAI-compatible API (like OpenRouter).*
- **Função:** `call_llm_with_fallback(model_config: Dict[str, str], prompt: str, temperature: float, logger: logging.Logger)`
  - *Orchestrates LLM calls with a primary and fallback model.*

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
