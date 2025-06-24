# tests/test_code_validator.py
import pytest
import json
import logging
from pathlib import Path
from agent.code_validator import validate_python_code, validate_json_syntax

# Configurar um logger simples para os testes, se necessário
# Ou mockar o logger passado para as funções
logger = logging.getLogger("test_code_validator")
logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# logger.addHandler(handler)

# Testes para validate_python_code
def test_validate_python_code_valid(tmp_path: Path):
    valid_py_file = tmp_path / "valid.py"
    valid_py_file.write_text("def hello():\n  print('world')\n")
    result = validate_python_code(valid_py_file, logger)
    assert result[0] is True  # is_valid
    assert result[1] is None  # error_msg

def test_validate_python_code_invalid_syntax(tmp_path: Path):
    invalid_py_file = tmp_path / "invalid.py"
    invalid_py_file.write_text("def hello()\n  print('world')\n") # Erro de sintaxe: faltando ':'
    result = validate_python_code(invalid_py_file, logger)
    assert result[0] is False  # is_valid
    assert result[1] is not None  # error_msg
    assert isinstance(result[1], str)
    # A mensagem exata pode variar com a versão do Python, então verificamos se há uma mensagem.
    # Exemplo: "expected ':'" ou similar.

def test_validate_python_code_file_not_found(tmp_path: Path):
    non_existent_file = tmp_path / "non_existent.py"
    result = validate_python_code(non_existent_file, logger)
    assert result[0] is False  # is_valid
    assert result[1] is not None  # error_msg
    assert "Arquivo não encontrado" in result[1]

def test_validate_python_code_empty_file(tmp_path: Path):
    empty_py_file = tmp_path / "empty.py"
    empty_py_file.write_text("") # Arquivo vazio é Python válido
    result = validate_python_code(empty_py_file, logger)
    assert result[0] is True  # is_valid
    assert result[1] is None  # error_msg

# Testes para validate_json_syntax
def test_validate_json_syntax_valid(tmp_path: Path):
    valid_json_file = tmp_path / "valid.json"
    valid_json_content = {"key": "value", "number": 123, "nested": {"bool": True}}
    valid_json_file.write_text(json.dumps(valid_json_content))
    is_valid, error_msg = validate_json_syntax(valid_json_file, logger)
    assert is_valid is True
    assert error_msg is None

def test_validate_json_syntax_invalid_syntax(tmp_path: Path):
    invalid_json_file = tmp_path / "invalid.json"
    invalid_json_file.write_text('{"key": "value", "number": 123, "error"') # JSON malformado
    is_valid, error_msg = validate_json_syntax(invalid_json_file, logger)
    assert is_valid is False
    assert error_msg is not None
    assert isinstance(error_msg, str)
    # A mensagem de erro específica pode variar, e.g., "Expecting property name enclosed in double quotes"
    # ou "Unterminated string starting at..."

def test_validate_json_syntax_file_not_found(tmp_path: Path):
    non_existent_file = tmp_path / "non_existent.json"
    is_valid, error_msg = validate_json_syntax(non_existent_file, logger)
    assert is_valid is False
    assert error_msg is not None
    assert "Arquivo não encontrado" in error_msg

def test_validate_json_syntax_empty_file(tmp_path: Path):
    empty_json_file = tmp_path / "empty.json"
    empty_json_file.write_text("") # Arquivo JSON vazio não é válido
    is_valid, error_msg = validate_json_syntax(empty_json_file, logger)
    assert is_valid is False
    assert error_msg is not None

def test_validate_json_syntax_not_json_content(tmp_path: Path):
    not_json_file = tmp_path / "not_json.json" # Extensão .json, mas conteúdo não é JSON
    not_json_file.write_text("apenas texto simples")
    is_valid, error_msg = validate_json_syntax(not_json_file, logger)
    assert is_valid is False
    assert error_msg is not None

def test_validate_json_syntax_valid_but_complex(tmp_path: Path):
    complex_json_file = tmp_path / "complex.json"
    complex_data = {
        "name": "Test Suite",
        "version": 1.0,
        "items": [
            {"id": 1, "type": "A", "active": True, "tags": None},
            {"id": 2, "type": "B", "active": False, "tags": ["test", "example"]},
        ],
        "config": {"retries": 3, "timeout": 30.5}
    }
    complex_json_file.write_text(json.dumps(complex_data, indent=2))
    is_valid, error_msg = validate_json_syntax(complex_json_file, logger)
    assert is_valid is True
    assert error_msg is None

"""
Observações sobre os testes de `code_validator`:
- `tmp_path` é usado para criar arquivos temporários para validação.
- Para `validate_python_code`, testamos código válido, inválido, arquivo inexistente e arquivo vazio.
- Para `validate_json_syntax`, testamos JSON válido, inválido (várias formas), arquivo inexistente, arquivo vazio e conteúdo não-JSON.
- O logger é passado para as funções, mas seu output não é verificado nos testes (poderia ser com `caplog` fixture do pytest se necessário).
"""
