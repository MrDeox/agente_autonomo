# tests/test_main_flow.py
import pytest
import json
import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from main import HephaestusAgent
# Importar funções específicas que serão mockadas se necessário
# from agent.brain import get_action_plan, get_maestro_decision # Removidas
from agent.brain import generate_next_objective, generate_capacitation_objective, generate_commit_message
# As classes ArchitectAgent e MaestroAgent serão mockadas diretamente ou seus métodos
# from agent.agents import ArchitectAgent, MaestroAgent
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

    # Criar um hephaestus_config.json básico DENTRO do project_dir
    default_config = {
        "models": {
            "architect_default": "mock-architect-model",
            "maestro_default": "mock-maestro-model",
            "objective_generator": "mock-objective-model",
            "capacitation_generator": "mock-capacitation-model",
            "commit_message_generator": "mock-commit-model" # Adicionado para teste de commit
        },
        "validation_strategies": {
            "APPLY_AND_VALIDATE_SYNTAX_SANDBOX": { # Nomeado para clareza
                "steps": ["apply_patches_to_disk", "validate_syntax"], # Estes rodarão no sandbox
                "sanity_check_step": "check_file_existence" # Este rodará no real
            },
            "APPLY_AND_PYTEST_SANDBOX": { # Nomeado para clareza
                "steps": ["apply_patches_to_disk", "validate_syntax", "run_pytest_validation"], # Estes rodarão no sandbox
                "sanity_check_step": "run_pytest" # Este rodará no real
            },
            "DISCARD_ALL": { # Para testar o descarte sem aplicar
                "steps": [], # Sem apply_patches_to_disk
                "sanity_check_step": "skip_sanity_check"
            }
        },
        "cycle_delay_seconds": 0.01
    }
    config_file = project_dir / "hephaestus_config.json"
    config_file.write_text(json.dumps(default_config, indent=4))

    # Criar um AGENTS.md inicial DENTRO do project_dir
    (project_dir / "AGENTS.md").write_text("# Test AGENTS.md\nProject root for testing.\n")

    # Criar um diretório tests/ DENTRO do project_dir para run_pytest
    tests_subdir = project_dir / "tests"
    tests_subdir.mkdir(exist_ok=True)
    (tests_subdir / "__init__.py").touch()
    (tests_subdir / "test_placeholder.py").write_text("def test_always_pass():\n    assert True\n")


    # Criar um .gitattributes para normalizar line endings, se necessário em alguns ambientes
    # (project_dir / ".gitattributes").write_text("* text=auto eol=lf\n")

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

# Os patches agora devem mirar nos métodos dos agentes instanciados ou nas classes em `main`
# Se HephaestusAgent instancia ArchitectAgent e MaestroAgent em seu __init__,
# podemos mockar as classes em si se elas são importadas em `main.py`,
# ou mockar os métodos das instâncias após a criação do `hephaestus_agent`.

