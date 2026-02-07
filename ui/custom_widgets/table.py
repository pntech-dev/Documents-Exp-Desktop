from PyQt5.QtGui import (
    QPainter, QMouseEvent, QStandardItemModel, 
    QStandardItem, QPalette
)
from PyQt5.QtCore import (
    Qt, QModelIndex, QEvent, QRect, pyqtSignal, QAbstractItemModel, QTimer,
    QPersistentModelIndex, QSize
)
from PyQt5.QtWidgets import (
    QTableView, QWidget, QFrame,
    QAbstractItemView, QStyle, QStyledItemDelegate,
    QStyleOptionViewItem, QHeaderView, QCheckBox,
    QApplication, QSizePolicy
)

from PyQt5.QtWidgets import QStyleOptionButton
from utils import ThemeManagerInstance


ROLE_PLACEHOLDER = Qt.UserRole + 99


class _HoverDelegate(QStyledItemDelegate):
    """Delegate to handle full row hover effect."""
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if index.data(ROLE_PLACEHOLDER):
            painter.save()
            # Draw placeholder style (e.g. dashed border)
            pen = painter.pen()
            pen.setStyle(Qt.DashLine)
            pen.setColor(option.palette.color(QPalette.Disabled, QPalette.Text))
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            r = option.rect.adjusted(2, 2, -2, -2)
            painter.drawRoundedRect(r, 4, 4)
            painter.restore()
            return

        view = self.parent()
        if hasattr(view, "hover_row") and view.hover_row == index.row():
            option.state |= QStyle.State_MouseOver
        super().paint(painter, option, index)


