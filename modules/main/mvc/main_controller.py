from PyQt5.QtWidgets import QMainWindow
from .main_model import MainModel
from .main_view import MainView
from modules.auth.auth_module import AuthWindow


class MainController:
    def __init__(self, model: MainModel, view: MainView, window: QMainWindow) -> None:
        self.model = model
        self.view = view
        self.window = window


        """=== Handlers ==="""

        self.view.button_clicked(self.button_clicked_handler)


    def button_clicked_handler(self):
        self.auth = AuthWindow()
        self.auth.show()
        self.window.close()