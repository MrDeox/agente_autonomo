import pytest
from agent.validation_steps.syntax_validator import ValidateJsonSyntax
import json
import logging

def test_validate_json_syntax_success():
    """Teste de validação de sintaxe JSON bem-sucedida."""
    validator = ValidateJsonSyntax()
    valid_config = {"key": "value"}
    
    # Simule a validação com um arquivo válido
    with open('test_valid.json', 'w') as f:
        json.dump(valid_config, f)
    assert validator.execute(Path('test_valid.json'), logging.getLogger())

def test_validate_json_syntax_failure():
    """Teste de falha na validação de sintaxe JSON."""
    validator = ValidateJsonSyntax()
    
    # Simule a validação com um arquivo inválido
    with open('test_invalid.json', 'w') as f:
        f.write('{invalid: config}')
    assert not validator.execute(Path('test_invalid.json'), logging.getLogger())