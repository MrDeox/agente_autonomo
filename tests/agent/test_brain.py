import pytest
from unittest.mock import patch, MagicMock, ANY # ANY pode não ser necessário com AsyncMock
import logging
import asyncio # Para asyncio.run nos testes e marcar testes como async

# Funções para testar (agora são async)
from agent.brain import generate_next_objective, generate_capacitation_objective, generate_commit_message

# Usar pytest.mark.asyncio para testes async
# A classe de teste pode ser removida ou mantida se preferir a estrutura unittest,
# mas pytest lida bem com funções de teste diretas.
# Vamos converter para funções de teste pytest para consistência com pytest-asyncio.

@pytest.fixture
def logger_fixture():
    logger = logging.getLogger("TestBrainAsync")
    logger.setLevel(logging.DEBUG)
    return logger

@pytest.fixture
def brain_common_params(logger_fixture):
    return {
        "api_key": "test_api_key",
        "model": "test_model",
        "base_url": "https://api.example.com/v1",
        "logger": logger_fixture
    }

@pytest.fixture
def default_config_fixture():
    return {
        "code_analysis_thresholds": {
            "file_loc": 250,
            "function_loc": 40,
            "function_cc": 8
        }
    }

# Mock para call_llm_api que é async
def async_mock_call_llm_api(return_value=("Default Mocked LLM Response", None)):
    async def mock_llm(*args, **kwargs):
        # Simular um pequeno delay, se necessário, para testes de concorrência (não crucial aqui)
        # await asyncio.sleep(0.01)
        return return_value
    return mock_llm

# Mock para analyze_code_metrics (que se tornou async)
def async_mock_analyze_code_metrics(return_value={"summary": {}}):
    async def mock_metrics(*args, **kwargs):
        return return_value
    return mock_metrics


@pytest.mark.asyncio
@patch('agent.brain.call_llm_api', new_callable=lambda: async_mock_call_llm_api(return_value=("New objective based on defaults", None)))
@patch('agent.brain.analyze_code_metrics', new_callable=lambda: async_mock_analyze_code_metrics(return_value={"summary": {"large_files": [("file.py", 300)]}}))
async def test_generate_next_objective_uses_config_thresholds(mock_analyze_code_metrics_patched, mock_call_llm_api_patched, brain_common_params, default_config_fixture):
    # --- Test with default thresholds ---
    await generate_next_objective(
        **brain_common_params,
        current_manifest="Manifest content",
        project_root_dir=".",
        config=default_config_fixture,
        memory_summary="No relevant history."
    )
    # analyze_code_metrics é um mock de uma função async agora
    # A asserção precisa ser feita no mock que foi injetado no módulo.
    # O patch cria um mock, e esse mock é que tem o `assert_called_with`.
    # A forma como os mocks são nomeados nos argumentos do teste é importante.
    # `mock_analyze_code_metrics_patched` é o mock real.

    # Corrigindo a forma de acessar o mock para assertivas
    # O patch substitui a função no módulo 'agent.brain'.
    # `mock_analyze_code_metrics_patched` e `mock_call_llm_api_patched` são os mocks corretos.

    # A chamada a `analyze_code_metrics` é awaitable, mas o mock em si não é.
    # O `assert_called_with` deve funcionar normalmente.
    mock_analyze_code_metrics_patched.assert_called_with(
        root_dir=".",
        file_loc_threshold=250,
        func_loc_threshold=40,
        func_cc_threshold=8
    )
    mock_call_llm_api_patched.assert_called_once()
    mock_analyze_code_metrics_patched.reset_mock()
    mock_call_llm_api_patched.reset_mock()

    # --- Test with different thresholds ---
    custom_config = {"code_analysis_thresholds": {"file_loc": 500, "function_loc": 100, "function_cc": 15}}
    # Reconfigurar o mock para a próxima chamada, se necessário, ou usar um novo patch se o escopo for diferente
    # Aqui, como o mock é o mesmo, podemos apenas chamar de novo.
    # Se `analyze_code_metrics` fosse mockado com `side_effect` para diferentes retornos, seria mais complexo.
    # Para este teste, o return_value do mock é fixo, o que é suficiente para testar os args passados.

    # Precisamos garantir que o mock de analyze_code_metrics é chamado com os novos parâmetros.
    # Se o mock for reutilizado, seu `return_value` precisa ser atualizado ou o teste precisa ser reestruturado.
    # Para este caso, como o mock `analyze_code_metrics` foi definido no patch com um `return_value` fixo,
    # e não estamos testando o `return_value` aqui, mas sim os argumentos com que foi chamado,
    # podemos prosseguir. No entanto, se `generate_next_objective` dependesse do *valor* retornado
    # de forma diferente para diferentes chamadas, precisaríamos de `side_effect`.

    await generate_next_objective(
        **brain_common_params,
        current_manifest="Manifest content",
        project_root_dir="/another/path",
        config=custom_config,
        memory_summary="Some history."
    )
    mock_analyze_code_metrics_patched.assert_called_with(
        root_dir="/another/path",
        file_loc_threshold=500,
        func_loc_threshold=100,
        func_cc_threshold=15
    )
    mock_call_llm_api_patched.assert_called_once() # Foi resetado, então é 1 para esta seção
    mock_analyze_code_metrics_patched.reset_mock()
    mock_call_llm_api_patched.reset_mock()

    # --- Test with missing thresholds ---
    config_missing_thresholds = {}
    await generate_next_objective(
        **brain_common_params,
        current_manifest="",
        project_root_dir=".",
        config=config_missing_thresholds
    )
    mock_analyze_code_metrics_patched.assert_called_with(
        root_dir=".",
        file_loc_threshold=300,
        func_loc_threshold=50,
        func_cc_threshold=10
    )
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.brain.call_llm_api', new_callable=lambda: async_mock_call_llm_api(return_value=("Test objective", None)))
@patch('agent.brain.analyze_code_metrics', new_callable=async_mock_analyze_code_metrics) # Default return é {"summary": {}}
async def test_generate_next_objective_llm_call_success(mock_analyze_code_metrics_patched, mock_call_llm_api_patched, brain_common_params, default_config_fixture):
    objective = await generate_next_objective(
        **brain_common_params,
        current_manifest="Test Manifest",
        project_root_dir=".",
        config=default_config_fixture
    )
    assert objective == "Test objective"
    mock_analyze_code_metrics_patched.assert_called_once()
    mock_call_llm_api_patched.assert_called_once()

    # As kwargs da chamada ao mock async são acessadas da mesma forma
    # O mock em si (mock_call_llm_api_patched) é um MagicMock ou similar, não um coroutine.
    # O que ele retorna (quando chamado) é um coroutine.
    called_kwargs_llm = mock_call_llm_api_patched.call_args.kwargs
    assert called_kwargs_llm["api_key"] == brain_common_params["api_key"]
    assert called_kwargs_llm["model"] == brain_common_params["model"]
    assert "Test Manifest" in called_kwargs_llm["prompt"]
    assert called_kwargs_llm["temperature"] == 0.3
    assert called_kwargs_llm["base_url"] == brain_common_params["base_url"]
    assert called_kwargs_llm["logger"] == brain_common_params["logger"]

