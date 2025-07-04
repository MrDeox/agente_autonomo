import pytest
from agent.cycle_runner import run_cycles, _initialize_cycle_state, _execute_evolution_step, _validate_cycle_results, _log_cycle_details
from agent.state import AgentState
from agent.memory import Memory
from agent.config_loader import load_validation_strategies


def test_run_cycles_initialization(mocker):
    """Testa a inicialização do estado do ciclo."""
    agent = HephaestusAgent()
    queue_manager = QueueManager()
    
    mock_load_strategies = mocker.patch('agent.cycle_runner.load_validation_strategies')
    mock_load_strategies.return_value = ['CYCLOMATIC_COMPLEXITY_CHECK']
    
    _initialize_cycle_state(agent, queue_manager)
    assert agent.state.current_cycle == 1
    assert agent.state.validation_strategies == ['CYCLOMATIC_COMPLEXITY_CHECK']


def test_run_cycles_validates_results(mocker):
    """Testa a validação de resultados com estratégia de complexidade."""
    agent = HephaestusAgent()
    queue_manager = QueueManager()
    mock_strategy = mocker.MagicMock()
    mock_strategy.validate.return_value = False
    mock_strategy.blocking = True
    
    agent.state.validation_strategies = [mock_strategy]
    task = {'output': 'test_output', 'metrics': {'cyclomatic_complexity': 35}}
    
    with pytest.raises(CycleValidationException):
        _validate_cycle_results(agent, task)
    mock_strategy.validate.assert_called_once_with(task['metrics'])