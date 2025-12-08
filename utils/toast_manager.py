import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication

from ui import Notification_UI


class ToastWidget(QWidget):
    def __init__(
            self, 
            type: str, 
            label: str, 
            description: str, 
            parent=None
    ) -> None:
        super().__init__(parent)

        self.type = type
        self.label = label
        self.description = description

        # Types of notifications
        self.toasts_types = ["success", "info", "warning", "error"] 

        # Check notification type
        if self.type not in self.toasts_types:
            message = f"NOTIFICATION TYPE. The type of toast notification was incorrect.\nYour type: {self.type}. Correct types: {self.toasts_types}"
            logging.error(msg=message)
            return
        
        # Set notification style
        self.ui = Notification_UI()
        self.ui.setupUi(self)
        
        # Set text and adjust layout
        self.ui.label.setText(self.label)
        self.ui.description.setText(self.description)
        
        # Set window flags
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set notification property
        self.setProperty("notificationType", self.type)
        
    
    def show_notification(self) -> None:
        """Show the notification"""
        self.show()
