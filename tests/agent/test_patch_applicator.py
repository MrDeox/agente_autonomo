import pytest
from agent.patch_applicator import apply_patches, _validate_patch_complexity
from agent.code_metrics import analyze_complexity
import logging

def test_high_complexity_patch_blocked(caplog):
    """Teste se patches com CC > 30 são bloqueados."""
    mock_instruction = {'operation': 'INSERT', 'content': 'def complex_function():\n    if True:\n        pass\n    else:\n        pass\n    for i in range(10):\n        pass\n    while True:\n        break'}
    logger = logging.getLogger('test')
    assert not _validate_patch_complexity(mock_instruction, logger)
    assert 'Patch blocked due to high cyclomatic complexity' in caplog.text

def test_low_complexity_patch_applied():
    """Teste se patches com CC <= 30 são aplicados."""
    mock_instruction = {'operation': 'INSERT', 'content': 'def simple_function():\n    pass'}
    logger = logging.getLogger('test')
    assert _validate_patch_complexity(mock_instruction, logger)