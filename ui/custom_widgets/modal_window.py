from PyQt5.QtWidgets import QFrame, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter


# Shadow
class ShadowContainer(QFrame):
    """A QFrame that serves as the visible background for a custom dialog."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)


# Overlay
class ModalOverlay(QWidget):
    """A semi-transparent widget to darken the background."""
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.opacity = 100 # (0–255)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self.opacity))