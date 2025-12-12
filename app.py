import sys

from PyQt5.QtWidgets import QApplication

from modules import AuthWindow
from core.worker import APIWorker
from utils import ThemeManagerInstance
from modules.main.main_module import MainWindow
from modules.auth.mvc.auth_model import AuthModel


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.auth_window = None

        # Set theme
        self.theme_manager = ThemeManagerInstance()
        self.theme_manager.switch_theme(theme=0)

        # Check auto login
        self.auth_model = AuthModel()
        if self.auth_model.get_auto_login_state():
            self.attempt_auto_login()
        else:
            self.show_auth_window()


    def attempt_auto_login(self):
        self.worker = APIWorker(self.auth_model.verify_token)
        self.worker.finished.connect(self.on_token_verified)
        self.worker.error.connect(self.on_token_verification_failed)
        self.worker.start()


    def on_token_verified(self, data):
        # Token is valid, show the main window
        self.show_main_window(mode="auth")


    def on_token_verification_failed(self, error):
        # Token is invalid or expired, clear data and show login
        print(f"Token verification failed: {error}. Refresh tokens...")
        self.worker = APIWorker(self.auth_model.refresh_tokens)
        self.worker.finished.connect(self.on_token_verified)
        self.worker.error.connect(self.on_token_refresh_failed)
        self.worker.start()


    def on_token_refresh_failed(self, error):
        print(f"Token refresh failed: {error}. Logging out...")
        self.auth_model.logout()
        self.show_auth_window()


    def show_auth_window(self):
        self.auth_window = AuthWindow()
        self.auth_window.controller.login_successful.connect(self.on_login_successful)
        self.auth_window.show()


    def show_main_window(self, mode: str = "auth"):
        self.main_window = MainWindow(mode=mode)
        self.main_window.controller.logout_requested.connect(self.on_logout_requested)
        self.main_window.show()


    def on_login_successful(self, mode: str):
        if self.auth_window:
            self.auth_window.close()
            self.auth_window = None

        # Guest mode doesn't need verification.
        # Auth mode just came from a successful login, so it's already verified.
        self.show_main_window(mode=mode)


    def on_logout_requested(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        # On logout, clear the stored user data
        self.auth_model.logout()
        self.show_auth_window()


    def run(self):
        sys.exit(self.app.exec_())



if __name__ == "__main__":
    app = Application()
    app.run()
