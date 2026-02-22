from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from pathlib import Path

from .layouts import FlowLayout
from utils import ThemeManagerInstance

class FileWidget(QFrame):
    """Widget representing a single file."""
    deleteClicked = pyqtSignal()

    def __init__(self, file_data: object, width: int = 300, parent=None):
        """
        Initializes the FileWidget.

        Args:
            file_data (object): Data associated with the file (dict or path string).
            width (int): Fixed width of the widget.
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)
        self.file_data = file_data
        
        if isinstance(file_data, dict):
            self.file_identifier = file_data.get("id")
            self.file_name = file_data.get("filename", "Unknown")
        else:
            self.file_identifier = str(file_data)
            self.file_name = Path(self.file_identifier).name

        self.setFixedSize(width, 150)
        self.setObjectName("FileWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Top row: Icon + Delete button
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel()
        # Using a generic document icon from resources (assuming it exists or using text fallback)
        # For now, we can use a placeholder or text if icon not available
        self.icon_label.setText("📄") 
        self.icon_label.setObjectName("fileIconLabel")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(40, 40)
        
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setObjectName("fileDeleteButton")
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(self.deleteClicked.emit)
        
        top_layout.addWidget(self.icon_label)
        top_layout.addStretch()
        top_layout.addWidget(self.delete_btn)
        
        layout.addLayout(top_layout)
        
        # Filename
        self.name_label = QLabel(self.file_name)
        self.name_label.setObjectName("fileNameLabel")
        self.name_label.setWordWrap(True)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.name_label)
        layout.addStretch()


class FileListWidget(QWidget):
    """Container for file widgets using FlowLayout."""
    fileDeleted = pyqtSignal(object)

    def __init__(self, parent=None):
        """Initializes the FileListWidget."""
        super().__init__(parent)
        self.spacing = 16
        self.layout = FlowLayout(self, margin=0, spacing=self.spacing)
        
        self.item_width = 300

    def resizeEvent(self, event):
        """Handles resize events to recalculate item sizes."""
        self._recalculate_item_size()
        super().resizeEvent(event)

    def _recalculate_item_size(self):
        """Recalculates the width of file widgets based on container width."""
        width = self.width()
        if width <= 0:
            return

        margins = self.layout.getContentsMargins()
        available_width = width - margins[0] - margins[2] - 1
        
        max_columns = 5
        min_item_width = 180
        
        columns = max_columns
        while columns > 1:
            w = (available_width - (columns - 1) * self.spacing) // columns
            if w >= min_item_width:
                break
            columns -= 1
            
        self.item_width = (available_width - (columns - 1) * self.spacing) // columns
        
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, FileWidget):
                widget.setFixedSize(self.item_width, 150)

    def add_file(self, file_data: object):
        """
        Adds a file widget to the list.

        Args:
            file_data (object): Data associated with the file.
        """
        widget = FileWidget(file_data, width=self.item_width)
        widget.deleteClicked.connect(lambda: self._on_widget_delete_clicked(widget))
        self.layout.addWidget(widget)

    def _on_widget_delete_clicked(self, widget: FileWidget):
        """Handles the delete button click on a file widget."""
        # Mark the widget so remove_file knows exactly which instance to delete
        widget._pending_deletion = True
        self.fileDeleted.emit(widget.file_identifier)

    def remove_file(self, file_identifier: object):
        """
        Removes a file widget from the list.

        Args:
            file_identifier (object): Identifier of the file to remove.
        """
        # 1. First, look for the marked widget (if deletion was triggered by a click)
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, FileWidget) and widget.file_identifier == file_identifier:
                if getattr(widget, '_pending_deletion', False):
                    widget.hide()
                    widget.deleteLater()
                    self.layout.takeAt(i)
                    self.layout.invalidate()
                    return

        # 2. If no marked widget (external deletion), delete the first one found
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, FileWidget) and widget.file_identifier == file_identifier:
                widget.hide()
                widget.deleteLater()
                self.layout.takeAt(i)
                self.layout.invalidate()
                break