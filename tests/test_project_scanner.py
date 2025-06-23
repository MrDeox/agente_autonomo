# tests/test_project_scanner.py
import pytest
import os
from pathlib import Path
from agent.project_scanner import _extract_elements, update_project_manifest

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
    # Nota: _extract_elements atualmente não extrai métodos de classe, apenas classes e funções no nível do módulo.
    # Se a extração de métodos for desejada, _extract_elements precisaria ser modificado.
    # Por enquanto, o teste reflete o comportamento atual.
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
    assert ('import', 'from my_module import specific_function', None, None) in elements
    assert ('function', 'async_function', 'arg', None) in elements # ast.unparse para args de async pode variar
    assert ('class', 'ClassWithNoDoc', None, None) in elements
    assert ('function', 'func_with_defaults', "a=1, b='test'", None) in elements


# Testes para update_project_manifest
@pytest.fixture
def sample_project_structure(tmp_path: Path):
    project_dir = tmp_path / "sample_project"
    project_dir.mkdir()

    # Arquivo Python principal
    main_py_content = """
import utils
from my_lib import HelperClass

class MainApp:
    '''Classe principal da aplicação.'''
    def run(self):
        helper = HelperClass()
        return utils.do_something()

def start_app():
    '''Inicia a aplicação.'''
    app = MainApp()
    app.run()
    """
    (project_dir / "main.py").write_text(main_py_content)

    # Biblioteca local
    my_lib_dir = project_dir / "my_lib"
    my_lib_dir.mkdir()
    (my_lib_dir / "__init__.py").write_text("")
    helper_py_content = """
class HelperClass:
    '''Ajuda com tarefas.'''
    def assist(self):
        return True
    """
    (my_lib_dir / "helper.py").write_text(helper_py_content)

    # Módulo de utilidades
    utils_py_content = """
def do_something():
    '''Faz algo útil.'''
    return "done"

# Este é um comentário
    """
    (project_dir / "utils.py").write_text(utils_py_content)

    # Arquivo de dados (não Python)
    (project_dir / "data.json").write_text('{"key": "value"}')

    # Arquivo de texto
    (project_dir / "README.md").write_text("# Sample Project\n\nThis is a test project.")

    # Subdiretório vazio
    (project_dir / "empty_dir").mkdir()

    # Arquivo Python com erro de sintaxe
    error_py_content = "def error_func(:\n pass"
    (project_dir / "error_module.py").write_text(error_py_content)

    return project_dir

def test_update_project_manifest_happy_path(sample_project_structure: Path, tmp_path: Path):
    manifest_output_path = tmp_path / "AGENTS_TEST.md"
    target_files_rel = ["main.py", "data.json"] # Caminhos relativos à raiz do projeto de teste

    # Caminhos completos para target_files, relativos ao sample_project_structure
    # update_project_manifest espera caminhos relativos ao root_dir que ele escaneia

    update_project_manifest(
        root_dir=str(sample_project_structure),
        target_files=target_files_rel,
        output_path=str(manifest_output_path)
    )

    assert manifest_output_path.exists()
    content = manifest_output_path.read_text()

    # Verificar estrutura básica
    assert "# MANIFESTO DO PROJETO HEPHAESTUS" in content
    assert "## 1. ESTRUTURA DE ARQUIVOS (OTIMIZADA)" in content
    assert "## 2. RESUMO DAS INTERFACES (APIs Internas)" in content
    assert "## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO" in content

    # Verificar listagem de arquivos
    assert "sample_project/" in content # Diretório raiz
    assert "    main.py" in content
    assert "    utils.py" in content
    assert "    data.json" in content
    assert "    README.md" in content
    assert "    error_module.py" in content
    assert "    my_lib/" in content
    assert "        __init__.py" in content
    assert "        helper.py" in content
    assert "    empty_dir/" in content # Diretório vazio deve ser listado

    # Verificar resumo de APIs (exemplos)
    assert "### Módulo: `main.py`" in content
    assert "- **Classe:** `MainApp`" in content
    assert "  - *Classe principal da aplicação.*" in content
    assert "- **Função:** `start_app()`" in content
    assert "  - *Inicia a aplicação.*" in content

    assert "### Módulo: `my_lib/helper.py`" in content
    assert "- **Classe:** `HelperClass`" in content
    assert "  - *Ajuda com tarefas.*" in content

    assert "### Módulo: `utils.py`" in content
    assert "- **Função:** `do_something()`" in content
    assert "  - *Faz algo útil.*" in content

    # Verificar tratamento de erro em API
    assert "### Módulo: `error_module.py`" in content
    assert "- [ERRO] Erro na análise AST" in content # Ou mensagem similar

    # Verificar conteúdo dos arquivos alvo
    assert "### Arquivo: `main.py`" in content
    assert "class MainApp:" in content # Conteúdo de main.py
    assert "### Arquivo: `data.json`" in content
    assert '{"key": "value"}' in content # Conteúdo de data.json

    # Verificar que um arquivo não alvo NÃO tem seu conteúdo completo
    assert "### Arquivo: `utils.py`" not in content # utils.py não é alvo, então não deve ter seção de conteúdo completo

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
    assert "# ARQUIVO NÃO ENCONTRADO" in content # Ou mensagem de erro se o scanner tentar ler e falhar
    # Ajuste: a lógica atual do scanner para arquivos alvo que não existem no disco mas estão na lista `target_files`
    # resulta em "# ARQUIVO NÃO ENCONTRADO" no manifesto.

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
    assert "empty_project/" in content
    assert "## 2. RESUMO DAS INTERFACES (APIs Internas)" in content # Seções devem existir
    assert "## 3. CONTEÚDO COMPLETO DOS ARQUIVOS ALVO" in content
    # Não deve haver muitos arquivos ou APIs listados

