import pytest
import asyncio # Para testes async
from unittest.mock import MagicMock, patch # mock_open não é necessário com aiofiles
from pathlib import Path
import os # Para os.path.exists (via asyncio.to_thread)

# Importar a classe a ser testada
from agent.validation_steps.pytest_new_file_validator import PytestNewFileValidator
# Importar a função mockada (run_pytest é async)
from agent.tool_executor import run_pytest as async_run_pytest


@pytest.fixture
def mock_logger():
    logger = MagicMock()
    # Configurar todos os métodos de log para serem MagicMock também
    for level in ['info', 'debug', 'warning', 'error', 'critical']:
        setattr(logger, level, MagicMock())
    return logger

@pytest.fixture
def validator_instance(mock_logger, tmp_path):
    return PytestNewFileValidator(
        logger=mock_logger,
        base_path=str(tmp_path),
        patches_to_apply=[],
        use_sandbox=True
    )

# Mock para a função async run_pytest
async def mock_async_run_pytest_function(test_dir, cwd, success_status=True, details_message="Pytest async passed"):
    # Simula o comportamento de run_pytest
    return success_status, details_message

@pytest.mark.asyncio
# Mockear a função run_pytest importada no módulo do validador
@patch('agent.validation_steps.pytest_new_file_validator.run_pytest')
@patch('asyncio.to_thread') # Para mockar a chamada os.path.exists
async def test_pytest_new_file_validator_success(mock_asyncio_to_thread, mock_run_pytest_patched, validator_instance, tmp_path):
    test_file_path_str = "tests/new_module/test_new_feature.py"
    validator_instance.patches_to_apply = [{
        "file_path": test_file_path_str, "operation": "REPLACE",
        "block_to_replace": None, "content": "..."
    }]

    mock_asyncio_to_thread.return_value = True # Simula que o arquivo existe
    mock_run_pytest_patched.return_value = (True, f"Pytest passed for {test_file_path_str}.\n1 test passed")

    success, reason, message = await validator_instance.execute()

    assert success is True
    assert reason == "PYTEST_NEW_FILE_PASSED"
    assert f"Pytest passed for {test_file_path_str}" in message

    # Verificar se run_pytest foi chamado corretamente
    # O primeiro argumento para run_pytest é test_dir, o segundo é cwd
    mock_run_pytest_patched.assert_called_once_with(test_dir=test_file_path_str, cwd=str(tmp_path))
    # Verificar se asyncio.to_thread foi chamado para Path.exists
    # A forma de verificar a chamada a `asyncio.to_thread(target_file_path.exists)`
    # pode ser um pouco mais complexa se você precisar verificar o argumento `target_file_path`.
    # Por agora, vamos apenas verificar se foi chamado.
    mock_asyncio_to_thread.assert_called_once()


@pytest.mark.asyncio
@patch('agent.validation_steps.pytest_new_file_validator.run_pytest')
@patch('asyncio.to_thread')
async def test_pytest_new_file_validator_pytest_fails(mock_asyncio_to_thread, mock_run_pytest_patched, validator_instance, tmp_path):
    test_file_path_str = "tests/failing/test_failing_feature.py"
    validator_instance.patches_to_apply = [{
        "file_path": test_file_path_str, "operation": "REPLACE",
        "block_to_replace": None, "content": "assert False"
    }]

    mock_asyncio_to_thread.return_value = True # Arquivo existe
    mock_run_pytest_patched.return_value = (False, "Pytest failed: AssertionError")

    success, reason, message = await validator_instance.execute()

    assert success is False
    assert reason == "PYTEST_NEW_FILE_FAILED"
    assert "Pytest failed: AssertionError" in message
    mock_run_pytest_patched.assert_called_once_with(test_dir=test_file_path_str, cwd=str(tmp_path))

@pytest.mark.asyncio
@patch('asyncio.to_thread')
async def test_pytest_new_file_validator_file_not_found(mock_asyncio_to_thread, validator_instance):
    test_file_path_str = "tests/non_existent/test_not_found.py"
    validator_instance.patches_to_apply = [{
        "file_path": test_file_path_str, "operation": "REPLACE",
        "block_to_replace": None, "content": "..."
    }]
    mock_asyncio_to_thread.return_value = False # Arquivo NÃO existe

    success, reason, message = await validator_instance.execute()

    assert success is False
    assert reason == "TEST_FILE_NOT_FOUND"
    assert f"Test file {test_file_path_str} not found" in message

@pytest.mark.asyncio
async def test_pytest_new_file_validator_no_new_test_file_patch(validator_instance):
    validator_instance.patches_to_apply = [{"file_path": "src/module.py", "operation": "REPLACE", "content": "..."}]
    success, reason, message = await validator_instance.execute()
    assert success is False
    assert reason == "NO_NEW_TEST_FILE_PATCH"

@pytest.mark.asyncio
async def test_pytest_new_file_validator_patch_missing_filepath(validator_instance):
    validator_instance.patches_to_apply = [{"operation": "REPLACE", "content": "..."}]
    # O validador procura por file_path, então se estiver ausente, não deve encontrar patch.
    success, reason, message = await validator_instance.execute()
    assert success is False
    assert reason == "NO_NEW_TEST_FILE_PATCH" # Ou um erro mais específico se a lógica mudar

# O PytestNewFileValidator não escreve mais arquivos temporariamente.
# Ele assume que um PatchApplicatorStep anterior (que será async) já escreveu o arquivo.
# Portanto, os testes relacionados a `TEMP_WRITE_ERROR` e a lógica de unlink interna
# não são mais diretamente aplicáveis da mesma forma.
# O teste `test_pytest_new_file_validator_file_already_exists` agora é o comportamento padrão:
# o validador espera que o arquivo exista.
