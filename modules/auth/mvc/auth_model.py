import yaml

from pathlib import Path

from api.api_client import APIClient


class AuthModel:
    def __init__(self) -> None:

        # Load configuration from YAML file
        self.config_data = self._load_config()

        # API Client Initialization
        self.api = APIClient(base_url=self.config_data.get("base_url", None))


    def login(self, email: str, password: str) -> dict:
        return self.api.login(email=email, password=password)


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