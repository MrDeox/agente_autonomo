import pytest
from unittest.mock import patch, MagicMock

from agent.brain import (
    generate_next_objective,
    generate_capacitation_objective,
    generate_commit_message
)
from agent.memory import Memory
from agent.model_optimizer import ModelOptimizer

# Test setup
@pytest.fixture
def mock_model_config():
    return {"model": "test-model", "api_key": "test-key"}

@pytest.fixture
def mock_logger():
    return MagicMock()

@pytest.fixture
def mock_memory():
    return MagicMock(spec=Memory)

@pytest.fixture
def mock_model_optimizer():
    return MagicMock(spec=ModelOptimizer)

class TestGenerateNextObjective:
    def test_with_empty_manifest(self, mock_model_config, mock_logger):
        """Test generating an objective with no manifest or analysis data."""
        result = generate_next_objective(
            model_config=mock_model_config,
            current_manifest="",
            logger=mock_logger,
            project_root_dir="."
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_with_manifest_and_analysis(self, mock_model_config, mock_logger):
        """Test generating an objective with manifest and analysis data."""
        result = generate_next_objective(
            model_config=mock_model_config,
            current_manifest="Test manifest content",
            logger=mock_logger,
            project_root_dir="."
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_with_memory_context(self, mock_model_config, mock_logger, mock_memory):
        """Test generating an objective with memory context."""
        mock_memory.get_full_history_for_prompt.return_value = "Test memory history"
        result = generate_next_objective(
            model_config=mock_model_config,
            current_manifest="Test manifest",
            logger=mock_logger,
            project_root_dir=".",
            memory=mock_memory
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_with_performance_data(self, mock_model_config, mock_logger, mock_model_optimizer):
        """Test generating an objective with performance data."""
        mock_model_optimizer.get_agent_performance_summary.return_value = {
            "agent1": {"success_rate": 0.9, "average_quality_score": 0.85}
        }
        result = generate_next_objective(
            model_config=mock_model_config,
            current_manifest="Test manifest",
            logger=mock_logger,
            project_root_dir=".",
            model_optimizer=mock_model_optimizer
        )
        assert isinstance(result, str)
        assert len(result) > 0

class TestGenerateCapacitationObjective:
    def test_basic_capacitation(self, mock_model_config, mock_logger):
        """Test generating a basic capacitation objective."""
        result = generate_capacitation_objective(
            model_config=mock_model_config,
            engineer_analysis="We need a new tool to make HTTP requests",
            logger=mock_logger
        )
        assert isinstance(result, str)
        assert "[CAPACITATION TASK]" in result

    def test_with_memory_context(self, mock_model_config, mock_logger):
        """Test generating a capacitation objective with memory context."""
        result = generate_capacitation_objective(
            model_config=mock_model_config,
            engineer_analysis="We need to improve the JSON parser",
            memory_summary="Previous attempt to improve JSON parser failed",
            logger=mock_logger
        )
        assert isinstance(result, str)
        assert "[CAPACITATION TASK]" in result

class TestGenerateCommitMessage:
    def test_feat_commit_message(self, mock_logger):
        """Test generating a feature commit message."""
        result = generate_commit_message(
            analysis_summary="Test analysis",
            objective="Add new HTTP client functionality",
            logger=mock_logger
        )
        assert isinstance(result, str)
        assert "feat: " in result

    def test_fix_commit_message(self, mock_logger):
        """Test generating a fix commit message."""
        result = generate_commit_message(
            analysis_summary="Test analysis",
            objective="Fix bug in JSON parser",
            logger=mock_logger
        )
        assert isinstance(result, str)
        assert "fix: " in result

    def test_prefixed_commit_message(self, mock_logger):
        """Test generating a commit message when objective already has conventional prefix."""
        result = generate_commit_message(
            analysis_summary="Test analysis",
            objective="feat: Add new HTTP client functionality",
            logger=mock_logger
        )
        assert isinstance(result, str)
        assert result.startswith("feat: ")

    def test_long_objective_truncation(self, mock_logger):
        """Test that long objectives are properly truncated."""
        long_objective = "Add new HTTP client functionality with support for all HTTP methods, authentication, timeout handling, retry logic, and connection pooling"
        result = generate_commit_message(
            analysis_summary="Test analysis",
            objective=long_objective,
            logger=mock_logger
        )
        assert isinstance(result, str)
        assert len(result) <= 72
        assert "..." in result