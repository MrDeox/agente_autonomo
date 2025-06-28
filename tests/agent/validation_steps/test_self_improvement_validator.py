import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json
import ast

from agent.validation_steps.self_improvement_validator import SelfImprovementValidator

@pytest.fixture
def validator_instance(tmp_path):
    logger = MagicMock()
    (tmp_path / "HEPHAESTUS_MEMORY.json").write_text('{"improvements": []}')
    return SelfImprovementValidator(
        logger=logger,
        base_path=tmp_path,
        patches_to_apply=[],
        use_sandbox=False
    )

def test_self_improvement_detection(validator_instance, tmp_path):
    # Criar arquivo complexo
    complex_file = tmp_path / "complex.py"
    complex_code = '''
def a():
    if x:
        if y:
            for i in range(10):
                while z:
                    pass
    '''
    complex_file.write_text(complex_code)
    
    # Executar validação
    success, reason, _ = validator_instance.execute()
    
    assert success is True
    assert "SELF_IMPROVED" in reason
    assert any("complex.py" in k for k in validator_instance.metrics['complexity'])

def test_coverage_improvement_detection(validator_instance, tmp_path):
    # Criar arquivo com baixa cobertura
    test_file = tmp_path / "test_low_coverage.py"
    test_file.write_text("from low_coverage import func\ndef test_func(): assert func() is None")
    
    code_file = tmp_path / "low_coverage.py"
    code_file.write_text("def func(): pass")
    
    success, reason, _ = validator_instance.execute()
    
    assert success is True
    assert any("low_coverage.py" in k for k in validator_instance.metrics['test_coverage'])

def test_improvement_storage(validator_instance, tmp_path):
    complex_file = tmp_path / "to_refactor.py"
    complex_file.write_text("def a():\n    if x and y and z:\n        pass")
    
    validator_instance.execute()
    
    memory = json.loads((tmp_path / "HEPHAESTUS_MEMORY.json").read_text())
    assert len(memory['improvements']) > 0
    assert any("to_refactor.py" in imp['file_path'] for imp in memory['improvements'])

def test_metric_collection_failure(validator_instance, tmp_path, caplog):
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def invalid_func():\n    print(\"Missing closing parenthesis\"")  # Erro de sintaxe crítico
    
    success, reason, _ = validator_instance.execute()
    
    assert success is False
    assert "SELF_IMPROVEMENT_ERROR" in reason
    assert "invalid.py" in caplog.text
