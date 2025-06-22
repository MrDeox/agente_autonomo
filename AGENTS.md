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
        __init__.py
        test_hephaestus.py

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

### Módulo: `tests/__init__.py`

### Módulo: `tests/test_hephaestus.py`
- **Função:** `test_dummy()`

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
            
            elif isinstance(node, ast.FunctionDef):
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
    
    # Caches otimizados
    target_content_cache: Dict[str, Tuple[Optional[str], Optional[Exception]]] = {}
    api_summary_cache: Dict[str, List[Tuple]] = {}
    
    with open(output_path, 'w', encoding='utf-8') as manifest:
        manifest.write("# MANIFESTO DO PROJETO HEPHAESTUS\n\n")
        
        ##### SEÇÃO 1: ESTRUTURA DE ARQUIVOS #####
        manifest.write("## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)\n")
        
        for root, dirs, files in os.walk(root_path, topdown=True):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
            if not dirs and not files:
                continue
                
            level = pathlib.Path(root).relative_to(root_path).parts
            indent = ' ' * 4 * len(level)
            manifest.write(f"{indent}{os.path.basename(root)}/\n")
            
            sub_indent = ' ' * 4 * (len(level) + 1)
            
            for f in files:
                if not f.startswith('.'):
                    manifest.write(f"{sub_indent}{f}\n")
                    
                    file_path = pathlib.Path(root) / f
                    rel_path = file_path.relative_to(root_path)
                    rel_path_str = str(rel_path)
                    
                    # Processa arquivos durante a travessia
                    if rel_path_str in target_files_set:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f_obj:
                                content = f_obj.read()
                            target_content_cache[rel_path_str] = (content, None)
                        except Exception as e:
                            target_content_cache[rel_path_str] = (None, e)
                    
                    elif f.endswith('.py'):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f_obj:
                                content = f_obj.read()
                            api_summary_cache[rel_path_str] = _extract_elements(content)
                        except Exception as e:
                            api_summary_cache[rel_path_str] = [('error', None, None, f"Erro na leitura do arquivo: {str(e)}")]
        
        ##### SEÇÃO 2: RESUMO DAS INTERFACES #####
        manifest.write("\n## 2. RESUMO DAS INTERFACES (APIs Internas)\n")
        
        for rel_path, elements in api_summary_cache.items():
            manifest.write(f"\n### Módulo: `{rel_path}`\n")
            
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
        
        ##### SEÇÃO 3: CONTEÚDO DOS ARQUIVOS ALVO #####
        manifest.write("\n## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO\n")
        
        for rel_path in target_files:
            manifest.write(f"\n### Arquivo: `{rel_path}`\n\n```\n")
            
            if rel_path in target_content_cache:
                content, error = target_content_cache[rel_path]
                if error:
                    manifest.write(f"# ERRO: {str(error)}\n")
                elif content is None:
                    manifest.write("# ERRO: Conteúdo não disponível\n")
                else:
                    manifest.write(content + "\n")
            else:
                manifest.write("# ARQUIVO NÃO ENCONTRADO\n")
            
            manifest.write("```\n")

```
