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

def update_project_manifest(
    root_dir: str,
    target_files: List[str],
    output_path: str = "AGENTS.md",
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
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]
            # Depois, os padrões de diretórios excluídos
            # Para excluded_dir_patterns, precisamos checar o nome do diretório E o caminho relativo
            # Isso é feito para permitir padrões como "tests" (qualquer pasta chamada tests)
            # ou "src/tests" (uma pasta específica).
            # No entanto, `d` aqui é apenas o nome base. Para padrões de caminho, precisaríamos do caminho completo.
            # Vamos simplificar por agora para filtrar apenas pelo nome base do diretório.
            # Padrões mais complexos (como caminhos relativos) exigiriam uma lógica mais elaborada aqui
            # ou um pré-processamento de todos os caminhos.
            # Por enquanto, `active_excluded_dir_patterns` conterá nomes de diretórios a serem excluídos.
            dirs[:] = [d for d in dirs if d not in active_excluded_dir_patterns and not any(fnmatch.fnmatch(d, pattern) for pattern in active_excluded_dir_patterns)]


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
                if current_dir_name in active_excluded_dir_patterns or \
                   any(fnmatch.fnmatch(current_dir_name, pattern) for pattern in active_excluded_dir_patterns) or \
                   current_dir_name in skip_dirs: # Adicionado skip_dirs aqui também
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
