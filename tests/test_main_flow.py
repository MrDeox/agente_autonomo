# tests/test_main_flow.py
import pytest
import json
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from main import HephaestusAgent
# Importar funções específicas que serão mockadas se necessário
from agent.brain import get_action_plan, get_maestro_decision, generate_next_objective, generate_capacitation_objective
from agent.project_scanner import update_project_manifest
from agent.patch_applicator import apply_patches
from agent.code_validator import validate_python_code, validate_json_syntax
from agent.tool_executor import run_pytest, check_file_existence


# Configuração de um logger para o agente durante os testes
@pytest.fixture
def test_agent_logger():
    logger = logging.getLogger("TestHephaestusAgent")
    logger.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler() # Para ver logs durante o teste
    # logger.addHandler(handler)
    return logger

@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Cria um diretório de projeto temporário para o agente operar."""
    project_dir = tmp_path / "hephaestus_test_project"
    project_dir.mkdir()

    # Criar um hephaestus_config.json básico
    default_config = {
        "models": {
            "architect_default": "mock-architect-model",
            "maestro_default": "mock-maestro-model",
            "objective_generator": "mock-objective-model",
            "capacitation_generator": "mock-capacitation-model"
        },
        "validation_strategies": {
            "APPLY_AND_VALIDATE_SYNTAX": {
                "steps": ["apply_patches_to_disk", "validate_syntax"],
                "sanity_check_step": "check_file_existence"
            },
            "APPLY_AND_PYTEST": {
                "steps": ["apply_patches_to_disk", "validate_syntax", "run_pytest_validation"],
                "sanity_check_step": "run_pytest"
            },
            "DISCARD_ALL": {
                "steps": ["discard_patches"], # "discard_patches" não é um step real, mas para o teste
                "sanity_check_step": "skip_sanity_check"
            }
        },
        "cycle_delay_seconds": 0.01
    }
    config_file = project_dir / "hephaestus_config.json"
    config_file.write_text(json.dumps(default_config))

    # Criar um AGENTS.md inicial (pode ser vazio ou com estrutura mínima)
    (project_dir / "AGENTS.md").write_text("# Test AGENTS.md\n")

    # Criar um diretório tests/ para run_pytest
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "tests" / "__init__.py").touch()


    return project_dir

@pytest.fixture
def hephaestus_agent(temp_project_dir: Path, test_agent_logger: logging.Logger, mocker) -> HephaestusAgent:
    """Inicializa o HephaestusAgent para testes, operando no temp_project_dir."""
    # Mock OPENROUTER_API_KEY
    mocker.patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-testapikey"})

    # Mudar o diretório de trabalho atual para o temp_project_dir
    # para que o agente leia/escreva arquivos relativos corretamente.
    original_cwd = Path.cwd()
    os.chdir(temp_project_dir)

    agent = HephaestusAgent(logger_instance=test_agent_logger)

    # Retornar ao CWD original após o teste
    yield agent # Teste executa aqui
    os.chdir(original_cwd)


# --- Testes de Fluxo ---

@patch('main.get_action_plan') # Corrigido
@patch('main.get_maestro_decision') # Corrigido
@patch('main.generate_next_objective') # Corrigido
@patch('main.run_pytest') # Corrigido
@patch('main.check_file_existence') # Corrigido
def test_main_flow_apply_and_validate_syntax_success(
    mock_check_file_existence, mock_run_pytest,
    mock_gen_next_obj, mock_maestro, mock_architect,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path, test_agent_logger: logging.Logger
):
    # --- Configuração dos Mocks ---
    # 1. Arquiteto retorna um patch simples
    action_plan_response = {
        "analysis": "Test analysis: create a new Python file.",
        "patches_to_apply": [{
            "file_path": "new_module.py",
            "operation": "INSERT",
            "content": "print('Hello from new_module.py')\n# Valid Python"
        }]
    }
    mock_architect.return_value = (action_plan_response, None)

    # 2. Maestro escolhe a estratégia APPLY_AND_VALIDATE_SYNTAX
    maestro_decision_response = {"strategy_key": "APPLY_AND_VALIDATE_SYNTAX"}
    # get_maestro_decision retorna uma lista de logs de tentativa
    mock_maestro.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model": "mock_model", "raw_response": ""}]


    # 3. Gerador de próximo objetivo (será chamado no final do ciclo de sucesso)
    mock_gen_next_obj.return_value = "Objective: Do more tests."

    # 4. check_file_existence (sanity check) retorna sucesso
    mock_check_file_existence.return_value = (True, "All files checked exist.")


    # --- Execução do Ciclo do Agente ---
    # Adicionar um objetivo inicial para o agente processar
    hephaestus_agent.objective_stack.append("Initial Objective: Create new_module.py")

    # Rodar um ciclo (ou o método run() adaptado para um ciclo, ou chamar fases)
    # Para este teste, vamos chamar run() e esperar que ele complete um ciclo.
    # Se run() for um loop infinito, precisaremos de uma forma de pará-lo ou testar as fases.
    # Assumindo que run() executa até a pilha de objetivos ficar vazia.

    # Como run() tem um `while self.objective_stack:`, ele tentará gerar novos objetivos.
    # Precisamos garantir que ele pare após um ciclo para este teste.
    # Podemos mockar `generate_next_objective` para que ele não adicione nada,
    # ou fazer com que ele levante uma exceção controlada para parar o loop após o primeiro ciclo.

    # Uma forma de controlar: mockar generate_next_objective para esvaziar a pilha
    def stop_loop_after_next_objective(*args, **kwargs):
        hephaestus_agent.objective_stack.clear() # Esvazia a pilha para parar o loop
        return "Objective: Stop loop."
    mock_gen_next_obj.side_effect = stop_loop_after_next_objective

    hephaestus_agent.run() # Executa o loop, que deve parar após um ciclo bem-sucedido

    # --- Asserções ---
    # 1. Verificar se os mocks foram chamados
    mock_architect.assert_called_once()
    mock_maestro.assert_called_once()
    mock_gen_next_obj.assert_called_once() # Chamado após sucesso e sanidade
    mock_check_file_existence.assert_called_once() # Chamado como sanity check

    # 2. Verificar se o arquivo foi criado e tem o conteúdo correto
    created_file_path = temp_project_dir / "new_module.py"
    assert created_file_path.exists()
    content = created_file_path.read_text()
    assert "print('Hello from new_module.py')" in content
    assert "# Valid Python" in content

    # 3. Verificar o estado final do agente (ex: resultado da validação)
    assert hephaestus_agent.state["validation_result"][0] is True # Sucesso
    assert hephaestus_agent.state["validation_result"][1] == "APPLIED_AND_VALIDATED"

    # 4. Verificar se AGENTS.md foi atualizado (após sucesso e sanidade)
    # update_project_manifest é chamado com root_dir="." e target_files=[]
    # O mock de update_project_manifest não é necessário se testamos o efeito (conteúdo de AGENTS.md)
    agents_md_content_after = (temp_project_dir / "AGENTS.md").read_text()
    assert "new_module.py" in agents_md_content_after # Deve estar listado na estrutura de arquivos
    assert "### Módulo: `new_module.py`" in agents_md_content_after # E no resumo de APIs

    # 5. Verificar logs (opcional, usando test_agent_logger ou caplog)
    # Ex: test_agent_logger.info.assert_any_call("SUCESSO NO CICLO! Razão: APPLIED_AND_VALIDATED")


@patch('main.get_action_plan')
@patch('main.get_maestro_decision')
@patch('main.generate_capacitation_objective')
def test_main_flow_capacitation_required(
    mock_gen_cap_obj, mock_maestro, mock_architect,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path
):
    # 1. Arquiteto sugere algo que o Maestro identificará como necessidade de capacitação
    action_plan_response = {
        "analysis": "This task requires a new tool 'super_tool'.",
        "patches_to_apply": [] # Pode ou não ter patches
    }
    mock_architect.return_value = (action_plan_response, None)

    # 2. Maestro decide CAPACITATION_REQUIRED
    maestro_decision_response = {"strategy_key": "CAPACITATION_REQUIRED"}
    mock_maestro.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"m", "raw_response":""}]

    # 3. Gerador de objetivo de capacitação
    mock_gen_cap_obj.return_value = "Objective: Create super_tool."

    # --- Execução ---
    initial_objective = "Initial Objective: Use super_tool."
    hephaestus_agent.objective_stack.append(initial_objective)

    # Para parar o loop após o ciclo de capacitação:
    def stop_after_capacitation_obj_generated(*args, **kwargs):
        # O objetivo de capacitação e o original são re-empilhados.
        # O novo objetivo de capacitação será o próximo.
        # Para o teste, vamos apenas verificar se ele foi adicionado.
        # Esvaziar a pilha para que o run() pare.
        hephaestus_agent.objective_stack.clear()
        return "Objective: Create super_tool." # Retorno do mock
    mock_gen_cap_obj.side_effect = stop_after_capacitation_obj_generated

    hephaestus_agent.run()

    # --- Asserções ---
    mock_architect.assert_called_once()
    mock_maestro.assert_called_once()
    mock_gen_cap_obj.assert_called_once_with(
        hephaestus_agent.api_key,
        hephaestus_agent.config["models"]["capacitation_generator"],
        action_plan_response["analysis"], # Análise do arquiteto
        hephaestus_agent.logger
    )

    # No final do ciclo, a pilha foi limpa pelo side_effect.
    # A lógica do agente é:
    # self.objective_stack.append(current_objective) -> re-empilha o original
    # self.objective_stack.append(capacitation_objective) -> empilha o novo
    # O teste precisa verificar que o capacitation_objective foi gerado.
    # O side_effect já confirma que mock_gen_cap_obj foi chamado.
    # Se quiséssemos verificar o estado da pilha antes de limpar:
    # assert "Objective: Create super_tool." in hephaestus_agent.objective_stack
    # assert initial_objective in hephaestus_agent.objective_stack


@patch('main.get_action_plan')
@patch('main.get_maestro_decision')
@patch('main.run_pytest')
def test_main_flow_pytest_failure_triggers_correction_objective(
    mock_run_pytest, mock_maestro, mock_architect,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path
):
    # 1. Arquiteto retorna um patch que (simularemos) causa falha no pytest
    faulty_patch_content = "def test_always_fails():\n  assert False"
    action_plan_response = {
        "analysis": "Test analysis: add a failing test.",
        "patches_to_apply": [{
            "file_path": "tests/test_new_feature.py", # Assume diretório tests/ existe
            "operation": "INSERT",
            "content": faulty_patch_content
        }]
    }
    mock_architect.return_value = (action_plan_response, None)

    # 2. Maestro escolhe estratégia que roda pytest
    maestro_decision_response = {"strategy_key": "APPLY_AND_PYTEST"}
    mock_maestro.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"m", "raw_response":""}]

    # 3. run_pytest retorna falha
    mock_run_pytest.return_value = (False, "Pytest failed: 1 test failed.")

    # --- Execução ---
    initial_objective = "Objective: Add a new feature and test it."
    hephaestus_agent.objective_stack.append(initial_objective)

    # Mock generate_next_objective para parar o loop após o ciclo de falha.
    # Em caso de falha corrigível, um novo objetivo de correção é adicionado.
    # O loop continuaria.
    with patch('agent.brain.generate_next_objective') as mock_gen_next_obj_stopper:
        def stop_loop_after_correction_obj(*args, **kwargs):
            hephaestus_agent.objective_stack.clear()
            return "This should not be reached if correction happens"
        mock_gen_next_obj_stopper.side_effect = stop_loop_after_correction_obj

        hephaestus_agent.run()

    # --- Asserções ---
    mock_architect.assert_called_once()
    mock_maestro.assert_called_once()
    mock_run_pytest.assert_called_once() # run_pytest na validação
    mock_run_pytest.assert_any_call(test_dir='tests/') # sanity_check_step também é run_pytest para esta estratégia

    # Verificar se o arquivo de teste foi criado com o patch
    created_test_file = temp_project_dir / "tests" / "test_new_feature.py"
    assert created_test_file.exists()
    assert faulty_patch_content in created_test_file.read_text()

    # Verificar se um objetivo de correção foi adicionado à pilha (antes de ser limpa pelo mock)
    # O estado final do agente deve refletir a falha.
    assert hephaestus_agent.state["validation_result"][0] is False
    # A razão da falha pode ser PYTEST_FAILURE (da validação) ou REGRESSION_DETECTED_BY_RUN_PYTEST (da sanidade)
    # A lógica é: se a validação falha, a sanidade não roda.
    assert hephaestus_agent.state["validation_result"][1] == "PYTEST_FAILURE"

    # O importante é que o loop `run` teria continuado com um objetivo de correção.
    # No `run`, após falha corrigível:
    # self.objective_stack.append(current_objective)
    # self.objective_stack.append(correction_obj_text)
    # O mock `stop_loop_after_correction_obj` limpou a pilha, então não podemos verificar o conteúdo final dela.
    # Mas podemos verificar se o logger registrou a criação do objetivo de correção.
    # test_agent_logger.info.assert_any_call("Gerado novo objetivo de correção e adicionado à pilha.")
    # Isso requer que o logger seja mais granularmente mockado ou usar caplog.

    # Para verificar o objetivo de correção mais diretamente, precisaríamos de acesso
    # ao que foi colocado na pilha antes do mock `stop_loop_after_correction_obj` limpar.
    # Ou, não mockar `generate_next_objective` e deixar o agente tentar processar o
    # objetivo de correção, mockando `get_action_plan` para a segunda chamada.
    # Isso tornaria o teste mais complexo.
    # Por agora, confiamos que a lógica de adicionar objetivo de correção foi ativada
    # pela falha do pytest.

"""
Observações sobre os testes de `main_flow`:
- Fixtures `test_agent_logger`, `temp_project_dir`, e `hephaestus_agent` preparam o ambiente.
- `temp_project_dir` inclui um `hephaestus_config.json` básico.
- O CWD é alterado para `temp_project_dir` durante a execução do agente.
- Mocks são usados para:
    - `os.environ` para `OPENROUTER_API_KEY`.
    - Funções do `agent.brain` (LLM interactions).
    - Ferramentas de validação como `run_pytest`, `check_file_existence`.
- Teste de fluxo de sucesso:
    - Verifica criação de arquivo, atualização do manifesto, chamadas de mock.
    - Usa um `side_effect` em `generate_next_objective` para parar o loop `run()` após um ciclo.
- Teste de `CAPACITATION_REQUIRED`:
    - Verifica se `generate_capacitation_objective` é chamado com os argumentos corretos.
- Teste de falha (Pytest) e gatilho de correção:
    - Simula falha no `run_pytest`.
    - Verifica se o estado do agente reflete a falha.
    - Indiretamente verifica se a lógica de objetivo de correção seria ativada.
- Estes são testes de integração "focados" ou "verticais", não testes de unidade completos para `main.py`.
  Eles verificam a interação correta dos componentes principais em cenários chave.
"""