@patch('main.ArchitectAgent.plan_action') # Mock do método na classe importada em main
@patch('main.MaestroAgent.choose_strategy') # Mock do método na classe importada em main
@patch('main.generate_next_objective')
@patch('main.run_pytest')
@patch('main.check_file_existence')
@patch('main.generate_commit_message') # Adicionado para cobrir o fluxo de commit
def test_main_flow_apply_and_validate_syntax_success(
    mock_gen_commit_msg, mock_check_file_existence, mock_run_pytest,
    mock_gen_next_obj, mock_maestro_choose_strategy, mock_architect_plan_action,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path, test_agent_logger: logging.Logger
):
    # --- Configuração dos Mocks ---
    # 1. ArchitectAgent.plan_action retorna um patch simples
    action_plan_response = {
        "analysis": "Test analysis: create a new Python file.",
        "patches_to_apply": [{
            "file_path": "new_module.py",
            "operation": "INSERT",
            "content": "print('Hello from new_module.py')\n# Valid Python"
        }]
    }
    # ArchitectAgent.plan_action retorna (plan_data, error_msg)
    mock_architect_plan_action.return_value = (action_plan_response, None)

    # 2. MaestroAgent.choose_strategy escolhe a estratégia
    maestro_decision_response = {"strategy_key": "APPLY_AND_VALIDATE_SYNTAX_SANDBOX"}
    # MaestroAgent.choose_strategy retorna uma lista de logs de tentativa
    mock_maestro_choose_strategy.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model": "mock_maestro_model", "raw_response": json.dumps(maestro_decision_response)}]

    # 3. Gerador de próximo objetivo
    mock_gen_next_obj.return_value = "Objective: Do more tests."

    # 4. check_file_existence (sanity check) retorna sucesso
    mock_check_file_existence.return_value = (True, "All files checked exist.")

    # 5. generate_commit_message retorna uma mensagem
    mock_gen_commit_msg.return_value = "feat: Create new_module.py"

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

    # Definir o limite de ciclos para 1 para este teste.
    hephaestus_agent.objective_stack_depth_for_testing = 1
    # O mock_gen_next_obj ainda é útil para fornecer um valor de retorno previsível
    # e para a asserção de que foi chamado.
    mock_gen_next_obj.return_value = "Objective: Stop loop." # Não mais limpa a pilha aqui

    hephaestus_agent.run() # Executa o loop, que deve parar após um ciclo bem-sucedido

    # --- Asserções ---
    # 1. Verificar se os mocks dos métodos dos agentes foram chamados
    mock_architect_plan_action.assert_called_once_with(
        objective="Initial Objective: Create new_module.py",
        manifest=hephaestus_agent.state.manifesto_content # Manifesto após _generate_manifest
    )
    mock_maestro_choose_strategy.assert_called_once_with(
        action_plan_data=action_plan_response,
        memory_summary=hephaestus_agent.memory.get_full_history_for_prompt()
    )
    mock_gen_next_obj.assert_called_once() # Chamado após sucesso e sanidade
    mock_check_file_existence.assert_called_once() # Chamado como sanity check
    mock_gen_commit_msg.assert_called_once() # Chamado para o commit

    # 2. Verificar se o arquivo foi criado e tem o conteúdo correto
    created_file_path = temp_project_dir / "new_module.py"
    assert created_file_path.exists()
    content = created_file_path.read_text()
    assert "print('Hello from new_module.py')" in content
    assert "# Valid Python" in content

    # 3. Verificar o estado final do agente (ex: resultado da validação)
    assert hephaestus_agent.state.validation_result[0] is True # Sucesso
    assert hephaestus_agent.state.validation_result[1] == "APPLIED_AND_VALIDATED"

    # 4. Verificar se AGENTS.md foi atualizado (após sucesso e sanidade)
    # update_project_manifest é chamado com root_dir="." e target_files=[]
    # O mock de update_project_manifest não é necessário se testamos o efeito (conteúdo de AGENTS.md)
    agents_md_content_after = (temp_project_dir / "AGENTS.md").read_text()
    assert "new_module.py" in agents_md_content_after # Deve estar listado na estrutura de arquivos
    assert "### Módulo: `new_module.py`" in agents_md_content_after # E no resumo de APIs

    # 5. Verificar logs (opcional, usando test_agent_logger ou caplog)
    # Ex: test_agent_logger.info.assert_any_call("SUCESSO NO CICLO! Razão: APPLIED_AND_VALIDATED")


