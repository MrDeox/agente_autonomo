import os
import fnmatch
import pathlib
import ast
from typing import List, Optional, Tuple

def _extract_elements(code_string: str) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
    """
    Extrai elementos estruturais do código (imports, classes, funções).
    
    Args:
        code_string: Código fonte como string
        
    Returns:
        Lista de tuplas (tipo, nome, detalhes, docstring)
    """
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
    """
    Gera esqueleto do código com definições principais e docstrings.
    
    Args:
        code_string: Código fonte como string
        
    Returns:
        String com estrutura simplificada do código
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

def update_project_manifest(root_dir: str, target_files: List[str], output_path: str = "AGENTS.md") -> None:
    """
    Gera manifesto do projeto em Markdown otimizado com estrutura, interfaces e código alvo.
    
    Args:
        root_dir: Diretório raiz do projeto
        target_files: Lista de arquivos para inclusão integral
        output_path: Caminho de saída do manifesto
    """
    root_path = pathlib.Path(root_dir).resolve()
    skip_dirs = {'venv', '__pycache__', '.git', 'node_modules'}
    
    with open(output_path, 'w', encoding='utf-8') as manifest:
        manifest.write("# MANIFESTO DO PROJETO HEPHAESTUS\n\n")
        
        # Seção 1: Estrutura de Arquivos
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
        
        # Seção 2: Resumo de Interfaces
        manifest.write("\n## 2. RESUMO DAS INTERFACES (APIs Internas)\n")
        for root, dirs, files in os.walk(root_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = pathlib.Path(root) / file
                    rel_path = file_path.relative_to(root_path)
                    
                    if str(rel_path) in target_files:
                        continue
                    
                    manifest.write(f"\n### Módulo: `{rel_path}`\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        elements = _extract_elements(content)
                        
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
                    except Exception as e:
                        manifest.write(f"  - [ERRO] {str(e)}\n")
        
        # Seção 3: Código-fonte completo
        manifest.write("\n## 3. FOCO DA TAREFA (CÓDIGO-FONTE COMPLETO)\n")
        MAX_FILE_SIZE = 10000  # 10KB por arquivo
        
        for target in target_files:
            target_path = root_path / target
            if not target_path.exists():
                manifest.write(f"\n# Arquivo não encontrado: {target}\n")
                continue
            
            manifest.write(f"\n--- INÍCIO DO CÓDIGO-FONTE: {target} ---\n")
            manifest.write("```python\n")
            try:
                with open(target_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > MAX_FILE_SIZE:
                        content = content[:MAX_FILE_SIZE] + "\n# ... [conteúdo truncado por tamanho excessivo]"
                    manifest.write(content)
            except Exception as e:
                manifest.write(f"# Erro ao ler arquivo: {str(e)}\n")
            manifest.write("\n```\n")
            manifest.write(f"--- FIM DO CÓDIGO-FONTE: {target} ---\n")
