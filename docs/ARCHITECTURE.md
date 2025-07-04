# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    MCP_SETUP_GUIDE.md
    README.md
    mcp_server.log
    PROPOSTA_SERVIDOR_MCP.md
    CURSOR_MCP_GUIA_FINAL.md
    REVISAO_PROJETO_HEPHAESTUS.md
    demo_self_awareness.py
    hephaestus_mcp_server.py
    META_INTELLIGENCE_UPGRADE_SUMMARY.md
    run_mcp.py
    mcp_server_example.py
    cli.py
    README_MCP_HEPHAESTUS.md
    poetry.lock
    main.py
    GUIA_MCP_CURSOR.md
    CHECKLIST_MCP_HEPHAESTUS.md
    evolution_monitoring.txt
    demo_meta_intelligence.py
    GUIA_CONFIGURACAO_CURSOR.md
    start_mcp_server.sh
    setup_mcp.py
    cursor_mcp_config.json
    pyproject.toml
    tools/
        app.py
    agent/
        analysis_processor.py
        brain.py
        __init__.py
        code_metrics.py
        model_optimizer.py
        hephaestus_agent.py
        hephaestus_config.json
        git_utils.py
        meta_cognitive_controller.py
        root_cause_analyzer.py
        code_validator.py
        meta_intelligence_core.py
        llm_performance_booster.py
        self_awareness_core.py
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
        advanced_knowledge_system.py
        validation_steps/
            pytest_validator.py
            __init__.py
            main.yaml
            base.py
            patch_applicator.py
            syntax_validator.py
            pytest_new_file_validator.py
            models/
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
            infrastructure_manager.py
            intelligent_cache.py
            ux_enhancer.py
            night_improvements.py
    config/
        example_config.yaml
        base_config.yaml
        default.yaml
        models/
            main.yaml
            local.yaml
        validation_strategies/
            main.yaml
    reports/
        model_performance.db
        night_work/
            NIGHT_WORK_SUMMARY.md
            NIGHT_AGENT_README.md
        memory/
            HEPHAESTUS_MEMORY.json
        evolution/
            evolution_report_20250704_085755.json
            night_report_20250704_004455.json
    logs/
        hephaestus.log
        continuous_evolution_corrected.log
        continuous_evolution.log
        evolution_monitoring.log
        night_agent.log
        hephaestus_corrected.log
        evolution_log.csv
        continuous_evolution_fixed.log

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Arquivo: `demo_self_awareness.py`
- **Função:** `create_demo_config()`
  - *Criar configuração de demonstração*
- **Função:** `demonstrate_self_awareness()`
  - *Demonstra as capacidades de auto-consciência*
- **Função:** `demonstrate_mcp_integration()`
  - *Demonstra a integração com MCP*
- **Função:** `create_comparison_summary()`
  - *Cria um resumo comparativo das melhorias*
- **Função:** `main()`
  - *Função principal*

### Arquivo: `hephaestus_mcp_server.py`
- **Classe:** `HephaestusMCPServer`
  - *Servidor MCP principal que gerencia todas as funcionalidades do Hephaestus*
- **Função:** `analyze_code(code: str, context: str='')`
  - *Analisa código usando as capacidades avançadas de RSI do Hephaestus.*
- **Função:** `generate_objective(context: str, type: str='standard')`
  - *Gera objetivos inteligentes usando o sistema Brain do Hephaestus.*
- **Função:** `execute_rsi_cycle(objective: str, area: str='general')`
  - *Executa um ciclo completo de auto-aprimoramento recursivo.*
- **Função:** `meta_intelligence_report()`
  - *Gera relatório completo da meta-inteligência do sistema.*
- **Função:** `performance_analysis()`
  - *Análise profunda de performance usando múltiplos sistemas.*
- **Função:** `evolve_capabilities(focus_area: str='general')`
  - *Evolui as capacidades do sistema usando meta-inteligência.*
- **Função:** `system_status()`
  - *Status geral do sistema Hephaestus.*
- **Função:** `deep_self_reflection(focus_area: str='general')`
  - *Realiza auto-reflexão profunda e introspecção do sistema.*
- **Função:** `self_awareness_report()`
  - *Relatório completo de auto-consciência do sistema.*
