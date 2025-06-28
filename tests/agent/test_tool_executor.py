import pytest
from unittest.mock import patch, MagicMock # MagicMock pode precisar ser AsyncMock para alguns casos
import asyncio # Import asyncio
from agent.tool_executor import web_search, run_pytest, run_git_command, check_file_existence, run_in_sandbox
import sys # Para sys.executable
import os # Para os.path.exists em check_file_existence (se não for mockado)
from pathlib import Path

# Testes para web_search (que agora usa aiohttp)
@pytest.mark.asyncio
# O patch para aiohttp.ClientSession é mais complexo.
# Vamos mockar a função `web_search` no nível mais alto para estes testes iniciais,
# ou mockar `aiohttp.ClientSession().get()`
# Para simplificar, vamos mockar a chamada `session.get()` dentro de `web_search`.
@patch('aiohttp.ClientSession.get') # Patching aiohttp get
async def test_web_search_success(mock_aio_get):
    # Configurar mock para aiohttp
    mock_response = MagicMock() # Se o objeto response tiver métodos async, precisaremos de AsyncMock
    mock_response.status = 200 # aiohttp usa 'status', não 'status_code'

    # O método json() de aiohttp.ClientResponse é uma corrotina
    async def mock_json_method():
        return {
            "AbstractText": "Resultado abstrato.",
            "RelatedTopics": [{"Text": "Tópico Relacionado 1", "FirstURL": "https://exemplo.com/rel1"}],
            "Results": [{"Text": "Resultado Web 1", "FirstURL": "https://exemplo.com/web1"}]
        }
    mock_response.json = mock_json_method

    # raise_for_status() é um método síncrono em aiohttp.ClientResponse
    mock_response.raise_for_status = MagicMock()

    # O context manager `async with session.get(...) as response:` precisa ser mockado.
    # `mock_aio_get` será o mock de `session.get`. Ele precisa retornar um objeto
    # que possa ser usado em um `async with`, e esse objeto (o response mock)
    # deve ter os atributos e métodos esperados.

    # Criar um mock para o context manager de get
    mock_cm = MagicMock() # Pode precisar ser um AsyncContextManager mock
    mock_cm.__aenter__.return_value = mock_response
    mock_aio_get.return_value = mock_cm
        
    success, results = await web_search("test query")

    assert success
    assert "Resultado abstrato." in results
    assert "Tópico Relacionado 1" in results
    # Não esperamos "Resultado Web 1" porque AbstractText e RelatedTopics têm prioridade
    mock_aio_get.assert_called_once()


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_web_search_no_results(mock_aio_get):
    mock_response = MagicMock()
    mock_response.status = 200
    async def mock_json_method():
        return {"AbstractText": "", "RelatedTopics": [], "Results": []}
    mock_response.json = mock_json_method
    mock_response.raise_for_status = MagicMock()

    mock_cm = MagicMock()
    mock_cm.__aenter__.return_value = mock_response
    mock_aio_get.return_value = mock_cm

    success, results = await web_search("test query")

    assert success
    assert results == "Nenhum resultado principal encontrado para a pesquisa."

@pytest.mark.asyncio
@patch('aiohttp.ClientSession.get')
async def test_web_search_client_error(mock_aio_get):
    # Configurar mock para levantar aiohttp.ClientError
    mock_aio_get.side_effect = aiohttp.ClientError("Erro de cliente HTTP")

    success, results = await web_search("test query")

    assert not success
    assert "Erro na pesquisa web (ClientError): Erro de cliente HTTP" in results

@pytest.mark.asyncio
@patch('agent.tool_executor.run_async_subprocess')
async def test_run_pytest_success(mock_run_async_subprocess):
    mock_run_async_subprocess.return_value = (0, "Pytest stdout", "Pytest stderr")

    success, output = await run_pytest(test_dir="specific_tests/", cwd="/test/path")

    assert success
    assert "Pytest Command: " in output
    assert f"{sys.executable} -m pytest specific_tests/" in output
    assert "CWD: /test/path" in output
    assert "Exit Code: 0" in output
    assert "Stdout:\nPytest stdout" in output
    assert "Stderr:\nPytest stderr" in output
    mock_run_async_subprocess.assert_called_once_with([sys.executable, "-m", "pytest", "specific_tests/"], "/test/path")

