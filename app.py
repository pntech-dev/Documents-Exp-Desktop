import sys

from ui import MainWindow_UI
from utils import ThemeManager, ToastWidget
from modules.main.mvc import MainModel, MainView, MainController

from PyQt5.QtWidgets import QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # UI Initialization
        self.ui = MainWindow_UI()
        self.ui.setupUi(self)

        # Set theme
        self.theme_manager = ThemeManager()
        self.theme_manager.switch_theme(theme=0)

        # MVC Initialization
        self.model = MainModel()
        self.view = MainView(ui=self.ui)
        self.controller = MainController(model=self.model, view=self.view, window=self)

        # Notification
        self.toast = ToastWidget(type="info", label="Информация", description="Доступна новая версия приложения.\nНажмите чтобы обновить.")
        self.toast.show_notification()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())