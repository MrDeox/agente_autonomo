import os
import fnmatch
import pathlib
import ast
from typing import List, Optional, Tuple, Dict, Set, Any

def _extract_elements(code_string: str) -> List[Tuple[str, str, Optional[str], Optional[str]]]:
    """Extract code elements (imports, classes, functions) from Python source.
    
    Args:
        code_string: Python source code to analyze
        
    Returns:
        List of tuples with (element_type, name, details, docstring)
        where element_type is 'import', 'class', 'function', or 'error'
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
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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

def _get_default_skip_dirs() -> Set[str]:
    """Get default directories to skip during project scanning.
    
    Returns:
        Set of directory names to skip by default
    """
    return {'venv', '__pycache__', '.git', 'node_modules', 'tests', 'test', 
            '.pytest_cache', 'dist', 'build', 'docs', 'examples', 'scripts'}

def _should_skip_directory(dir_name: str, excluded_dirs: Set[str]) -> bool:
    """Determine if a directory should be skipped during scanning.
    
    Args:
        dir_name: Name of directory to check
        excluded_dirs: Set of directory patterns to exclude
        
    Returns:
        True if directory should be skipped, False otherwise
    """
    return (dir_name.startswith('.') or 
            dir_name in excluded_dirs or 
            any(fnmatch.fnmatch(dir_name, pattern) for pattern in excluded_dirs))

def _process_file_for_manifest(
    file_path_obj: pathlib.Path, 
    root_path: pathlib.Path, 
    target_files_set: Set[str],
    target_content_cache: Dict[str, Tuple[Optional[str], Optional[Exception]]],
    api_summary_cache: Dict[str, List[Tuple]]
) -> None:
    """Process a file for manifest generation.
    
    Args:
        file_path_obj: Path object to the file
        root_path: Root path of the project
        target_files_set: Set of target file paths
        target_content_cache: Cache for target file contents
        api_summary_cache: Cache for API summaries
    """
    rel_path_str = str(file_path_obj.relative_to(root_path))
    
    # Process target files for full content
    if rel_path_str in target_files_set:
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f_obj:
                content = f_obj.read()
            target_content_cache[rel_path_str] = (content, None)
        except Exception as e:
            target_content_cache[rel_path_str] = (None, e)
    
    # Process all Python files for API summary
    if file_path_obj.suffix == '.py':
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

def _write_manifest_section(
    manifest_file, 
    section_title: str, 
    content: str, 
    indent_level: int = 0
) -> None:
    """Write a section to the manifest file.
    
    Args:
        manifest_file: Open manifest file object
        section_title: Title of the section
        content: Content to write
        indent_level: Indentation level (default 0)
    """
    indent = ' ' * 4 * indent_level
    manifest_file.write(f"{indent}{section_title}\n{content}\n")

def update_project_manifest(
    root_dir: str,
    target_files: List[str],
    output_path: str = "docs/ARCHITECTURE.md",
    excluded_dir_patterns: Optional[List[str]] = None
) -> None:
    """Generate a project manifest documenting the code structure and APIs.
    
    Args:
        root_dir: Root directory to scan
        target_files: List of files to include full content for
        output_path: Output file path for the manifest
        excluded_dir_patterns: Patterns of directories to exclude
    """
    root_path = pathlib.Path(root_dir).resolve()
    default_skip_dirs = _get_default_skip_dirs()
    
    if excluded_dir_patterns:
        current_excluded_dirs = default_skip_dirs.union(set(excluded_dir_patterns))
    else:
        current_excluded_dirs = default_skip_dirs

    target_files_set = set(target_files)
    target_content_cache: Dict[str, Tuple[Optional[str], Optional[Exception]]] = {}
    api_summary_cache: Dict[str, List[Tuple]] = {}
    
    with open(output_path, 'w', encoding='utf-8') as manifest:
        manifest.write("# MANIFESTO DO PROJETO HEPHAESTUS\n\n")
        
        # File structure section
        _write_manifest_section(manifest, "## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)", "")
        
        for root, dirs, files in os.walk(root_path, topdown=True):
            current_path_obj = pathlib.Path(root)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not _should_skip_directory(d, current_excluded_dirs)]
            
            # Skip root if it matches exclusion patterns (except the starting root_dir)
            if current_path_obj != root_path and _should_skip_directory(current_path_obj.name, current_excluded_dirs):
                continue
                
            # Write directory entry
            if current_path_obj == root_path:
                level_parts = []
            else:
                try:
                    level_parts = current_path_obj.relative_to(root_path).parts
                except ValueError:
                    level_parts = current_path_obj.parts

            indent = ' ' * 4 * len(level_parts)
            manifest.write(f"{indent}{current_path_obj.name}/\n")
            
            # Process files in directory
            sub_indent = ' ' * 4 * (len(level_parts) + 1)
            
            for f_name in files:
                if f_name.startswith('.'):
                    continue
                
                # Skip test files
                if f_name.endswith('.py') and (f_name.startswith('test_') or f_name.endswith('_test.py')):
                    continue
                    
                manifest.write(f"{sub_indent}{f_name}\n")
                
                file_path_obj = current_path_obj / f_name
                _process_file_for_manifest(file_path_obj, root_path, target_files_set, 
                                         target_content_cache, api_summary_cache)
        
        # API summary section
        _write_manifest_section(manifest, "\n## 2. RESUMO DAS INTERFACES (APIs Internas)", "")
        
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
        
        # Full content section
        _write_manifest_section(manifest, "\n## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO", "")
        
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
                manifest.write("# ARQUIVO NÃO ENCONTRADO OU NÃO PROCESSADO\n")
            
            manifest.write("```\n")

def _collect_project_files(root_path: pathlib.Path, excluded_dirs: Set[str]) -> Tuple[List[str], Set[str]]:
    """Collect all Python files in the project, separating test files.
    
    Args:
        root_path: Root path of the project
        excluded_dirs: Set of directory patterns to exclude
        
    Returns:
        Tuple of (project_files, test_files)
    """
    project_files = []
    test_files = set()
    
    for root, dirs, files in os.walk(root_path, topdown=True):
        # Filter directories
        dirs[:] = [d for d in dirs if not _should_skip_directory(d, excluded_dirs)]
        
        current_path_obj = pathlib.Path(root)
        if current_path_obj != root_path and _should_skip_directory(current_path_obj.name, excluded_dirs):
            continue
            
        for file_name in files:
            if file_name.endswith('.py'):
                file_path_obj = current_path_obj / file_name
                relative_path_str = str(file_path_obj.relative_to(root_path))
                
                if file_name.startswith('test_') or file_name.endswith('_test.py'):
                    test_files.add(relative_path_str)
                else:
                    project_files.append(relative_path_str)
    
    return project_files, test_files

def _analyze_single_file(
    file_path_obj: pathlib.Path,
    root_path: pathlib.Path,
    file_loc_threshold: int,
    func_loc_threshold: int,
    func_cc_threshold: int,
    test_files: Set[str]
) -> Dict[str, Any]:
    """Analyze metrics for a single Python file.
    
    Args:
        file_path_obj: Path to the file to analyze
        root_path: Root path of the project
        file_loc_threshold: LOC threshold for large files
        func_loc_threshold: LOC threshold for large functions
        func_cc_threshold: CC threshold for complex functions
        test_files: Set of test file paths
        
    Returns:
        Dictionary with file metrics and analysis results
    """
    from radon.visitors import ComplexityVisitor
    from radon.raw import analyze as analyze_raw
    
    relative_path_str = str(file_path_obj.relative_to(root_path))
    
    try:
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            code_content = f.read()

        # Parse AST
        try:
            ast_tree = ast.parse(code_content, filename=str(file_path_obj))
        except SyntaxError:
            raw_analysis = analyze_raw(code_content)
            file_loc = raw_analysis.loc
            return {
                'file_loc': file_loc,
                'functions': [],
                'error': 'SyntaxError parsing file'
            }

        # File metrics
        raw_analysis = analyze_raw(code_content)
        file_loc = raw_analysis.loc
        
        # Function metrics
        visitor = ComplexityVisitor.from_ast(ast_tree)
        file_functions_metrics = []
        
        for node in ast_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_name = node.name
                func_loc = (node.end_lineno or node.lineno) - node.lineno + 1
                
                # Find complexity
                current_cc = 0
                for f_block in visitor.functions:
                    if f_block.name == func_name and f_block.lineno == node.lineno:
                        current_cc = f_block.complexity
                        break
                
                if current_cc == 0:
                    for class_block in visitor.classes:
                        for method_block in class_block.methods:
                            if method_block.name == func_name and method_block.lineno == node.lineno:
                                current_cc = method_block.complexity
                                break
                        if current_cc != 0:
                            break
                
                args_list = [ast.unparse(arg) for arg in node.args.args]
                args_str = ", ".join(args_list)
                
                file_functions_metrics.append({
                    'name': func_name,
                    'args': args_str,
                    'loc': func_loc,
                    'cc': current_cc,
                    'is_large': func_loc > func_loc_threshold,
                    'is_complex': current_cc > func_cc_threshold
                })
        
        return {
            'file_loc': file_loc,
            'functions': file_functions_metrics
        }
        
    except FileNotFoundError:
        return {'error': 'File not found during metrics analysis'}
    except Exception as e:
        return {'error': f'Error analyzing {relative_path_str}: {str(e)}'}

def _check_missing_tests(
    relative_path_str: str, 
    file_functions_metrics: List[Dict[str, Any]], 
    file_loc: int, 
    test_files: Set[str]
) -> bool:
    """Check if a module is missing corresponding test files.
    
    Args:
        relative_path_str: Path to the module file
        file_functions_metrics: Metrics for the module's functions
        file_loc: LOC of the module
        test_files: Set of test file paths
        
    Returns:
        True if tests are missing, False otherwise
    """
    path_parts = list(pathlib.Path(relative_path_str).parts)
    if len(path_parts) > 0:
        module_name = path_parts[-1][:-3]
        
        # Check possible test file locations
        test_paths = [
            str(pathlib.Path(*["tests"] + path_parts[:-1] + [f"test_{module_name}.py"])),
            str(pathlib.Path(*["tests"] + path_parts[:-1] + [f"{module_name}_test.py"])),
            str(pathlib.Path(*["tests"] + [f"test_{module_name}.py"])),
            str(pathlib.Path(*["tests"] + [f"{module_name}_test.py"]))
        ]
        
        if not any(test_path in test_files for test_path in test_paths):
            return file_functions_metrics or file_loc > 20
    
    return False

def analyze_code_metrics(
    root_dir: str,
    excluded_dir_patterns: Optional[List[str]] = None,
    file_loc_threshold: int = 300,
    func_loc_threshold: int = 50,
    func_cc_threshold: int = 10
) -> Dict[str, Any]:
    """Analyze Python files in a directory for code metrics like LOC and Cyclomatic Complexity.
    
    Args:
        root_dir: Root directory to scan
        excluded_dir_patterns: List of directory patterns to exclude
        file_loc_threshold: LOC threshold for large files
        func_loc_threshold: LOC threshold for large functions
        func_cc_threshold: CC threshold for complex functions
        
    Returns:
        Dictionary containing:
        - 'metrics': File path to metrics mapping
        - 'summary': Summary of large/complex items and missing tests
    """
    root_path = pathlib.Path(root_dir).resolve()
    default_skip_dirs = _get_default_skip_dirs()
    
    if excluded_dir_patterns:
        current_excluded_dirs = default_skip_dirs.union(set(excluded_dir_patterns))
    else:
        current_excluded_dirs = default_skip_dirs

    all_metrics: Dict[str, Dict[str, Any]] = {}
    large_files_summary: List[Tuple[str, int]] = []
    large_functions_summary: List[Tuple[str, str, int]] = []
    complex_functions_summary: List[Tuple[str, str, int]] = []
    missing_tests_summary: List[str] = []
    
    project_files, test_files = _collect_project_files(root_path, current_excluded_dirs)
    
    for relative_path_str in project_files:
        file_path_obj = root_path / relative_path_str
        file_metrics = _analyze_single_file(
            file_path_obj, root_path, 
            file_loc_threshold, func_loc_threshold, func_cc_threshold,
            test_files
        )
        
        all_metrics[relative_path_str] = file_metrics
        
        # Check for large files
        if 'file_loc' in file_metrics and file_metrics['file_loc'] > file_loc_threshold:
            large_files_summary.append((relative_path_str, file_metrics['file_loc']))
            
        # Check functions
        if 'functions' in file_metrics:
            for func_metrics in file_metrics['functions']:
                if func_metrics['is_large']:
                    large_functions_summary.append(
                        (relative_path_str, func_metrics['name'], func_metrics['loc'])
                    )
                if func_metrics['is_complex']:
                    complex_functions_summary.append(
                        (relative_path_str, func_metrics['name'], func_metrics['cc'])
                    )
            
            # Check for missing tests
            if _check_missing_tests(
                relative_path_str, 
                file_metrics['functions'], 
                file_metrics.get('file_loc', 0), 
                test_files
            ):
                missing_tests_summary.append(relative_path_str)
    
    return {
        "metrics": all_metrics,
        "summary": {
            "large_files": large_files_summary,
            "large_functions": large_functions_summary,
            "complex_functions": complex_functions_summary,
            "missing_tests": missing_tests_summary,
        }
    }