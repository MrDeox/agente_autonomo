import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from collections import OrderedDict
from pathlib import Path

from agent.agents.maestro_agent import StrategyCache, MaestroAgent

class TestStrategyCache:
    def test_cache_initialization(self):
        """Test that the cache initializes correctly."""
        cache = StrategyCache(max_size=50, ttl=3600)
        assert cache.max_size == 50
        assert cache.ttl == timedelta(seconds=3600)
        assert isinstance(cache.cache, OrderedDict)
        assert len(cache.cache) == 0

    def test_get_and_set(self):
        """Test basic cache get and set operations."""
        cache = StrategyCache()
        test_data = {"key": "value"}
        
        # Test setting and getting
        cache.set("test_key", test_data)
        retrieved = cache.get({"key": "value"}, "")
        assert retrieved == test_data
        
        # Test cache eviction when max size is reached
        small_cache = StrategyCache(max_size=2)
        small_cache.set("key1", "value1")
        small_cache.set("key2", "value2")
        small_cache.set("key3", "value3")
        assert "key1" not in small_cache.cache
        assert "key2" in small_cache.cache
        assert "key3" in small_cache.cache

    def test_cache_expiration(self):
        """Test that cache entries expire after TTL."""
        cache = StrategyCache(ttl=1)  # 1 second TTL
        test_data = {"key": "value"}
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1)
            cache.set("test_key", test_data)
            
            # Should still be valid
            mock_datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 0, 999999)
            assert cache.get({"key": "value"}, "") == test_data
            
            # Should be expired
            mock_datetime.now.return_value = datetime(2023, 1, 1, 0, 0, 1)
            assert cache.get({"key": "value"}, "") is None

class TestMaestroAgent:
    @pytest.fixture
    def mock_config(self):
        return {
            "models": {"maestro_default": {}},
            "validation_strategies": [
                "CREATE_NEW_TEST_FILE_STRATEGY",
                "CONFIG_UPDATE_STRATEGY",
                "DOC_UPDATE_STRATEGY",
                "sandbox_validation_no_tests"
            ]
        }

    @pytest.fixture
    def mock_logger(self):
        return MagicMock()

    @pytest.fixture
    def maestro(self, mock_config, mock_logger):
        return MaestroAgent(mock_config, mock_logger)

    def test_initialization(self, maestro):
        """Test that the MaestroAgent initializes correctly."""
        assert isinstance(maestro.strategy_cache, StrategyCache)
        assert isinstance(maestro.performance_data, dict)
        assert isinstance(maestro.strategy_weights, dict)
        assert maestro.logger is not None

    def test_load_historical_performance(self, maestro, mock_logger, tmp_path):
        """Test loading historical performance from evolution_log.csv."""
        # Create a test CSV file
        log_file = tmp_path / "evolution_log.csv"
        log_file.write_text(
            "strategy,success,metrics\n"
            "strategy1,true,\"{}\"\n"
            "strategy1,false,\"{}\"\n"
            "strategy2,true,\"{}\"\n"
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', unittest.mock.mock_open(read_data=log_file.read_text())):
                maestro._load_historical_performance()
        
        assert "strategy1" in maestro.performance_data
        assert "strategy2" in maestro.performance_data
        assert maestro.performance_data["strategy1"]["success_count"] == 1
        assert maestro.performance_data["strategy1"]["failure_count"] == 1
        assert maestro.performance_data["strategy2"]["success_count"] == 1

    def test_calculate_strategy_weights(self, maestro):
        """Test calculation of strategy weights based on performance."""
        maestro.performance_data = {
            "strategy1": {"success_count": 8, "failure_count": 2, "total_executions": 10},
            "strategy2": {"success_count": 5, "failure_count": 5, "total_executions": 10},
            "strategy3": {"success_count": 1, "failure_count": 9, "total_executions": 10}
        }
        
        maestro._calculate_strategy_weights()
        
        assert "strategy1" in maestro.strategy_weights
        assert "strategy2" in maestro.strategy_weights
        assert "strategy3" in maestro.strategy_weights
        
        # Strategy1 should have the highest weight
        assert maestro.strategy_weights["strategy1"] > maestro.strategy_weights["strategy2"]
        assert maestro.strategy_weights["strategy2"] > maestro.strategy_weights["strategy3"]

    def test_select_strategy(self, maestro):
        """Test strategy selection with weighting."""
        # Setup performance data
        maestro.performance_data = {
            "CREATE_NEW_TEST_FILE_STRATEGY": {"success_count": 8, "failure_count": 2, "total_executions": 10},
            "sandbox_validation_no_tests": {"success_count": 5, "failure_count": 5, "total_executions": 10}
        }
        maestro._calculate_strategy_weights()
        
        # Test context with test files (should prefer CREATE_NEW_TEST_FILE_STRATEGY)
        test_context = {"patches_to_apply": [{"file_path": "tests/test_file.py"}]}
        strategy = maestro.select_strategy(test_context)
        assert strategy["strategy_type"] == "CREATE_NEW_TEST_FILE_STRATEGY"
        
        # Test context with no test files (should prefer sandbox_validation_no_tests)
        non_test_context = {"patches_to_apply": [{"file_path": "src/file.py"}]}
        strategy = maestro.select_strategy(non_test_context)
        assert strategy["strategy_type"] == "sandbox_validation_no_tests"

    def test_record_performance(self, maestro):
        """Test recording strategy performance."""
        strategy = {"strategy_type": "test_strategy"}
        metrics = {"time_taken": 1.5, "memory_used": 100}
        
        # First record
        maestro.record_performance(strategy, True, metrics)
        assert maestro.performance_data["test_strategy"]["success_count"] == 1
        assert maestro.performance_data["test_strategy"]["total_executions"] == 1
        
        # Second record (failure)
        maestro.record_performance(strategy, False, metrics)
        assert maestro.performance_data["test_strategy"]["success_count"] == 1
        assert maestro.performance_data["test_strategy"]["failure_count"] == 1
        assert maestro.performance_data["test_strategy"]["total_executions"] == 2
        
        # Check average metrics
        assert "time_taken" in maestro.performance_data["test_strategy"]["average_metrics"]
        assert "memory_used" in maestro.performance_data["test_strategy"]["average_metrics"]

    def test_rule_based_classification(self, maestro):
        """Test the rule-based strategy classification."""
        # Test new test file detection
        test_file_context = {"patches_to_apply": [{"file_path": "tests/new_test.py", "operation": "INSERT"}]}
        assert maestro._classify_strategy_by_rules(test_file_context) == "CREATE_NEW_TEST_FILE_STRATEGY"
        
        # Test config file detection
        config_file_context = {"patches_to_apply": [{"file_path": "config/settings.yaml"}]}
        assert maestro._classify_strategy_by_rules(config_file_context) == "CONFIG_UPDATE_STRATEGY"
        
        # Test doc file detection
        doc_file_context = {"patches_to_apply": [{"file_path": "docs/README.md"}]}
        assert maestro._classify_strategy_by_rules(doc_file_context) == "DOC_UPDATE_STRATEGY"
        
        # Test no patches
        no_patches_context = {"patches_to_apply": []}
        assert maestro._classify_strategy_by_rules(no_patches_context) == "DISCARD"

    # TODO: Add more test cases for choose_strategy method
    # TODO: Add test cases for edge cases and error handling
    # TODO: Add integration tests with actual strategy execution