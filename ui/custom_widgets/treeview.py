from typing import Iterable
from dataclasses import dataclass

from PyQt5.QtGui import (
    QIcon, QColor, QStandardItem, 
    QStandardItemModel, QMouseEvent, QFont,
    QPainter, QPalette, QFontMetrics
)
from PyQt5.QtCore import (
    Qt, QRect, pyqtSignal, QEvent, QAbstractItemModel,
    QModelIndex, pyqtProperty, QSize, QPersistentModelIndex, QPoint, QItemSelectionModel
)
from PyQt5.QtWidgets import (
    QTreeView, QWidget, QStyledItemDelegate,
    QAbstractItemView, QStyleOptionViewItem, QStyle
)

from utils import ThemeManagerInstance



ROLE_ID = Qt.UserRole + 1
ROLE_COUNT = Qt.UserRole + 2
ROLE_DISABLED = Qt.UserRole + 3
ROLE_IS_GROUP = Qt.UserRole + 4
ROLE_EDITABLE = Qt.UserRole + 5


@dataclass
class SidebarItem:
    """Data class representing an item in the sidebar."""
    id: str
    title: str
    count: int = 0
    icon: QIcon | None = None
    disabled: bool = False
    editable: bool = True


def _create_color_property(private_name: str) -> pyqtProperty:
    """Creates a QColor property."""
    def getter(self) -> QColor:
        return getattr(self, private_name)

    def setter(self, color: QColor) -> None:
        setattr(self, private_name, color)
        self.viewport().update()

    return pyqtProperty(QColor, getter, setter)


def _resolve_view_color(view: QWidget | None, attr_name: str) -> QColor | None:
    """Resolves a color from the view's attributes."""
    if view is None:
        return None
    color = getattr(view, attr_name, None)
    if isinstance(color, QColor) and color.isValid():
        return color
    return None


