# tests/test_project_scanner.py
import pytest
import os
from pathlib import Path
from agent.project_scanner import _extract_elements, update_project_manifest
import builtins # CORRIGIDO: Adicionado import builtins

# Testes para _extract_elements
def test_extract_elements_simple_code():
    code = """
import os
import sys

class MyClass:
    '''Docstring da classe.'''
    def method_one(self, arg1):
        '''Docstring do método.'''
        pass

def my_function(param1, param2):
    '''Docstring da função.'''
    return param1 + param2

class AnotherClass(MyClass):
    pass
    """
    elements = _extract_elements(code)
    assert ('import', 'import os', None, None) in elements
    assert ('import', 'import sys', None, None) in elements
    assert ('class', 'MyClass', None, 'Docstring da classe.') in elements
    assert ('function', 'my_function', 'param1, param2', 'Docstring da função.') in elements
    assert ('class', 'AnotherClass', 'MyClass', None) in elements

def test_extract_elements_empty_code():
    elements = _extract_elements("")
    assert elements == []

def test_extract_elements_invalid_syntax():
    elements = _extract_elements("def func( : pass")
    assert len(elements) == 1
    assert elements[0][0] == 'error'
    assert "Erro na análise AST" in elements[0][3]

def test_extract_elements_with_various_constructs():
    code = """
from my_module import specific_function
async def async_function(arg): pass
class ClassWithNoDoc: pass
def func_with_defaults(a=1, b='test'): pass
    """
    elements = _extract_elements(code)
    # expected_elements agora deve incluir async_function corretamente
    assert ('import', 'from my_module import specific_function', None, None) in elements
    # O unparse de args para async pode ser só 'arg' ou 'arg: None' dependendo da versão do ast.unparse e python
    # Vamos ser flexíveis ou verificar o comportamento exato.
    # Com a correção em _extract_elements, ast.AsyncFunctionDef é tratado.
    found_async_func = False
    for el_type, name, details, docstring in elements:
        if el_type == 'function' and name == 'async_function':
            assert details == 'arg' # Esperado após correção e comportamento típico de unparse
            assert docstring is None
            found_async_func = True
            break
    assert found_async_func, "Função async não encontrada ou detalhes incorretos"
    assert ('class', 'ClassWithNoDoc', None, None) in elements
    assert ('function', 'func_with_defaults', "a=1, b='test'", None) in elements


# Testes para update_project_manifest
@pytest.fixture
def sample_project_structure(tmp_path: Path):
    project_dir = tmp_path / "sample_project"
    project_dir.mkdir()

    (project_dir / "main.py").write_text("""
import utils
from my_lib import HelperClass

class MainApp:
    '''Classe principal da aplicação.'''
    def run(self):
        helper = HelperClass()
        return utils.do_something()

async def async_main_runner(): # Adicionado para testar AsyncFunctionDef no manifesto
    '''Runs main async.'''
    pass

def start_app():
    '''Inicia a aplicação.'''
    app = MainApp()
    app.run()
    """)

    my_lib_dir = project_dir / "my_lib"
    my_lib_dir.mkdir()
    (my_lib_dir / "__init__.py").write_text("")
    (my_lib_dir / "helper.py").write_text("""
class HelperClass:
    '''Ajuda com tarefas.'''
    def assist(self):
        return True
    """)

    (project_dir / "utils.py").write_text("""
def do_something():
    '''Faz algo útil.'''
    return "done"
    """)
    (project_dir / "data.json").write_text('{"key": "value"}')
    (project_dir / "README.md").write_text("# Sample Project\n\nThis is a test project.")
    (project_dir / "empty_dir").mkdir() # Diretório vazio
    (project_dir / "error_module.py").write_text("def error_func(:\n pass")

    return project_dir

def test_update_project_manifest_happy_path(sample_project_structure: Path, tmp_path: Path):
    manifest_output_path = tmp_path / "AGENTS_TEST.md"
    target_files_rel = ["main.py", "data.json"]

    update_project_manifest(
        root_dir=str(sample_project_structure),
        target_files=target_files_rel,
        output_path=str(manifest_output_path)
    )

    assert manifest_output_path.exists()
    content = manifest_output_path.read_text()

    assert "# MANIFESTO DO PROJETO HEPHAESTUS" in content
    assert "## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)" in content
    assert "sample_project/" in content
    assert "    main.py" in content
    assert "    utils.py" in content
    assert "    data.json" in content
    assert "    README.md" in content
    assert "    error_module.py" in content
    assert "    my_lib/" in content
    assert "        __init__.py" in content
    assert "        helper.py" in content
    assert "    empty_dir/" in content # CORRIGIDO: Esperado que diretórios vazios sejam listados

    assert "## 2. RESUMO DAS INTERFACES (APIs Internas)" in content
    assert "### Módulo: `main.py`" in content
    assert "- **Classe:** `MainApp`" in content
    assert "- **Função:** `async_main_runner()`" in content # Testar se a função async é listada
    assert "  - *Runs main async.*" in content
    assert "- **Função:** `start_app()`" in content

    assert "### Módulo: `my_lib/helper.py`" in content
    assert "- **Classe:** `HelperClass`" in content

    assert "### Módulo: `error_module.py`" in content
    assert "- [ERRO] Erro na análise AST" in content

    assert "## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO" in content
    assert "### Arquivo: `main.py`" in content
    assert "class MainApp:" in content
    assert "async def async_main_runner():" in content
    assert "### Arquivo: `data.json`" in content
    assert '{"key": "value"}' in content
    assert "### Arquivo: `utils.py`" not in content # utils.py não é alvo

