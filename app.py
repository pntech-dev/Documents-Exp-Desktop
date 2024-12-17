import sys

from delib import *
from config import *

from PyQt5 import QtWidgets
from ui.DE_UI import Ui_MainWindow

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Buttons
        buttons = [
            [self.ui.pushButton, "Конструторская документация", KD_DOCUMENT_PATH],
            [self.ui.pushButton_2, "Операционные карты", OP_DOCUMENT_PATH],
            [self.ui.pushButton_3, "Стандарты предприятия", STP_DOCUMENT_PATH],
            [self.ui.pushButton_4, "Технологическая документация", TD_DOCUMENT_PATH],
            [self.ui.pushButton_5, "Технические условия", TY_DOCUMENT_PATH]
        ]

        for button in buttons:
            button[0].clicked.connect(lambda checked, b=button: self.ui.label.setText(f"{self.ui.label.text()[0:9]} {b[1]}"))
            button[0].clicked.connect(lambda checked, b=button: button_clicked(lineEdit=self.ui.lineEdit, document_path=b[2], table_view=self.ui.tableView))

        # Table
        self.ui.tableView.doubleClicked.connect(lambda index: double_clicked(table=self.ui.tableView, index=index, lineEdit=self.ui.lineEdit, label=self.ui.label))

app = QtWidgets.QApplication([])
application = MyWindow()
application.show()
sys.exit(app.exec())