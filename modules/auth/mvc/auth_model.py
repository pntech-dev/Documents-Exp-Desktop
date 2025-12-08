import yaml
import json
import keyring
import logging

from pathlib import Path
from keyring import errors as keyring_errors

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
        """Verify token for the last logged-in user."""

        def read_json(file_path: Path) -> dict | None:
            if not file_path.exists():
                return None
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logging.error(f"Error reading or parsing JSON from {file_path}: {e}")
                return None

        # Find user_id of the last logged-in user
        local_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        last_logged_file = local_dir / "last_logged.json"

        last_logged_data = read_json(last_logged_file)
        if not last_logged_data:
            raise ValueError("No last logged user file found.")

        user_id = last_logged_data.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in last logged user file.")

        # Get the token for that user
        access_token = keyring.get_password(
            service_name="Documents Exp",
            username=f"access_token_{user_id}"
        )

        if not access_token:
            raise ValueError(f"Access token for user_id {user_id} not found in keyring.")

        # Verify via API
        return self.api.verify(token=access_token)
    

    def refresh_tokens(self) -> dict:
        """
        Refreshes the access and refresh tokens for the last logged-in user.
        
        Raises:
            ValueError: If the last logged-in user or their refresh token cannot be found.
        
        Returns:
            dict: A dictionary containing the new access and refresh tokens.
        """
        def read_json(file_path: Path) -> dict | None:
            if not file_path.exists():
                return None
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logging.error(f"Error reading or parsing JSON from {file_path}: {e}")
                return None

        # 1. Find user_id of the last logged-in user
        local_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        last_logged_file = local_dir / "last_logged.json"

        last_logged_data = read_json(last_logged_file)
        if not last_logged_data:
            raise ValueError("No last logged user file found. Cannot refresh tokens.")

        user_id = last_logged_data.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in last logged user file. Cannot refresh tokens.")

        # 2. Get the current refresh token for that user
        try:
            refresh_token = keyring.get_password(
                service_name="Documents Exp",
                username=f"refresh_token_{user_id}"
            )
        except keyring_errors.NoKeyringError:
            raise RuntimeError("Keyring backend not found. Please install a backend library.")

        if not refresh_token:
            raise ValueError(f"Refresh token for user_id {user_id} not found in keyring.")

        # 3. Call the API to get new tokens
        new_tokens = self.api.refresh(refresh_token=refresh_token)

        # 4. Save the new tokens, overwriting the old ones
        new_access_token = new_tokens.get("access_token")
        new_refresh_token = new_tokens.get("refresh_token")

        if not new_access_token or not new_refresh_token:
            raise ValueError("API response for token refresh did not contain new tokens.")

        keyring.set_password(
            service_name="Documents Exp",
            username=f"access_token_{user_id}",
            password=new_access_token
        )
        keyring.set_password(
            service_name="Documents Exp",
            username=f"refresh_token_{user_id}",
            password=new_refresh_token
        )
        
        logging.info(f"Successfully refreshed tokens for user_id {user_id}.")

        # 5. Return the new tokens
        return new_tokens


    def logout(self) -> None:
        """
        Logs out the user by deleting session tokens and disabling auto-login.
        This action clears the user's session from the device but keeps their profile data.
        """
        def delete_file(file_path: Path) -> None:
            if file_path.exists():
                file_path.unlink()

        def read_json(file_path: Path) -> dict | None:
            if not file_path.exists():
                return None
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                logging.error(f"Error reading or parsing JSON from {file_path}: {e}")
                return None

        # Paths
        local_dir = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        last_logged_file = local_dir / "last_logged.json"

        # Get last user id
        last_logged_data = read_json(last_logged_file)
        if not last_logged_data:
            logging.info("No last logged user file found. Nothing to log out.")
            return

        user_id = last_logged_data.get("user_id")

        if user_id:
            # 1. Clear user-specific tokens from keyring to end the session
            try:
                keyring.delete_password(service_name="Documents Exp", username=f"access_token_{user_id}")
                keyring.delete_password(service_name="Documents Exp", username=f"refresh_token_{user_id}")
                logging.info(f"Tokens for user_id {user_id} deleted from keyring.")
            except keyring_errors.PasswordDeleteError:
                logging.info(f"Tokens for user_id {user_id} not found in keyring, skipping deletion.")

        # 2. Delete the last logged user file to disable auto-login on next start
        delete_file(last_logged_file)
        logging.info("Last logged user file deleted to disable auto-login. User is fully logged out.")


    def save_user(self, user_data: dict, auto_login: bool) -> None:
        # Get user data
        user = user_data.get("user", None)
        user_id = user.get("id", None)

        # Save access and refresh tokens
        keyring.set_password(
            service_name="Documents Exp", 
            username=f"access_token_{user_id}", 
            password=user_data.get("access_token", None)
        )

        keyring.set_password(
            service_name="Documents Exp", 
            username=f"refresh_token_{user_id}", 
            password=user_data.get("refresh_token", None)
        )

        # Save user data
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