def test_update_project_manifest_target_file_not_found(sample_project_structure: Path, tmp_path: Path):
    manifest_output_path = tmp_path / "AGENTS_TEST_missing.md"
    target_files = ["main.py", "non_existent_file.txt"]

    update_project_manifest(
        root_dir=str(sample_project_structure),
        target_files=target_files,
        output_path=str(manifest_output_path)
    )

    content = manifest_output_path.read_text()
    assert "### Arquivo: `non_existent_file.txt`" in content
    assert "# ARQUIVO NÃO ENCONTRADO OU NÃO PROCESSADO" in content # Mensagem atualizada no scanner

def test_update_project_manifest_empty_project(tmp_path: Path):
    empty_project_dir = tmp_path / "empty_project"
    empty_project_dir.mkdir()
    manifest_output_path = tmp_path / "AGENTS_TEST_empty.md"

    update_project_manifest(
        root_dir=str(empty_project_dir),
        target_files=[],
        output_path=str(manifest_output_path)
    )
    content = manifest_output_path.read_text()
    assert "empty_project/" in content # CORRIGIDO: Esperado que o diretório raiz vazio seja listado
    assert "## 2. RESUMO DAS INTERFACES (APIs Internas)" in content
    assert "## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO" in content

def test_update_project_manifest_skip_dirs(tmp_path: Path):
    project_dir = tmp_path / "skip_test_project"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('hello')")

    (project_dir / ".git").mkdir()
    (project_dir / ".git" / "config").write_text("git stuff")
    (project_dir / "venv").mkdir()
    (project_dir / "venv" / "lib").mkdir()
    (project_dir / "__pycache__").mkdir()
    (project_dir / "__pycache__" / "cachefile.pyc").write_text("cache")

    manifest_output_path = tmp_path / "AGENTS_TEST_skip.md"
    update_project_manifest(
        root_dir=str(project_dir),
        target_files=[],
        output_path=str(manifest_output_path)
    )
    content = manifest_output_path.read_text()

    assert ".git/" not in content # Os diretórios em si não devem ser listados se estão em skip_dirs
    assert "venv/" not in content
    assert "__pycache__/" not in content
    assert "main.py" in content

def test_project_scanner_file_read_error_in_target_file(tmp_path: Path, mocker):
    project_dir = tmp_path / "read_error_project"
    project_dir.mkdir()
    target_file_path = project_dir / "problematic_file.txt"
    target_file_path.write_text("initial content")

    manifest_output_path = tmp_path / "AGENTS_TEST_read_error.md"

    original_open = builtins.open # Salva o original
    def mock_open_specific_error(file, mode='r', *args, **kwargs):
        if str(file) == str(target_file_path) and mode == 'r':
            raise OSError("Simulated read error for target")
        return original_open(file, mode, *args, **kwargs)

    mocker.patch('builtins.open', mock_open_specific_error)

    update_project_manifest(
        root_dir=str(project_dir),
        target_files=[target_file_path.name],
        output_path=str(manifest_output_path)
    )

    content = manifest_output_path.read_text()
    assert f"### Arquivo: `{target_file_path.name}`" in content
    assert "# ERRO: Simulated read error for target" in content

def test_project_scanner_file_read_error_in_api_summary(tmp_path: Path, mocker):
    project_dir = tmp_path / "api_read_error_project"
    project_dir.mkdir()
    python_file_path = project_dir / "problematic_api.py"
    python_file_path.write_text("print('valid python but will fail to read for API summary')")

    manifest_output_path = tmp_path / "AGENTS_TEST_api_read_error.md"

    original_open = builtins.open # Salva o original
    def mock_open_api_error(file, mode='r', *args, **kwargs):
        if str(file) == str(python_file_path) and 'r' in mode: # Checar modo 'r'
            raise OSError("Simulated API read error")
        return original_open(file, mode, *args, **kwargs)

    mocker.patch('builtins.open', mock_open_api_error)

    update_project_manifest(
        root_dir=str(project_dir),
        target_files=[], # Não é alvo, mas deve ser escaneado para API
        output_path=str(manifest_output_path)
    )

    content = manifest_output_path.read_text()
    assert f"### Módulo: `{python_file_path.name}`" in content
    assert "- [ERRO] Erro na leitura do arquivo: Simulated API read error" in content

"""
Observações sobre os testes de `update_project_manifest`:
- A fixture `sample_project_structure` cria um ambiente de projeto realista.
- `tmp_path` é usado para garantir que os testes não deixem rastros.
- Verificamos as seções principais, a listagem de arquivos, os resumos de API e o conteúdo dos arquivos alvo.
- Casos de erro como arquivo alvo não encontrado e erro de sintaxe em Python são cobertos.
- O mock de `builtins.open` é uma técnica mais avançada para simular erros de I/O específicos.
"""
