from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPoint
from PyQt5.QtGui import QColor


from .mvc import (
    DocumentEditorModel, DocumentEditorView, DocumentEditorController
)

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGraphicsDropShadowEffect, QApplication
)

from ui.custom_widgets.modal_window import ShadowContainer, ModalOverlay


class EditorWindow(QDialog):
    document_saved = pyqtSignal()
    document_deleted = pyqtSignal()

    def __init__(
            self, 
            parent=None, 
            mode: str = None,
            category_id: int = None,
            document_data: dict = None, 
            pages: list[dict] = None
    ) -> None:
        super().__init__(parent)

        self.overlay = None

        # === Window flags ===
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # === Container & Layout ===
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setAlignment(Qt.AlignCenter)
        
        self.container = ShadowContainer(self)
        self.container.setObjectName("editorContainer")
        main_layout.addWidget(self.container)

        # === Shadow ===
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        # MVC Initialization
        self.model = DocumentEditorModel(
            category_id=category_id,
            document_data=document_data, 
            pages=pages
        )
        self.view = DocumentEditorView(container=self.container)
        self.controller = DocumentEditorController(
            mode=mode,
            model=self.model, 
            view=self.view, 
            window=self,
        )

        # Set initial geometry to prevent flickering
        self.center_on_screen()

    def keyPressEvent(self, event):
        """Prevents the window from closing when the Enter key is pressed."""
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            return
        super().keyPressEvent(event)

    # Center modal on screen
    def showEvent(self, event):
        super().showEvent(event)
        self.create_overlay()
        self.center_on_screen()

    
    def closeEvent(self, event):
        if self.overlay:
            self.overlay.close()
        super().closeEvent(event)


    def create_overlay(self):
        if self.parent():
            # Try to find the top level window to cover
            parent_window = self.parent().window()
            self.overlay = ModalOverlay(parent_window)
            self.overlay.resize(parent_window.size())
            self.overlay.show()
            self.overlay.raise_()


    def center_on_screen(self):
        if self.parent():
            parent = self.parent().window()
            self.resize(parent.size())
            self.move(parent.mapToGlobal(QPoint(0, 0)))
        else:
            self.adjustSize()
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.center().x() - self.width() // 2
            y = screen.center().y() - self.height() // 2
            self.move(x, y)