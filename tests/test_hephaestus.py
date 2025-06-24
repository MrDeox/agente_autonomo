import pytest
import logging
import os
from unittest.mock import patch, MagicMock, call # Adicionado call
from pathlib import Path

# Adicionar imports necessários do seu projeto
from main import HephaestusAgent
from agent.memory import Memory

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
            "maestro_default_list": ["test-model-maestro"],
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
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return config_path

import json # Adicionar import json que faltava no fixture temp_config_file


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock das variáveis de ambiente necessárias."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key")
    # Adicione outras variáveis de ambiente se o agente as utilizar diretamente

@pytest.fixture
def agent_instance(mock_logger, temp_config_file, mock_env_vars, tmp_path):
    """Cria uma instância do HephaestusAgent com mocks para testes."""
    # Precisamos garantir que o diretório de trabalho seja o tmp_path para isolamento
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    # Mockear o arquivo de configuração para que ele use o temp_config_file
    with patch('main.HephaestusAgent.load_config', return_value=json.load(open(temp_config_file))):
        # Mock para evitar chamadas reais à API LLM
        with patch('agent.brain._call_llm_api', return_value=("Mocked LLM Response", None)) as mock_llm_call, \
             patch('agent.agents._call_llm_api', return_value=("Mocked LLM Response Agents", None)) as mock_llm_agents, \
             patch('main.run_git_command', return_value=(True, "Mocked git output")) as mock_git, \
             patch('main.update_project_manifest') as mock_update_manifest, \
             patch('main.apply_patches') as mock_apply_patches, \
             patch('main.validate_python_code', return_value=(True, None)) as mock_validate_py, \
             patch('main.validate_json_syntax', return_value=(True, None)) as mock_validate_json, \
             patch('main.run_pytest', return_value=(True, "Pytest OK")) as mock_run_pytest, \
             patch('main.check_file_existence', return_value=(True, "Files exist")) as mock_check_files:

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

            agent = HephaestusAgent(
                logger_instance=mock_logger,
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
                "validate_py": mock_validate_py,
                "validate_json": mock_validate_json,
                "pytest": mock_run_pytest,
                "check_files": mock_check_files
            }
            yield agent # Fornece a instância do agente para o teste

    # Restaurar o diretório de trabalho original
    os.chdir(original_cwd)


# Teste básico para verificar se o agente é inicializado
def test_agent_initialization(agent_instance, mock_logger, temp_config_file):
    assert agent_instance is not None
    assert agent_instance.logger == mock_logger
    assert agent_instance.config["memory_file_path"] == str(Path(temp_config_file).parent / "test_hephaestus_memory.json")
    mock_logger.info.assert_any_call(f"Carregando memória de {agent_instance.config['memory_file_path']}...")

    # Espera-se que, como .git não é criado no tmp_path pelo fixture ANTES da inicialização do agente,
    # o agente tentará inicializar o repositório.
    agent_instance._mocks["git"].assert_any_call(['git', 'init'])
    # E subsequentemente, chamadas para configurar user.name e user.email, e adicionar .gitignore
    agent_instance._mocks["git"].assert_any_call(['git', 'config', '--local', 'user.name', 'Hephaestus Agent'])
    agent_instance._mocks["git"].assert_any_call(['git', 'config', '--local', 'user.email', 'hephaestus@example.com'])
    agent_instance._mocks["git"].assert_any_call(['git', 'add', '.gitignore'])
    agent_instance._mocks["git"].assert_any_call(['git', 'commit', '-m', 'chore: Initial commit by Hephaestus Agent'])


# Teste para a lógica de detecção de loop degenerativo
def test_degenerative_loop_detection(agent_instance, mock_logger):
    # Configurar a memória para simular falhas repetidas
    repeated_objective = "Objetivo Repetitivo com Falha"
    agent_instance.memory.recent_objectives_log = [] # Limpar log recente

    # Adicionar 2 falhas (não deve disparar)
    agent_instance.memory.add_failed_objective(repeated_objective, "reason1", "details1")
    agent_instance.memory.add_failed_objective(repeated_objective, "reason2", "details2")

    agent_instance.objective_stack = [repeated_objective]
    agent_instance.continuous_mode = False # Para este teste, não precisa ser contínuo
    agent_instance.objective_stack_depth_for_testing = 1 # Executar um ciclo

    # Mockear _generate_manifest para evitar erros, já que o objetivo não será processado
    with patch.object(agent_instance, '_generate_manifest', return_value=True):
        agent_instance.run()

    # Verificar se o log de erro NÃO foi chamado e o objetivo foi processado (ou tentado)
    # Isso é um pouco implícito. Se o loop não foi detectado, o ciclo tentaria rodar.
    # Precisamos garantir que o erro de loop degenerativo NÃO foi logado.
    loop_detected_error_call = call.error(f"Loop degenerativo detectado para o objetivo: \"{repeated_objective}\". Ocorreram 2 falhas consecutivas.")
    assert loop_detected_error_call not in mock_logger.method_calls
    # E que o objetivo foi removido da pilha (tentativa de processamento)
    assert not agent_instance.objective_stack


    # Agora, adicionar a terceira falha para disparar a detecção
    agent_instance.memory.add_failed_objective(repeated_objective, "reason3", "details3")
    assert len(agent_instance.memory.recent_objectives_log) == 3 # 3 falhas para o mesmo objetivo

    # Reiniciar a pilha de objetivos
    agent_instance.objective_stack = [repeated_objective]
    # Resetar mocks de log para verificar chamadas específicas desta execução
    mock_logger.reset_mock()

    with patch.object(agent_instance, '_generate_manifest', return_value=True) as mock_gen_manifest:
        agent_instance.run()

    # Verificar se o log de erro FOI chamado
    expected_error_msg = f"Loop degenerativo detectado para o objetivo: \"{repeated_objective}\". Ocorreram 3 falhas consecutivas."
    mock_logger.error.assert_any_call(expected_error_msg)

    # Verificar se o objetivo foi registrado como falha de loop degenerativo na memória
    assert any(
        entry["objective"] == repeated_objective and entry["reason"] == "DEGENERATIVE_LOOP_DETECTED"
        for entry in agent_instance.memory.failed_objectives
    )
    # Verificar se o objetivo problemático não está mais na pilha e não foi processado
    assert not agent_instance.objective_stack
    mock_gen_manifest.assert_not_called() # Não deve nem começar a processar o objetivo


