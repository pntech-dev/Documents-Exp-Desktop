from modules import AuthWindow

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication


class AppWindow(QMainWindow):
    def __init__(self):
        pass

        print("app was started")


if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)
    application: AppWindow = AppWindow()
    application.show()
    sys.exit(app.exec_())