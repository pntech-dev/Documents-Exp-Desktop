from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
    QFrame,
    QHBoxLayout
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from ui.custom_widgets import PrimaryButton, TertiaryButton

class UpdateConfirmDialog(BaseModalDialog):
    def __init__(self, parent=None, version: str = ""):
        super().__init__(parent)
        
        # Container setup
        self.container = ShadowContainer(self)
        self.container.setObjectName("updateConfirmContainer")
        
        # Layouts
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(24)

        # Text Frame
        text_frame = QFrame()
        text_layout = QVBoxLayout(text_frame)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(16)

        # Title
        self.title_label = QLabel("Доступно обновление")
        self.title_label.setObjectName("title_label") # Uses existing QSS styles
        font = QFont()
        font.setPointSize(14)
        self.title_label.setFont(font)
        text_layout.addWidget(self.title_label)

        # Info
        self.info_label = QLabel(f"Доступна новая версия приложения: {version}\nХотите обновить сейчас?")
        self.info_label.setObjectName("text_label") # Uses existing QSS styles
        font_info = QFont()
        font_info.setPointSize(12)
        self.info_label.setFont(font_info)
        self.info_label.setWordWrap(True)
        text_layout.addWidget(self.info_label)

        container_layout.addWidget(text_frame)

        # Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(16)

        self.cancel_button = TertiaryButton()
        self.cancel_button.setText("Позже")
        self.cancel_button.setMinimumHeight(42)
        self.cancel_button.clicked.connect(self.reject)
        
        self.update_button = PrimaryButton()
        self.update_button.setText("Обновить")
        self.update_button.setMinimumHeight(42)
        self.update_button.clicked.connect(self.accept)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.update_button)

        container_layout.addWidget(buttons_frame)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)