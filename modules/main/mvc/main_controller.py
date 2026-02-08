import logging

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QObject, pyqtSignal

from .main_view import MainView
from .main_model import MainModel
from ui.custom_widgets import SidebarItem, ROLE_ID
from modules.document_editor.document_editor_module import EditorWindow



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



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
        self.editor_window = None
        self.current_documents = []

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

            if dept_id and dept_id != self.model.current_department_id:
                self.model.current_department_id = dept_id
                self._update_categories_list()


    def _on_category_selected(self, selected, deselected) -> None:
        """Handles category selection change."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            cat_id = index.data(ROLE_ID)

            if cat_id and cat_id != self.model.current_category_id:
                self.model.current_category_id = cat_id
                self._update_documents_list()


    def _on_update_button_clicked(self) -> None:
        """Handles the update button click."""
        pass

    
    def _on_edit_button_clicked(self) -> None:
        """Handles the edit button click."""
        # If the window is already open,
        # just activate it instead of creating a new one.
        if self.editor_window and self.editor_window.isVisible():
            self.editor_window.activateWindow()
            self.editor_window.raise_()
            return
        
        # Get selected document data
        document = next((doc for doc in self.current_documents 
                         if doc.get("id") == self.model.selected_document[0]), {})

        # Get selected document pages list
        pages = self.model.get_document_pages(
            document_id=self.model.selected_document[0]
        )

        # Show document editor window
        self.editor_window = EditorWindow(
            parent=self.window,
            document_data=document,
            pages=pages
        )
        self.editor_window.document_saved.connect(self._on_document_changed)
        self.editor_window.document_deleted.connect(self._on_document_changed)
        self.editor_window.show()


    def _on_export_button_clicked(self) -> None:
        """Handles the export button click."""
        pass

    def _on_print_button_clicked(self) -> None:
        """Handles the print button click."""
        pass


    def _on_change_data_view_button_clicked(self) -> None:
        """Handles the change of data view button click."""
        pass


    def _on_back_button_clicked(self) -> None:
        """Handles the back button click."""
        pass


    def _on_document_selected(self, selected, deselected) -> None:
        """Handles document selection change."""
        indexes = selected.indexes()
        if indexes:
            current_index = indexes[0]
            row = current_index.row()
            
            if 0 <= row < len(self.current_documents):
                document = self.current_documents[row]
                self.model.selected_document = (document.get("id"), document.get("is_page"))

        # Update the document editor button state
        state=True if self.model.selected_document[0] is not None else False
        self.view.update_document_editor_state(state=state)                


    def _on_document_double_clicked(self, index) -> None:
        """Handles document double click."""
        self._on_edit_button_clicked()


    def _on_document_changed(self) -> None:
        """Handles the document change event."""
        self.model.refresh_data()
        self._update_app_data()


    # ====================
    # Controller Methods
    # ====================


    def _init_ui(self) -> None:
        """Initializes the UI with default data."""
        self._load_sidebar_data()
        self.view.set_profile_mode(self.mode)

        # Set user data
        if self.mode == "auth":
            user_data = self.model.get_user_data()

            if user_data:
                username = user_data.get("username")
                department = user_data.get("department")
                self.view.set_username(name=username if username else user_data.get("email"))
                self.view.set_user_department(dept=department if department else "Отдел не выбран")

        else:
            self.view.set_username("Гость")
            self.view.set_user_department("Войдите в аккаунт")

        # Set documents data
        self._update_documents_list()


    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""
        self.view.connect_theme_switch(self._on_theme_switcher_clicked)
        self.view.connect_logout(self._on_logout_clicked)
        self.view.connect_departments_selection(self._on_department_selected)
        self.view.connect_categories_selection(self._on_category_selected)

        # Toolbar Buttons
        self.view.connect_update_button(self._on_update_button_clicked)
        self.view.connect_edit_button(self._on_edit_button_clicked)
        self.view.connect_export_button(self._on_export_button_clicked)
        self.view.connect_print_button(self._on_print_button_clicked)
        self.view.connect_change_data_view_button(self._on_change_data_view_button_clicked)
        self.view.connect_back_button(self._on_back_button_clicked)
        self.view.connect_document_selection(self._on_document_selected)
        self.view.connect_document_double_click(self._on_document_double_clicked)


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

    def _update_documents_list(self) -> None:
        """Updates the documents list based on the current category."""
        self.model.current_document_id = None
        documents = []
        for doc in self.model.documents:
            if doc.get("category_id") == self.model.current_category_id:
                doc["is_page"] = False
                documents.append(doc)
        
        self.current_documents = documents
        self.view.update_documents_table(documents=documents)

    
    def _update_app_data(self):
        """Updates the application data."""
        # TODO Rewrite the data update so that it includes the search results
        
        # Save current selection to restore it after reload
        saved_dept_id = self.model.current_department_id
        saved_cat_id = self.model.current_category_id

        self._load_sidebar_data()
        
        # Restore department
        if saved_dept_id:
            # If the update triggered an auto-selection (e.g. first item), 
            # the model might have changed. We force it back.
            if self.model.current_department_id != saved_dept_id:
                self.model.current_department_id = saved_dept_id
                self._update_categories_list()

            self.view.select_department(saved_dept_id)

        # Restore category
        if saved_cat_id:
            self.model.current_category_id = saved_cat_id
            self.view.select_category(saved_cat_id)

        self._update_documents_list()