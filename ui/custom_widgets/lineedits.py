from PyQt5.QtGui import (
    QResizeEvent, QFocusEvent, QIcon
)
from PyQt5.QtCore import (
    Qt, QEvent, pyqtSignal
)
from PyQt5.QtWidgets import (
    QLineEdit, QWidget, QLabel, QFrame, QHBoxLayout, QSizePolicy
)

from utils import ThemeManagerInstance
from .tags import DeletableTag



class IconLineEdit(QLineEdit):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the icon line edit."""
        super().__init__(parent)

        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

        # icon settings
        self.icon_size = 20

        # icon storage (each state has light/dark option)
        self.icons = {
            "default":  {"light": None, "dark": None},
            "hover":    {"light": None, "dark": None},
            "focus":    {"light": None, "dark": None},
            "disabled": {"light": None, "dark": None},
        }

        # QLabel for icon
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # margins
        self.left_padding = 16
        self.setTextMargins(self.left_padding + self.icon_size, 0, 0, 0)

        # states
        self._hover = False
        self._focus = False
        self._disabled = False

        self._update_icon()


    # Assign icons for both light/dark themes
    def set_icon_paths(
        self,
        default_light: str | None = None, default_dark: str | None = None,
        hover_light: str | None = None, hover_dark: str | None = None,
        focus_light: str | None = None, focus_dark: str | None = None,
        disabled_light: str | None = None, disabled_dark: str | None = None
    ) -> None:
        """
        Sets icon paths for different states and themes.

        Args:
            default_light: Default icon for light theme.
            default_dark: Default icon for dark theme.
            hover_light: Hover icon for light theme.
            hover_dark: Hover icon for dark theme.
            focus_light: Focus icon for light theme.
            focus_dark: Focus icon for dark theme.
            disabled_light: Disabled icon for light theme.
            disabled_dark: Disabled icon for dark theme.
        """
        mapping = {
            ("default",  "light"): default_light,
            ("default",  "dark"):  default_dark,
            ("hover",    "light"): hover_light,
            ("hover",    "dark"):  hover_dark,
            ("focus",    "light"): focus_light,
            ("focus",    "dark"):  focus_dark,
            ("disabled", "light"): disabled_light,
            ("disabled", "dark"):  disabled_dark,
        }

        for (state, mode), path in mapping.items():
            if path:
                icon = QIcon(path)
                if not icon.isNull():
                    self.icons[state][mode] = icon

        self._update_icon()


    # Reload icons when theme changes
    def refresh_icons(self) -> None:
        """Refreshes the icons."""
        self._update_icon()

    # icon placement
    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handles resize events to reposition the icon."""
        super().resizeEvent(event)

        self.icon_label.setGeometry(
            self.left_padding,
            (self.height() - self.icon_size) // 2,
            self.icon_size,
            self.icon_size
        )

    # hover
    def enterEvent(self, event: QEvent) -> None:
        """Handles mouse enter events."""
        super().enterEvent(event)
        self._hover = True
        self._update_icon()

    def leaveEvent(self, event: QEvent) -> None:
        """Handles mouse leave events."""
        super().leaveEvent(event)
        self._hover = False
        self._update_icon()

    # focus
    def focusInEvent(self, event: QFocusEvent) -> None:
        """Handles focus in events."""
        super().focusInEvent(event)
        self._focus = True
        self._update_icon()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Handles focus out events."""
        super().focusOutEvent(event)
        self._focus = False
        self._update_icon()

    # disabled
    def setDisabled(self, disabled: bool) -> None:
        """Sets the disabled state of the widget."""
        super().setDisabled(disabled)
        self._disabled = disabled
        self._update_icon()


    # State priority + theme-based icon selection
    def _update_icon(self) -> None:
        """Updates the icon based on the current state and theme."""
        theme_id = ThemeManagerInstance().current_theme_id
        theme = "light" if theme_id == "0" else "dark"

        if self._disabled:
            icon = self.icons["disabled"][theme]
        elif self._focus:
            icon = self.icons["focus"][theme]
        elif self._hover:
            icon = self.icons["hover"][theme]
        else:
            icon = self.icons["default"][theme]

        if icon is None:
            self.icon_label.clear()
        else:
            self.icon_label.setPixmap(icon.pixmap(self.icon_size, 
                                                  self.icon_size))


    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
        self._update_icon()


class TagsLineEdit(QFrame):
    """
    Custom widget for entering tags.
    It contains a list of tags, an input field, and a counter.
    """
    tagsChanged = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self._tags = []
        self._max_tags = 5
        
        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 2, 16, 2)
        self._layout.setSpacing(8)
        
        # Line Edit
        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("tagsInputLineEdit")
        self.line_edit.setFrame(False)
        self.line_edit.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.line_edit.installEventFilter(self)
        self.line_edit.textChanged.connect(self._on_text_changed)
        self.line_edit.returnPressed.connect(self._on_return_pressed)
        
        self._layout.addWidget(self.line_edit)
        
        # Counter
        self.counter_label = QLabel(f"0/{self._max_tags}")
        self.counter_label.setObjectName("tagsCounterLabel")
        self.counter_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self._layout.addWidget(self.counter_label)


    def get_tags(self):
        return self._tags

    def add_tag(self, text):
        if len(self._tags) >= self._max_tags:
            return

        if text in self._tags:
             self.line_edit.clear()
             return

        tag = DeletableTag(text)
        tag.deleteRequested.connect(lambda: self.remove_tag(tag))
        
        # Inserting the tag in front of the input field
        idx = self._layout.indexOf(self.line_edit)
        self._layout.insertWidget(idx, tag)
        
        self._tags.append(text)
        self._update_counter()
        self.tagsChanged.emit(self._tags)
        
        if len(self._tags) >= self._max_tags:
            self.line_edit.clear()
            self.line_edit.setPlaceholderText("Достигнут максимум тегов")
            self.line_edit.setEnabled(False)

    def remove_tag(self, tag_widget):
        text = tag_widget.text()
        if text in self._tags:
            self._tags.remove(text)
            self._layout.removeWidget(tag_widget)
            tag_widget.deleteLater()
            self._update_counter()
            self.tagsChanged.emit(self._tags)
            
            if not self.line_edit.isEnabled():
                self.line_edit.setEnabled(True)
                self.line_edit.setPlaceholderText("")
                self.line_edit.setFocus()

    def _on_text_changed(self, text):
        if not text:
            return
            
        if text.endswith(" "):
            tag_text = text.strip()
            if tag_text:
                self.add_tag(tag_text)
            self.line_edit.clear()

    def _on_return_pressed(self):
        text = self.line_edit.text().strip()
        if text:
            self.add_tag(text)
            self.line_edit.clear()

    def _update_counter(self):
        self.counter_label.setText(f"{len(self._tags)}/{self._max_tags}")

    def eventFilter(self, obj, event):
        if obj == self.line_edit:
            if event.type() == QEvent.FocusIn:
                self.setProperty("focused", True)
                self.style().unpolish(self)
                self.style().polish(self)
            elif event.type() == QEvent.FocusOut:
                self.setProperty("focused", False)
                self.style().unpolish(self)
                self.style().polish(self)
            elif event.type() == QEvent.KeyPress:
                # Deleting the last tag by Backspace if the field is empty
                if event.key() == Qt.Key_Backspace and not self.line_edit.text():
                    if self._tags:
                        idx = self._layout.indexOf(self.line_edit)
                        if idx > 0:
                            item = self._layout.itemAt(idx - 1)
                            widget = item.widget()
                            if isinstance(widget, DeletableTag):
                                self.remove_tag(widget)
        
        return super().eventFilter(obj, event)
    
    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)