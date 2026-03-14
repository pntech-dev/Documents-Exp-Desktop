import keyring
import json
import logging

from pathlib import Path
from keyring import errors as keyring_errors

from api.api_client import APIClient
from utils.app_paths import get_app_data_dir, get_local_data_dir
from utils.file_utils import load_config, read_json


class AuthModel:
    def __init__(self) -> None:

        # Load configuration from YAML file
        self.config_data = load_config()

        # API Client Initialization
        self.api = APIClient(base_url=self.config_data.get("base_url", None))

        # Constants
        self.APP_DIR = get_app_data_dir()
        self.LOCAL_DIR = get_local_data_dir()
        self.LOCAL_DIR_LAST_LOGGED = self.LOCAL_DIR / "last_logged.json"


    # ====================
    # Model Base Methods
    # ====================


    """=== Login ==="""
    def login(self, email: str, password: str) -> dict:
        """Sends a login request to the API.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            A dictionary containing the API response.
        """
        return self.api.login(email=email, password=password)



    """=== Signup ==="""
    def signup(self, code: str, email: str, password: str) -> dict:
        """Sends a signup request to the API.

        Args:
            code: The confirmation code sent to the user's email.
            email: The user's email address.
            password: The user's desired password.

        Returns:
            A dictionary containing the API response.
        """
        return self.api.signup(code=code, email=email, password=password)


    def signup_send_code(self, email: str) -> dict:
        """Sends a signup confirmation code to the user's email.

        Args:
            email: The user's email address.

        Returns:
            A dictionary containing the API response.
        """
        return self.api.signup_send_code(email=email)



    """=== Reset password ==="""
    def request_reset_password(self, email: str) -> dict:
        """Sends a password reset request to the API.

        Args:
            email: The user's email address.

        Returns:
            A dictionary containing the API response.
        """
        return self.api.request_reset_password(email=email)


    def reset_password_confirm_email(self, email: str, code: str) -> dict:
        """Confirms the password reset with a code.

        Args:
            email: The user's email address.
            code: The confirmation code sent to the user's email.

        Returns:
            A dictionary containing the API response.
        """
        return self.api.reset_password_confirm_email(email=email, code=code)


    def reset_password(self, password: str) -> dict:
        """Resets the password using a reset token.

        Retrieves the reset token from the keyring and sends the new password
        to the API.

        Args:
            password: The new password.

        Returns:
            A dictionary containing the API response.
        """
        token = keyring.get_password(
            service_name="Documents Exp",
            username="reset_token"
        )

        return self.api.reset_password(reset_token=token, password=password)
    

    # ====================
    # Model Secondary Methods
    # ====================


    """=== User ==="""
    def save_user(self, user_data: dict, auto_login: bool) -> int | None:
        """Saves user data and tokens to local files and keyring.

        Args:
            user_data: A dictionary containing user information and tokens.
            auto_login: A boolean indicating whether to enable auto-login.
        """
        # Get user data
        user = user_data.get("user", None)
        if not user:
            return None

        user_id = user.get("id", None)

        # Save access and refresh tokens
        self.save_token(token_name=f"access_token_{user_id}", token="access_token", data=user_data)
        self.save_token(token_name=f"refresh_token_{user_id}", token="refresh_token", data=user_data)

        # Save user data
        if Path.home():
            # AppData/Roaming/Documents Exp/Profiles...
            app_dir = self.APP_DIR / "Profiles"

            # Create app folders if not exists or continue
            app_dir.mkdir(parents=True, exist_ok=True)

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
            data = {
                "user_id": user_id
            }

            # Ensure the directory exists before writing
            self.LOCAL_DIR.mkdir(parents=True, exist_ok=True)

            with open(self.LOCAL_DIR_LAST_LOGGED, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        
        return user_id


    """=== Login ==="""
    def get_auto_login_state(self) -> bool:
        """Checks if auto-login is enabled for the last logged-in user.

        Returns:
            True if auto-login is enabled, False otherwise.
        """

        def get_flag(path: Path) -> bool:
            data = read_json(file_path=path)
            
            return data.get("auto_login", None) is True if isinstance(data, dict) else False


        # If app folder not exists
        app_dir = self.APP_DIR / 'Profiles'

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
            # Get user from file
            data = read_json(file_path=self.LOCAL_DIR_LAST_LOGGED)
            if data is None:
                return False
            
            # Check user id
            user_id = data.get("user_id", None)
            if not isinstance(user_id, int):
                return False

            # Path to user_data file
            user_data_file_path = app_dir / f"user_data_{user_id}.json"
            
            return get_flag(path=user_data_file_path)


    def get_last_logged_user_id(self) -> int | None:
        """
        Retrieves the user ID of the last successfully logged-in user.

        Returns:
            The user ID as an integer, or None if not found.
        """
        last_logged_data = read_json(self.LOCAL_DIR_LAST_LOGGED)
        if not last_logged_data:
            return None
        
        user_id = last_logged_data.get("user_id")

        return user_id if isinstance(user_id, int) else None


    def logout(self) -> None:
        """Logs out the current user.

        This function deletes the user's session tokens from the keyring and
        removes the file that indicates the last logged-in user, effectively
        disabling auto-login.
        """
        def delete_file(file_path: Path) -> None:
            if file_path.exists():
                file_path.unlink()

        # Get last user id
        last_logged_data = read_json(self.LOCAL_DIR_LAST_LOGGED)
        if not last_logged_data:
            logging.info("No last logged user file found. Nothing to log out.")
            return

        user_id = last_logged_data.get("user_id")

        if user_id:
            # Clear user-specific tokens from keyring to end the session
            try:
                keyring.delete_password(service_name="Documents Exp", username=f"access_token_{user_id}")
                keyring.delete_password(service_name="Documents Exp", username=f"refresh_token_{user_id}")
                logging.info(f"Tokens for user_id {user_id} deleted from keyring.")
            except keyring_errors.PasswordDeleteError:
                logging.info(f"Tokens for user_id {user_id} not found in keyring, skipping deletion.")

        # Delete the last logged user file to disable auto-login on next start
        delete_file(self.LOCAL_DIR_LAST_LOGGED)
        logging.info("Last logged user file deleted to disable auto-login. User is fully logged out.")


    """=== Token ==="""
    def verify_token(self) -> dict:
        """Verifies the access token of the last logged-in user.

        Raises:
            ValueError: If the last logged-in user's data or access token
                cannot be found.

        Returns:
            A dictionary containing the API response from the token
            verification endpoint.
        """

        # Find user_id of the last logged-in user
        last_logged_data = read_json(self.LOCAL_DIR_LAST_LOGGED)
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

        # Find user_id of the last logged-in user
        last_logged_data = read_json(self.LOCAL_DIR_LAST_LOGGED)
        if not last_logged_data:
            raise ValueError("No last logged user file found. Cannot refresh tokens.")

        user_id = last_logged_data.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in last logged user file. Cannot refresh tokens.")

        # Get the current refresh token for that user
        try:
            refresh_token = keyring.get_password(
                service_name="Documents Exp",
                username=f"refresh_token_{user_id}"
            )
        except keyring_errors.NoKeyringError:
            raise RuntimeError("Keyring backend not found. Please install a backend library.")

        if not refresh_token:
            raise ValueError(f"Refresh token for user_id {user_id} not found in keyring.")

        # Call the API to get new tokens
        new_tokens = self.api.refresh(refresh_token=refresh_token)

        # Save the new tokens, overwriting the old ones
        self.save_token(token_name=f"access_token_{user_id}", token="access_token", data=new_tokens)
        self.save_token(token_name=f"refresh_token_{user_id}", token="refresh_token", data=new_tokens)
        
        logging.info(f"Successfully refreshed tokens for user_id {user_id}.")

        # Return the new tokens
        return new_tokens


    def save_token(self, token_name: str, token: str, data: dict) -> None:
        """Saves a token to the system's keyring.

        Args:
            token_name: The name to use as the username in the keyring.
            token: The key for the token in the data dictionary.
            data: A dictionary containing the token to save.
        """
        try:
            keyring.set_password(
                service_name="Documents Exp", 
                username=token_name, 
                password=data.get(token, None)
            )
        
        except keyring_errors.PasswordSetError as e:
            logging.error(msg="PasswordSetError", exc_info=True)
            raise RuntimeError("Не удалось сохранить данные сессии в системное хранилище.") from e
        except Exception as e:
            logging.error(msg=e, exc_info=True)
            raise RuntimeError("Не удалось сохранить данные сессии в системное хранилище.") from e