- **Função:** `hephaestus_status()`
  - *Status detalhado do sistema Hephaestus*
- **Função:** `hephaestus_capabilities()`
  - *Capacidades detalhadas do sistema*
- **Função:** `hephaestus_memory()`
  - *Acesso à memória do sistema*
- **Função:** `main()`
  - *Função principal para executar o servidor MCP*
- **Função:** `run_server()`
  - *Função para executar o servidor sem conflitos de asyncio*

### Arquivo: `run_mcp.py`
- **Classe:** `MCPServerRunner`
  - *Executa o servidor MCP de forma robusta*
- **Função:** `main()`
  - *Função principal*

### Arquivo: `mcp_server_example.py`
- **Classe:** `HephaestusSimulator`
  - *Simulador das capacidades do Hephaestus para demonstração*
- **Função:** `analyze_code(code: str)`
  - *Analisa código usando as capacidades avançadas do Hephaestus RSI.*
- **Função:** `generate_objective(context: str)`
  - *Gera um objetivo de aprimoramento baseado no contexto fornecido.*
- **Função:** `self_improve(area: str)`
  - *Executa um ciclo de auto-aprimoramento em uma área específica.*
- **Função:** `performance_analysis()`
  - *Retorna análise completa de performance do sistema Hephaestus.*
- **Função:** `capability_assessment()`
  - *Avalia as capacidades atuais do sistema Hephaestus.*
- **Função:** `system_status()`
  - *Status atual do sistema Hephaestus*
- **Função:** `capabilities_resource()`
  - *Configuração detalhada das capacidades*
- **Função:** `analyze_and_improve_prompt(code: str, focus_area: str='general')`
  - *Prompt para análise e aprimoramento de código.*
- **Função:** `main()`
  - *Função principal para executar o servidor MCP*

### Arquivo: `cli.py`
- **Função:** `run(continuous: bool=typer.Option(False, '--continuous', '-c', help='Run in continuous mode'), max_cycles: int=typer.Option(None, '--max-cycles', '-m', help='Maximum number of evolution cycles'))`
  - *Run the Hephaestus agent*
- **Função:** `submit(objective: str)`
  - *Submit a new objective to the agent*
- **Função:** `status()`
  - *Check agent status*

### Arquivo: `main.py`

### Arquivo: `demo_meta_intelligence.py`
- **Função:** `setup_logging()`
  - *Setup comprehensive logging for the demo*
- **Função:** `demo_model_optimizer(logger)`
  - *Demonstrate the Model Optimizer system*
- **Função:** `demo_knowledge_system(logger)`
  - *Demonstrate the Advanced Knowledge System*
- **Função:** `demo_root_cause_analyzer(logger)`
  - *Demonstrate the Root Cause Analyzer*
- **Função:** `demo_meta_intelligence_integration(logger, optimizer, knowledge_system, analyzer)`
  - *Demonstrate the integrated Meta-Intelligence Core*
- **Função:** `main()`
  - *Main demonstration function*

### Arquivo: `setup_mcp.py`
- **Função:** `run_command(cmd: str, description: str='')`
  - *Executa um comando e retorna o resultado*
- **Função:** `install_dependencies()`
  - *Instala as dependências do MCP*
- **Função:** `create_cursor_config()`
  - *Cria configuração para Cursor*
- **Função:** `create_claude_config()`
  - *Cria configuração para Claude Desktop*
- **Função:** `create_test_client()`
  - *Cria cliente de teste para o servidor MCP*
- **Função:** `main()`
  - *Função principal do setup*

### Arquivo: `tools/app.py`
- **Classe:** `Objective(BaseModel)`
- **Classe:** `SelfReflectionRequest(BaseModel)`
- **Função:** `startup_event()`
- **Função:** `submit_objective(obj: Objective)`
  - *Submit a new objective for the agent to process*
- **Função:** `get_status()`
  - *Get basic status of the agent and meta-intelligence*
- **Função:** `get_comprehensive_meta_intelligence_status()`
  - *Get comprehensive status of all meta-intelligence systems*
- **Função:** `perform_deep_self_reflection(request: SelfReflectionRequest)`
  - *Trigger deep self-reflection and introspection*
