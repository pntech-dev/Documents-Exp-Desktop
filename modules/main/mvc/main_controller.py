from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal

from .main_view import MainView
from .main_model import MainModel
from ui.ui_converted.custom_widgets import SidebarItem



class MainController(QObject):
    """Controller for the main application window.

    Manages the interaction between the MainModel and MainView, handling
    user input and updating the UI state.
    """
    logout_requested = pyqtSignal()

    def __init__(
            self, 
            model: MainModel, 
            view: MainView, 
            window: QMainWindow, 
            mode: str = "guest"
    ) -> None:
        """Initializes the MainController.

        Args:
            model: The data model.
            view: The main UI view.
            window: The main QMainWindow instance.
            mode: The application mode ('guest' or 'auth').
        """
        super().__init__()
        self.model = model
        self.view = view
        self.window = window
        self.mode = mode

        self._init_ui()
        self._setup_connections()


    # ====================
    # Controller Handlers
    # ====================


    def _on_theme_switcher_clicked(self, checked: bool) -> None:
        """Handles the theme switcher button click.

        Calls the view's `set_theme` method to toggle between light and dark
        themes for the application.
        """
        self.view.set_theme()

    def _on_logout_clicked(self) -> None:
        """Handles the logout action."""
        self.logout_requested.emit()


    # ====================
    # Controller Methods
    # ====================


    def _init_ui(self) -> None:
        """Initializes the UI with default data."""
        self._load_sidebar_data()
        self.view.set_profile_mode(self.mode)


    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""
        self.view.connect_theme_switch(self._on_theme_switcher_clicked)
        self.view.connect_logout(self._on_logout_clicked)


    def _load_sidebar_data(self) -> None:
        """Loads and updates sidebar data (departments and categories)."""

        # Departments
        dept_items = []

        for dept in self.model.departments:
            dept_items.append(SidebarItem(id=dept["id"], title=dept["name"], count=0, icon=None))
            
        self.view.update_departments(dept_items)

        # Categories
        cat_items = []
        for cat in self.model.categories:
            if cat["group_id"] == self.model.current_department_id:
                cat_items.append(SidebarItem(id=cat["id"], title=cat["name"], count=0, icon=None))
            
        self.view.update_categories(cat_items)