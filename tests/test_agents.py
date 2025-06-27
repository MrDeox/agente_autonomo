import pytest
import json
import logging
from unittest.mock import MagicMock, patch
import requests

from agent.agents import ArchitectAgent, MaestroAgent, _call_llm_api, parse_json_response

# Logger mockado que pode ser passado para as funções do cérebro
@pytest.fixture
def mock_logger():
    logger = MagicMock(spec=logging.Logger)
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warn = MagicMock()
    logger.error = MagicMock()
    return logger

# --- Testes para _call_llm_api (copiado para agent.agents) ---
@patch('agent.agents.requests.post')
def test_agents_call_llm_api_success(mock_post, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Resposta LLM simulada"}}]
    }
    mock_post.return_value = mock_response

    content, error = _call_llm_api("fake_key", "model_x", "prompt_y", 0.5, "http://fake.url", mock_logger)

    assert content == "Resposta LLM simulada"
    assert error is None
    mock_post.assert_called_once()

@patch('agent.agents.requests.post')
def test_agents_call_llm_api_request_exception(mock_post, mock_logger):
    mock_post.side_effect = requests.exceptions.RequestException("Erro de rede simulado")
    content, error = _call_llm_api("fake_key", "model_x", "prompt_y", 0.5, "http://fake.url", mock_logger)
    assert content is None
    assert "Request failed: Erro de rede simulado" in error

# --- Testes para parse_json_response (copiado para agent.agents) ---
def test_agents_parse_json_response_valid_json(mock_logger):
    json_str = '{"key": "value", "number": 123}'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"key": "value", "number": 123}

def test_agents_parse_json_response_with_markdown_block(mock_logger):
    json_str = '```json\n{"key": "value"}\n```'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"key": "value"}

def test_agents_parse_json_response_invalid_json(mock_logger):
    json_str = '{"key": "value", "invalid"}'
    data, error = parse_json_response(json_str, mock_logger)
    assert data is None
    assert "Erro ao decodificar JSON" in error

# --- Testes para ArchitectAgent ---
@patch('agent.agents._call_llm_api')
def test_architect_plan_action_success(mock_call_llm, mock_logger):
    valid_patches_json_str = json.dumps({
        "analysis": "Análise detalhada aqui.",
        "patches_to_apply": [
            {"file_path": "file1.py", "operation": "INSERT", "content": "import new_module"},
            {"file_path": "file2.txt", "operation": "REPLACE", "block_to_replace": "old", "content": "new"}
        ]
    })
    mock_call_llm.return_value = (valid_patches_json_str, None)
    architect = ArchitectAgent("key", "model_arch", mock_logger)
    plan_data, error = architect.plan_action("objetivo", "manifesto")

    assert error is None
    assert plan_data is not None
    assert plan_data["analysis"] == "Análise detalhada aqui."
    assert len(plan_data["patches_to_apply"]) == 2
    mock_call_llm.assert_called_once()
    # Verificar se o prompt contém o objetivo e o manifesto
    args, kwargs = mock_call_llm.call_args
    prompt_arg = args[2] # prompt é o terceiro argumento posicional
    assert "objetivo" in prompt_arg
    assert "manifesto" in prompt_arg


@patch('agent.agents._call_llm_api')
def test_architect_plan_action_llm_error(mock_call_llm, mock_logger):
    mock_call_llm.return_value = (None, "Erro de API simulado")
    architect = ArchitectAgent("key", "model_arch", mock_logger)
    plan_data, error = architect.plan_action("objetivo", "manifesto")

    assert plan_data is None
    assert "Erro ao chamar LLM para plano de patches: Erro de API simulado" in error

@patch('agent.agents._call_llm_api')
def test_architect_plan_action_empty_llm_response(mock_call_llm, mock_logger):
    mock_call_llm.return_value = ("", None) # Resposta vazia
    architect = ArchitectAgent("key", "model_arch", mock_logger)
    plan_data, error = architect.plan_action("objetivo", "manifesto")
    assert plan_data is None
    assert "Resposta vazia do LLM para plano de patches" in error


@patch('agent.agents._call_llm_api')
def test_architect_plan_action_malformed_json(mock_call_llm, mock_logger):
    mock_call_llm.return_value = ("{json_invalido", None)
    architect = ArchitectAgent("key", "model_arch", mock_logger)
    plan_data, error = architect.plan_action("objetivo", "manifesto")

    assert plan_data is None
    assert "Erro ao fazer parse do JSON do plano de patches: Erro ao decodificar JSON" in error # Erro de parse_json_response

@patch('agent.agents._call_llm_api')
def test_architect_plan_action_json_missing_patches_key(mock_call_llm, mock_logger):
    invalid_json_str = json.dumps({"analysis": "sem patches"})
    mock_call_llm.return_value = (invalid_json_str, None)
    architect = ArchitectAgent("key", "model_arch", mock_logger)
    plan_data, error = architect.plan_action("objetivo", "manifesto")

    assert plan_data is None
    assert "JSON do plano de patches inválido ou não contém a chave 'patches_to_apply' como uma lista." in error


@patch('agent.agents._call_llm_api')
def test_architect_plan_action_invalid_patch_structure(mock_call_llm, mock_logger):
    # Patch INSERT sem content
    invalid_patches_json_str = json.dumps({
        "analysis": "Análise",
        "patches_to_apply": [{"file_path": "f.py", "operation": "INSERT"}] # Falta "content"
    })
    mock_call_llm.return_value = (invalid_patches_json_str, None)
    architect = ArchitectAgent("key", "model_arch", mock_logger)
    plan_data, error = architect.plan_action("objetivo", "manifesto")
    assert plan_data is None
    assert "não tem 'content'" in error


