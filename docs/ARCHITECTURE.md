# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)

agente_autonomo/
    README.md
    setup_multiple_keys.py
    hephaestus_mcp_server.py
    cli.py
    monitor_evolution.py
    next_meta_functionalities_v2.md
    debug_keys.py
    poetry.lock
    analyze_meta_functionalities.py
    main.py
    hephaestus_config.json
    CLAUDE.md
    pyproject.toml
    src/
        hephaestus/
            __init__.py
            agents/
                agent_expansion_coordinator.py
                linter_agent.py
                bug_hunter_enhanced.py
                __init__.py
                enhanced_base.py
                self_reflection_agent.py
                log_analysis_agent.py
                performance_analyzer.py
                base.py
                cycle_monitor_agent.py
                error_detector_agent.py
                architect_enhanced.py
                dependency_fixer_agent.py
                swarm_coordinator_agent.py
                mixins.py
                organizer_enhanced.py
                maestro_enhanced.py
                mixins/
            core/
                agent.py
                objective_generator.py
                brain.py
                __init__.py
                commit_message_generator.py
                arthur_interface_generator.py
                code_metrics.py
                system_activator.py
                hot_reload_manager.py
                code_validator.py
                patch_applicator.py
                cycle_runner.py
                memory.py
                coverage_activator.py
                cognitive_evolution_manager.py
                prompt_builder.py
                state.py
                agents/
                    autonomous_monitor_agent.py
            data_sources/
                __init__.py
                crypto_apis.py
            api/
                __init__.py
                dashboard_server.py
                rest/
                    main.py.backup
                    main.py
                    error_resilience.py
                    validation_service.py
                    validation.py
                mcp/
                    server.py
                cli/
                    main.py
            validation/
                __init__.py
                unified_validator.py
            utils/
                api_key_manager.py
                __init__.py
                json_parser.py
                llm_manager.py
                agent_factory.py
                error_prevention_system.py
                continuous_monitor.py
                smart_validator.py
                git_utils.py
                log_cleaner.py
                llm_client.py
                llm_optimizer.py
                startup_validator.py
                metrics_collector.py
                advanced_logging.py
                config_manager.py
                error_handling.py
                infrastructure_manager.py
                intelligent_cache.py
                rate_limiter.py
                tool_executor.py
                logger_factory.py
                project_scanner.py
                queue_manager.py
                ux_enhancer.py
                night_improvements.py
                config_loader.py
            monitoring/
                __init__.py
                unified_dashboard.py
                predictive_failure_dashboard.py
            intelligence/
                self_awareness.py
                __init__.py
                real_time_evolution_engine.py
                meta_objective_generator.py
                evolution_callbacks.py
                model_optimizer.py
                parallel_reality_testing.py
                collective_intelligence_network.py
                root_cause_analyzer.py
                knowledge_system.py
                self_awareness_core.py
                evolution_analytics.py
                parallel_reality_tester.py
                temporal_intelligence.py
                predictive_failure_engine.py
                meta_core.py
                meta_learning_intelligence.py
                dynamic_agent_dna.py
            services/
                __init__.py
                communication/
                    inter_agent.py
                validation/
                    pytest_validator.py
                    __init__.py
                    main.yaml
                    base.py
                    patch_applicator.py
                    syntax_validator.py
                    pytest_new_file_validator.py
                monitoring/
                    performance.py
                optimization/
                    optimized_api_startup.py
                    initialization_optimization.py
                coordination/
                orchestration/
                    async_orchestrator.py
            financial/
                trading_engine.py
                opportunity_detector.py
                __init__.py
                crypto_arbitrage.py
                risk_manager.py
    config/
        example_config.yaml
        base_config.yaml
        default.yaml
        models/
            main.yaml
            local.yaml
        dynamic/
            runtime_config.yaml
        validation_strategies/
            main.yaml
    templates/
        dashboard.html
    reports/
        model_performance.db
        memory/
            HEPHAESTUS_MEMORY.json
    data/
        execution_lock.json
        collective_intelligence/
            agents/
                hephaestus_agent_124423607735120.json
                hephaestus_agent_130662635941712.json
                hephaestus_agent_126302631188496.json
                hephaestus_agent_136018006606288.json
                hephaestus_agent_130114010357968.json
                hephaestus_agent_127244829982160.json
                hephaestus_agent_137408510679952.json
                hephaestus_agent_130730365742800.json
                hephaestus_agent_137304120246224.json
                hephaestus_agent_134188832802064.json
                hephaestus_agent_128298663626256.json
                hephaestus_agent_134198072856208.json
                hephaestus_agent_126280159603280.json
                hephaestus_agent_130698451963792.json
                hephaestus_agent_132721687100368.json
                hephaestus_agent_132305318048144.json
                hephaestus_agent_126569939634000.json
                hephaestus_agent_123950374728656.json
                hephaestus_agent_129748972437456.json
                hephaestus_agent_135442763201808.json
                hephaestus_agent_139396809887184.json
                hephaestus_agent_123283764277712.json
                hephaestus_agent_125576807409232.json
                hephaestus_agent_123169772310352.json
                hephaestus_agent_138225092982032.json
                hephaestus_agent_131515852781136.json
                hephaestus_agent_123338135004624.json
                hephaestus_agent_129041742934352.json
                hephaestus_agent_124203824008784.json
                hephaestus_agent_139220132189904.json
                hephaestus_agent_132641144558672.json
                hephaestus_agent_132442195839952.json
                hephaestus_agent_139334092803024.json
            insights/
            knowledge/
                strategy_discovery_df51ad30.json
                strategy_discovery_13ddf8ce.json
                strategy_discovery_767ee161.json
                strategy_discovery_23817242.json
                strategy_discovery_67d55065.json
                strategy_discovery_57f200e2.json
                strategy_discovery_cedd7679.json
                strategy_discovery_c6d261f1.json
                strategy_discovery_d509214e.json
                strategy_discovery_3c2f012c.json
                strategy_discovery_ae850502.json
                strategy_discovery_e106bffc.json
                strategy_discovery_a28125aa.json
                strategy_discovery_fa9dc1d0.json
                strategy_discovery_c4a8133c.json
                strategy_discovery_539cbb83.json
                strategy_discovery_058ea617.json
                strategy_discovery_9db8dbd9.json
                strategy_discovery_54524758.json
                strategy_discovery_2984dcdd.json
                strategy_discovery_03f8dab4.json
                strategy_discovery_39760a01.json
                strategy_discovery_f6232653.json
                strategy_discovery_496dcb64.json
                strategy_discovery_33311d83.json
                strategy_discovery_38cc52a2.json
                strategy_discovery_706eb9c4.json
                strategy_discovery_10c4cf55.json
                strategy_discovery_0bb3a3d0.json
                strategy_discovery_e59e00e2.json
                strategy_discovery_af629508.json
                strategy_discovery_f0329457.json
                strategy_discovery_62e281e2.json
        agents/
            bug_hunter_config_backup_20250708_155245.yaml
            architect_config_backup_20250708_155245.yaml
            maestro_config.yaml
            bug_hunter_config.yaml
            maestro_config_backup_20250708_155245.yaml
            architect_config.yaml
        objectives/
            simple_debug_objective.json
        memory/
            HEPHAESTUS_MEMORY.json
            META_FUNCTIONALITIES_MEMORY.json
        prompts/
            maestro_prompts_prompt.txt
            objective_generation_prompt.txt
            architect_prompts_prompt.txt
        reports/
            model_performance.db
            feature_activation_20250705_162115.json
            coverage_activation_report_20250705_120445.json
            evolution_state_20250708_130731.json
            failure_patterns.json
            system_engineer_analysis_20250705_161711.json
            night_work/
                NIGHT_WORK_SUMMARY.md
                NIGHT_AGENT_README.md
            memory/
            evolution/
                evolution_report_20250704_085755.json
                night_report_20250704_004455.json
        self_awareness/
            awareness_data.json
        parallel_tests/
            results/
            environments/
        meta_learning/
            learning_data.json
        logs/
            error_prevention_test.log
            feature_activation.log
            error_prevention.log
            monitor_test_results_20250705_112439.json
            uvicorn.log
            performance_metrics.json
            autonomous_monitor.log
            uvicorn_optimized.log
            monitor_hephaestus.log
            cursor_protection_test.log
            feature_integration.log
            night_evolution_20250705.log
            hephaestus_main.log
            evolution_log.csv
            system_engineer_analysis.log
            feature_activation_test.log
            hephaestus_alerts.json
            hephaestus_evolution_20250705_014830.log
            test_json_serialization.log
            hephaestus_evolution_20250705_014743.log
            monitor_tester.log
            agents/
                organizeragentenhanced_agent.log
                maestroagentenhanced_agent.log
                test_agent.log
                bughunteragentenhanced_agent.log
                testenhanced_agent.log
                architectagentenhanced_agent.log
        intelligence/
            meta_objectives/
                meta_objective_data.json
            temporal/
                temporal_data.json
        evolution_analytics/
            metrics_history.json
            chart_cycle_success_rate_7d.png
            trends_history.json
            chart_cycle_duration_seconds_7d.png
            chart_agents_per_cycle_7d.png
        backups/
            bug_hunter_config_backup_20250708_223022.yaml
            config_backup_20250708_222438.yaml
            config_backup_20250708_222415.yaml
            config_backup_20250708_221716.yaml
            config_backup_20250708_222849.yaml
            maestro_config_backup_20250708_221722.yaml
            config_backup_20250708_223101.yaml
            config_backup_20250708_222305.yaml
            bug_hunter_config_backup_20250708_222659.yaml
            maestro_config_backup_20250708_222443.yaml
            config_backup_20250708_222844.yaml
            config_backup_20250708_222127.yaml
            maestro_config_backup_20250708_223028.yaml
            config_backup_20250708_222955.yaml
            config_backup_20250708_222901.yaml
            config_backup_20250708_222038.yaml
            config_backup_20250708_222816.yaml
            error_handling_workflow_backup_20250708_222410.yaml
            validation_pipeline_workflow_backup_20250708_222155.yaml
            bug_hunter_config_backup_20250708_222111.yaml
            architect_config_backup_20250708_221944.yaml
            agent_coordination_workflow_backup_20250708_222049.yaml
            config_backup_20250708_222749.yaml
            config_backup_20250708_222343.yaml
            config_backup_20250708_222300.yaml
            config_backup_20250708_222549.yaml
            config_backup_20250708_222359.yaml
            validation_pipeline_workflow_backup_20250708_223112.yaml
            config_backup_20250708_222922.yaml
            config_backup_20250708_222505.yaml
            agent_coordination_workflow_backup_20250708_221638.yaml
            agent_coordination_workflow_backup_20250708_221632.yaml
            config_backup_20250708_222244.yaml
            config_backup_20250708_221806.yaml
            config_backup_20250708_222138.yaml
            config_backup_20250708_221911.yaml
            validation_pipeline_workflow_backup_20250708_222217.yaml
            config_backup_20250708_223107.yaml
            bug_hunter_config_backup_20250708_223045.yaml
            bug_hunter_config_backup_20250708_221538.yaml
            config_backup_20250708_222054.yaml
            config_backup_20250708_222710.yaml
            config_backup_20250708_222811.yaml
            config_backup_20250708_222144.yaml
            config_backup_20250708_222510.yaml
            architect_config_backup_20250708_221933.yaml
            config_backup_20250708_222721.yaml
            error_handling_workflow_backup_20250708_154558.yaml
            config_backup_20250708_222527.yaml
            maestro_config_backup_20250708_222349.yaml
            config_backup_20250708_222206.yaml
            config_backup_20250708_222532.yaml
            agent_coordination_workflow_backup_20250708_222605.yaml
            config_backup_20250708_223012.yaml
            config_backup_20250708_221744.yaml
            config_backup_20250708_221828.yaml
            config_backup_20250708_222222.yaml
            config_backup_20250708_222117.yaml
            config_backup_20250708_222033.yaml
            config_backup_20250708_221438.yaml
            config_backup_20250708_222233.yaml
            config_backup_20250708_222255.yaml
            config_backup_20250708_221454.yaml
            config_backup_20250708_221554.yaml
            architect_config_backup_20250708_222638.yaml
            architect_config_backup_20250708_222338.yaml
            agent_coordination_workflow_backup_20250708_222944.yaml
            architect_config_backup_20250708_222005.yaml
            config_backup_20250708_221559.yaml
            config_backup_20250708_221812.yaml
            agent_coordination_workflow_backup_20250708_222754.yaml
            config_backup_20250708_222726.yaml
            architect_config_backup_20250708_222855.yaml
            config_backup_20250708_222333.yaml
            error_handling_workflow_backup_20250708_222621.yaml
            agent_coordination_workflow_backup_20250708_221855.yaml
            config_backup_20250708_221605.yaml
            config_backup_20250708_222516.yaml
            config_backup_20250708_222122.yaml
            config_backup_20250708_222928.yaml
            config_backup_20250708_222805.yaml
            architect_config_backup_20250708_221954.yaml
            bug_hunter_config_backup_20250708_222632.yaml
            bug_hunter_config_backup_20250708_222643.yaml
            config_backup_20250708_222311.yaml
            agent_coordination_workflow_backup_20250708_222743.yaml
            config_backup_20250708_221733.yaml
            bug_hunter_config_backup_20250708_221833.yaml
            maestro_config_backup_20250708_222327.yaml
            config_backup_20250708_222105.yaml
            architect_config_backup_20250708_221516.yaml
            architect_config_backup_20250708_222249.yaml
            config_backup_20250708_222133.yaml
            config_backup_20250708_222912.yaml
            config_backup_20250708_222027.yaml
            maestro_config_backup_20250708_222715.yaml
            config_backup_20250708_222738.yaml
            config_backup_20250708_221621.yaml
            bug_hunter_config_backup_20250708_221849.yaml
            config_backup_20250708_221627.yaml
            architect_config_backup_20250708_221839.yaml
            config_backup_20250708_221510.yaml
            architect_config_backup_20250708_222044.yaml
            config_backup_20250708_222454.yaml
            config_backup_20250708_222448.yaml
            config_backup_20250708_222616.yaml
            config_backup_20250708_221616.yaml
            agent_coordination_workflow_backup_20250708_221938.yaml
            config_backup_20250708_221800.yaml
            config_backup_20250708_221949.yaml
            config_backup_20250708_222654.yaml
            config_backup_20250708_222559.yaml
            config_backup_20250708_223122.yaml
            maestro_config_backup_20250708_221727.yaml
            config_backup_20250708_222316.yaml
            config_backup_20250708_222800.yaml
            config_backup_20250708_222432.yaml
            maestro_config_backup_20250708_222211.yaml
            config_backup_20250708_223128.yaml
            error_handling_workflow_backup_20250708_222838.yaml
            config_backup_20250708_221449.yaml
            architect_config_backup_20250708_221711.yaml
            config_backup_20250708_222917.yaml
            config_backup_20250708_222200.yaml
            config_backup_20250708_222100.yaml
            config_backup_20250708_223050.yaml
            bug_hunter_config_backup_20250708_222149.yaml
            config_backup_20250708_222500.yaml
            error_handling_workflow_backup_20250708_154516.yaml
            config_backup_20250708_222832.yaml
            config_backup_20250708_221928.yaml
            config_backup_20250708_221700.yaml
            bug_hunter_config_backup_20250708_221543.yaml
            agent_coordination_workflow_backup_20250708_221548.yaml
            architect_config_backup_20250708_221738.yaml
            config_backup_20250708_222610.yaml
            config_backup_20250708_221443.yaml
            config_backup_20250708_222649.yaml
            maestro_config_backup_20250708_222934.yaml
        workflows/
            validation_pipeline_workflow.yaml
            agent_coordination_workflow.yaml
            error_handling_workflow.yaml
    logs/
        error_prevention.log
        evolution_log_backup_20250708_155245.csv
        evolution_log.csv

