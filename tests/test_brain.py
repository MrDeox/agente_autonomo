# tests/test_brain.py
import pytest
import json
import requests
import logging
from unittest.mock import MagicMock, patch # Para mockar requests.post e o logger

from agent.brain import (
    _call_llm_api,
    get_action_plan,
    generate_next_objective,
    generate_capacitation_objective,
    get_maestro_decision
)

# Logger mockado que pode ser passado para as funções do cérebro
@pytest.fixture
def mock_logger():
    logger = MagicMock(spec=logging.Logger)
    # Configurar métodos de log para não fazer nada ou retornar algo, se necessário
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warn = MagicMock()
    logger.error = MagicMock()
    return logger

# --- Testes para _call_llm_api (função auxiliar) ---
# Embora seja uma função interna, testá-la pode simplificar os testes das funções públicas.

@patch('agent.brain.requests.post')
def test_call_llm_api_success(mock_post, mock_logger):
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
    # Aqui poderíamos verificar os args da chamada a mock_post se quiséssemos ser mais granulares

@patch('agent.brain.requests.post')
def test_call_llm_api_request_exception(mock_post, mock_logger):
    mock_post.side_effect = requests.exceptions.RequestException("Erro de rede simulado")

    content, error = _call_llm_api("fake_key", "model_x", "prompt_y", 0.5, "http://fake.url", mock_logger)

    assert content is None
    assert "Request failed: Erro de rede simulado" in error
    mock_logger.debug.assert_not_called() # Não deve logar API Response se falhar antes

@patch('agent.brain.requests.post')
def test_call_llm_api_http_error(mock_post, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Erro interno do servidor"
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    mock_post.return_value = mock_response

    content, error = _call_llm_api("fake_key", "model_x", "prompt_y", 0.5, "http://fake.url", mock_logger)

    assert content is None
    assert "Status: 500, Response: Erro interno do servidor" in error

@patch('agent.brain.requests.post')
def test_call_llm_api_missing_choices_key(mock_post, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_key": "valor"} # Sem "choices"
    mock_post.return_value = mock_response

    content, error = _call_llm_api("fake_key", "model_x", "prompt_y", 0.5, "http://fake.url", mock_logger)

    assert content is None
    assert "API response missing 'choices' key" in error

@patch('agent.brain.requests.post')
def test_call_llm_api_key_error_in_response_structure(mock_post, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Resposta com 'choices' mas estrutura interna errada
    mock_response.json.return_value = {"choices": [{"wrong_key": "data"}]}
    mock_post.return_value = mock_response

    content, error = _call_llm_api("fake_key", "model_x", "prompt_y", 0.5, "http://fake.url", mock_logger)

    assert content is None
    assert "KeyError: 'message'" in error # Espera 'message' dentro de 'choices'[0]

# --- Testes para get_action_plan ---

@patch('agent.brain._call_llm_api')
def test_get_action_plan_success(mock_call_llm, mock_logger):
    valid_patches_json_str = json.dumps({
        "analysis": "Análise detalhada aqui.",
        "patches_to_apply": [
            {"file_path": "file1.py", "operation": "INSERT", "content": "import new_module"},
            {"file_path": "file2.txt", "operation": "REPLACE", "block_to_replace": "old", "content": "new"}
        ]
    })
    mock_call_llm.return_value = (valid_patches_json_str, None)

    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)

    assert error is None
    assert plan_data is not None
    assert plan_data["analysis"] == "Análise detalhada aqui."
    assert len(plan_data["patches_to_apply"]) == 2
    assert plan_data["patches_to_apply"][0]["file_path"] == "file1.py"
    mock_call_llm.assert_called_once()
    # O prompt usado para chamar _call_llm_api também pode ser verificado se necessário

@patch('agent.brain._call_llm_api')
def test_get_action_plan_llm_error(mock_call_llm, mock_logger):
    mock_call_llm.return_value = (None, "Erro de API simulado")

    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)

    assert plan_data is None
    assert "Erro ao chamar LLM para plano de patches: Erro de API simulado" in error

@patch('agent.brain._call_llm_api')
def test_get_action_plan_empty_llm_response(mock_call_llm, mock_logger):
    mock_call_llm.return_value = ("", None) # Resposta vazia

    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)

    assert plan_data is None
    assert "Resposta vazia do LLM para plano de patches" in error

@patch('agent.brain._call_llm_api')
def test_get_action_plan_malformed_json(mock_call_llm, mock_logger):
    mock_call_llm.return_value = ("{json_invalido", None)

    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)

    assert plan_data is None
    assert "Erro ao decodificar JSON do plano de patches" in error

@patch('agent.brain._call_llm_api')
def test_get_action_plan_json_missing_patches_key(mock_call_llm, mock_logger):
    invalid_json_str = json.dumps({"analysis": "sem patches"})
    mock_call_llm.return_value = (invalid_json_str, None)

    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)

    assert plan_data is None
    assert "JSON do plano de patches não contém a chave 'patches_to_apply'" in error

