from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal

from .main_model import MainModel
from .main_view import MainView


class MainController(QObject):
    logout_requested = pyqtSignal()

    def __init__(
            self, 
            model: MainModel, 
            view: MainView, 
            window: QMainWindow, 
            mode: str = "guest"
    ) -> None:
    
        super().__init__()
        self.model = model
        self.view = view
        self.window = window
        self.mode = mode


        """=== Handlers ==="""
        self.view.button_clicked(self.button_clicked_handler)


    def button_clicked_handler(self):
        self.logout_requested.emit()
