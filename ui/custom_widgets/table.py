from PyQt5.QtGui import (
    QPainter, QMouseEvent, QStandardItemModel, 
    QStandardItem
)
from PyQt5.QtCore import (
    Qt, QModelIndex, QEvent
)
from PyQt5.QtWidgets import (
    QTableView, QWidget, QFrame,
    QAbstractItemView, QStyle, QStyledItemDelegate,
    QStyleOptionViewItem, QHeaderView
)

from utils import ThemeManagerInstance



class _HoverDelegate(QStyledItemDelegate):
    """Delegate to handle full row hover effect."""
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        view = self.parent()
        if hasattr(view, "hover_row") and view.hover_row == index.row():
            option.state |= QStyle.State_MouseOver
        super().paint(painter, option, index)

class DocumentsTableView(QTableView):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the custom table view."""
        super().__init__(parent)
        
        # Behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setMouseTracking(True)
        self.hover_row = -1
        self.setItemDelegate(_HoverDelegate(self))
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Text wrapping
        self.setWordWrap(True)
        self.setTextElideMode(Qt.ElideNone)
        
        # Headers
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.verticalHeader().setMinimumSectionSize(44)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setSortingEnabled(True)

        # Model initialization
        self._model = QStandardItemModel(self)
        self.setModel(self._model)

        # Update row heights when columns are resized (e.g. window resize)
        self.horizontalHeader().sectionResized.connect(lambda *args: self.resizeRowsToContents())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles mouse move to track hovered row."""
        index = self.indexAt(event.pos())
        old_hover = self.hover_row
        if index.isValid():
            self.hover_row = index.row()
        else:
            self.hover_row = -1
        
        if self.hover_row != old_hover:
            self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handles mouse leave to reset hovered row."""
        if self.hover_row != -1:
            self.hover_row = -1
            self.viewport().update()
        super().leaveEvent(event)

    def set_headers(self, labels: list[str]) -> None:
        """Sets the horizontal header labels."""
        self._model.setHorizontalHeaderLabels(labels)

    def set_rows(self, rows: list[list]) -> None:
        """Replaces the table data with new rows."""
        # Optimization: Disable updates and sorting during bulk insertion
        self.setUpdatesEnabled(False)
        self.setSortingEnabled(False)

        self._model.removeRows(0, self._model.rowCount())
        for row_data in rows:
            items = []
            for value in row_data:
                item = QStandardItem(str(value))
                item.setEditable(False)
                items.append(item)
            self._model.appendRow(items)

        self.setSortingEnabled(True)
        self.setUpdatesEnabled(True)
        self.resizeRowsToContents()