import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
import logging
import json
import asyncio

# Importar a função a ser testada (agora é async)
from agent.utils.llm_client import call_llm_api

# --- Fixtures ---
@pytest.fixture
def logger_fixture_llm_client(): # Nome da fixture atualizado para evitar conflitos
    logger = logging.getLogger("TestCallLlmApiAsync")
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture
def common_params_llm_client(logger_fixture_llm_client): # Nome da fixture atualizado
    return {
        "api_key": "test_api_key_llm",
        "model": "test_model_llm",
        "prompt": "test_prompt_llm",
        "temperature": 0.5,
        "base_url": "https://api.example.com/v1",
        "logger": logger_fixture_llm_client # Usando o logger da fixture
    }

# --- Testes ---
@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_success(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200

    async def mock_json_method():
        return {"choices": [{"message": {"content": "Test LLM response content"}}]}
    mock_response.json = mock_json_method
    mock_response.text = AsyncMock(return_value='Test LLM response content') # .text() também é async
    mock_response.raise_for_status = MagicMock() # não é async

    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)

    mock_aio_post.assert_called_once()
    args_call, kwargs_call = mock_aio_post.call_args
    assert args_call[0] == f"{common_params_llm_client['base_url']}/chat/completions"
    assert kwargs_call['json']['model'] == common_params_llm_client['model']
    assert kwargs_call['json']['messages'][0]['content'] == common_params_llm_client['prompt']
    assert kwargs_call['headers']['Authorization'] == f"Bearer {common_params_llm_client['api_key']}"

    assert content == "Test LLM response content"
    assert error is None

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_http_error(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 401

    async def mock_text_method(): return "Unauthorized access"
    mock_response.text = mock_text_method

    http_error = aiohttp.ClientResponseError(
        request_info=MagicMock(), history=(), status=401,
        message="Unauthorized", headers={}
    )
    mock_response.raise_for_status.side_effect = http_error

    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)

    mock_aio_post.assert_called_once()
    assert content is None
    assert error is not None
    assert "HTTP error occurred" in error
    assert "Status: 401" in error
    # A mensagem de erro de ClientResponseError é usada.
    # Se call_llm_api for atualizado para ler response.text() no except, esta asserção mudaria.
    assert "Message: Unauthorized" in error
    # Para incluir o corpo, a função call_llm_api precisaria ser ajustada para ler response.text() no bloco de exceção.
    # Exemplo de como seria se o corpo fosse incluído:
    # assert "Body: Unauthorized access" in error


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_client_connector_error(mock_aio_post, common_params_llm_client):
    mock_aio_post.side_effect = aiohttp.ClientConnectorError(MagicMock(), OSError("Network error"))

    content, error = await call_llm_api(**common_params_llm_client)

    mock_aio_post.assert_called_once()
    assert content is None
    assert error is not None
    assert "Request failed (ClientConnectorError)" in error

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_timeout_error(mock_aio_post, common_params_llm_client):
    mock_aio_post.side_effect = asyncio.TimeoutError("Request timed out")

    content, error = await call_llm_api(**common_params_llm_client)

    mock_aio_post.assert_called_once()
    assert content is None
    assert error is not None
    assert "Request timed out" in error

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_missing_choices(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200
    async def mock_json_method(): return {"error": "No choices here"}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()
    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)
    assert content is None
    assert error is not None
    assert "API response missing 'choices' key or 'choices' is empty" in error

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_empty_choices(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200
    async def mock_json_method(): return {"choices": []}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()
    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)
    assert content is None
    assert error is not None
    assert "API response missing 'choices' key or 'choices' is empty" in error

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_missing_message_in_choice(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200
    async def mock_json_method(): return {"choices": [{"no_message_here": "..."}]}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()
    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)
    assert content is None
    assert error is not None
    assert "API response 'choices'[0] missing 'message' key" in error

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_missing_content_in_message(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200
    async def mock_json_method(): return {"choices": [{"message": {"no_content_here": "..."}}]}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()
    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)
    assert content is None
    assert error is not None
    assert "API response 'message' missing 'content' key" in error

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_unexpected_json_structure_attr_error(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200
    # 'message' é uma string, não um dict, causará AttributeError em .get('content')
    async def mock_json_method(): return {"choices": [{"message": "not_a_dict"}]}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()
    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)
    assert content is None
    assert error is not None
    assert "Error parsing LLM response (AttributeError)" in error


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post', new_callable=AsyncMock)
async def test_call_llm_api_key_error_in_parsing(mock_aio_post, common_params_llm_client):
    mock_response = AsyncMock(spec=aiohttp.ClientResponse)
    mock_response.status = 200
    # 'content' está ausente dentro de 'message', o que deve ser pego pelo get com fallback,
    # mas se a lógica fosse diferente e acessasse diretamente, um KeyError poderia ocorrer.
    # A lógica atual com .get() deve retornar None para content, levando ao erro "missing 'content' key".
    async def mock_json_method(): return {"choices": [{"message": {"unexpected_key": "..."}}]}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()
    mock_aio_post.return_value.__aenter__.return_value = mock_response

    content, error = await call_llm_api(**common_params_llm_client)
    assert content is None
    assert error is not None
    assert "API response 'message' missing 'content' key" in error
