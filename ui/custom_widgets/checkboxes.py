from PyQt5.QtGui import (
    QIcon, QMouseEvent
)
from PyQt5.QtCore import (
    Qt, QSize, QEvent
)
from PyQt5.QtWidgets import (
    QCheckBox, QWidget
)

from utils import ThemeManagerInstance



class ViewPasswordCheckbox(QCheckBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the view password checkbox."""
        super().__init__(parent=parent)
        self.setCursor(Qt.PointingHandCursor)
        # Hiding the standard checkbox indicator so that only the icon is displayed
        self.setStyleSheet(
            "QCheckBox::indicator { width: 0px; height: 0px; border: none; background: transparent; }"
        )
        
        ThemeManagerInstance.themeChanged.connect(self._on_theme_changed)
        self.stateChanged.connect(self._on_state_changed)

        # Structure: theme -> status (checked/unchecked) -> mode (default/hover/pressed)
        self.icons = {
            "light": {
                "unchecked": {"default": None, "hover": None, 
                              "pressed": None, "disabled": None},
                "checked":   {"default": None, "hover": None, 
                              "pressed": None, "disabled": None}
            },
            "dark": {
                "unchecked": {"default": None, "hover": None, 
                              "pressed": None, "disabled": None},
                "checked":   {"default": None, "hover": None, 
                              "pressed": None, "disabled": None}
            }
        }
        self._hover = False
        self._pressed = False
        self.setIconSize(QSize(24, 24))

    def set_icon_paths(
            self, 
            light_unchecked: str | None = None, 
            light_unchecked_hover: str | None = None, 
            light_unchecked_pressed: str | None = None, 
            light_unchecked_disabled: str | None = None,
            light_checked: str | None = None, 
            light_checked_hover: str | None = None, 
            light_checked_pressed: str | None = None, 
            light_checked_disabled: str | None = None,

            dark_unchecked: str | None = None, 
            dark_unchecked_hover: str | None = None, 
            dark_unchecked_pressed: str | None = None, 
            dark_unchecked_disabled: str | None = None,
            dark_checked: str | None = None, 
            dark_checked_hover: str | None = None, 
            dark_checked_pressed: str | None = None, 
            dark_checked_disabled: str | None = None
        ) -> None:
        """
        Sets icon paths for different states and themes.

        Args:
            light_unchecked: Default unchecked icon for light theme.
            light_unchecked_hover: Hover unchecked icon for light theme.
            light_unchecked_pressed: Pressed unchecked icon for light theme.
            light_unchecked_disabled: Disabled unchecked icon for light theme.
            light_checked: Default checked icon for light theme.
            light_checked_hover: Hover checked icon for light theme.
            light_checked_pressed: Pressed checked icon for light theme.
            light_checked_disabled: Disabled checked icon for light theme.
            dark_unchecked: Default unchecked icon for dark theme.
            dark_unchecked_hover: Hover unchecked icon for dark theme.
            dark_unchecked_pressed: Pressed unchecked icon for dark theme.
            dark_unchecked_disabled: Disabled unchecked icon for dark theme.
            dark_checked: Default checked icon for dark theme.
            dark_checked_hover: Hover checked icon for dark theme.
            dark_checked_pressed: Pressed checked icon for dark theme.
            dark_checked_disabled: Disabled checked icon for dark theme.
        """
        mapping = {
            ("light", "unchecked", "default"): light_unchecked,
            ("light", "unchecked", "hover"): light_unchecked_hover,
            ("light", "unchecked", "pressed"): light_unchecked_pressed,
            ("light", "unchecked", "disabled"): light_unchecked_disabled,
            ("light", "checked", "default"): light_checked,
            ("light", "checked", "hover"): light_checked_hover,
            ("light", "checked", "pressed"): light_checked_pressed,
            ("light", "checked", "disabled"): light_checked_disabled,
            ("dark", "unchecked", "default"): dark_unchecked,
            ("dark", "unchecked", "hover"): dark_unchecked_hover,
            ("dark", "unchecked", "pressed"): dark_unchecked_pressed,
            ("dark", "unchecked", "disabled"): dark_unchecked_disabled,
            ("dark", "checked", "default"): dark_checked,
            ("dark", "checked", "hover"): dark_checked_hover,
            ("dark", "checked", "pressed"): dark_checked_pressed,
            ("dark", "checked", "disabled"): dark_checked_disabled,
        }

        for (theme, state, mode), path in mapping.items():
            self.icons[theme][state][mode] = QIcon(path) if path else None

        self._update_icon()

    def _update_icon(self) -> None:
        """Updates the icon based on the current state and theme."""
        theme_id = ThemeManagerInstance.current_theme_id
        theme = "light" if theme_id == "0" else "dark"
        
        state = "checked" if self.isChecked() else "unchecked"
        
        mode = "default"
        if not self.isEnabled():
            mode = "disabled"
        elif self._pressed:
            mode = "pressed"
        elif self._hover:
            mode = "hover"
            
        icon = self.icons[theme][state].get(mode)
        if not icon or icon.isNull():
            icon = self.icons[theme][state].get("default")
            
        if icon and not icon.isNull():
            self.setIcon(icon)
        else:
            self.setIcon(QIcon())

    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
        self._update_icon()

    def _on_state_changed(self, state: int) -> None:
        """Handles checkbox state change events."""
        self._update_icon()

    def enterEvent(self, event: QEvent) -> None:
        """Handles mouse enter events."""
        self._hover = True
        self._update_icon()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Handles mouse leave events."""
        self._hover = False
        self._update_icon()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events."""
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._update_icon()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handles mouse release events."""
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self._update_icon()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event: QEvent) -> None:
        """Handles widget state change events."""
        if event.type() == QEvent.EnabledChange:
            self._update_icon()
        super().changeEvent(event)