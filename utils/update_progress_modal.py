from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGraphicsDropShadowEffect,
    QLabel,
    QHBoxLayout
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal

from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from ui.custom_widgets import TertiaryButton, ProgressBar

class UpdateProgressDialog(BaseModalDialog):
    canceled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.container = ShadowContainer(self)
        self.container.setObjectName("updateProgressContainer")
        
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
        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setProgressValue(0)
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
                self.progress_bar.setRange(0, 0)
            # Show downloaded volume in MB
            self.status_label.setText(f"{current / 1024 / 1024:.1f} MB")
            return

        if self.progress_bar.maximum() != 100:
            self.progress_bar.setRange(0, 100)
        
        percent = int((current / total) * 100)
        self.progress_bar.setProgressValue(percent)
        
        current_mb = current / 1024 / 1024
        total_mb = total / 1024 / 1024
        self.status_label.setText(f"{current_mb:.1f} / {total_mb:.1f} MB ({percent}%)")

    def reject(self):
        self.canceled.emit()
        super().reject()