## 2. RESUMO DAS INTERFACES (APIs Internas)


### Arquivo: `setup_multiple_keys.py`
- **Função:** `setup_env_template()`
  - *Cria template do .env com múltiplas chaves*
- **Função:** `create_key_test_script()`
  - *Cria script de teste para múltiplas chaves*
- **Função:** `show_providers_info()`
  - *Mostra informações sobre os provedores*

### Arquivo: `hephaestus_mcp_server.py`
- **Função:** `initialize_components()`
  - *Initialize Hephaestus components on-demand.*
- **Função:** `get_enhanced_agent(agent_type: str)`
  - *Get or create enhanced agent instances.*
- **Função:** `handle_list_tools()`
  - *Lista todas as ferramentas disponíveis para controlar o Hephaestus.*
- **Função:** `handle_call_tool(name: str, arguments: Dict[str, Any])`
  - *Processa chamadas de ferramentas das IAs.*
- **Função:** `handle_list_resources()`
  - *Lista recursos disponíveis.*
- **Função:** `handle_read_resource(uri: str)`
  - *Lê recursos do sistema.*
- **Função:** `main()`
  - *Função principal do MCP server.*

### Arquivo: `cli.py`

### Arquivo: `monitor_evolution.py`
- **Função:** `monitor_system()`
  - *Monitora o sistema em tempo real*

