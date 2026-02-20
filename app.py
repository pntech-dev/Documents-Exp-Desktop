import os
import sys
import ctypes
import requests
import logging
from logging.handlers import RotatingFileHandler

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from modules import AuthWindow
from core.worker import APIWorker
from utils import ThemeManagerInstance, NotificationService
from modules.main.main_module import MainWindow
from modules.auth.mvc.auth_model import AuthModel
from utils.error_messages import get_friendly_error_message
from utils.app_paths import get_local_data_dir
from core.updater import UpdateManager
from utils.file_utils import load_config


os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_SCALE_FACTOR_ROUNDING_POLICY", "PassThrough")


APP_VERSION = "0.1.0"

class Application:
    """
    Main application class that manages the lifecycle of the application.

    It handles initialization, window management (AuthWindow, MainWindow),
    auto-login logic, and global error handling for token verification.
    """
    def __init__(self):
        """Initializes the Application, sets up logging, theme, and checks for auto-login."""
        # Fix for Windows taskbar icon
        if sys.platform == "win32":
            myappid = 'pntech.documents_exp.desktop.3.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon(":/light/logo_icon_light.svg"))

        self.main_window = None
        self.auth_window = None

        # Setup logging
        log_dir = get_local_data_dir()
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                RotatingFileHandler(
                    log_dir / "app.log", 
                    maxBytes=5*1024*1024, # 5 MB
                    backupCount=2,
                    encoding="utf-8"
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("App")

        # Set theme
        self.theme_manager = ThemeManagerInstance()
        self.theme_manager.switch_theme(theme=1)

        # Check for updates
        self.check_for_updates()

        # Check auto login
        self.auth_model = AuthModel()
        if self.auth_model.get_auto_login_state():
            self.attempt_auto_login()
        else:
            # NotificationService is initialized in AuthWindow
            self.show_auth_window()

    def check_for_updates(self):
        """Checks for updates using the GitHub repository specified in config."""
        config = load_config()
        github_repo = config.get("github_repo")
        if github_repo:
            self.update_manager = UpdateManager(APP_VERSION, github_repo)
            self.update_manager.check_for_updates(silent=True)

    def attempt_auto_login(self):
        """Attempts to automatically log in the user using stored tokens."""
        self.worker = APIWorker(self.auth_model.verify_token)
        self.worker.finished.connect(self.on_token_verified)
        self.worker.error.connect(self.on_token_verification_failed)
        self.worker.start()


    def on_token_verified(self, data):
        """
        Callback for successful token verification.

        Args:
            data (dict): The data returned from the verification API.
        """
        # Token is valid, show the main window
        self.show_main_window(mode="auth")


    def on_token_verification_failed(self, error):
        """
        Callback for failed token verification.

        Args:
            error (Exception): The exception that occurred during verification.
        """
        # Token is invalid or expired, clear data and show login
        if isinstance(error, requests.exceptions.ConnectionError):
            self.show_auth_window()
            NotificationService().show_toast(
                notification_type="error",
                title="Ошибка подключения",
                message="Не удалось подключиться к серверу."
            )
            return

        self.logger.warning(f"Token verification failed: {error}. Refresh tokens...")
        self.worker = APIWorker(self.auth_model.refresh_tokens)
        self.worker.finished.connect(self.on_token_verified)
        self.worker.error.connect(self.on_token_refresh_failed)
        self.worker.start()


    def on_token_refresh_failed(self, error):
        """
        Callback for failed token refresh.

        Args:
            error (Exception): The exception that occurred during refresh.
        """
        self.logger.error(f"Token refresh failed: {error}. Logging out...")
        self.auth_model.logout()
        self.show_auth_window()
        NotificationService().show_toast(
            notification_type="warning",
            title="Сессия истекла",
            message="Срок действия сессии истек. Пожалуйста, войдите снова."
        )


    def show_auth_window(self):
        """Displays the authentication window."""
        self.auth_window = AuthWindow()
        self.auth_window.controller.login_successful.connect(self.on_login_successful)
        self.auth_window.show()


    def show_main_window(self, mode: str = "auth"):
        """
        Displays the main application window.

        Args:
            mode (str): The mode to open the window in ('auth' or 'guest').
        """
        try:
            self.main_window = MainWindow(mode=mode)
            self.main_window.logout_requested.connect(self.on_logout_requested)
            self.main_window.showMaximized()

            if self.auth_window:
                self.auth_window.close()
                self.auth_window = None

        except Exception as e:
            self.logger.critical(f"Error initializing MainWindow: {e}", exc_info=True)
            if not self.auth_window:
                self.show_auth_window()
            
            msg = get_friendly_error_message(e)
            NotificationService().show_toast(
                notification_type="error",
                title="Ошибка запуска",
                message=msg
            )


    def on_login_successful(self, mode: str):
        """
        Handles successful login event from AuthWindow.

        Args:
            mode (str): The mode of login ('auth' or 'guest').
        """
        # Guest mode doesn't need verification.
        # Auth mode just came from a successful login, so it's already verified.
        self.show_main_window(mode=mode)


    def on_logout_requested(self):
        """Handles logout request from MainWindow."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        # On logout, clear the stored user data
        self.auth_model.logout()
        self.show_auth_window()


    def run(self):
        """Starts the application event loop."""
        sys.exit(self.app.exec_())
        
        
if __name__ == "__main__":
    app = Application()
    app.run()
