import pytest
from unittest.mock import MagicMock, patch
from agent.agents.maestro_agent import MaestroAgent, StrategyCache

class TestStrategyCache:
    def test_cache_operations(self):
        """Test basic cache operations."""
        cache = StrategyCache(maxsize=2, ttl=60)
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test LRU eviction
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        assert cache.get("key1") is None
        
        # TODO: Add TTL expiration tests

class TestMaestroAgent:
    @pytest.fixture
    def mock_agent(self):
        """Fixture for a MaestroAgent with mocked dependencies."""
        model_config = {"primary_model": "test-model"}
        logger = MagicMock()
        return MaestroAgent(model_config, logger)
    
    def test_initial_strategy_weights(self, mock_agent):
        """Test that initial strategy weights are set correctly."""
        assert len(mock_agent.strategy_weights) > 0
        for weight in mock_agent.strategy_weights.values():
            assert 0.0 <= weight <= 1.0
    
    def test_select_strategy_distribution(self, mock_agent):
        """Test that strategy selection follows weight distribution."""
        strategies = set()
        for _ in range(100):
            strategies.add(mock_agent.select_strategy({}))
        
        # Should have selected multiple strategies based on weights
        assert len(strategies) > 1
    
    def test_weight_adjustment_on_success(self, mock_agent):
        """Test that successful executions increase strategy weights."""
        strategy = "test_strategy"
        initial_weight = mock_agent.strategy_weights[strategy] = 0.5
        
        mock_agent._update_strategy_weights(strategy, True)
        assert mock_agent.strategy_weights[strategy] == initial_weight + 0.05
    
    def test_weight_adjustment_on_failure(self, mock_agent):
        """Test that failed executions decrease strategy weights."""
        strategy = "test_strategy"
        initial_weight = mock_agent.strategy_weights[strategy] = 0.5
        
        mock_agent._update_strategy_weights(strategy, False)
        assert mock_agent.strategy_weights[strategy] == initial_weight - 0.1
    
    def test_weight_clamping(self, mock_agent):
        """Test that weights stay within valid range."""
        # Test minimum clamping
        mock_agent.strategy_weights["low_strategy"] = 0.09
        mock_agent._update_strategy_weights("low_strategy", False)
        assert mock_agent.strategy_weights["low_strategy"] == 0.1
        
        # Test maximum clamping
        mock_agent.strategy_weights["high_strategy"] = 0.99
        mock_agent._update_strategy_weights("high_strategy", True)
        assert mock_agent.strategy_weights["high_strategy"] == 1.0
    
    @patch('agent.agents.maestro_agent.MaestroAgent._execute_strategy_impl')
    def test_execute_strategy_success(self, mock_execute, mock_agent):
        """Test successful strategy execution updates weights."""
        strategy = "test_strategy"
        initial_weight = mock_agent.strategy_weights[strategy] = 0.5
        mock_execute.return_value = {"status": "success"}
        
        result = mock_agent.execute_strategy(strategy, {})
        assert result["status"] == "success"
        assert mock_agent.strategy_weights[strategy] == initial_weight + 0.05
    
    @patch('agent.agents.maestro_agent.MaestroAgent._execute_strategy_impl')
    def test_execute_strategy_failure(self, mock_execute, mock_agent):
        """Test failed strategy execution updates weights and logs error."""
        strategy = "test_strategy"
        initial_weight = mock_agent.strategy_weights[strategy] = 0.5
        mock_execute.side_effect = Exception("Test error")
        
        with pytest.raises(Exception):
            mock_agent.execute_strategy(strategy, {})
        
        assert mock_agent.strategy_weights[strategy] == initial_weight - 0.1
        mock_agent.logger.error.assert_called()
    
    def test_analyze_evolution_log(self, mock_agent):
        """Test evolution log analysis returns expected structure."""
        # TODO: Implement with actual test log data
        result = mock_agent.analyze_evolution_log("path/to/log.csv")
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, float)
            assert 0.0 <= value <= 1.0