### Arquivo: `debug_keys.py`

### Arquivo: `analyze_meta_functionalities.py`
- **Função:** `analyze_logs()`
  - *Analisa logs para verificar status das meta-funcionalidades*
- **Função:** `check_memory_files()`
  - *Verifica arquivos de memória para estado das meta-funcionalidades*
- **Função:** `monitor_real_time_improvements()`
  - *Monitora melhorias em tempo real*
- **Função:** `show_key_log_patterns()`
  - *Mostra padrões-chave para procurar nos logs*

### Arquivo: `main.py`
- **Função:** `main()`
  - *Main function with startup validation.*

### Arquivo: `src/hephaestus/__init__.py`

### Arquivo: `src/hephaestus/agents/agent_expansion_coordinator.py`
- **Classe:** `AgentExpansionCoordinator(BaseAgent)`
  - *Coordenador para expansão e criação de novos agentes.*

### Arquivo: `src/hephaestus/agents/linter_agent.py`
- **Classe:** `LinterAgent`
  - *An agent that uses a static linter (ruff) to find, fix, and safely propose*

### Arquivo: `src/hephaestus/agents/bug_hunter_enhanced.py`
- **Classe:** `BugReport`
  - *Enhanced bug report with validation.*
- **Classe:** `BugFix`
  - *Enhanced bug fix with rollback support.*
- **Classe:** `BugHunterAgentEnhanced(EnhancedBaseAgent)`
  - *Enhanced Bug Hunter Agent using the new modular architecture.*

### Arquivo: `src/hephaestus/agents/__init__.py`

### Arquivo: `src/hephaestus/agents/enhanced_base.py`
- **Classe:** `EnhancedBaseAgent(EnhancedAgentMixin,BaseAgent,ABC)`
  - *Enhanced base agent with all modern capabilities:*
- **Classe:** `SimpleEnhancedAgent(EnhancedBaseAgent)`
  - *Simple enhanced agent for testing purposes.*

### Arquivo: `src/hephaestus/agents/self_reflection_agent.py`
- **Classe:** `SelfReflectionAgent`
  - *Agent that analyzes the Hephaestus codebase itself to identify patterns,*

### Arquivo: `src/hephaestus/agents/log_analysis_agent.py`
- **Classe:** `LogAnalysisAgent`
  - *An agent specialized in analyzing log files to identify issues and suggest improvements.*

### Arquivo: `src/hephaestus/agents/performance_analyzer.py`
- **Classe:** `PerformanceAnalysisAgent`
  - *An agent dedicated to analyzing the performance of Hephaestus.*

### Arquivo: `src/hephaestus/agents/base.py`
- **Classe:** `AgentCapability(Enum)`
  - *Standardized agent capabilities*
- **Classe:** `AgentPriority(Enum)`
  - *Standardized agent priority levels*
- **Classe:** `AgentStatus(Enum)`
  - *Standardized agent status*
- **Classe:** `AgentContext`
  - *Typed context system for agent operations*
- **Classe:** `AgentResult`
  - *Standardized agent result format*
- **Classe:** `AgentMetrics`
  - *Standardized agent performance metrics*
- **Classe:** `AgentInterface(Protocol)`
  - *Formal interface protocol for all agents*
- **Classe:** `BaseAgent(ABC)`
  - *Abstract base class implementing the AgentInterface protocol*
- **Classe:** `AgentRegistry`
  - *Registry for managing agent instances and their capabilities*
- **Função:** `get_agent_registry()`
  - *Get the global agent registry instance*

### Arquivo: `src/hephaestus/agents/cycle_monitor_agent.py`
- **Classe:** `CycleMonitorAgent(BaseAgent)`
  - *Agente para monitorar ciclos de execução do sistema.*

### Arquivo: `src/hephaestus/agents/error_detector_agent.py`
- **Classe:** `ErrorDetectorAgent`
  - *Agente especializado em detectar erros.*

### Arquivo: `src/hephaestus/agents/architect_enhanced.py`
- **Classe:** `ArchitectAgentEnhanced(EnhancedBaseAgent)`
  - *Enhanced Architect Agent using the new modular architecture.*

### Arquivo: `src/hephaestus/agents/dependency_fixer_agent.py`
- **Classe:** `DependencyFixerAgent`

### Arquivo: `src/hephaestus/agents/swarm_coordinator_agent.py`
- **Classe:** `SwarmCoordinatorAgent(BaseAgent)`
  - *Agente coordenador de enxame.*

### Arquivo: `src/hephaestus/agents/mixins.py`
- **Classe:** `ConfigMixin`
  - *Mixin for standardized configuration access.*
- **Classe:** `LoggerMixin`
  - *Mixin for standardized logger setup.*
- **Classe:** `MetricsMixin`
  - *Mixin for standardized metrics collection.*
- **Classe:** `CacheMixin`
  - *Mixin for standardized caching functionality.*
- **Classe:** `ValidationMixin`
  - *Mixin for common validation functionality.*
- **Classe:** `ErrorHandlingMixin`
  - *Mixin for standardized error handling.*
- **Classe:** `EnhancedAgentMixin(ConfigMixin,LoggerMixin,MetricsMixin,CacheMixin,ValidationMixin,ErrorHandlingMixin)`
  - *Combined mixin with all agent enhancements.*

### Arquivo: `src/hephaestus/agents/organizer_enhanced.py`
- **Classe:** `FileAnalysis`
  - *Enhanced file analysis for organization.*
- **Classe:** `DirectoryStructure`
  - *Enhanced directory structure proposal.*
- **Classe:** `OrganizationPlan`
  - *Enhanced organization plan with execution tracking.*
- **Classe:** `OrganizerAgentEnhanced(EnhancedBaseAgent)`
  - *Enhanced Organizer Agent using the new modular architecture.*

### Arquivo: `src/hephaestus/agents/maestro_enhanced.py`
- **Classe:** `MaestroAgentEnhanced(EnhancedBaseAgent)`
  - *Enhanced Maestro Agent using the new modular architecture.*

### Arquivo: `src/hephaestus/core/agent.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Arquivo: `src/hephaestus/core/objective_generator.py`
- **Função:** `generate_next_objective(model_config: Dict[str, str], current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, memory: Optional[Memory]=None, model_optimizer: Optional[ModelOptimizer]=None, current_objective: Optional[str]=None)`
  - *Generates the next evolutionary objective using code analysis and performance data.*
- **Função:** `generate_capacitation_objective(model_config: Dict[str, str], engineer_analysis: str, logger: logging.Logger, memory_summary: Optional[str]=None)`
  - *Generates an objective to create necessary new capabilities.*

### Arquivo: `src/hephaestus/core/brain.py`
- **Função:** `generate_next_objective(model_config: Dict[str, str], current_manifest: str, logger: logging.Logger, project_root_dir: str, config: Optional[Dict[str, Any]]=None, memory: Optional[Any]=None, model_optimizer: Optional[Any]=None, current_objective: Optional[str]=None)`
  - *Generates the next evolutionary objective using code analysis and performance data.*

### Arquivo: `src/hephaestus/core/__init__.py`

### Arquivo: `src/hephaestus/core/commit_message_generator.py`
- **Função:** `generate_commit_message(analysis_summary: str, objective: str, logger: logging.Logger)`
  - *Generates a concise and informative commit message using a rule-based system.*

### Arquivo: `src/hephaestus/core/arthur_interface_generator.py`
- **Classe:** `ArthurInterfaceGenerator`
  - *Gerador de interfaces especializadas para Arthur.*

### Arquivo: `src/hephaestus/core/code_metrics.py`
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

### Arquivo: `src/hephaestus/core/system_activator.py`
- **Classe:** `SystemActivator`
  - *Ativador de sistemas avançados.*
- **Função:** `get_system_activator(logger: logging.Logger, config: Dict, disable_signal_handlers: bool=False)`
  - *Obter instância do ativador de sistema.*

### Arquivo: `src/hephaestus/core/hot_reload_manager.py`
- **Classe:** `ModuleReloadHandler(FileSystemEventHandler)`
  - *Handler para detectar mudanças em arquivos Python.*
- **Classe:** `HotReloadManager`
  - *Gerenciador REAL de hot reload de módulos.*
