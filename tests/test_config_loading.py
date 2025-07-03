import os
import pytest
import logging
from pathlib import Path
from hydra.core.global_hydra import GlobalHydra

from agent.config_loader import load_config

@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    config_root = tmp_path / "config"
    config_root.mkdir()

    (config_root / "base_config.yaml").write_text(
        """
memory_file_path: "TEMP_MEMORY.json"
default_model_settings: {temperature: 0.25, max_tokens: 1000}
code_analysis_thresholds: {file_loc: 200}
log_level: "TEST_INFO"
max_retries: 2
timeout_seconds: 15
"""
    )
    models_dir = config_root / "models"; models_dir.mkdir()
    (models_dir / "main.yaml").write_text(
        """
# No defaults list here for this simplified test model.
# Inheritance would be more complex to set up robustly in a minimal fixture
# if it relies on specific schema definitions or @package directives not present here.

test_model:
  primary: "test_primary_model"
  fallback: "test_fallback_model"
  temperature: 0.77 # Override default
"""
    )
    vs_dir = config_root / "validation_strategies"; vs_dir.mkdir()
    (vs_dir / "main.yaml").write_text(
        """
TEST_STRATEGY: {steps: [step1, step2], sanity_check_step: "test_sanity"}
"""
    )
    (config_root / "default.yaml").write_text(
        """
defaults: [base_config, models: main, validation_strategies: main, _self_]
test_top_level_key: "test_value"
"""
    )
    return tmp_path # This is the parent of 'config', so CWD should be this path

def run_load_config_test(test_path: Path, caplog, action_fn=None, expected_error_type=None, expected_error_msg_parts=None):
    original_cwd = Path.cwd()
    os.chdir(test_path) # CWD must be the parent of the 'config' dir for initialize_config_dir
    GlobalHydra.instance().clear()

    try:
        if action_fn:
            action_fn(test_path / "config") # Pass the actual config dir to the action

        if expected_error_type:
            with pytest.raises(expected_error_type) as excinfo:
                load_config()
            if expected_error_msg_parts:
                # Ensure all parts are in the error message (case-insensitive)
                error_str_lower = str(excinfo.value).lower()
                for part in expected_error_msg_parts:
                    assert part.lower() in error_str_lower
        else:
            config = load_config()
            assert config is not None
            assert isinstance(config, dict)
            # Basic check, more specific checks in dedicated test
            assert config.get("memory_file_path") == "TEMP_MEMORY.json"
            assert "Hydra configuration loaded successfully." in caplog.text
            return config # Return for more specific checks

    finally:
        os.chdir(original_cwd)
        GlobalHydra.instance().clear()

def test_load_config_successful(temp_config_dir: Path, caplog):
    caplog.set_level(logging.INFO)
    # temp_config_dir is the parent of 'config/', which is what run_load_config_test expects
    config = run_load_config_test(temp_config_dir, caplog)

    assert config.get("log_level") == "TEST_INFO"
    assert config.get("code_analysis_thresholds", {}).get("file_loc") == 200
    models_cfg = config.get("models", {})
    assert models_cfg.get("test_model", {}).get("primary") == "test_primary_model"
    assert models_cfg.get("test_model", {}).get("temperature") == 0.77 # Explicitly set in test_model
    # max_tokens is NOT inherited into test_model with the current simplified fixture
    assert models_cfg.get("test_model", {}).get("max_tokens") is None

    # Verify that default_model_settings itself is loaded correctly from base_config
    default_settings = config.get("default_model_settings", {})
    assert default_settings.get("max_tokens") == 1000
    assert default_settings.get("temperature") == 0.25

    vs_cfg = config.get("validation_strategies", {})
    assert vs_cfg.get("TEST_STRATEGY", {}).get("steps") == ["step1", "step2"]
    assert config.get("test_top_level_key") == "test_value"

def test_load_config_missing_default_yaml(tmp_path: Path, caplog): # Use tmp_path directly
    caplog.set_level(logging.ERROR)
    # Create an empty 'config' directory directly under tmp_path.
    # The run_load_config_test expects CWD to be the parent of 'config'.
    # So, CWD will be tmp_path, and it will look for tmp_path / "config" / "default.yaml".
    config_root = tmp_path / "config"
    config_root.mkdir()

    run_load_config_test(tmp_path, caplog, # tmp_path is the 'test_path'
                         expected_error_type=RuntimeError,
                         expected_error_msg_parts=["failed to compose", "cannot find primary config", "default"])

def test_load_config_malformed_yaml(temp_config_dir: Path, caplog):
    caplog.set_level(logging.ERROR)
    def malform_action(config_path: Path): # config_path is temp_config_dir / "config"
        (config_path / "base_config.yaml").write_text("invalid_yaml: [")

    # temp_config_dir is the parent of 'config/', which is what run_load_config_test expects
    run_load_config_test(temp_config_dir, caplog,
                         action_fn=malform_action,
                         expected_error_type=RuntimeError,
                         expected_error_msg_parts=["unexpected error", "parsing a flow node", "base_config.yaml"])

def test_load_config_missing_include(temp_config_dir: Path, caplog):
    caplog.set_level(logging.ERROR)
    def missing_include_action(config_path: Path): # config_path is temp_config_dir / "config"
        (config_path / "default.yaml").write_text(
            # This attempts to load a group 'non_existent' with a 'main' config from it
            "defaults: [base_config, non_existent: main, _self_]"
        )

    # temp_config_dir is the parent of 'config/', which is what run_load_config_test expects
    run_load_config_test(temp_config_dir, caplog,
                         action_fn=missing_include_action,
                         expected_error_type=RuntimeError,
                         expected_error_msg_parts=["failed to compose", "could not find", "non_existent/main"])