class _CheckBoxDelegate(_HoverDelegate):
    """Delegate to draw a checkbox using the application's QCheckBox style."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dummy_check = QCheckBox(parent)
        self.dummy_check.setVisible(False)
        self.dummy_check.setAttribute(Qt.WA_StyledBackground, True)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if index.data(ROLE_PLACEHOLDER):
            return

        # Remove check indicator feature so base class doesn't draw the default one
        opt = QStyleOptionViewItem(option)
        opt.features &= ~QStyleOptionViewItem.HasCheckIndicator
        
        # Draw background/selection via base
        super().paint(painter, opt, index)
        
        # Draw our custom checkbox
        check_state = index.data(Qt.CheckStateRole)
        
        btn_opt = QStyleOptionButton()
        box_size = 20
        r = option.rect
        x = r.left() + (r.width() - box_size) // 2
        y = r.top() + (r.height() - box_size) // 2
        btn_opt.rect = QRect(x, y, box_size, box_size)
        
        btn_opt.state = QStyle.State_Enabled | QStyle.State_Active
        if check_state == Qt.Checked:
            btn_opt.state |= QStyle.State_On
        else:
            btn_opt.state |= QStyle.State_Off
            
        if option.state & QStyle.State_MouseOver:
             btn_opt.state |= QStyle.State_MouseOver

        style = self.dummy_check.style() or QApplication.style()
        style.drawPrimitive(QStyle.PE_IndicatorCheckBox, btn_opt, painter, self.dummy_check)

    def editorEvent(self, event: QEvent, model: QAbstractItemModel, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        # Handle mouse events to toggle checkbox manually
        if event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick):
            if event.button() == Qt.LeftButton:
                # Calculate checkbox rect (must match paint logic)
                box_size = 20
                r = option.rect
                x = r.left() + (r.width() - box_size) // 2
                y = r.top() + (r.height() - box_size) // 2
                checkbox_rect = QRect(x, y, box_size, box_size)
                
                if checkbox_rect.contains(event.pos()):
                    if event.type() == QEvent.MouseButtonRelease:
                        state = index.data(Qt.CheckStateRole)
                        new_state = Qt.Unchecked if state == Qt.Checked else Qt.Checked
                        model.setData(index, new_state, Qt.CheckStateRole)
                    return True # Consume event to prevent row selection
        return super().editorEvent(event, model, option, index)


class _DragHandleDelegate(_HoverDelegate):
    """Delegate to draw a drag handle icon in the last column."""
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if index.data(ROLE_PLACEHOLDER):
            return

        # Draw the background (hover effect)
        super().paint(painter, option, index)

        # Draw the drag handle icon (three horizontal lines)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center of the cell
        cx, cy = option.rect.center().x(), option.rect.center().y()
        w = 14  # Width of the handle
        h = 10  # Total height of the handle
        
        # Color based on text color
        pen = painter.pen()
        color = option.palette.color(QPalette.Text)
        if option.state & QStyle.State_Selected:
             color = option.palette.color(QPalette.HighlightedText)
        
        # Make it slightly lighter/greyer for the handle
        color.setAlpha(128)
        pen.setColor(color)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawLine(cx - w//2, cy - 4, cx + w//2, cy - 4)
        painter.drawLine(cx - w//2, cy,     cx + w//2, cy)
        painter.drawLine(cx - w//2, cy + 4, cx + w//2, cy + 4)
        
        painter.restore()


class CheckBoxHeader(QHeaderView):
    """Header with a checkbox in the first column."""
    toggled = pyqtSignal(bool)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.isOn = False
        self.dummy_check = QCheckBox(parent)
        self.dummy_check.setVisible(False)
        self.dummy_check.setAttribute(Qt.WA_StyledBackground, True)

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            option = QStyleOptionButton()
            # Center the checkbox
            box_size = 18
            x = rect.left() + (rect.width() - box_size) // 2
            y = rect.top() + (rect.height() - box_size) // 2
            option.rect = QRect(x, y, box_size, box_size)
            
            option.state = QStyle.State_Enabled | QStyle.State_Active
            if self.isOn:
                option.state |= QStyle.State_On
            else:
                option.state |= QStyle.State_Off
            
            style = self.dummy_check.style() or QApplication.style()
            style.drawPrimitive(QStyle.PE_IndicatorCheckBox, option, painter, self.dummy_check)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if the click is within the first section
            if self.logicalIndexAt(event.pos()) == 0:
                self.isOn = not self.isOn
                self.toggled.emit(self.isOn)
                self.viewport().update()
                super().mousePressEvent(event)
                return
        super().mousePressEvent(event)

    def setChecked(self, checked: bool):
        if self.isOn != checked:
            self.isOn = checked
            self.viewport().update()


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


class EditorTableView(DocumentsTableView):
    """
    Table view for the editor with checkboxes and drag-and-drop reordering.
    Signals:
        rowMoved(str, int): Emitted when a row is dropped (id, new_index).
    """
    rowMoved = pyqtSignal(str, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        # Enable Drag & Drop
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)

        # Custom Header
        self._header = CheckBoxHeader(Qt.Horizontal, self)
        self.setHorizontalHeader(self._header)
        self._header.toggled.connect(self._on_header_toggled)
        
        # We need to ensure the header behaves like the base class header regarding resize modes
        self._header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self._header.setStretchLastSection(False) # We will manage the last column manually or let it resize
        
        self.setItemDelegateForColumn(0, _CheckBoxDelegate(self))
        
        self._placeholder_row = None
        self._source_persistent_index = QPersistentModelIndex()
        self._source_original_row = -1
        self._source_items = []
        self._drag_active = False
        self._bulk_update = False

        self._model.rowsInserted.connect(self._on_rows_changed)
        self._model.rowsRemoved.connect(self._on_rows_changed)
        self._model.modelReset.connect(self._on_rows_changed)

        # Set initial constraints
        self.setMinimumHeight(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def set_rows(self, rows: list[tuple[str, list]]) -> None:
        """
        Sets the rows for the editor table.
        Args:
            rows: List of tuples (id, [data_values...])
        """
        self._bulk_update = True
        self.setUpdatesEnabled(False)
        self.setSortingEnabled(False)
        self._model.removeRows(0, self._model.rowCount())

        for row_id, row_data in rows:
            items = []
            
            # 1. Checkbox Column
            check_item = QStandardItem()
            check_item.setCheckable(True)
            check_item.setEditable(False)
            check_item.setDropEnabled(False)
            check_item.setData(row_id, Qt.UserRole) # Store ID in the first item
            items.append(check_item)
            
            # 2. Data Columns
            for value in row_data:
                item = QStandardItem(str(value))
                item.setEditable(True)
                item.setDropEnabled(False)
                items.append(item)
            
            # 3. Drag Handle Column
            drag_item = QStandardItem()
            drag_item.setEditable(False)
            drag_item.setDropEnabled(False)
            items.append(drag_item)
            
            self._model.appendRow(items)

        # Set delegate for the last column (Drag Handle)
        if self._model.columnCount() > 0:
            last_col = self._model.columnCount() - 1
            self.setItemDelegateForColumn(last_col, _DragHandleDelegate(self))
            self.horizontalHeader().setSectionResizeMode(last_col, QHeaderView.Fixed)
            self.setColumnWidth(last_col, 40)
            
        # Stretch the second column (Name)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self._bulk_update = False
        self.setUpdatesEnabled(True)
        self.resizeRowsToContents()

    def resizeRowsToContents(self):
        super().resizeRowsToContents()
        self._update_table_height()

    def _on_rows_changed(self, *args):
        if not self._bulk_update:
            self.resizeRowsToContents()

    def _update_table_height(self):
        """Updates the geometry to trigger layout recalculation."""
        self.updateGeometry()

    def sizeHint(self) -> QSize:
        """Returns the size hint based on content."""
        # Header height
        h = self.horizontalHeader().height()
        # Rows height
        h += self.verticalHeader().length()
        # Frame width (top + bottom)
        h += self.frameWidth() * 2
        
        target_h = max(300, h)
        return QSize(super().sizeHint().width(), target_h)

    def _on_header_toggled(self, checked: bool):
        """Selects or deselects all row checkboxes."""
        for row in range(self._model.rowCount()):
            item = self._model.item(row, 0)
            item.setCheckState(Qt.Checked if checked else Qt.Unchecked)

    def startDrag(self, supportedActions):
        indexes = self.selectedIndexes()
        if not indexes:
            return
            
        self._drag_active = True
        self._source_original_row = indexes[0].row()
        # Clone items for restoration or drop
        self._source_items = [self._model.item(self._source_original_row, c).clone() for c in range(self._model.columnCount())]
        
        self._placeholder_row = None
        self._drop_completed = False
        
        # Schedule removal of the row to happen after drag starts (so pixmap is created from visible row)
        QTimer.singleShot(0, self._remove_source_row)
        
        super().startDrag(supportedActions)
        
        self._drag_active = False
        
        # Cleanup after drag (if drop didn't happen or was cancelled)
        if self._placeholder_row is not None:
            self._model.removeRow(self._placeholder_row)
            self._placeholder_row = None
            
        if not self._drop_completed:
            # Restore the row if it was removed and not dropped
            if not self._source_persistent_index.isValid():
                self._model.insertRow(self._source_original_row, self._source_items)
            
        self.viewport().update()

    def _remove_source_row(self):
        if self._drag_active and self._source_persistent_index.isValid():
            r = self._source_persistent_index.row()
            self._model.removeRow(r)
            
            if self._placeholder_row is not None and self._placeholder_row > r:
                self._placeholder_row -= 1
        self.viewport().update()

    def dragMoveEvent(self, event):
        if event.source() != self:
            super().dragMoveEvent(event)
            return

        pos = event.pos()
        target_index = self.indexAt(pos)
        
        if target_index.isValid():
            target_row = target_index.row()
        else:
            # If below last item
            target_row = self._model.rowCount()
            
        # If we are over the placeholder, we don't need to move it.
        if self._placeholder_row is not None and target_row == self._placeholder_row:
            event.accept()
            return

        # Insert or Move placeholder
        if self._placeholder_row is None:
            self._insert_placeholder(target_row)
        else:
            # Move placeholder
            items = self._model.takeRow(self._placeholder_row)
            
            # Adjust target_row if needed because of removal
            if target_row > self._placeholder_row:
                target_row -= 1
                
            self._model.insertRow(target_row, items)
            self._placeholder_row = target_row

        event.accept()

    def dragLeaveEvent(self, event):
        # Remove placeholder if drag leaves the widget
        if self._placeholder_row is not None:
            self._model.removeRow(self._placeholder_row)
            self._placeholder_row = None
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        """Handles row reordering manually to prevent duplication and allow flexible dropping."""
        if event.source() != self or event.dropAction() != Qt.MoveAction:
            super().dropEvent(event)
            return

        if self._placeholder_row is None:
            event.ignore()
            return

        dest_row = self._placeholder_row
        self._model.removeRow(self._placeholder_row)
        self._placeholder_row = None
        
        if self._source_persistent_index.isValid():
            src_row = self._source_persistent_index.row()
            self._model.removeRow(src_row)
            if src_row < dest_row:
                dest_row -= 1
        
        new_items = [item.clone() for item in self._source_items]
        self._model.insertRow(dest_row, new_items)
        
        self._drop_completed = True
        
        row_id = new_items[0].data(Qt.UserRole)
        self.rowMoved.emit(str(row_id), dest_row)
            
        event.accept()

    def _insert_placeholder(self, row):
        items = []
        for i in range(self._model.columnCount()):
            item = QStandardItem()
            item.setEditable(False)
            item.setDropEnabled(False)
            item.setData(True, ROLE_PLACEHOLDER)
            item.setFlags(Qt.NoItemFlags)
            items.append(item)
        self._model.insertRow(row, items)
        self._placeholder_row = row