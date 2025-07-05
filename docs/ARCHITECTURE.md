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
    HOT_RELOAD_DOCUMENTATION.md
    README_MCP_HEPHAESTUS.md
    poetry.lock
    main.py
    API_REST_DOCUMENTATION.md
    hephaestus_config.json
    GUIA_MCP_CURSOR.md
    CHECKLIST_MCP_HEPHAESTUS.md
    evolution_monitoring.txt
    demo_meta_intelligence.py
    GUIA_CONFIGURACAO_CURSOR.md
    start_mcp_server.sh
    setup_mcp.py
    ERROR_DETECTOR_DOCUMENTATION.md
    cursor_mcp_config.json
    pyproject.toml
    tools/
        app.py
    agent/
        async_orchestrator.py
        objective_generator.py
        analysis_processor.py
        brain.py
        __init__.py
        commit_message_generator.py
        arthur_interface_generator.py
        code_metrics.py
        knowledge_integration.py
        model_optimizer.py
        hephaestus_agent.py
        hephaestus_config.json
        git_utils.py
        meta_cognitive_controller.py
        root_cause_analyzer.py
        hot_reload_manager.py
        code_validator.py
        meta_intelligence_core.py
        llm_performance_booster.py
        self_awareness_core.py
        flow_self_modifier.py
        patch_applicator.py
        cycle_runner.py
        self_improvement_engine.py
        memory.py
        cognitive_evolution_manager.py
        prompt_builder.py
        tool_executor.py
        project_scanner.py
        queue_manager.py
        state.py
        strategy_optimizer.py
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
        config/
            technical_debt_config.yaml
        agents/
            capability_gap_detector.py
            linter_agent.py
            __init__.py
            self_reflection_agent.py
            log_analysis_agent.py
            architect_agent.py
            frontend_artisan_agent.py
            performance_analyzer.py
            error_correction.py
            error_detector_agent.py
            code_review_agent.py
            maestro_agent.py
            model_sommelier_agent.py
            prompt_optimizer.py
            debt_hunter_agent.py
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
    templates/
        dashboard.html
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
    generated_interfaces/
        arthur_interface_1751661619.html

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
- **Classe:** `ObjectiveRequest(BaseModel)`
- **Classe:** `DeepReflectionRequest(BaseModel)`
- **Classe:** `AsyncEvolutionRequest(BaseModel)`
- **Classe:** `InterfaceGenerationRequest(BaseModel)`
- **Classe:** `AgentConfigRequest(BaseModel)`
- **Classe:** `SystemStatusResponse(BaseModel)`
- **Função:** `add_process_time_header(request: Request, call_next)`
- **Função:** `rate_limiting_middleware(request: Request, call_next)`
- **Função:** `get_auth_user(credentials: HTTPAuthorizationCredentials=Depends(security))`
- **Função:** `startup_event()`
  - *Initialize the system on startup*
- **Função:** `shutdown_event()`
  - *Cleanup on shutdown*
- **Função:** `periodic_log_analysis_task()`
  - *A background task that periodically queues system monitoring tasks.*
- **Função:** `worker_thread()`
  - *Starts the agent's main execution loop.*
- **Função:** `process_objective(objective_data: Any)`
  - *DEPRECATED: This logic is now handled by the CycleRunner.run() loop.*
- **Função:** `root()`
  - *API Root - Welcome page with navigation*
- **Função:** `health_check()`
  - *Enhanced health check with comprehensive system status*
- **Função:** `get_status()`
  - *Get detailed system status including all subsystems*
- **Função:** `submit_objective(request: ObjectiveRequest, auth_user: dict=Depends(get_auth_user))`
  - *Submit a new objective to the agent with priority and metadata*
- **Função:** `get_queue_status(auth_user: dict=Depends(get_auth_user))`
  - *Get current queue status and pending objectives*
