from PyQt5.QtGui import (
    QResizeEvent, QFocusEvent, QIcon
)
from PyQt5.QtCore import (
    Qt, QEvent
)
from PyQt5.QtWidgets import (
    QLineEdit, QWidget, QLabel
)

from utils import ThemeManagerInstance



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