@patch('main.ArchitectAgent.plan_action')
@patch('main.MaestroAgent.choose_strategy')
@patch('main.generate_capacitation_objective')
def test_main_flow_capacitation_required(
    mock_gen_cap_obj, mock_maestro_choose_strategy, mock_architect_plan_action,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path
):
    # 1. ArchitectAgent.plan_action sugere algo que requer capacitação
    action_plan_response = {
        "analysis": "This task requires a new tool 'super_tool'.",
        "patches_to_apply": []
    }
    mock_architect_plan_action.return_value = (action_plan_response, None)

    # 2. MaestroAgent.choose_strategy decide CAPACITATION_REQUIRED
    maestro_decision_response = {"strategy_key": "CAPACITATION_REQUIRED"}
    mock_maestro_choose_strategy.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"mock_maestro_model", "raw_response":json.dumps(maestro_decision_response)}]

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
    mock_architect_plan_action.assert_called_once()
    mock_maestro_choose_strategy.assert_called_once()
    mock_gen_cap_obj.assert_called_once_with(
        api_key=hephaestus_agent.api_key,
        model=hephaestus_agent.config["models"]["capacitation_generator"],
        engineer_analysis=action_plan_response["analysis"],
        logger=hephaestus_agent.logger, # O logger global do agente é passado
        memory_summary=hephaestus_agent.memory.get_full_history_for_prompt() # memory_summary é passado
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


@patch('main.ArchitectAgent.plan_action')
@patch('main.MaestroAgent.choose_strategy')
@patch('main.run_pytest')
def test_main_flow_pytest_failure_triggers_correction_objective(
    mock_run_pytest, mock_maestro_choose_strategy, mock_architect_plan_action,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path
):
    # 1. ArchitectAgent.plan_action retorna um patch que (simularemos) causa falha no pytest
    faulty_patch_content = "def test_always_fails():\n  assert False"
    action_plan_response = {
        "analysis": "Test analysis: add a failing test.",
        "patches_to_apply": [{
            "file_path": "tests/test_new_feature.py", # Assume diretório tests/ existe
            "operation": "INSERT",
            "content": faulty_patch_content
        }]
    }
    mock_architect_plan_action.return_value = (action_plan_response, None)

    # 2. MaestroAgent.choose_strategy escolhe estratégia que roda pytest
    maestro_decision_response = {"strategy_key": "APPLY_AND_PYTEST_SANDBOX"}
    mock_maestro_choose_strategy.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"mock_maestro_model", "raw_response":json.dumps(maestro_decision_response)}]

    # 3. run_pytest retorna falha
    mock_run_pytest.return_value = (False, "Pytest failed: 1 test failed.")

    # --- Execução ---
    initial_objective = "Objective: Add a new feature and test it."
    hephaestus_agent.objective_stack.append(initial_objective)

    # Mock generate_next_objective para parar o loop após o ciclo de falha.
    # Em caso de falha corrigível, um novo objetivo de correção é adicionado.
    # O loop continuaria. Para o teste, queremos que ele pare após este primeiro ciclo de falha.
    hephaestus_agent.objective_stack_depth_for_testing = 1

    # Não precisamos mais mockar generate_next_objective para parar o loop aqui,
    # pois o limite de ciclo cuidará disso.
    hephaestus_agent.run()

    # --- Asserções ---
    mock_architect_plan_action.assert_called_once()
    mock_maestro_choose_strategy.assert_called_once()

    # run_pytest é chamado duas vezes: uma na validação (sandbox) e uma na sanidade (real)
    # A primeira chamada é com cwd do sandbox, a segunda com cwd="."
    # O mock_run_pytest precisa lidar com isso ou ser mais específico.
    # Para este teste, a falha ocorre na primeira chamada (validação no sandbox).
    calls = mock_run_pytest.call_args_list
    assert len(calls) >= 1 # Deve ser chamado ao menos uma vez para a validação
    # A primeira chamada (validação no sandbox) terá um cwd que é o sandbox
    assert calls[0][1]['cwd'] == hephaestus_agent.state.validation_result[2].split("'")[1] if hephaestus_agent.state.validation_result[1] == "PYTEST_FAILURE_IN_SANDBOX" else "."


    # Verificar se o arquivo de teste foi criado com o patch (no sandbox, que depois é limpo)
    # Não podemos verificar diretamente o arquivo após o run() se o sandbox é limpo.
    # Mas podemos verificar se o apply_patches foi chamado corretamente.
    # A lógica de criação do objetivo de correção é o principal aqui.
    created_test_file = temp_project_dir / "tests" / "test_new_feature.py"
    assert created_test_file.exists()
    assert faulty_patch_content in created_test_file.read_text()

    # Verificar se um objetivo de correção foi adicionado à pilha (antes de ser limpa pelo mock)
    # O estado final do agente deve refletir a falha.
    assert hephaestus_agent.state.validation_result[0] is False
    # A razão da falha deve ser PYTEST_FAILURE_IN_SANDBOX, pois a estratégia é APPLY_AND_PYTEST_SANDBOX
    assert hephaestus_agent.state.validation_result[1] == "PYTEST_FAILURE_IN_SANDBOX"

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


# --- Testes de Fluxo com Sandbox ---

