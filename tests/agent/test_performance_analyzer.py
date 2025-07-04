import pandas as pd
import pytest
from agent.agents import PerformanceAnalysisAgent # Updated import

@pytest.fixture
def mock_log_file(tmp_path):
    def _mock_log_file(data):
        log_file = tmp_path / "logs" / "evolution_log.csv"
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
            "status": ["sucesso", "falha", "sucesso", "sucesso", "falha", "sucesso"],
            "estrategia_usada": ["SYNTAX_AND_PYTEST", "SYNTAX_ONLY", "FULL_VALIDATION", "SYNTAX_AND_PYTEST", "SYNTAX_ONLY", "FULL_VALIDATION"],
            "duration_seconds": [100, 150, 200, 120, 180, 90]
        }
    log_file = mock_log_file(data)
    agent = PerformanceAnalysisAgent(evolution_log_path=log_file)
    summary = agent.analyze_performance()

    assert "Total Cycles: 6" in summary
    assert "Successful Cycles: 4" in summary
    assert "Failed Cycles: 2" in summary
    assert "Success Rate: 66.67%" in summary
    assert "Average Cycle Duration: 140.00 seconds" in summary
    assert "Performance by Strategy (sorted by failures):" in summary
    assert "- Strategy 'SYNTAX_ONLY': Success Rate: 0.00% (Failures: 2/2)" in summary
    assert "- Strategy 'SYNTAX_AND_PYTEST': Success Rate: 100.00% (Failures: 0/2)" in summary
    assert "- Strategy 'FULL_VALIDATION': Success Rate: 100.00% (Failures: 0/2)" in summary