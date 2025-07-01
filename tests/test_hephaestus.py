import logging
import os
import json
import pytest
from unittest.mock import patch, MagicMock, call

# Adicionar imports necessários do seu projeto

# Configuração de logger para testes, se necessário
# Pode ser útil para depurar testes, mas geralmente não é necessário para asserções.
# logging.basicConfig(level=logging.DEBUG)
# test_logger = logging.getLogger("TestHephaestusAgent")


@pytest.fixture
def mock_logger():
    """Fixture para mockar o logger."""
    return MagicMock(spec=logging.Logger)

@pytest.fixture
def temp_config_file(tmp_path):
    """Cria um arquivo de configuração temporário para os testes."""
    config_data = {
        "models": {
            "objective_generator": "test-model-light",
            "architect_default": "test-model-architect",
            "maestro_default": {"primary": "test-model-maestro"},
            "capacitation_generator": "test-model-capacitation",
            "commit_message_generator": "test-model-commit"
        },
        "validation_strategies": {
            "DEFAULT_STRATEGY": {
                "steps": ["apply_patches_to_disk", "validate_syntax", "run_pytest_validation"],
                "sanity_check_step": "run_pytest"
            },
            "NO_OP_STRATEGY": {
                "steps": [],
                "sanity_check_step": "skip_sanity_check"
            }
        },
        "continuous_mode_delay_seconds": 0.1, # Pequeno delay para testes
        "cycle_delay_seconds": 0.1,
        "memory_file_path": str(tmp_path / "test_hephaestus_memory.json")
    }
    config_path = tmp_path / "test_hephaestus_config.json"
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock das variáveis de ambiente necessárias."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    # Adicione outras variáveis de ambiente se o agente as utilizar diretamente

@pytest.fixture
def agent_instance(mock_logger, temp_config_file, mock_env_vars, tmp_path):
    """Cria uma instância do HephaestusAgent com mocks para testes."""
    # Import HephaestusAgent here to ensure mocks are applied before instantiation
    from agent.hephaestus_agent import HephaestusAgent as MockableHephaestusAgent # Import with alias

    # Precisamos garantir que o diretório de trabalho seja o tmp_path para isolamento
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    # Mockear o arquivo de configuração para que ele use o temp_config_file
    with patch('agent.config_loader.load_config', return_value=json.load(open(temp_config_file))):
        # Patch git initialization before HephaestusAgent is instantiated
        with patch('agent.git_utils.initialize_git_repository', return_value=True) as mock_init_git:
                # Mock para evitar chamadas reais à API LLM
                with (
                    patch('agent.brain.call_llm_api', return_value=("Mocked LLM Response", None)) as mock_llm_call,
                    patch('agent.agents.call_llm_api', return_value=("Mocked LLM Response Agents", None)) as mock_llm_agents,
                    
                    patch('agent.cycle_runner.run_git_command', return_value=(True, "Mocked git output")) as mock_git,
                    patch('agent.cycle_runner.update_project_manifest') as mock_update_manifest,
                    patch(
                        'agent.validation_steps.patch_applicator.PatchApplicatorStep.execute',
                        return_value=(True, 'PATCH_APPLICATION_SUCCESS', '')
                    ) as mock_apply_patches,
                    patch(
                        'agent.validation_steps.syntax_validator.SyntaxValidator.execute',
                        return_value=(True, 'SYNTAX_VALIDATION_SUCCESS', '')
                    ) as mock_validate_syntax,
                    patch(
                        'agent.validation_steps.pytest_validator.PytestValidator.execute',
                        return_value=(True, 'PYTEST_SUCCESS', '')
                    ) as mock_run_pytest
                ):

                    # Garantir que não existe .git para forçar o caminho de inicialização
                    git_dir = tmp_path / ".git"
                    if git_dir.exists():
                        if git_dir.is_dir():
                            import shutil
                            shutil.rmtree(git_dir)
                        else:
                            git_dir.unlink()

                    # Criar arquivos e diretórios básicos que o agente pode esperar
                    (tmp_path / "tests").mkdir(exist_ok=True)
                    (tmp_path / "AGENTS.md").touch() # Para _generate_manifest

                    agent = MockableHephaestusAgent( # Use the aliased class
                        logger_instance=mock_logger,
                        config=json.load(open(temp_config_file)), # Pass the loaded config
                        continuous_mode=False, # Testar modo não contínuo por padrão
                        objective_stack_depth_for_testing=1 # Limitar a 1 ciclo para a maioria dos testes
                    )
                    # Anexar mocks ao agente para facilitar o acesso nos testes, se necessário
                    agent._mocks = {
                        "llm_brain": mock_llm_call,
                        "llm_agents": mock_llm_agents,
                        
                        "git": mock_git,
                        "manifest": mock_update_manifest,
                        "apply_patches": mock_apply_patches,
                        "validate_syntax": mock_validate_syntax,
                        "pytest": mock_run_pytest,
                        "init_git": mock_init_git
                    }
                    yield agent # Fornece a instância do agente para o teste

    # Restaurar o diretório de trabalho original
    os.chdir(original_cwd)


