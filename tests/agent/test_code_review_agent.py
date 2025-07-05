import pytest
import logging
from unittest.mock import MagicMock, patch

from agent.agents.code_review_agent import CodeReviewAgent

@pytest.fixture
def mock_logger():
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def code_review_agent(mock_logger):
    # O model_config pode ser um mock vazio, pois os testes determinísticos não o utilizam
    model_config = {}
    return CodeReviewAgent(model_config=model_config, logger=mock_logger)

def test_review_patches_with_valid_syntax_and_trivial_change(code_review_agent):
    """
    Testa que um patch com sintaxe válida e conteúdo trivial passa na revisão
    sem precisar de uma chamada LLM.
    """
    patches = [{
        "file_path": "src/module.py",
        "operation": "INSERT",
        "content": "# This is a comment"
    }]
    review_passed, feedback = code_review_agent.review_patches(patches)
    assert review_passed is True
    assert "auto-approved" in feedback

def test_review_patches_with_syntax_error(code_review_agent):
    """
    Testa que um patch contendo um erro de sintaxe é reprovado imediatamente
    pela verificação determinística.
    """
    patches = [{
        "file_path": "src/module.py",
        "operation": "REPLACE",
        "content": "def my_function(param1, param2):\n    print(param1, param2)\n    return x = 1 # Invalid syntax"
    }]
    review_passed, feedback = code_review_agent.review_patches(patches)
    assert review_passed is False
    assert "SyntaxError" in feedback
    assert "Automated syntax check failed" in feedback

def test_review_patches_with_no_patches(code_review_agent):
    """
    Testa que a revisão passa se não houver patches para revisar.
    """
    patches = []
    review_passed, feedback = code_review_agent.review_patches(patches)
    assert review_passed is True
    assert "No patches to review" in feedback

def test_review_patches_with_valid_syntax_but_needs_llm_review(code_review_agent, mocker):
    """
    Testa que, após a aprovação da sintaxe, a chamada LLM é feita para patches não triviais.
    Aqui, zombamos da chamada LLM para simular uma revisão bem-sucedida.
    """
    patches = [{
        "file_path": "src/module.py",
        "operation": "REPLACE",
        "content": "def my_complex_function(data):\n    # Some complex logic here\n    return True"
    }]
    
    # Mock da chamada LLM para que não seja feita uma chamada de API real
    mock_llm_call = mocker.patch('agent.utils.llm_client.call_llm_api')
    mock_llm_call.return_value = ('{"review_passed": true, "feedback": "OK"}', {"error": None})

    review_passed, feedback = code_review_agent.review_patches(patches)
    
    assert review_passed is True
    assert feedback == "OK"
    mock_llm_call.assert_called_once() # Verifica se o LLM foi realmente chamado

def test_review_patches_ignores_non_python_files_for_syntax_check(code_review_agent):
    """
    Testa que arquivos não-.py com conteúdo que seria sintaxe inválida em Python
    passam na verificação de sintaxe.
    """
    patches = [{
        "file_path": "README.md",
        "operation": "INSERT",
        "content": "This is `not` python code and should pass."
    }]
    # Como o conteúdo é não trivial, ele irá para a revisão LLM.
    # Nós zombamos da revisão LLM para isolar o teste da verificação de sintaxe.
    with patch('agent.utils.llm_client.call_llm_api', return_value=('{"review_passed": true, "feedback": "OK"}', {"error": None})):
        review_passed, feedback = code_review_agent.review_patches(patches)
        
    assert review_passed is True
    assert feedback == "OK" 