- **Classe:** `SelfEvolutionEngine`
  - *Engine REAL de auto-evolução do sistema.*

### Arquivo: `src/hephaestus/core/code_validator.py`
- **Função:** `perform_deep_validation(file_path: Path, logger: logging.Logger)`
  - *Realiza uma análise profunda da qualidade do código Python.*
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool=True)`
  - *Valida se o código Python em um arquivo é sintaticamente correto e, opcionalmente, realiza uma análise profunda.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Arquivo: `src/hephaestus/core/patch_applicator.py`
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
- **Classe:** `PatchApplicator`
  - *Main class for applying patches to files.*

### Arquivo: `src/hephaestus/core/cycle_runner.py`
- **Classe:** `CycleRunner`
  - *Manages the main asynchronous execution loop of the Hephaestus agent.*

### Arquivo: `src/hephaestus/core/memory.py`
- **Classe:** `SemanticPattern`
  - *Represents a learned pattern in objectives or strategies.*
- **Classe:** `Heuristic`
  - *Represents a learned heuristic about what works and what doesn't.*
- **Classe:** `SemanticCluster`
  - *Groups similar objectives/strategies for pattern recognition.*
- **Classe:** `Memory`
  - *Manages persistent memory for the Hephaestus agent, storing historical data*

### Arquivo: `src/hephaestus/core/coverage_activator.py`
- **Classe:** `CoverageActivator`
  - *Ativador de cobertura para aumentar a utilização do sistema.*

### Arquivo: `src/hephaestus/core/cognitive_evolution_manager.py`
- **Classe:** `CognitiveEvolutionManager`
  - *Gerenciador de evolução cognitiva do sistema.*
- **Função:** `get_evolution_manager(config: Dict, logger: logging.Logger, memory, model_optimizer)`
  - *Obter instância do gerenciador de evolução.*
- **Função:** `start_cognitive_evolution(model_config: str, logger: logging.Logger, memory, model_optimizer)`
  - *Iniciar evolução cognitiva.*

### Arquivo: `src/hephaestus/core/prompt_builder.py`
- **Função:** `build_memory_context_section(memory_summary: Optional[str])`
  - *Constrói a seção de contexto da memória para os prompts.*
- **Função:** `build_initial_objective_prompt(memory_context_section: str)`
  - *Constrói o prompt para gerar o objetivo inicial quando não há manifesto ou análise de código.*
- **Função:** `build_meta_analysis_objective_prompt(current_objective: str, original_failed_objective: str, error_reason_for_meta: str, performance_summary_str: str, memory_context_section: str, capabilities_content: str, roadmap_content: str)`
  - *Constrói o prompt para gerar um objetivo estratégico após uma meta-análise de falha.*
- **Função:** `build_standard_objective_prompt(memory_context_section: str, performance_summary_str: str, code_analysis_summary_str: str, current_manifest: str, capabilities_content: str, roadmap_content: str, dashboard_content: str)`
  - *Constrói o prompt padrão para gerar o próximo objetivo estratégico.*

### Arquivo: `src/hephaestus/core/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

### Arquivo: `src/hephaestus/core/agents/autonomous_monitor_agent.py`
- **Classe:** `AutonomousMonitorAgent`
  - *Agente de monitoramento autônomo do sistema.*

### Arquivo: `src/hephaestus/data_sources/__init__.py`

### Arquivo: `src/hephaestus/data_sources/crypto_apis.py`
- **Classe:** `CryptoPrice`
  - *Cryptocurrency price data.*
- **Classe:** `CryptoDataProvider`
  - *Multi-source cryptocurrency data provider with arbitrage detection.*
- **Função:** `main()`
  - *Test the crypto data provider.*

### Arquivo: `src/hephaestus/api/__init__.py`

### Arquivo: `src/hephaestus/api/dashboard_server.py`
- **Classe:** `DashboardServer`
  - *Simple web dashboard for Hephaestus monitoring and validation.*
- **Função:** `start_dashboard(host: str='localhost', port: int=8080)`
  - *Start the dashboard server.*

### Arquivo: `src/hephaestus/api/rest/main.py`
- **Classe:** `OptimizedAgentInitializer`
  - *Inicializador otimizado para agentes do sistema.*
- **Função:** `start_background_threads(logger: logging.Logger)`
  - *Inicia threads de background de forma otimizada.*
- **Função:** `lifespan(app: FastAPI)`
  - *Lifespan context manager for FastAPI startup and shutdown events (OPTIMIZED).*
- **Função:** `load_config()`
  - *Load configuration for the application*
- **Classe:** `LoginRequest(BaseModel)`
- **Classe:** `TokenResponse(BaseModel)`
- **Classe:** `RefreshTokenRequest(BaseModel)`
- **Classe:** `ObjectiveRequest(BaseModel)`
- **Classe:** `DeepReflectionRequest(BaseModel)`
- **Classe:** `AsyncEvolutionRequest(BaseModel)`
- **Classe:** `InterfaceGenerationRequest(BaseModel)`
- **Classe:** `AgentConfigRequest(BaseModel)`
- **Classe:** `SystemStatusResponse(BaseModel)`
- **Função:** `add_process_time_header(request: Request, call_next)`
- **Função:** `rate_limiting_middleware(request: Request, call_next)`
  - *Rate limiting middleware using auth manager*
- **Função:** `get_auth_user(credentials: HTTPAuthorizationCredentials=Depends(security))`
  - *Authenticate user with JWT token*
- **Função:** `periodic_log_analysis_task()`
  - *A background task that periodically queues system monitoring tasks.*
- **Função:** `worker_thread()`
  - *Starts the agent's main execution loop.*
- **Função:** `process_objective(objective_data: Any)`
  - *DEPRECATED: This logic is now handled by the CycleRunner.run() loop.*
- **Função:** `login(request: LoginRequest)`
  - *Authenticate user and return JWT tokens*
- **Função:** `refresh_token(request: RefreshTokenRequest)`
  - *Refresh access token using refresh token*
- **Função:** `logout(auth_user: dict=Depends(get_auth_user))`
  - *Logout user and invalidate session*
- **Função:** `root()`
  - *API Root - Welcome page with navigation*
- **Função:** `health_check()`
  - *Enhanced health check with comprehensive system status*
- **Função:** `get_status()`
  - *Get detailed system status including all subsystems and current cycle/goal info*
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
- **Função:** `get_swarm_status(auth_user: dict=Depends(get_auth_user))`
  - *Get swarm communication and coordination status*
- **Função:** `start_swarm_conversation(request: dict, auth_user: dict=Depends(get_auth_user))`
  - *Start a conversation between agents*
- **Função:** `coordinate_swarm_task(request: dict, auth_user: dict=Depends(get_auth_user))`
  - *Coordinate a complex task using swarm intelligence*
- **Função:** `resolve_swarm_conflict(request: dict, auth_user: dict=Depends(get_auth_user))`
  - *Resolve conflicts between agents using negotiation*
- **Função:** `start_collective_problem_solving(request: dict, auth_user: dict=Depends(get_auth_user))`
  - *Start collective problem solving session*
- **Função:** `start_knowledge_sharing(request: dict, auth_user: dict=Depends(get_auth_user))`
  - *Start knowledge sharing session between agents*
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
- **Função:** `analyze_project_structure(auth_user: dict=Depends(get_auth_user))`
  - *Analisa a estrutura atual do projeto*
- **Função:** `generate_organization_plan(auth_user: dict=Depends(get_auth_user))`
  - *Gera plano de reorganização do projeto*
- **Função:** `execute_organization_plan(dry_run: bool=Body(True, description='Se True, apenas simula a execução'), auth_user: dict=Depends(get_auth_user))`
  - *Executa o plano de reorganização*
- **Função:** `get_organization_report(auth_user: dict=Depends(get_auth_user))`
  - *Gera relatório completo da organização*
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
- **Função:** `start_bug_hunter(auth_user: dict=Depends(get_auth_user))`
  - *Start bug hunting monitoring*
- **Função:** `stop_bug_hunter(auth_user: dict=Depends(get_auth_user))`
  - *Stop bug hunting monitoring*
- **Função:** `get_bug_hunter_status(auth_user: dict=Depends(get_auth_user))`
  - *Get bug hunter status and report*
- **Função:** `trigger_bug_scan(auth_user: dict=Depends(get_auth_user))`
  - *Trigger immediate bug scan*
- **Função:** `global_exception_handler(request: Request, exc: Exception)`
  - *Global exception handler that reports errors to the detector*