- **Função:** `enable_turbo_mode(auth_user: dict=Depends(get_auth_user))`
  - *Enable turbo evolution mode with maximum parallelism*
- **Função:** `start_async_evolution(request: AsyncEvolutionRequest, auth_user: dict=Depends(get_auth_user))`
  - *Start async evolution with parallel multi-agent orchestration*
- **Função:** `get_orchestration_status(auth_user: dict=Depends(get_auth_user))`
  - *Get detailed async orchestration status*
- **Função:** `perform_deep_reflection(request: DeepReflectionRequest, auth_user: dict=Depends(get_auth_user))`
  - *Perform deep self-reflection and introspection*
- **Função:** `get_comprehensive_meta_intelligence_status(auth_user: dict=Depends(get_auth_user))`
  - *Get comprehensive meta-intelligence status*
- **Função:** `trigger_evolution_cycle(auth_user: dict=Depends(get_auth_user))`
  - *Manually trigger a meta-intelligence evolution cycle*
- **Função:** `generate_arthur_interface(request: InterfaceGenerationRequest, auth_user: dict=Depends(get_auth_user))`
  - *Generate personalized interface for Arthur*
- **Função:** `serve_arthur_interface()`
  - *Serve the latest generated interface for Arthur*
- **Função:** `list_generated_interfaces(auth_user: dict=Depends(get_auth_user))`
  - *List all generated interfaces*
- **Função:** `get_system_metrics(auth_user: dict=Depends(get_auth_user))`
  - *Get comprehensive system metrics*
- **Função:** `get_recent_logs(limit: int=50, auth_user: dict=Depends(get_auth_user))`
  - *Get recent system logs*
- **Função:** `get_dashboard_page()`
  - *Serves the main evolution dashboard HTML page.*
- **Função:** `get_dashboard_data(auth_user: dict=Depends(get_auth_user))`
  - *Provides real-time data for the evolution dashboard.*
- **Função:** `update_agent_config(request: AgentConfigRequest, auth_user: dict=Depends(get_auth_user))`
  - *Update agent configuration and persist it*
- **Função:** `get_current_config(auth_user: dict=Depends(get_auth_user))`
  - *Get current agent configuration*
- **Função:** `legacy_orchestration_status()`
  - *Legacy endpoint for orchestration status*
- **Função:** `legacy_enable_turbo_mode()`
  - *Legacy endpoint for enabling turbo mode*
- **Função:** `legacy_start_async_evolution(request: AsyncEvolutionRequest)`
  - *Legacy endpoint for async evolution*
- **Função:** `legacy_arthur_interface()`
  - *Legacy endpoint for Arthur interface*
- **Função:** `enable_hot_reload(auth_user: dict=Depends(get_auth_user))`
  - *Habilitar hot reload para evolução em tempo real*
- **Função:** `disable_hot_reload(auth_user: dict=Depends(get_auth_user))`
  - *Desabilitar hot reload*
- **Função:** `get_hot_reload_status(auth_user: dict=Depends(get_auth_user))`
  - *Obter status do hot reload*
- **Classe:** `SelfModificationRequest(BaseModel)`
- **Função:** `self_modify_code(request: SelfModificationRequest, auth_user: dict=Depends(get_auth_user))`
  - *Permitir que o sistema modifique seu próprio código*
- **Classe:** `DynamicImportRequest(BaseModel)`
- **Função:** `dynamic_import_code(request: DynamicImportRequest, auth_user: dict=Depends(get_auth_user))`
  - *Importar código dinamicamente em tempo de execução*
- **Função:** `trigger_self_evolution(auth_user: dict=Depends(get_auth_user))`
  - *Disparar auto-evolução baseada em performance*
- **Função:** `get_evolution_history(limit: int=20, auth_user: dict=Depends(get_auth_user))`
  - *Obter histórico de evoluções em tempo real*
- **Função:** `get_error_detector_status(auth_user: dict=Depends(get_auth_user))`
  - *Get current status of the error detector agent*
