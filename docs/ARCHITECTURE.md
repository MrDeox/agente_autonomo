# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    NIGHT_WORK_SUMMARY.md
    README.md
    hephaestus.log
    META_INTELLIGENCE_SYSTEM.md
    cli.py
    monitor_evolution.py
    AGENTS.md
    EXEMPLO_INTEGRACAO_FLOW_MODIFIER.md
    poetry.lock
    CONTRIBUTING.md
    app.py
    HEPHAESTUS_MEMORY.json
    main.py
    ROADMAP.md
    ANALISE_OTIMIZACAO_LLM_CALLS.md
    ANALISE_PROFUNDA_SISTEMA.md
    night_agent.log
    hephaestus_config.json
    requirements.txt
    run_agent.py
    RESUMO_OTIMIZACOES_LLM.md
    MANIFESTO.md
    evolution_log.csv
    CODE_OF_CONDUCT.md
    ANALISE_PERFORMANCE_HEPHAESTUS.md
    ISSUES.md
    NIGHT_AGENT_README.md
    night_agent.py
    ANALISE_TECNICA_HEPHAESTUS.md
    night_report_20250704_004455.json
    Sugestões de Melhoria para o Projeto Agente Autônomo.md
    CAPABILITIES.md
    pyproject.toml
    agent/
        brain.py
        __init__.py
        code_metrics.py
        hephaestus_agent.py
        hephaestus_config.json
        git_utils.py
        meta_cognitive_controller.py
        code_validator.py
        meta_intelligence_core.py
        flow_self_modifier.py
        patch_applicator.py
        cycle_runner.py
        memory.py
        cognitive_evolution_manager.py
        prompt_builder.py
        tool_executor.py
        project_scanner.py
        queue_manager.py
        state.py
        config_loader.py
        validation_steps/
            pytest_validator.py
            __init__.py
            base.py
            patch_applicator.py
            syntax_validator.py
            pytest_new_file_validator.py
        agents/
            capability_gap_detector.py
            __init__.py
            self_reflection_agent.py
            architect_agent.py
            performance_analyzer.py
            error_correction.py
            code_review_agent.py
            maestro_agent.py
            prompt_optimizer.py
            error_analyzer.py
        utils/
            __init__.py
            json_parser.py
            smart_validator.py
            llm_client.py
            llm_optimizer.py
            advanced_logging.py
            error_handling.py
            intelligent_cache.py
            ux_enhancer.py
            night_improvements.py
    config/
        example_config.yaml
        base_config.yaml
        default.yaml
        models/
            main.yaml
        validation_strategies/
            main.yaml

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Arquivo: `cli.py`
- **Função:** `run(continuous: bool=typer.Option(False, '--continuous', '-c', help='Run in continuous mode'), max_cycles: int=typer.Option(None, '--max-cycles', '-m', help='Maximum number of evolution cycles'))`
  - *Run the Hephaestus agent*
- **Função:** `submit(objective: str)`
  - *Submit a new objective to the agent*
- **Função:** `status()`
  - *Check agent status*

### Arquivo: `monitor_evolution.py`
- **Classe:** `EvolutionMonitor`
  - *Monitor inteligente para acompanhar a evolução do sistema*
- **Função:** `main()`
  - *Função principal*

### Arquivo: `app.py`
- **Classe:** `Objective(BaseModel)`
- **Função:** `startup_event()`
- **Função:** `submit_objective(obj: Objective)`
- **Função:** `get_status()`

### Arquivo: `main.py`

### Arquivo: `run_agent.py`

### Arquivo: `night_agent.py`
- **Classe:** `NightAgent`
  - *Agente noturno que trabalha continuamente melhorando o sistema*

### Arquivo: `agent/brain.py`
- **Função:** `generate_next_objective(model_config: Dict[str, str], current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, memory_summary: Optional[str]=None, current_objective: Optional[str]=None)`
  - *Generates the next evolutionary objective using a lightweight model and code analysis.*
- **Função:** `generate_capacitation_objective(model_config: Dict[str, str], engineer_analysis: str, memory_summary: Optional[str]=None, logger: Optional[logging.Logger]=None)`
  - *Generates an objective to create necessary new capabilities.*
- **Função:** `generate_commit_message(analysis_summary: str, objective: str, logger: logging.Logger)`
  - *Generates a concise and informative commit message using a rule-based system.*

### Arquivo: `agent/__init__.py`

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

