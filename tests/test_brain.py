import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from agent.brain import _call_llm_api

@pytest.fixture
def mock_logger():
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.error = Mock()
    return logger
# tests/test_brain.py
import pytest
import json
import requests # Mantido devido à cópia de _call_llm_api
import logging
from unittest.mock import MagicMock, patch

from agent.brain import (
    _call_llm_api, # Mantido para testar a cópia local
    generate_next_objective,
    generate_capacitation_objective,
    # get_action_plan, # Removido
    # get_maestro_decision, # Removido
    # parse_json_response # Removido
    generate_commit_message # Adicionado para teste se necessário
)

# Logger mockado
@pytest.fixture
def mock_logger():
    logger = MagicMock(spec=logging.Logger)
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger

# --- Testes para _call_llm_api (cópia local em brain.py) ---
# Estes testes verificam a funcionalidade da cópia de _call_llm_api que permanece em brain.py
# para uso por generate_next_objective, etc.
@patch('agent.brain.requests.post') # Patch no local correto
def test_brain_call_llm_api_success(mock_post, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta LLM simulada (brain)"}}]
    }
    mock_post.return_value = mock_response

    content, error = _call_llm_api("fake_key_brain", "model_brain", "prompt_brain", 0.5, "http://fake.url.brain", mock_logger)

    assert content == "Resposta LLM simulada (brain)"
    assert error is None
    mock_post.assert_called_once()
    # Verificar se o logger foi chamado com a mensagem específica
    mock_logger.debug.assert_called_once()
    args, _ = mock_logger.debug.call_args
    assert "API Response (brain._call_llm_api)" in args[0]


@patch('agent.brain.requests.post')
def test_brain_call_llm_api_request_exception(mock_post, mock_logger):
    mock_post.side_effect = requests.exceptions.RequestException("Erro de rede (brain)")
    content, error = _call_llm_api("fk", "mb", "pb", 0.5, "http://fake.url.brain", mock_logger)
    assert content is None
    assert "Request failed: Erro de rede (brain)" in error


# --- Testes para generate_next_objective (que usa a _call_llm_api de brain.py) ---
@patch('agent.brain._call_llm_api') # Patch no _call_llm_api DENTRO de brain.py
def test_generate_next_objective_success(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Próximo objetivo simulado.", None)

    objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger, "/dummy/path", base_url="http://fake.url")
    assert objective == "Próximo objetivo simulado."
    mock_call_llm_api.assert_called_once()
    # Verificar args da chamada para _call_llm_api
    # A chamada em generate_next_objective usa keyword arguments
    args, kwargs = mock_call_llm_api.call_args
    assert not args # Assegurar que não foram passados argumentos posicionais
    assert kwargs['api_key'] == "key"
    assert kwargs['model'] == "model_light"
    assert "manifesto_atual" in kwargs['prompt']
    assert kwargs['temperature'] == 0.3
    assert kwargs['base_url'] == "http://fake.url"
    assert kwargs['logger'] == mock_logger

@patch('agent.brain._call_llm_api')
def test_generate_next_objective_api_error(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = (None, "Erro de API simulado")

    objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger, "/dummy/path")
    assert objective == "Analisar o estado atual do projeto e propor uma melhoria incremental" # Fallback
    mock_logger.error.assert_called_with("Erro ao gerar próximo objetivo: Erro de API simulado")

    @patch('agent.brain._call_llm_api')
    def test_generate_next_objective_empty_llm_response(mock_call_llm_api, mock_logger):
        mock_call_llm_api.return_value = ("", None) # Resposta de conteúdo vazia

        # Adicionando argumento faltante memory_summary
        objective = generate_next_objective(
            api_key="key",
            model="model_light", 
            current_manifest="manifesto_atual",
            logger=mock_logger,
            project_root_dir="/dummy/path",
            memory_summary=""
        )
        assert "Analisar" in objective # Verificação mais flexível
        mock_logger.warning.assert_called_with("Resposta vazia do LLM para próximo objetivo.")


