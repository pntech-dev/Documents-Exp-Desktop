import re
import logging
from pathlib import Path
from PyQt5.QtGui import QTextDocument
from PyQt5.QtWidgets import QFileDialog, QDialog, QMessageBox
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from utils import NotificationService
from utils.error_messages import get_friendly_error_message
from utils.delete_info_modal import DeleteInfoDialog



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class DocumentEditorController:
    """
    Controller for the document editor window.

    Manages the logic for creating, editing, and saving documents and their pages.
    """
    def __init__(
            self, 
            mode,
            model, 
            view, 
            window,
    ): 
        self.mode = mode
        self.model = model
        self.view = view
        self.window = window

        # Setup Notification Service
        NotificationService().set_main_window(self.window)

        # Initialize UI
        self._init_ui()
        self._setup_connections()


    # ====================
    # Handlers
    # ====================


    def _on_document_data_changed(self, *args):
        """Handles changes in document data to update UI state."""
        self.model.is_document_edited = True
        self._update_generate_button_state()
        self._update_save_document_button_state()


    def _on_table_selection_changed(self, *args) -> None:
        """Updates the delete page button state."""
        state = self.view.has_selected_pages()
        self.view.update_duplicate_button_state(state=state)
        self.view.update_delete_page_button_state(state=state)


    def _generate_tags(self) -> None:
        """Handles the generate tags button click event."""
        document_data = self.view.get_document_data()

        # Get tags from document name
        document_tags = {}
        document_name_tags = re.sub(r"[^\w\s]", "", document_data.get("name", "")).split()
        
        for tag in document_name_tags:
            if len(tag) < 4: continue
            tag_lower = tag.lower()
            document_tags[tag_lower] = document_tags.get(tag_lower, 0) + 1

        # Get tags from document pages
        pages_tags = {}
        for page in document_data.get("pages", []):
            page_tags = re.sub(r"[^\w\s]", "", page.get("name")).split()

            for tag in page_tags:
                if len(tag) < 4: continue
                tag_lower = tag.lower()
                pages_tags[tag_lower] = pages_tags.get(tag_lower, 0) + 1

        # Return if not tags from document name and pages
        if not document_tags and not pages_tags:
            return
        
        # Helper to get sorted tags
        def get_sorted_tags(tags_dict):
            sorted_items = sorted(tags_dict.items(), key=lambda item: item[1], reverse=True)
            return [tag.capitalize() for tag, count in sorted_items]

        name_candidates = get_sorted_tags(document_tags)
        page_candidates = get_sorted_tags(pages_tags)

        # Priority list construction:
        # 1. Top 2 from Name
        # 2. Top 3 from Pages
        # 3. Rest from Name
        # 4. Rest from Pages
        priority_list = name_candidates[:2] + page_candidates[:3] + name_candidates[2:] + page_candidates[3:]
        
        # Filter duplicates and take top 5
        tags = list(dict.fromkeys(priority_list))[:5]
        
        if tags:
            self.view.set_document_tags(tags=tags)
        

    def _on_add_page_button_clicked(self) -> None:
        """Handles the add page button click event."""
        self.view.add_new_page()
        self._on_document_data_changed()


    def _on_duplicate_page_button_clicked(self) -> None:
        """Handles the duplicate page button click event."""
        self.view.duplicate_selected_pages()
        self._on_document_data_changed()


    def _on_print_button_clicked(self) -> None:
        """Handles the print button click event."""
        data = self.view.get_document_data()
        
        code = data.get("code", "")
        name = data.get("name", "")
        pages = data.get("pages", [])

        # 1. Generate rows HTML
        rows_html = ""
        for page in pages:
            p_name = page.get("name", "")
            p_designation = page.get("designation", "")
            rows_html += f"<tr><td>{p_name}</td><td>{p_designation}</td></tr>"

        # 2. Load template
        try:
            # Path to: project_root/resources/templates/print_document.html
            root_dir = Path(__file__).resolve().parents[3]
            template_path = root_dir / "resources" / "templates" / "print_document.html"
            
            with open(template_path, "r", encoding="utf-8") as f:
                html = f.read().format(code=code, name=name, rows=rows_html)
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
                title="Печать документа",
                message="Документ успешно напечатан."
            )


    def _on_import_button_clicked(self) -> None:
        """Handles the import button click event."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
            "Импорт из Word",
            str(Path.home()),
            "Word Documents (*.docx)"
        )

        if file_path:
            try:
                imported_pages = self.model.import_from_docx(file_path)
                
                if imported_pages:
                    current_data = self.view.get_document_data()
                    current_pages = current_data.get("pages", [])
                    combined_pages = current_pages + imported_pages
                    
                    self.view.pages_table.update_pages(pages=combined_pages)
                    self._on_document_data_changed()

                    # Show notification
                    NotificationService().show_toast(
                        notification_type="success",
                        title="Импорт страниц документа",
                        message="Страницы документа успешно импортированы."
                    )
                else:
                    NotificationService().show_toast(
                        notification_type="error",
                        title="Импорт страниц документа",
                        message="Не удалось найти подходящую таблицу для импорта."
                    )
            except Exception as e:
                msg = get_friendly_error_message(e)
                NotificationService().show_toast("error", "Ошибка импорта", msg)


    def _on_export_button_clicked(self) -> None:
        """Handles the export button click event."""
        data = self.view.get_document_data()
        filename = f"{data.get('code')} - {data.get('name')}.docx"
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
                msg = get_friendly_error_message(e)
                NotificationService().show_toast("error", "Ошибка экспорта", msg)


    def _on_delete_page_button_clicked(self) -> None:
        """Handles the delete page button click event."""
        self.view.delete_selected_pages()
        self._on_document_data_changed()
        self._on_table_selection_changed()


    def _on_files_dropped(self, files: list) -> None:
        """Handles the files dropped event."""
        blocked_extensions = {
            "exe", "dll", "bat", "cmd", "sh", "js", "vbs", "scr", 
            "com", "pif", "jar", "app", "php", "pl", "py", "rb", 
            "asp", "aspx", "jsp", "cgi", "ps1", "reg", "msi", "wsf",
            "hta", "cpl", "msc", "lnk", "inf"
        }
        
        blocked_files = []
        valid_files = []

        for file_path in files:
            ext = Path(file_path).suffix.lower().lstrip('.')
            if ext in blocked_extensions:
                blocked_files.append(Path(file_path).name)
            else:
                valid_files.append(file_path)
        
        if blocked_files:
            msg = "Файлы с таким расширением нельзя загрузить:\n" + "\n".join(blocked_files[:5])
            if len(blocked_files) > 5:
                msg += f"\n...и еще {len(blocked_files) - 5}"
            NotificationService().show_toast("error", "Ошибка загрузки", msg)

        for file_path in valid_files:
            self.model.add_pending_file(file_path)
            self.view.add_file_widget(file_path)
        
        if valid_files:
            self._on_document_data_changed()


    def _on_drag_drop_area_clicked(self) -> None:
        """Handles the drag and drop area click event."""
        files, _ = QFileDialog.getOpenFileNames(
            self.window,
            "Выберите файлы",
            str(Path.home()),
            "All Files (*)"
        )
        if files:
            self._on_files_dropped(files)

    def _on_file_widget_deleted(self, file_identifier: object) -> None:
        """Handles the deletion of a file."""
        if isinstance(file_identifier, int):
             # Existing file (ID)
            try:
                self.model.delete_file(file_identifier)
                self.view.remove_file_widget(file_identifier)
                NotificationService().show_toast("success", "Файл удален", "Файл успешно удален.")
            except Exception as e:
                msg = get_friendly_error_message(e)
                NotificationService().show_toast("error", "Ошибка удаления файла", msg)
        else:
            # Pending file (path string)
            self.model.remove_pending_file(file_identifier)
            self.view.remove_file_widget(file_identifier)

    def _on_delete_document_button_clicked(self) -> None:
        """Handles the delete document button click event."""
        dialog = DeleteInfoDialog(parent=self.window, info_type="document")
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                doc_name = self.model.document_data.get("name", "")
                doc_code = self.model.document_data.get("code", "")

                self.model.delete_document()
                logger.info(f"Document deleted: {doc_name} ({doc_code})")
                self.window.document_deleted.emit()
                
                if self.window.parent():
                    NotificationService().set_main_window(self.window.parent())

                self.window.close()
                
                # Show notification
                NotificationService().show_toast(
                    notification_type="success",
                    title="Удаление документа",
                    message="Документ успешно удален."
                )
            except Exception as e:
                msg = get_friendly_error_message(e)
                NotificationService().show_toast("error", "Ошибка удаления", msg)

    
    def _on_save_button_clicked(self) -> None:
        """Handles the save button click event."""
        try:
            data = self.view.get_document_data()
            is_creation = self.model.document_data.get("id") is None

            self.model.save_document(data=data)
            
            # Upload pending files
            if self.model.pending_files:
                self.model.upload_pending_files()
            
            doc_name = data.get("name", "")
            doc_code = data.get("code", "")
            if is_creation:
                logger.info(f"Document created: {doc_name} ({doc_code})")
            else:
                logger.info(f"Document updated: {doc_name} ({doc_code})")

            self.window.document_saved.emit()
            
            if self.window.parent():
                NotificationService().set_main_window(self.window.parent())

            self.window.close()
            
            if is_creation:
                NotificationService().show_toast(
                    notification_type="success",
                    title="Создано",
                    message="Документ успешно создан."
                )
            else:
                NotificationService().show_toast(
                    notification_type="success",
                    title="Сохранено",
                    message="Документ успешно сохранен."
                )
        except Exception as e:
            msg = get_friendly_error_message(e)
            NotificationService().show_toast("error", "Ошибка сохранения", msg)


    def _on_cancel_button_clicked(self) -> None:
        """Handles the cancel button click event."""
        self.window.close()


    # ====================
    # Controller Methods
    # ====================


    def _init_ui(self) -> None:
        """Initializes the UI with default data."""
        can_edit = True if self.mode == "auth" else False
        is_creation = self.model.document_data.get("id") is None
        self.view.set_mode_visibility(can_edit=can_edit, is_creation=is_creation)

        self._fill_document_tags()
        self._fill_document_data()
        self._fill_pages_table()
        self._fill_files_list()


    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""
        # Lineedits
        self.view.code_lineedit_text_changed(handler=self._on_document_data_changed)
        self.view.name_lineedit_text_changed(handler=self._on_document_data_changed)
        self.view.tags_lineedit_text_changed(handler=self._on_document_data_changed)
        self.view.generate_tags_button_clicked(handler=self._generate_tags)

        # Toolbar
        self.view.toolbar_add_page_button_clicked(handler=self._on_add_page_button_clicked)
        self.view.toolbar_duplicate_page_button_clicked(handler=self._on_duplicate_page_button_clicked)
        self.view.toolbar_print_button_clicked(handler=self._on_print_button_clicked)
        self.view.toolbar_import_button_clicked(handler=self._on_import_button_clicked)
        self.view.toolbar_export_button_clicked(handler=self._on_export_button_clicked)
        self.view.toolbar_delete_page_button_clicked(handler=self._on_delete_page_button_clicked)

        # Pages table
        self.view.pages_table_item_changed(handler=self._on_document_data_changed)
        self.view.pages_table_row_moved(handler=self._on_document_data_changed)
        self.view.pages_table_selection_changed(handler=self._on_table_selection_changed)
        self.view.pages_table_item_changed(handler=self._on_table_selection_changed)

        # Files
        self.view.file_drop_widget_files_dropped(handler=self._on_files_dropped)
        self.view.file_drop_widget_clicked(handler=self._on_drag_drop_area_clicked)
        self.view.file_deleted(handler=self._on_file_widget_deleted)

        # Buttons
        self.view.delete_document_button_clicked(handler=self._on_delete_document_button_clicked)
        self.view.cancel_button_clicked(handler=self._on_cancel_button_clicked)
        self.view.save_button_clicked(handler=self._on_save_button_clicked)


    def _fill_document_tags(self) -> None:
        """Fills the document tags with data."""
        tags = []
        for tag in self.model.document_data.get("tags", []):
            tags.append(tag.get("name"))

        self.view.set_document_tags(tags=tags)

    
    def _fill_document_data(self) -> None:
        """Fills the document data with default values."""
        self.view.set_document_code(code=self.model.document_data.get("code") or "")
        self.view.set_document_name(name=self.model.document_data.get("name") or "")


    def _fill_pages_table(self) -> None:
        """Fills the pages table with data."""
        # Sorting the pages according to their order_index property
        self.model.pages.sort(key=lambda x: x.get("order_index", 0))

        # Make a list of pages for the editor table
        data = []
        if self.model.pages:
            for page in self.model.pages:
                name = page.get("name") or ""
                designation = page.get("designation") or ""
                data.append({
                    "id": page.get("id"),
                    "name": name,
                    "designation": designation
                })

        # Fill the editor table with a list of pages
        self.view.pages_table.update_pages(pages=data)

        # Update delete button state
        self._on_table_selection_changed()


    def _fill_files_list(self) -> None:
        """Fills the files list with data."""
        files = self.model.document_data.get("files", [])
        for file in files:
            self.view.add_file_widget(file)


    def _update_generate_button_state(self):
        """Updates the generate tags button state."""
        state = False if len(self.view.get_document_data().get("tags")) == 5 else True
        self.view.update_generate_button_state(state=state)

    
    def _update_save_document_button_state(self):
        """Updates the save document button state."""
        self.view.update_save_button_state(state=self.model.is_document_edited)