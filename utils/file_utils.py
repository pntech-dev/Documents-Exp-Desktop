import json
import yaml
import logging
from pathlib import Path
from utils.app_paths import get_app_root

def load_config() -> dict:
    """
    Loads the application configuration from the 'config.yaml' file.

    Returns:
        dict: The configuration dictionary.
    """
    try:
        config_path = get_app_root() / "config.yaml"
        with open(config_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            if data is None:
                return {}
            if not isinstance(data, dict):
                logging.error(
                    "Configuration file has invalid root type: expected mapping, got %s.",
                    type(data).__name__,
                )
                return {}
            return data
    except FileNotFoundError:
        logging.error("Configuration file not found.", exc_info=True)
        return {}
    except yaml.YAMLError as e:
        logging.error(f"Error parsing configuration file: {e}", exc_info=True)
        return {}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {}

def read_json(file_path: Path) -> dict | None:
    """
    Reads and parses a JSON file.

    Args:
        file_path (Path): The path to the JSON file.

    Returns:
        dict | None: The parsed JSON data or None if reading fails.
    """
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error reading JSON {file_path}: {e}", exc_info=True)
        return None
