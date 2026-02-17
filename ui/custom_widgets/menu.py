from PyQt5.QtGui import (
    QIcon, QMouseEvent
)
from PyQt5.QtCore import (
    Qt, QEvent
)
from PyQt5.QtWidgets import (
    QMenu, QWidget, QAction,
    QHBoxLayout, QLabel,
    QWidgetAction, QCheckBox, QFrame, QSizePolicy, QVBoxLayout
)

from utils import ThemeManagerInstance



class MenuItemWidget(QWidget):
    def __init__(
            self, 
            text: str, 
            action: QAction, 
            danger: bool = False, 
            checkable: bool = False,
            checked: bool = False,
            parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
        self.action = action
        self.checkable = checkable
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover)
        self.setAttribute(Qt.WA_StyledBackground)
        
        self.setProperty("danger", danger)
        self.setProperty("is_disabled", "true" if not self.isEnabled() else "false")

        self.icons = {
            "light": {"default": None, "hover": None, "pressed": None, "disabled": None},
            "dark": {"default": None, "hover": None, "pressed": None, "disabled": None}
        }
        self._hover = False
        self._pressed = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)
        
        if self.checkable:
            self.checkbox = QCheckBox()
            self.checkbox.setChecked(checked)
            self.checkbox.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.checkbox.setAttribute(Qt.WA_StyledBackground, True)
            self.checkbox.setFocusPolicy(Qt.NoFocus)
            self.checkbox.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(self.checkbox)
            
            # Sync action state
            action.setCheckable(True)
            action.setChecked(checked)
            action.toggled.connect(self.checkbox.setChecked)
        else:
            self.icon_label = QLabel()
            self.icon_label.setFixedSize(20, 20)
            self.icon_label.setScaledContents(True)
            self.icon_label.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(self.icon_label)
        
        self.text_label = QLabel(text)
        self.text_label.setProperty("danger", danger)
        self.text_label.setStyleSheet("background: transparent; border: none; font-size: 12pt;")
        layout.addWidget(self.text_label)
        
        layout.addStretch()

    def set_icon_paths(self,
                       light_default: str | None = None, light_hover: str | None = None, 
                       light_pressed: str | None = None, light_disabled: str | None = None,
                       dark_default: str | None = None, dark_hover: str | None = None, 
                       dark_pressed: str | None = None, dark_disabled: str | None = None) -> None:
        """Sets the icon paths for different states and themes."""
        if self.checkable:
            return

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
            self.icons[theme][state] = QIcon(path) if path else None

        self._update_icon()

    def _update_icon(self) -> None:
        """Updates the icon based on the current state and theme."""
        if self.checkable:
            return

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
        if not icon or icon.isNull():
            icon = self.icons[theme].get("default")

        if icon and not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(20, 20))
        else:
            self.icon_label.clear()

    def _on_theme_changed(self, theme_id: str) -> None:
        self._update_icon()

    def enterEvent(self, event: QEvent) -> None:
        self._hover = True
        self._update_icon()
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)
        # Обновляем стили дочерних элементов (текста)
        self.text_label.style().unpolish(self.text_label)
        self.text_label.style().polish(self.text_label)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._hover = False
        self._update_icon()
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.text_label.style().unpolish(self.text_label)
        self.text_label.style().polish(self.text_label)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._update_icon()
            self.setProperty("pressed", True)
            self.style().unpolish(self)
            self.style().polish(self)
            self.text_label.style().unpolish(self.text_label)
            self.text_label.style().polish(self.text_label)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self._update_icon()
            self.setProperty("pressed", False)
            self.style().unpolish(self)
            self.style().polish(self)
            self.text_label.style().unpolish(self.text_label)
            self.text_label.style().polish(self.text_label)

        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            if self.checkable:
                # Toggle state without triggering (which closes menu)
                self.action.setChecked(not self.action.isChecked())
                return

            self.action.trigger()
            menu = self.parent()
            while menu and not isinstance(menu, QMenu):
                menu = menu.parent()
            if isinstance(menu, QMenu):
                menu.close()
        super().mouseReleaseEvent(event)

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.EnabledChange:
            self.setProperty("is_disabled", "true" if not self.isEnabled() else "false")
            self._update_icon()
            self.style().unpolish(self)
            self.style().polish(self)
            self.text_label.style().unpolish(self.text_label)
            self.text_label.style().polish(self.text_label)
            self.update()
        super().changeEvent(event)


class ThemeAwareMenu(QMenu):
    """A QMenu that updates its actions' icons when the theme changes."""
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        # Enable styling via properties and QSS
        self.setCursor(Qt.PointingHandCursor)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def add_theme_action(
            self,
            text: str,
            light_icon: str | None = None,
            dark_icon: str | None = None,
            danger_action: bool = False,
            checkable: bool = False,
            checked: bool = False,
            callback=None,
            **icon_kwargs
    ) -> QAction:
        """Adds an action with theme-aware icons."""
        
        # Теперь все элементы - это QWidgetAction с MenuItemWidget
        action = QWidgetAction(self)
        widget = MenuItemWidget(text, action, danger=danger_action, checkable=checkable, checked=checked)
        action.setDefaultWidget(widget)

        # Sync enabled state
        def sync_state():
            widget.setEnabled(action.isEnabled())
        action.changed.connect(sync_state)
        sync_state()
        
        # Backward compatibility for simple light/dark icon arguments
        if light_icon and "light_default" not in icon_kwargs:
            icon_kwargs["light_default"] = light_icon
        if dark_icon and "dark_default" not in icon_kwargs:
            icon_kwargs["dark_default"] = dark_icon
            
        widget.set_icon_paths(**icon_kwargs)
            
        if callback:
            action.triggered.connect(callback)
            
        self.addAction(action)
        return action

    def add_section_header(self, text: str) -> QAction:
        """Adds a section header with text and a separator line."""
        action = QWidgetAction(self)
        widget = QWidget()
        widget.setAttribute(Qt.WA_StyledBackground)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(8)
        
        label = QLabel(text)
        label.setObjectName("menuSectionLabel")
        
        # Обертка для линии, чтобы гарантировать вертикальное центрирование
        line_container = QWidget()
        line_layout = QVBoxLayout(line_container)
        line_layout.setContentsMargins(0, 0, 0, 0)
        line_layout.setSpacing(0)
        
        line = QFrame()
        line.setObjectName("menuSectionLine")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        line.setFixedHeight(2)
        
        line_layout.addStretch()
        line_layout.addWidget(line)
        line_layout.addStretch()
        
        layout.addWidget(label)
        layout.addWidget(line_container, 1)
        
        action.setDefaultWidget(widget)
        action.setEnabled(False)
        self.addAction(action)
        return action