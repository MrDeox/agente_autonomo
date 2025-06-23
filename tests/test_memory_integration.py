import pytest
import json
import os
import shutil
import builtins # Import for robust access to original open
from unittest.mock import patch, MagicMock, call, mock_open

from main import HephaestusAgent # Assuming main.py contains HephaestusAgent
from agent.memory import Memory

# Minimal config for testing
@pytest.fixture
def temp_config_file_integration(tmp_path):
    config_data = {
        "memory_file_path": str(tmp_path / "test_agent_memory_integration.json"),
        "models": {
            "objective_generator": "test_objective_model",
            "architect_default": "test_architect_model",
            "maestro_default": "test_maestro_model",
            "capacitation_generator": "test_capacitation_model",
            "commit_message_generator": "test_commit_model"
        },
        "validation_strategies": {
            "successful_strategy": {
                "steps": ["apply_patches_to_disk", "run_pytest_validation"],
                "sanity_check_step": "skip_sanity_check"
            },
            "failing_strategy": {
                "steps": ["apply_patches_to_disk", "run_pytest_validation"],
                "sanity_check_step": "skip_sanity_check"
            }
        },
        "cycle_delay_seconds": 0
    }
    config_file = tmp_path / "test_config_integration.json"
    # Use the real open to write the temp config file
    with builtins.open(config_file, 'w') as f:
        json.dump(config_data, f)
    return str(config_file)

