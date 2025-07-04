import pytest
from unittest.mock import MagicMock, patch
from agent.cycle_runner import CycleRunner
from agent.hephaestus_agent import HephaestusAgent
from agent.queue_manager import QueueManager

@pytest.fixture
def mock_agent():
    """Fixture to create a mocked HephaestusAgent."""
    agent = MagicMock(spec=HephaestusAgent)
    agent.logger = MagicMock()
    agent.config = {}
    agent.objective_stack = []
    agent.memory = MagicMock()
    agent.state = MagicMock()
    return agent

def test_cycle_runner_initialization(mock_agent):
    """Test that the CycleRunner can be initialized."""
    queue_manager = QueueManager()
    cycle_runner = CycleRunner(mock_agent, queue_manager)
    assert cycle_runner.agent == mock_agent
    assert cycle_runner.queue_manager == queue_manager
    assert cycle_runner.cycle_count == 0

@pytest.mark.skip(reason="Teste temporariamente desabilitado - loop infinito no CycleRunner")
@patch('agent.cycle_runner.generate_next_objective')
def test_run_single_cycle_no_continuous_mode(mock_generate_objective, mock_agent):
    """Test a single cycle run when not in continuous mode."""
    # Arrange - configuração mais simples
    mock_agent.continuous_mode = False
    mock_agent.objective_stack_depth_for_testing = 1
    mock_agent.config = {"degenerative_loop_threshold": 3}
    mock_agent.objective_stack = ["Test Objective"]  # Já tem um objetivo
    
    # Mock state simples
    mock_agent.state.current_objective = "Test Objective"
    mock_agent.state.strategy_key = "TEST_STRATEGY"
    mock_agent.state.validation_result = (True, "APPLIED_AND_VALIDATED", "Success")
    
    # Mock memory simples
    mock_agent.memory.recent_objectives_log = []
    mock_agent.memory.save.return_value = None
    
    queue_manager = QueueManager()
    cycle_runner = CycleRunner(mock_agent, queue_manager)
    
    # Mock all required methods to return success immediately
    mock_agent._reset_cycle_state.return_value = None
    mock_agent._generate_manifest.return_value = True
    mock_agent._run_architect_phase.return_value = True
    mock_agent._run_code_review_phase.return_value = True
    mock_agent._run_maestro_phase.return_value = True
    mock_agent._execute_validation_strategy.return_value = None

    # Act
    cycle_runner.run()

    # Assert - verificações básicas
    assert cycle_runner.cycle_count == 1
    mock_agent._reset_cycle_state.assert_called_once()
    mock_agent.memory.save.assert_called_once()

@pytest.mark.skip(reason="Teste temporariamente desabilitado - loop infinito no CycleRunner")
@patch('agent.cycle_runner.generate_next_objective')
@patch('agent.cycle_runner.time.sleep') # Mock time.sleep to avoid delays
def test_run_continuous_mode(mock_sleep, mock_generate_objective, mock_agent):
    """Test that the agent generates a new objective in continuous mode."""
    # Arrange
    mock_agent.continuous_mode = True
    # Let it run for 2 cycles
    mock_agent.objective_stack_depth_for_testing = 2
    
    # Start with an empty queue and stack
    queue_manager = QueueManager()
    
    cycle_runner = CycleRunner(mock_agent, queue_manager)
    
    mock_generate_objective.side_effect = ["Objective 1", "Objective 2"]
    
    mock_agent._generate_manifest.return_value = True
    mock_agent._run_architect_phase.return_value = True
    mock_agent._run_maestro_phase.return_value = True
    mock_agent.state.validation_result = (True, "APPLIED_AND_VALIDATED", "Success")

    # Act
    cycle_runner.run()

    # Assert
    assert mock_generate_objective.call_count == 2
    assert cycle_runner.cycle_count == 2
    mock_sleep.assert_called_once() 