### Arquivo: `agent/hephaestus_agent.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Arquivo: `agent/git_utils.py`
- **Função:** `initialize_git_repository(logger: logging.Logger)`
  - *Ensure a git repository exists and is configured.*

### Arquivo: `agent/meta_cognitive_controller.py`
- **Classe:** `FlowModificationType(Enum)`
  - *Types of modifications the system can make to LLM flows*
- **Classe:** `LLMCallPoint`
  - *Represents a point in the code where an LLM call is made*
- **Classe:** `FlowModification`
  - *Represents a proposed modification to the LLM flow*
- **Classe:** `MetaCognitiveController`
  - *Controller that monitors and modifies LLM call flows dynamically.*

### Arquivo: `agent/code_validator.py`
- **Função:** `perform_deep_validation(file_path: Path, logger: logging.Logger)`
  - *Realiza uma análise profunda da qualidade do código Python.*
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool=True)`
  - *Valida se o código Python em um arquivo é sintaticamente correto e, opcionalmente, realiza uma análise profunda.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Arquivo: `agent/meta_intelligence_core.py`
- **Classe:** `PromptGene`
  - *A genetic component of a prompt*
- **Classe:** `AgentBlueprint`
  - *Blueprint for creating a new agent*
- **Classe:** `CognitiveArchitecture`
  - *Defines how an agent thinks and processes information*
- **Classe:** `PromptEvolutionEngine`
  - *Evolves prompts using genetic algorithms and performance feedback*
- **Classe:** `AgentGenesisFactory`
  - *Creates new agents when capability gaps are detected*
- **Classe:** `MetaIntelligenceCore`
  - *The ultimate meta-cognitive controller that orchestrates all self-improvement*
- **Função:** `get_meta_intelligence(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global meta-intelligence instance*

### Arquivo: `agent/flow_self_modifier.py`
- **Classe:** `CallContext`
  - *Context for an LLM call*
- **Classe:** `CallDecision`
  - *Decision about whether and how to make an LLM call*
- **Classe:** `FlowSelfModifier`
  - *A practical implementation of dynamic flow modification.*
- **Função:** `get_flow_modifier(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global flow modifier instance.*
- **Função:** `optimize_llm_call(agent_type: str)`
  - *Decorator to automatically optimize LLM calls.*

### Arquivo: `agent/patch_applicator.py`
- **Classe:** `PatchOperationHandler(ABC)`
  - *Abstract base class for a patch operation handler.*
- **Classe:** `InsertHandler(PatchOperationHandler)`
  - *Handler for INSERT operations.*
- **Classe:** `ReplaceHandler(PatchOperationHandler)`
  - *Handler for REPLACE operations.*
- **Classe:** `DeleteBlockHandler(PatchOperationHandler)`
  - *Handler for DELETE_BLOCK operations.*
- **Função:** `get_handler(operation: str)`
  - *Factory function to get the correct handler for an operation.*
- **Função:** `apply_patches(instructions: List[Dict[str, Any]], logger: logging.Logger, base_path: str='.')`
  - *Aplica uma lista de instruções de patch aos arquivos.*

### Arquivo: `agent/cycle_runner.py`
- **Classe:** `CycleRunner`
  - *Manages the main execution loop of the Hephaestus agent.*
- **Função:** `run_cycles(agent: 'HephaestusAgent', queue_manager: QueueManager)`
  - *Execute the main evolution loop for the given agent.*

### Arquivo: `agent/memory.py`
- **Classe:** `SemanticPattern`
  - *Represents a learned pattern in objectives or strategies.*
- **Classe:** `Heuristic`
  - *Represents a learned heuristic about what works and what doesn't.*
- **Classe:** `SemanticCluster`
  - *Groups similar objectives/strategies for pattern recognition.*
- **Classe:** `Memory`
  - *Manages persistent memory for the Hephaestus agent, storing historical data*

### Arquivo: `agent/cognitive_evolution_manager.py`
- **Classe:** `EvolutionEvent`
  - *Represents a significant evolutionary event in the system*
- **Classe:** `CognitiveEvolutionManager`
  - *The master controller for cognitive evolution.*
- **Função:** `get_evolution_manager(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global evolution manager*
- **Função:** `start_cognitive_evolution(model_config: Dict[str, str], logger: logging.Logger)`
  - *Start the cognitive evolution process*

### Arquivo: `agent/prompt_builder.py`
- **Função:** `build_memory_context_section(memory_summary: Optional[str])`
  - *Constrói a seção de contexto da memória para os prompts.*
- **Função:** `build_initial_objective_prompt(memory_context_section: str)`
  - *Constrói o prompt para gerar o objetivo inicial quando não há manifesto ou análise de código.*
- **Função:** `build_meta_analysis_objective_prompt(current_objective: str, original_failed_objective: str, error_reason_for_meta: str, performance_summary_str: str, memory_context_section: str, capabilities_content: str, roadmap_content: str)`
  - *Constrói o prompt para gerar um objetivo estratégico após uma meta-análise de falha.*
- **Função:** `build_standard_objective_prompt(memory_context_section: str, performance_summary_str: str, code_analysis_summary_str: str, current_manifest: str, capabilities_content: str, roadmap_content: str)`
  - *Constrói o prompt padrão para gerar o próximo objetivo estratégico.*

### Arquivo: `agent/tool_executor.py`
- **Função:** `run_pytest(test_dir: str='tests/', cwd: str | Path | None=None)`
  - *Executa testes pytest no diretório especificado e retorna resultados.*
- **Função:** `check_file_existence(file_paths: list[str])`
  - *Verifica se todos os arquivos especificados existem.*
- **Função:** `run_in_sandbox(temp_dir_path: str, objective: str)`
  - *Executa o main.py de um diretório isolado monitorando tempo e memória.*
- **Função:** `run_git_command(command: list[str])`
  - *Executa um comando Git e retorna o status e a saída.*
- **Função:** `web_search(query: str, max_results: int=5, context: str='')`
  - *Realiza uma pesquisa na web inteligente usando múltiplas estratégias.*
- **Função:** `_optimize_search_query(query: str, context: str)`
  - *Otimiza a query de busca baseada no contexto.*
- **Função:** `_create_fallback_query(query: str, context: str)`
  - *Cria uma query de fallback mais específica.*
- **Função:** `_search_duckduckgo(query: str, max_results: int)`
  - *Realiza busca no DuckDuckGo.*
- **Função:** `_process_and_rank_results(results: list, original_query: str, context: str)`
  - *Processa e ranqueia resultados por relevância.*
- **Função:** `_calculate_relevance_score(result: dict, query_words: set, context_words: set)`
  - *Calcula score de relevância para um resultado.*
- **Função:** `_format_search_results(results: list)`
  - *Formata os resultados de busca para exibição.*
- **Função:** `advanced_web_search(query: str, search_type: str='general', context: dict | None=None)`
  - *Busca web avançada com diferentes tipos de pesquisa otimizados.*
- **Função:** `_optimize_query_by_type(query: str, search_type: str, context: dict)`
  - *Otimiza query baseada no tipo de busca.*
- **Função:** `_process_results_by_type(raw_results: str, search_type: str, context: dict)`
  - *Processa resultados baseado no tipo de busca.*
- **Função:** `_create_results_summary(results: list, search_type: str)`
  - *Cria um resumo dos resultados encontrados.*
- **Função:** `_create_recommendations(results: list, search_type: str, context: dict)`
  - *Cria recomendações baseadas nos resultados.*

### Arquivo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
- **Função:** `_extract_skeleton(code_string: str)`
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md', excluded_dir_patterns: Optional[List[str]]=None)`
- **Função:** `analyze_code_metrics(root_dir: str, excluded_dir_patterns: Optional[List[str]]=None, file_loc_threshold: int=300, func_loc_threshold: int=50, func_cc_threshold: int=10)`
  - *Analisa arquivos Python em um diretório para métricas de código como LOC e Complexidade Ciclomática.*

### Arquivo: `agent/queue_manager.py`
- **Classe:** `QueueManager`

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

### Arquivo: `agent/config_loader.py`
- **Função:** `load_config()`
  - *Load configuration using Hydra.*

### Arquivo: `agent/validation_steps/pytest_validator.py`
- **Classe:** `PytestValidator(ValidationStep)`
  - *Runs pytest as a validation step.*

### Arquivo: `agent/validation_steps/__init__.py`
- **Classe:** `BenchmarkValidator(ValidationStep)`
- **Classe:** `CheckFileExistenceValidator(ValidationStep)`
- **Classe:** `ValidateJsonSyntax(ValidationStep)`
  - *Validates the syntax of JSON files mentioned in patches.*
- **Função:** `get_validation_step(name: str)`

### Arquivo: `agent/validation_steps/base.py`
- **Classe:** `ValidationStep(ABC)`
  - *Abstract base class for a validation step.*

### Arquivo: `agent/validation_steps/patch_applicator.py`
- **Classe:** `PatchApplicatorStep(ValidationStep)`
  - *Applies patches to the specified base path.*

### Arquivo: `agent/validation_steps/syntax_validator.py`
- **Função:** `validate_config_structure(config: dict, logger: logging.Logger)`
  - *Valida a estrutura do hephaestus_config.json contra um esquema definido.*
- **Classe:** `SyntaxValidator(ValidationStep)`
  - *Validates the syntax of Python and JSON files.*

### Arquivo: `agent/validation_steps/pytest_new_file_validator.py`
- **Classe:** `PytestNewFileValidator(ValidationStep)`
  - *A validation step that runs pytest specifically on newly created test files.*

### Arquivo: `agent/agents/capability_gap_detector.py`
- **Classe:** `CapabilityGapDetector`
  - *Analyzes failure patterns and evolution history to detect when the agent*

### Arquivo: `agent/agents/__init__.py`

### Arquivo: `agent/agents/self_reflection_agent.py`
- **Classe:** `SelfReflectionAgent`
  - *Agent that analyzes the Hephaestus codebase itself to identify patterns,*

### Arquivo: `agent/agents/architect_agent.py`
- **Classe:** `ArchitectAgent`

### Arquivo: `agent/agents/performance_analyzer.py`
- **Classe:** `PerformanceAnalysisAgent`
  - *An agent dedicated to analyzing the performance of Hephaestus.*

### Arquivo: `agent/agents/error_correction.py`
- **Classe:** `ErrorCorrectionAgent`
  - *Agent for analyzing errors and generating corrective actions.*

### Arquivo: `agent/agents/code_review_agent.py`
- **Classe:** `CodeReviewAgent`

### Arquivo: `agent/agents/maestro_agent.py`
- **Classe:** `StrategyCache`
  - *Cache LRU com TTL para decisões de estratégia*
- **Classe:** `MaestroAgent`

### Arquivo: `agent/agents/prompt_optimizer.py`
- **Classe:** `PromptOptimizer`
  - *Analyzes prompt performance and automatically optimizes prompts*

### Arquivo: `agent/agents/error_analyzer.py`
- **Classe:** `ErrorAnalysisAgent`

### Arquivo: `agent/utils/__init__.py`

### Arquivo: `agent/utils/json_parser.py`
- **Função:** `parse_json_response(raw_str: str, logger: logging.Logger)`
  - *Analisa uma string bruta que se espera conter JSON, limpando-a e decodificando-a.*

### Arquivo: `agent/utils/smart_validator.py`
- **Classe:** `SmartValidator`
  - *Validador inteligente para diferentes tipos de dados*

### Arquivo: `agent/utils/llm_client.py`
- **Função:** `call_gemini_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Calls the Google Gemini API.*
- **Função:** `call_openrouter_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Calls a generic OpenAI-compatible API (like OpenRouter).*
- **Função:** `call_llm_with_fallback(model_config: Dict[str, Any], prompt: str, temperature: float, logger: logging.Logger)`
  - *Orchestrates LLM calls with a primary and fallback model.*

### Arquivo: `agent/utils/llm_optimizer.py`
- **Classe:** `LLMCallOptimizer`
  - *Otimizador inteligente para chamadas LLM*

### Arquivo: `agent/utils/advanced_logging.py`
- **Função:** `setup_advanced_logging(name: str, level: int=logging.INFO)`
  - *Setup advanced logging configuration*

### Arquivo: `agent/utils/error_handling.py`
- **Função:** `safe_execute(func: Callable, *args, **kwargs)`
  - *Execute function safely with error handling*
- **Função:** `retry_with_backoff(func: Callable, max_retries: int=3, backoff_factor: int=2)`
  - *Retry function with exponential backoff*

### Arquivo: `agent/utils/intelligent_cache.py`
- **Classe:** `IntelligentCache`
  - *Cache inteligente com TTL e LRU*
- **Função:** `cached(ttl: int=3600)`
  - *Decorator para cache automático*

### Arquivo: `agent/utils/ux_enhancer.py`
- **Classe:** `UXEnhancer`
  - *Melhorador de experiência do usuário*

### Arquivo: `agent/utils/night_improvements.py`
- **Classe:** `ContinuousImprovement`
  - *Sistema de melhorias contínuas*

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
