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

                if rel_path_str in target_files_set:
                    try:
                        with open(file_path_obj, 'r', encoding='utf-8') as f_obj:
                            content = f_obj.read()
                        target_content_cache[rel_path_str] = (content, None)
                    except Exception as e:
                        target_content_cache[rel_path_str] = (None, e)

                elif f_name.endswith('.py'): # Processar para resumo de API mesmo se não for alvo
                    try:
                        with open(file_path_obj, 'r', encoding='utf-8') as f_obj:
                            content = f_obj.read()
                        api_summary_cache[rel_path_str] = _extract_elements(content)
                    except Exception as e:
                        api_summary_cache[rel_path_str] = [('error', None, None, f"Erro na leitura do arquivo: {str(e)}")]
        
        manifest.write("\n## 2. RESUMO DAS INTERFACES (APIs Internas)\n")
        
        for rel_path_str, elements in api_summary_cache.items():
            manifest.write(f"\n### Módulo: `{rel_path_str}`\n")
            
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
