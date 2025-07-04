import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from agent.utils.llm_client import call_llm_api

@pytest.fixture
def mock_logger():
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.error = Mock()
    return logger

@pytest.fixture
def model_config():
    return {
        "primary": "test_model",
        "fallback": "fallback_model",
        "primary_api_key": "test_api_key",
        "fallback_api_key": "fallback_api_key",
        "primary_base_url": "http://fake.url.brain",
        "fallback_base_url": "http://fallback.url.brain",
    }

# tests/test_brain.py
import pytest
import json
import requests
import logging
from unittest.mock import MagicMock, patch

from agent.brain import (
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message
)
from agent.utils.llm_client import call_llm_api

# --- Testes para call_llm_api (em agent.utils.llm_client) ---
# Verificam a funcionalidade da chamada LLM usada pelas funções do brain
@patch('agent.utils.llm_client.requests.post')
def test_brain_call_llm_api_success(mock_post, mock_logger, model_config):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta LLM simulada (brain)"}}]
    }
    mock_post.return_value = mock_response

    content, error = call_llm_api(model_config, "prompt_brain", 0.5, mock_logger)

    assert content == "Resposta LLM simulada (brain)"
    assert error is None
    mock_post.assert_called_once()


@patch('agent.utils.llm_client.requests.post')
def test_brain_call_llm_api_request_exception(mock_post, mock_logger, model_config):
    mock_post.side_effect = requests.exceptions.RequestException("Erro de rede (brain)")
    content, error = call_llm_api(model_config, "pb", 0.5, mock_logger)
    assert content is None
    assert error is not None and "Erro de rede (brain)" in error


