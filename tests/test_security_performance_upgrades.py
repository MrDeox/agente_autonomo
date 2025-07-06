"""
Test Security and Performance Upgrades - Agente Autônomo v2.8.1
Validates the critical action items implemented from the technical audit report.
"""

import pytest
import asyncio
import time
import json
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from pathlib import Path

from agent.interfaces import (
    AgentInterface, AgentCapability, AgentPriority, AgentStatus,
    AgentContext, AgentResult, AgentMetrics, BaseAgent, AgentRegistry
)
from agent.dependency_resolver import (
    DependencyResolver, DependencyScope, DependencyType,
    CircularDependencyError, DependencyNotFoundError, AgentFactory
)
from agent.security.auth_manager import (
    AuthManager, AuthLevel, TokenType, UserSession, TokenPayload
)
from agent.performance.config_cache import ConfigCache, get_config_cache


class TestAgent(BaseAgent):
    """Test agent implementing the new interface"""
    
    def __init__(self, name: str, capabilities: list, logger: logging.Logger):
        super().__init__(name, capabilities, logger)
        self._execution_count = 0
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute a test task"""
        start_time = time.time()
        
        try:
            # Simulate work
            await asyncio.sleep(0.1)
            self._execution_count += 1
            
            execution_time = time.time() - start_time
            result = AgentResult(
                task_id=context.task_id,
                success=True,
                data={"message": f"Task {context.task_id} completed", "count": self._execution_count},
                execution_time=execution_time
            )
            
            self._update_metrics(True, execution_time, context.capabilities_required[0] if context.capabilities_required else None)
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            result = AgentResult(
                task_id=context.task_id,
                success=False,
                data=None,
                error_message=str(e),
                execution_time=execution_time
            )
            
            self._update_metrics(False, execution_time)
            return result
    
    def get_capability_score(self, capability: AgentCapability) -> float:
        """Get capability score for this test agent"""
        if capability in self._capabilities:
            return 0.9
        return 0.0


class TestSecurityPerformanceUpgrades:
    """Test suite for security and performance upgrades"""
    
    @pytest.fixture
    def logger(self):
        """Create test logger"""
        return logging.getLogger("test")
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return {
            "security": {
                "secret_key": "test_secret_key_32_chars_long_for_testing"
            },
            "models": {
                "architect_default": {
                    "model": "gpt-4",
                    "api_key": "test_key"
                }
            }
        }
    
    @pytest.fixture
    def auth_manager(self, config, logger):
        """Create authentication manager"""
        return AuthManager(config, logger)
    
    @pytest.fixture
    def dependency_resolver(self, logger):
        """Create dependency resolver"""
        return DependencyResolver(logger)
    
    @pytest.fixture
    def config_cache(self, logger):
        """Create config cache"""
        return ConfigCache(max_size_mb=10, logger=logger)
    
    @pytest.fixture
    def agent_registry(self):
        """Create agent registry"""
        return AgentRegistry()
    
    def test_agent_interface_protocol(self, logger):
        """Test that agents implement the formal interface protocol"""
        # Create test agent
        agent = TestAgent("test_agent", [AgentCapability.CODE_ANALYSIS], logger)
        
        # Verify it implements the protocol
        assert isinstance(agent, AgentInterface)
        assert agent.name == "test_agent"
        assert AgentCapability.CODE_ANALYSIS in agent.capabilities
        assert agent.status == AgentStatus.INITIALIZING
        
        # Test capability scoring
        score = agent.get_capability_score(AgentCapability.CODE_ANALYSIS)
        assert score == 0.9
        
        score = agent.get_capability_score(AgentCapability.BUG_DETECTION)
        assert score == 0.0
    
    @pytest.mark.asyncio
    async def test_agent_execution(self, logger):
        """Test agent execution with typed context"""
        agent = TestAgent("test_agent", [AgentCapability.CODE_ANALYSIS], logger)
        
        # Initialize agent
        success = await agent.initialize({"test": "config"})
        assert success
        assert agent.status == AgentStatus.IDLE
        
        # Create typed context
        context = AgentContext(
            task_id="test_task_1",
            objective="Test objective",
            priority=AgentPriority.HIGH,
            capabilities_required=[AgentCapability.CODE_ANALYSIS]
        )
        
        # Execute task
        result = await agent.execute(context)
        
        assert isinstance(result, AgentResult)
        assert result.success
        assert result.task_id == "test_task_1"
        assert result.execution_time > 0
        assert "message" in result.data
        
        # Check metrics
        assert agent.metrics.tasks_completed == 1
        assert agent.metrics.success_rate == 1.0
    
    def test_agent_registry(self, agent_registry, logger):
        """Test agent registry functionality"""
        # Create test agents
        agent1 = TestAgent("agent1", [AgentCapability.CODE_ANALYSIS], logger)
        agent2 = TestAgent("agent2", [AgentCapability.BUG_DETECTION], logger)
        agent3 = TestAgent("agent3", [AgentCapability.CODE_ANALYSIS, AgentCapability.BUG_DETECTION], logger)
        
        # Register agents
        assert agent_registry.register_agent(agent1)
        assert agent_registry.register_agent(agent2)
        assert agent_registry.register_agent(agent3)
        
        # Test retrieval
        retrieved_agent = agent_registry.get_agent("agent1")
        assert retrieved_agent == agent1
        
        # Test capability-based retrieval
        code_analysis_agents = agent_registry.get_agents_with_capability(AgentCapability.CODE_ANALYSIS)
        assert len(code_analysis_agents) == 2
        assert agent1 in code_analysis_agents
        assert agent3 in code_analysis_agents
        
        # Test best agent selection
        best_agent = agent_registry.get_best_agent_for_capability(AgentCapability.CODE_ANALYSIS)
        assert best_agent is not None
        assert best_agent.get_capability_score(AgentCapability.CODE_ANALYSIS) > 0
    
    def test_dependency_resolver(self, dependency_resolver, logger):
        """Test dependency resolver functionality"""
        # Register a service
        def create_test_service(config):
            return {"service": "test", "config": config}
        
        assert dependency_resolver.register_service("test_service", create_test_service)
        
        # Register configuration
        test_config = {"key": "value"}
        assert dependency_resolver.register_configuration("test_config", test_config)
        
        # Register agent factory
        def create_test_agent(config, logger):
            return TestAgent("resolved_agent", [AgentCapability.CODE_ANALYSIS], logger)
        
        assert dependency_resolver.register_agent("test_agent", create_test_agent)
        
        # Test resolution
        service = dependency_resolver.resolve("test_service")
        assert service["service"] == "test"
        
        config = dependency_resolver.resolve("test_config")
        assert config["key"] == "value"
        
        agent = dependency_resolver.resolve_agent("test_agent")
        assert isinstance(agent, TestAgent)
        assert agent.name == "resolved_agent"
    
    def test_circular_dependency_detection(self, dependency_resolver):
        """Test circular dependency detection"""
        # Create circular dependency
        def service_a(service_b):
            return {"service": "A", "depends_on": service_b}
        
        def service_b(service_a):
            return {"service": "B", "depends_on": service_a}
        
        dependency_resolver.register_service("service_a", service_a, dependencies=["service_b"])
        dependency_resolver.register_service("service_b", service_b, dependencies=["service_a"])
        
        # Should raise circular dependency error
        with pytest.raises(CircularDependencyError):
            dependency_resolver.resolve("service_a")
    
    def test_authentication_manager(self, auth_manager):
        """Test authentication manager functionality"""
        # Test user authentication
        user_data = auth_manager.authenticate_user("admin", "admin123")
        assert user_data is not None
        assert user_data["username"] == "admin"
        assert user_data["auth_level"] == AuthLevel.ADMIN
        
        # Test invalid authentication
        user_data = auth_manager.authenticate_user("admin", "wrong_password")
        assert user_data is None
        
        # Test token creation
        access_token = auth_manager.create_access_token(
            "user_admin",
            "admin",
            AuthLevel.ADMIN,
            ["read", "write", "admin"]
        )
        assert access_token is not None
        
        # Test token verification
        token_payload = auth_manager.verify_token(access_token)
        assert token_payload is not None
        assert token_payload.username == "admin"
        assert token_payload.auth_level == AuthLevel.ADMIN
        assert token_payload.token_type == TokenType.ACCESS
        
        # Test invalid token
        invalid_token = "invalid.token.here"
        token_payload = auth_manager.verify_token(invalid_token)
        assert token_payload is None
    
    def test_session_management(self, auth_manager):
        """Test session management"""
        # Create session
        session_id = auth_manager.create_session(
            "user_admin",
            "admin",
            AuthLevel.ADMIN,
            ["read", "write", "admin"],
            ip_address="127.0.0.1"
        )
        assert session_id is not None
        
        # Retrieve session
        session = auth_manager.get_session(session_id)
        assert session is not None
        assert session.username == "admin"
        assert session.auth_level == AuthLevel.ADMIN
        assert session.is_active
        
        # Invalidate session
        assert auth_manager.invalidate_session(session_id)
        session = auth_manager.get_session(session_id)
        assert session is None
    
    def test_rate_limiting(self, auth_manager):
        """Test rate limiting functionality"""
        identifier = "test_user"
        
        # Should allow requests within limit
        for i in range(60):
            assert auth_manager.check_rate_limit(identifier)
        
        # Should block requests over limit
        assert not auth_manager.check_rate_limit(identifier)
    
    def test_config_cache(self, config_cache, tmp_path):
        """Test configuration caching"""
        # Create test config file
        config_file = tmp_path / "test_config.yaml"
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432
            },
            "api": {
                "timeout": 30
            }
        }
        
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        # Test config loading and caching
        loaded_config = config_cache.get_config(str(config_file))
        assert loaded_config is not None
        assert loaded_config["database"]["host"] == "localhost"
        
        # Test cache hit
        cached_config = config_cache.get_config(str(config_file))
        assert cached_config == loaded_config
        
        # Check cache stats
        stats = config_cache.get_cache_stats()
        assert stats["cache_size"] == 1
        assert stats["hit_rate"] > 0
    
    def test_config_cache_invalidation(self, config_cache, tmp_path):
        """Test config cache invalidation"""
        # Create test config file
        config_file = tmp_path / "test_config.yaml"
        config_data = {"key": "value1"}
        
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config_data, f)
        
        # Load config
        config_cache.get_config(str(config_file))
        
        # Modify file
        config_data["key"] = "value2"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Should reload due to file modification
        reloaded_config = config_cache.get_config(str(config_file))
        assert reloaded_config["key"] == "value2"
    
    def test_security_headers(self, auth_manager):
        """Test security headers"""
        headers = auth_manager.get_security_headers()
        
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
    
    def test_agent_factory(self, dependency_resolver, logger):
        """Test agent factory with dependency injection"""
        factory = AgentFactory(dependency_resolver, logger)
        
        # Register agent factory
        def create_test_agent(config, logger):
            return TestAgent("factory_agent", [AgentCapability.CODE_ANALYSIS], logger)
        
        dependency_resolver.register_agent("test_agent", create_test_agent)
        
        # Create agent
        agent = factory.create_agent("test_agent", {"test": "config"})
        assert agent is not None
        assert agent.name == "factory_agent"
        assert agent.status == AgentStatus.IDLE
    
    def test_performance_metrics(self, logger):
        """Test performance metrics collection"""
        agent = TestAgent("metrics_agent", [AgentCapability.CODE_ANALYSIS], logger)
        
        # Simulate multiple executions
        for i in range(5):
            context = AgentContext(
                task_id=f"task_{i}",
                objective=f"Task {i}",
                priority=AgentPriority.MEDIUM,
                capabilities_required=[AgentCapability.CODE_ANALYSIS]
            )
            
            # Execute synchronously for testing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(agent.execute(context))
                assert result.success
            finally:
                loop.close()
        
        # Check metrics
        metrics = agent.metrics
        assert metrics.tasks_completed == 5
        assert metrics.tasks_failed == 0
        assert metrics.success_rate == 1.0
        assert metrics.average_execution_time > 0
        assert AgentCapability.CODE_ANALYSIS in metrics.capabilities_used
        assert metrics.capabilities_used[AgentCapability.CODE_ANALYSIS] == 5


class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, logger):
        """Test complete workflow with all new components"""
        # Initialize components
        config = {
            "security": {"secret_key": "test_secret_key_32_chars_long_for_testing"},
            "models": {"architect_default": {"model": "gpt-4"}}
        }
        
        auth_manager = AuthManager(config, logger)
        dependency_resolver = DependencyResolver(logger)
        config_cache = ConfigCache(max_size_mb=10, logger=logger)
        agent_registry = AgentRegistry()
        
        # Register agents
        agent1 = TestAgent("architect", [AgentCapability.ARCHITECTURE_DESIGN], logger)
        agent2 = TestAgent("bug_hunter", [AgentCapability.BUG_DETECTION], logger)
        
        agent_registry.register_agent(agent1)
        agent_registry.register_agent(agent2)
        
        # Authenticate user
        user_data = auth_manager.authenticate_user("admin", "admin123")
        assert user_data is not None
        
        # Create access token
        access_token = auth_manager.create_access_token(
            user_data["user_id"],
            user_data["username"],
            user_data["auth_level"],
            user_data["permissions"]
        )
        
        # Verify token
        token_payload = auth_manager.verify_token(access_token)
        assert token_payload is not None
        
        # Get best agent for capability
        best_agent = agent_registry.get_best_agent_for_capability(AgentCapability.ARCHITECTURE_DESIGN)
        assert best_agent is not None
        
        # Execute task
        context = AgentContext(
            task_id="integration_test",
            objective="Test integration",
            priority=AgentPriority.HIGH,
            capabilities_required=[AgentCapability.ARCHITECTURE_DESIGN]
        )
        
        result = await best_agent.execute(context)
        assert result.success
        
        # Check rate limiting
        assert auth_manager.check_rate_limit(user_data["user_id"])
        
        # Verify all components work together
        assert len(agent_registry.get_all_agents()) == 2
        assert auth_manager.get_session("test_session") is None  # No session created in this test


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 