- **Função:** `get_error_report(auth_user: dict=Depends(get_auth_user))`
  - *Get detailed error analysis report*
- **Função:** `inject_test_error(error_message: str=Body(..., description='Error message to inject for testing'), auth_user: dict=Depends(get_auth_user))`
  - *Inject a test error for testing the error detection system*
- **Função:** `start_error_monitoring(auth_user: dict=Depends(get_auth_user))`
  - *Start error monitoring*
- **Função:** `stop_error_monitoring(auth_user: dict=Depends(get_auth_user))`
  - *Stop error monitoring*
- **Função:** `get_real_time_analysis(auth_user: dict=Depends(get_auth_user))`
  - *Get real-time analysis of system errors and health*
- **Função:** `capture_agent_error(agent_name: str=Body(..., description='Name of the agent that generated the error'), error_message: str=Body(..., description='Error message from the agent'), context: Optional[Dict[str, Any]]=Body(None, description='Additional error context'), auth_user: dict=Depends(get_auth_user))`
  - *Capture and analyze an error from a specific agent*
- **Função:** `global_exception_handler(request: Request, exc: Exception)`
  - *Global exception handler that reports errors to the detector*
- **Função:** `worker()`

### Arquivo: `agent/async_orchestrator.py`
- **Classe:** `AgentType(Enum)`
- **Classe:** `AgentTask`
  - *Representa uma tarefa para um agente específico*
- **Classe:** `AgentResult`
  - *Resultado de uma tarefa de agente*
- **Classe:** `AsyncAgentOrchestrator`
  - *Orquestrador assíncrono para múltiplos agentes*

### Arquivo: `agent/objective_generator.py`
- **Função:** `generate_next_objective(model_config: Dict[str, str], current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, memory: Optional[Memory]=None, model_optimizer: Optional[ModelOptimizer]=None, current_objective: Optional[str]=None)`
  - *Generates the next evolutionary objective using code analysis and performance data.*
- **Função:** `generate_capacitation_objective(model_config: Dict[str, str], engineer_analysis: str, logger: logging.Logger, memory_summary: Optional[str]=None)`
  - *Generates an objective to create necessary new capabilities.*

### Arquivo: `agent/analysis_processor.py`
- **Classe:** `AnalysisProcessor`

### Arquivo: `agent/brain.py`
- **Função:** `generate_next_objective(model_config: Dict[str, str], current_manifest: str, current_objective: Optional[str]=None)`
  - *Generates the next evolutionary objective using code analysis and performance data.*

### Arquivo: `agent/__init__.py`

### Arquivo: `agent/commit_message_generator.py`
- **Função:** `generate_commit_message(analysis_summary: str, objective: str, logger: logging.Logger)`
  - *Generates a concise and informative commit message using a rule-based system.*

### Arquivo: `agent/arthur_interface_generator.py`
- **Classe:** `InterfaceElement`
  - *Elemento da interface gerada*
- **Classe:** `ArthurInterfaceGenerator`
  - *Gerador de interfaces personalizadas para o Arthur*

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

### Arquivo: `agent/knowledge_integration.py`
- **Classe:** `KnowledgePattern`
  - *Represents a recognized pattern in knowledge.*
- **Classe:** `KnowledgeIntegrator`
  - *Core knowledge integration engine.*

### Arquivo: `agent/model_optimizer.py`
- **Classe:** `ModelPerformanceData`
  - *Performance data for a specific model call*
- **Classe:** `FineTuningDataset`
  - *A dataset prepared for fine-tuning*
- **Classe:** `ModelOptimizer`
  - *Advanced system for model self-optimization through performance data collection*
- **Função:** `get_model_optimizer(model_config: Dict[str, str], logger: logging.Logger)`
  - *Factory function to get a singleton instance of the ModelOptimizer.*

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

