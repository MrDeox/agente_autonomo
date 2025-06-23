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
        test_main_flow.py
        test_project_scanner.py
        __init__.py
        test_hephaestus.py
        test_code_validator.py
        conftest.py
        test_brain.py
        test_patch_applicator.py

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

### Módulo: `tests/test_main_flow.py`
- **Função:** `test_agent_logger()`
- **Função:** `temp_project_dir(tmp_path: Path)`
  - *Cria um diretório de projeto temporário para o agente operar.*
- **Função:** `hephaestus_agent(temp_project_dir: Path, test_agent_logger: logging.Logger, mocker)`
  - *Inicializa o HephaestusAgent para testes, operando no temp_project_dir.*
- **Função:** `test_main_flow_apply_and_validate_syntax_success(mock_check_file_existence, mock_run_pytest, mock_gen_next_obj, mock_maestro, mock_architect, hephaestus_agent: HephaestusAgent, temp_project_dir: Path, test_agent_logger: logging.Logger)`
- **Função:** `test_main_flow_capacitation_required(mock_gen_cap_obj, mock_maestro, mock_architect, hephaestus_agent: HephaestusAgent, temp_project_dir: Path)`
- **Função:** `test_main_flow_pytest_failure_triggers_correction_objective(mock_run_pytest, mock_maestro, mock_architect, hephaestus_agent: HephaestusAgent, temp_project_dir: Path)`

### Módulo: `tests/test_project_scanner.py`
- **Função:** `test_extract_elements_simple_code()`
- **Função:** `test_extract_elements_empty_code()`
- **Função:** `test_extract_elements_invalid_syntax()`
- **Função:** `test_extract_elements_with_various_constructs()`
- **Função:** `sample_project_structure(tmp_path: Path)`
- **Função:** `test_update_project_manifest_happy_path(sample_project_structure: Path, tmp_path: Path)`
- **Função:** `test_update_project_manifest_target_file_not_found(sample_project_structure: Path, tmp_path: Path)`
- **Função:** `test_update_project_manifest_empty_project(tmp_path: Path)`
- **Função:** `test_update_project_manifest_skip_dirs(tmp_path: Path)`
- **Função:** `test_project_scanner_file_read_error_in_target_file(tmp_path: Path, mocker)`
- **Função:** `test_project_scanner_file_read_error_in_api_summary(tmp_path: Path, mocker)`

### Módulo: `tests/__init__.py`

### Módulo: `tests/test_hephaestus.py`
- **Função:** `test_dummy()`

### Módulo: `tests/test_code_validator.py`
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

### Módulo: `tests/conftest.py`

### Módulo: `tests/test_brain.py`
- **Função:** `mock_logger()`
- **Função:** `test_call_llm_api_success(mock_post, mock_logger)`
- **Função:** `test_call_llm_api_request_exception(mock_post, mock_logger)`
- **Função:** `test_call_llm_api_http_error(mock_post, mock_logger)`
- **Função:** `test_call_llm_api_missing_choices_key(mock_post, mock_logger)`
- **Função:** `test_call_llm_api_key_error_in_response_structure(mock_post, mock_logger)`
- **Função:** `test_get_action_plan_success(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_llm_error(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_empty_llm_response(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_malformed_json(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_json_missing_patches_key(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_patches_not_a_list(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_invalid_patch_structure_missing_keys(mock_call_llm, mock_logger)`
- **Função:** `test_get_action_plan_cleans_json_code_block(mock_call_llm, mock_logger)`
- **Função:** `test_generate_next_objective_success(mock_call_llm, mock_logger)`
- **Função:** `test_generate_next_objective_api_error(mock_post_direct, mock_logger)`
- **Função:** `test_generate_next_objective_empty_manifest(mock_post_direct, mock_logger)`
- **Função:** `test_generate_capacitation_objective_success(mock_post_direct, mock_logger)`
- **Função:** `test_get_maestro_decision_success(mock_post_direct, mock_logger)`
- **Função:** `test_get_maestro_decision_capacitation_required(mock_post_direct, mock_logger)`
- **Função:** `test_get_maestro_decision_invalid_json_response(mock_post_direct, mock_logger)`
- **Função:** `test_get_maestro_decision_json_missing_strategy_key(mock_post_direct, mock_logger)`
- **Função:** `test_get_maestro_decision_cleans_code_block(mock_post_direct, mock_logger)`
- **Função:** `test_get_maestro_decision_uses_multiple_models_on_failure(mock_post_direct, mock_logger)`

### Módulo: `tests/test_patch_applicator.py`
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
