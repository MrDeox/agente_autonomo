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
    get_maestro_decision,
    parse_json_response # Adicionar a função importada
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

@patch('agent.brain._call_llm_api')
def test_generate_next_objective_success(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Próximo objetivo simulado.", None)

    objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger, base_url="http://fake.url")
    assert objective == "Próximo objetivo simulado."
    mock_call_llm_api.assert_called_once()
    # Verificar args da chamada para _call_llm_api
    args, kwargs = mock_call_llm_api.call_args
    assert args[0] == "key"              # api_key
    assert args[1] == "model_light"      # model
    assert "manifesto_atual" in args[2]  # prompt
    assert args[3] == 0.3                # temperature
    assert args[4] == "http://fake.url"  # base_url
    assert args[5] == mock_logger        # logger

@patch('agent.brain._call_llm_api')
def test_generate_next_objective_api_error(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = (None, "Erro de API simulado")

    objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger)
    assert objective == "Analisar o estado atual do projeto e propor uma melhoria incremental" # Fallback
    mock_logger.error.assert_called_with("Erro ao gerar próximo objetivo: Erro de API simulado")

@patch('agent.brain._call_llm_api')
def test_generate_next_objective_empty_llm_response(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("", None) # Resposta de conteúdo vazia

    objective = generate_next_objective("key", "model_light", "manifesto_atual", mock_logger)
    assert objective == "Analisar o estado atual do projeto e propor uma melhoria incremental" # Fallback
    mock_logger.warn.assert_called_with("Resposta vazia do LLM para próximo objetivo.")


@patch('agent.brain._call_llm_api')
def test_generate_next_objective_empty_manifest(mock_call_llm_api, mock_logger):
    mock_call_llm_api.return_value = ("Objetivo para manifesto vazio", None)

    objective = generate_next_objective("key", "model", "", mock_logger) # Manifesto vazio
    assert objective == "Objetivo para manifesto vazio"

    # Verificar se o prompt correto foi usado para manifesto vazio
    args, kwargs = mock_call_llm_api.call_args
    prompt_arg = args[2] # prompt é o terceiro argumento posicional
    assert "Este é o primeiro ciclo de execução" in prompt_arg


# --- Testes para generate_capacitation_objective ---

@patch('agent.brain._call_llm_api')
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

# --- Testes para get_maestro_decision ---

@patch('agent.brain._call_llm_api')
def test_get_maestro_decision_success(mock_call_llm_api, mock_logger):
    maestro_response_json_str = json.dumps({"strategy_key": "APPLY_AND_TEST"})
    # _call_llm_api retorna (content, error)
    mock_call_llm_api.return_value = (maestro_response_json_str, None)

    engineer_resp = {"analysis": "...", "patches_to_apply": []}
    config_data = {"validation_strategies": {"APPLY_AND_TEST": {}}}

    # Passar logger para get_maestro_decision
    decision_logs = get_maestro_decision("key", ["model1"], engineer_resp, config_data, logger=mock_logger)

    assert len(decision_logs) == 1
    attempt = decision_logs[0]
    assert attempt["success"] is True
    assert attempt["parsed_json"] == {"strategy_key": "APPLY_AND_TEST"}
    mock_call_llm_api.assert_called_once()
    args, kwargs = mock_call_llm_api.call_args
    assert args[1] == "model1" # model
    assert args[3] == 0.2     # temperature

@patch('agent.brain._call_llm_api')
def test_get_maestro_decision_api_error_then_success(mock_call_llm_api, mock_logger):
    maestro_response_model2_json_str = json.dumps({"strategy_key": "MODEL2_WINS"})

    # Configurar side_effect para simular falha no primeiro modelo, sucesso no segundo
    mock_call_llm_api.side_effect = [
        (None, "Erro API no modelo1"), # _call_llm_api retorna (content, error)
        (maestro_response_model2_json_str, None)
    ]

    engineer_resp = {}
    config_data = {"validation_strategies": {"MODEL2_WINS": {}}}
    model_list = ["model1_fails", "model2_works"]

    decision_logs = get_maestro_decision("key", model_list, engineer_resp, config_data, logger=mock_logger)

    assert len(decision_logs) == 2

    # Checar tentativa 1 (falha)
    assert decision_logs[0]["model"] == "model1_fails"
    assert decision_logs[0]["success"] is False
    assert "Erro da API ao obter decisão do Maestro (modelo model1_fails): Erro API no modelo1" in decision_logs[0]["raw_response"]

    # Checar tentativa 2 (sucesso)
    assert decision_logs[1]["model"] == "model2_works"
    assert decision_logs[1]["success"] is True
    assert decision_logs[1]["parsed_json"] == {"strategy_key": "MODEL2_WINS"}

    assert mock_call_llm_api.call_count == 2

@patch('agent.brain._call_llm_api')
def test_get_maestro_decision_parsing_error(mock_call_llm_api, mock_logger):
    # _call_llm_api retorna content OK, mas o content é JSON inválido
    mock_call_llm_api.return_value = ("json { invalido", None)

    decision_logs = get_maestro_decision("key", ["model1"], {}, {"validation_strategies": {}}, logger=mock_logger)
    assert len(decision_logs) == 1
    assert decision_logs[0]["success"] is False
    assert "Erro ao fazer parse da decisão do Maestro (modelo model1): Erro ao decodificar JSON" in decision_logs[0]["raw_response"]
    assert "json { invalido" in decision_logs[0]["raw_response"] # Checa se o conteúdo original está na msg

@patch('agent.brain._call_llm_api')
def test_get_maestro_decision_json_schema_invalid(mock_call_llm_api, mock_logger):
    # _call_llm_api retorna JSON válido, mas não tem a chave esperada "strategy_key"
    mock_call_llm_api.return_value = (json.dumps({"other_key": "val"}), None)

    decision_logs = get_maestro_decision("key", ["model1"], {}, {"validation_strategies": {}}, logger=mock_logger)
    assert len(decision_logs) == 1
    assert decision_logs[0]["success"] is False
    assert "JSON da decisão do Maestro (modelo model1) com formato inválido ou faltando 'strategy_key'" in decision_logs[0]["raw_response"]

# Os testes existentes para _call_llm_api e get_action_plan permanecem válidos.
# Os testes para parse_json_response também.
# Apenas os testes para as funções que foram refatoradas para usar _call_llm_api precisam de ajuste no mock.
# test_get_maestro_decision_capacitation_required, test_get_maestro_decision_invalid_json_response (já coberto por parsing_error),
# test_get_maestro_decision_json_missing_strategy_key (já coberto por json_schema_invalid),
# test_get_maestro_decision_cleans_code_block (a limpeza agora é em parse_json_response, _call_llm_api não limpa)
# test_get_maestro_decision_uses_multiple_models_on_failure (já coberto por api_error_then_success)
# Precisamos garantir que os testes de `get_maestro_decision` cubram a lógica de limpeza de `parse_json_response` indiretamente.

@patch('agent.brain._call_llm_api')
def test_get_maestro_decision_capacitation_required_via_call_llm(mock_call_llm_api, mock_logger):
    # Teste para garantir que CAPACITATION_REQUIRED funciona com a nova estrutura
    maestro_response_json_str = json.dumps({"strategy_key": "CAPACITATION_REQUIRED"})
    mock_call_llm_api.return_value = (maestro_response_json_str, None)

    engineer_resp = {"analysis": "Precisa de nova ferramenta X."}
    config_data = {"validation_strategies": {}}

    decision_logs = get_maestro_decision("key", ["model1"], engineer_resp, config_data, logger=mock_logger)
    assert decision_logs[0]["success"] is True
    assert decision_logs[0]["parsed_json"] == {"strategy_key": "CAPACITATION_REQUIRED"}

@patch('agent.brain._call_llm_api')
def test_get_maestro_decision_cleans_code_block_indirectly(mock_call_llm_api, mock_logger):
    # Testar que a limpeza feita por parse_json_response funciona quando chamada de get_maestro_decision
    json_with_codeblock = "```json\n{\"strategy_key\": \"CLEANED_MAESTRO\"}\n```"
    mock_call_llm_api.return_value = (json_with_codeblock, None) # _call_llm_api retorna o JSON sujo

    decision_logs = get_maestro_decision("key", ["model1"], {}, {"validation_strategies": {"CLEANED_MAESTRO": {}}}, logger=mock_logger)
    assert len(decision_logs) == 1
    attempt = decision_logs[0]
    assert attempt["success"] is True
    assert attempt["parsed_json"] == {"strategy_key": "CLEANED_MAESTRO"}
    # Verificar se o raw_response no log da tentativa é o JSON "sujo"
    assert attempt["raw_response"] == json_with_codeblock

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

# --- Testes para parse_json_response ---

def test_parse_json_response_valid_json(mock_logger):
    json_str = '{"key": "value", "number": 123}'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"key": "value", "number": 123}

