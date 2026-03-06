from ui import MainWindow_UI
from utils import ThemeManagerInstance
from .mvc import MainModel, MainView, MainController

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow


from utils.settings_manager import SettingsManager

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, mode: str = "guest", settings_manager: SettingsManager | None = None) -> None:
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Application work mode ('guest' - Guest mode, 'auth' - Authorized mode)
        self.mode = mode
        self.settings_manager = settings_manager

        # UI Initialization
        self.ui = MainWindow_UI()
        self.ui.setupUi(self)

        # Set theme
        self.theme_manager = ThemeManagerInstance

        # MVC Initialization
        self.model = MainModel(mode=self.mode)
        self.view = MainView(ui=self.ui)
        self.controller = MainController(
            model=self.model, 
            view=self.view, 
            window=self, 
            mode=self.mode,
            settings_manager=self.settings_manager
        )
        # Logout signal
        self.controller.logout_requested.connect(self.logout_requested.emit)