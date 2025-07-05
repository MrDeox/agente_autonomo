import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from collections import OrderedDict
from pathlib import Path
import csv
import logging

from agent.agents.maestro_agent import MaestroAgent, StrategyCache

@pytest.fixture
def mock_logger():
    return Mock(spec=logging.Logger)

@pytest.fixture
def sample_config():
    return {
        "models": {"maestro_default": {}},
        "validation_strategies": ["STRATEGY_A", "STRATEGY_B", "STRATEGY_C"]
    }

@pytest.fixture
def maestro_agent(sample_config, mock_logger):
    return MaestroAgent(sample_config, mock_logger)

class TestStrategyCache:
    def test_cache_initialization(self):
        cache = StrategyCache(max_size=50, ttl=1800)
        assert cache.max_size == 50
        assert cache.ttl == timedelta(seconds=1800)
        assert len(cache.cache) == 0

    def test_get_set_cache(self):
        cache = StrategyCache()
        test_data = {"key": "value"}
        
        # Test setting and getting from cache
        cache.set("test_key", test_data)
        result = cache.get({"key": "value"}, "")
        assert result == test_data
        
        # Test cache expiration
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(seconds=3601)
            result = cache.get({"key": "value"}, "")
            assert result is None

class TestMaestroAgent:
    def test_initialization(self, maestro_agent, sample_config, mock_logger):
        assert maestro_agent.config == sample_config
        assert maestro_agent.logger == mock_logger
        assert isinstance(maestro_agent.strategy_cache, StrategyCache)
        assert maestro_agent.performance_data == {}
        assert maestro_agent.strategy_weights == {}

    def test_load_historical_performance(self, maestro_agent, mock_logger, tmp_path):
        # Create test evolution log
        log_file = tmp_path / "evolution_log.csv"
        log_file.write_text("strategy,success\nSTRATEGY_A,true\nSTRATEGY_A,false\nSTRATEGY_B,true")
        
        with patch('pathlib.Path.exists', return_value=True):
            maestro_agent._load_historical_performance()
        
        assert "STRATEGY_A" in maestro_agent.performance_data
        assert maestro_agent.performance_data["STRATEGY_A"]["success_count"] == 1
        assert maestro_agent.performance_data["STRATEGY_A"]["failure_count"] == 1
        assert "STRATEGY_B" in maestro_agent.performance_data
        assert maestro_agent.performance_data["STRATEGY_B"]["success_count"] == 1

    def test_calculate_strategy_weights(self, maestro_agent):
        # Setup test performance data
        maestro_agent.performance_data = {
            "STRATEGY_A": {"success_count": 3, "failure_count": 1, "total_executions": 4, "average_metrics": {}},
            "STRATEGY_B": {"success_count": 1, "failure_count": 1, "total_executions": 2, "average_metrics": {}},
            "STRATEGY_C": {"success_count": 0, "failure_count": 0, "total_executions": 0, "average_metrics": {}}
        }
        
        maestro_agent._calculate_strategy_weights()
        
        # STRATEGY_A should have highest weight (75% success)
        assert maestro_agent.strategy_weights["STRATEGY_A"] > maestro_agent.strategy_weights["STRATEGY_B"]
        # STRATEGY_C should have default weight (0.5)
        assert maestro_agent.strategy_weights["STRATEGY_C"] == 0.5

    def test_select_strategy(self, maestro_agent):
        # Setup test weights
        maestro_agent.strategy_weights = {
            "STRATEGY_A": 0.8,
            "STRATEGY_B": 0.6,
            "STRATEGY_C": 0.4
        }
        
        context = {"patches_to_apply": [{"file_path": "test.py"}]}
        strategy = maestro_agent.select_strategy(context)
        
        # Should select highest weighted applicable strategy
        assert strategy["strategy_type"] == "STRATEGY_A"
        assert strategy["fallback_strategy"] == "STRATEGY_B"

    def test_record_performance(self, maestro_agent):
        strategy = {"strategy_type": "STRATEGY_X"}
        metrics = {"execution_time": 1.5, "memory_usage": 100}
        
        # First record (success)
        maestro_agent.record_performance(strategy, True, metrics)
        assert maestro_agent.performance_data["STRATEGY_X"]["success_count"] == 1
        assert maestro_agent.performance_data["STRATEGY_X"]["average_metrics"]["execution_time"] == 1.5
        
        # Second record (failure)
        maestro_agent.record_performance(strategy, False, metrics)
        assert maestro_agent.performance_data["STRATEGY_X"]["failure_count"] == 1
        
        # Check weight calculation
        assert maestro_agent.strategy_weights["STRATEGY_X"] == 0.5  # 1 success / 2 total

    def test_integrate_error_analyzer(self, maestro_agent):
        mock_error_analyzer = Mock()
        
        maestro_agent.integrate_error_analyzer(mock_error_analyzer)
        
        assert maestro_agent.error_analyzer == mock_error_analyzer
        maestro_agent.logger.info.assert_called_with("Successfully integrated ErrorAnalysisAgent with MaestroAgent")

    def test_choose_strategy_cache_hit(self, maestro_agent):
        context = {"patches_to_apply": [{"file_path": "test.py"}]}
        
        # Setup cache
        maestro_agent.strategy_cache.put(context, "", "CACHED_STRATEGY")
        
        result = maestro_agent.choose_strategy(context)
        assert result[0]["parsed_json"]["strategy_key"] == "CACHED_STRATEGY"
        maestro_agent.logger.info.assert_called_with("MaestroAgent: Cache hit! Using cached strategy: CACHED_STRATEGY")

    def test_choose_strategy_rule_based(self, maestro_agent):
        context = {"patches_to_apply": [{"file_path": "tests/test_file.py", "operation": "INSERT"}]}
        
        result = maestro_agent.choose_strategy(context)
        assert result[0]["parsed_json"]["strategy_key"] == "CREATE_NEW_TEST_FILE_STRATEGY"
        maestro_agent.logger.info.assert_called_with("Rule-based classification: Detected new test file creation.")

    def test_choose_strategy_weighted(self, maestro_agent):
        context = {"patches_to_apply": [{"file_path": "test.py"}]}
        maestro_agent.strategy_weights = {"STRATEGY_A": 0.9, "STRATEGY_B": 0.7}
        
        result = maestro_agent.choose_strategy(context)
        assert result[0]["parsed_json"]["strategy_key"] == "STRATEGY_A"
        maestro_agent.logger.info.assert_called_with("MaestroAgent: Selected strategy 'STRATEGY_A' based on weighted selection")