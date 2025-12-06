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
    

    def signup(self, email: str, password: str) -> dict:
        return self.api.signup(email=email, password=password)
    

    def save_user(self, user_data: dict, auto_login: bool) -> None:
        # Save access and refresh tokens
        keyring.set_password(
            service_name="Documents Exp", 
            username="access_token", 
            password=user_data.get("access_token", None)
        )

        keyring.set_password(
            service_name="Documents Exp", 
            username="refresh_token", 
            password=user_data.get("refresh_token", None)
        )

        # Save user data
        user = user_data.get("user", None)
        
        if Path.home():
            base_dir = Path.home() / 'AppData' / 'Roaming' # AppData/Roaming/...
            app_dir = base_dir / "Documents Exp" # AppData/Roaming/Documents Exp...
            local_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp' # AppData/Local/Documents Exp...

            # Create app folders if not exists or continue
            app_dir.mkdir(parents=True, exist_ok=True)
            local_dir.mkdir(parents=True, exist_ok=True)

            # Write a data
            user_id = user.get("id", None)
            user_data_file_path = app_dir / f"user_data_{user_id}.json"

            data = {
                "user": {
                    "id": user_id,
                    "email": user.get("email", None),
                    "username": user.get("username", None),
                    "department": user.get("department", None)
                },
                "auto_login": auto_login
            }

            with open(user_data_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            # Rewrite last logged in user
            last_user_profile = local_dir / "last_logged.json"

            data = {
                "user_id": user_id
            }

            with open(last_user_profile, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)


    def get_auto_login_state(self) -> bool:
        """Check auto login flag"""
        if Path.home():
            # If app folder not exists
            app_dir = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp'

            if not app_dir.exists():
                return False
            
            # Check number of users profiles
            users_profiles = app_dir.iterdir()

            # If not user profiles
            if len(list(users_profiles)) == 0:
                return False
            
            # If more then 1 user profile
            if len(list(users_profiles)) == 1:
                # Path to user_data file
                user_data_file_path = app_dir / users_profiles[0].name

                if not user_data_file_path.exists():
                    return False

                # Read user_data file
                with open(user_data_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Get auto_login flag
                auto_login = data.get("auto_login", None)

                return False if auto_login is None else auto_login
            
            else:
                # Get the last logged in user
                local_app_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
                last_user_profile = local_app_dir / "last_logged.json"

                # Check if file exists
                if not last_user_profile.exists():
                    return False
                
                # Get user from file
                with open(last_user_profile, "r", encoding="utf-8") as f:
                    data = json.load(f)

                user_id = data.get("user_id", None)

                # Path to user_data file
                user_data_file_path = app_dir / f"user_data_{user_id}.json"

                if not user_data_file_path.exists():
                    return False
                
                # Read user_data file
                with open(user_data_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

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