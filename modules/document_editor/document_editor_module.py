from .mvc import (
    DocumentEditorModel, DocumentEditorView, DocumentEditorController
)

from PyQt5.QtWidgets import QDialog


class EditorWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()

        # UI Initialization
        from ui import DocumentEditor_UI
        self.ui = DocumentEditor_UI()
        self.ui.setupUi(self)

        # MVC Initialization
        self.model = DocumentEditorModel()
        self.view = DocumentEditorView(ui=self.ui)
        self.controller = DocumentEditorController(
            model=self.model, 
            view=self.view, 
            window=self
        )