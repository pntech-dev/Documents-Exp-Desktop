from PyQt5.QtCore import (
    Qt, QEvent, QPoint, QPropertyAnimation,
    QEasingCurve, QRect, QSize, pyqtSignal, pyqtProperty
)
from PyQt5.QtGui import (
    QPainter, QPainterPath, QTransform,
    QPixmap, QIcon, QFontMetrics
)
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QFrame, QScrollArea,
    QSizePolicy, QApplication
)

from utils import ThemeManagerInstance


# ---------------------------------------------------------------------------
# Arrow label with rotation animation
# ---------------------------------------------------------------------------

class _ArrowLabel(QLabel):
    """Renders a pixmap rotated by an animated angle."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self._angle: float = 0.0
        self._source: QPixmap | None = None

    def set_source(self, pixmap: QPixmap) -> None:
        """Sets the source pixmap to rotate."""
        self._source = pixmap
        self._repaint()

    @pyqtProperty(float)
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        self._angle = value
        self._repaint()

    def _repaint(self) -> None:
        if self._source is None:
            return
        rotated = self._source.transformed(
            QTransform().rotate(self._angle),
            Qt.SmoothTransformation
        )
        result = QPixmap(self.size())
        result.fill(Qt.transparent)
        p = QPainter(result)
        x = (self.width() - rotated.width()) // 2
        y = (self.height() - rotated.height()) // 2
        p.drawPixmap(x, y, rotated)
        p.end()
        self.setPixmap(result)


# ---------------------------------------------------------------------------
# Single item in the dropdown list
# ---------------------------------------------------------------------------

class _ComboBoxItem(QWidget):
    """A single selectable row in the dropdown popup."""

    clicked = pyqtSignal(str, object)

    def __init__(
        self,
        text: str,
        user_data: object = None,
        parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._user_data = user_data
        self._hovered = False

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)

        self._label = QLabel(text, self)
        self._label.setObjectName("comboItemLabel")
        layout.addWidget(self._label)

    def set_hovered(self, hovered: bool) -> None:
        """Updates the hovered state and refreshes styling."""
        self._hovered = hovered
        self.setProperty("hovered", "true" if hovered else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._text, self._user_data)

    def enterEvent(self, event) -> None:
        self.set_hovered(True)

    def leaveEvent(self, event) -> None:
        self.set_hovered(False)


# ---------------------------------------------------------------------------
# Floating dropdown popup
# ---------------------------------------------------------------------------

class _ComboBoxPopup(QFrame):
    """Frameless popup window containing the list of combo box items."""

    item_selected = pyqtSignal(str, object)

    _MAX_VISIBLE_ITEMS = 6
    _ITEM_HEIGHT = 42       # item height + spacing
    _CONTAINER_PADDING = 8  # top + bottom padding inside container

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            parent,
            Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("ComboBoxPopup")

        self._items: list[_ComboBoxItem] = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._container = QFrame(self)
        self._container.setObjectName("comboPopupContainer")
        self._container.setAttribute(Qt.WA_StyledBackground, True)

        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(4, 4, 4, 4)
        container_layout.setSpacing(0)

        self._scroll = QScrollArea(self._container)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setObjectName("comboPopupScroll")

        self._list_widget = QWidget()
        self._list_widget.setObjectName("comboPopupList")
        self._list_widget.setAttribute(Qt.WA_StyledBackground, True)

        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(2)

        self._scroll.setWidget(self._list_widget)
        container_layout.addWidget(self._scroll)
        outer.addWidget(self._container)

    def add_item(self, text: str, user_data: object = None) -> None:
        """Appends an item to the dropdown list."""
        item = _ComboBoxItem(text, user_data, self._list_widget)
        item.clicked.connect(self._on_item_clicked)
        self._list_layout.addWidget(item)
        self._items.append(item)

    def clear_items(self) -> None:
        """Removes all items from the dropdown list."""
        for item in self._items:
            item.deleteLater()
        self._items.clear()

    def show_below(self, widget: QWidget, min_width: int) -> None:
        """Positions and shows the popup directly below the given widget."""
        pos = widget.mapToGlobal(QPoint(0, widget.height() + 4))

        visible = min(len(self._items), self._MAX_VISIBLE_ITEMS)
        popup_height = visible * self._ITEM_HEIGHT + self._CONTAINER_PADDING

        self.setFixedWidth(max(min_width, 120))
        self.setFixedHeight(popup_height)
        self._scroll.setFixedHeight(popup_height - self._CONTAINER_PADDING)

        self.move(pos)
        self.show()
        self.raise_()

    def _on_item_clicked(self, text: str, user_data: object) -> None:
        self.item_selected.emit(text, user_data)
        self.hide()


# ---------------------------------------------------------------------------
# Public ComboBox widget
# ---------------------------------------------------------------------------

class ComboBox(QWidget):
    """
    Custom combo box widget with animated arrow rotation and themed dropdown.

    Provides a drop-in replacement for QComboBox with full QSS theme support
    and smooth open/close arrow animation.

    Signals:
        currentTextChanged(str): Emitted when the selected text changes.
        currentIndexChanged(int): Emitted when the selected index changes.

    Usage:
        combo = ComboBox()
        combo.add_item("Option 1")
        combo.add_item("Option 2", user_data={"id": 2})
        combo.current_text_changed.connect(lambda t: print(t))
    """

    currentTextChanged = pyqtSignal(str)
    currentIndexChanged = pyqtSignal(int)

    _ARROW_ANIMATION_DURATION = 180

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("ComboBox")

        self._items: list[tuple[str, object]] = []
        self._current_index: int = -1
        self._placeholder: str = "Select..."
        self._is_open: bool = False
        self._hovered: bool = False

        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(4)

        self._text_label = QLabel(self._placeholder, self)
        self._text_label.setObjectName("comboTextLabel")
        self._text_label.setAttribute(Qt.WA_StyledBackground, True)
        layout.addWidget(self._text_label, 1)

        self._arrow = _ArrowLabel(self)
        self._arrow.setObjectName("comboArrow")
        self._arrow.setAttribute(Qt.WA_StyledBackground, True)
        layout.addWidget(self._arrow, 0, Qt.AlignVCenter)

        # Arrow animation
        self._anim = QPropertyAnimation(self._arrow, b"angle")
        self._anim.setDuration(self._ARROW_ANIMATION_DURATION)
        self._anim.setEasingCurve(QEasingCurve.InOutQuad)

        # Popup
        self._popup = _ComboBoxPopup()
        self._popup.item_selected.connect(self._on_item_selected)
        self._popup.installEventFilter(self)

        # Theme support
        ThemeManagerInstance.themeChanged.connect(self._on_theme_changed)
        self._load_arrow_icon()
        self._refresh_states()

    # ------------------------------------------------------------------
    # Theme and icon management
    # ------------------------------------------------------------------

    def _load_arrow_icon(self) -> None:
        """Loads the arrow icon for the current theme."""
        theme_id = ThemeManagerInstance.current_theme_id
        theme = "light" if theme_id == "0" else "dark"

        pixmap = QPixmap(f":/icons/{theme}/{theme}/arrow_default.svg")
        if pixmap.isNull():
            pixmap = self._draw_fallback_arrow()

        scaled = pixmap.scaled(12, 12, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._arrow.set_source(scaled)

    def _draw_fallback_arrow(self, size: int = 12) -> QPixmap:
        """Draws a simple triangle arrow as a fallback when the icon is missing."""
        px = QPixmap(size, size)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.white)
        path = QPainterPath()
        m = size * 0.15
        path.moveTo(m, size * 0.35)
        path.lineTo(size - m, size * 0.35)
        path.lineTo(size / 2, size * 0.72)
        path.closeSubpath()
        p.drawPath(path)
        p.end()
        return px

    def _on_theme_changed(self, theme_id: str) -> None:
        """Reloads the arrow icon when the application theme changes."""
        self._load_arrow_icon()

    # ------------------------------------------------------------------
    # State management and QSS property refresh
    # ------------------------------------------------------------------

    def _refresh_states(self) -> None:
        """Updates QSS dynamic properties to reflect the current widget state."""
        self.setProperty("open", "true" if self._is_open else "false")
        self.setProperty("hovered", "true" if self._hovered else "false")
        self.setProperty(
            "empty", "true" if self._current_index == -1 else "false"
        )
        self.style().unpolish(self)
        self.style().polish(self)

        self._text_label.setProperty("open", "true" if self._is_open else "false")
        self._text_label.setProperty("hovered", "true" if self._hovered else "false")
        self._text_label.setProperty(
            "empty", "true" if self._current_index == -1 else "false"
        )
        self.style().unpolish(self._text_label)
        self.style().polish(self._text_label)
        self.update()

    # ------------------------------------------------------------------
    # Popup open / close
    # ------------------------------------------------------------------

    def _open_popup(self) -> None:
        if not self._items or not self.isEnabled():
            return
        self._is_open = True
        self._refresh_states()
        self._animate_arrow(open_=True)

        self._popup.clear_items()
        for text, data in self._items:
            self._popup.add_item(text, data)
        self._popup.show_below(self, self.width())

    def _close_popup(self) -> None:
        self._is_open = False
        self._refresh_states()
        self._animate_arrow(open_=False)
        self._popup.hide()

    def _toggle_popup(self) -> None:
        if self._is_open:
            self._close_popup()
        else:
            self._open_popup()

    def _animate_arrow(self, open_: bool) -> None:
        """Animates the arrow rotation between 0° (closed) and 180° (open)."""
        self._anim.stop()
        self._anim.setStartValue(self._arrow.angle)
        self._anim.setEndValue(180.0 if open_ else 0.0)
        self._anim.start()

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def _on_item_selected(self, text: str, user_data: object) -> None:
        old_index = self._current_index
        for i, (t, _) in enumerate(self._items):
            if t == text:
                self._current_index = i
                break

        self._text_label.setText(text)
        self._is_open = False
        self._animate_arrow(open_=False)
        self._refresh_states()

        if self._current_index != old_index:
            self.currentIndexChanged.emit(self._current_index)
            self.currentTextChanged.emit(text)

    # ------------------------------------------------------------------
    # Qt event overrides
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._toggle_popup()

    def enterEvent(self, event) -> None:
        self._hovered = True
        self._refresh_states()

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self._refresh_states()

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.EnabledChange:
            self._refresh_states()
            self.setCursor(
                Qt.ArrowCursor if not self.isEnabled() else Qt.PointingHandCursor
            )
        super().changeEvent(event)

    def hideEvent(self, event) -> None:
        self._close_popup()
        super().hideEvent(event)

    def eventFilter(self, obj, event) -> bool:
        if obj is self._popup and event.type() == QEvent.Hide:
            if self._is_open:
                self._close_popup()
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Public API (compatible with QComboBox naming conventions)
    # ------------------------------------------------------------------

    def addItem(self, text: str, user_data: object = None) -> None:
        """Appends an item with optional associated data."""
        self._items.append((text, user_data))

    def addItems(self, texts: list[str]) -> None:
        """Appends multiple items by text."""
        for t in texts:
            self.addItem(t)

    def setPlaceholderText(self, text: str) -> None:
        """Sets the placeholder text shown when no item is selected."""
        self._placeholder = text
        if self._current_index == -1:
            self._text_label.setText(text)

    def setCurrentText(self, text: str) -> None:
        """Selects the item matching the given text."""
        for i, (t, _) in enumerate(self._items):
            if t == text:
                self._current_index = i
                self._text_label.setText(text)
                self._refresh_states()
                return

    def setCurrentIndex(self, index: int) -> None:
        """Selects the item at the given index."""
        if 0 <= index < len(self._items):
            self._current_index = index
            self._text_label.setText(self._items[index][0])
            self._refresh_states()

    def currentText(self) -> str:
        """Returns the currently selected text, or an empty string if none."""
        if self._current_index >= 0:
            return self._items[self._current_index][0]
        return ""

    def currentData(self) -> object:
        """Returns the user data associated with the currently selected item."""
        if self._current_index >= 0:
            return self._items[self._current_index][1]
        return None

    def currentIndex(self) -> int:
        """Returns the index of the currently selected item, or -1 if none."""
        return self._current_index

    def count(self) -> int:
        """Returns the total number of items."""
        return len(self._items)

    def itemText(self, index: int) -> str:
        """Returns the text of the item at the given index."""
        if 0 <= index < len(self._items):
            return self._items[index][0]
        return ""

    def itemData(self, index: int) -> object:
        """Returns the user data of the item at the given index."""
        if 0 <= index < len(self._items):
            return self._items[index][1]
        return None

    def clear(self) -> None:
        """Removes all items and resets the selection."""
        self._items.clear()
        self._current_index = -1
        self._text_label.setText(self._placeholder)
        self._refresh_states()
