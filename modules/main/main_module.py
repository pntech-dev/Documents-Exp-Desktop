from ui import MainWindow_UI
from .mvc import MainModel, MainView, MainController
from utils import ThemeManagerInstance, NotificationService

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
        self.showMaximized()

        # Set theme
        self.theme_manager = ThemeManagerInstance()

        # Setup Notification Service
        NotificationService().set_main_window(self)
        NotificationService().show_toast(
            notification_type="info",
            title="Главное окно",
            message="Добро пожаловать!"
        )

        # MVC Initialization
        self.model = MainModel()
        self.view = MainView(ui=self.ui)
        self.controller = MainController(
            model=self.model, 
            view=self.view, 
            window=self, 
            mode=self.mode
        )