def test_parse_json_response_with_markdown_block(mock_logger):
    json_str = '```json\n{"key": "value"}\n```'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"key": "value"}

def test_parse_json_response_with_markdown_block_no_json_tag(mock_logger):
    json_str = '```\n{"key": "value"}\n```'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"key": "value"}

def test_parse_json_response_with_text_before_and_after(mock_logger):
    json_str = 'Some text before\n{"key": "value", "nested": {"num": 1}}\nSome text after'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"key": "value", "nested": {"num": 1}}

def test_parse_json_response_empty_string(mock_logger):
    data, error = parse_json_response("", mock_logger)
    assert data is None
    assert "String de entrada vazia" in error
    mock_logger.error.assert_called_once()

def test_parse_json_response_whitespace_string(mock_logger):
    data, error = parse_json_response("   \n\t  ", mock_logger)
    assert data is None
    assert "String de entrada vazia" in error
    mock_logger.error.assert_called_once()

def test_parse_json_response_invalid_json(mock_logger):
    json_str = '{"key": "value", "invalid"}'
    data, error = parse_json_response(json_str, mock_logger)
    assert data is None
    assert "Erro ao decodificar JSON" in error
    mock_logger.error.assert_called_with(pytest.string_contains("Erro ao decodificar JSON: Expecting ':' delimiter"))


