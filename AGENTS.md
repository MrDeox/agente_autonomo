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
    ISSUES.md
    agent/
        brain.py
        __init__.py
        code_validator.py
        deep_validator.py
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
        test_deep_validator.py
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
- **Função:** `perform_deep_validation(file_path: Path, logger: logging.Logger) -> dict | None`
  - *Realiza uma análise profunda da qualidade do código Python usando o módulo `deep_validator`.*
- **Função:** `validate_python_code(file_path: str | Path, logger: logging.Logger, perform_deep_analysis: bool = True) -> tuple[bool, str | None, dict | None]`
  - *Valida a sintaxe do código Python e opcionalmente realiza uma análise profunda de qualidade.*
- **Função:** `validate_json_syntax(file_path: str | Path, logger: logging.Logger)`
  - *Valida se um arquivo contém JSON válido.*

### Arquivo: `agent/deep_validator.py`
- **Função:** `analyze_complexity(code_string: str) -> dict`
  - *Analisa a complexidade ciclomática e outras métricas do código Python fornecido.*
- **Função:** `detect_code_duplication(code_string: str, min_lines: int = 4, strip_comments_and_blanks: bool = True) -> list[dict]`
  - *Detecta blocos de código duplicados no código Python fornecido.*
- **Função:** `calculate_quality_score(complexity_report: dict, duplication_report: list) -> float`
  - *Calcula um score de qualidade do código com base nos relatórios de complexidade e duplicação.*

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

### Arquivo: `tests/test_deep_validator.py`
- **Função:** `simple_code()`
  - *Fixture com código Python simples.*
- **Função:** `complex_code()`
  - *Fixture com código Python de alta complexidade ciclomática.*
- **Função:** `duplicated_code()`
  - *Fixture com blocos de código duplicados.*
- **Função:** `code_with_no_comments()`
  - *Fixture com código Python sem comentários.*
- **Função:** `very_large_code()`
  - *Fixture que gera uma string de código Python muito longa (simulando um arquivo grande).*
- **Função:** `test_analyze_complexity_simple(simple_code)`
  - *Testa a análise de complexidade em código simples.*
- **Função:** `test_analyze_complexity_complex(complex_code)`
  - *Testa a análise de complexidade em código complexo.*
- **Função:** `test_analyze_complexity_empty_string()`
  - *Testa a análise de complexidade com string vazia.*
- **Função:** `test_analyze_complexity_syntax_error()`
  - *Testa a análise de complexidade com erro de sintaxe.*
- **Função:** `test_detect_duplication_present(duplicated_code)`
  - *Testa a detecção de duplicação quando há código duplicado.*
- **Função:** `test_detect_duplication_none(simple_code)`
  - *Testa a detecção de duplicação quando não há código duplicado.*
- **Função:** `test_detect_duplication_min_lines_too_high(duplicated_code)`
  - *Testa a detecção de duplicação com `min_lines` alto demais.*
- **Função:** `test_detect_duplication_empty_string()`
  - *Testa a detecção de duplicação com string vazia.*
- **Função:** `test_detect_duplication_strip_comments(duplicated_code)`
  - *Testa se a detecção de duplicação ignora comentários.*
- **Função:** `test_calculate_quality_score_perfect()`
  - *Testa o cálculo do score de qualidade para código "perfeito".*
- **Função:** `test_calculate_quality_score_high_complexity(complex_code)`
  - *Testa o cálculo do score de qualidade para código com alta complexidade.*
- **Função:** `test_calculate_quality_score_with_duplication(duplicated_code)`
  - *Testa o cálculo do score de qualidade para código com duplicação.*
- **Função:** `test_calculate_quality_score_very_large_code()`
  - *Testa o cálculo do score de qualidade para código simulado muito grande.*
- **Função:** `test_calculate_quality_score_no_comments(code_with_no_comments)`
  - *Testa o cálculo do score de qualidade para código sem comentários.*
- **Função:** `test_calculate_quality_score_all_penalties()`
  - *Testa o cálculo do score de qualidade com todas as penalidades aplicadas.*
- **Função:** `test_score_never_below_zero()`
  - *Testa se o score de qualidade nunca fica abaixo de zero.*
- **Função:** `test_handle_error_in_complexity_report()`
  - *Testa como o score de qualidade lida com um relatório de complexidade com erro.*

### Arquivo: `tests/conftest.py`

### Arquivo: `tests/test_brain.py`
- **Função:** `mock_logger()`
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

### Arquivo: `agent/project_scanner.py`

```
import os
import fnmatch
import pathlib
import ast
from typing import List, Optional, Tuple, Dict, Set

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

def update_project_manifest(root_dir: str, target_files: List[str], output_path: str = "AGENTS.md") -> None:
    root_path = pathlib.Path(root_dir).resolve()
    skip_dirs = {'venv', '__pycache__', '.git', 'node_modules'}
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
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]

            # Escrever o nome do diretório atual (root)
            # A menos que o próprio root seja um diretório skip_dirs (o que não deve acontecer se root_path for o início)
            # ou se o root for o próprio root_path E não tiver conteúdo (dirs filtrados e files)
            if current_path_obj == root_path and not dirs and not files:
                 # Caso especial: root_dir é completamente vazio ou só contém skip_dirs
                 # Ainda assim, queremos listar o próprio root_dir
                 pass # Não pular a escrita do root_dir em si

            # Calcular indentação e escrever o nome do diretório atual
            if current_path_obj == root_path:
                level_parts = []
            else:
                try:
                    level_parts = current_path_obj.relative_to(root_path).parts
                except ValueError: # current_path_obj não é subdiretório de root_path (não deveria acontecer com os.walk)
                    level_parts = current_path_obj.parts # Fallback, mas improvável

            indent = ' ' * 4 * len(level_parts)
            manifest.write(f"{indent}{os.path.basename(root)}/\n")
            
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

```
