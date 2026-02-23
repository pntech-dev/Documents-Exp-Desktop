from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

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
        self.setAcceptDrops(False)
        self.setObjectName("FileDropWidget")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_Hover, True)

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
        
        self.sub_label = QLabel("Максимальный размер файла — 50 МБ")
        self.sub_label.setObjectName("fileDropSubLabel")
        self.sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sub_label)
        
    def _on_theme_changed(self, theme_id: str) -> None:
        self.style().unpolish(self)
        self.style().polish(self)

    def setDragActive(self, active: bool):
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)
        self.sub_label.style().unpolish(self.sub_label)
        self.sub_label.style().polish(self.sub_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)