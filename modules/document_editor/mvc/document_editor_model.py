class DocumentEditorModel:
    def __init__(
            self, 
            document_data: dict = None, 
            pages: list[dict] = None
    ) -> None:
        self.document_data = document_data
        self.pages = pages