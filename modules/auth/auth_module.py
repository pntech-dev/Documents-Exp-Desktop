from ui import AuthWindow_UI
from .mvc import AuthModel, AuthView, AuthController
from utils import NotificationService

from PyQt5.QtWidgets import QMainWindow


class AuthWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # UI Initialization
        self.ui = AuthWindow_UI()
        self.ui.setupUi(self)

        # Setup Notification Service
        NotificationService().set_main_window(self)

        # MVC Initialization
        self.model = AuthModel()
        self.view = AuthView(ui=self.ui)
        self.controller = AuthController(model=self.model, 
                                         view=self.view, 
                                         window=self)