import pytest
import json
import logging
import tempfile
from pathlib import Path
from agent.config_loader import load_config
from agent.validation_steps import ValidateJsonSyntax

def test_load_config_success():
    """Teste de carregamento bem-sucedido da configuração."""
    config = load_config()
    assert config is not None
    # Verificar se tem estruturas básicas esperadas
    assert isinstance(config, dict)

def test_config_syntax_validation():
    """Teste de validação de sintaxe JSON no config."""
    logger = logging.getLogger("test")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Teste com sintaxe válida
        valid_config_file = Path(temp_dir) / "hephaestus_config.json"
        test_config = {
            "agent": {
                "validation_steps": {
                    "syntax_validator": {
                        "enabled": True
                    }
                }
            }
        }
        
        with open(valid_config_file, 'w') as f:
            json.dump(test_config, f)
        
        patches = [{"file_path": "hephaestus_config.json", "operation": "REPLACE"}]
        
        validator = ValidateJsonSyntax(
            logger=logger,
            base_path=temp_dir,
            patches_to_apply=patches,
            use_sandbox=False
        )
        
        success, reason, details = validator.execute()
        assert success
        assert reason == "JSON_SYNTAX_VALIDATION_SUCCESS"

def test_config_syntax_validation_invalid():
    """Teste de validação com JSON inválido."""
    logger = logging.getLogger("test")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Teste com sintaxe inválida
        invalid_config_file = Path(temp_dir) / "hephaestus_config.json"
        
        with open(invalid_config_file, 'w') as f:
            f.write('{invalid: config}')  # JSON inválido
        
        patches = [{"file_path": "hephaestus_config.json", "operation": "REPLACE"}]
        
        validator = ValidateJsonSyntax(
            logger=logger,
            base_path=temp_dir,
            patches_to_apply=patches,
            use_sandbox=False
        )
        
        success, reason, details = validator.execute()
        assert not success
        assert "JSON_SYNTAX_VALIDATION_FAILED" in reason