
import pandas as pd
import pytest
from agent.performance_analyzer import PerformanceAnalysisAgent

@pytest.fixture
def mock_log_file(tmp_path):
    def _mock_log_file(data):
        log_file = tmp_path / "evolution_log.csv"
        if data:
            df = pd.DataFrame(data)
            df.to_csv(log_file, index=False)
        else:
            log_file.touch()
        return str(log_file)
    return _mock_log_file

def test_analyze_performance_no_log_file():
    agent = PerformanceAnalysisAgent(evolution_log_path="non_existent_log.csv")
    summary = agent.analyze_performance()
    assert "Evolution log not found" in summary

def test_analyze_performance_empty_log_file(mock_log_file):
    log_file = mock_log_file(None)
    agent = PerformanceAnalysisAgent(evolution_log_path=log_file)
    summary = agent.analyze_performance()
    assert "Evolution log is empty" in summary

def test_analyze_performance_with_data(mock_log_file):
    data = {
        "success": [True, False, True, True, False],
    }
    log_file = mock_log_file(data)
    agent = PerformanceAnalysisAgent(evolution_log_path=log_file)
    summary = agent.analyze_performance()

    assert "Total Cycles: 5" in summary
    assert "Successful Cycles: 3" in summary
    assert "Failed Cycles: 2" in summary
    assert "Success Rate: 60.00%" in summary
