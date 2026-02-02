import yaml
import json
import keyring
import logging

from pathlib import Path

from api.api_client import APIClient


class MainModel:
    def __init__(self) -> None:
        self.config_data = self._load_config()

        # API Client Initialization
        self.api = APIClient(base_url=self.config_data.get("base_url", None))
        
        # Constants
        self.APP_DIR = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp'
        self.LOCAL_DIR = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        self.LOCAL_DIR_LAST_LOGGED = self.LOCAL_DIR / "last_logged.json"

        # Sidebar data
        self.departments = self._get_departments()
        self.current_department_id = self.departments[0]["id"]
        self.categories = self._get_categories()


    # ====================
    # Model Methods
    # ====================

    
    def _load_config(self) -> dict:
        try:
            config_path = Path(Path.cwd(), "config.yaml")

            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)

            return config
        
        except FileNotFoundError:
            print("Configuration file not found.")
            return {}
        
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            return {}
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {}
        
        
    def _read_json(self, file_path: Path) -> dict | None:
        """Reads and parses a JSON file.

        Args:
            file_path: The path to the JSON file.

        Returns:
            A dictionary with the JSON data or None if the file doesn't exist
            or an error occurs during reading or parsing.
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data
        
        except json.JSONDecodeError:
            logging.error(msg="JSONDecodeError", exc_info=True)
            return None
        
        except Exception as e:
            logging.error(msg=e, exc_info=True)
            return None


    def _get_departments(self) -> list[dict]:
        departments = self.api.get_departments()
        return departments["departments"]


    def _get_categories(self) -> list[dict]:
        categories = self.api.get_categories()
        return categories["categories"]