- **Função:** `worker()`
- **Função:** `activate_maximum_evolution(auth_user: dict=Depends(get_auth_user))`
  - *Ativa o modo de evolução máxima para desenvolvimento autônomo*
- **Função:** `get_protected_processes(auth_user: dict=Depends(get_auth_user))`
  - *Lista processos protegidos que não serão mortos pelo CycleMonitorAgent*
- **Função:** `add_protected_process(process_name: str, auth_user: dict=Depends(get_auth_user))`
  - *Adiciona um processo à lista de protegidos*
- **Função:** `activate_system_features(auth_user: dict=Depends(get_auth_user))`
  - *Ativa funcionalidades não utilizadas do sistema*
- **Função:** `start_night_evolution(auth_user: dict=Depends(get_auth_user))`
  - *Inicia evolução noturna autônoma para desenvolvimento contínuo*
- **Função:** `analyze_dependencies(error_logs: str=Body(..., description='Error logs to analyze for import issues'), auth_user: dict=Depends(get_auth_user))`
  - *Analyze and fix import/dependency issues*
- **Função:** `get_dependency_fixer_status(auth_user: dict=Depends(get_auth_user))`
  - *Get Dependency Fixer Agent status*
- **Função:** `get_cycle_monitor_status(auth_user: dict=Depends(get_auth_user))`
  - *Get cycle monitor status and system health*
- **Função:** `force_cycle_cleanup(auth_user: dict=Depends(get_auth_user))`
  - *Force immediate cleanup of all detected issues*
- **Função:** `get_agent_expansion_status(auth_user: dict=Depends(get_auth_user))`
  - *Get status of agent expansion coordination*
- **Função:** `get_agent_utilization_analysis(auth_user: dict=Depends(get_auth_user))`
  - *Get detailed analysis of agent utilization*
- **Função:** `get_agent_activation_plan(auth_user: dict=Depends(get_auth_user))`
  - *Get plan for activating underutilized agents*
- **Função:** `get_agent_objectives(auth_user: dict=Depends(get_auth_user))`
  - *Get objectives for underutilized agents*
- **Função:** `activate_underutilized_agents(auth_user: dict=Depends(get_auth_user))`
  - *Ativa agentes subutilizados com objetivos específicos*
- **Função:** `activate_all_agents_in_main_cycle(auth_user: dict=Depends(get_auth_user))`
  - *Ativa todos os agentes no ciclo principal automaticamente*
- **Função:** `get_system_health()`
  - *Endpoint para verificar a saúde do sistema*
- **Função:** `get_detailed_health()`
  - *Endpoint para relatório detalhado de saúde*
- **Função:** `get_autonomous_monitor_status(auth_user: dict=Depends(get_auth_user))`
  - *Get autonomous monitor status and current issues*
- **Função:** `get_autonomous_monitor_issues(auth_user: dict=Depends(get_auth_user))`
  - *Get current issues detected by autonomous monitor*
- **Função:** `start_autonomous_monitoring(auth_user: dict=Depends(get_auth_user))`
  - *Start autonomous monitoring system*
- **Função:** `stop_autonomous_monitoring(auth_user: dict=Depends(get_auth_user))`
  - *Stop autonomous monitoring system*
- **Função:** `get_prevention_report(auth_user: dict=Depends(get_auth_user))`
  - *Get error prevention and monitoring report*
- **Função:** `get_enhanced_cache_stats(auth_user: dict=Depends(get_auth_user))`
  - *Get enhanced cache statistics*
- **Função:** `get_enhanced_monitor_metrics(category: str=None, auth_user: dict=Depends(get_auth_user))`
  - *Get enhanced monitoring metrics*
- **Função:** `track_metric(name: str=Body(..., description='Metric name'), value: Any=Body(..., description='Metric value'), category: str=Body('general', description='Metric category'), auth_user: dict=Depends(get_auth_user))`
  - *Track a metric using enhanced monitoring*
- **Função:** `validate_with_enhanced_system(target: str=Body(..., description='Target to validate (file path, code, etc.)'), validation_type: str=Body('comprehensive', description='Type of validation'), auth_user: dict=Depends(get_auth_user))`
  - *Run validation using enhanced validation system*
- **Função:** `generate_enhanced_interface(interface_type: str=Body(..., description='Type of interface to generate'), data: Dict[str, Any]=Body(..., description='Data for interface generation'), auth_user: dict=Depends(get_auth_user))`
  - *Generate interface using enhanced interface system*
- **Função:** `get_enhanced_systems_status(auth_user: dict=Depends(get_auth_user))`
  - *Get status of all enhanced systems*
- **Função:** `get_evolution_status(auth_user: dict=Depends(get_auth_user))`
  - *Get complete evolution system status - Real-Time Evolution, Parallel Testing, Collective Intelligence*
- **Função:** `test_parallel_strategies(objective: str=Body(..., description='Objective to test strategies for'), strategy_count: int=Body(3, description='Number of strategies to test in parallel'), auth_user: dict=Depends(get_auth_user))`
  - *Test multiple strategies in parallel and return the best performing one*
- **Função:** `get_collective_insights(limit: int=10, auth_user: dict=Depends(get_auth_user))`
  - *Get collective intelligence insights from the network*
- **Função:** `trigger_evolution_mutation(mutation_type: str=Body(..., description='Type of mutation to trigger'), auth_user: dict=Depends(get_auth_user))`
  - *Manually trigger a specific type of evolution mutation*
- **Função:** `start_real_time_evolution(auth_user: dict=Depends(get_auth_user))`
  - *Start the real-time evolution engine*
- **Função:** `stop_real_time_evolution(auth_user: dict=Depends(get_auth_user))`
  - *Stop the real-time evolution engine*
- **Função:** `demo_full_evolution_system(auth_user: dict=Depends(get_auth_user))`
  - *Comprehensive demonstration of the full evolution system working together*

### Arquivo: `src/hephaestus/api/rest/error_resilience.py`
- **Classe:** `SelfReflectionRequest(BaseModel)`
  - *Modelo Pydantic para validação de requisições de auto-reflexão*
- **Classe:** `AwarenessMetric(BaseModel)`
  - *Modelo para métricas de auto-consciência*
- **Classe:** `CognitiveState(BaseModel)`
  - *Modelo para estado cognitivo*
- **Classe:** `SelfAwarenessResponse(BaseModel)`
  - *Modelo para respostas de auto-consciência*
- **Classe:** `ErrorResilience`
  - *Classe principal para funcionalidades de resiliência a erros*
- **Classe:** `MCPErrorHandler`
  - *Specialized error handler for MCP server functions*
- **Classe:** `RecoveryMechanism`
  - *Mechanisms for recovering from failures*

### Arquivo: `src/hephaestus/api/rest/validation_service.py`
- **Classe:** `SelfReflectionRequest(BaseModel)`
  - *Pydantic model for deep_self_reflection endpoint request*
- **Classe:** `SelfReflectionResponse(BaseModel)`
  - *Pydantic model for deep_self_reflection endpoint response*
- **Classe:** `AwarenessReportRequest(BaseModel)`
  - *Pydantic model for self_awareness_report endpoint request*
- **Classe:** `AwarenessReportResponse(BaseModel)`
  - *Pydantic model for self_awareness_report endpoint response*
- **Classe:** `ValidationService`
  - *Service for validating and recovering from invalid responses*

### Arquivo: `src/hephaestus/api/rest/validation.py`
- **Classe:** `SelfReflectionSchema(BaseModel)`
  - *Schema for deep_self_reflection endpoint*
- **Classe:** `AwarenessReportSchema(BaseModel)`
  - *Schema for self_awareness_report endpoint*
- **Função:** `validate_self_reflection(data: Dict[str, Any])`
  - *Validate deep_self_reflection response*
- **Função:** `validate_awareness_report(data: Dict[str, Any])`
  - *Validate self_awareness_report response*

### Arquivo: `src/hephaestus/api/mcp/server.py`
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

### Arquivo: `src/hephaestus/api/cli/main.py`
- **Função:** `run(continuous: bool=typer.Option(False, '--continuous', '-c', help='Run in continuous mode'), max_cycles: int=typer.Option(None, '--max-cycles', '-m', help='Maximum number of evolution cycles'))`
  - *Run the Hephaestus agent*
- **Função:** `submit(objective: str)`
  - *Submit a new objective to the agent*
- **Função:** `status()`
  - *Check agent status*
- **Função:** `cleanup()`
  - *Limpa logs e backups antigos*

### Arquivo: `src/hephaestus/validation/__init__.py`

