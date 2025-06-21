import pathlib
import fnmatch
from typing import List, Optional

def generate_project_snapshot(
    root_dir: str,
    exclude_dirs: Optional[List[str]] = None,
    exclude_files: Optional[List[str]] = None,
    use_gitignore: bool = True
) -> str:
    """
    Gera um snapshot do projeto contendo o código-fonte de todos os arquivos .py.
    
    Args:
        root_dir: Diretório raiz do projeto
        exclude_dirs: Diretórios a serem ignorados
        exclude_files: Arquivos específicos a serem ignorados
        use_gitignore: Se deve usar o arquivo .gitignore para exclusões
    
    Returns:
        String formatada com a estrutura do projeto e conteúdo dos arquivos
    """
    root_path = pathlib.Path(root_dir)
    exclude_dirs = exclude_dirs or []
    exclude_files = exclude_files or []
    
    # Padrões de exclusão padrão
    default_exclude_dirs = ['__pycache__', '.git', '.venv', 'logs']
    default_exclude_files = ['.env']
    
    # Combina exclusões padrão com as fornecidas pelo usuário
    exclude_dirs = list(set(exclude_dirs + default_exclude_dirs))
    exclude_files = list(set(exclude_files + default_exclude_files))
    
    # Padrões do .gitignore
    gitignore_patterns = []
    if use_gitignore:
        gitignore_path = root_path / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('!'):
                        gitignore_patterns.append(line)
    
    output = ["### ARQUITETURA DO PROJETO ###\n"]
    
    # Percorre recursivamente apenas arquivos .py
    for file_path in root_path.rglob('**/*.py'):
        if not file_path.is_file():
            continue
            
        # Obtém caminho relativo
        rel_path = file_path.relative_to(root_path)
        rel_path_str = str(rel_path)
        
        # Verifica exclusões por nome de arquivo
        if file_path.name in exclude_files:
            continue
            
        # Verifica exclusões por diretório
        if any(ex_dir in file_path.parts for ex_dir in exclude_dirs):
            continue
            
        # Verifica se o arquivo está em um diretório venv
        if 'venv' in file_path.parts or '.venv' in file_path.parts:
            continue
            
        # Verifica padrões do .gitignore
        for pattern in gitignore_patterns:
            # Padrões que terminam com / devem corresponder apenas a diretórios
            if pattern.endswith('/'):
                dir_pattern = pattern.rstrip('/')
                if fnmatch.fnmatch(str(rel_path.parent), dir_pattern):
                    continue
                if fnmatch.fnmatch(rel_path.name, dir_pattern):
                    continue
            else:
                if fnmatch.fnmatch(rel_path_str, pattern):
                    continue
                if fnmatch.fnmatch(f"{rel_path_str}/", pattern):
                    continue
        
        try:
            # Lê o conteúdo do arquivo
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            content = f"# Erro ao ler arquivo: {str(e)}"
        
        # Adiciona ao output formatado
        output.append(f"--- INÍCIO DO ARQUIVO: {rel_path} ---")
        output.append(f"```python\n{content}\n```")
        output.append(f"--- FIM DO ARQUIVO: {rel_path} ---\n")
    
    return "\n".join(output)