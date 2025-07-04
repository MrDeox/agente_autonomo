import pytest
import json
from agent.config_loader import load_config
from agent.validation_steps.syntax_validator import ValidateJsonSyntax
from pathlib import Path

def test_load_config_success():
    """Teste de carregamento bem-sucedido do hephaestus_config.json."""
    config = load_config()
    assert config is not None
    assert 'agent' in config
    assert 'validation_steps' in config['agent']

def test_config_syntax_validation():
    """Teste de validação de sintaxe JSON no config."""
    validator = ValidateJsonSyntax()
    test_config = {
        "agent": {
            "validation_steps": {
                "syntax_validator": {
                    "enabled": true
                }
            }
        }
    }
    
    # Teste com sintaxe válida
    assert validator.execute(Path('hephaestus_config.json'), logging.getLogger())
    
    # Teste com sintaxe inválida
    with open('hephaestus_config.json', 'w') as f:
        f.write('{invalid: config}')
    assert not validator.execute(Path('hephaestus_config.json'), logging.getLogger())