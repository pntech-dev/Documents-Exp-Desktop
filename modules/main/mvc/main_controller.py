from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal

from .main_view import MainView
from .main_model import MainModel
from ui.ui_converted.custom_widgets import SidebarItem, ROLE_ID



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

    def _on_department_selected(self, selected, deselected) -> None:
        """Handles department selection change."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            dept_id = index.data(ROLE_ID)

            if dept_id:
                self.model.current_department_id = dept_id
                self._update_categories_list()
                print(f"Department selected ID: {dept_id}")

    def _on_category_selected(self, selected, deselected) -> None:
        """Handles category selection change."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            cat_id = index.data(ROLE_ID)

            if cat_id:
                self.model.current_category_id = cat_id
                print(f"Category selected ID: {cat_id}")


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
        self.view.connect_departments_selection(self._on_department_selected)
        self.view.connect_categories_selection(self._on_category_selected)


    def _load_sidebar_data(self) -> None:
        """Loads and updates sidebar data (departments and categories)."""
        dept_items = []

        for dept in self.model.departments:
            dept_items.append(
                SidebarItem(
                    id=dept["id"], 
                    title=dept["name"], 
                    count=dept.get("documents_count", 0), 
                    icon=None
                )
            )
            
        self.view.update_departments(dept_items)
        self._update_categories_list()

    def _update_categories_list(self) -> None:
        """Updates the categories list based on the current department."""
        cat_items = []
        for cat in self.model.categories:
            if self.model.current_department_id and cat.get("group_id") == self.model.current_department_id:
                cat_items.append(
                    SidebarItem(
                        id=cat["id"], 
                        title=cat["name"], 
                        count=cat.get("documents_count", 0), 
                        icon=None
                    )
                )
            
        self.view.update_categories(cat_items)