# --- Testes para generate_next_objective (que usa call_llm_api) ---
@patch('agent.brain.call_llm_api')
def test_generate_next_objective_success(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = ("Próximo objetivo simulado.", None)

    objective = generate_next_objective(model_config, "manifesto_atual", mock_logger, "/dummy/path")
    assert objective == "Próximo objetivo simulado."
    mock_call_llm_api.assert_called_once()
    # Verificar args da chamada para call_llm_api
    # A chamada em generate_next_objective usa keyword arguments
    _, kwargs = mock_call_llm_api.call_args
    assert kwargs['model_config'] == model_config
    assert "manifesto_atual" in kwargs['prompt']
    assert kwargs['temperature'] == 0.3
    assert kwargs['logger'] == mock_logger

@patch('agent.brain.call_llm_api')
def test_generate_next_objective_api_error(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = (None, "Erro de API simulado")

    objective = generate_next_objective(model_config, "manifesto_atual", mock_logger, "/dummy/path")
    assert objective == "Analisar o estado atual do projeto e propor uma melhoria incremental" # Fallback
    mock_logger.error.assert_called_with("Erro ao gerar próximo objetivo: Erro de API simulado")

@patch('agent.brain.call_llm_api')
def test_generate_next_objective_empty_llm_response(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = ("", None) # Resposta de conteúdo vazia

    # Adicionando argumento faltante memory_summary
    objective = generate_next_objective(
        model_config=model_config, 
        current_manifest="manifesto_atual",
        logger=mock_logger,
        project_root_dir="/dummy/path",
        memory_summary=""
    )
    assert "Analisar" in objective # Verificação mais flexível
    mock_logger.warning.assert_called_with("Resposta vazia do LLM para próximo objetivo.")


@patch('agent.brain.call_llm_api')
def test_generate_next_objective_empty_manifest(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = ("Objetivo para manifesto vazio", None)

    objective = generate_next_objective(model_config, "", mock_logger, "/dummy/path") # Manifesto vazio
    assert objective == "Objetivo para manifesto vazio"

    # Verificar conceitos-chave no prompt
    _, kwargs = mock_call_llm_api.call_args
    prompt_arg = kwargs['prompt']
    assert "Planejador Estratégico" in prompt_arg
    assert "Hephaestus" in prompt_arg
    assert "objetivo" in prompt_arg

@patch('agent.brain.call_llm_api')
def test_generate_next_objective_with_memory(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = ("Objetivo com memória.", None)
    memory_summary = "Lembre-se de X."
    objective = generate_next_objective(model_config, "manifesto", mock_logger, "/dummy/path", memory_summary=memory_summary)
    assert objective == "Objetivo com memória."
    _, kwargs = mock_call_llm_api.call_args
    prompt_arg = kwargs['prompt'] # prompt é acessado via kwargs
    assert "HISTÓRICO RECENTE DO PROJETO E DO AGENTE" in prompt_arg
    assert memory_summary in prompt_arg


# --- Testes para generate_capacitation_objective (que usa call_llm_api) ---
@patch('agent.brain.call_llm_api')
def test_generate_capacitation_objective_success(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = ("Objetivo de capacitação simulado.", None)

    objective = generate_capacitation_objective(model_config, "Análise do engenheiro.", logger=mock_logger)
    assert objective == "Objetivo de capacitação simulado."
    mock_call_llm_api.assert_called_once()
    _, kwargs = mock_call_llm_api.call_args
    assert kwargs['model_config'] == model_config
    assert "Análise do Engenheiro que Requer Nova Capacidade" in kwargs['prompt']
    assert "Análise do engenheiro." in kwargs['prompt']
    assert kwargs['temperature'] == 0.3
    assert kwargs['logger'] == mock_logger

@patch('agent.brain.call_llm_api')
def test_generate_capacitation_objective_api_error(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = (None, "Erro de API capacitação")
    objective = generate_capacitation_objective(model_config, "Análise.", logger=mock_logger)
    assert objective == "Analisar a necessidade de capacitação e propor uma solução" # Fallback
    mock_logger.error.assert_called_with("Erro ao gerar objetivo de capacitação: Erro de API capacitação")

@patch('agent.brain.call_llm_api')
def test_generate_capacitation_objective_with_memory(mock_call_llm_api, mock_logger, model_config):
    mock_call_llm_api.return_value = ("Objetivo de capacitação com memória.", None)
    memory_summary = "Capacitação X já foi tentada."
    objective = generate_capacitation_objective(model_config, "Análise.", logger=mock_logger, memory_summary=memory_summary)
    assert objective == "Objetivo de capacitação com memória."
    _, kwargs = mock_call_llm_api.call_args
    prompt_arg = kwargs['prompt']
    assert "HISTÓRICO RECENTE DO AGENTE" in prompt_arg
    assert memory_summary in prompt_arg

# --- Testes para generate_commit_message (simulado, sem chamada real de LLM) ---
# A função generate_commit_message no código fornecido está atualmente simulando a chamada LLM
# e construindo a mensagem heuristicamente. Portanto, não precisamos mockar call_llm_api para ela.
def test_generate_commit_message_feat(mock_logger, model_config):
    objective = "Adicionar nova funcionalidade X"
    analysis = "Implementado X com sucesso."
    commit_msg = generate_commit_message(analysis, objective, mock_logger)
    assert commit_msg.startswith("feat: ")
    assert "Adicionar nova funcionalidade X" in commit_msg

def test_generate_commit_message_fix(mock_logger, model_config):
    objective = "Corrigir bug na validação Y"
    analysis = "Validação Y agora funciona corretamente."
    commit_msg = generate_commit_message(analysis, objective, mock_logger)
    assert commit_msg.startswith("fix: ")
    assert "Corrigir bug na validação Y" in commit_msg

def test_generate_commit_message_long_objective_truncates(mock_logger, model_config):
    objective = "Este é um objetivo muito longo que definitivamente excede o limite de setenta caracteres imposto pela heurística da função de mensagem de commit."
    analysis = "Implementado."
    commit_msg = generate_commit_message(analysis, objective, mock_logger)
    assert len(commit_msg.split(":")[1].strip()) <= 70 + 3 # "..."
    assert commit_msg.endswith("...")