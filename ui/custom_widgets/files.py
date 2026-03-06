from PyQt5.QtWidgets import QWidget, QFrame, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QGraphicsDropShadowEffect, QStyleOption, QStyle
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import QIcon, QColor, QPainter
from pathlib import Path
from datetime import datetime

from .layouts import FlowLayout
from utils import ThemeManagerInstance
from .buttons import PrimaryButton, TertiaryButton, NoFrameButton
from .menu import ThemeAwareMenu

class _FileActionsFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

class FileWidget(QWidget):
    """Widget representing a single file."""
    deleteClicked = pyqtSignal()
    openClicked = pyqtSignal(object)
    downloadClicked = pyqtSignal(object)

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
        
        self.file_size_str = ""
        self.file_date_str = ""

        if isinstance(file_data, dict):
            self.file_identifier = file_data.get("id")
            self.file_name = file_data.get("filename", "Unknown")
            
            size = file_data.get("size", 0)
            created_at = file_data.get("created_at")
            
            self.file_size_str = self._format_size(size)
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    self.file_date_str = dt.strftime("%d:%m:%Y")
                except ValueError:
                    pass
        else:
            self.file_identifier = str(file_data)
            self.file_name = Path(self.file_identifier).name
            try:
                p = Path(self.file_identifier)
                if p.exists():
                    stat = p.stat()
                    self.file_size_str = self._format_size(stat.st_size)
                    dt = datetime.fromtimestamp(stat.st_ctime)
                    self.file_date_str = dt.strftime("%d:%m:%Y")
            except Exception:
                pass

        self.setFixedWidth(width)
        self.setObjectName("FileWidget")
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main layout with margins for shadow
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Container (The visible card)
        self.container = QFrame(self)
        self.container.setObjectName("FileWidgetContainer")
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.main_layout.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Top row: Icon + Delete button
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        self.icon_label = QLabel()
        self.icon_label.setObjectName("fileIconLabel")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(56, 56)
        
        self.menu_btn = NoFrameButton(self.container)
        self.menu_btn.setObjectName("fileMenuButton")
        self.menu_btn.setFixedSize(42, 42)
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.clicked.connect(self._show_menu)
        self.menu_btn.set_icon_paths(
            # Light theme
            light_default=":/icons/light/light/menu_default.svg",
            light_hover=":/icons/light/light/menu_hover.svg",
            light_pressed=":/icons/light/light/menu_clicked.svg",
            light_disabled=":/icons/light/light/menu_disabled.svg",

            # Dark theme
            dark_default=":/icons/dark/dark/menu_default.svg",
            dark_hover=":/icons/dark/dark/menu_hover.svg",
            dark_pressed=":/icons/dark/dark/menu_clicked.svg",
            dark_disabled=":/icons/dark/dark/menu_disabled.svg",
        )
        self._setup_menu()
        
        top_layout.addWidget(self.icon_label)
        top_layout.addStretch()
        top_layout.addWidget(self.menu_btn)
        
        layout.addLayout(top_layout)
        
        # Filename
        self.name_label = QLabel(self.file_name)
        self.name_label.setObjectName("fileNameLabel")
        self.name_label.setToolTip(self.file_name)
        self.name_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.name_label)
        
        # Size Label
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.size_label = QLabel(self.file_size_str)
        self.size_label.setObjectName("fileInfoLabel")
        info_layout.addWidget(self.size_label)

        # Date Label
        self.date_label = QLabel(self.file_date_str)
        self.date_label.setObjectName("fileInfoLabel")
        info_layout.addWidget(self.date_label)
        
        layout.addLayout(info_layout)

        # Actions Overlay
        self.actions_frame = _FileActionsFrame(self.container)
        self.actions_frame.setObjectName("fileActionsFrame")
        self.actions_frame.hide()
        
        # Menu Shadow        
        actions_layout = QHBoxLayout(self.actions_frame)
        actions_layout.setContentsMargins(8, 8, 8, 8)
        actions_layout.setSpacing(8)
        
        self.open_btn = TertiaryButton(self.actions_frame)
        self.open_btn.setText("Открыть")
        self.open_btn.set_icon_paths(
            # Light theme
            light_default=":/icons/light/light/open_default.svg",
            light_hover=":/icons/light/light/open_hover.svg",
            light_pressed=":/icons/light/light/open_clicked.svg",
            light_disabled=":/icons/light/light/open_disabled.svg",

            # Dark theme
            dark_default=":/icons/dark/dark/open_default.svg",
            dark_hover=":/icons/dark/dark/open_hover.svg",
            dark_pressed=":/icons/dark/dark/open_clicked.svg",
            dark_disabled=":/icons/dark/dark/open_disabled.svg"
        )
        self.open_btn.setFixedHeight(42)
        self.open_btn.clicked.connect(lambda: self.openClicked.emit(self.file_identifier))
        
        self.download_btn = PrimaryButton(self.actions_frame)
        self.download_btn.setText("Скачать")
        self.download_btn.set_icon_paths(
            # Light theme
            light_default=":/icons/light/light/download_primary_default.svg",

            # Dark theme
            dark_default=":/icons/dark/dark/download_primary_default.svg",
            dark_disabled=":/icons/dark/dark/download_primary_disabled.svg"
        )
        self.download_btn.setFixedHeight(42)
        self.download_btn.clicked.connect(lambda: self.downloadClicked.emit(self.file_identifier))
        
        actions_layout.addWidget(self.open_btn)
        actions_layout.addWidget(self.download_btn)
        
        ThemeManagerInstance.themeChanged.connect(self._on_theme_changed)
        self._update_icon()

    def _setup_menu(self):
        self.menu = ThemeAwareMenu(self)
        
        self.menu.add_theme_action(
            text="Открыть",
            callback=lambda: self.openClicked.emit(self.file_identifier),
            # Light theme
            light_default=":/icons/light/light/open_default.svg",
            light_hover=":/icons/light/light/open_hover.svg",
            light_pressed=":/icons/light/light/open_clicked.svg",
            light_disabled=":/icons/light/light/open_disabled.svg",

            # Dark theme
            dark_default=":/icons/dark/dark/open_default.svg",
            dark_hover=":/icons/dark/dark/open_hover.svg",
            dark_pressed=":/icons/dark/dark/open_clicked.svg",
            dark_disabled=":/icons/dark/dark/open_disabled.svg"
        )
        
        self.menu.add_theme_action(
            text="Скачать",
            callback=lambda: self.downloadClicked.emit(self.file_identifier),
            # Light theme
            light_default=":/icons/light/light/download_default.svg",
            light_hover=":/icons/light/light/download_hover.svg",
            light_pressed=":/icons/light/light/download_clicked.svg",
            light_disabled=":/icons/light/light/download_disabled.svg",

            # Dark theme
            dark_default=":/icons/dark/dark/download_default.svg",
            dark_hover=":/icons/dark/dark/download_hover.svg",
            dark_pressed=":/icons/dark/dark/download_clicked.svg",
            dark_disabled=":/icons/dark/dark/download_disabled.svg"
        )
        
        self.menu.addSeparator()
        
        self.menu.add_theme_action(
            text="Удалить",
            danger_action=True,
            callback=self.deleteClicked.emit,
            # Light theme
            light_default=":/icons/light/light/trash_noframe_default.svg",
            light_hover=":/icons/light/light/trash_noframe_hover.svg",
            light_pressed=":/icons/light/light/trash_noframe_clicked.svg",
            light_disabled=":/icons/light/light/trash_noframe_disabled.svg",

            # Dark theme
            dark_default=":/icons/dark/dark/trash_noframe_default.svg",
            dark_hover=":/icons/dark/dark/trash_noframe_hover.svg",
            dark_pressed=":/icons/dark/dark/trash_noframe_clicked.svg",
            dark_disabled=":/icons/dark/dark/trash_noframe_disabled.svg"
        )

    def _show_menu(self):
        pos = self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height()))
        self.menu.exec_(pos)

    def enterEvent(self, event):
        self.actions_frame.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.actions_frame.hide()
        super().leaveEvent(event)

    def resizeEvent(self, event):
        if hasattr(self, 'actions_frame'):
            w = self.container.width()
            h = self.actions_frame.sizeHint().height()
            self.actions_frame.setGeometry(0, self.container.height() - h, w, h)
        self._update_elided_text()
        super().resizeEvent(event)

    def paintEvent(self, event):
        # No need to paint background for FileWidget itself as it is translucent
        pass

    def _format_size(self, size: int) -> str:
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def _update_elided_text(self):
        if not hasattr(self, 'name_label'):
            return
        
        available_width = self.width() - 48
        if available_width > 0:
            fm = self.name_label.fontMetrics()
            self.name_label.setText(fm.elidedText(self.file_name, Qt.ElideMiddle, available_width))

    def _get_icon_name(self) -> str:
        ext = Path(self.file_name).suffix.lower().lstrip('.')
        
        excel_exts = {'xls', 'xlsx', 'csv', 'ods', 'xlt', 'xltx'}
        pdf_exts = {'pdf'}
        word_exts = {'doc', 'docx', 'txt', 'rtf', 'odt'}
        media_exts = {'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'mp4', 'avi', 'mov', 'mkv', 'dwg', 'dxf'}
        
        if ext in excel_exts:
            return "attachment_green"
        elif ext in pdf_exts:
            return "attachment_red"
        elif ext in word_exts:
            return "attachment_blue"
        elif ext in media_exts:
            return "attachment_yellow"
        else:
            return "attachment_gray"

    def _update_icon(self):
        theme_id = ThemeManagerInstance.current_theme_id
        theme = "light" if theme_id == "0" else "dark"
        
        icon_name = self._get_icon_name()
        icon_path = f":/icons/{theme}/{theme}/{icon_name}.svg"
        
        icon = QIcon(icon_path)
        if not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(56, 56))
            self.icon_label.setText("")
        else:
            self.icon_label.setText("📄")

    def _on_theme_changed(self, theme_id: str):
        self._update_icon()

class FileListWidget(QWidget):
    """Container for file widgets using FlowLayout."""
    fileDeleted = pyqtSignal(object)
    fileDownloadRequested = pyqtSignal(object)
    fileOpenRequested = pyqtSignal(object)

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
                widget.setFixedWidth(self.item_width)

    def add_file(self, file_data: object):
        """
        Adds a file widget to the list.

        Args:
            file_data (object): Data associated with the file.
        """
        widget = FileWidget(file_data, width=self.item_width)
        widget.deleteClicked.connect(lambda: self._on_widget_delete_clicked(widget))
        widget.downloadClicked.connect(self.fileDownloadRequested.emit)
        widget.openClicked.connect(self.fileOpenRequested.emit)
        self.layout.addWidget(widget)

    def _on_widget_delete_clicked(self, widget: FileWidget):
        """Handles the delete button click on a file widget."""
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