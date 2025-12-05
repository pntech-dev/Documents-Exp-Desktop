import sys

from PyQt5.QtWidgets import QApplication

from modules import AuthWindow
from modules.main.main_module import MainWindow
from modules.auth.mvc.auth_model import AuthModel

class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = None
        self.auth_window = None

        auth_model = AuthModel()
        if auth_model.get_auto_login_state():
            self.show_main_window()
        else:
            self.show_auth_window()

    def show_auth_window(self):
        self.auth_window = AuthWindow()
        self.auth_window.controller.login_successful.connect(self.on_login_successful)
        self.auth_window.show()

    def show_main_window(self):
        self.main_window = MainWindow()
        self.main_window.controller.logout_requested.connect(self.on_logout_requested)
        self.main_window.show()

    def on_login_successful(self):
        if self.auth_window:
            self.auth_window.close()
            self.auth_window = None
        self.show_main_window()

    def on_logout_requested(self):
        if self.main_window:
            self.main_window.close()
            self.main_window = None
        self.show_auth_window()

    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = Application()
    app.run()
