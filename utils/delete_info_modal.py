from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon

from ui.ui_converted.delete_info import Ui_Dialog as DeleteInfo_UI
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from utils import ThemeManagerInstance


class DeleteInfoDialog(BaseModalDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # === Setup UI ===
        self.ui = DeleteInfo_UI()
        self.ui.setupUi(self)

        # Take layout from UI
        original_layout = self.layout()

        # Create a container widget that will hold the UI and have the shadow
        container = ShadowContainer(self)
        container.setLayout(original_layout)
        container.setObjectName("deleteInfoContainer")

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
        self.ui.delete_pushButton.clicked.connect(self.accept)
        self.ui.cancel_pushButton.clicked.connect(self.reject)

        # Set danger style for delete button
        if hasattr(self.ui.delete_pushButton, "set_danger"):
            self.ui.delete_pushButton.set_danger(is_danger=True)

        # === Icon setup ===
        self._update_icon()
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

    def _update_icon(self):
        theme_id = ThemeManagerInstance().current_theme_id
        if theme_id == "0":
            icon_path = ":/icons/light/light/notification_warning_red.svg"
        else:
            icon_path = ":/icons/dark/dark/notification_warning_red.svg"
        
        if hasattr(self.ui.icon_label, "setIcon"):
            self.ui.icon_label.setIcon(QIcon(icon_path))
            if hasattr(self.ui.icon_label, "setIconSize"):
                self.ui.icon_label.setIconSize(QSize(24, 24))

    def _on_theme_changed(self, theme_id: str):
        self._update_icon()