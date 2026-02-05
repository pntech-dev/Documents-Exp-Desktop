class DocumentEditorController:
    def __init__(
            self, 
            model, 
            view, 
            window, 
            pages: list[dict]
    ):
        self.model = model
        self.view = view
        self.window = window
        self.pages = pages

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
        # Sorting the pages according to their order_index property
        self.pages.sort(key=lambda x: x.get("order_index", 0))

        # Make a list of pages for the editor table
        data = []
        for page in self.pages:
            p_name = page.get("name") or ""
            p_designation = page.get("designation") or ""
            full_name = f"{p_name} {p_designation}".strip()
            data.append({"name": full_name})

        # Fill the editor table with a list of pages
        self.view.pages_table.update_pages(pages=data)


    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""
        self.view.cancel_button_clicked(handler=self._on_cancel_button_clicked)