### Arquivo: `agent/hot_reload_manager.py`
- **Classe:** `HotReloadManager`
  - *Sistema de hot reload para evolução em tempo real*
- **Classe:** `SelfEvolutionEngine`
  - *Engine para auto-evolução do sistema*

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

### Arquivo: `agent/self_improvement_engine.py`
- **Classe:** `ImprovementProposal`
  - *A proposed system improvement with justification.*
- **Classe:** `SelfImprovementEngine`
  - *Core self-improvement engine.*

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
- **Função:** `get_evolution_manager(model_config: Dict[str, str], logger: logging.Logger, memory: Memory, model_optimizer: ModelOptimizer)`
  - *Factory function to get a singleton instance of the CognitiveEvolutionManager.*
- **Função:** `start_cognitive_evolution(model_config: Dict[str, str], logger: logging.Logger, memory: Memory, model_optimizer: ModelOptimizer)`
  - *Utility function to start the cognitive evolution process*

### Arquivo: `agent/prompt_builder.py`
- **Função:** `build_memory_context_section(memory_summary: Optional[str])`
  - *Constrói a seção de contexto da memória para os prompts.*
- **Função:** `build_initial_objective_prompt(memory_context_section: str)`
  - *Constrói o prompt para gerar o objetivo inicial quando não há manifesto ou análise de código.*
- **Função:** `build_meta_analysis_objective_prompt(current_objective: str, original_failed_objective: str, error_reason_for_meta: str, performance_summary_str: str, memory_context_section: str, capabilities_content: str, roadmap_content: str)`
  - *Constrói o prompt para gerar um objetivo estratégico após uma meta-análise de falha.*
- **Função:** `build_standard_objective_prompt(memory_context_section: str, performance_summary_str: str, code_analysis_summary_str: str, current_manifest: str, capabilities_content: str, roadmap_content: str, dashboard_content: str)`
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
  - *Cria recomendações acionáveis a partir dos resultados.*
- **Função:** `list_available_models()`
  - *Fetches the list of available models from the OpenRouter API and filters for free ones.*

### Arquivo: `agent/project_scanner.py`
- **Função:** `_extract_elements(code_string: str)`
  - *Extract code elements (imports, classes, functions) from Python source.*
- **Função:** `_extract_skeleton(code_string: str)`
  - *Generate a code skeleton showing imports, classes and functions without implementation.*
- **Função:** `_get_default_skip_dirs()`
  - *Get default directories to skip during project scanning.*
- **Função:** `_should_skip_directory(dir_name: str, excluded_dirs: Set[str])`
  - *Determine if a directory should be skipped during scanning.*
- **Função:** `_process_file_for_manifest(file_path_obj: pathlib.Path, root_path: pathlib.Path, target_files_set: Set[str], target_content_cache: Dict[str, Tuple[Optional[str], Optional[Exception]]], api_summary_cache: Dict[str, List[Tuple]])`
  - *Process a file for manifest generation.*
