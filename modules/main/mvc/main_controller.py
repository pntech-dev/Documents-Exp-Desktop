import logging
import re

from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from .main_view import MainView
from .main_model import MainModel
from ui.custom_widgets import SidebarItem, ROLE_ID
from modules.document_editor.document_editor_module import EditorWindow
from utils import NotificationService



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

        # Search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(200)
        self.search_timer.timeout.connect(self._perform_search)

        # Setup Notification Service
        NotificationService().set_main_window(self.window)

        self._init_ui()
        self._setup_connections()


    # ====================
    # Controller Handlers
    # ====================


    def _on_search_lineedit_text_changed(self) -> None:
        """Handles the search line edit text change."""
        search_text = self.view.get_search_text()
        
        # If empty, update immediately without delay
        if not search_text:
            self.search_timer.stop()
            self._update_documents_list()
            return
        
        # Restart timer for debounce
        self.search_timer.start()


    def _perform_search(self) -> None:
        """Executes the search request after delay."""
        search_text = self.view.get_search_text()
        if not search_text:
            return

        search_result = self.model.search_data(query=search_text)

        # Optimization: Create a lookup map for documents to avoid O(N) search in loop
        docs_map = {doc["id"]: doc for doc in self.model.documents}

        data = []
        for result in search_result.get("result", []):
            if result.get("category_id") is not None:
                data.append(result)
            else:
                # Fast lookup
                document = docs_map.get(result.get("document_id"), {})
                
                result["code"] = document.get("code")
                result["name"] = f"{result.get('name')} ({result.get('designation')})"
                result["is_page"] = True
                
                data.append(result)
        
        # Natural sort: splits string into text and number parts for correct ordering (e.g. 2 before 10)
        data.sort(key=lambda x: [
            int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(x.get("code") or ""))
        ])

        self.current_documents = data
        self.view.update_documents_table(documents=data)


    def _on_theme_switcher_clicked(self, checked: bool) -> None:
        """Handles the theme switcher button click.

        Calls the view's `set_theme` method to toggle between light and dark
        themes for the application.
        """
        self.view.set_theme()


    def _on_create_button_clicked(self) -> None:
        """Handles the create button click."""
        # If the window is already open,
        # just activate it instead of creating a new one.
        if self.editor_window and self.editor_window.isVisible():
            self.editor_window.activateWindow()
            self.editor_window.raise_()
            return
        
        # Show document editor window
        self.editor_window = EditorWindow(
            mode=self.mode,
            parent=self.window,
            category_id=self.model.current_category_id,
            document_data={},
            pages=[]
        )
        self.editor_window.document_saved.connect(self._on_document_changed)
        self.editor_window.document_deleted.connect(self._on_document_changed)
        self.editor_window.show()


    def _on_logout_clicked(self) -> None:
        """Handles the logout action."""
        self.logout_requested.emit()


    def _on_department_selected(self, selected, deselected) -> None:
        """Handles department selection change."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            dept_id = index.data(ROLE_ID)

            if dept_id is not None and dept_id != self.model.current_department_id:
                self.model.current_department_id = dept_id
                self.model.current_category_id = None
                self._update_categories_list()
                
                if self.view.get_search_text():
                    self._on_search_lineedit_text_changed()
                else:
                    self._update_documents_list()


    def _on_category_selected(self, selected, deselected) -> None:
        """Handles category selection change."""
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            cat_id = index.data(ROLE_ID)

            if cat_id is not None and cat_id != self.model.current_category_id:
                self.model.current_category_id = cat_id
                if self.view.get_search_text():
                    self._on_search_lineedit_text_changed()
                else:
                    self._update_documents_list()
        else:
            self.model.current_category_id = None
            if self.view.get_search_text():
                self._on_search_lineedit_text_changed()
            else:
                self._update_documents_list()


    def _on_update_button_clicked(self) -> None:
        """Handles the update button click."""
        self.model.refresh_data()
        self._update_app_data()

    
    def _on_edit_button_clicked(self) -> None:
        """Handles the edit button click."""
        # If the window is already open,
        # just activate it instead of creating a new one.
        if self.editor_window and self.editor_window.isVisible():
            self.editor_window.activateWindow()
            self.editor_window.raise_()
            return
        
        selected_id, is_page = self.model.selected_document
        
        if selected_id is None:
            return

        document_id = selected_id

        if is_page:
            selected_item = next(
                (item for item in self.current_documents 
                 if item.get("id") == selected_id and item.get("is_page")), 
                None
            )
            if selected_item:
                document_id = selected_item.get("document_id")
        
        # Get selected document data
        document = next((doc for doc in self.model.documents 
                         if doc.get("id") == document_id), {})

        # Get selected document pages list
        pages = self.model.get_document_pages(
            document_id=document_id
        )

        # Show document editor window
        self.editor_window = EditorWindow(
            mode=self.mode,
            parent=self.window,
            document_data=document,
            pages=pages
        )
        self.editor_window.document_saved.connect(self._on_document_changed)
        self.editor_window.document_deleted.connect(self._on_document_changed)
        self.editor_window.show()


    def _on_export_button_clicked(self) -> None:
        """Handles the export button click event."""
        data = self.view.get_documents_list()
        department = next((dept.get("name") for dept in self.model.departments 
                           if dept.get("id") == self.model.current_department_id), {})
        category = next((cat.get("name") for cat in self.model.categories 
                         if cat.get("id") == self.model.current_category_id), {})
        
        data = {
            "department": department,
            "category": category,
            "documents": data
        }
    
        filename = f"{department} - {category}.docx"
        # Replace slashes to prevent path interpretation issues
        filename = filename.replace("/", "_").replace("\\", "_")

        file_path, _ = QFileDialog.getSaveFileName(
            self.window,
            "Экспорт в Word",
            str(Path.home() / filename),
            "Word Documents (*.docx)"
        )

        if file_path:
            path_obj = Path(file_path)
            self.model.export_to_docx(
                path=str(path_obj.parent), 
                filename=path_obj.name, 
                data=data
            )

            # Show notification
            NotificationService().show_toast(
                notification_type="success",
                title="Экспорт документа",
                message="Документ успешно экспортирован."
            )


    def _on_print_button_clicked(self) -> None:
        """Handles the print button click."""
        data = self.view.get_documents_list()
        
        department = next((dept.get("name") for dept in self.model.departments 
                           if dept.get("id") == self.model.current_department_id), "")
        category = next((cat.get("name") for cat in self.model.categories 
                         if cat.get("id") == self.model.current_category_id), "")

        # 1. Generate rows HTML
        rows_html = ""
        for doc in data:
            d_code = doc.get("code", "")
            d_name = doc.get("name", "")
            # Using Name first to match the template structure from DocumentEditor
            rows_html += f"<tr><td>{d_name}</td><td>{d_code}</td></tr>"

        # 2. Load template
        try:
            # Path to: project_root/resources/templates/print_document.html
            root_dir = Path(__file__).resolve().parents[3]
            template_path = root_dir / "resources" / "templates" / "print_document.html"
            
            with open(template_path, "r", encoding="utf-8") as f:
                html = f.read().format(code=department, name=category, rows=rows_html)
        except Exception as e:
            print(f"Error loading print template: {e}")
            return

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self.window)

        if dialog.exec_() == QPrintDialog.Accepted:
            document = QTextDocument()
            document.setHtml(html)
            document.print_(printer)

            # Show notification
            NotificationService().show_toast(
                notification_type="success",
                title="Печать списка",
                message="Список документов успешно напечатан."
            )


    def _on_change_data_view_button_clicked(self) -> None:
        """Handles the change of data view button click."""
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
        # Sidebar
        self.view.connect_logout(self._on_logout_clicked)
        self.view.connect_departments_selection(self._on_department_selected)
        self.view.connect_categories_selection(self._on_category_selected)

        # Navbar
        self.view.connect_search_lineedit(self._on_search_lineedit_text_changed)
        self.view.connect_theme_switch(self._on_theme_switcher_clicked)
        self.view.connect_create_button(self._on_create_button_clicked)

        # Toolbar Buttons
        self.view.connect_update_button(self._on_update_button_clicked)
        self.view.connect_edit_button(self._on_edit_button_clicked)
        self.view.connect_export_button(self._on_export_button_clicked)
        self.view.connect_print_button(self._on_print_button_clicked)
        self.view.connect_change_data_view_button(self._on_change_data_view_button_clicked)
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
            if self.model.current_department_id is not None and cat.get(
                "group_id"
            ) == self.model.current_department_id:
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
        
        # Natural sort: splits string into text and number parts for correct ordering (e.g. 2 before 10)
        documents.sort(key=lambda x: [
            int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(x.get("code") or ""))
        ])

        self.current_documents = documents
        self.view.update_documents_table(documents=documents)

    
    def _update_app_data(self):
        """Updates the application data."""
        # TODO Rewrite the data update so that it includes the search results
        
        # Save current selection to restore it after reload
        saved_dept_id = self.model.current_department_id
        saved_cat_id = self.model.current_category_id

        self._load_sidebar_data()
        
        # Check if saved department exists
        dept_exists = any(d["id"] == saved_dept_id for d in self.model.departments)

        if dept_exists:
            self.view.select_department(saved_dept_id)
            
            # Restore category
            cat_exists = any(c["id"] == saved_cat_id for c in self.model.categories)
            if cat_exists:
                self.view.select_category(saved_cat_id)
            
            if self.view.get_search_text():
                self._on_search_lineedit_text_changed()
            else:
                self._update_documents_list()

        elif self.model.departments:
            # Select first department
            first_dept_id = self.model.departments[0]["id"]
            self.view.select_department(first_dept_id)

            # Select first category of the new department
            first_dept_cats = [c for c in self.model.categories if c.get(
                "group_id"
            ) == first_dept_id]
            if first_dept_cats:
                self.view.select_category(first_dept_cats[0]["id"])
            
            if self.view.get_search_text():
                self._on_search_lineedit_text_changed()
            else:
                self._update_documents_list()