import sys

from ui import AuthWindow_UI
from auth_mvc import AuthModel, AuthView, AuthController

from PyQt5.QtWidgets import QMainWindow, QApplication



class AuthWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.ui = AuthWindow_UI()
        self.ui.setupUi(self)

        print("Auth opened")



if __name__ == "__main__":
    app = QApplication(sys)
    application = AuthWindow()
    application.show()
    sys.exit(app.exec_())