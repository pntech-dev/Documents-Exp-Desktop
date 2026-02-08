from pathlib import Path
from PyQt5.QtWidgets import QFileDialog



class DocumentEditorController:
    def __init__(
            self, 
            model, 
            view, 
            window,
    ):
        self.model = model
        self.view = view
        self.window = window

        self._init_ui()
        self._setup_connections()


    # ====================
    # Handlers
    # ====================


    def _on_document_data_changed(self, *args):
        self.model.is_document_edited = True
        self._update_save_document_button_state()


    def _on_table_selection_changed(self, *args) -> None:
        """Updates the delete page button state."""
        state = self.view.has_selected_pages()
        self.view.update_duplicate_button_state(state=state)
        self.view.update_delete_page_button_state(state=state)


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
        print("Print button clicked")


    def _on_import_button_clicked(self) -> None:
        """Handles the import button click event."""
        print("Import button clicked")


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
            self.model.export_to_docx(
                path=str(path_obj.parent), 
                filename=path_obj.name, 
                data=data
            )


    def _on_delete_page_button_clicked(self) -> None:
        """Handles the delete page button click event."""
        self.view.delete_selected_pages()
        self._on_document_data_changed()
        self._on_table_selection_changed()

    
    def _on_save_button_clicked(self) -> None:
        """Handles the save button click event."""
        data = self.view.get_document_data()
        self.model.save_document(data=data)
        self.window.document_saved.emit()
        self.window.close()


    def _on_cancel_button_clicked(self) -> None:
        """Handles the cancel button click event."""
        self.window.close()


    # ====================
    # Controller Methods
    # ====================


    def _init_ui(self) -> None:
        """Initializes the UI with default data."""
        self._fill_document_data()
        self._fill_pages_table()


    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""
        self.view.code_lineedit_text_changed(handler=self._on_document_data_changed)
        self.view.name_lineedit_text_changed(handler=self._on_document_data_changed)

        self.view.toolbar_add_page_button_clicked(handler=self._on_add_page_button_clicked)
        self.view.toolbar_duplicate_page_button_clicked(handler=self._on_duplicate_page_button_clicked)
        self.view.toolbar_print_button_clicked(handler=self._on_print_button_clicked)
        self.view.toolbar_import_button_clicked(handler=self._on_import_button_clicked)
        self.view.toolbar_export_button_clicked(handler=self._on_export_button_clicked)
        self.view.toolbar_delete_page_button_clicked(handler=self._on_delete_page_button_clicked)

        self.view.pages_table_item_changed(handler=self._on_document_data_changed)
        self.view.pages_table_row_moved(handler=self._on_document_data_changed)
        self.view.pages_table_selection_changed(handler=self._on_table_selection_changed)
        self.view.pages_table_item_changed(handler=self._on_table_selection_changed)

        self.view.cancel_button_clicked(handler=self._on_cancel_button_clicked)
        self.view.save_button_clicked(handler=self._on_save_button_clicked)

    
    def _fill_document_data(self) -> None:
        """Fills the document data with default values."""
        self.view.set_document_code(code=self.model.document_data.get("code"))
        self.view.set_document_name(name=self.model.document_data.get("name"))


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

    
    def _update_save_document_button_state(self):
        """Updates the save document button state."""
        self.view.update_save_button_state(state=self.model.is_document_edited)