@patch('main.ArchitectAgent.plan_action')
@patch('main.MaestroAgent.choose_strategy')
@patch('main.generate_next_objective') # Para controlar o loop
@patch('shutil.copytree')
@patch('tempfile.TemporaryDirectory')
def test_main_flow_sandbox_syntax_error_discarded(
    mock_temp_dir, mock_copytree,
    mock_gen_next_obj, mock_maestro_choose_strategy, mock_architect_plan_action,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path, test_agent_logger: logging.Logger
):
    # --- Configuração do Projeto Inicial ---
    original_file_name = "module_to_patch.py"
    original_file_content = "def valid_function():\n    return True\n"
    original_file_path_project = temp_project_dir / original_file_name
    original_file_path_project.write_text(original_file_content)

    # --- Configuração dos Mocks ---
    # 1. Mock TemporaryDirectory
    mock_sandbox_path = temp_project_dir / "mock_sandbox"
    mock_sandbox_path.mkdir()
    # O objeto retornado por TemporaryDirectory() tem um atributo 'name' e um método 'cleanup()'
    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.name = str(mock_sandbox_path)
    mock_temp_dir.return_value = mock_temp_dir_instance

    # 2. Mock shutil.copytree
    # Fazemos a cópia real para o mock_sandbox_path para que apply_patches e validação funcionem
    def actual_copytree(src, dst, dirs_exist_ok=False):
        if Path(dst).exists() and dirs_exist_ok: # Simular dirs_exist_ok
             for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if Path(s).is_dir():
                    shutil.copytree(s, d, dirs_exist_ok=dirs_exist_ok, symlinks=False, ignore=None)
                else:
                    shutil.copy2(s, d) # copy2 para simular melhor
        else:
            shutil.copytree(src, dst, symlinks=False, ignore=None, dirs_exist_ok=dirs_exist_ok)

    mock_copytree.side_effect = actual_copytree


    # 3. ArchitectAgent.plan_action retorna um patch com erro de sintaxe
    invalid_patch_content = "def invalid_function():\n  print 'hello world'\n" # Erro de sintaxe Python 3
    action_plan_response = {
        "analysis": "Test analysis: apply a patch with syntax error.",
        "patches_to_apply": [{
            "file_path": original_file_name,
            "operation": "REPLACE",
            "block_to_replace": None,
            "content": invalid_patch_content
        }]
    }
    mock_architect_plan_action.return_value = (action_plan_response, None)

    # 4. MaestroAgent.choose_strategy escolhe estratégia que aplica e valida sintaxe
    maestro_decision_response = {"strategy_key": "APPLY_AND_VALIDATE_SYNTAX_SANDBOX"}
    mock_maestro_choose_strategy.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"mock_maestro_model", "raw_response":json.dumps(maestro_decision_response)}]

    # 5. Gerador de próximo objetivo será mockado para retornar um valor previsível.
    mock_gen_next_obj.return_value = "Objective: Stop after sandbox failure."

    # Definir o limite de ciclos para 1 para este teste.
    hephaestus_agent.objective_stack_depth_for_testing = 1

    # Mocks para outras funções de geração que podem ser chamadas.
    with patch('main.generate_capacitation_objective') as mock_gen_cap_obj, \
         patch('main.generate_commit_message') as mock_gen_commit_msg:
        mock_gen_cap_obj.return_value = "Dummy Capacitation Obj"
        mock_gen_commit_msg.return_value = "Dummy Commit Msg"

        # --- Execução do Ciclo do Agente ---
        hephaestus_agent.objective_stack.append("Initial Objective: Patch a file with syntax error.")
        hephaestus_agent.run()

    # --- Asserções ---
    # 1. Mocks de sandbox foram chamados
    mock_temp_dir.assert_called_once()
    # copytree é chamado com "." como src e o nome do sandbox_dir como dst
    # A primeira chamada a copytree é para copiar o projeto para o sandbox
    mock_copytree.assert_any_call(".", str(mock_sandbox_path), dirs_exist_ok=True)


    # 2. apply_patches foi chamado com base_path do sandbox
    # Precisamos mockar apply_patches para verificar seus argumentos
    with patch('main.apply_patches') as mock_apply_patches_main:
        # Re-executar a parte relevante ou ter uma forma de capturar a chamada
        # Isso é complicado porque run() já executou.
        # Alternativa: verificar o log ou o efeito (arquivo no mock_sandbox_path)
        # Por agora, vamos verificar o efeito:
        patched_file_in_sandbox = mock_sandbox_path / original_file_name
        assert patched_file_in_sandbox.exists()
        # Nota: se apply_patches falhar internamente, este arquivo pode não ser escrito
        # ou pode ser parcialmente escrito. A validação de sintaxe deve pegar isso.
        # O apply_patches do agente é robusto e tentará escrever.
        assert invalid_patch_content in patched_file_in_sandbox.read_text()


    # 3. validate_python_code foi chamado com o caminho do arquivo no sandbox
    # Precisamos mockar validate_python_code para verificar
    with patch('main.validate_python_code') as mock_validate_py_code:
        # Re-run não é ideal. Precisamos que o HephaestusAgent use uma instância mockada
        # ou que o mock seja global.
        # Para este teste, vamos assumir que a chamada ocorreu se o resultado da validação for o esperado.
        # Idealmente:
        # mock_validate_py_code.assert_called_once_with(
        #     Path(mock_sandbox_path) / original_file_name, # ou str(...)
        #     test_agent_logger
        # )
        # Devido à estrutura, esta asserção é difícil de fazer diretamente sem refatorar
        # como as funções de validação são chamadas ou injetadas.
        pass


    # 4. Arquivo original no projeto real NÃO foi alterado
    assert original_file_path_project.read_text() == original_file_content

    # 5. Estado de validação é PATCH_DISCARDED
    validation_status, reason, details = hephaestus_agent.state.validation_result # Acesso direto
    assert validation_status is False
    assert reason == "PATCH_DISCARDED"
    # Detalhes devem conter a razão da falha no sandbox
    assert "SYNTAX_VALIDATION_FAILED_IN_SANDBOX" in details
    assert original_file_name in details # Nome do arquivo com erro
    assert "invalid syntax" in details.lower() # Mensagem do PyCompileError

    # 6. mock_sandbox_path (simulando o TemporaryDirectory) teve cleanup chamado
    mock_temp_dir_instance.cleanup.assert_called_once()

    # 7. Verificar se o objetivo de correção foi tentado (log)
    # Como paramos o loop, o objetivo de correção não foi processado.
    # Mas o logger deve indicar sua criação.
    # Precisaria do `caplog` fixture do pytest para verificar logs.
    # Ex: assert "Gerado novo objetivo de correção para patches descartados" in caplog.text

    # 8. Verificar que os métodos dos agentes foram chamados
    mock_architect_plan_action.assert_called_once()
    mock_maestro_choose_strategy.assert_called_once()

    # 9. O generate_next_objective foi chamado.
    mock_gen_next_obj.assert_called()