@patch('agent.brain._call_llm_api')
def test_generate_next_objective_empty_manifest(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Objetivo para manifesto vazio", None)

    objective = generate_next_objective("key", "model", "", mock_logger, "/dummy/path") # Manifesto vazio
    assert objective == "Objetivo para manifesto vazio"

    # Verificar conceitos-chave no prompt
    args, kwargs = mock_call_llm_api.call_args
    prompt_arg = kwargs['prompt']
    assert "Planejador Estratégico" in prompt_arg
    assert "Hephaestus" in prompt_arg
    assert "objetivo" in prompt_arg

@patch('agent.brain._call_llm_api')
def test_generate_next_objective_with_memory(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Objetivo com memória.", None)
    memory_summary = "Lembre-se de X."
    objective = generate_next_objective("key", "model", "manifesto", mock_logger, "/dummy/path", memory_summary=memory_summary)
    assert objective == "Objetivo com memória."
    args, kwargs = mock_call_llm_api.call_args
    assert not args # Assegurar que não foram passados argumentos posicionais
    prompt_arg = kwargs['prompt'] # prompt é acessado via kwargs
    assert "HISTÓRICO RECENTE DO PROJETO E DO AGENTE" in prompt_arg
    assert memory_summary in prompt_arg


# --- Testes para generate_capacitation_objective (que usa a _call_llm_api de brain.py) ---
@patch('agent.brain._call_llm_api') # Patch no _call_llm_api DENTRO de brain.py
def test_generate_capacitation_objective_success(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Objetivo de capacitação simulado.", None)

    objective = generate_capacitation_objective("key", "model_cap", "Análise do engenheiro.", base_url="http://fake.url", logger=mock_logger)
    assert objective == "Objetivo de capacitação simulado."
    mock_call_llm_api.assert_called_once()
    args, kwargs = mock_call_llm_api.call_args
    assert args[0] == "key"
    assert args[1] == "model_cap"
    assert "Análise do Engenheiro que Requer Nova Capacidade" in args[2]
    assert "Análise do engenheiro." in args[2]
    assert args[3] == 0.3 # temperature
    assert args[4] == "http://fake.url"
    assert args[5] == mock_logger

@patch('agent.brain._call_llm_api')
def test_generate_capacitation_objective_api_error(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = (None, "Erro de API capacitação")
    objective = generate_capacitation_objective("key", "model", "Análise.", logger=mock_logger)
    assert objective == "Analisar a necessidade de capacitação e propor uma solução" # Fallback
    mock_logger.error.assert_called_with("Erro ao gerar objetivo de capacitação: Erro de API capacitação")

@patch('agent.brain._call_llm_api')
def test_generate_capacitation_objective_with_memory(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Objetivo de capacitação com memória.", None)
    memory_summary = "Capacitação X já foi tentada."
    objective = generate_capacitation_objective("key", "model", "Análise.", logger=mock_logger, memory_summary=memory_summary)
    assert objective == "Objetivo de capacitação com memória."
    args, kwargs = mock_call_llm_api.call_args
    prompt_arg = args[2]
    assert "HISTÓRICO RECENTE DO AGENTE" in prompt_arg
    assert memory_summary in prompt_arg

# --- Testes para generate_commit_message (que usa a _call_llm_api de brain.py - simulado) ---
# A função generate_commit_message no código fornecido está atualmente simulando a chamada LLM
# e construindo a mensagem heuristicamente. Portanto, não precisamos mockar _call_llm_api para ela.
def test_generate_commit_message_feat(mock_logger):
    objective = "Adicionar nova funcionalidade X"
    analysis = "Implementado X com sucesso."
    commit_msg = generate_commit_message("key", "model", analysis, objective, mock_logger)
    assert commit_msg.startswith("feat: ")
    assert "Adicionar nova funcionalidade X" in commit_msg

def test_generate_commit_message_fix(mock_logger):
    objective = "Corrigir bug na validação Y"
    analysis = "Validação Y agora funciona corretamente."
    commit_msg = generate_commit_message("key", "model", analysis, objective, mock_logger)
    assert commit_msg.startswith("fix: ")
    assert "Corrigir bug na validação Y" in commit_msg

def test_generate_commit_message_long_objective_truncates(mock_logger):
    objective = "Este é um objetivo muito longo que definitivamente excede o limite de setenta caracteres imposto pela heurística da função de mensagem de commit."
    analysis = "Implementado."
    commit_msg = generate_commit_message("key", "model", analysis, objective, mock_logger)
    assert len(commit_msg.split(":")[1].strip()) <= 70 + 3 # "..."
    assert commit_msg.endswith("...")


"""
Observações sobre os testes de `brain.py` após refatoração:
- Testes para `get_action_plan`, `get_maestro_decision`, e `parse_json_response` foram removidos
  deste arquivo, pois essas funções foram movidas para `agent/agents.py`.
  Os testes correspondentes estão agora em `tests/test_agents.py`.
- Testes para a cópia local de `_call_llm_api` em `brain.py` foram mantidos e adaptados
  para garantir que as funções restantes (`generate_next_objective`, etc.) usem-na corretamente.
- Testes para `generate_next_objective` e `generate_capacitation_objective` foram mantidos,
  assegurando que eles chamam a `_call_llm_api` interna de `brain.py`.
  Foram adicionados casos para testar o uso do `memory_summary`.
- Testes para `generate_commit_message` foram adicionados/mantidos, refletindo sua lógica atual
  (que é uma simulação/heurística, não uma chamada LLM real no código fornecido).
- O arquivo está mais enxuto, focando apenas nas responsabilidades que permaneceram em `brain.py`.
"""
