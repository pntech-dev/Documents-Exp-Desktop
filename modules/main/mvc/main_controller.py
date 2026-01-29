from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal

from .main_model import MainModel
from .main_view import MainView

from ui.ui_converted.custom_widgets import SidebarItem


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
            SidebarItem(id="tech", title="ТехУпр", count=23, icon=None),
            SidebarItem(id="shop1", title="Цех №1", count=57, icon=None),
            SidebarItem(id="shop19", title="Цех №19", count=964, icon=None),
            SidebarItem(id="rmp", title="РМП", count=0, icon=None, disabled=True),
        ]

        self.view.sidebar.update_tree(items=items, group_title="Отделы", group_icon=None)

    
    def _update_categories(self):
        # TODO Change it with data from the database
        items = [
            SidebarItem(id="all_docs", title="Все документы", count=964, icon=None),
            SidebarItem(id="standards_docs", title="Стандарты предприятия", count=64, icon=None),
            SidebarItem(id="construct_docs", title="Конструкторская документация", count=144, icon=None),
            SidebarItem(id="tech_docs", title="Технологическая документация", count=25, icon=None),
            SidebarItem(id="notices", title="Извещения", count=453, icon=None),
            SidebarItem(id="block-schemas", title="Блок-схемы", count=278, icon=None),
        ]

        self.view.sidebar.update_tree(items=items, group_title="Категории", group_icon=None)