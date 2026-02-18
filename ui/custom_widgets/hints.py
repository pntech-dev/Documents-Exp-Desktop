from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor

class PasswordHint(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Container for styling
        self.container = QWidget(self)
        self.container.setObjectName("passwordHintContainer")
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(16, 16, 16, 16)
        
        self.layout.addWidget(self.container)
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)
        
        self.labels = []

    def update_status(self, status_list: list[dict]):
        # Clear old labels
        for label in self.labels:
            self.container_layout.removeWidget(label)
            label.deleteLater()
        self.labels.clear()
        
        for item in status_list:
            label = QLabel(f"• {item['text']}")
            label.setObjectName("passwordHintLabel")
            label.setProperty("valid", item['valid'])
            self.container_layout.addWidget(label)
            self.labels.append(label)
            
        self.adjustSize()

    def show_at(self, pos: QPoint):
        self.move(pos)
        self.show()