# --- Testes para MaestroAgent ---
@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_success(mock_call_llm, mock_logger):
    maestro_response_json_str = json.dumps({"strategy_key": "APPLY_AND_TEST"})
    mock_call_llm.return_value = (maestro_response_json_str, None)

    config_data = {"validation_strategies": {"APPLY_AND_TEST": {}}}
    maestro = MaestroAgent("key", ["model_maestro"], config_data, mock_logger)
    action_plan = {"analysis": "...", "patches_to_apply": []}

    decision_logs = maestro.choose_strategy(action_plan)

    assert len(decision_logs) == 1
    attempt = decision_logs[0]
    assert attempt["success"] is True
    assert attempt["parsed_json"] == {"strategy_key": "APPLY_AND_TEST"}
    mock_call_llm.assert_called_once()
    args, kwargs = mock_call_llm.call_args
    prompt_arg = args[2]
    assert json.dumps(action_plan, ensure_ascii=False, indent=2) in prompt_arg # Verificar se o plano de ação está no prompt

@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_api_error_then_success(mock_call_llm, mock_logger):
    maestro_response_model2_json_str = json.dumps({"strategy_key": "MODEL2_WINS"})
    mock_call_llm.side_effect = [
        (None, "Erro API no modelo1"),
        (maestro_response_model2_json_str, None)
    ]

    config_data = {"validation_strategies": {"MODEL2_WINS": {}}}
    model_list = ["model1_fails", "model2_works"]
    maestro = MaestroAgent("key", model_list, config_data, mock_logger)

    decision_logs = maestro.choose_strategy({})

    assert len(decision_logs) == 2
    assert decision_logs[0]["success"] is False
    assert "Erro da API (modelo model1_fails): Erro API no modelo1" in decision_logs[0]["raw_response"]
    assert decision_logs[1]["success"] is True
    assert decision_logs[1]["parsed_json"] == {"strategy_key": "MODEL2_WINS"}
    assert mock_call_llm.call_count == 2

@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_parsing_error(mock_call_llm, mock_logger):
    mock_call_llm.return_value = ("json { invalido", None)
    maestro = MaestroAgent("key", ["model1"], {"validation_strategies": {}}, mock_logger)
    decision_logs = maestro.choose_strategy({})

    assert len(decision_logs) == 1
    assert decision_logs[0]["success"] is False
    assert "Erro ao fazer parse (modelo model1): Erro ao decodificar JSON" in decision_logs[0]["raw_response"]

@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_json_schema_invalid(mock_call_llm, mock_logger):
    mock_call_llm.return_value = (json.dumps({"other_key": "val"}), None)
    maestro = MaestroAgent("key", ["model1"], {"validation_strategies": {}}, mock_logger)
    decision_logs = maestro.choose_strategy({})
    assert len(decision_logs) == 1
    assert decision_logs[0]["success"] is False
    assert "JSON com formato inválido ou faltando 'strategy_key' (modelo model1)" in decision_logs[0]["raw_response"]

@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_capacitation_required(mock_call_llm, mock_logger):
    maestro_response_json_str = json.dumps({"strategy_key": "CAPACITATION_REQUIRED"})
    mock_call_llm.return_value = (maestro_response_json_str, None)
    maestro = MaestroAgent("key", ["model1"], {"validation_strategies": {}}, mock_logger)
    decision_logs = maestro.choose_strategy({})

    assert decision_logs[0]["success"] is True
    assert decision_logs[0]["parsed_json"] == {"strategy_key": "CAPACITATION_REQUIRED"}

@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_web_search_required(mock_call_llm, mock_logger):
    """Test that MaestroAgent can return WEB_SEARCH_REQUIRED strategy"""
    maestro_response_json_str = json.dumps({"strategy_key": "WEB_SEARCH_REQUIRED"})
    mock_call_llm.return_value = (maestro_response_json_str, None)
    maestro = MaestroAgent("key", ["model1"], {"validation_strategies": {}}, mock_logger)
    decision_logs = maestro.choose_strategy({})

    assert decision_logs[0]["success"] is True
    assert decision_logs[0]["parsed_json"] == {"strategy_key": "WEB_SEARCH_REQUIRED"}
@patch('agent.agents._call_llm_api')
def test_maestro_choose_strategy_with_memory_summary(mock_call_llm, mock_logger):
    maestro_response_json_str = json.dumps({"strategy_key": "STRATEGY_WITH_MEMORY"})
    mock_call_llm.return_value = (maestro_response_json_str, None)

    config_data = {"validation_strategies": {"STRATEGY_WITH_MEMORY": {}}}
    maestro = MaestroAgent("key", ["model_mem"], config_data, mock_logger)
    memory_summary = "Recentemente, a estratégia X falhou."

    decision_logs = maestro.choose_strategy({}, memory_summary=memory_summary)

    assert decision_logs[0]["success"] is True
    mock_call_llm.assert_called_once()
    args, kwargs = mock_call_llm.call_args
    prompt_arg = args[2]
    assert "[HISTÓRICO RECENTE (OBJETIVOS E ESTRATÉGIAS USADAS)]" in prompt_arg
    assert memory_summary in prompt_arg
    assert "STRATEGY_WITH_MEMORY" == decision_logs[0]["parsed_json"]["strategy_key"]
