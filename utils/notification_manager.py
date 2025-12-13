from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect


class NotificationWidget(QDialog):
    def __init__(self, type: str, label: str, description: str, parent=None):
        super().__init__(parent)
        self.type = type
        self.label = label
        self.description = description

        # Set notification style
        from ui import Notification_D_UI
        self.ui = Notification_D_UI()
        self.ui.setupUi(self)

        # Set window flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        # self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set texts
        self._set_texts()

        # Set layout margins
        self.ui.horizontalLayout.setContentsMargins(20, 20, 20, 20)

        # Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        self.ui.notification_container.setGraphicsEffect(shadow)

        """=== Handlers ==="""
        self.ui.close_pushButton.clicked.connect(self.close_notification)

    
    def close_notification(self):
        self.close()

    
    def _set_texts(self):
        self.ui.label_label.setText(self.label)
        self.ui.description_label.setText(self.description)