### Arquivo: `src/hephaestus/validation/unified_validator.py`
- **Classe:** `ValidationResult`
  - *Result of a validation check.*
- **Classe:** `ValidationSuite`
  - *Collection of validation results.*
- **Classe:** `UnifiedValidator`
  - *Comprehensive validation system for the Hephaestus platform.*
- **Função:** `get_unified_validator()`
  - *Get the global unified validator instance.*

### Arquivo: `src/hephaestus/utils/api_key_manager.py`
- **Classe:** `APIKey`
  - *Representa uma chave API com metadados de saúde*
- **Classe:** `APIKeyManager`
  - *🔑 Gerenciador de Chaves API com Redundância Inteligente*
- **Função:** `get_api_key_manager()`
  - *Get singleton instance of APIKeyManager*

### Arquivo: `src/hephaestus/utils/__init__.py`

### Arquivo: `src/hephaestus/utils/json_parser.py`
- **Função:** `_fix_common_json_errors(json_string: str, logger: logging.Logger)`
  - *Tenta corrigir erros comuns de JSON gerado por LLM.*
- **Função:** `_extract_json_from_response(raw_str: str, logger: logging.Logger)`
  - *Extract JSON content from various response formats.*
- **Função:** `parse_json_response(raw_str: str, logger: logging.Logger)`
  - *Analyzes a raw string to find and parse a JSON object, cleaning and fixing it as needed.*

### Arquivo: `src/hephaestus/utils/llm_manager.py`
- **Classe:** `LLMCallManager`
  - *Manages LLM calls with standardized retry, caching, and metrics.*
- **Função:** `llm_call_with_metrics(func: Callable)`
  - *Decorator to automatically add metrics to LLM call methods.*
- **Função:** `llm_call_with_retry(max_retries: int=3, fallback_models: Optional[List[str]]=None)`
  - *Decorator to automatically add retry logic to LLM call methods.*

### Arquivo: `src/hephaestus/utils/agent_factory.py`
- **Classe:** `AgentFactory`
  - *Factory for creating agents with standardized dependency injection.*
- **Classe:** `AgentRegistry`
  - *Registry for managing active agent instances.*
- **Função:** `get_global_registry()`
  - *Get the global agent registry.*

### Arquivo: `src/hephaestus/utils/error_prevention_system.py`
- **Classe:** `ErrorSeverity(Enum)`
- **Classe:** `ErrorType(Enum)`
- **Classe:** `ErrorEvent`
- **Classe:** `ConstructorValidator`
  - *Valida construtores de agentes e componentes*
- **Classe:** `HealthMonitor`
  - *Monitora a saúde do sistema continuamente*
- **Classe:** `AutoRecovery`
  - *Sistema de recuperação automática*
- **Classe:** `ErrorPreventionSystem`
  - *Sistema principal de prevenção de erros*
- **Função:** `validate_constructor(error_prevention_system: ErrorPreventionSystem)`
  - *Decorator para validar construtores automaticamente*

### Arquivo: `src/hephaestus/utils/continuous_monitor.py`
- **Classe:** `SystemMetrics`
- **Classe:** `Alert`
- **Classe:** `ContinuousMonitor`
  - *Monitora o sistema continuamente e detecta problemas*
- **Função:** `get_continuous_monitor(logger: logging.Logger)`
  - *Retorna instância singleton do monitor*

### Arquivo: `src/hephaestus/utils/smart_validator.py`
- **Classe:** `SmartValidator`
  - *Validador inteligente para diferentes tipos de dados*

### Arquivo: `src/hephaestus/utils/git_utils.py`
- **Função:** `initialize_git_repository(logger: logging.Logger)`
  - *Ensure a git repository exists and is configured.*

### Arquivo: `src/hephaestus/utils/log_cleaner.py`
- **Classe:** `LogCleaner`
  - *Sistema de limpeza automática de logs e backups*
- **Função:** `get_log_cleaner(config: Dict[str, Any], logger: logging.Logger)`
  - *Factory function para criar LogCleaner*

