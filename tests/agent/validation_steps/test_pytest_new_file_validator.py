import pytest
import subprocess
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

# Import the class to be tested
from agent.validation_steps.pytest_new_file_validator import PytestNewFileValidator

# Mock logger fixture (can be moved to a conftest.py if used more widely)
@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    return logger

@pytest.fixture
def validator_instance(mock_logger, tmp_path):
    # tmp_path is a pytest fixture providing a temporary directory unique to the test invocation
    return PytestNewFileValidator(
        logger=mock_logger,
        base_path=str(tmp_path), # Use temporary path as base for tests
        patches_to_apply=[],    # Will be overridden in specific tests
        use_sandbox=True        # Assuming sandbox usage for these tests
    )

def create_mock_subprocess_run(returncode=0, stdout="Pytest passed", stderr=""):
    mock_process = MagicMock(spec=subprocess.CompletedProcess)
    mock_process.returncode = returncode
    mock_process.stdout = stdout
    mock_process.stderr = stderr
    return mock_process

# --- Test Cases ---

def test_pytest_new_file_validator_success(validator_instance, mock_logger, tmp_path):
    """Test successful validation when pytest passes for the new file."""
    test_file_path = "tests/new_module/test_new_feature.py"
    test_file_content = "import pytest\ndef test_example():\n    assert True\n"

    validator_instance.patches_to_apply = [{
        "file_path": test_file_path,
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": test_file_content
    }]

    # Mock subprocess.run to simulate pytest passing
    with patch("subprocess.run", return_value=create_mock_subprocess_run(returncode=0, stdout="1 test passed")) as mock_run:
        # Mock Path.exists to simulate file already written by a previous step (or validator writes it)
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False # Force validator to attempt to write the file

            # Mock open to prevent actual file I/O for this specific test if validator writes
            with patch("builtins.open", mock_open()) as mock_file_open:
                with patch.object(Path, 'unlink') as mock_unlink: # Mock unlink
                    success, reason, message = validator_instance.execute()

                    assert success is True
                    assert reason == "PYTEST_PASSED"
                    assert f"Pytest passed for {test_file_path}" in message
                    mock_run.assert_called_once()
                    # Check if pytest was called on the correct file
                    args, kwargs = mock_run.call_args
                    assert str(Path(tmp_path) / test_file_path) in args[0]
                    # Check if the temporary file was written and then unlinked
                    mock_file_open.assert_called_once_with(Path(tmp_path) / test_file_path, "w", encoding="utf-8")
                    mock_unlink.assert_called_once()


def test_pytest_new_file_validator_pytest_fails(validator_instance, mock_logger, tmp_path):
    """Test validation failure when pytest fails for the new file."""
    test_file_path = "tests/failing_module/test_failing_feature.py"
    test_file_content = "import pytest\ndef test_example():\n    assert False\n"

    validator_instance.patches_to_apply = [{
        "file_path": test_file_path,
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": test_file_content
    }]

    with patch("subprocess.run", return_value=create_mock_subprocess_run(returncode=1, stdout="1 test failed", stderr="AssertionError")) as mock_run:
        with patch.object(Path, 'exists', return_value=False): # Force write attempt
            with patch("builtins.open", mock_open()):
                 with patch.object(Path, 'unlink') as mock_unlink:
                    success, reason, message = validator_instance.execute()

                    assert success is False
                    assert reason == "PYTEST_FAILED"
                    assert f"Pytest failed for {test_file_path}" in message
                    assert "AssertionError" in message # Check if stderr is in the message
                    mock_run.assert_called_once()
                    mock_unlink.assert_called_once()

def test_pytest_new_file_validator_no_tests_collected(validator_instance, mock_logger, tmp_path):
    """Test validation failure when pytest collects no tests (exit code 5)."""
    test_file_path = "tests/empty_module/test_empty_feature.py"
    test_file_content = "# No tests here\n"

    validator_instance.patches_to_apply = [{
        "file_path": test_file_path,
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": test_file_content
    }]

    # Pytest exit code 5 for no tests collected
    with patch("subprocess.run", return_value=create_mock_subprocess_run(returncode=5, stdout="collected 0 items", stderr="")) as mock_run:
        with patch.object(Path, 'exists', return_value=False):
            with patch("builtins.open", mock_open()):
                with patch.object(Path, 'unlink') as mock_unlink:
                    success, reason, message = validator_instance.execute()

                    assert success is False
                    assert reason == "PYTEST_FAILED" # Still PYTEST_FAILED, but check message for exit code 5
                    assert f"Pytest failed for {test_file_path} (exit code 5)" in message
                    mock_run.assert_called_once()
                    mock_unlink.assert_called_once()

def test_pytest_new_file_validator_subprocess_timeout(validator_instance, mock_logger, tmp_path):
    """Test validation failure on pytest timeout."""
    test_file_path = "tests/hanging_module/test_hanging_feature.py"
    validator_instance.patches_to_apply = [{"file_path": test_file_path, "operation": "REPLACE", "block_to_replace": None, "content": "import time\ndef test_hang(): time.sleep(100)"}]

    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="pytest", timeout=60)) as mock_run:
        with patch.object(Path, 'exists', return_value=False):
            with patch("builtins.open", mock_open()):
                with patch.object(Path, 'unlink') as mock_unlink:
                    success, reason, message = validator_instance.execute()

                    assert success is False
                    assert reason == "PYTEST_TIMEOUT"
                    assert f"Pytest timed out for {test_file_path}" in message
                    mock_run.assert_called_once()
                    mock_unlink.assert_called_once()

def test_pytest_new_file_validator_subprocess_exception(validator_instance, mock_logger, tmp_path):
    """Test validation failure on other subprocess execution error."""
    test_file_path = "tests/error_module/test_error_feature.py"
    validator_instance.patches_to_apply = [{"file_path": test_file_path, "operation": "REPLACE", "block_to_replace": None, "content": "content"}]

    with patch("subprocess.run", side_effect=Exception("Some Subprocess Error")) as mock_run:
        with patch.object(Path, 'exists', return_value=False):
            with patch("builtins.open", mock_open()):
                with patch.object(Path, 'unlink') as mock_unlink:
                    success, reason, message = validator_instance.execute()

                    assert success is False
                    assert reason == "PYTEST_EXECUTION_ERROR"
                    assert "Some Subprocess Error" in message
                    mock_run.assert_called_once()
                    mock_unlink.assert_called_once()

def test_pytest_new_file_validator_no_new_test_file_patch(validator_instance, mock_logger):
    """Test failure when no suitable patch for a new test file is provided."""
    validator_instance.patches_to_apply = [{
        "file_path": "src/module.py", # Not a test file path
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": "class A: pass"
    }]
    success, reason, message = validator_instance.execute()
    assert success is False
    assert reason == "NO_NEW_TEST_FILE_PATCH"

def test_pytest_new_file_validator_patch_missing_filepath(validator_instance, mock_logger):
    """Test failure when the patch is missing the file_path."""
    validator_instance.patches_to_apply = [{
        # "file_path": "tests/module/test_feature.py", # Missing
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": "import pytest"
    }]
    success, reason, message = validator_instance.execute()
    assert success is False
    assert reason == "NO_NEW_TEST_FILE_PATCH"

def test_pytest_new_file_validator_temp_write_error(validator_instance, mock_logger, tmp_path):
    """Test failure when temporarily writing the new test file fails."""
    test_file_path = "tests/new_module/test_new_feature.py"
    validator_instance.patches_to_apply = [{"file_path": test_file_path, "operation": "REPLACE", "block_to_replace": None, "content": "content"}]

    with patch.object(Path, 'exists', return_value=False): # Ensure it tries to write
        # Make open raise an exception
        with patch("builtins.open", mock_open()) as mock_file_open:
            mock_file_open.side_effect = IOError("Disk full")
            success, reason, message = validator_instance.execute()

            assert success is False
            assert reason == "TEMP_WRITE_ERROR"
            assert "Disk full" in message
            # unlink should not be called if write failed before pytest run
            Path(tmp_path, test_file_path).unlink(missing_ok=True) # manual cleanup if needed

def test_pytest_new_file_validator_file_already_exists(validator_instance, mock_logger, tmp_path):
    """Test successful validation when pytest passes and file already exists (not written by validator)."""
    test_file_path_str = "tests/existing_test/test_already_here.py"
    abs_test_file_path = tmp_path / test_file_path_str
    abs_test_file_path.parent.mkdir(parents=True, exist_ok=True)
    abs_test_file_path.write_text("import pytest\ndef test_existing(): assert 1 == 1")

    validator_instance.patches_to_apply = [{
        "file_path": test_file_path_str,
        "operation": "REPLACE",
        "block_to_replace": None,
        "content": "ignored content as file exists"
    }]

    with patch("subprocess.run", return_value=create_mock_subprocess_run(returncode=0, stdout="1 test passed")) as mock_run:
        # Mock Path.exists to simulate file already being there
        with patch.object(Path, 'exists') as mock_path_exists:
            # This is a bit tricky. The exists check is on `target_file_path` which is `tmp_path / test_file_path_str`
            # We need it to return True for this specific path.
            mock_path_exists.return_value = True

            # mock_open should NOT be called if Path.exists is True
            with patch("builtins.open", mock_open()) as mock_file_open:
                # mock_unlink should NOT be called if validator didn't write the file
                with patch.object(Path, 'unlink') as mock_unlink:
                    success, reason, message = validator_instance.execute()

                    assert success is True
                    assert reason == "PYTEST_PASSED"
                    mock_run.assert_called_once()
                    mock_file_open.assert_not_called() # Crucial: validator should not overwrite
                    mock_unlink.assert_not_called() # Crucial: validator should not delete pre-existing file

    abs_test_file_path.unlink() # Clean up the manually created file
