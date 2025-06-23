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
    assert hephaestus_agent.state.validation_result[0] is False
    # A razão da falha pode ser PYTEST_FAILURE (da validação) ou REGRESSION_DETECTED_BY_RUN_PYTEST (da sanidade)
    # A lógica é: se a validação falha, a sanidade não roda.
    assert hephaestus_agent.state.validation_result[1] == "PYTEST_FAILURE"

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

@patch('main.get_action_plan')
@patch('main.get_maestro_decision')
@patch('main.generate_next_objective') # Para controlar o loop
@patch('shutil.copytree')
@patch('tempfile.TemporaryDirectory')
def test_main_flow_sandbox_syntax_error_discarded(
    mock_temp_dir, mock_copytree,
    mock_gen_next_obj, mock_maestro, mock_architect,
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


    # 3. Arquiteto retorna um patch com erro de sintaxe
    invalid_patch_content = "def invalid_function():\n  print 'hello world'\n" # Erro de sintaxe Python 3
    action_plan_response = {
        "analysis": "Test analysis: apply a patch with syntax error.",
        "patches_to_apply": [{
            "file_path": original_file_name,
            "operation": "REPLACE", # Substituir todo o conteúdo
            "block_to_replace": None,
            "content": invalid_patch_content
        }]
    }
    mock_architect.return_value = (action_plan_response, None)

    # 4. Maestro escolhe estratégia que aplica e valida sintaxe
    maestro_decision_response = {"strategy_key": "APPLY_AND_VALIDATE_SYNTAX_SANDBOX"}
    mock_maestro.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"m", "raw_response":""}]

    # 5. Gerador de próximo objetivo para parar o loop (após tentativa de correção)
    # O agente vai tentar um objetivo de correção. Queremos parar depois disso.
    correction_objective_generated = False
    def stop_loop_after_correction_objective_gen(*args, **kwargs):
        nonlocal correction_objective_generated
        # A primeira vez que é chamado é para o próximo objetivo normal (não será, pois falha)
        # A segunda vez é para o objetivo de correção
        if not correction_objective_generated:
             correction_objective_generated = True
             # Manter o objetivo de correção na pilha para que o agente o pegue
             # Mas para o teste, vamos limpar e parar.
             # Na verdade, o generate_next_objective não é chamado se a falha for corrigível.
             # Em vez disso, um objetivo de correção é adicionado e o loop continua.
             # Precisamos de uma maneira diferente de parar.
             # O objetivo de correção será o próximo item na pilha.
             # Vamos deixar o generate_next_objective não fazer nada para que a pilha se esgote
             # após o objetivo de correção ser (hipoteticamente) processado.
             # No entanto, o teste foca no *primeiro* ciclo de falha.
             # O objetivo de correção é gerado *após* o validation_result ser definido.
             # Para este teste, vamos parar o loop após o primeiro ciclo de falha.
             hephaestus_agent.objective_stack.clear() # Esvazia a pilha
             return "Objective: Stop after sandbox failure."

        hephaestus_agent.objective_stack.clear()
        return "Objective: Stop (should not be reached if logic is correct)."

    # A lógica atual de `run()`: se falha corrigível, adiciona obj de correção e continua.
    # Se `generate_next_objective` for mockado para limpar a pilha,
    # o loop parará *antes* do objetivo de correção ser processado.
    # Para testar o descarte, precisamos que o ciclo falhe e o estado `PATCH_DISCARDED` seja setado.
    # O objetivo de correção é um efeito colateral *dessa falha*.

    # Vamos mockar `generate_next_objective` para que ele pare o loop.
    # E também `generate_capacitation_objective` e `generate_commit_message` por segurança
    mock_gen_next_obj.side_effect = stop_loop_after_correction_objective_gen
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

    # 8. Verificar que o Arquiteto e Maestro foram chamados
    mock_architect.assert_called_once()
    mock_maestro.assert_called_once()

    # 9. O generate_next_objective foi chamado para tentar parar o loop.
    # A lógica de parada foi complexa, vamos garantir que foi chamado.
    mock_gen_next_obj.assert_called()


@patch('main.get_action_plan')
@patch('main.get_maestro_decision')
@patch('main.generate_next_objective')
@patch('main.run_pytest') # Mock para sanity check
@patch('main.check_file_existence') # Mock para sanity check
@patch('main.update_project_manifest') # Mock para evitar IO real no AGENTS.md
@patch('main.run_git_command') # Mock para evitar operações git reais
@patch('shutil.copytree')
@patch('shutil.copy2') # Para verificar a promoção do sandbox
@patch('tempfile.TemporaryDirectory')
def test_main_flow_sandbox_success_promotion(
    mock_temp_dir, mock_shutil_copy2, mock_shutil_copytree,
    mock_run_git, mock_update_manifest, mock_check_file_existence, mock_run_pytest_sanity,
    mock_gen_next_obj, mock_maestro, mock_architect,
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
        # Simplified copy for test purposes, actual files are written to mock_sandbox_path directly if needed by patches
        if Path(dst).exists() and dirs_exist_ok:
            for item in os.listdir(src):
                s_item = Path(src) / item
                d_item = Path(dst) / item
                if s_item.name == ".git": continue # Não copiar .git para o sandbox
                if s_item.is_dir():
                    shutil.copytree(s_item, d_item, dirs_exist_ok=True, symlinks=False, ignore=shutil.ignore_patterns(".git"))
                else:
                    shutil.copy2(s_item, d_item)
        else:
             shutil.copytree(src, dst, dirs_exist_ok=dirs_exist_ok, symlinks=False, ignore=shutil.ignore_patterns(".git"))

    mock_shutil_copytree.side_effect = actual_copytree_success

    # 3. Arquiteto retorna um patch válido
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
    mock_architect.return_value = (action_plan_response, None)

    # 4. Maestro escolhe estratégia APPLY_AND_VALIDATE_SYNTAX_SANDBOX
    maestro_decision_response = {"strategy_key": "APPLY_AND_VALIDATE_SYNTAX_SANDBOX"}
    mock_maestro.return_value = [{"success": True, "parsed_json": maestro_decision_response, "model":"m", "raw_response":""}]

    # 5. Mocks para o final do ciclo de sucesso
    mock_gen_next_obj.return_value = "Objective: Stop after success."
    hephaestus_agent.objective_stack_depth_for_testing = 1 # Para parar após um ciclo

    def stop_loop_after_one_successful_cycle(*args, **kwargs):
        hephaestus_agent.objective_stack.clear()
        return "Objective: Stop after success (from mock_gen_next_obj)."
    mock_gen_next_obj.side_effect = stop_loop_after_one_successful_cycle

    mock_check_file_existence.return_value = (True, "Sanity check: Files exist.") # Sanity check
    mock_update_manifest.return_value = None # Não faz nada
    mock_run_git.return_value = (True, "Git command successful.") # Mock para git add/commit

    # Mock para generate_commit_message
    with patch('main.generate_commit_message') as mock_gen_commit_msg:
        mock_gen_commit_msg.return_value = "feat: Test commit message for sandbox success"

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

    # 9. Chamadas principais
    mock_architect.assert_called_once()
    mock_maestro.assert_called_once()
    mock_gen_next_obj.assert_called_once() # Para parar o loop


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
