# MANIFESTO DO PROJETO HEPHAESTUS

## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)
agente_autonomo/
    README.md
    hephaestus.log
    AGENTS.md
    HEPHAESTUS_MEMORY.json
    main.py
    hephaestus_config.json
    requirements.txt
    MANIFESTO.md
    ISSUES.md
    agent/
        brain.py
        __init__.py
        code_validator.py
        agents.py
        patch_applicator.py
        memory.py
        tool_executor.py
        project_scanner.py
        state.py
    tests/
        test_agents.py
        test_project_scanner.py
        __init__.py
        test_hephaestus.py
        test_code_validator.py
        conftest.py
        test_brain.py
        test_memory.py
        test_patch_applicator.py

## 2. RESUMO DAS INTERFACES (APIs Internas)

### Arquivo: `main.py`
- **Classe:** `HephaestusAgent`
  - *Classe principal que encapsula a lógica do agente autônomo.*

### Arquivo: `agent/brain.py`
- **Função:** `_call_llm_api(api_key: str, model: str, prompt: str, temperature: float, base_url: str, logger: Any)`
  - *Função auxiliar para fazer chamadas à API LLM.*
- **Função:** `generate_next_objective(api_key: str, model: str, current_manifest: str, logger: Any, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None)`
  - *Gera o próximo objetivo evolutivo usando um modelo leve.*
- **Função:** `generate_capacitation_objective(api_key: str, model: str, engineer_analysis: str, base_url: str='https://openrouter.ai/api/v1', memory_summary: Optional[str]=None, logger: Optional[Any]=None)`
  - *Gera um objetivo para criar novas capacidades necessárias.*
- **Função:** `generate_commit_message(api_key: str, model: str, analysis_summary: str, objective: str, logger: Any, base_url: str='https://openrouter.ai/api/v1')`
  - *Gera uma mensagem de commit concisa e informativa usando um LLM.*

### Arquivo: `agent/__init__.py`