- **Função:** `get_self_awareness_report()`
  - *Get comprehensive self-awareness report*
- **Função:** `get_knowledge_system_status()`
  - *Get status of the knowledge acquisition system*
- **Função:** `get_model_optimizer_status()`
  - *Get status of the model optimization system*
- **Função:** `get_root_cause_analyzer_status()`
  - *Get status of the root cause analysis system*
- **Função:** `health_check()`
  - *Health check endpoint*

### Arquivo: `agent/analysis_processor.py`
- **Classe:** `AnalysisProcessor`

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

### Arquivo: `agent/model_optimizer.py`
- **Classe:** `ModelPerformanceData`
  - *Performance data for a specific model call*
- **Classe:** `FineTuningDataset`
  - *A dataset prepared for fine-tuning*
- **Classe:** `ModelOptimizer`
  - *Advanced system for model self-optimization through performance data collection*
- **Função:** `get_model_optimizer(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global model optimizer instance.*

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

### Arquivo: `agent/root_cause_analyzer.py`
- **Classe:** `FailureType(Enum)`
  - *Types of failures the system can experience*
- **Classe:** `CausalLayer(Enum)`
  - *Different layers of causality*
- **Classe:** `FailureEvent`
  - *A single failure event with comprehensive metadata*
- **Classe:** `CausalFactor`
  - *A factor that contributes to failures*
- **Classe:** `RootCauseAnalysis`
  - *Complete root cause analysis result*
- **Classe:** `RootCauseAnalyzer`
  - *Advanced root cause analysis system that can identify deep, systemic*
- **Função:** `get_root_cause_analyzer(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global root cause analyzer instance.*

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

### Arquivo: `agent/llm_performance_booster.py`
- **Classe:** `SemanticCache`
  - *Cache semântico avançado para chamadas LLM*
- **Classe:** `RuleBasedBypass`
  - *Sistema de bypass baseado em regras*
- **Classe:** `PromptCompressor`
  - *Compressor inteligente de prompts*
- **Classe:** `LLMPerformanceBooster`
  - *Sistema principal de otimização de performance*
- **Função:** `get_performance_booster(logger: Optional[logging.Logger]=None)`
  - *Retorna instância singleton do performance booster*
- **Função:** `optimized_llm_call(agent_type: str, prompt: str, model_config: Dict[str, Any], temperature: float=0.3, context: Optional[Dict]=None, logger: Optional[logging.Logger]=None)`
  - *Função principal para chamadas LLM otimizadas.*

### Arquivo: `agent/self_awareness_core.py`
- **Classe:** `CognitiveState`
  - *Represents the current cognitive state of the system*
- **Classe:** `SelfInsight`
  - *Represents a deep insight about the system's own nature*
- **Classe:** `CognitiveEvolutionEvent`
  - *Tracks significant changes in cognitive capabilities*
- **Classe:** `SelfAwarenessCore`
  - *The unified self-awareness system that provides deep introspection*
- **Função:** `get_self_awareness_core(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global self-awareness core*

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
- **Função:** `read_file(file_path: str)`
  - *Lê o conteúdo de um arquivo e o retorna como uma string.*
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
  - *Generate a code skeleton showing imports, classes and functions without implementation.*
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='docs/ARCHITECTURE.md', excluded_dir_patterns: Optional[List[str]]=None)`
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

### Arquivo: `agent/advanced_knowledge_system.py`
- **Classe:** `KnowledgeEntry`
  - *A single piece of knowledge with metadata*
- **Classe:** `SearchResult`
  - *Enhanced search result with intelligence metadata*
- **Classe:** `AdvancedKnowledgeSystem`
  - *Advanced knowledge acquisition and processing system that can learn*
- **Função:** `get_knowledge_system(model_config: Dict[str, str], logger: logging.Logger)`
  - *Get or create the global knowledge system instance.*

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
- **Função:** `_fix_common_json_errors(json_string: str, logger: logging.Logger)`
  - *Tenta corrigir erros comuns de JSON gerado por LLM.*
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

### Arquivo: `agent/utils/infrastructure_manager.py`
- **Classe:** `InfrastructureManager`
  - *Gerenciador de infraestrutura básica do sistema*
- **Função:** `ensure_basic_infrastructure(logger: Optional[logging.Logger]=None)`
  - *Função utilitária para garantir infraestrutura básica*
- **Função:** `diagnose_and_fix_infrastructure(logger: Optional[logging.Logger]=None)`
  - *Função utilitária para diagnosticar e corrigir infraestrutura*
- **Função:** `get_infrastructure_manager(logger: Optional[logging.Logger]=None)`
  - *Retorna instância do gerenciador de infraestrutura*

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

### Arquivo: `agent/project_scanner.py`

```
import os
import fnmatch
import pathlib
import ast
from typing import List, Optional, Tuple, Dict, Set, Any # Adicionado Any

def _extract_elements(code_string: str) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
    try:
        tree = ast.parse(code_string)
        elements = []
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                elements.append(('import', ast.unparse(node), None, None))
            
            elif isinstance(node, ast.ClassDef):
                bases = [ast.unparse(base) for base in node.bases]
                docstring = ast.get_docstring(node)
                elements.append(('class', node.name, ','.join(bases) if bases else None, docstring))
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)): # CORRIGIDO para AsyncFunctionDef
                args = ast.unparse(node.args)
                docstring = ast.get_docstring(node)
                elements.append(('function', node.name, args, docstring))
        
        return elements
    
    except Exception as e:
        return [('error', None, None, f"Erro na análise AST: {str(e)}")]

def _extract_skeleton(code_string: str) -> str:
    """Generate a code skeleton showing imports, classes and functions without implementation.
    
    Args:
        code_string: Python source code to analyze
        
    Returns:
        String containing a simplified skeleton of the code structure
    """
    elements = _extract_elements(code_string)
    
    if elements and elements[0][0] == 'error':
        return f"# {elements[0][3]}"

    skeleton_lines = []
    for el_type, name, details, docstring in elements:
        if el_type == 'import':
            skeleton_lines.append(name)
        
        elif el_type == 'class':
            class_def = f"class {name}"
            if details:
                class_def += f"({details})"
            class_def += ":"
            skeleton_lines.append(class_def)
            
            if docstring:
                skeleton_lines.append(f'    """{docstring}"""')
            
            skeleton_lines.append("    # ... (corpo omitido para brevidade)\n")
        
        elif el_type == 'function':
            func_def = f"def {name}({details}):"
            skeleton_lines.append(func_def)
            
            if docstring:
                skeleton_lines.append(f'    """{docstring}"""')
            
            skeleton_lines.append("    # ... (corpo omitido para brevidade)\n")
    
    return "\n".join(skeleton_lines)

def update_project_manifest(
    root_dir: str,
    target_files: List[str],
    output_path: str = "docs/ARCHITECTURE.md",
    excluded_dir_patterns: Optional[List[str]] = None
) -> None:
    root_path = pathlib.Path(root_dir).resolve()
    # Padrões de diretório a serem ignorados globalmente na varredura.
    # Inclui diretórios comuns de dependências, controle de versão e caches.
    # Também inclui "tests" e "test" para evitar a análise de código de teste como código de produção.
    default_skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', 'tests', 'test', '.pytest_cache', 'dist', 'build', 'docs', 'examples', 'scripts'}

    # Combina os padrões de exclusão fornecidos pelo usuário com os padrões padrão.
    # Os padrões do usuário têm precedência se houver sobreposição (embora aqui seja uma união).
    if excluded_dir_patterns:
        current_excluded_dirs = default_skip_dirs.union(set(excluded_dir_patterns))
    else:
        current_excluded_dirs = default_skip_dirs

    target_files_set = set(target_files)
    
    target_content_cache: Dict[str, Tuple[Optional[str], Optional[Exception]]] = {}
    api_summary_cache: Dict[str, List[Tuple]] = {}
    
    with open(output_path, 'w', encoding='utf-8') as manifest:
        manifest.write("# MANIFESTO DO PROJETO HEPHAESTUS\n\n")
        
        manifest.write("## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)\n")
        
        for root, dirs, files in os.walk(root_path, topdown=True):
            current_path_obj = pathlib.Path(root)

            # Filtrar dirs ANTES de decidir se o root atual deve ser pulado por modificação de dirs[:]
            original_dirs_for_current_root = list(dirs) # Copia para referência

            # Nova lógica de filtragem de diretórios
            # Primeiro, os diretórios básicos de skip_dirs e ocultos
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in default_skip_dirs]
            # Depois, os padrões de diretórios excluídos
            # Para excluded_dir_patterns, precisamos checar o nome do diretório E o caminho relativo
            # Isso é feito para permitir padrões como "tests" (qualquer pasta chamada tests)
            # ou "src/tests" (uma pasta específica).
            # No entanto, `d` aqui é apenas o nome base. Para padrões de caminho, precisaríamos do caminho completo.
            # Vamos simplificar por agora para filtrar apenas pelo nome base do diretório.
            # Padrões mais complexos (como caminhos relativos) exigiriam uma lógica mais elaborada aqui
            # ou um pré-processamento de todos os caminhos.
            dirs[:] = [d for d in dirs if d not in current_excluded_dirs and not any(fnmatch.fnmatch(d, pattern) for pattern in current_excluded_dirs)]


            # Escrever o nome do diretório atual (root)
            # A menos que o próprio root seja um diretório skip_dirs (o que não deve acontecer se root_path for o início)
            # ou se o root for o próprio root_path E não tiver conteúdo (dirs filtrados e files)
            if current_path_obj == root_path and not dirs and not files:
                 # Caso especial: root_dir é completamente vazio ou só contém skip_dirs
                 # Ainda assim, queremos listar o próprio root_dir
                 pass # Não pular a escrita do root_dir em si

            # Se o diretório atual (root) corresponde a um padrão de exclusão, pule-o completamente.
            # Isso não impede que os.walk entre nele se não for filtrado por dirs[:],
            # mas impede sua listagem e o processamento de seus arquivos.
            # Esta verificação é feita APÓS a modificação de dirs[:],
            # pois os.walk já decidiu entrar neste 'root'.
            # No entanto, para ser mais eficaz, a decisão de pular um 'root' deve ser feita
            # antes de qualquer processamento ou escrita para esse 'root'.

            # CORREÇÃO: A filtragem de `dirs[:]` já impede a entrada em subdiretórios.
            # O que precisamos aqui é garantir que, se o `current_path_obj` (o `root` atual)
            # em si for um diretório que deveria ser excluído (exceto se for o `root_path` inicial),
            # então não o listamos e não processamos seus arquivos.

            current_dir_name = os.path.basename(root)
            if current_path_obj != root_path: # Não excluir o diretório raiz do manifesto
                if current_dir_name in current_excluded_dirs or \
                   any(fnmatch.fnmatch(current_dir_name, pattern) for pattern in current_excluded_dirs) or \
                   current_dir_name in default_skip_dirs: # Adicionado default_skip_dirs aqui também
                    continue # Pula para o próximo diretório no os.walk

            # Calcular indentação e escrever o nome do diretório atual
            if current_path_obj == root_path:
                level_parts = []
            else:
                try:
                    level_parts = current_path_obj.relative_to(root_path).parts
                except ValueError:
                    level_parts = current_path_obj.parts

            indent = ' ' * 4 * len(level_parts)
            manifest.write(f"{indent}{current_dir_name}/\n")
            
            # Pular o processamento de ARQUIVOS DENTRO DESTE DIRETÓRIO (root)
            # se ele não tiver mais subdiretórios para visitar (dirs ficou vazio após filtro)
            # E não tiver arquivos próprios.
            # A listagem do diretório (acima) já ocorreu.
            # Esta condição é para evitar o cabeçalho de arquivos "sub_indent" se não houver arquivos.
            # E também para otimizar, não processando caches para arquivos que não serão listados.
            # No entanto, o processamento de cache deve ocorrer mesmo para arquivos não alvo (para API summary)
            # Então, o `continue` aqui deve ser apenas se `files` estiver vazio.
            # A lógica original era: if not dirs and not files: continue (antes de listar o dir)
            # A correção é listar o dir, e SÓ pular a listagem de SEUS ARQUIVOS se não houver arquivos.

            sub_indent = ' ' * 4 * (len(level_parts) + 1)
            
            # Processar arquivos DENTRO do diretório 'root' atual
            for f_name in files:
                if f_name.startswith('.'): # Pular arquivos ocultos na listagem de arquivos
                    continue

                # Verificar se é um arquivo de teste Python
                is_test_file = False
                if f_name.endswith('.py'):
                    if f_name.startswith('test_') or f_name.endswith('_test.py'):
                        is_test_file = True

                # Se for um arquivo de teste, não o liste na estrutura de arquivos e não processe para API.
                if is_test_file:
                    continue

                manifest.write(f"{sub_indent}{f_name}\n")

                file_path_obj = current_path_obj / f_name
                # rel_path_str deve ser relativo ao root_path original do scan
                rel_path_str = str(file_path_obj.relative_to(root_path))

                # Processar arquivos alvo para conteúdo completo
                if rel_path_str in target_files_set:
                    try:
                        with open(file_path_obj, 'r', encoding='utf-8') as f_obj:
                            content = f_obj.read()
                        target_content_cache[rel_path_str] = (content, None)
                    except Exception as e:
                        target_content_cache[rel_path_str] = (None, e)

                # Processar todos os arquivos Python para resumo de API
                if f_name.endswith('.py'):
                    # Se já lemos o arquivo para conteúdo alvo, usar o conteúdo do cache
                    if rel_path_str in target_content_cache:
                        content, error = target_content_cache[rel_path_str]
                        if error:
                            api_summary_cache[rel_path_str] = [('error', None, None, f"Erro na leitura do arquivo: {str(error)}")]
                        else:
                            api_summary_cache[rel_path_str] = _extract_elements(content)
                    else:
                        try:
                            with open(file_path_obj, 'r', encoding='utf-8') as f_obj:
                                content = f_obj.read()
                            api_summary_cache[rel_path_str] = _extract_elements(content)
                        except Exception as e:
                            api_summary_cache[rel_path_str] = [('error', None, None, f"Erro na leitura do arquivo: {str(e)}")]
        
        manifest.write("\n## 2. RESUMO DAS INTERFACES (APIs Internas)\n")
        
        for rel_path_str, elements in api_summary_cache.items():
            manifest.write(f"\n### Arquivo: `{rel_path_str}`\n")
            
            if elements and elements[0][0] == 'error':
                manifest.write(f"  - [ERRO] {elements[0][3]}\n")
            else:
                for el_type, name, details, docstring in elements:
                    if el_type == 'class':
                        class_sig = f"{name}({details})" if details else name
                        manifest.write(f"- **Classe:** `{class_sig}`\n")
                        if docstring:
                            first_line = docstring.strip().split('\n')[0]
                            manifest.write(f"  - *{first_line}*\n")
                    
                    elif el_type == 'function':
                        manifest.write(f"- **Função:** `{name}({details})`\n")
                        if docstring:
                            first_line = docstring.strip().split('\n')[0]
                            manifest.write(f"  - *{first_line}*\n")
        
        manifest.write("\n## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO\n")
        
        for rel_path_str in target_files:
            manifest.write(f"\n### Arquivo: `{rel_path_str}`\n\n```\n")
            
            if rel_path_str in target_content_cache:
                content, error = target_content_cache[rel_path_str]
                if error:
                    manifest.write(f"# ERRO: {str(error)}\n")
                elif content is None:
                    manifest.write("# ERRO: Conteúdo não disponível\n")
                else:
                    manifest.write(content + "\n")
            else:
                manifest.write("# ARQUIVO NÃO ENCONTRADO OU NÃO PROCESSADO\n") # Mensagem mais genérica
            
            manifest.write("```\n")


def analyze_code_metrics(
    root_dir: str,
    excluded_dir_patterns: Optional[List[str]] = None,
    file_loc_threshold: int = 300,
    func_loc_threshold: int = 50,
    func_cc_threshold: int = 10
) -> Dict[str, Any]:
    """
    Analisa arquivos Python em um diretório para métricas de código como LOC e Complexidade Ciclomática.

    Args:
        root_dir: O diretório raiz para iniciar a varredura.
        excluded_dir_patterns: Uma lista de padrões de nomes de diretório a serem excluídos.
        file_loc_threshold: Limiar de LOC para considerar um arquivo grande.
        func_loc_threshold: Limiar de LOC para considerar uma função grande.
        func_cc_threshold: Limiar de CC para considerar uma função complexa.

    Returns:
        Um dicionário contendo:
        - 'metrics': Um dicionário onde chaves são caminhos de arquivo relativos e
                     valores são dicionários com 'file_loc' (LOC total do arquivo)
                     e 'functions' (uma lista de dicionários com métricas de função:
                     'name', 'args', 'loc', 'cc', 'is_large', 'is_complex').
        - 'summary': Um dicionário com listas de arquivos/funções que excedem os limiares:
                     'large_files': Lista de (caminho, loc).
                     'large_functions': Lista de (caminho, nome_func, loc).
                     'complex_functions': Lista de (caminho, nome_func, cc).
                     'missing_tests': Lista de caminhos de arquivo de módulo sem teste correspondente.
    """
    from radon.visitors import ComplexityVisitor
    from radon.metrics import h_visit_ast
    from radon.raw import analyze as analyze_raw

    root_path = pathlib.Path(root_dir).resolve()
    # Padrões de diretório a serem ignorados.
    default_skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', 'tests', 'test', '.pytest_cache', 'dist', 'build', 'docs', 'examples', 'scripts'}
    if excluded_dir_patterns:
        current_excluded_dirs = default_skip_dirs.union(set(excluded_dir_patterns))
    else:
        current_excluded_dirs = default_skip_dirs

    all_metrics: Dict[str, Dict[str, Any]] = {}
    large_files_summary: List[Tuple[str, int]] = []
    large_functions_summary: List[Tuple[str, str, int]] = []
    complex_functions_summary: List[Tuple[str, str, int]] = []
    missing_tests_summary: List[str] = []

    project_files = []
    test_files = set()

    for root, dirs, files in os.walk(root_path, topdown=True):
        # Filtra diretórios
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in current_excluded_dirs and not any(fnmatch.fnmatch(d, pattern) for pattern in current_excluded_dirs if '*' in pattern)]

        current_path_obj = pathlib.Path(root)
        # Pular o diretório raiz se ele próprio estiver na lista de exclusão (improvável para root_dir, mas seguro)
        if current_path_obj != root_path and (current_path_obj.name in current_excluded_dirs or any(fnmatch.fnmatch(current_path_obj.name, pattern) for pattern in current_excluded_dirs if '*' in pattern)):
            continue

        for file_name in files:
            if file_name.endswith('.py'):
                file_path_obj = current_path_obj / file_name
                relative_path_str = str(file_path_obj.relative_to(root_path))
                project_files.append(relative_path_str)
                if file_name.startswith('test_') or file_name.endswith('_test.py'):
                    test_files.add(relative_path_str)


    for relative_path_str in project_files:
        # Ignorar arquivos de teste na análise principal de métricas
        if relative_path_str in test_files:
            continue

        file_path_obj = root_path / relative_path_str

        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                code_content = f.read()

            # AST para funções e classes
            try:
                ast_tree = ast.parse(code_content, filename=str(file_path_obj))
            except SyntaxError:
                # Se houver erro de sintaxe, não podemos processar AST ou Radon para CC.
                # Podemos ainda obter LOC bruto.
                raw_analysis = analyze_raw(code_content)
                file_loc = raw_analysis.loc
                all_metrics[relative_path_str] = {
                    'file_loc': file_loc,
                    'functions': [],
                    'error': 'SyntaxError parsing file'
                }
                if file_loc > file_loc_threshold:
                    large_files_summary.append((relative_path_str, file_loc))
                continue # Pula para o próximo arquivo

            # Métricas de LOC do arquivo
            raw_analysis = analyze_raw(code_content)
            file_loc = raw_analysis.loc
            if file_loc > file_loc_threshold:
                large_files_summary.append((relative_path_str, file_loc))

            file_functions_metrics = []

            # Complexidade Ciclomática com Radon
            # Radon espera um AST, então usamos o que já parseamos
            visitor = ComplexityVisitor.from_ast(ast_tree)

            # Iterar sobre funções e classes para métricas
            for node in ast_tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_name = node.name
                    # Radon calcula LOC para a função de forma diferente (linhas de código lógicas)
                    # Para consistência com o LOC total do arquivo, podemos re-analisar o bloco da função
                    # ou usar o lineno e end_lineno.
                    func_loc = (node.end_lineno or node.lineno) - node.lineno + 1

                    # Encontrar a complexidade da função usando o nome
                    # (Radon armazena por nome, o que pode ser um problema com métodos de mesmo nome em classes diferentes)
                    # Uma abordagem mais robusta seria iterar `visitor.functions` e `visitor.classes`
                    # e mapear de volta para os nós AST se necessário, ou usar `lineno`.
                    current_cc = 0
                    for f_block in visitor.functions: # Procura por nome e linha inicial
                        if f_block.name == func_name and f_block.lineno == node.lineno:
                            current_cc = f_block.complexity
                            break
                    # Para métodos dentro de classes
                    if current_cc == 0: # Se não achou, pode ser um método
                        for class_block in visitor.classes:
                            for method_block in class_block.methods:
                                if method_block.name == func_name and method_block.lineno == node.lineno:
                                    current_cc = method_block.complexity
                                    break
                            if current_cc != 0:
                                break

                    args_list = [ast.unparse(arg) for arg in node.args.args]
                    args_str = ", ".join(args_list)

                    is_large_func = func_loc > func_loc_threshold
                    is_complex_func = current_cc > func_cc_threshold

                    if is_large_func:
                        large_functions_summary.append((relative_path_str, func_name, func_loc))
                    if is_complex_func:
                        complex_functions_summary.append((relative_path_str, func_name, current_cc))

                    file_functions_metrics.append({
                        'name': func_name,
                        'args': args_str,
                        'loc': func_loc,
                        'cc': current_cc,
                        'is_large': is_large_func,
                        'is_complex': is_complex_func,
                    })

            all_metrics[relative_path_str] = {
                'file_loc': file_loc,
                'functions': file_functions_metrics
            }

            # Verificar ausência de arquivo de teste
            # Isso é uma heurística simples. `test_foo.py` ou `foo_test.py` para `foo.py`
            # Se `relative_path_str` é `agent/brain.py`, esperamos `tests/agent/test_brain.py`

            path_parts = list(pathlib.Path(relative_path_str).parts) # ex: ['agent', 'brain.py']
            if len(path_parts) > 0 : # Se não for um arquivo na raiz
                module_name = path_parts[-1][:-3] # 'brain'

                # Construir caminhos de teste esperados
                # Caso 1: tests/path/to/module/test_module.py
                expected_test_path1_parts = ["tests"] + path_parts[:-1] + [f"test_{module_name}.py"]
                expected_test_path1 = str(pathlib.Path(*expected_test_path1_parts))

                # Caso 2: tests/path/to/module/module_test.py
                expected_test_path2_parts = ["tests"] + path_parts[:-1] + [f"{module_name}_test.py"]
                expected_test_path2 = str(pathlib.Path(*expected_test_path2_parts))

                # Caso 3: Se o módulo está na raiz: tests/test_module.py
                expected_test_path3_parts = ["tests"] + [f"test_{module_name}.py"]
                expected_test_path3 = str(pathlib.Path(*expected_test_path3_parts))

                # Caso 4: Se o módulo está na raiz: tests/module_test.py
                expected_test_path4_parts = ["tests"] + [f"{module_name}_test.py"]
                expected_test_path4 = str(pathlib.Path(*expected_test_path4_parts))

                if not (expected_test_path1 in test_files or \
                        expected_test_path2 in test_files or \
                        expected_test_path3 in test_files or \
                        expected_test_path4 in test_files):
                    # Apenas adicionar se o módulo tiver funções ou for significativamente grande
                    if file_functions_metrics or file_loc > 20: # Limiar pequeno para considerar
                        missing_tests_summary.append(relative_path_str)

        except FileNotFoundError:
            all_metrics[relative_path_str] = {'error': 'File not found during metrics analysis'}
        except Exception as e:
            all_metrics[relative_path_str] = {'error': f'Error analyzing {relative_path_str}: {str(e)}'}

    return {
        "metrics": all_metrics,
        "summary": {
            "large_files": large_files_summary,
            "large_functions": large_functions_summary,
            "complex_functions": complex_functions_summary,
            "missing_tests": missing_tests_summary,
        }
    }
```