def test_update_project_manifest_skip_dirs(tmp_path: Path):
    project_dir = tmp_path / "skip_test_project"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('hello')")

    # Diretórios que devem ser ignorados
    (project_dir / ".git").mkdir()
    (project_dir / ".git" / "config").write_text("git stuff")
    (project_dir / "venv").mkdir()
    (project_dir / "venv" / "lib").mkdir() # Simular estrutura de venv
    (project_dir / "__pycache__").mkdir()
    (project_dir / "__pycache__" / "cachefile.pyc").write_text("cache")

    manifest_output_path = tmp_path / "AGENTS_TEST_skip.md"
    update_project_manifest(
        root_dir=str(project_dir),
        target_files=[],
        output_path=str(manifest_output_path)
    )
    content = manifest_output_path.read_text()

    assert ".git/" not in content
    assert "venv/" not in content
    assert "__pycache__/" not in content
    assert "main.py" in content # Arquivo não ignorado deve estar lá

def test_project_scanner_file_read_error_in_target_file(tmp_path: Path, mocker):
    project_dir = tmp_path / "read_error_project"
    project_dir.mkdir()
    target_file_path = project_dir / "problematic_file.txt"
    target_file_path.write_text("initial content") # Create the file

    manifest_output_path = tmp_path / "AGENTS_TEST_read_error.md"

    # Mock open para simular um erro de leitura APENAS para o target_file específico
    # Esta é uma forma mais complexa de mockar. Uma forma mais simples seria
    # se o project_scanner tivesse uma função auxiliar para ler arquivos, que pudesse ser mockada.
    # Por enquanto, vamos testar o comportamento de erro que o scanner já pode ter.
    # O scanner atual captura exceções durante a leitura de `target_files`.

    # Para simular um erro de leitura mais diretamente, precisaríamos de um hook ou permissões.
    # O teste atual vai cobrir o caso de "arquivo não encontrado" se o arquivo for removido
    # ou se houver um erro genérico de `open()`.
    # Vamos testar o erro capturado por `target_content_cache[rel_path_str] = (None, e)`

    # Para forçar um erro de leitura diferente de FileNotFoundError, podemos mockar `open`
    # de forma que ele levante uma exceção para um arquivo específico.

    original_open = builtins.open
    def mock_open(file, mode='r', *args, **kwargs):
        if str(file) == str(target_file_path) and mode == 'r':
            raise OSError("Simulated read error")
        return original_open(file, mode, *args, **kwargs)

    # Precisamos importar builtins para mockar open
    import builtins
    mocker.patch('builtins.open', mock_open)

    update_project_manifest(
        root_dir=str(project_dir),
        target_files=[target_file_path.name], # Usar nome relativo
        output_path=str(manifest_output_path)
    )

    content = manifest_output_path.read_text()
    assert f"### Arquivo: `{target_file_path.name}`" in content
    assert "# ERRO: Simulated read error" in content

def test_project_scanner_file_read_error_in_api_summary(tmp_path: Path, mocker):
    project_dir = tmp_path / "api_read_error_project"
    project_dir.mkdir()
    python_file_path = project_dir / "problematic_api.py"
    python_file_path.write_text("print('valid python but will fail to read')")

    manifest_output_path = tmp_path / "AGENTS_TEST_api_read_error.md"

    import builtins
    original_open = builtins.open
    def mock_open_api(file, mode='r', *args, **kwargs):
        if str(file) == str(python_file_path) and mode == 'r':
            raise OSError("Simulated API read error")
        return original_open(file, mode, *args, **kwargs)

    mocker.patch('builtins.open', mock_open_api)

    update_project_manifest(
        root_dir=str(project_dir),
        target_files=[],
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