def test_parse_json_response_string_not_json_at_all(mock_logger):
    json_str = 'apenas uma string normal sem json'
    data, error = parse_json_response(json_str, mock_logger)
    assert data is None
    assert "Erro ao decodificar JSON" in error # Espera-se que falhe no json.loads
    # A mensagem exata pode variar dependendo da implementação do json.loads,
    # mas deve indicar um erro de decodificação.
    # Ex: "Expecting value: line 1 column 1 (char 0)"

def test_parse_json_response_with_control_chars(mock_logger):
    # Inclui um caractere de controle (BEL) que deve ser removido
    json_str = '{"key": "value\u0007", "number": 123}'
    clean_json_str = '{"key": "value", "number": 123}'
    # Simular que o char de controle está lá, mas o parser o remove
    # A lógica atual remove chars < 32 exceto \n \r \t. BEL é 7.

    # O teste aqui é que o JSON é parseado corretamente *apesar* do char
    # se a limpeza funcionar como esperado.
    # O JSON enviado para json.loads DEVE estar limpo.
    # A função parse_json_response faz a limpeza *antes* de json.loads.

    # A string original com o caractere de controle:
    original_with_control_char = '{"key": "value\u0007", "number": 123}'

    # O que esperamos que seja passado para json.loads depois da limpeza:
    # (Nota: a string 'value\u0007' no json.loads causaria erro se não limpa)
    # A limpeza deve remover \u0007
    expected_after_cleaning = '{"key": "value", "number": 123}'

    # Teste
    data, error = parse_json_response(original_with_control_char, mock_logger)
    assert error is None
    assert data == {"key": "value", "number": 123}

def test_parse_json_response_json_within_text_no_markdown(mock_logger):
    json_str = "Aqui está o JSON: {\"message\": \"Olá\"}. E algum texto depois."
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {"message": "Olá"}

def test_parse_json_response_multiple_json_objects_takes_first_valid_spanning(mock_logger):
    # A lógica atual pega do primeiro '{' ao último '}'
    # Então, se houver JSONs aninhados ou múltiplos que são tecnicamente um grande JSON, ele tentará parsear.
    # Se for tipo {"a":1}{"b":2}, ele pegará '{"a":1}{"b":2}' que é inválido.
    # Se for {"a":{"b":1}, "c":{"d":2}}, ele pega tudo.
    json_str = '{"outer": {"key1": "val1"}, "extra": "ignore this part"} {"key2": "val2"}'
    # Esperado: parseia '{"outer": {"key1": "val1"}, "extra": "ignore this part"} {"key2": "val2"}'
    # que é inválido.
    # A lógica atual de first_brace/last_brace pegaria tudo até o último '}'
    # '{"outer": {"key1": "val1"}, "extra": "ignore this part"} {"key2": "val2"}'
    # Isto é um JSON inválido.
    data, error = parse_json_response(json_str, mock_logger)
    assert data is None
    assert "Erro ao decodificar JSON" in error # Esperado falhar

    json_str_valid_outer = 'Content before {"key": "value", "obj": {"k": "v"}} and after'
    data_valid, error_valid = parse_json_response(json_str_valid_outer, mock_logger)
    assert error_valid is None
    assert data_valid == {"key": "value", "obj": {"k": "v"}}

