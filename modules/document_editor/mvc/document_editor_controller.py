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
        self.view.cancel_button_clicked(handler=self._on_cancel_button_clicked)

    
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
                p_name = page.get("name") or ""
                p_designation = page.get("designation") or ""
                full_name = f"{p_name} {p_designation}".strip()
                data.append({"name": full_name})

        # Fill the editor table with a list of pages
        self.view.pages_table.update_pages(pages=data)