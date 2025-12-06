from ui import AuthWindow_UI
from utils import ThemeManager
from .mvc import AuthModel, AuthView, AuthController

from PyQt5.QtWidgets import QMainWindow


class AuthWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # UI Initialization
        self.ui = AuthWindow_UI()
        self.ui.setupUi(self)

        # Set theme
        self.theme_manager = ThemeManager()
        self.theme_manager.switch_theme(theme=0)

        # MVC Initialization
        self.model = AuthModel()
        self.view = AuthView(ui=self.ui)
        self.controller = AuthController(model=self.model, 
                                         view=self.view, 
                                         window=self)