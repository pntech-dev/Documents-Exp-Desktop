from ui import MainWindow_UI
from utils import ThemeManager
from .mvc import MainModel, MainView, MainController

from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, mode: str = "guest") -> None:
        super().__init__()

        # Application work mode ('guest' - Guest mode, 'auth' - Authorized mode)
        self.mode = mode

        print(self.mode)

        # UI Initialization
        self.ui = MainWindow_UI()
        self.ui.setupUi(self)

        # Set theme
        self.theme_manager = ThemeManager()
        self.theme_manager.switch_theme(theme=0)

        # MVC Initialization
        self.model = MainModel()
        self.view = MainView(ui=self.ui)
        self.controller = MainController(
            model=self.model, 
            view=self.view, 
            window=self, 
            mode=self.mode
        )