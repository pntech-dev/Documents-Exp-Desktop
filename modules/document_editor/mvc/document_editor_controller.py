class DocumentEditorController:
    def __init__(self, model, view, window):
        self.model = model
        self.view = view
        self.window = window

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

    def _setup_connections(self) -> None:
        """Sets up signal-slot connections."""
        self.view.cancel_button_clicked(handler=self._on_cancel_button_clicked)

        # TODO Rewrite to adding real data
        self.view.pages_table.update_pages(pages=[
            {"name": "Страница 1"},
            {"name": "Страница 2"}, 
            {"name": "Страница 3"},
            {"name": "Страница 4"},
            {"name": "Страница 5"},
            {"name": "Страница 6"},
            {"name": "Страница 7"},
            {"name": "Страница 8"},
            {"name": "Страница 9"},
            {"name": "Страница 10"}
        ])