### Arquivo: `agent/code_validator.py`
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger)`
  - *Valida se o código Python em um arquivo é sintaticamente correto usando py_compile.*
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
- **Função:** `update_project_manifest(root_dir: str, target_files: List[str], output_path: str='AGENTS.md')`

### Arquivo: `agent/state.py`
- **Classe:** `AgentState`
  - *Representa o estado interno do agente Hephaestus durante um ciclo de processamento.*

### Arquivo: `tests/test_agents.py`
- **Função:** `mock_logger()`
- **Função:** `test_agents_call_llm_api_success(mock_post, mock_logger)`
- **Função:** `test_agents_call_llm_api_request_exception(mock_post, mock_logger)`
- **Função:** `test_agents_parse_json_response_valid_json(mock_logger)`
- **Função:** `test_agents_parse_json_response_with_markdown_block(mock_logger)`
- **Função:** `test_agents_parse_json_response_invalid_json(mock_logger)`
- **Função:** `test_architect_plan_action_success(mock_call_llm, mock_logger)`
- **Função:** `test_architect_plan_action_llm_error(mock_call_llm, mock_logger)`
- **Função:** `test_architect_plan_action_empty_llm_response(mock_call_llm, mock_logger)`
- **Função:** `test_architect_plan_action_malformed_json(mock_call_llm, mock_logger)`
- **Função:** `test_architect_plan_action_json_missing_patches_key(mock_call_llm, mock_logger)`
- **Função:** `test_architect_plan_action_invalid_patch_structure(mock_call_llm, mock_logger)`
- **Função:** `test_maestro_choose_strategy_success(mock_call_llm, mock_logger)`
- **Função:** `test_maestro_choose_strategy_api_error_then_success(mock_call_llm, mock_logger)`
- **Função:** `test_maestro_choose_strategy_parsing_error(mock_call_llm, mock_logger)`
- **Função:** `test_maestro_choose_strategy_json_schema_invalid(mock_call_llm, mock_logger)`
- **Função:** `test_maestro_choose_strategy_capacitation_required(mock_call_llm, mock_logger)`
- **Função:** `test_maestro_choose_strategy_with_memory_summary(mock_call_llm, mock_logger)`

### Arquivo: `tests/test_project_scanner.py`
- **Função:** `test_extract_elements_simple_code()`
- **Função:** `test_extract_elements_empty_code()`
- **Função:** `test_extract_elements_invalid_syntax()`
- **Função:** `test_extract_elements_with_various_constructs()`
- **Função:** `sample_project_structure(tmp_path: Path)`
- **Função:** `test_update_project_manifest_happy_path(sample_project_structure: Path, tmp极_path: Path)`
- **Função:** `test_update_project_manifest_target_file_not_found(sample_project_structure: Path, tmp_path: Path)`
- **Função:** `test_update_project_manifest_empty_project(tmp_path: Path)`
- **Função:** `test_update_project_manifest_skip_dirs(tmp_path: Path)`
- **Função:** `test_project_scanner_file_read_error_in_target_file(tmp_path: Path, mocker)`
- **Função:** `test_project_scanner_file_read_error_in_api_summary(tmp_path: Path, mocker)`

### Arquivo: `tests/__init__.py`

### Arquivo: `tests/test_hephaestus.py`
- **Função:** `test_dummy()`

### Arquivo: `tests/test_code_validator.py`
- **Função:** `test_validate_python_code_valid(tmp_path: Path)`
- **Função:** `test_validate_python_code_invalid_syntax(tmp_path: Path)`
- **Função:** `test_validate_python_code_file_not_found(tmp_path: Path)`
- **Função:** `test_validate_python_code_empty_file(tmp_path: Path)`
- **Função:** `test_validate_json_syntax_valid(tmp_path: Path)`
- **Função:** `test_validate_json_syntax_invalid_syntax(tmp_path: Path)`
- **Função:** `test_validate_json_syntax_file_not_found(tmp_path: Path)`
- **Função:** `test_validate_json_syntax_empty_file(tmp_path: Path)`
- **Função:** `test_validate_json_syntax_not_json_content(tmp_path: Path)`
- **Função:** `test_validate_json_syntax_valid_but_complex(tmp_path: Path)`

### Arquivo: `tests/conftest.py`

### Arquivo: `tests/test_brain.py`
- **Função:** `mock_logger()`
- **Função:** `test_brain_call_llm_api_success(mock_post, mock_logger)`
- **Função:** `test_brain_call_llm_api_request_exception(mock_post, mock_logger)`
- **Função:** `test_generate_next_objective_success(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_next_objective_api_error(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_next_objective_empty_llm_response(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_next_objective_empty_manifest(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_next_objective_with_memory(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_capacitation_objective_success(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_capacitation_objective_api_error(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_capacitation_objective_with_memory(mock_call_llm_api, mock_logger)`
- **Função:** `test_generate_commit_message_feat(mock_logger)`
- **Função:** `test_generate_commit_message_fix(mock_logger)`
- **Função:** `test_generate_commit_message_long_objective_truncates(mock_logger)`

### Arquivo: `tests/test_memory.py`
- **Função:** `temp_memory_file(tmp_path)`
  - *Fixture to create a temporary memory file path.*
- **Função:** `test_memory_initialization(temp_memory_file)`
  - *Test that Memory initializes correctly with a filepath.*
- **Função:** `test_save_and_load_empty_memory(temp_memory_file)`
  - *Test saving and loading an empty memory.*
- **Função:** `test_add_completed_objective(temp_memory_file)`
  - *Test adding and saving/loading a completed objective.*
- **Função:** `test_add_failed_objective(temp_memory_file)`
  - *Test adding and saving/loading a failed objective.*
- **Função:** `test_add_capability(temp_memory_file)`
  - *Test adding and saving/loading an acquired capability.*
- **Função:** `test_load_non_existent_file(tmp_path)`
  - *Test loading from a non-existent file path, should start fresh.*
- **Função:** `test_load_corrupted_json_file(temp_memory_file)`
  - *Test loading from a corrupted JSON file, should start fresh and print warning.*
- **Função:** `test_file_persistence_across_instances(temp_memory_file)`
  - *Test that data saved by one instance is loaded by another.*
- **Função:** `test_get_history_summary_format_and_content(temp_memory_file)`
  - *Test the format and content of get_history_summary.*
- **Função:** `test_get_history_summary_max_items(temp_memory_file)`
  - *Test that max_items_per_category limits the output correctly.*

### Arquivo: `tests/test_patch_applicator.py`
- **Função:** `test_files_dir(tmp_path: Path)`
  - *Cria um diretório base para os arquivos de teste dentro de tmp_path.*
- **Função:** `check_file_content(file_path: Path, expected_lines: list[str])`
- **Função:** `test_insert_into_existing_file_start(test_files_dir: Path)`
- **Função:** `test_insert_into_existing_file_middle(test_files_dir: Path)`
- **Função:** `test_insert_into_existing_file_end_with_line_number(test_files_dir: Path)`
- **Função:** `test_insert_into_existing_file_end_no_line_number(test_files_dir: Path)`
- **Função:** `test_insert_creates_new_file(test_files_dir: Path)`
- **Função:** `test_insert_into_empty_file(test_files_dir: Path)`
- **Função:** `test_insert_invalid_line_number_string(test_files_dir: Path, caplog)`
- **Função:** `test_replace_block_literal_in_existing_file(test_files_dir: Path)`
- **Função:** `test_replace_block_regex_in_existing_file(test_files_dir: Path)`
- **Função:** `test_replace_block_regex_implicit(test_files_dir: Path)`
- **Função:** `test_replace_entire_file_content(test_files_dir: Path)`
- **Função:** `test_replace_creates_new_file_if_block_is_null(test_files_dir: Path)`
- **Função:** `test_replace_block_not_found_literal(test_files_dir: Path, caplog)`
- **Função:** `test_replace_block_not_found_regex(test_files_dir: Path, caplog)`
- **Função:** `test_replace_specific_block_in_non_existent_file_fails(test_files_dir: Path, caplog)`
- **Função:** `test_delete_block_literal_in_existing_file(test_files_dir: Path)`
- **Função:** `test_delete_block_regex_in_existing_file(test_files_dir: Path)`
- **Função:** `test_delete_entire_file_with_block_to_delete_none(test_files_dir: Path)`
- **Função:** `test_delete_block_not_found_literal(test_files_dir: Path, caplog)`
- **Função:** `test_delete_block_in_non_existent_file(test_files_dir: Path, caplog)`
- **Função:** `test_apply_patches_invalid_operation(test_files_dir: Path, caplog)`
- **Função:** `test_apply_patches_missing_filepath(test_files_dir: Path, caplog)`
- **Função:** `test_apply_patches_base_path_resolution(tmp_path: Path)`
- **Função:** `test_apply_patches_filepath_is_normalized(tmp_path: Path)`
- **Função:** `test_replace_regex_with_special_chars_in_content(test_files_dir: Path)`
- **Função:** `test_delete_block_literal_multiline(test_files_dir: Path)`

## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO
