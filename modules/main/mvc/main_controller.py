import re
import logging
import requests

from pathlib import Path
from PyQt5.QtGui import QTextDocument
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from .main_view import MainView
from .main_model import MainModel
from core.worker import APIWorker
from ui.custom_widgets import SidebarItem, ROLE_ID
from modules.document_editor.document_editor_module import EditorWindow
from modules.departments_editings import (
    EditDepartment, CreateDepartment
)
from modules.categories_editings import (
    CreateCategory, EditCategory
)
from modules.profile.profile_dialog import ProfileDialog
from utils import NotificationService
from utils.error_messages import get_friendly_error_message



from utils.settings_manager import SettingsManager

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
            mode: str = "guest",
            settings_manager: SettingsManager | None = None
    ) -> None:
        """Initializes the MainController.

        Args:
            model: The data model.
            view: The main UI view.
            window: The main QMainWindow instance.
            mode: The application mode ('guest' or 'auth').
            settings_manager: The manager for user-specific settings.
        """
        super().__init__()
        self.model = model
        self.view = view
        self.window = window
        self.mode = mode
        self.settings_manager = settings_manager
        self.editor_window = None
        self.current_documents = []
        self.current_search_worker = None
        self.current_load_worker = None
        self.initial_load_worker = None
        self.active_workers = set()
        self.is_updating_data = False

        # Pagination state
        self.limit = 5000
        self.offset = 0
        self.is_loading = False
        self.has_more = True
        self.search_results_all: list = []  # Full search results for client-side pagination

        # Chunk loading for large lists to prevent UI freezing.
        self.pending_documents_to_add = []

        # Search debounce timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(200)
        self.search_timer.timeout.connect(self._perform_search)

        # Setup Notification Service
        NotificationService().set_main_window(self.window)

        self._setup_connections()
        self._init_ui()


    # ====================
    # Controller Handlers
    # ====================


    def _on_search_lineedit_text_changed(self) -> None:
        """Handles the search line edit text change."""
        search_text = self.view.get_search_text()
        
        # If empty, update immediately without delay
        if not search_text:
            self.search_timer.stop()
            # Invalidate any in-flight search worker so that if it finishes
            # after _update_documents_list it won't overwrite the table.
            self.current_search_worker = None
            self.search_results_all = []
            self._update_documents_list()
            return
        
        # Restart timer for debounce
        self.search_timer.start()


    def _on_search_filters_changed(self, checked: bool) -> None:
        """Handles search filter changes and saves them."""
        filters = self.view.get_search_filters()
        if self.settings_manager:
            self.settings_manager.set_setting("search_filters", filters)

        if self.view.get_search_text():
            self._on_search_lineedit_text_changed()


    def _perform_search(self) -> None:
        """Executes the search request after delay."""
        search_text = self.view.get_search_text()
        filters = self.view.get_search_filters()
        if not search_text:
            return

        # Use APIWorker to prevent UI freezing during search
        # Pass a copy of current_documents to be thread-safe
        worker = APIWorker(
            self._search_data_task, 
            query=search_text, 
            filters=filters,
            current_docs=list(self.current_documents)
        )
        
        self.current_search_worker = worker
        self.active_workers.add(worker)
        
        worker.finished.connect(self._on_search_finished)
        worker.error.connect(self._on_search_error)
        worker.finished.connect(self._cleanup_worker)
        worker.error.connect(self._cleanup_worker)
        worker.start()


    def _on_theme_switcher_clicked(self, checked: bool) -> None:
        """Handles the theme switcher button click.

        Calls the view's `set_theme` method to toggle between light and dark
        themes for the application.
        """
        self.view.set_theme()

    
    def _on_craete_department_clicked(self) -> None:
        """"Handles the create department action button click."""
        try:
            # Show create department window (returns tuple)
            result = CreateDepartment.get_data(parent=self.window)

            if not result:
                return
            
            department_name, show_for_guest, has_all_docs = result
            data = self.model.create_department(
                name=department_name, 
                show_for_guest=show_for_guest, 
                has_all_docs_search=has_all_docs
            )
            new_id = data.get("id")

            if new_id:
                # Refresh data to include the new department
                self.model.refresh_data()

                # Set new department as current department
                self.model.current_department_id = new_id
                self.model.current_category_id = None

                logger.info(f"Created department: {department_name}")
                NotificationService().show_toast(
                    notification_type="success",
                    title="Создание отдела",
                    message=f"Отдел: {data['name']} успешно создан."
                )

                # Update UI
                self._load_sidebar_data()
                
                # Select the new department in the sidebar
                QTimer.singleShot(50, lambda: self.view.select_department(new_id))
                self._update_documents_list()
                self._update_create_category_state()
                self._update_create_document_state()

        except Exception as e:
            self._handle_error(e, "Создание отдела")

    
    def _on_craete_category_clicked(self) -> None:
        """"Handles the create category action button click."""
        try:
            # Show create category window (returns tuple)
            result = CreateCategory.get_data(parent=self.window)

            if not result:
                return

            category_name, show_for_guest = result
            data = self.model.create_category(name=category_name, show_for_guest=show_for_guest)
            new_id = data.get("id")

            if new_id:
                # Refresh data to include the new category
                self.model.refresh_data()

                # Set new category as current category
                self.model.current_category_id = new_id

                logger.info(f"Created category: {category_name}")
                NotificationService().show_toast(
                    notification_type="success",
                    title="Создание категории",
                    message=f"Категория: {data['name']} успешно создана."
                )

                # Update UI and restore selection
                self._update_app_data()

        except Exception as e:
            self._handle_error(e, "Создание категории")


    def _on_edit_department_clicked(self, dept_id: str) -> None:
        """Handles the edit department button click."""
        department = next((dept for dept in self.model.departments 
                           if str(dept.get("id")) == str(dept_id)), None)
        
        if department:
            try:
                current_name = department.get("name", "")
                current_has_all_docs = department.get("has_all_docs_search", False)
                action, result = EditDepartment.show_dialog(
                    parent=self.window, 
                    current_name=current_name, 
                    current_show_for_guest=department.get("show_for_guest", False),
                    current_has_all_docs=current_has_all_docs
                )
                
                if action == "edit":
                    if result:
                        new_name, show_for_guest, new_has_all_docs = result
                        self.model.edit_department(
                            name=new_name, 
                            department_id=int(dept_id), 
                            show_for_guest=show_for_guest,
                            has_all_docs_search=new_has_all_docs
                        )
                        self.model.refresh_data()

                        logger.info(f"Department updated: {new_name}")
                        NotificationService().show_toast(
                            notification_type="success",
                            title="Изменение отдела",
                            message=f"Отдел: {new_name} успешно изменен."
                        )
                        self._update_app_data()
                
                elif action == "delete":
                    self.model.delete_department(department_id=int(dept_id))
                    self.model.refresh_data()

                    # If the deleted department was the current one, reset selection
                    if str(self.model.current_department_id) == str(dept_id):
                        if self.model.departments:
                            self.model.current_department_id = self.model.departments[0]["id"]
                        else:
                            self.model.current_department_id = None

                        self.model.current_category_id = None
                        self._update_documents_list()

                    logger.info(f"Department deleted: {current_name}")
                    NotificationService().show_toast(
                        notification_type="success",
                        title="Изменение отдела",
                        message=f"Отдел: {current_name} успешно удален."
                    )
                    self._update_app_data()
            except Exception as e:
                self._handle_error(e, "Изменение отдела")


    def _on_edit_category_clicked(self, cat_id: str) -> None:
        """Handles the edit category button click."""
        category = next((cat for cat in self.model.categories 
                         if str(cat.get("id")) == str(cat_id)), None)
        
        if category:
            try:
                current_name = category.get("name", "")
                action, result = EditCategory.show_dialog(
                    parent=self.window, 
                    current_name=current_name,
                    current_show_for_guest=category.get("show_for_guest", False)
                )
                
                if action == "edit":
                    if result:
                        new_name, show_for_guest = result
                        self.model.edit_category(
                            name=new_name, 
                            category_id=int(cat_id),
                            show_for_guest=show_for_guest
                        )
                        self.model.refresh_data()

                        logger.info(f"Category updated: {new_name}")
                        NotificationService().show_toast(
                            notification_type="success",
                            title="Изменение категории",
                            message=f"Категория: {new_name} успешно изменена."
                        )
                        self._update_app_data()
                
                elif action == "delete":
                    self.model.delete_category(category_id=int(cat_id))
                    self.model.refresh_data()

                    # If the deleted category was the current one, reset selection
                    if str(self.model.current_category_id) == str(cat_id):
                        self.model.current_category_id = None
                        self._update_documents_list()

                    logger.info(f"Category deleted: {current_name}")
                    NotificationService().show_toast(
                        notification_type="success",
                        title="Изменение категории",
                        message=f"Категория: {current_name} успешно удалена."
                    )
                    self._update_app_data()
            except Exception as e:
                self._handle_error(e, "Изменение категории")


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


    def _show_profile_dialog(self) -> None:
        """Handles showing the user profile dialog."""
        if self.mode != "auth":
            return

        try:
            user_data = self.model.get_full_user_data()
            if not user_data:
                logger.warning("Could not retrieve user data for profile.")
                return

            departments = self.model.departments
            
            updated_data = ProfileDialog.show_dialog(
                parent=self.window,
                user_data=user_data,
                departments=departments
            )

            if updated_data:
                worker = APIWorker(
                    self.model.update_user_profile,
                    user_id=user_data['id'],
                    data=updated_data
                )
                self.active_workers.add(worker)
                worker.finished.connect(self._on_profile_update_finished)
                worker.error.connect(lambda e: self._handle_error(e, "Ошибка обновления профиля"))
                worker.finished.connect(self._cleanup_worker)
                worker.error.connect(self._cleanup_worker)
                worker.start()

        except Exception as e:
            self._handle_error(e, "Ошибка профиля")


    def _on_profile_update_finished(self, new_data: dict):
        """Handles successful profile update."""
        logger.info(f"User profile updated successfully for user ID: {new_data.get('id')}")
        
        # Refresh all data to ensure consistency
        self.model.refresh_data()
        
        # Update the UI with new user data
        self._init_ui()

        NotificationService().show_toast(
            notification_type="success",
            title="Профиль обновлен",
            message="Ваши данные были успешно сохранены."
        )


    def _on_department_selected(self, selected, deselected) -> None:
        """Handles department selection change."""
        if self.is_updating_data:
            return

        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            dept_id = index.data(ROLE_ID)

            if dept_id is not None and dept_id != self.model.current_department_id:
                self.model.current_department_id = dept_id
                self.model.current_category_id = None
                
                # Explicitly clear documents to avoid showing stale data from previous department
                self._update_documents_list()                
                self._update_categories_list()
                
                if self.view.get_search_text():
                    self._on_search_lineedit_text_changed()

                self._update_create_category_state()
                self._update_create_document_state()


    def _on_category_selected(self, selected, deselected) -> None:
        """Handles category selection change."""
        if self.is_updating_data:
            return

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

        self._update_create_category_state()
        self._update_create_document_state()


    def _on_update_button_clicked(self) -> None:
        """Handles the update button click."""
        try:
            self.model.refresh_data()
            self._update_app_data()
            self._update_documents_list() # Reload list
            NotificationService().show_toast(
                notification_type="success",
                title="Обновлено",
                message="Данные успешно обновлены."
            )
        except Exception as e:
            self._handle_error(e, "Ошибка обновления")

    
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
        document = {}
        if document_id:
            try:
                document = self.model.get_document(document_id)
            except Exception as e:
                logger.error(f"Error fetching document details: {e}")

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
            try:
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
            except Exception as e:
                self._handle_error(e, "Ошибка экспорта")


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
            logging.error(f"Error loading print template: {e}", exc_info=True)
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
        else:
            self.model.selected_document = (None, False)

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

    
    def _on_table_scroll(self, value: int) -> None:
        """Handles table scroll to load more data."""
        if len(self.current_documents) == 0:
            return

        scrollbar = self.view.ui.tableView.verticalScrollBar()
        at_bottom = value >= scrollbar.maximum() - 20

        if not at_bottom:
            return

        if self.view.get_search_text():
            # Search results are held fully in memory — paginate client-side
            self._load_more_search_results()
        elif not self.is_loading and self.has_more:
            self._load_more_documents()

    def _load_more_search_results(self) -> None:
        """Appends the next batch of search results from the in-memory cache."""
        already_shown = len(self.current_documents)
        remaining = self.search_results_all[already_shown:]
        if not remaining:
            return
        batch = remaining[:100]
        self.current_documents.extend(batch)
        self.view.append_documents_table(batch)

    
    def _search_data_task(
            self, 
            query: str, 
            filters: dict, 
            current_docs: list
    ) -> list:
        """Background task logic for searching."""
        # Extract tags from query (e.g. "@tag")
        tags = re.findall(r'@([^\s]+)', query)
        # Remove tags from query to get clean text
        clean_query = re.sub(r'@[^\s]+', '', query).strip()

        cat_id = self.model.current_category_id
        group_id = None
        if isinstance(cat_id, str) and cat_id.startswith("virtual_"):
            group_id = int(cat_id.split("_")[1])
            cat_id = None

        search_result = self.model.search_data(
            query=clean_query, 
            tags=tags, 
            category_id=cat_id, 
            group_id=group_id, 
            filters=filters
        )

        # Handle API response (list or dict)
        results_list = search_result if isinstance(
            search_result, list
        ) else search_result.get("result", [])

        # API now returns document_code directly in each page result —
        # no need to fetch parent documents separately.
        data = []
        for result in results_list:
            if result.get("category_id") is not None:
                # Regular document
                data.append(result)
            else:
                # Page — API provides document_code directly
                result["code"] = result.get("document_code") or ""
                name = result.get("name") or ""
                designation = result.get("designation") or ""
                result["name"] = f"{name} ({designation})"
                result["is_page"] = True
                data.append(result)

        data.sort(key=self._get_natural_sort_key)
        return data


    def _on_search_finished(self, data: list) -> None:
        """Handles successful search completion."""
        # Ignore results from stale workers (if a new search started)
        if self.sender() != self.current_search_worker:
            return

        # If the user cleared the search field while the worker was running,
        # discard the result — _update_documents_list already took over.
        search_text = self.view.get_search_text()
        if not search_text:
            return

        tags = re.findall(r'@([^\s]+)', search_text)
        self.view.set_active_search_tags(tags)

        total_count = len(data)

        # Store full results for client-side pagination on scroll
        self.search_results_all = data

        # Render only the first batch to keep the UI responsive,
        # using the same chunked approach as _on_load_more_finished
        # to avoid UI freezing and visual flicker.
        first_batch = data[:100]
        self.current_documents = list(first_batch)
        self.view.clear_documents_table()
        self.pending_documents_to_add = list(first_batch)
        QTimer.singleShot(0, self._add_document_chunk)
        self.view.set_finded_counter(total_count)
        self._add_popular_tags()
        self.view.set_export_print_enabled(total_count > 0)


    def _on_search_error(self, error: Exception) -> None:
        """Handles search errors."""
        if self.sender() != self.current_search_worker:
            return
        self.current_search_worker = None
        self._handle_error(error, "Ошибка поиска")

    def _cleanup_worker(self) -> None:
        """Removes the worker from the active set."""
        worker = self.sender()
        if worker in self.active_workers:
            self.active_workers.discard(worker)


    # ====================
    # Controller Methods
    # ====================


    def _init_ui(self) -> None:
        """Initializes the UI with default data."""
        self.view.set_profile_mode(self.mode)

        # Load and apply settings
        if self.settings_manager:
            search_filters = self.settings_manager.get_setting("search_filters")
            if search_filters:
                self.view.set_search_filters(search_filters)
        self._load_initial_data()

    def _load_initial_data(self) -> None:
        """Loads the initial sidebar and profile data without blocking the UI thread."""
        worker = APIWorker(self.model.load_initial_data)
        self.initial_load_worker = worker
        self.active_workers.add(worker)
        worker.finished.connect(self._on_initial_data_loaded)
        worker.error.connect(self._on_initial_data_error)
        worker.finished.connect(self._cleanup_worker)
        worker.error.connect(self._cleanup_worker)
        worker.start()

    def _on_initial_data_loaded(self, data: dict) -> None:
        if self.sender() != self.initial_load_worker:
            return

        self.initial_load_worker = None
        self.model.departments = data.get("departments", [])
        self.model.categories = data.get("categories", [])
        self.model.current_department_id = self.model.departments[0]["id"] if self.model.departments else None
        self._load_sidebar_data()

        if self.mode == "auth":
            self._apply_user_data(data.get("user_data"))
        else:
            self.view.set_username("Гость")
            self.view.set_user_department("Войдите в аккаунт")
            if self.model.departments:
                first_dept_id = self.model.departments[0].get("id")
                if first_dept_id:
                    QTimer.singleShot(50, lambda: self.view.select_department(first_dept_id))

        self._update_create_category_state()
        self._update_create_document_state()

    def _on_initial_data_error(self, error: Exception) -> None:
        if self.sender() != self.initial_load_worker:
            return

        self.initial_load_worker = None
        if self.mode == "auth":
            self.view.set_username("Пользователь")
            self.view.set_user_department("Не удалось загрузить данные")
        else:
            self.view.set_username("Гость")
            self.view.set_user_department("Войдите в аккаунт")
        self._handle_error(error, "Ошибка загрузки данных")

    def _apply_user_data(self, user_data: dict | None) -> None:
        """Applies the loaded user data to the UI and restores sidebar selection."""
        if not user_data:
            return

        username = user_data.get("username")
        department_name = user_data.get("department")
        self.view.set_username(name=username if username else user_data.get("email"))
        self.view.set_user_department(dept=department_name if department_name else "Отдел не выбран")

        user_dept_id = None
        if department_name:
            for dept in self.model.departments:
                if dept.get("name") == department_name:
                    user_dept_id = dept.get("id")
                    break

        if user_dept_id:
            QTimer.singleShot(50, lambda: self.view.select_department(user_dept_id))
        elif self.model.departments:
            first_dept_id = self.model.departments[0].get("id")
            if first_dept_id:
                QTimer.singleShot(50, lambda: self.view.select_department(first_dept_id))


    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""      
        # Sidebar
        self.view.connect_logout(self._on_logout_clicked)
        self.view.connect_profile_action(self._show_profile_dialog)
        self.view.connect_departments_selection(self._on_department_selected)
        self.view.connect_categories_selection(self._on_category_selected)
        self.view.connect_department_edit(self._on_edit_department_clicked)
        self.view.connect_category_edit(self._on_edit_category_clicked)

        # Navbar
        self.view.connect_search_lineedit(self._on_search_lineedit_text_changed)
        self.view.connect_search_filters_changed(self._on_search_filters_changed)
        self.view.connect_theme_switch(self._on_theme_switcher_clicked)
        self.view.connect_create_button(self._on_create_button_clicked)
        self.view.connect_create_department(self._on_craete_department_clicked)
        self.view.connect_create_category(self._on_craete_category_clicked)
        self.view.connect_filter_tag_toggled(self._on_filter_tag_toggled)

        # Toolbar Buttons
        self.view.connect_update_button(self._on_update_button_clicked)
        self.view.connect_edit_button(self._on_edit_button_clicked)
        self.view.connect_export_button(self._on_export_button_clicked)
        self.view.connect_print_button(self._on_print_button_clicked)
        self.view.connect_change_data_view_button(self._on_change_data_view_button_clicked)
        self.view.connect_document_selection(self._on_document_selected)
        self.view.connect_document_double_click(self._on_document_double_clicked)
        self.view.connect_documents_scroll(self._on_table_scroll)

    def _on_filter_tag_toggled(self, checked: bool, text: str) -> None:
        """Handles filter tag toggle event."""
        tag_query = f"@{text}"
        current_text = self.view.get_search_text()
        parts = current_text.split()
        
        # Case-insensitive handling
        parts_lower = [p.lower() for p in parts]
        tag_query_lower = tag_query.lower()

        if checked:
            if tag_query_lower not in parts_lower:
                parts.append(tag_query)
        else:
            # Remove all occurrences (case-insensitive)
            parts = [p for p in parts if p.lower() != tag_query_lower]
        
        self.view.set_search_text(" ".join(parts))


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
        
        # Check for virtual category "All Documents"
        current_dept = next((d for d in self.model.departments 
                             if str(d["id"]) == str(self.model.current_department_id)), None)
        if current_dept and current_dept.get("has_all_docs_search"):
            cat_items.append(SidebarItem(
                id=f"virtual_{current_dept['id']}",
                title="Все документы",
                count=current_dept.get("documents_count", 0),
                icon=None,
                editable=False
            ))

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

        if self.model.current_category_id is None:
            self.offset = 0
            self.has_more = False
            self.current_documents = []
            self.search_results_all = []
            self.pending_documents_to_add = []
            self.view.clear_documents_table()
            self.view.set_finded_counter(0)
            self.view.set_active_search_tags([])
            self.view.set_export_print_enabled(False)
            return

        self.offset = 0
        self.has_more = True

        self.is_loading = False
        self.current_load_worker = None
        self.pending_documents_to_add = []

        self._load_more_documents()


    def _load_more_documents(self) -> None:
        """Loads the next page of documents."""
        # Do not load more if loading, no category selected, or SEARCH IS ACTIVE
        if self.is_loading or self.model.current_category_id is None or self.view.get_search_text():
            return

        self.is_loading = True
        
        try:
            cat_id = self.model.current_category_id
            group_id = None
            
            if isinstance(cat_id, str) and cat_id.startswith("virtual_"):
                group_id = int(cat_id.split("_")[1])
                cat_id = None

            worker = APIWorker(
                self.model.fetch_documents,
                category_id=cat_id, 
                group_id=group_id, 
                limit=self.limit, 
                offset=self.offset
            )
            
            self.current_load_worker = worker
            self.active_workers.add(worker)
            worker.finished.connect(self._on_load_more_finished)
            worker.error.connect(self._on_load_more_error)
            worker.finished.connect(self._cleanup_worker)
            worker.error.connect(self._cleanup_worker)
            worker.start()
        except Exception as e:
            self.is_loading = False
            logger.error(f"Failed to start load worker: {e}", exc_info=True)
            self._handle_error(e, "Ошибка загрузки")
    
    def _on_load_more_finished(self, docs: list) -> None:
        if self.sender() != self.current_load_worker:
            return

        self.is_loading = False
        self.current_load_worker = None
        self.search_results_all = []

        # Prevent updating UI if search is active (stale request)
        if self.view.get_search_text():
            return

        # With a large limit, we assume we've fetched all documents.
        # This allows for correct client-side natural sorting.
        self.has_more = False

        # We are replacing the list, not extending it.
        self.current_documents = docs
        self.current_documents.sort(key=self._get_natural_sort_key)

        # Instead of one large, blocking update, we add the data in chunks
        # to keep the UI responsive.
        self.view.clear_documents_table()
        self.view.set_active_search_tags([])
        self.pending_documents_to_add = list(self.current_documents)
        # Start the chunked update. Use a single shot timer to yield to the event loop.
        QTimer.singleShot(0, self._add_document_chunk)

        self.view.set_finded_counter(len(self.current_documents))
        self._add_popular_tags()
        self.view.set_export_print_enabled(len(self.current_documents) > 0)

    def _add_document_chunk(self):
        """Adds a chunk of documents to the table view to avoid freezing the UI."""
        if not self.pending_documents_to_add:
            return
            
        chunk_size = 100
        chunk = self.pending_documents_to_add[:chunk_size]
        self.pending_documents_to_add = self.pending_documents_to_add[chunk_size:]
        
        self.view.append_documents_table(chunk)
        
        # If there are more documents, schedule the next chunk
        if self.pending_documents_to_add:
            # Use a single shot timer with 0ms timeout to yield to the event loop,
            # allowing the UI to repaint before adding the next chunk.
            QTimer.singleShot(0, self._add_document_chunk)

    def _on_load_more_error(self, error: Exception) -> None:
        if self.sender() != self.current_load_worker:
            return

        self.is_loading = False
        self.current_load_worker = None
        self._handle_error(error, "Ошибка загрузки документов")

    
    def _update_app_data(self):
        """Updates the application data."""
        self.is_updating_data = True
        
        try:
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
                
                if not cat_exists and isinstance(
                    saved_cat_id, str
                ) and saved_cat_id.startswith("virtual_"):
                    cat_exists = True

                if cat_exists:
                    self.view.select_category(saved_cat_id)
                else:
                    # If category was deleted or not selected, select the first one if available
                    # to match SidebarBlock behavior (which selects first item on reset)
                    dept_cats = [c for c in self.model.categories 
                                 if c.get("group_id") == saved_dept_id]
                    if dept_cats:
                        self.model.current_category_id = dept_cats[0]["id"]
                        self.view.select_category(self.model.current_category_id)
                    else:
                        self.model.current_category_id = None
        finally:
            self.is_updating_data = False

        # Trigger update manually after state is restored
        if dept_exists:
            if self.view.get_search_text():
                # Perform search immediately, bypassing debounce timer
                self._perform_search()
            else:
                self._update_documents_list()

        self._update_create_category_state()
        self._update_create_document_state()


    def _get_natural_sort_key(self, doc: dict) -> list:
        """
        Generates a sort key for natural (human-friendly) sorting.

        Correctly handles codes like '03/1КД', '01КД-03КД', '05КД' by
        splitting on both digits and non-digit characters (including
        separators such as '/', '-', '.') so that numeric segments are
        compared numerically and text segments lexicographically.

        Args:
            doc (dict): The document dictionary.

        Returns:
            list: A list of tuples representing the sort key.
        """
        code = str(doc.get("code") or "").strip()

        # Empty codes are sorted to the end
        if not code:
            return [(1, 0, "")]

        parts = []
        for part in re.findall(r'\d+|[^\d]+', code):
            if part.isdigit():
                # (type=0 → numbers first, numeric value, empty string as tiebreaker)
                parts.append((0, int(part), ""))
            else:
                # (type=1 → strings after numbers, 0 as tiebreaker, lowercased value)
                parts.append((1, 0, part.lower()))

        # Prepend marker so non-empty codes sort before empty ones
        return [(0, 0, "")] + parts
    
    def _add_popular_tags(self) -> None:
        """Calculates and updates tag statistics for current documents."""
        tags_count = {}
        for doc in self.current_documents:
            for tag in doc.get("tags", []):
                tag_name = tag.get("name")
                if tag_name:
                    tags_count[tag_name] = tags_count.get(tag_name, 0) + 1
        
        # Sort by count desc and take top 7
        sorted_tags = sorted(tags_count.items(), key=lambda item: item[1], reverse=True)
        top_tags = [tag[0] for tag in sorted_tags[:7]]
        
        self.view.set_popular_tags(top_tags)


    def _update_create_category_state(self) -> None:
        """Updates the state of the create category button."""
        state = self.model.current_department_id is not None
        self.view.set_category_creation_enabled(state)


    def _update_create_document_state(self) -> None:
        """Updates the state of the create document button."""
        # Disable creation if virtual category is selected
        cat_id = self.model.current_category_id
        state = cat_id is not None and not (isinstance(cat_id, str) and cat_id.startswith("virtual_"))
        self.view.set_document_creation_enabled(state)


    def _handle_error(self, e: Exception, title: str = "Ошибка") -> None:
        """Handles exceptions, checking for auth errors."""
        if isinstance(e, requests.exceptions.HTTPError) and e.response is not None and e.response.status_code == 401:
            logger.warning(f"Session expired (401) during {title}. Logging out.")
            self.logout_requested.emit()
            NotificationService().show_toast(
                notification_type="warning",
                title="Сессия истекла",
                message="Срок действия сессии истек. Пожалуйста, войдите снова."
            )
        else:
            logger.error(f"{title}: {e}")
            msg = get_friendly_error_message(e)
            NotificationService().show_toast(
                notification_type="error",
                title=title,
                message=msg
            )
