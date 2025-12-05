from ui import MainWindow_UI


class MainView:
    def __init__(self, ui: MainWindow_UI) -> None:
        self.ui = ui


    def button_clicked(self, handler):
        self.ui.pushButton.clicked.connect(handler)