- **Função:** `_write_manifest_section(manifest_file, section_title: str, content: str, indent_level: int=0)`
  - *Write a section to the manifest file.*
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='docs/ARCHITECTURE.md', excluded_dir_patterns: Optional[List[str]]=None)`
  - *Generate a project manifest documenting the code structure and APIs.*
- **Função:** `_collect_project_files(root_path: pathlib.Path, excluded_dirs: Set[str])`
  - *Collect all Python files in the project, separating test files.*
- **Função:** `_analyze_single_file(file_path_obj: pathlib.Path, root_path: pathlib.Path, file_loc_threshold: int, func_loc_threshold: int, func_cc_threshold: int, test_files: Set[str])`
  - *Analyze metrics for a single Python file.*
- **Função:** `_check_missing_tests(relative_path_str: str, file_functions_metrics: List[Dict[str, Any]], file_loc: int, test_files: Set[str])`
  - *Check if a module is missing corresponding test files.*
- **Função:** `analyze_code_metrics(root_dir: str, excluded_dir_patterns: Optional[List[str]]=None, file_loc_threshold: int=300, func_loc_threshold: int=50, func_cc_threshold: int=10)`
  - *Analyze Python files in a directory for code metrics like LOC and Cyclomatic Complexity.*

### Arquivo: `agent/queue_manager.py`
- **Classe:** `QueueManager`

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

### Arquivo: `agent/strategy_optimizer.py`
- **Classe:** `StrategyVariant`
  - *A specific strategy variant with performance metrics.*
- **Classe:** `StrategyOptimizer`
  - *Core strategy optimization engine.*

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
- **Função:** `_safe_json_serialize(obj: Any)`
  - *Safely serialize objects to JSON-compatible format.*

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

### Arquivo: `agent/agents/linter_agent.py`
- **Classe:** `LinterAgent`
  - *An agent that uses a static linter (ruff) to find, fix, and safely propose*

### Arquivo: `agent/agents/__init__.py`

### Arquivo: `agent/agents/self_reflection_agent.py`
- **Classe:** `SelfReflectionAgent`
  - *Agent that analyzes the Hephaestus codebase itself to identify patterns,*

### Arquivo: `agent/agents/log_analysis_agent.py`
- **Classe:** `LogAnalysisAgent`
  - *An agent specialized in analyzing log files to identify issues and suggest improvements.*

### Arquivo: `agent/agents/architect_agent.py`
- **Classe:** `ArchitectAgent`

### Arquivo: `agent/agents/frontend_artisan_agent.py`
- **Classe:** `FrontendArtisanAgent`
  - *An agent that specializes in analyzing and improving web frontends.*

### Arquivo: `agent/agents/performance_analyzer.py`
- **Classe:** `PerformanceAnalysisAgent`
  - *An agent dedicated to analyzing the performance of Hephaestus.*

### Arquivo: `agent/agents/error_correction.py`
- **Classe:** `ErrorCorrectionAgent`
  - *Agent for analyzing errors and generating corrective actions.*

### Arquivo: `agent/agents/error_detector_agent.py`
- **Classe:** `ErrorPattern`
  - *Representa um padrão de erro detectado*
- **Classe:** `ErrorDetectorAgent`
  - *Agente que monitora erros da API REST e implementa correções automáticas*

### Arquivo: `agent/agents/code_review_agent.py`
- **Classe:** `CodeReviewAgent`

### Arquivo: `agent/agents/maestro_agent.py`
- **Classe:** `StrategyCache`
  - *LRU cache with TTL for strategy decisions.*
- **Classe:** `MaestroAgent`
  - *Orchestrates strategy selection and execution for the Hephaestus system.*

### Arquivo: `agent/agents/model_sommelier_agent.py`
- **Classe:** `ModelSommelierAgent`
  - *An agent that analyzes the performance of other agents and proposes*

### Arquivo: `agent/agents/prompt_optimizer.py`
- **Classe:** `PromptOptimizer`
  - *Analyzes prompt performance and automatically optimizes prompts*

### Arquivo: `agent/agents/debt_hunter_agent.py`
- **Classe:** `DebtType(Enum)`
- **Classe:** `TechnicalDebtItem`
- **Classe:** `DebtHunterAgent`
  - *An autonomous agent that proactively hunts for technical debt and proposes*

### Arquivo: `agent/agents/error_analyzer.py`
- **Classe:** `ErrorAnalysisAgent`

### Arquivo: `agent/utils/__init__.py`

### Arquivo: `agent/utils/json_parser.py`
- **Função:** `_fix_common_json_errors(json_string: str, logger: logging.Logger)`
  - *Tenta corrigir erros comuns de JSON gerado por LLM.*
- **Função:** `parse_json_response(raw_str: str, logger: logging.Logger)`
  - *Analyzes a raw string to find and parse a JSON object, cleaning and fixing it as needed.*

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