# Teste para a lógica de detecção de loop degenerativo
def test_degenerative_loop_detection(agent_instance, mock_logger):
    agent = agent_instance # Get the actual agent instance
    # Configurar a memória para simular falhas repetidas
    repeated_objective = "Objetivo Repetitivo com Falha"
    agent.memory.recent_objectives_log = [] # Limpar log recente

    # Adicionar 2 falhas (não deve disparar)
    agent.memory.add_failed_objective(repeated_objective, "reason1", "details1")
    agent.memory.add_failed_objective(repeated_objective, "reason2", "details2")

    agent.objective_stack = [repeated_objective]
    agent.continuous_mode = False # Para este teste, não precisa ser contínuo
    agent.objective_stack_depth_for_testing = 1 # Executar um ciclo

    # Mockear _generate_manifest para evitar erros, já que o objetivo não será processado
    with patch.object(agent, '_generate_manifest', return_value=True):
        agent.run()

    # Verificar se o log de erro NÃO foi chamado e o objetivo foi processado (ou tentado)
    # Isso é um pouco implícito. Se o loop não foi detectado, o ciclo tentaria rodar.
    # Precisamos garantir que o erro de loop degenerativo NÃO foi logado.
    loop_detected_error_call = call.error(f"Loop degenerativo detectado para o objetivo: \"{repeated_objective}\". Ocorreram 2 falhas consecutivas.")
    assert loop_detected_error_call not in mock_logger.method_calls
    # E que o objetivo foi removido da pilha (tentativa de processamento)
    assert not agent.objective_stack


    # Agora, adicionar a terceira falha para disparar a detecção
    agent.memory.add_failed_objective(repeated_objective, "reason3", "details3")
    assert len(agent.memory.recent_objectives_log) == 3 # 3 falhas para o mesmo objetivo

    # Reiniciar a pilha de objetivos
    agent.objective_stack = [repeated_objective]
    # Resetar mocks de log para verificar chamadas específicas desta execução
    mock_logger.reset_mock()

    with patch.object(agent, '_generate_manifest', return_value=True) as mock_gen_manifest:
        agent.run()

    # Verificar se o log de erro FOI chamado
    expected_error_msg = f"Loop degenerativo detectado para o objetivo: \"{repeated_objective}\". Ocorreram 3 falhas consecutivas."
    mock_logger.error.assert_any_call(expected_error_msg)

    # Verificar se o objetivo foi registrado como falha de loop degenerativo na memória
    assert any(
        entry["objective"] == repeated_objective and entry["reason"] == "DEGENERATIVE_LOOP_DETECTED"
        for entry in agent.memory.failed_objectives
    )
    # Verificar se o objetivo problemático não está mais na pilha e não foi processado
    assert not agent.objective_stack
    mock_gen_manifest.assert_not_called() # Não deve nem começar a processar o objetivo


def test_degenerative_loop_break_success_interspersed(agent_instance, mock_logger):
    agent = agent_instance # Get the actual agent instance
    """Testa se um sucesso entre falhas reseta a contagem do loop degenerativo."""
    objective = "Objetivo com Sucesso Intercalado"
    agent.memory.recent_objectives_log = []

    agent.memory.add_failed_objective(objective, "f1", "d1")
    agent.memory.add_failed_objective(objective, "f2", "d2")
    agent.memory.add_completed_objective(objective, "s1", "d_comp") # Sucesso!
    agent.memory.add_failed_objective(objective, "f3", "d3") # Terceira falha, mas após um sucesso

    agent.objective_stack = [objective]
    agent.objective_stack_depth_for_testing = 1

    # Mockar as fases do ciclo para que ele "execute" o objetivo
    agent._mocks["llm_brain"].return_value = ("{\"analysis\": \"mock analysis\", \"patches_to_apply\": []}", None) # Arquiteto
    agent._mocks["llm_agents"].return_value = ("{\"strategy_key\": \"NO_OP_STRATEGY\"}", None) # Maestro

    with patch.object(agent, '_generate_manifest', return_value=True) as mock_gen_manifest:
        agent.run()

    # O loop degenerativo NÃO deve ser detectado
    loop_detected_error_call_pattern = f"Loop degenerativo detectado para o objetivo: \"{objective}\"."
    for log_call in mock_logger.error.call_args_list:
        assert loop_detected_error_call_pattern not in log_call[0][0]

    # O objetivo deve ter sido processado (manifesto gerado)
    mock_gen_manifest.assert_called_once()
    # E o objetivo de sucesso deve ter sido adicionado à memória (isso já foi feito no setup do teste,
    # mas a run() também adicionará se a estratégia for bem sucedida)
    # O importante é que o ciclo rodou.


# Adicionar mais testes para HephaestusAgent conforme necessário,
# por exemplo, para testar o modo contínuo, diferentes estratégias, etc.
# Estes testes podem se tornar complexos devido à natureza integrada do agente.
# Considere testes mais focados (unitários) para os componentes individuais (Architect, Maestro, etc.)
# em seus próprios arquivos de teste.

def test_dummy(): # Manter ou remover se não for mais necessário
    assert True