### Arquivo: `src/hephaestus/utils/llm_client.py`
- **Função:** `call_gemini_api_with_key(api_key: str, model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Calls the Google Gemini API with a specific key.*
- **Função:** `call_gemini_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Calls the Google Gemini API with automatic key management.*
- **Função:** `call_openrouter_api_with_key(api_key: str, model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Calls OpenRouter API with a specific key.*
- **Função:** `call_openrouter_api(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Calls OpenRouter API with automatic key management.*
- **Função:** `call_llm_with_fallback(model_config: dict, prompt: str, temperature: float, logger: logging.Logger)`
  - *Orchestrates LLM calls with a primary and fallback model.*
- **Função:** `call_openrouter_api_async(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Async version of OpenRouter API call.*
- **Função:** `call_gemini_api_async(model: str, prompt: str, temperature: float, max_tokens: Optional[int], logger: logging.Logger)`
  - *Async version of Gemini API call (runs in thread pool since google.generativeai is sync).*
- **Função:** `call_llm_with_fallback_async(model_config: dict, prompt: str, temperature: float, logger: logging.Logger)`
  - *Async version of LLM call with fallback.*

### Arquivo: `src/hephaestus/utils/llm_optimizer.py`
- **Classe:** `LLMCallOptimizer`
  - *Otimizador inteligente para chamadas LLM*

### Arquivo: `src/hephaestus/utils/startup_validator.py`
- **Classe:** `ValidationResult`
- **Classe:** `StartupValidator`
  - *Valida todos os componentes críticos antes do startup*
- **Função:** `validate_startup(config: Dict[str, Any])`
  - *Decorator para validar startup antes de executar uma função*

### Arquivo: `src/hephaestus/utils/metrics_collector.py`
- **Classe:** `MetricsCollector`
  - *Centralized metrics collection system for all agents and services.*
- **Função:** `get_global_metrics_collector()`
  - *Get the global metrics collector instance.*

### Arquivo: `src/hephaestus/utils/advanced_logging.py`
- **Função:** `setup_advanced_logging(name: str, level: int=logging.INFO)`
  - *Setup advanced logging configuration*

### Arquivo: `src/hephaestus/utils/config_manager.py`
- **Classe:** `ConfigManager`
  - *Centralized configuration manager with caching and hot reload support.*

### Arquivo: `src/hephaestus/utils/error_handling.py`
- **Função:** `safe_execute(func: Callable, *args, **kwargs)`
  - *Execute function safely with error handling*
- **Função:** `retry_with_backoff(func: Callable, max_retries: int=3, backoff_factor: int=2)`
  - *Retry function with exponential backoff*

### Arquivo: `src/hephaestus/utils/infrastructure_manager.py`
- **Classe:** `InfrastructureManager`
  - *Gerenciador de infraestrutura básica do sistema*
- **Função:** `ensure_basic_infrastructure(logger: Optional[logging.Logger]=None)`
  - *Função utilitária para garantir infraestrutura básica*
- **Função:** `diagnose_and_fix_infrastructure(logger: Optional[logging.Logger]=None)`
  - *Função utilitária para diagnosticar e corrigir infraestrutura*
- **Função:** `get_infrastructure_manager(logger: Optional[logging.Logger]=None)`
  - *Retorna instância do gerenciador de infraestrutura*

### Arquivo: `src/hephaestus/utils/intelligent_cache.py`
- **Classe:** `IntelligentCache`
  - *Cache inteligente com TTL e LRU*
- **Função:** `cached(ttl: int=3600)`
  - *Decorator para cache automático*

### Arquivo: `src/hephaestus/utils/rate_limiter.py`
- **Classe:** `RateLimitConfig`
  - *Configuração de rate limiting*
- **Classe:** `RateLimiter`
  - *Sistema de rate limiting global para chamadas à API*
- **Função:** `get_global_rate_limiter(config: Dict[str, Any], logger: logging.Logger)`
  - *Obtém a instância global do rate limiter*
- **Função:** `with_rate_limiting(func, *args, **kwargs)`
  - *Decorator para aplicar rate limiting a uma função*

### Arquivo: `src/hephaestus/utils/tool_executor.py`
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

### Arquivo: `src/hephaestus/utils/logger_factory.py`
- **Classe:** `LoggerFactory`
  - *Factory for creating standardized loggers with consistent formatting.*

### Arquivo: `src/hephaestus/utils/project_scanner.py`
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

### Arquivo: `src/hephaestus/utils/queue_manager.py`
- **Classe:** `QueueManager`

### Arquivo: `src/hephaestus/utils/ux_enhancer.py`
- **Classe:** `UXEnhancer`
  - *Melhorador de experiência do usuário*

### Arquivo: `src/hephaestus/utils/night_improvements.py`
- **Classe:** `ContinuousImprovement`
  - *Sistema de melhorias contínuas*

### Arquivo: `src/hephaestus/utils/config_loader.py`
- **Função:** `load_config()`
  - *Load configuration using Hydra.*

### Arquivo: `src/hephaestus/monitoring/__init__.py`

### Arquivo: `src/hephaestus/monitoring/unified_dashboard.py`
- **Classe:** `SystemHealth`
  - *System health status.*
- **Classe:** `AgentStatus`
  - *Individual agent status.*
- **Classe:** `UnifiedDashboard`
  - *Central monitoring dashboard for the entire Hephaestus system.*
- **Função:** `get_unified_dashboard()`
  - *Get the global unified dashboard instance.*

### Arquivo: `src/hephaestus/monitoring/predictive_failure_dashboard.py`
- **Classe:** `PredictiveFailureDashboard`
  - *Dashboard para monitorar o desempenho do Predictive Failure Engine*
- **Função:** `get_predictive_failure_dashboard(config: Dict[str, Any], logger: logging.Logger, memory_path: str)`
  - *Get singleton instance of the dashboard*

### Arquivo: `src/hephaestus/intelligence/self_awareness.py`
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

### Arquivo: `src/hephaestus/intelligence/__init__.py`

### Arquivo: `src/hephaestus/intelligence/real_time_evolution_engine.py`
- **Classe:** `MutationType(Enum)`
  - *Tipos de mutação que podem ser aplicadas*
- **Classe:** `EvolutionPhase(Enum)`
  - *Fases da evolução em tempo real*
- **Classe:** `EvolutionCandidate`
  - *Candidato a evolução que está sendo testado*
- **Classe:** `EvolutionMetrics`
  - *Métricas de performance da evolução*
- **Classe:** `RealTimeEvolutionEngine`
  - *⚡ Engine de Evolução em Tempo Real - O Coração da Auto-Melhoria*
- **Função:** `get_real_time_evolution_engine(config: Dict[str, Any], logger: logging.Logger, collective_network=None)`
  - *Get singleton instance of the Real-Time Evolution Engine*

### Arquivo: `src/hephaestus/intelligence/meta_objective_generator.py`
- **Classe:** `ObjectiveType(Enum)`
  - *Tipos de objetivos que podem ser gerados*
- **Classe:** `ObjectiveComplexity(Enum)`
  - *Níveis de complexidade dos objetivos*
- **Classe:** `ObjectiveScope(Enum)`
  - *Escopo dos objetivos*
- **Classe:** `GeneratedObjective`
  - *Objetivo gerado pelo sistema*
- **Classe:** `CapabilityAssessment`
  - *Avaliação das capacidades de geração de objetivos*
- **Classe:** `MetaObjectivePattern`
  - *Padrão identificado na geração de meta-objetivos*
- **Classe:** `MetaObjectiveGenerator`
  - *🎯 Meta-Objective Generator - Sistema que gera objetivos para melhorar objetivos*
- **Função:** `get_meta_objective_generator(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of MetaObjectiveGenerator*

### Arquivo: `src/hephaestus/intelligence/evolution_callbacks.py`
- **Classe:** `EvolutionChange`
  - *Representa uma mudança REAL aplicada ao sistema*
- **Classe:** `RealEvolutionCallbacks`
  - *Sistema de callbacks FUNCIONAIS que aplicam mutações reais no sistema.*
- **Função:** `get_evolution_callbacks(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of Real Evolution Callbacks*

### Arquivo: `src/hephaestus/intelligence/model_optimizer.py`
- **Classe:** `ModelPerformanceData`
  - *Performance data for a specific model call*
- **Classe:** `FineTuningDataset`
  - *A dataset prepared for fine-tuning*
- **Classe:** `ModelOptimizer`
  - *Advanced system for model self-optimization through performance data collection*
- **Função:** `get_model_optimizer(model_config: Dict[str, str], logger: logging.Logger)`
  - *Factory function to get a singleton instance of the ModelOptimizer.*

### Arquivo: `src/hephaestus/intelligence/parallel_reality_testing.py`
- **Classe:** `TestEnvironmentType(Enum)`
  - *Tipos de ambiente de teste*
- **Classe:** `StrategyType(Enum)`
  - *Tipos de estratégias que podem ser testadas*
- **Classe:** `TestStrategy`
  - *Representa uma estratégia a ser testada*
- **Classe:** `TestResult`
  - *Resultado de um teste de estratégia*
- **Classe:** `ParallelRealityTester`
  - *Sistema de teste paralelo que executa múltiplas estratégias simultaneamente*
- **Função:** `get_parallel_reality_tester(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of Parallel Reality Tester*

### Arquivo: `src/hephaestus/intelligence/collective_intelligence_network.py`
- **Classe:** `KnowledgeType(Enum)`
  - *Tipos de conhecimento compartilhado*
- **Classe:** `KnowledgeRelevance(Enum)`
  - *Níveis de relevância do conhecimento*
- **Classe:** `KnowledgeItem`
  - *Item de conhecimento compartilhado*
- **Classe:** `AgentProfile`
  - *Perfil de um agente na rede*
- **Classe:** `CollectiveInsight`
  - *Insight coletivo gerado pela rede*
- **Classe:** `CollectiveIntelligenceNetwork`
  - *Rede de inteligência coletiva que permite compartilhamento de conhecimento*
- **Função:** `get_collective_intelligence_network(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of Collective Intelligence Network*

### Arquivo: `src/hephaestus/intelligence/root_cause_analyzer.py`
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

### Arquivo: `src/hephaestus/intelligence/knowledge_system.py`
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

### Arquivo: `src/hephaestus/intelligence/self_awareness_core.py`
- **Classe:** `CognitiveState(Enum)`
  - *Estados cognitivos possíveis do sistema*
- **Classe:** `BiasType(Enum)`
  - *Tipos de vieses cognitivos que podem ser detectados*
- **Classe:** `SelfOptimizationTrigger(Enum)`
  - *Triggers que indicam necessidade de auto-otimização*
- **Classe:** `CognitiveStateSnapshot`
  - *Snapshot do estado cognitivo em um momento*
- **Classe:** `SelfReflection`
  - *Resultado de uma sessão de auto-reflexão profunda*
- **Classe:** `PersonalityProfile`
  - *Perfil de personalidade do sistema*
- **Classe:** `SelfAwarenessCore`
  - *🧠 Self-Awareness Core 2.0*
- **Função:** `get_self_awareness_core(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of SelfAwarenessCore*

### Arquivo: `src/hephaestus/intelligence/evolution_analytics.py`
- **Classe:** `EvolutionMetric`
  - *Métrica de evolução capturada*
- **Classe:** `EvolutionTrend`
  - *Tendência de evolução identificada*
- **Classe:** `EvolutionAnalytics`
  - *Sistema de análise de evolução de longo prazo*
- **Função:** `get_evolution_analytics(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of Evolution Analytics*

### Arquivo: `src/hephaestus/intelligence/parallel_reality_tester.py`
- **Classe:** `RealityTestStatus(Enum)`
  - *Status de um teste de realidade paralela*
- **Classe:** `StrategyType(Enum)`
  - *Tipos de estratégias que podem ser testadas*
- **Classe:** `RealityTest`
  - *Representa um teste de realidade (estratégia sendo executada)*
- **Classe:** `ParallelTestSession`
  - *Sessão de teste paralelo com múltiplas realidades*
- **Classe:** `ParallelRealityTester`
  - *🧪 Parallel Reality Testing System*
- **Função:** `get_parallel_reality_tester(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of ParallelRealityTester*

### Arquivo: `src/hephaestus/intelligence/temporal_intelligence.py`
- **Classe:** `TemporalPerspective(Enum)`
  - *Perspectivas temporais do sistema*
- **Classe:** `TemporalScope(Enum)`
  - *Escopo temporal de análise*
- **Classe:** `PredictionConfidence(Enum)`
  - *Níveis de confiança nas predições*
- **Classe:** `TemporalPattern`
  - *Padrão identificado na linha temporal*
- **Classe:** `FuturePrediction`
  - *Predição sobre eventos/necessidades futuras*
- **Classe:** `TemporalContext`
  - *Contexto temporal completo para tomada de decisões*
- **Classe:** `TemporalIntelligence`
  - *🕐 Temporal Intelligence System - Consciência temporal completa*
- **Função:** `get_temporal_intelligence(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of TemporalIntelligence*

### Arquivo: `src/hephaestus/intelligence/predictive_failure_engine.py`
- **Classe:** `FailurePattern`
  - *Representa um padrão de falha identificado*
- **Classe:** `ObjectiveAnalysis`
  - *Análise preditiva de um objetivo*
- **Classe:** `PredictiveFailureEngine`
  - *🔮 Engine de Predição de Falhas - O Oráculo do Hephaestus*
- **Função:** `get_predictive_failure_engine(config: Dict[str, Any], logger: logging.Logger, memory_path: str)`
  - *Get singleton instance of the Predictive Failure Engine*

### Arquivo: `src/hephaestus/intelligence/meta_core.py`
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

### Arquivo: `src/hephaestus/intelligence/meta_learning_intelligence.py`
- **Classe:** `LearningType(Enum)`
  - *Tipos de aprendizado que o sistema pode fazer*
- **Classe:** `LearningContext(Enum)`
  - *Contextos onde o aprendizado acontece*
- **Classe:** `LearningEffectiveness(Enum)`
  - *Níveis de efetividade do aprendizado*
- **Classe:** `LearningEvent`
  - *Representa um evento de aprendizado*
- **Classe:** `LearningPattern`
  - *Padrão de aprendizado identificado*
- **Classe:** `AdaptiveMemory`
  - *Sistema de memória que adapta retention baseado na relevância*
- **Classe:** `MetaLearningIntelligence`
  - *🧠 Meta-Learning Intelligence System*
- **Função:** `get_meta_learning_intelligence(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of MetaLearningIntelligence*

### Arquivo: `src/hephaestus/intelligence/dynamic_agent_dna.py`
- **Classe:** `GeneType(Enum)`
  - *Tipos de genes cognitivos*
- **Classe:** `SelectionPressure(Enum)`
  - *Pressões de seleção natural*
- **Classe:** `CognitiveGene`
  - *Gene cognitivo individual*
- **Classe:** `AgentDNA`
  - *DNA cognitivo completo de um agente*
- **Classe:** `PopulationStats`
  - *Estatísticas da população*
- **Classe:** `DynamicAgentDNA`
  - *🧬 Dynamic Agent DNA System - Evolução darwiniana para agentes*
- **Função:** `get_dynamic_agent_dna(config: Dict[str, Any], logger: logging.Logger)`
  - *Get singleton instance of DynamicAgentDNA*

### Arquivo: `src/hephaestus/services/__init__.py`

### Arquivo: `src/hephaestus/services/communication/inter_agent.py`
- **Classe:** `MessageType(Enum)`
  - *Tipos de mensagens entre agentes*
- **Classe:** `AgentRole(Enum)`
  - *Papéis dos agentes na comunicação*
- **Classe:** `AgentMessage`
  - *Mensagem entre agentes*
- **Classe:** `Conversation`
  - *Conversa entre múltiplos agentes*
- **Classe:** `CollaborationSession`
  - *Sessão de colaboração para tarefas complexas*
- **Classe:** `InterAgentCommunication`
  - *Sistema de comunicação inter-agente*
- **Função:** `get_inter_agent_communication(config: Dict[str, Any], logger: logging.Logger)`
  - *Retorna instância global do sistema de comunicação inter-agente*

### Arquivo: `src/hephaestus/services/validation/pytest_validator.py`
- **Classe:** `PytestValidator(ValidationStep)`
  - *Runs pytest as a validation step.*

### Arquivo: `src/hephaestus/services/validation/__init__.py`
- **Classe:** `BenchmarkValidator(ValidationStep)`
- **Classe:** `CheckFileExistenceValidator(ValidationStep)`
- **Classe:** `ValidateJsonSyntax(ValidationStep)`
  - *Validates the syntax of JSON files mentioned in patches.*
- **Função:** `get_validation_step(name: str)`

### Arquivo: `src/hephaestus/services/validation/base.py`
- **Classe:** `ValidationStep(ABC)`
  - *Abstract base class for a validation step.*

### Arquivo: `src/hephaestus/services/validation/patch_applicator.py`
- **Classe:** `PatchApplicatorStep(ValidationStep)`
  - *Applies patches to the specified base path.*

### Arquivo: `src/hephaestus/services/validation/syntax_validator.py`
- **Função:** `validate_config_structure(config: dict, logger: logging.Logger)`
  - *Valida a estrutura do hephaestus_config.json contra um esquema definido.*
- **Classe:** `SyntaxValidator(ValidationStep)`
  - *Validates the syntax of Python and JSON files.*

### Arquivo: `src/hephaestus/services/validation/pytest_new_file_validator.py`
- **Classe:** `PytestNewFileValidator(ValidationStep)`
  - *A validation step that runs pytest specifically on newly created test files.*

### Arquivo: `src/hephaestus/services/monitoring/performance.py`
- **Classe:** `PerformanceMonitor`
  - *Monitor de performance em tempo real*
- **Classe:** `PerformanceOptimizer`
  - *Otimizador automático de performance*

### Arquivo: `src/hephaestus/services/optimization/optimized_api_startup.py`
- **Classe:** `OptimizedAgentInitializer`
  - *Inicializador otimizado para agentes do sistema.*
- **Função:** `optimized_lifespan(app: FastAPI)`
  - *Versão otimizada do lifespan para FastAPI.*
- **Função:** `start_background_threads(logger: logging.Logger)`
  - *Inicia threads de background de forma otimizada.*
- **Função:** `apply_optimization_to_main_api()`
  - *Instruções para aplicar a otimização na API principal.*

### Arquivo: `src/hephaestus/services/optimization/initialization_optimization.py`
- **Classe:** `ParallelAgentInitializer`
  - *Inicializador paralelo para agentes do sistema.*
- **Função:** `optimize_lifespan_startup(config: Dict[str, Any], logger: logging.Logger)`
  - *Função otimizada para substituir a inicialização sequencial no lifespan.*
- **Função:** `test_parallel_initialization()`
  - *Testa a inicialização paralela.*

### Arquivo: `src/hephaestus/services/orchestration/async_orchestrator.py`
- **Classe:** `AgentType(Enum)`
- **Classe:** `AgentTask`
  - *Representa uma tarefa para um agente específico*
- **Classe:** `AgentResult`
  - *Resultado de uma tarefa de agente*
- **Classe:** `AsyncAgentOrchestrator`
  - *Orquestrador assíncrono para múltiplos agentes*

### Arquivo: `src/hephaestus/financial/trading_engine.py`
- **Classe:** `Trade`
  - *Representa uma operação de trade.*
- **Classe:** `ArbitrageExecution`
  - *Representa uma execução completa de arbitragem.*
- **Classe:** `ExchangeAPI`
  - *Base class for exchange API implementations.*
- **Classe:** `BinanceAPI(ExchangeAPI)`
  - *Binance API implementation for trading.*
- **Classe:** `CoinbaseAPI(ExchangeAPI)`
  - *Coinbase Pro API implementation for trading.*
- **Classe:** `TradingEngine`
  - *Main trading engine for executing arbitrage opportunities.*
- **Classe:** `MockExchangeAPI(ExchangeAPI)`
  - *Mock exchange API for testing.*
- **Função:** `demo_trading_engine()`
  - *Demonstrate trading engine functionality.*

### Arquivo: `src/hephaestus/financial/opportunity_detector.py`
- **Classe:** `FinancialOpportunity`
  - *Generic financial opportunity structure.*
- **Classe:** `OpportunityDetector`
  - *Main financial opportunity detection engine.*
- **Função:** `main()`
  - *Test the opportunity detector.*

### Arquivo: `src/hephaestus/financial/__init__.py`

### Arquivo: `src/hephaestus/financial/crypto_arbitrage.py`
- **Classe:** `ArbitrageOpportunity`
  - *Structured arbitrage opportunity data.*
- **Classe:** `CryptoArbitrageDetector`
  - *Advanced cryptocurrency arbitrage detection with AI-powered optimization.*
- **Função:** `main()`
  - *Test the arbitrage detector.*

### Arquivo: `src/hephaestus/financial/risk_manager.py`
- **Classe:** `RiskLimits`
  - *Definição de limites de risco.*
- **Classe:** `RiskEvent`
  - *Evento de risco detectado.*
- **Classe:** `PortfolioManager`
  - *Gerenciador de portfólio e posições.*
- **Classe:** `RiskManager`
  - *Sistema avançado de gerenciamento de risco.*
- **Função:** `demo_risk_manager()`
  - *Demonstração do sistema de risk management.*

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO

