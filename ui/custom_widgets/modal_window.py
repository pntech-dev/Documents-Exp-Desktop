from PyQt5.QtWidgets import QFrame, QWidget, QDialog, QApplication
from PyQt5.QtCore import Qt, QTimer, QPoint, QEvent
from PyQt5.QtGui import QColor, QPainter, QShowEvent, QCloseEvent


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
        self.setAttribute(Qt.WA_AlwaysStackOnTop, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.opacity = 100 # (0–255)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self.opacity))


class BaseModalDialog(QDialog):
    """Base class for modal dialogs with overlay and centering."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.overlay = None
        self._overlay_parent = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.create_overlay()
        QTimer.singleShot(0, self.center_on_screen)

    def closeEvent(self, event: QCloseEvent):
        if self.overlay:
            self.overlay.close()
        if self._overlay_parent:
            self._overlay_parent.removeEventFilter(self)
            self._overlay_parent = None
        super().closeEvent(event)

    def accept(self):
        if self.overlay:
            self.overlay.close()
        if self._overlay_parent:
            self._overlay_parent.removeEventFilter(self)
            self._overlay_parent = None
        super().accept()

    def reject(self):
        if self.overlay:
            self.overlay.close()
        if self._overlay_parent:
            self._overlay_parent.removeEventFilter(self)
            self._overlay_parent = None
        super().reject()

    def create_overlay(self):
        if self.parent():
            parent_window = self.parent().window()
            self._overlay_parent = parent_window
            parent_window.installEventFilter(self)
            self.overlay = ModalOverlay(parent_window)
            self._sync_overlay_geometry()
            self.overlay.show()
            self.overlay.raise_()

    def _sync_overlay_geometry(self):
        if self.overlay and self._overlay_parent:
            self.overlay.setGeometry(self._overlay_parent.rect())
            self.overlay.raise_()

    def eventFilter(self, watched, event):
        if watched == self._overlay_parent and event.type() in (
            QEvent.Resize,
            QEvent.Move,
            QEvent.Show,
            QEvent.ZOrderChange,
            QEvent.ChildAdded,
        ):
            self._sync_overlay_geometry()
        return super().eventFilter(watched, event)

    def center_on_screen(self):
        self.adjustSize()
        if self.parent():
            parent = self.parent().window()
            x = parent.x() + (parent.width() - self.width()) // 2
            y = parent.y() + (parent.height() - self.height()) // 2
            self.move(x, y)
        else:
            screen = QApplication.primaryScreen().availableGeometry()
            x = screen.center().x() - self.width() // 2
            y = screen.center().y() - self.height() // 2
            self.move(x, y)
