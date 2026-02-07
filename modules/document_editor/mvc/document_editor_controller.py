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


    def _on_document_data_changed(self):
        self.model.is_document_edited = True
        self._update_save_document_button_state()


    def _on_add_page_button_clicked(self) -> None:
        """Handles the add page button click event."""
        self.view.add_new_page()
        self._on_document_data_changed()

    
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
        self.view.save_button_clicked(handler=self._on_save_button_clicked)
        self.view.cancel_button_clicked(handler=self._on_cancel_button_clicked)
        self.view.pages_table_item_changed(handler=self._on_document_data_changed)
        self.view.pages_table_row_moved(handler=self._on_document_data_changed)

    
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

    
    def _update_save_document_button_state(self):
        """Updates the save document button state."""
        self.view.update_save_button_state(state=self.model.is_document_edited)