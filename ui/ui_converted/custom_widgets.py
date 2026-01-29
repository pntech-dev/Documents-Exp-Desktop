from PyQt5.QtCore import Qt, QEvent, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import QPushButton, QLabel, QCheckBox, QLineEdit

from utils import ThemeManagerInstance


"""=== Buttons ==="""

class PrimaryButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class SecondaryButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class TertiaryButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class ThemeButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setCursor(Qt.PointingHandCursor)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

        self.icons = {
            "light": {"default": None, "hover": None, "pressed": None, "disabled": None},
            "dark": {"default": None, "hover": None, "pressed": None, "disabled": None}
        }
        self._hover = False
        self._pressed = False
        self.setIconSize(QSize(24, 24))

    def set_icon_paths(self,
                       light_default=None, light_hover=None, light_pressed=None, light_disabled=None,
                       dark_default=None, dark_hover=None, dark_pressed=None, dark_disabled=None):
        
        def get_icon(path):
            return QIcon(path) if path else None

        self.icons["light"]["default"] = get_icon(light_default)
        self.icons["light"]["hover"] = get_icon(light_hover)
        self.icons["light"]["pressed"] = get_icon(light_pressed)
        self.icons["light"]["disabled"] = get_icon(light_disabled)

        self.icons["dark"]["default"] = get_icon(dark_default)
        self.icons["dark"]["hover"] = get_icon(dark_hover)
        self.icons["dark"]["pressed"] = get_icon(dark_pressed)
        self.icons["dark"]["disabled"] = get_icon(dark_disabled)

        self._update_icon()

    def _update_icon(self):
        theme_id = ThemeManagerInstance().current_theme_id
        theme = "light" if theme_id == "0" else "dark"

        state = "default"
        if not self.isEnabled():
            state = "disabled"
        elif self._pressed:
            state = "pressed"
        elif self._hover:
            state = "hover"

        icon = self.icons[theme].get(state)
        # Если иконки для конкретного состояния нет, берем дефолтную
        if not icon or icon.isNull():
            icon = self.icons[theme].get("default")

        if icon and not icon.isNull():
            self.setIcon(icon)
        else:
            self.setIcon(QIcon())

    def _on_theme_changed(self, theme_id):
        self._update_icon()

    def enterEvent(self, event):
        self._hover = True
        self._update_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self._update_icon()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._update_icon()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self._update_icon()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            self._update_icon()
        super().changeEvent(event)


"""=== Labels ==="""

class LogoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

        self.icons = {"light": None, "dark": None}

    def set_icon_paths(self, light=None, dark=None):
        if light:
            self.icons["light"] = QIcon(light)
        if dark:
            self.icons["dark"] = QIcon(dark)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        theme_id = ThemeManagerInstance().current_theme_id
        theme = "light" if theme_id == "0" else "dark"

        icon = self.icons.get(theme)
        if icon and not icon.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            icon.paint(painter, self.rect(), Qt.AlignCenter)

    def _on_theme_changed(self, theme_id):
        self.update()


class InfoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


class TextButton(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


"""=== Checkboxes ==="""

class ViewPasswordCheckbox(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setCursor(Qt.PointingHandCursor)
        # Hiding the standard checkbox indicator so that only the icon is displayed
        self.setStyleSheet("QCheckBox::indicator { width: 0px; height: 0px; border: none; background: transparent; }")
        
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
        self.stateChanged.connect(self._on_state_changed)

        # Structure: theme -> status (checked/unchecked) -> mode (default/hover/pressed)
        self.icons = {
            "light": {
                "unchecked": {"default": None, "hover": None, "pressed": None, "disabled": None},
                "checked":   {"default": None, "hover": None, "pressed": None, "disabled": None}
            },
            "dark": {
                "unchecked": {"default": None, "hover": None, "pressed": None, "disabled": None},
                "checked":   {"default": None, "hover": None, "pressed": None, "disabled": None}
            }
        }
        self._hover = False
        self._pressed = False
        self.setIconSize(QSize(24, 24))

    def set_icon_paths(self, 
                       light_unchecked=None, light_unchecked_hover=None, light_unchecked_pressed=None, light_unchecked_disabled=None,
                       light_checked=None, light_checked_hover=None, light_checked_pressed=None, light_checked_disabled=None,
                       dark_unchecked=None, dark_unchecked_hover=None, dark_unchecked_pressed=None, dark_unchecked_disabled=None,
                       dark_checked=None, dark_checked_hover=None, dark_checked_pressed=None, dark_checked_disabled=None):
        
        def get_icon(path):
            return QIcon(path) if path else None

        # Light theme
        self.icons["light"]["unchecked"]["default"] = get_icon(light_unchecked)
        self.icons["light"]["unchecked"]["hover"] = get_icon(light_unchecked_hover)
        self.icons["light"]["unchecked"]["pressed"] = get_icon(light_unchecked_pressed)
        self.icons["light"]["unchecked"]["disabled"] = get_icon(light_unchecked_disabled)
        
        self.icons["light"]["checked"]["default"] = get_icon(light_checked)
        self.icons["light"]["checked"]["hover"] = get_icon(light_checked_hover)
        self.icons["light"]["checked"]["pressed"] = get_icon(light_checked_pressed)
        self.icons["light"]["checked"]["disabled"] = get_icon(light_checked_disabled)

        # Dark theme
        self.icons["dark"]["unchecked"]["default"] = get_icon(dark_unchecked)
        self.icons["dark"]["unchecked"]["hover"] = get_icon(dark_unchecked_hover)
        self.icons["dark"]["unchecked"]["pressed"] = get_icon(dark_unchecked_pressed)
        self.icons["dark"]["unchecked"]["disabled"] = get_icon(dark_unchecked_disabled)
        
        self.icons["dark"]["checked"]["default"] = get_icon(dark_checked)
        self.icons["dark"]["checked"]["hover"] = get_icon(dark_checked_hover)
        self.icons["dark"]["checked"]["pressed"] = get_icon(dark_checked_pressed)
        self.icons["dark"]["checked"]["disabled"] = get_icon(dark_checked_disabled)

        self._update_icon()

    def _update_icon(self):
        theme_id = ThemeManagerInstance().current_theme_id
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

    def _on_theme_changed(self, theme_id):
        self._update_icon()

    def _on_state_changed(self, state):
        self._update_icon()

    def enterEvent(self, event):
        self._hover = True
        self._update_icon()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        self._update_icon()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._update_icon()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self._update_icon()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            self._update_icon()
        super().changeEvent(event)


"""=== QLineEdit ==="""

class IconLineEdit(QLineEdit):
    def __init__(self, parent=None):
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
        default_light=None, default_dark=None,
        hover_light=None, hover_dark=None,
        focus_light=None, focus_dark=None,
        disabled_light=None, disabled_dark=None
    ):
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
    def refresh_icons(self):
        self._update_icon()

    # icon placement
    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.icon_label.setGeometry(
            self.left_padding,
            (self.height() - self.icon_size) // 2,
            self.icon_size,
            self.icon_size
        )

    # hover
    def enterEvent(self, event):
        super().enterEvent(event)
        self._hover = True
        self._update_icon()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._hover = False
        self._update_icon()

    # focus
    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._focus = True
        self._update_icon()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._focus = False
        self._update_icon()

    # disabled
    def setDisabled(self, disabled):
        super().setDisabled(disabled)
        self._disabled = disabled
        self._update_icon()


    # State priority + theme-based icon selection
    def _update_icon(self):
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
            self.icon_label.setPixmap(icon.pixmap(self.icon_size, self.icon_size))

    
    def _on_theme_changed(self, theme_id):
        self._update_icon()