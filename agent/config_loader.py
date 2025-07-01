import os
import json
from pathlib import Path
from omegaconf import OmegaConf
import hydra
from hydra.core.global_hydra import GlobalHydra
import logging

config_logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Load configuration using Hydra with fallbacks.
    
    Returns:
        dict: Configuration dictionary
    """
    try:
        # Initialize Hydra if not already initialized
        if not GlobalHydra().is_initialized():
            hydra.initialize_config_dir(
                config_dir=os.path.join(Path.cwd(), "config"),
                version_base=None
            )
        
        # Compose configuration
        cfg = hydra.compose(config_name="default")
        return OmegaConf.to_container(cfg, resolve=True)
    except Exception as e:
        config_logger.error(f"Failed to load Hydra configuration: {e}")
        try:
            # Fallback to JSON configuration
            with open("hephaestus_config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            config_logger.error("hephaestus_config.json not found in fallback")
        except json.JSONDecodeError as e:
            config_logger.error(f"Error parsing hephaestus_config.json: {e}")
        
        # Final fallback to example config
        try:
            with open("example_config.json", "r", encoding="utf-8") as f:
                config_logger.info("Loaded example_config.json as fallback")
                return json.load(f)
        except Exception as e:
            config_logger.error(f"All configuration fallbacks failed: {e}")
    
    return {}