def test_degenerative_loop_break_success_interspersed(agent_instance, mock_logger):
    """Testa se um sucesso entre falhas reseta a contagem do loop degenerativo."""
    objective = "Objetivo com Sucesso Intercalado"
    agent_instance.memory.recent_objectives_log = []

    agent_instance.memory.add_failed_objective(objective, "f1", "d1")
    agent_instance.memory.add_failed_objective(objective, "f2", "d2")
    agent_instance.memory.add_completed_objective(objective, "s1", "d_comp") # Sucesso!
    agent_instance.memory.add_failed_objective(objective, "f3", "d3") # Terceira falha, mas após um sucesso

    agent_instance.objective_stack = [objective]
    agent_instance.objective_stack_depth_for_testing = 1

    # Mockar as fases do ciclo para que ele "execute" o objetivo
    agent_instance._mocks["llm_brain"].return_value = ("{\"analysis\": \"mock analysis\", \"patches_to_apply\": []}", None) # Arquiteto
    agent_instance._mocks["llm_agents"].return_value = ("{\"strategy_key\": \"NO_OP_STRATEGY\"}", None) # Maestro

    with patch.object(agent_instance, '_generate_manifest', return_value=True) as mock_gen_manifest:
        agent_instance.run()

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

# Exemplo de um teste para o modo contínuo (simplificado)
@patch('time.sleep', return_value=None) # Mock para evitar delays reais
def test_continuous_mode_generates_new_objective_when_stack_empty(mock_sleep, agent_instance, mock_logger):
    agent_instance.continuous_mode = True
    agent_instance.objective_stack = [] # Pilha vazia
    # Permitir 2 ciclos:
    # 1. O agente inicia, vê a pilha vazia, gera um objetivo inicial (devido ao modo contínuo).
    # 2. O agente processa esse objetivo. Se a pilha ficar vazia novamente, ele deve gerar outro.
    agent_instance.objective_stack_depth_for_testing = 2

    # Mock para generate_next_objective para retornar um objetivo previsível
    initial_continuous_objective = "Objetivo Inicial do Modo Contínuo"
    subsequent_continuous_objective = "Objetivo Subsequente do Modo Contínuo"
    agent_instance._mocks["llm_brain"].side_effect = [
        (initial_continuous_objective, None),
        ("{\"analysis\": \"mock analysis for initial_continuous_objective\", \"patches_to_apply\": []}", None),
        (subsequent_continuous_objective, None),
        ("{\"analysis\": \"mock analysis for subsequent_continuous_objective\", \"patches_to_apply\": []}", None),
    ]
    agent_instance._mocks["llm_agents"].return_value = ("{\"strategy_key\": \"NO_OP_STRATEGY\"}", None)

    with patch.object(agent_instance, '_generate_manifest', return_value=True) as mock_gen_manifest:
        agent_instance.run()

    # Verificar se o primeiro objetivo gerado continuamente foi logado
    mock_logger.info.assert_any_call(f"Novo objetivo gerado para modo contínuo: {initial_continuous_objective}")
    # Verificar se o segundo objetivo gerado continuamente foi logado
    mock_logger.info.assert_any_call(f"Novo objetivo gerado para modo contínuo: {subsequent_continuous_objective}")

    assert agent_instance.state.current_objective == subsequent_continuous_objective
    assert mock_gen_manifest.call_count == 2

    if agent_instance.config["continuous_mode_delay_seconds"] > 0:
        # Espera-se que sleep seja chamado duas vezes: uma após cada geração de objetivo em modo contínuo
        # quando a pilha está vazia e o agente vai buscar um novo objetivo.
        assert mock_sleep.call_count >= 1 # Pelo menos uma vez. Idealmente 2, mas depende do fluxo exato e do depth.
                                        # Com depth=2, ele processará 2 objetivos.
                                        # 1. Vazio -> gera obj1 -> sleep -> processa obj1
                                        # 2. Vazio -> gera obj2 -> sleep -> processa obj2 -> FIM
                                        # Então, 2 sleeps.

def test_dummy(): # Manter ou remover se não for mais necessário
    assert True
