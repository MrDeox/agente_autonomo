import pytest
from agent.validation_steps import ValidateJsonSyntax
import json
import logging
from pathlib import Path
import tempfile
import os

def test_validate_json_syntax_success():
    """Teste de validação de sintaxe JSON bem-sucedida."""
    logger = logging.getLogger("test")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Criar arquivo JSON válido
        test_file = Path(temp_dir) / "test_valid.json"
        valid_config = {"key": "value"}
        
        with open(test_file, 'w') as f:
            json.dump(valid_config, f)
        
        # Criar patch que referencia este arquivo
        patches = [{"file_path": "test_valid.json", "operation": "REPLACE"}]
        
        validator = ValidateJsonSyntax(
            logger=logger,
            base_path=temp_dir,
            patches_to_apply=patches,
            use_sandbox=False
        )
        
        success, reason, details = validator.execute()
        assert success
        assert reason == "JSON_SYNTAX_VALIDATION_SUCCESS"

def test_validate_json_syntax_failure():
    """Teste de falha na validação de sintaxe JSON."""
    logger = logging.getLogger("test")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Criar arquivo JSON inválido
        test_file = Path(temp_dir) / "test_invalid.json"
        
        with open(test_file, 'w') as f:
            f.write('{invalid: config}')  # JSON inválido
        
        # Criar patch que referencia este arquivo
        patches = [{"file_path": "test_invalid.json", "operation": "REPLACE"}]
        
        validator = ValidateJsonSyntax(
            logger=logger,
            base_path=temp_dir,
            patches_to_apply=patches,
            use_sandbox=False
        )
        
        success, reason, details = validator.execute()
        assert not success
        assert "JSON_SYNTAX_VALIDATION_FAILED" in reason

def test_validate_json_syntax_no_patches():
    """Teste com nenhum patch para validar."""
    logger = logging.getLogger("test")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        validator = ValidateJsonSyntax(
            logger=logger,
            base_path=temp_dir,
            patches_to_apply=[],
            use_sandbox=False
        )
        
        success, reason, details = validator.execute()
        assert success
        assert reason == "JSON_SYNTAX_VALIDATION_SKIPPED"