def test_parse_json_response_no_json_object_in_string(mock_logger):
    json_str = "Não há nenhum objeto json aqui."
    data, error = parse_json_response(json_str, mock_logger)
    assert data is None
    assert "Erro ao decodificar JSON" in error # json.loads falhará

def test_parse_json_response_only_braces_empty_object(mock_logger):
    json_str = "{}"
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {}

def test_parse_json_response_braces_with_whitespace_empty_object(mock_logger):
    json_str = "  {  }  "
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data == {}

def test_parse_json_response_complex_nested_json_with_markdown_and_text(mock_logger):
    json_str = """Aqui está algum texto antes.
```json
{
  "name": "Complex Test",
  "version": 1.0,
  "details": {
    "owner": "TestUser",
    "settings": [
      {"id": "a", "value": true},
      {"id": "b", "value": null},
      {"id": "c", "value": [1, 2, "mixed"]}
    ],
    "description": "Um JSON aninhado e um pouco mais complexo para testar a extração. Inclui newlines \\n e tabs \\t."
  },
  "status": "active"
}
```
E algum texto depois.
"""
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    assert data["name"] == "Complex Test"
    assert data["details"]["owner"] == "TestUser"
    assert len(data["details"]["settings"]) == 3
    assert data["details"]["settings"][2]["value"][2] == "mixed"
    assert "newlines \\n e tabs \\t" in data["details"]["description"]

def test_parse_json_response_logger_is_none(capfd): # capfd para capturar prints
    json_str = '{"key": "value"}'
    data, error = parse_json_response(json_str, None) # Passa None como logger
    assert error is None
    assert data == {"key": "value"}

    # Verificar se não houve erros de logger e se os prints de fallback funcionam
    json_str_empty = ""
    data_empty, error_empty = parse_json_response(json_str_empty, None)
    assert data_empty is None
    assert "String de entrada vazia" in error_empty
    out, err = capfd.readouterr() # Captura o print
    assert "parse_json_response: Recebeu string vazia ou apenas com espaços." in out

    json_str_invalid = '{"key": "value", invalid}'
    data_invalid, error_invalid = parse_json_response(json_str_invalid, None)
    assert data_invalid is None
    assert "Erro ao decodificar JSON" in error_invalid
    out, err = capfd.readouterr() # Captura o print de erro
    assert "parse_json_response: Erro ao decodificar JSON: Expecting ':' delimiter" in out

def test_parse_json_response_ends_unexpectedly(mock_logger):
    json_str = '{"key": "value", "unterminated": {"a": 1' # JSON não termina corretamente
    data, error = parse_json_response(json_str, mock_logger)
    assert data is None
    assert "Erro ao decodificar JSON" in error
    # A mensagem exata pode variar, mas deve indicar um fim inesperado ou malformação.
    # e.g. "json.decoder.JSONDecodeError: Expecting '}' delimiter: line 1 column 39 (char 38)"

def test_parse_json_response_json_starts_with_array(mock_logger):
    # A função espera um objeto JSON (dicionário), não um array no nível raiz por causa de Dict[str, Any]
    # Mas json.loads pode parsear um array. A tipagem de retorno é Dict.
    # A implementação atual de parse_json_response não impõe que seja um Dict, apenas json.loads.
    # Se json.loads retornar uma lista, a função retornará essa lista.
    # Isso pode ser um problema para os chamadores que esperam Dict.
    # Por agora, testaremos o comportamento atual.
    json_str = '[1, 2, {"key": "value"}]'
    data, error = parse_json_response(json_str, mock_logger)
    assert error is None
    # A tipagem de retorno é Tuple[Optional[Dict[str, Any]], Optional[str]]
    # Se data for uma lista, isso tecnicamente não corresponde ao Dict.
    # No entanto, json.loads(['...', '[1,2,3]']) -> [1,2,3]
    # O type hint da função é Dict, mas a implementação permite List.
    # Vamos considerar isso um ponto a ser observado. Por enquanto, o teste reflete a implementação.
    assert isinstance(data, list)
    assert data == [1, 2, {"key": "value"}]

    # Para ser estrito com o Dict, a função parse_json_response precisaria de uma checagem adicional:
    # parsed = json.loads(...)
    # if not isinstance(parsed, dict):
    #    return None, "JSON não é um objeto/dicionário."
    # Por ora, o teste passa com o comportamento atual.
