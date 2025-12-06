import yaml
import json
import keyring
import logging

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


    def verify_token(self) -> dict:
        access_token = keyring.get_password(
            service_name="Documents Exp",
            username="access_token"
        )
        return self.api.verify(token=access_token)


    def logout(self) -> None:
        """Clear user data"""

        def delete_file(file_path: Path) -> None:
            if file_path.exists():
                file_path.unlink()

        # Clear keyring
        try:
            keyring.delete_password(service_name="Documents Exp", username="access_token")
            keyring.delete_password(service_name="Documents Exp", username="refresh_token")
            
        except keyring.errors.PasswordNotFoundError:
            logging.info("Tokens not found in keyring, skipping deletion.")

        # Paths
        app_dir = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp'
        local_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        last_logged_file = local_dir / "last_logged.json"

        # Get last user id
        if last_logged_file.exists():
            try:
                with open(last_logged_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                user_id = data.get("user_id")

                if user_id:
                    user_data_file = app_dir / 'Profiles' / f"user_data_{user_id}.json"
                    delete_file(user_data_file)

                delete_file(last_logged_file)

            except (json.JSONDecodeError, Exception) as e:
                logging.error(f"Error processing last logged user file: {e}")


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
            # AppData/Roaming/...
            base_dir = Path.home() / 'AppData' / 'Roaming'

            # AppData/Roaming/Documents Exp...
            app_dir = base_dir / "Documents Exp" / "Profiles"

            # AppData/Local/Documents Exp...
            local_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'

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

        def read_json(file_path: Path) -> dict | None:
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
            
        
        def get_flag(path: Path) -> bool:
            data = read_json(file_path=path)
            
            return data.get("auto_login", None) is True if isinstance(data, dict) else False


        # If app folder not exists
        app_dir = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp' / 'Profiles'

        if not app_dir.exists():
            return False
        
        # Check number of users profiles
        users_profiles = [
            file for file in app_dir.iterdir() 
            if file.is_file() and file.name.startswith("user_data_") and file.suffix == ".json"
        ]

        # If not user profiles
        if len(users_profiles) == 0:
            return False
        
        # If more then 1 user profile
        if len(users_profiles) == 1:
            return get_flag(path=users_profiles[0])
        
        else:
            # Get the last logged in user
            local_app_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
            last_user_profile = local_app_dir / "last_logged.json"
            
            # Get user from file
            data = read_json(file_path=last_user_profile)
            if data is None:
                return False
            
            # Check user id
            user_id = data.get("user_id", None)
            if not isinstance(user_id, int):
                return False

            # Path to user_data file
            user_data_file_path = app_dir / f"user_data_{user_id}.json"
            
            return get_flag(path=user_data_file_path)


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