import json
import logging

config_logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Load configuration from ``hephaestus_config.json`` with fallbacks.

    Returns an empty dictionary if both the main and fallback configuration
    files are missing or malformed. Errors are logged for visibility.
    """
    try:
        with open("hephaestus_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        config_logger.error(
            "Configuration file 'hephaestus_config.json' not found. "
            "Falling back to defaults."
        )
    except json.JSONDecodeError as e:
        config_logger.error(
            f"Error parsing 'hephaestus_config.json': {e}. "
            "Falling back to defaults."
        )

    # Try fallback configuration
    try:
        with open("example_config.json", "r", encoding="utf-8") as f:
            config_logger.info(
                "Loaded default configuration from 'example_config.json'."
            )
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        config_logger.error(
            "Fallback configuration 'example_config.json' could not be "
            f"loaded: {e}. Using empty defaults."
        )

    return {}
