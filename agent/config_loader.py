import os
import json # Keep for potential future use, but not for primary loading
from pathlib import Path
from omegaconf import OmegaConf, MissingMandatoryValue
import hydra
from hydra.core.global_hydra import GlobalHydra
from hydra.errors import ConfigCompositionException
import logging

config_logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Load configuration using Hydra.

    This function initializes Hydra, composes the configuration based on defaults
    (typically specified in config/default.yaml and other files in the config directory),
    and returns the configuration as a Python dictionary.

    If Hydra fails to initialize or compose the configuration, this function
    will log the error and raise a RuntimeError, as configuration is critical.
    
    Returns:
        dict: Configuration dictionary.

    Raises:
        RuntimeError: If Hydra configuration loading fails.
    """
    try:
        # Ensure Hydra is initialized only once
        if not GlobalHydra.instance().is_initialized():
            # Initialize Hydra to look for configurations in the 'config' directory
            # relative to the current working directory.
            # version_base=None is for compatibility with Hydra 1.1 behaviors.
            # For Hydra 1.2+, consider setting version_base to "1.2" or "1.3" and
            # adapting to any changes (e.g., CWD behavior).
            hydra.initialize_config_dir(
                config_dir=os.path.join(Path.cwd(), "config"),
                version_base=None
            )
        
        # Compose the configuration. Hydra will look for a "default.yaml"
        # (or a config specified by overrides if running from command line with Hydra).
        # The 'config_name="default"' explicitly tells Hydra to use 'default.yaml'
        # as the entry point.
        cfg = hydra.compose(config_name="default")
        
        # Convert the OmegaConf object to a standard Python dictionary.
        # 'resolve=True' ensures that any interpolations (e.g., ${...} variables)
        # in the YAML files are resolved.
        resolved_cfg = OmegaConf.to_container(cfg, resolve=True)
        config_logger.info("Hydra configuration loaded successfully.")
        return resolved_cfg

    except MissingMandatoryValue as e:
        config_logger.error(f"Hydra configuration error: Missing a mandatory value. {e}")
        raise RuntimeError(f"Hydra configuration error: Missing a mandatory value. Details: {e}") from e
    except ConfigCompositionException as e:
        config_logger.error(f"Hydra configuration composition error: {e}")
        # This can happen if there are issues with the config files structure or references
        raise RuntimeError(f"Failed to compose Hydra configuration. Details: {e}") from e
    except Exception as e:
        # Catch any other Hydra or OmegaConf related errors
        config_logger.error(f"Failed to load Hydra configuration due to an unexpected error: {e}")
        raise RuntimeError(f"Unexpected error during Hydra configuration loading. Details: {e}") from e

if __name__ == '__main__':
    # Example of how to use the loader
    # This part is for testing the loader directly
    logging.basicConfig(level=logging.INFO)
    try:
        config = load_config()
        config_logger.info("Configuration loaded:")
        # Pretty print the loaded configuration
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(config)

        # Example: Accessing a specific config value
        # Note: Structure depends on your YAML files
        if config:
            memory_path = config.get('memory_file_path', 'N/A')
            config_logger.info(f"Memory file path from config: {memory_path}")

            models_config = config.get('models', {})
            if models_config:
                architect_model = models_config.get('architect_default', {}).get('primary', 'N/A')
                config_logger.info(f"Architect default primary model: {architect_model}")
            else:
                config_logger.warning("Models configuration not found.")

    except RuntimeError as e:
        config_logger.error(f"Failed to load configuration in example: {e}")
    except Exception as e:
        config_logger.error(f"An unexpected error occurred in example: {e}")