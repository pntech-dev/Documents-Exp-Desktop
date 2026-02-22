from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPainter, QPen, QColor

from utils import ThemeManagerInstance

class FileDropWidget(QFrame):
    """
    Виджет для Drag & Drop файлов.
    Поддерживает перетаскивание файлов и клик для открытия диалога.
    """
    filesDropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("FileDropWidget")
        self.setCursor(Qt.PointingHandCursor)

        # Default colors
        self._border_color = QColor("#808080")
        self._active_color = QColor("#CC3333")

        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        self.setMinimumHeight(100)
        
        # Label
        self.label = QLabel("Перетащите файлы сюда или нажмите для выбора")
        self.label.setObjectName("fileDropLabel")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self._is_drag_active = False

    def getBorderColor(self) -> QColor:
        return self._border_color

    def setBorderColor(self, color: QColor) -> None:
        self._border_color = color
        self.update()

    borderColor = pyqtProperty(QColor, getBorderColor, setBorderColor)

    def getActiveColor(self) -> QColor:
        return self._active_color

    def setActiveColor(self, color: QColor) -> None:
        self._active_color = color
        self.update()

    activeColor = pyqtProperty(QColor, getActiveColor, setActiveColor)

    def _on_theme_changed(self, theme_id: str) -> None:
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            self._is_drag_active = True
            self.update()
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self._is_drag_active = False
        self.update()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        self._is_drag_active = False
        self.update()
        
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path:
                files.append(file_path)
        
        if files:
            self.filesDropped.emit(files)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Отрисовка пунктирной рамки
        color = self._active_color if self._is_drag_active else self._border_color
        pen = QPen(color)
        pen.setWidth(2)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 8, 8)
        
        # Фон при наведении
        if self._is_drag_active:
            bg_color = QColor(self._active_color)
            bg_color.setAlpha(30)
            painter.fillRect(rect, bg_color)