@patch('agent.brain._call_llm_api')
def test_get_action_plan_patches_not_a_list(mock_call_llm, mock_logger):
    invalid_json_str = json.dumps({"analysis": "ok", "patches_to_apply": "não é uma lista"})
    mock_call_llm.return_value = (invalid_json_str, None)

    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)

    assert plan_data is None
    assert "patches_to_apply' ou não é uma lista" in error # Mensagem atual

@patch('agent.brain._call_llm_api')
def test_get_action_plan_invalid_patch_structure_missing_keys(mock_call_llm, mock_logger):
    # Patch sem file_path
    invalid_patches_json_str = json.dumps({
        "analysis": "Análise",
        "patches_to_apply": [{"operation": "INSERT", "content": "..."}]
    })
    mock_call_llm.return_value = (invalid_patches_json_str, None)
    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)
    assert plan_data is None
    assert "não tem 'file_path' ou 'operation'" in error

    # Patch INSERT sem content
    invalid_patches_json_str_2 = json.dumps({
        "analysis": "Análise",
        "patches_to_apply": [{"file_path": "f.py", "operation": "INSERT"}]
    })
    mock_call_llm.return_value = (invalid_patches_json_str_2, None)
    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)
    assert plan_data is None
    assert "não tem 'content'" in error

@patch('agent.brain._call_llm_api')
def test_get_action_plan_cleans_json_code_block(mock_call_llm, mock_logger):
    json_with_codeblock = """
```json
{
  "analysis": "Wrapped in code block.",
  "patches_to_apply": [
    {"file_path": "a.py", "operation": "INSERT", "content": "pass"}
  ]
}
```
    """
    mock_call_llm.return_value = (json_with_codeblock, None)
    plan_data, error = get_action_plan("key", "model", "objetivo", "manifesto", mock_logger)
    assert error is None
    assert plan_data is not None
    assert plan_data["analysis"] == "Wrapped in code block."
    assert len(plan_data["patches_to_apply"]) == 1

# --- Testes para generate_next_objective ---

@patch('agent.brain._call_llm_api') # Mock _call_llm_api que é usado internamente por generate_next_objective
def test_generate_next_objective_success(mock_call_llm, mock_logger):
    mock_call_llm.return_value = ("Próximo objetivo simulado.", None)

    # generate_next_objective agora chama requests.post diretamente, então precisamos mockar isso.
    # Ou, refatorar generate_next_objective para usar _call_llm_api consistentemente.
    # Por agora, vou mockar requests.post para esta função.
    with patch('agent.brain.requests.post') as mock_post_direct:
        mock_response_direct = MagicMock()
        mock_response_direct.status_code = 200
        mock_response_direct.json.return_value = {
            "choices": [{"message": {"content": "Próximo objetivo simulado."}}]
        }
        mock_post_direct.return_value = mock_response_direct

        objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger)
        assert objective == "Próximo objetivo simulado."
        mock_post_direct.assert_called_once()

@patch('agent.brain.requests.post') # Mockar requests.post diretamente
def test_generate_next_objective_api_error(mock_post_direct, mock_logger):
    mock_post_direct.side_effect = requests.exceptions.RequestException("Erro de API")

    objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger)
    # A função atualmente printa o erro e retorna um objetivo padrão.
    assert objective == "Analisar o estado atual do projeto e propor uma melhoria incremental"
    # Poderíamos usar capsys para verificar o print, ou melhor, fazer o logger ser usado.
    # A função original usa print(), não logger.error(). Isso pode ser um ponto de melhoria.

@patch('agent.brain.requests.post')
def test_generate_next_objective_empty_manifest(mock_post_direct, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Objetivo para manifesto vazio"}}]}
    mock_post_direct.return_value = mock_response

    objective = generate_next_objective("key", "model", "", mock_logger) # Manifesto vazio
    assert objective == "Objetivo para manifesto vazio"

    # Verificar se o prompt correto foi usado para manifesto vazio
    args, kwargs = mock_post_direct.call_args
    payload = kwargs['json']
    assert "Este é o primeiro ciclo de execução" in payload['messages'][0]['content']


# --- Testes para generate_capacitation_objective --- (similar a generate_next_objective)

@patch('agent.brain.requests.post')
def test_generate_capacitation_objective_success(mock_post_direct, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "Objetivo de capacitação simulado."}}]}
    mock_post_direct.return_value = mock_response

    objective = generate_capacitation_objective("key", "model", "Análise do engenheiro.", mock_logger)
    assert objective == "Objetivo de capacitação simulado."
    mock_post_direct.assert_called_once()
    # Verificar prompt
    args, kwargs = mock_post_direct.call_args
    payload = kwargs['json']
    assert "Análise do Engenheiro que Requer Nova Capacidade" in payload['messages'][0]['content']
    assert "Análise do engenheiro." in payload['messages'][0]['content']

# --- Testes para get_maestro_decision ---