@pytest.mark.asyncio
@patch('agent.tool_executor.run_async_subprocess')
async def test_run_pytest_failure(mock_run_async_subprocess):
    mock_run_async_subprocess.return_value = (1, "Some tests failed", "")

    success, output = await run_pytest() # Defaults

    assert not success
    assert "Exit Code: 1" in output
    assert "Stdout:\nSome tests failed" in output
    mock_run_async_subprocess.assert_called_once_with([sys.executable, "-m", "pytest", "tests/"], None)

@pytest.mark.asyncio
@patch('agent.tool_executor.run_async_subprocess')
async def test_run_git_command_success(mock_run_async_subprocess):
    mock_run_async_subprocess.return_value = (0, "Git stdout", "")
    git_cmd = ["git", "status"]

    success, output = await run_git_command(git_cmd)

    assert success
    assert "Comando: git status" in output
    assert "Exit Code: 0" in output
    assert "Stdout:\nGit stdout" in output
    mock_run_async_subprocess.assert_called_once_with(git_cmd)

@pytest.mark.asyncio
@patch('agent.tool_executor.run_async_subprocess')
async def test_run_git_command_failure(mock_run_async_subprocess):
    mock_run_async_subprocess.return_value = (128, "", "Git error")
    git_cmd = ["git", "commit", "-m", "fail"]

    success, output = await run_git_command(git_cmd)

    assert not success
    assert "Exit Code: 128" in output
    assert "Stderr:\nGit error" in output

@pytest.mark.asyncio
@patch('asyncio.to_thread') # Mocking to_thread para simular os.path.exists
async def test_check_file_existence_all_exist(mock_to_thread):
    mock_to_thread.return_value = True # Simula que os.path.exists retorna True
    files = ["file1.txt", "dir/file2.py"]

    success, message = await check_file_existence(files)

    assert success
    assert message == "Todos os arquivos especificados existem."
    # Verificar se to_thread foi chamado para cada arquivo
    assert mock_to_thread.call_count == len(files)
    mock_to_thread.assert_any_call(os.path.exists, "file1.txt")
    mock_to_thread.assert_any_call(os.path.exists, "dir/file2.py")


@pytest.mark.asyncio
@patch('asyncio.to_thread')
async def test_check_file_existence_some_missing(mock_to_thread):
    # Simular que o primeiro existe, o segundo não
    mock_to_thread.side_effect = [True, False]
    files = ["exists.txt", "missing.txt"]

    success, message = await check_file_existence(files)

    assert not success
    assert message == "Arquivo(s) não encontrado(s): missing.txt"
    assert mock_to_thread.call_count == len(files)

@pytest.mark.asyncio
async def test_check_file_existence_empty_list():
    success, message = await check_file_existence([])
    assert not success
    assert message == "Nenhum caminho de arquivo fornecido para verificação."

# Testes para run_in_sandbox são mais complexos devido à interação com subprocessos
# e monitoramento de recursos. Mockar run_async_subprocess é uma abordagem.
@pytest.mark.asyncio
@patch('agent.tool_executor.run_async_subprocess')
async def test_run_in_sandbox(mock_run_async_subprocess):
    # Gravar o tempo antes e depois da chamada para simular a passagem do tempo
    loop = asyncio.get_event_loop()
    start_time = loop.time()

    # Configurar o mock para run_async_subprocess
    mock_run_async_subprocess.return_value = (0, "Sandbox stdout", "Sandbox stderr")

    # Simular que a chamada a run_async_subprocess demora um pouco
    async def side_effect_for_subprocess(*args, **kwargs):
        await asyncio.sleep(0.1) # Simula o tempo de execução do subprocesso
        return (0, "Sandbox stdout", "Sandbox stderr")
    mock_run_async_subprocess.side_effect = side_effect_for_subprocess

    result = await run_in_sandbox("/tmp/sandbox", "test_objective")

    end_time = loop.time()

    assert result["exit_code"] == 0
    assert "Stdout:\nSandbox stdout" in result["output"]
    assert "Stderr:\nSandbox stderr" in result["output"]
    # Verificar se execution_time é razoável (ligeiramente maior que o sleep simulado)
    assert result["execution_time"] >= 0.1
    assert result["execution_time"] < (end_time - start_time + 0.05) # Uma margem pequena

    expected_cmd = [sys.executable, "main.py", "test_objective", "--benchmark", "--max-cycles=1"]
    mock_run_async_subprocess.assert_called_once_with(expected_cmd, "/tmp/sandbox")
