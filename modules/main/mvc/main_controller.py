from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal

from .main_model import MainModel
from .main_view import MainView

from ui.ui_converted.custom_widgets import DeptItem


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

        """ Update UI """
        self._update_departments()
        self._update_categories()


    """=== Updaters ==="""

    def _update_departments(self):
        # TODO Change it with data from the database
        items = [
            DeptItem(id="tech", title="ТехУпр", count=23, icon=None),
            DeptItem(id="shop1", title="Цех №1", count=57, icon=None),
            DeptItem(id="shop19", title="Цех №19", count=964, icon=None),
            DeptItem(id="rmp", title="РМП", count=0, icon=None, disabled=True),
        ]

        self.view.sidebar.update_departments(departments=items)

    
    def _update_categories(self):
        # TODO Change it with data from the database
        items = [
            DeptItem(id="all_docs", title="Все документы", count=964, icon=None),
            DeptItem(id="standards_docs", title="Стандарты предприятия", count=64, icon=None),
            DeptItem(id="construct_docs", title="Конструкторская документация", count=144, icon=None),
            DeptItem(id="tech_docs", title="Технологическая документация", count=25, icon=None),
            DeptItem(id="notices", title="Извещения", count=453, icon=None),
            DeptItem(id="block-schemas", title="Блок-схемы", count=278, icon=None),
        ]
        self.view.sidebar.update_categories(categories=items)