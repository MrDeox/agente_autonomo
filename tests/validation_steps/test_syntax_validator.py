import pytest
import logging
from agent.validation_steps.syntax_validator import validate_config_structure

def test_extra_fields_in_config(caplog):
    """Teste se a validação rejeita campos extras no config e loga corretamente."""
    invalid_config = {"key1": "value1", "key2": 42, "extra_key": "should_reject"}
    
    with pytest.raises(ValueError, match="Invalid config structure"):
        validate_config_structure(invalid_config, logging.getLogger())
    
    assert any(record.levelno == logging.ERROR and "extra_key" in record.message for record in caplog.records), 
    "Log should indicate rejection of extra fields in config"