@pytest.mark.asyncio
@patch('agent.brain.call_llm_api', new_callable=lambda: async_mock_call_llm_api(return_value=(None, "LLM Error")))
@patch('agent.brain.analyze_code_metrics', new_callable=async_mock_analyze_code_metrics)
async def test_generate_next_objective_llm_call_error(mock_analyze_code_metrics_patched, mock_call_llm_api_patched, brain_common_params, default_config_fixture):
    objective = await generate_next_objective(
         **brain_common_params,
        current_manifest="Test Manifest",
        project_root_dir=".",
        config=default_config_fixture
    )
    assert objective == "Analyze current project state and propose an incremental improvement"
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
@patch('agent.brain.call_llm_api', new_callable=lambda: async_mock_call_llm_api(return_value=("Capacitation objective", None)))
async def test_generate_capacitation_objective_success(mock_call_llm_api_patched, brain_common_params):
    engineer_analysis = "Need new tool X"
    objective = await generate_capacitation_objective(
        **brain_common_params,
        engineer_analysis=engineer_analysis
    )
    assert objective == "Capacitation objective"
    mock_call_llm_api_patched.assert_called_once()
    called_args = mock_call_llm_api_patched.call_args.args
    assert called_args[0] == brain_common_params["api_key"]
    assert called_args[1] == brain_common_params["model"]
    assert engineer_analysis in called_args[2]
    assert called_args[3] == 0.3
    assert called_args[4] == brain_common_params["base_url"]
    assert called_args[5] == brain_common_params["logger"]

@pytest.mark.asyncio
@patch('agent.brain.call_llm_api', new_callable=lambda: async_mock_call_llm_api(return_value=(None, "LLM Error")))
async def test_generate_capacitation_objective_error(mock_call_llm_api_patched, brain_common_params):
    engineer_analysis = "Need new tool X"
    objective = await generate_capacitation_objective(
        **brain_common_params,
        engineer_analysis=engineer_analysis
    )
    assert objective == "Analyze capacitation need and propose a solution"
    mock_call_llm_api_patched.assert_called_once()

@pytest.mark.asyncio
async def test_generate_commit_message_simulated(brain_common_params): # generate_commit_message é async
    analysis_summary = "Implemented feature Y by modifying Z."
    objective = "feat: Add new feature Y for enhanced performance"

    commit_message = await generate_commit_message( # await aqui
        **brain_common_params,
        analysis_summary=analysis_summary,
        objective=objective
    )
    expected_summary_part = "Add new feature Y for enhanced performance"
    assert commit_message == f"feat: {expected_summary_part}"

    long_objective = "feat: Implement a very long and detailed feature description that will certainly exceed the typical subject line length for a commit message"
    commit_message_long = await generate_commit_message( # await aqui
        **brain_common_params,
        analysis_summary=analysis_summary,
        objective=long_objective
    )
    expected_long_summary_part = "Implement a very long and detailed feature description that wil..."
    assert commit_message_long == f"feat: {expected_long_summary_part}"
    assert len(commit_message_long) <= 72

    objective_fix = "fix: Resolve critical bug in module X causing data corruption"
    commit_message_fix = await generate_commit_message( # await aqui
        **brain_common_params,
        analysis_summary="Fixed the bug.",
        objective=objective_fix
    )
    expected_fix_summary_part = "Resolve critical bug in module X causing data corruption"
    assert commit_message_fix == f"fix: {expected_fix_summary_part}"
    assert len(commit_message_fix) <= 72

    simple_objective = "Improve the logging system for better debuggability"
    commit_message_simple = await generate_commit_message( # await aqui
        **brain_common_params,
        analysis_summary="Added more logs.",
        objective=simple_objective
    )
    assert commit_message_simple == f"feat: {simple_objective}"

    objective_for_trunc = "refactor the entire authentication module to use new security protocols and also improve performance"
    commit_message_trunc = await generate_commit_message( # await aqui
       **brain_common_params,
        analysis_summary="Refactored auth.",
        objective=objective_for_trunc
    )
    expected_trunc_summary = "the entire authentication module to use new security protocol..."
    assert commit_message_trunc == f"refactor: {expected_trunc_summary}"

# Se houver um if __name__ == '__main__': unittest.main(), ele deve ser removido
# pois pytest não o utiliza.