@patch('agent.brain.requests.post')
def test_get_maestro_decision_success(mock_post_direct, mock_logger):
    maestro_response_json_str = json.dumps({"strategy_key": "APPLY_AND_TEST"})

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": maestro_response_json_str}}]}
    mock_post_direct.return_value = mock_response

    engineer_resp = {"analysis": "...", "patches_to_apply": []}
    config_data = {"validation_strategies": {"APPLY_AND_TEST": {}}}

    decision_logs = get_maestro_decision("key", ["model1"], engineer_resp, config_data)

    assert len(decision_logs) == 1
    attempt = decision_logs[0]
    assert attempt["success"] is True
    assert attempt["parsed_json"] == {"strategy_key": "APPLY_AND_TEST"}

@patch('agent.brain.requests.post')
def test_get_maestro_decision_capacitation_required(mock_post_direct, mock_logger):
    maestro_response_json_str = json.dumps({"strategy_key": "CAPACITATION_REQUIRED"})
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": maestro_response_json_str}}]}
    mock_post_direct.return_value = mock_response

    engineer_resp = {"analysis": "Precisa de nova ferramenta X."} # Simula necessidade
    config_data = {"validation_strategies": {}} # Nenhuma estratégia, mas CAPACITATION_REQUIRED é sempre válido

    decision_logs = get_maestro_decision("key", ["model1"], engineer_resp, config_data)
    assert decision_logs[0]["success"] is True
    assert decision_logs[0]["parsed_json"] == {"strategy_key": "CAPACITATION_REQUIRED"}


@patch('agent.brain.requests.post')
def test_get_maestro_decision_invalid_json_response(mock_post_direct, mock_logger):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": "json { invalido"}}]}
    mock_post_direct.return_value = mock_response

    decision_logs = get_maestro_decision("key", ["model1"], {}, {"validation_strategies": {}})
    assert decision_logs[0]["success"] is False
    assert "Erro na decisão do Maestro: Expecting property name enclosed in double quotes" in decision_logs[0]["raw_response"] # ou similar

@patch('agent.brain.requests.post')
def test_get_maestro_decision_json_missing_strategy_key(mock_post_direct, mock_logger):
    maestro_response_json_str = json.dumps({"other_key": "valor"}) # Sem strategy_key
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": maestro_response_json_str}}]}
    mock_post_direct.return_value = mock_response

    decision_logs = get_maestro_decision("key", ["model1"], {}, {"validation_strategies": {}})
    assert decision_logs[0]["success"] is False
    assert "Invalid JSON format or missing strategy_key" in decision_logs[0]["raw_response"]

@patch('agent.brain.requests.post')
def test_get_maestro_decision_cleans_code_block(mock_post_direct, mock_logger):
    json_with_codeblock = "```json\n{\"strategy_key\": \"CLEANED\"}\n```"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"choices": [{"message": {"content": json_with_codeblock}}]}
    mock_post_direct.return_value = mock_response

    decision_logs = get_maestro_decision("key", ["model1"], {}, {"validation_strategies": {"CLEANED": {}}})
    assert decision_logs[0]["success"] is True
    assert decision_logs[0]["parsed_json"] == {"strategy_key": "CLEANED"}

@patch('agent.brain.requests.post')
def test_get_maestro_decision_uses_multiple_models_on_failure(mock_post_direct, mock_logger):
    # Primeira chamada falha (ex: erro de API), segunda funciona
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"choices": [{"message": {"content": "{\"strategy_key\": \"MODEL2_SUCCESS\"}"}}]}

    # Simular falha na primeira chamada, sucesso na segunda
    mock_post_direct.side_effect = [
        requests.exceptions.Timeout("Timeout no modelo 1"),
        mock_response_success
    ]

    decision_logs = get_maestro_decision("key", ["model1_fails", "model2_works"], {}, {"validation_strategies": {"MODEL2_SUCCESS":{}}})

    assert len(decision_logs) == 2
    assert decision_logs[0]["success"] is False
    assert "model1_fails" == decision_logs[0]["model"]
    assert "Erro na decisão do Maestro: Timeout no modelo 1" in decision_logs[0]["raw_response"]

    assert decision_logs[1]["success"] is True
    assert "model2_works" == decision_logs[1]["model"]
    assert decision_logs[1]["parsed_json"] == {"strategy_key": "MODEL2_SUCCESS"}

    assert mock_post_direct.call_count == 2

"""
Observações sobre os testes de `brain`:
- Uso extensivo de `@patch` para mockar `requests.post` (para funções que o chamam diretamente)
  e `_call_llm_api` (para funções que usam o helper).
- `mock_logger` é uma fixture para fornecer um logger mockado.
- Testes cobrem caminhos de sucesso e vários tipos de erro para cada função:
    - Erros de API (rede, HTTP).
    - Respostas LLM malformadas ou com estrutura inesperada.
    - JSON inválido ou com chaves faltando.
- Testada a lógica de limpeza de blocos de código JSON.
- Testada a lógica de fallback de múltiplos modelos em `get_maestro_decision`.
- Alguns testes verificam o prompt enviado ao LLM (indiretamente, pela lógica da função).
- Pontos de melhoria no código original identificados:
    - `generate_next_objective` e `generate_capacitation_objective` usam `print()` para erros em vez de `logger.error()`.
    - Consistência no uso de `_call_llm_api` por todas as funções que interagem com LLM simplificaria o mocking.
"""