@pytest.fixture
def agent_instance_integration(temp_config_file_integration, tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_api_key_value")

    def mock_load_config_integration():
        # This open should be the real one to read the temp JSON config file
        # It will be handled by the smart_open_side_effect if it's not specific enough,
        # or directly by original_real_open if the patch isn't active yet.
        with builtins.open(temp_config_file_integration, "r") as f:
            return json.load(f)

    original_real_open = builtins.open

    def smart_open_side_effect(file_path, mode='r', *args, **kwargs):
        file_path_str = str(file_path)
        if file_path_str.endswith("AGENTS.md") and 'r' in mode:
            return mock_open(read_data="Manifest content for AGENTS.md")()
        # Delegate to the original open for other files (like config, memory json)
        return original_real_open(file_path_str, mode, *args, **kwargs)

    # Patch HephaestusAgent.load_config to use our function that reads the temp JSON config
    with patch('main.HephaestusAgent.load_config', side_effect=mock_load_config_integration):
        with patch('main.HephaestusAgent._initialize_git_repository', return_value=True):
            with patch('agent.project_scanner.update_project_manifest'):
                # Patch builtins.open globally within this context with our smart side_effect
                with patch('builtins.open', side_effect=smart_open_side_effect):
                    with patch('shutil.copytree'):
                        with patch('tempfile.TemporaryDirectory') as mock_tempdir:
                            mock_sandbox_path = tmp_path / "sandbox_integration"
                            mock_sandbox_path.mkdir(exist_ok=True)
                            mock_tempdir.return_value.__enter__.return_value = str(mock_sandbox_path)

                            logger_mock = MagicMock()
                            agent = HephaestusAgent(logger_instance=logger_mock)
                            # Ensure agent's memory filepath is from the (mocked) config
                            agent.memory.filepath = agent.config["memory_file_path"]
                            # Clean and load memory to ensure fresh state for test
                            if os.path.exists(agent.memory.filepath):
                                os.remove(agent.memory.filepath)
                            agent.memory.load()
                            yield agent
                            # Cleanup
                            if os.path.exists(agent.memory.filepath):
                                os.remove(agent.memory.filepath)

# --- Mocks for Brain Functions (can be redefined per test if needed) ---
mock_generate_next_objective_integration = MagicMock(return_value="Test Objective Integration 1")
mock_get_action_plan_integration = MagicMock(return_value=({"analysis": "Test analysis", "patches_to_apply": [{"file_path": "test.py", "operation": "INSERT", "content": "print('hello')"}]}, None))
mock_get_maestro_decision_success_integration = MagicMock(return_value=[{"success": True, "parsed_json": {"strategy_key": "successful_strategy"}}])
mock_generate_commit_message_integration = MagicMock(return_value="feat: Test commit integration")

# --- Mocks for Tool Executor Functions ---
mock_run_pytest_success_integration = MagicMock(return_value=(True, "Pytest success integration"))
mock_run_pytest_fail_integration = MagicMock(return_value=(False, "Pytest failed integration"))
mock_apply_patches_integration = MagicMock()


@patch('main.apply_patches', new_callable=lambda: mock_apply_patches_integration)
@patch('main.generate_commit_message', new_callable=lambda: mock_generate_commit_message_integration)
@patch('main.get_action_plan', new_callable=lambda: mock_get_action_plan_integration)
@patch('main.generate_next_objective', new_callable=lambda: mock_generate_next_objective_integration)
def test_successful_cycle_logs_to_memory_integration(
    mock_gen_next_obj,
    mock_get_action_plan,
    mock_gen_commit,
    mock_apply_patches,
    agent_instance_integration,
    temp_config_file_integration # Fixture needed for new_agent instantiation part
):
    agent = agent_instance_integration
    memory_file = agent.memory.filepath

    mock_generate_next_objective_integration.side_effect = None # Clear any previous side_effect
    mock_generate_next_objective_integration.return_value = "Initial Objective for Success Test Integration"

    with patch('main.get_maestro_decision', new_callable=lambda: mock_get_maestro_decision_success_integration):
        with patch('main.run_pytest', new_callable=lambda: mock_run_pytest_success_integration):
            agent.objective_stack = ["Initial Objective for Success Test Integration"]
            agent.run()

            assert len(agent.memory.completed_objectives) == 1
            completed_obj = agent.memory.completed_objectives[0]
            assert completed_obj["objective"] == "Initial Objective for Success Test Integration"

            assert os.path.exists(memory_file)
            with builtins.open(memory_file, 'r') as f: data_in_file = json.load(f) # Use real open
            assert len(data_in_file["completed_objectives"]) == 1
            assert data_in_file["completed_objectives"][0]["objective"] == "Initial Objective for Success Test Integration"

            new_logger_mock = MagicMock()
            def mock_load_conf_new_success(): # Renamed for clarity
                with builtins.open(temp_config_file_integration, "r") as f_new: return json.load(f_new) # Use real open

            with patch('main.HephaestusAgent.load_config', side_effect=mock_load_conf_new_success):
                 with patch('main.HephaestusAgent._initialize_git_repository', return_value=True):
                    # The smart_open_side_effect will handle AGENTS.md for the new agent too if it's still in scope
                    # or if we re-patch builtins.open for this specific instantiation.
                    # For this test, the new_agent creation is inside the original agent_instance_integration's builtins.open patch scope.
                    # However, the fixture `agent_instance_integration` has `yield agent`.
                    # The `with patch('builtins.open', side_effect=smart_open_side_effect)` from the fixture
                    # might not be active when this part of the test runs for `new_agent`.
                    # Let's re-apply the smart open patch for the new agent instantiation.
                    original_real_open_new_agent = builtins.open
                    def smart_open_new_agent(fp, m='r', *a, **kw):
                        if str(fp).endswith("AGENTS.md") and 'r' in m:
                            return mock_open(read_data="Manifest for new agent")()
                        return original_real_open_new_agent(fp, m, *a, **kw)

                    with patch('builtins.open', side_effect=smart_open_new_agent):
                        new_agent = HephaestusAgent(logger_instance=new_logger_mock)
                        assert new_agent.memory.filepath == memory_file
                        assert len(new_agent.memory.completed_objectives) == 1


@patch('main.apply_patches', new_callable=lambda: mock_apply_patches_integration)
@patch('main.get_action_plan', new_callable=lambda: mock_get_action_plan_integration)
@patch('main.generate_next_objective', new_callable=lambda: mock_generate_next_objective_integration)
def test_failed_cycle_logs_to_memory_integration(
    mock_gen_next_obj,
    mock_get_action_plan,
    mock_apply_patches,
    agent_instance_integration
):
    agent = agent_instance_integration
    memory_file = agent.memory.filepath

    mock_generate_next_objective_integration.side_effect = ["Objective that will fail Integration", "Corrective objective placeholder"]
    mock_get_maestro_decision_fail_integration = MagicMock(return_value=[{"success": True, "parsed_json": {"strategy_key": "failing_strategy"}}])

    with patch('main.get_maestro_decision', new_callable=lambda: mock_get_maestro_decision_fail_integration):
        with patch('main.run_pytest', new_callable=lambda: mock_run_pytest_fail_integration):
            agent.objective_stack = ["Initial Objective for Failure Test Integration"]
            agent.run()

            assert len(agent.memory.failed_objectives) == 1
            failed_obj = agent.memory.failed_objectives[0]
            assert failed_obj["objective"] == "Initial Objective for Failure Test Integration"
            assert failed_obj["reason"] == "PYTEST_FAILURE_IN_SANDBOX"

            assert os.path.exists(memory_file)
            with builtins.open(memory_file, 'r') as f: data_in_file = json.load(f) # Use real open
            assert len(data_in_file["failed_objectives"]) == 1


@patch('main.get_action_plan', new_callable=lambda: mock_get_action_plan_integration)
@patch('main.apply_patches', new_callable=lambda: mock_apply_patches_integration)
@patch('main.generate_commit_message', new_callable=lambda: mock_generate_commit_message_integration)
def test_capacitation_objective_logs_capability_on_success_integration(
    mock_gen_commit,
    mock_apply_patches,
    mock_get_action_plan,
    agent_instance_integration
):
    agent = agent_instance_integration
    memory_file = agent.memory.filepath

    capacitation_objective_text = "[TAREFA DE CAPACITAÇÃO] Create a new tool integration"
    mock_gen_cap_obj_integration = MagicMock(return_value=capacitation_objective_text)

    mock_get_maestro_decision_cap_needed_integration = MagicMock(return_value=[{"success": True, "parsed_json": {"strategy_key": "CAPACITATION_REQUIRED"}}])
    mock_get_maestro_decision_for_cap_success_integration = MagicMock(return_value=[{"success": True, "parsed_json": {"strategy_key": "successful_strategy"}}])

    mock_generate_next_objective_integration.side_effect = ["Original Objective Requiring Capacitation Int", "Next Objective After Capacitation Int"]

    with patch('main.generate_capacitation_objective', new_callable=lambda: mock_gen_cap_obj_integration):
        with patch('main.get_maestro_decision', side_effect=[mock_get_maestro_decision_cap_needed_integration.return_value, mock_get_maestro_decision_for_cap_success_integration.return_value]):
            with patch('main.run_pytest', new_callable=lambda: mock_run_pytest_success_integration):
                agent.objective_stack = ["Original Objective Requiring Capacitation Int"]
                agent.run()

                assert len(agent.memory.completed_objectives) == 1
                assert agent.memory.completed_objectives[0]["objective"] == capacitation_objective_text
                assert len(agent.memory.acquired_capabilities) == 1
                assert agent.memory.acquired_capabilities[0]["description"].startswith("Capacitation task completed")

                assert os.path.exists(memory_file)
                with builtins.open(memory_file, 'r') as f: data_in_file = json.load(f) # Use real open
                assert len(data_in_file["acquired_capabilities"]) == 1
                assert data_in_file["acquired_capabilities"][0]["description"].startswith("Capacitation task completed")