class _DeptDelegate(QStyledItemDelegate):
    """Draws a row: icon + text + badge on the right, selected item in red."""
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the delegate."""
        super().__init__(parent)

        self.row_h = 44
        self.pad_l = 16
        self.pad_r = 16
        self.icon_sz = 20
        self.gap = 10
        self.badge_pad_x = 6
        self.badge_h = 16
        self.radius = 8
        self.badge_font_size = 10
        self.badge_font_weight = QFont.Normal

        self.hover_alpha = 28

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        """Returns the size hint for the item."""
        sz = super().sizeHint(option, index)
        sz.setHeight(self.row_h)
        return sz

    def paint(
            self, 
            painter: QPainter, 
            option: QStyleOptionViewItem, 
            index: QModelIndex
    ) -> None:
        """Paints the item."""
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        is_group = bool(index.data(ROLE_IS_GROUP) or False)
        disabled = bool(index.data(ROLE_DISABLED) or False) or not (
            option.state & QStyle.State_Enabled
        )
        editable_val = index.data(ROLE_EDITABLE)
        is_editable = True if editable_val is None else bool(editable_val)
        is_selected = bool(option.state & QStyle.State_Selected)
        is_hover = bool(option.state & QStyle.State_MouseOver)
        palette = option.palette
        view = self.parent()
        highlight = palette.color(QPalette.Highlight)
        hover_color = _resolve_view_color(view, "hoverBackgroundColor") or palette.color(
            QPalette.AlternateBase
        )

        # Rounded background only for items (not for the group)
        r = option.rect
        if view is not None:
            # Draw background for the full width of the viewport, 
            # without clipping (removes artifacts during resize)
            r = QRect(
                0,
                option.rect.top(),
                view.viewport().width(),
                option.rect.height(),
            )
        if not is_group and not disabled:
            if is_selected:
                painter.setBrush(highlight)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(r, self.radius, self.radius)
            elif is_hover:
                painter.setBrush(hover_color)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(r, self.radius, self.radius)

        # Content
        x = option.rect.left() + self.pad_l
        y = option.rect.top()
        h = option.rect.height()
        
        right_edge = option.rect.right() - self.pad_r

        # Text colors
        # Default color if nothing matched
        text_color = palette.color(QPalette.WindowText)

        if disabled:
            text_color = _resolve_view_color(view, "disabledTextColor") or palette.color(
                QPalette.Disabled, QPalette.Text
            )
        elif is_group:
            if is_hover:
                c = _resolve_view_color(view, "groupTextHoverColor")
                if c: text_color = c
            else:
                c = _resolve_view_color(view, "groupTextColor")
                if c: text_color = c
        else:
            if is_selected:
                text_color = _resolve_view_color(
                    view, "itemTextSelectedColor"
                ) or palette.color(QPalette.HighlightedText)
            elif is_hover:
                text_color = _resolve_view_color(view, "itemTextHoverColor") or palette.color(
                    QPalette.Text
                )
            else:
                text_color = _resolve_view_color(view, "itemTextColor") or palette.color(
                    QPalette.Text
                )

        # Icon
        icon_rect = QRect(x, y + (h - self.icon_sz) // 2, self.icon_sz, self.icon_sz)
        icon_drawn = False
        if is_group:
            # Take the icon from widget properties (set via QSS)
            icon = QIcon()
            if is_hover and not disabled:
                icon = view.groupIconHover
            
            if icon.isNull():
                icon = view.groupIcon

            if not icon.isNull():
                tree = option.widget if isinstance(option.widget, QTreeView) else None
                if tree and tree.isExpanded(index):
                    painter.save()
                    center = icon_rect.center()
                    painter.translate(center)
                    painter.rotate(180)
                    painter.translate(-center)
                    icon.paint(painter, icon_rect, Qt.AlignCenter)
                    painter.restore()
                else:
                    icon.paint(painter, icon_rect, Qt.AlignCenter)
                icon_drawn = True
        else:
            icon = index.data(Qt.DecorationRole)
            if isinstance(icon, QIcon):
                mode = QIcon.Disabled if disabled else QIcon.Normal
                icon.paint(painter, icon_rect, Qt.AlignCenter, mode=mode)
                icon_drawn = True

        x += self.icon_sz + self.gap

        # Edit Button (only for selected items)
        edit_btn_w = 0
        if is_selected and not is_group and not disabled and is_editable:
            edit_icon = QIcon()
            if view and hasattr(view, "get_edit_icon"):
                edit_icon = view.get_edit_icon(index)

            if not edit_icon.isNull():
                edit_btn_w = self.icon_sz
                edit_rect = QRect(
                    right_edge - edit_btn_w,
                    y + (h - edit_btn_w) // 2,
                    edit_btn_w,
                    edit_btn_w
                )
                
                mode = QIcon.Normal
                edit_icon.paint(painter, edit_rect, Qt.AlignCenter, mode=mode)
                
                # Shift right edge for badge/text
                right_edge -= (edit_btn_w + self.gap)

        # Badge on the right (only for items)
        badge_w = 0
        count = index.data(ROLE_COUNT)
        if (count is not None) and (not is_group):
            count_str = str(int(count))

            # Use font from options, change only size
            badge_font = option.font
            if badge_font.pointSize() != self.badge_font_size:
                badge_font = QFont(badge_font)
                badge_font.setPointSize(self.badge_font_size)
                badge_font.setWeight(self.badge_font_weight)

            fm_b = QFontMetrics(badge_font)
            badge_w = max(32, fm_b.horizontalAdvance(count_str) + self.badge_pad_x * 2)

            badge_rect = QRect(
                right_edge - badge_w,
                y + (h - self.badge_h) // 2,
                badge_w,
                self.badge_h,
            )

            if is_selected and not disabled:
                badge_bg = (
                    _resolve_view_color(view, "badgeBackgroundSelectedColor")
                    or palette.color(QPalette.HighlightedText)
                )
            elif is_hover and not disabled:
                badge_bg = _resolve_view_color(view, "badgeBackgroundHoverColor") or palette.color(
                    QPalette.AlternateBase
                )
            else:
                badge_bg = _resolve_view_color(view, "badgeBackgroundColor") or QColor(
                    Qt.transparent
                )
            painter.setBrush(badge_bg)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(badge_rect, self.badge_h // 2, self.badge_h // 2)

            painter.setFont(badge_font)
            if disabled:
                badge_text = _resolve_view_color(view, "disabledTextColor") or palette.color(
                    QPalette.Disabled, QPalette.Text
                )
            elif is_selected and not disabled:
                badge_text = (
                    _resolve_view_color(view, "badgeTextSelectedColor")
                    or palette.color(QPalette.Highlight)
                )
            elif is_hover and not disabled:
                badge_text = _resolve_view_color(view, "badgeTextHoverColor") or palette.color(
                    QPalette.Text
                )
            else:
                badge_text = _resolve_view_color(view, "badgeTextColor") or palette.color(
                    QPalette.Text
                )
            painter.setPen(badge_text)

            # Calculate text width
            text_width = fm_b.horizontalAdvance(count_str)

            # Get font metrics for precise vertical centering
            font_ascent = fm_b.ascent()    # height from baseline to top of characters
            font_descent = fm_b.descent()  # height from baseline to bottom of characters

            # Calculate baseline position for ideal vertical centering
            baseline_y = badge_rect.top() + (badge_rect.height() + font_ascent - font_descent) // 2
            text_x = badge_rect.left() + (badge_rect.width() - text_width) // 2

            # Draw text with correct positioning
            painter.drawText(text_x, baseline_y, count_str)
            
            # Shift right edge for text
            right_edge -= (badge_w + self.gap)

        # Text (with elide so it doesn't overlap the badge)
        title = str(index.data(Qt.DisplayRole) or "")
        font = QFont(option.font)
        font.setPointSize(10)
        if is_selected and not is_group and not disabled:
            font.setWeight(QFont.Bold)
        painter.setFont(font)
        painter.setPen(text_color)

        text_right = right_edge
        text_rect = QRect(x, y, max(0, text_right - x), h)

        fm = QFontMetrics(font)
        elided = fm.elidedText(title, Qt.ElideMiddle, text_rect.width())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, elided)

        painter.restore()


class SidebarBlock(QTreeView):
    """
    QTreeView that can be promoted in Designer.
    Dynamically load items via set_items().
    """
    itemActivatedById = pyqtSignal(str)  # emits id on click/enter
    editItemClicked = pyqtSignal(str)    # emits id on edit button click

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the sidebar block."""
        super().__init__(parent)

        self._model = QStandardItemModel(self)
        self.setModel(self._model)

        self.setHeaderHidden(True)
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)

        self.setItemDelegate(_DeptDelegate(self))

        # Map id -> item for fast updates
        self._items_by_id: dict[str, QStandardItem] = {}
        self._active_id: str | None = None
        
        self.edit_icons = {
            "light": {"default": None, "hover": None, "pressed": None, "disabled": None},
            "dark": {"default": None, "hover": None, "pressed": None, "disabled": None}
        }
        self._edit_hovered_idx = QPersistentModelIndex()
        self._edit_pressed_idx = QPersistentModelIndex()

        self.clicked.connect(self._on_clicked)
        if self.selectionModel():
            self.selectionModel().currentChanged.connect(self._on_current_changed)
        self.collapsed.connect(self._on_group_collapsed)
        self.expanded.connect(self._on_group_expanded)
        ThemeManagerInstance.themeChanged.connect(self._on_theme_changed)
        # Initialization of private attributes for properties
        self._badge_background_color = QColor()
        self._badge_text_color = QColor()
        self._badge_background_selected_color = QColor()
        self._badge_text_selected_color = QColor()
        self._badge_background_hover_color = QColor()
        self._badge_text_hover_color = QColor()
        self._disabled_text_color = QColor()
        self._hover_background_color = QColor()
        self._group_text_color = QColor()
        self._group_text_hover_color = QColor()
        self._item_text_color = QColor()
        self._item_text_hover_color = QColor()
        self._item_text_selected_color = QColor()
        self._group_icon = QIcon()
        self._group_icon_hover = QIcon()

    # Creating properties via factory
    badgeBackgroundColor = _create_color_property("_badge_background_color")
    badgeTextColor = _create_color_property("_badge_text_color")
    badgeBackgroundSelectedColor = _create_color_property("_badge_background_selected_color")
    badgeTextSelectedColor = _create_color_property("_badge_text_selected_color")
    badgeBackgroundHoverColor = _create_color_property("_badge_background_hover_color")
    badgeTextHoverColor = _create_color_property("_badge_text_hover_color")
    disabledTextColor = _create_color_property("_disabled_text_color")
    hoverBackgroundColor = _create_color_property("_hover_background_color")
    groupTextColor = _create_color_property("_group_text_color")
    groupTextHoverColor = _create_color_property("_group_text_hover_color")
    itemTextColor = _create_color_property("_item_text_color")
    itemTextHoverColor = _create_color_property("_item_text_hover_color")
    itemTextSelectedColor = _create_color_property("_item_text_selected_color")

    @pyqtProperty(QIcon)
    def groupIcon(self) -> QIcon:
        """Returns the group icon."""
        return self._group_icon

    @groupIcon.setter
    def groupIcon(self, icon: QIcon) -> None:
        """Sets the group icon."""
        self._group_icon = icon
        self.viewport().update()

    @pyqtProperty(QIcon)
    def groupIconHover(self) -> QIcon:
        """Returns the hover group icon."""
        return self._group_icon_hover

    @groupIconHover.setter
    def groupIconHover(self, icon: QIcon) -> None:
        """Sets the hover group icon."""
        self._group_icon_hover = icon
        self.viewport().update()

    # ---------- Public API ----------
    def clear_items(self) -> None:
        """Clears all items from the sidebar."""
        self._model.clear()
        self._model.setHorizontalHeaderLabels([""])
        self._items_by_id.clear()
        self._active_id = None

    @staticmethod
    def _normalize_id(value) -> str:
        """Normalizes item identifiers for consistent internal lookups."""
        return str(value)

    def set_items(
        self,
        items: Iterable[SidebarItem],
        group_title: str | None = None,
        group_icon: QIcon | None = None,
        expand_group: bool = True,
    ) -> None:
        """
        Completely reload the list.
        If group_title is set, create one "group" at the top.

        Args:
            items: An iterable of SidebarItem objects.
            group_title: The title of the group (optional).
            group_icon: The icon for the group (optional).
            expand_group: Whether to expand the group by default.
        """
        previous_active_id = self._active_id
        current_index = self.currentIndex()
        if current_index.isValid():
            current_id = current_index.data(ROLE_ID)
            if current_id is not None:
                previous_active_id = self._normalize_id(current_id)

        self.clear_items()

        parent_item = self._model.invisibleRootItem()

        if group_title is not None:
            grp = QStandardItem(group_icon or QIcon(), group_title)
            grp.setData(True, ROLE_IS_GROUP)
            grp.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            parent_item.appendRow(grp)
            parent_item = grp

        for it in items:
            std = QStandardItem(it.icon or QIcon(), it.title)
            std.setData(it.id, ROLE_ID)
            std.setData(int(it.count), ROLE_COUNT)
            std.setData(bool(it.disabled), ROLE_DISABLED)
            std.setData(bool(it.editable), ROLE_EDITABLE)

            if it.disabled:
                std.setFlags(Qt.NoItemFlags)
            else:
                std.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            parent_item.appendRow(std)
            self._items_by_id[self._normalize_id(it.id)] = std

        if group_title is not None and expand_group:
            self.expand(self._model.index(0, 0))

        selected_index = None
        if previous_active_id:
            selected_item = self._items_by_id.get(previous_active_id)
            if selected_item:
                selected_index = selected_item.index()

        if selected_index is None:
            # Automatic selection of the first item
            if group_title is not None:
                group_idx = self._model.index(0, 0)
                if self._model.rowCount(group_idx) > 0:
                    selected_index = self._model.index(0, 0, group_idx)
            elif self._model.rowCount() > 0:
                selected_index = self._model.index(0, 0)

        if selected_index and selected_index.isValid():
            selection_model = self.selectionModel()
            if selection_model:
                selection_model.setCurrentIndex(
                    selected_index,
                    QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
                )
            else:
                self.setCurrentIndex(selected_index)

            selected_id = selected_index.data(ROLE_ID)
            if selected_id is not None:
                self._active_id = self._normalize_id(selected_id)
                self.itemActivatedById.emit(str(selected_id))

            # If there is a group, ensure it is visible (didn't scroll out of view due to scrolling to child)
            if group_title is not None:
                self.updateGeometry()
                self.verticalScrollBar().setValue(0)

    def update_count(self, id: str, count: int) -> None:
        """Updates the count badge for a specific item."""
        item = self._items_by_id.get(self._normalize_id(id))
        if not item:
            return
        item.setData(int(count), ROLE_COUNT)
        # ask view to repaint this row
        idx = item.index()
        self.viewport().update(self.visualRect(idx))

    def set_selected(self, id: str) -> None:
        """Selects an item by its ID."""
        normalized_id = self._normalize_id(id)
        item = self._items_by_id.get(normalized_id)
        if not item:
            return
        selection_model = self.selectionModel()
        if selection_model:
            selection_model.setCurrentIndex(
                item.index(),
                QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
        else:
            self.setCurrentIndex(item.index())
        self._active_id = normalized_id
        self.scrollTo(item.index(), QAbstractItemView.PositionAtCenter)

    def get_selected_id(self) -> str | None:
        """Returns the ID of the currently selected item."""
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        return idx.data(ROLE_ID)

    def set_edit_icon_paths(
            self,
            light_default: str | None = None, light_hover: str | None = None, 
            light_pressed: str | None = None, light_disabled: str | None = None,
            dark_default: str | None = None, dark_hover: str | None = None, 
            dark_pressed: str | None = None, dark_disabled: str | None = None
    ) -> None:
        """Sets the edit icon paths for different states and themes."""
        mapping = {
            ("light", "default"): light_default,
            ("light", "hover"): light_hover,
            ("light", "pressed"): light_pressed,
            ("light", "disabled"): light_disabled,
            ("dark", "default"): dark_default,
            ("dark", "hover"): dark_hover,
            ("dark", "pressed"): dark_pressed,
            ("dark", "disabled"): dark_disabled,
        }
        for (theme, state), path in mapping.items():
            self.edit_icons[theme][state] = QIcon(path) if path else None
        self.viewport().update()

    def get_edit_icon(self, index: QModelIndex) -> QIcon:
        """Returns the edit icon for the given index based on state."""
        theme_id = ThemeManagerInstance.current_theme_id
        theme = "light" if theme_id == "0" else "dark"
        
        state = "default"
        # Check if item is disabled (using ROLE_DISABLED as per delegate)
        if index.data(ROLE_DISABLED):
            state = "disabled"
        elif index == self._edit_pressed_idx:
            state = "pressed"
        elif index == self._edit_hovered_idx:
            state = "hover"
            
        icon = self.edit_icons[theme].get(state)
        if not icon or icon.isNull():
            icon = self.edit_icons[theme].get("default")
            
        return icon if icon else QIcon()

    def _is_over_edit_button(self, pos: QPoint, index: QModelIndex) -> bool:
        """Checks if the position is over the edit button of the item."""
        if not index.isValid(): return False
        
        rect = self.visualRect(index)
        pad_r = 16
        icon_sz = 20
        
        right_edge = rect.right() - pad_r
        btn_rect = QRect(
            right_edge - icon_sz,
            rect.top() + (rect.height() - icon_sz) // 2,
            icon_sz,
            icon_sz
        )
        return btn_rect.contains(pos)
    
    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
        self.viewport().update()

    def _on_current_changed(self, current: QModelIndex, previous: QModelIndex) -> None:
        """Keeps active item id in sync with selection model changes."""
        if not current.isValid():
            return
        if current.data(ROLE_IS_GROUP):
            return
        current_id = current.data(ROLE_ID)
        if current_id:
            self._active_id = str(current_id)

    def _remember_active_child_for_group(self, group_index: QModelIndex) -> None:
        """Stores current child selection before group collapse."""
        if not group_index.isValid():
            return

        current_index = self.currentIndex()
        if current_index.isValid() and current_index.parent() == group_index:
            current_id = current_index.data(ROLE_ID)
            if current_id:
                self._active_id = str(current_id)
                return

        selection_model = self.selectionModel()
        if not selection_model:
            return

        for selected_index in selection_model.selectedRows(0):
            if selected_index.parent() == group_index:
                selected_id = selected_index.data(ROLE_ID)
                if selected_id:
                    self._active_id = str(selected_id)
                    return

    def _restore_active_selection_for_group(self, group_index: QModelIndex) -> None:
        """Restores selected child in the expanded group if it was previously active."""
        if not group_index.isValid() or not self._active_id:
            return

        item = self._items_by_id.get(self._normalize_id(self._active_id))
        if not item:
            return

        item_index = item.index()
        if not item_index.isValid() or item_index.parent() != group_index:
            return

        selection_model = self.selectionModel()
        if selection_model:
            selection_model.setCurrentIndex(
                item_index,
                QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
            )
        else:
            self.setCurrentIndex(item_index)

    def _on_group_collapsed(self, index: QModelIndex) -> None:
        """Remembers selected child when a group gets collapsed."""
        if not index.isValid() or not index.data(ROLE_IS_GROUP):
            return
        self._remember_active_child_for_group(index)

    def _on_group_expanded(self, index: QModelIndex) -> None:
        """Restores selected child when a group gets expanded."""
        if not index.isValid() or not index.data(ROLE_IS_GROUP):
            return
        self._restore_active_selection_for_group(index)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events."""
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid():
                is_group = index.data(ROLE_IS_GROUP)
                
                if is_group:
                    # Intercept click on group: only collapse/expand
                    self._remember_active_child_for_group(index)
                    self.setUpdatesEnabled(False)
                    if self.isExpanded(index):
                        self.collapse(index)
                    else:
                        self.expand(index)
                    self.setUpdatesEnabled(True)
                    event.accept()
                    return
                
                # Check edit button press
                is_selected = self.selectionModel().isSelected(index)
                if is_selected and not is_group:
                    editable_val = index.data(ROLE_EDITABLE)
                    is_editable = True if editable_val is None else bool(editable_val)

                    if is_editable and self._is_over_edit_button(event.pos(), index):
                        self._edit_pressed_idx = QPersistentModelIndex(index)
                        self.viewport().update(self.visualRect(index))

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handles mouse release events."""
        if event.button() == Qt.LeftButton:
            if self._edit_pressed_idx.isValid():
                idx = QModelIndex(self._edit_pressed_idx)
                self._edit_pressed_idx = QPersistentModelIndex()
                if idx.isValid():
                    self.viewport().update(self.visualRect(idx))
                    
                    # Check if released over the button
                    if self._is_over_edit_button(event.pos(), idx):
                        id_ = idx.data(ROLE_ID)
                        if id_:
                            self.editItemClicked.emit(str(id_))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles mouse move events for hover effects."""
        index = self.indexAt(event.pos())
        old_hover = self._edit_hovered_idx
        
        if index.isValid():
            is_selected = self.selectionModel().isSelected(index)
            is_group = index.data(ROLE_IS_GROUP)
            if is_selected and not is_group:
                editable_val = index.data(ROLE_EDITABLE)
                is_editable = True if editable_val is None else bool(editable_val)

                if is_editable and self._is_over_edit_button(event.pos(), index):
                    if old_hover != index:
                        self._edit_hovered_idx = QPersistentModelIndex(index)
                        self.viewport().update(self.visualRect(index))
                        if old_hover.isValid():
                            self.viewport().update(self.visualRect(QModelIndex(old_hover)))
                    super().mouseMoveEvent(event)
                    return

        # If not over button or not valid
        if old_hover.isValid():
            self._edit_hovered_idx = QPersistentModelIndex()
            self.viewport().update(self.visualRect(QModelIndex(old_hover)))
            
        super().mouseMoveEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handles mouse leave events."""
        if self._edit_hovered_idx.isValid():
            idx = self._edit_hovered_idx
            self._edit_hovered_idx = QPersistentModelIndex()
            self.viewport().update(self.visualRect(QModelIndex(idx)))
        super().leaveEvent(event)

    # ---------- Internal ----------
    def _on_clicked(self, index: QModelIndex) -> None:
        """Handles item click events."""
        id_ = index.data(ROLE_ID)
        if id_:
            self._active_id = str(id_)
            self.itemActivatedById.emit(str(id_))
