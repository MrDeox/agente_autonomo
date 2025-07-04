import pytest
from unittest.mock import MagicMock, patch
from agent.brain import generate_commit_message, generate_next_objective

# Testes para generate_commit_message

def test_generate_commit_message_feat():
    """Testa se a mensagem de commit para uma nova feature é gerada corretamente."""
    logger = MagicMock()
    objective = "Add a new button to the main interface"
    analysis = "Added a new button with id 'new_button'"
    commit_message = generate_commit_message(analysis, objective, logger)
    assert commit_message.startswith("feat:")
    assert "Add a new button" in commit_message

def test_generate_commit_message_fix():
    """Testa se a mensagem de commit para uma correção de bug é gerada corretamente."""
    logger = MagicMock()
    objective = "Fix the login issue where the user is not redirected"
    analysis = "Fixed the redirection logic in the login controller"
    commit_message = generate_commit_message(analysis, objective, logger)
    assert commit_message.startswith("fix:")
    assert "Fix the login issue" in commit_message

def test_generate_commit_message_refactor():
    """Testa se a mensagem de commit para uma refatoração é gerada corretamente."""
    logger = MagicMock()
    objective = "Refactor the authentication service to use a new class"
    analysis = "Refactored AuthService"
    commit_message = generate_commit_message(analysis, objective, logger)
    assert commit_message.startswith("refactor:")

def test_generate_commit_message_docs():
    """Testa se a mensagem de commit para uma atualização de documentação é gerada corretamente."""
    logger = MagicMock()
    objective = "Update the README.md file with new installation instructions"
    analysis = "Updated README.md"
    commit_message = generate_commit_message(analysis, objective, logger)
    assert commit_message.startswith("docs:")

def test_generate_commit_message_test():
    """Testa se a mensagem de commit para a adição de testes é gerada corretamente."""
    logger = MagicMock()
    objective = "Create new tests for the user model"
    analysis = "Added tests for User"
    commit_message = generate_commit_message(analysis, objective, logger)
    assert commit_message.startswith("test:")

def test_generate_commit_message_long_objective_truncation():
    """Testa se um objetivo longo é truncado corretamente na mensagem de commit."""
    logger = MagicMock()
    objective = "feat: Implement a very long and detailed feature description that surely exceeds the recommended character limit for a commit summary line"
    analysis = "Done"
    commit_message = generate_commit_message(analysis, objective, logger)
    assert len(commit_message) <= 72
    assert commit_message.endswith("...")

# Esqueleto para testes de generate_next_objective (mais complexo)

@patch('agent.brain.call_llm_api')
@patch('agent.brain.analyze_code_metrics')
@patch('agent.brain.PerformanceAnalysisAgent')
def test_generate_next_objective_basic_flow(mock_perf_agent, mock_code_metrics, mock_call_llm):
    """
    Testa o fluxo básico de generate_next_objective, garantindo que as dependências são chamadas
    e que o prompt é construído e enviado para o LLM.
    """
    # Configuração dos Mocks
    logger = MagicMock()
    mock_code_metrics.return_value = {"summary": {"large_files": [("test.py", 500)]}}
    mock_perf_agent.return_value.analyze_performance.return_value = "Performance is great."
    mock_call_llm.return_value = ("Test Objective", None)

    # Execução da função
    objective = generate_next_objective(
        model_config={},
        current_manifest="Manifest content",
        logger=logger,
        project_root_dir="."
    )

    # Verificações
    mock_code_metrics.assert_called_once()
    mock_perf_agent.return_value.analyze_performance.assert_called_once()
    mock_call_llm.assert_called_once()
    assert objective == "Test Objective"
    
    # Verifica se o prompt contém as seções esperadas
    prompt_sent_to_llm = mock_call_llm.call_args[1]['prompt']
    assert "[CODE METRICS AND ANALYSIS]" in prompt_sent_to_llm
    assert "test.py (LOC: 500)" in prompt_sent_to_llm
    assert "[PERFORMANCE ANALYSIS]" in prompt_sent_to_llm
    assert "Performance is great." in prompt_sent_to_llm

# TODO: Adicionar mais testes para generate_next_objective cobrindo diferentes cenários (sem manifesto, erro na análise, etc.)
# TODO: Adicionar testes para generate_capacitation_objective 