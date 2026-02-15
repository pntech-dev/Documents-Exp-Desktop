from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor

from ui.ui_converted.delete_confirm import Ui_Dialog as DeleteConfirm_UI
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog


class DeleteConfirmDialog(BaseModalDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # === Setup UI ===
        self.ui = DeleteConfirm_UI()
        self.ui.setupUi(self)

        # Take layout from UI
        original_layout = self.layout()

        # Create a container widget that will hold the UI and have the shadow
        container = ShadowContainer(self)
        container.setLayout(original_layout)
        container.setObjectName("deleteConfirmContainer")

        # Reparent UI frames into container
        self.ui.info_frame.setParent(container)
        self.ui.buttons_frame.setParent(container)

        # === Shadow ===
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)

        # === Main layout (holds container with shadow margins) ===
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20) # For shadow space
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # === Connect handlers ===
        self.ui.delete_document_pushButton.clicked.connect(self.accept)
        self.ui.cancel_document_pushButton.clicked.connect(self.reject)

        # Set danger style for delete button
        if hasattr(self.ui.delete_document_pushButton, "set_danger"):
            self.ui.delete_document_pushButton.set_danger(is_danger=True)