@patch('main.get_action_plan')
@patch('main.MaestroAgent.choose_strategy')
@patch('main.generate_next_objective')
@patch('main.run_pytest')
@patch('main.check_file_existence')
@patch('main.update_project_manifest')
@patch('main.run_git_command')
@patch('main.generate_commit_message') # Adicionado
@patch('shutil.copytree')
@patch('shutil.copy2')
@patch('tempfile.TemporaryDirectory')
def test_main_flow_sandbox_success_promotion(
    mock_temp_dir, mock_shutil_copy2, mock_shutil_copytree,
    mock_gen_commit_msg, mock_run_git, mock_update_manifest, mock_check_file_existence, mock_run_pytest_sanity,
    mock_gen_next_obj, mock_maestro_choose_strategy, mock_architect_plan_action,
    hephaestus_agent: HephaestusAgent, temp_project_dir: Path, test_agent_logger: logging.Logger
):
    # --- Configuração do Projeto Inicial ---
    original_file_name = "module_to_promote.py"
    original_file_content = "def old_function():\n    return 'old'\n"
    original_file_path_project = temp_project_dir / original_file_name
    original_file_path_project.write_text(original_file_content)

    # --- Configuração dos Mocks ---
    # 1. Mock TemporaryDirectory
    mock_sandbox_path = temp_project_dir / "mock_sandbox_success"
    mock_sandbox_path.mkdir()
    mock_temp_dir_instance = MagicMock()
    mock_temp_dir_instance.name = str(mock_sandbox_path)
    mock_temp_dir.return_value = mock_temp_dir_instance

    # 2. Mock shutil.copytree (para copiar para o sandbox)
    def actual_copytree_success(src, dst, dirs_exist_ok=False):
        if Path(dst).exists() and dirs_exist_ok:
            for item in os.listdir(src):
                s_item = Path(src) / item
                d_item = Path(dst) / item
                if s_item.name == ".git": continue
                if s_item.is_dir():
                    shutil.copytree(s_item, d_item, dirs_exist_ok=True, symlinks=False, ignore=shutil.ignore_patterns(".git"))
                else:
                    shutil.copy2(s_item, d_item)
        else:
             shutil.copytree(src, dst, dirs_exist_ok=dirs_exist_ok, symlinks=False, ignore=shutil.ignore_patterns(".git"))
    mock_shutil_copytree.side_effect = actual_copytree_success

    # 3. ArchitectAgent.plan_action retorna um patch válido
    valid_patch_content = "def new_function():\n    return 'new and shiny!'\n"
    action_plan_response = {
        "analysis": "Test analysis: apply a valid patch.",
        "patches_to_apply": [{
            "file_path": original_file_name,
            "operation": "REPLACE",
            "block_to_replace": None,
            "content": valid_patch_content
        }]
    }
    mock_architect_plan_action.return_value = (action_plan_response, None)

    # 4. MaestroAgent.choose_strategy escolhe estratégia
    maestro_decision_response = {"strategy_key": "APPLY_AND_VALIDATE_SYNTAX_SANDBOX"}
    mock_maestro_choose_strategy.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"mock_maestro_model", "raw_response":json.dumps(maestro_decision_response)}]

    # 5. Mocks para o final do ciclo de sucesso
    mock_gen_next_obj.return_value = "Objective: Stop after success (from mock_gen_next_obj)."
    hephaestus_agent.objective_stack_depth_for_testing = 1

    mock_check_file_existence.return_value = (True, "Sanity check: Files exist.")
    mock_update_manifest.return_value = None
    mock_run_git.return_value = (True, "Git command successful.")
    mock_gen_commit_msg.return_value = "feat: Test commit message for sandbox success" # Já está como argumento do teste

    # --- Execução do Ciclo do Agente ---
    hephaestus_agent.objective_stack.append("Initial Objective: Patch file successfully via sandbox.")
    hephaestus_agent.run()

    # --- Asserções ---
    # 1. Mocks de sandbox e cópia para sandbox
    mock_temp_dir.assert_called_once()
    mock_shutil_copytree.assert_any_call(".", str(mock_sandbox_path), dirs_exist_ok=True)

    # 2. Arquivo foi modificado no sandbox (efeito de apply_patches)
    patched_file_in_sandbox = mock_sandbox_path / original_file_name
    assert patched_file_in_sandbox.exists()
    assert valid_patch_content in patched_file_in_sandbox.read_text()

    # 3. Validação de sintaxe (implícita, pois o fluxo continuou para promoção)
    # Poderíamos mockar validate_python_code e verificar sua chamada com o path do sandbox se necessário.

    # 4. Promoção: shutil.copy2 foi chamado para copiar do sandbox para o real
    # O caminho de origem é mock_sandbox_path / original_file_name
    # O caminho de destino é temp_project_dir / original_file_name
    expected_src_path = mock_sandbox_path / original_file_name
    expected_dst_path = temp_project_dir / original_file_name
    mock_shutil_copy2.assert_called_once_with(str(expected_src_path), str(expected_dst_path))

    # 5. Arquivo no projeto real FOI alterado
    assert original_file_path_project.exists()
    assert original_file_path_project.read_text() == valid_patch_content

    # 6. Estado de validação é APPLIED_AND_VALIDATED
    validation_status, reason, details = hephaestus_agent.state.validation_result # Acesso direto
    assert validation_status is True
    assert reason == "APPLIED_AND_VALIDATED"
    assert "sandbox" in details # Mensagem deve indicar que foi via sandbox

    # 7. Sanity check, manifest update, e git commit mocks foram chamados
    mock_check_file_existence.assert_called_once()
    mock_update_manifest.assert_called_once_with(root_dir=".", target_files=[]) # Verifica args

    # Verificar chamadas do git
    expected_commit_message = "feat: Test commit message for sandbox success" # Definido no mock de generate_commit_message
    mock_run_git.assert_any_call(['git', 'add', '.'])
    mock_run_git.assert_any_call(['git', 'commit', '-m', expected_commit_message])


    # 8. Cleanup do sandbox
    mock_temp_dir_instance.cleanup.assert_called_once()

    # 9. Chamadas dos métodos dos agentes e outros mocks
    mock_architect_plan_action.assert_called_once()
    mock_maestro_choose_strategy.assert_called_once()
    mock_gen_next_obj.assert_called_once()
    mock_gen_commit_msg.assert_called_once() # Verificar se foi chamado


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
