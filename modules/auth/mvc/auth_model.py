import yaml
import json
import keyring

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
    

    def save_user(self, user_data: dict, auto_login: bool) -> None:
        # Save access_token
        keyring.set_password(
            service_name="Documents Exp", 
            username="access_token", 
            password=user_data.get("access_token", None)
        )

        # Save user data
        user = user_data.get("user", None)
        
        if Path.home():
            base_dir = Path.home() / 'AppData' / 'Roaming' # AppData/Roaming/...
            app_dir = base_dir / "Documents Exp" # AppData/Roaming/Documents Exp...

            # Create app folder if not exists or continue
            app_dir.mkdir(parents=True, exist_ok=True)

            # Write a data
            user_data_file_path = app_dir / "user_data.json"

            data = {
                "user": {
                    "id": user.get("id", None),
                    "email": user.get("email", None),
                    "username": user.get("username", None),
                    "department": user.get("department", None)
                },
                "auto_login": auto_login
            }

            with open(user_data_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)


    def get_auto_login_state(self) -> bool:
        """Check auto login flag"""
        if Path.home():
            # If app folder not exists
            app_dir = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp'

            if not app_dir.exists():
                return False
            
            # Path to user_data file
            user_data_file_path = app_dir / "user_data.json"

            if not user_data_file_path.exists():
                return False

            # Read user_data file
            with open(user_data_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Get auto_login flag
            auto_login = data.get("auto_login", None)

            return False if auto_login is None else auto_login
        
        else:
            return False


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