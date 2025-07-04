import pytest
from agent.code_metrics import analyze_complexity
from agent.validation_steps import CYCLOMATIC_COMPLEXITY_CHECK

def test_high_cc_patch_rejection():
    """Valida que patches com CC >30 são bloqueados antes da aplicação."""
    # Simula um patch com alta complexidade
    high_cc_code = """
def complex_function():
    if True:
        pass
    elif False:
        pass
    else:
        pass
    for i in range(10):
        pass
    while True:
        pass
"""
    cc_report = analyze_complexity(high_cc_code)
    assert cc_report['cyclomatic_complexity'] > 30
    # Verifica que a validação bloqueia a aplicação
    with pytest.raises(ValueError, match=".*complexidade ciclomática excede o limite de 30.*"):
        CYCLOMATIC_COMPLEXITY_CHECK.validate(high_cc_code)