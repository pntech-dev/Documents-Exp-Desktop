from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
    QHBoxLayout
)
from PyQt5.QtGui import QColor, QFont

from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from ui.custom_widgets import PrimaryButton, TertiaryButton
from utils import ThemeManagerInstance

class InstallConfirmDialog(BaseModalDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.container = ShadowContainer(self)
        self.container.setObjectName("installConfirmContainer")
        
        self._update_style()
        ThemeManagerInstance().themeChanged.connect(self._update_style)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Title
        self.title_label = QLabel("Установка")
        self.title_label.setObjectName("title_label")
        font = QFont()
        font.setPointSize(14)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Info
        self.info_label = QLabel("Обновление скачано. Приложение будет закрыто для установки. Продолжить?")
        self.info_label.setObjectName("text_label")
        font_info = QFont()
        font_info.setPointSize(12)
        self.info_label.setFont(font_info)
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(16)

        self.cancel_button = TertiaryButton()
        self.cancel_button.setText("Отмена")
        self.cancel_button.setMinimumHeight(42)
        self.cancel_button.clicked.connect(self.reject)
        
        self.install_button = PrimaryButton()
        self.install_button.setText("Установить")
        self.install_button.setMinimumHeight(42)
        self.install_button.clicked.connect(self.accept)

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.install_button)

        layout.addLayout(buttons_layout)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)

    def _update_style(self):
        theme_id = ThemeManagerInstance().current_theme_id
        if theme_id == "0": # Light
            bg_color = "#FFFFFF"
            border_color = "#E6E6E6"
        else: # Dark
            bg_color = "#262626"
            border_color = "#404040"
            
        self.container.setStyleSheet(f"""
            QFrame#installConfirmContainer {{
                background-color: {bg_color};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
        """)