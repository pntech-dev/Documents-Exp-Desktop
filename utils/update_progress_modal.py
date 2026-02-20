from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
    QHBoxLayout,
    QProgressBar
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from ui.custom_widgets import TertiaryButton
from utils import ThemeManagerInstance

class UpdateProgressDialog(BaseModalDialog):
    canceled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.container = ShadowContainer(self)
        self.container.setObjectName("updateProgressContainer")
        
        self._update_style()
        ThemeManagerInstance().themeChanged.connect(self._update_style)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Title
        self.title_label = QLabel("Скачивание обновления...")
        self.title_label.setObjectName("title_label")
        font = QFont()
        font.setPointSize(14)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Status Label
        self.status_label = QLabel("0%")
        self.status_label.setAlignment(Qt.AlignRight)
        self.status_label.setObjectName("text_label")
        layout.addWidget(self.status_label)

        # Cancel Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = TertiaryButton()
        self.cancel_button.setText("Отмена")
        self.cancel_button.setMinimumHeight(42)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

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

    def set_progress(self, current: int, total: int):
        """Updates the progress bar and label."""
        if total <= 0:
            if self.progress_bar.maximum() != 0:
                self.progress_bar.setRange(0, 0) # Включает режим "бегающей" полоски (indeterminate)
            # Показываем скачанный объем в МБ
            self.status_label.setText(f"{current / 1024 / 1024:.1f} MB")
        else:
            if self.progress_bar.maximum() != 100:
                self.progress_bar.setRange(0, 100)
            
            percent = int((current / total) * 100)
            self.progress_bar.setValue(min(percent, 100))
            
            current_mb = current / 1024 / 1024
            total_mb = total / 1024 / 1024
            self.status_label.setText(f"{current_mb:.1f} / {total_mb:.1f} MB ({percent}%)")

    def reject(self):
        self.canceled.emit()
        super().reject()

    def _update_style(self):
        theme_id = ThemeManagerInstance().current_theme_id
        if theme_id == "0": # Light
            bg_color = "#FFFFFF"
            border_color = "#E6E6E6"
        else: # Dark
            bg_color = "#262626"
            border_color = "#404040"
            
        self.container.setStyleSheet(f"""
            QFrame#updateProgressContainer {{
                background-color: {bg_color};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
        """)