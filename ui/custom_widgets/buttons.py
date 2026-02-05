from PyQt5.QtGui import (
    QIcon, QMouseEvent, QPaintEvent,
    QPainter, QFontMetrics, QPalette
)
from PyQt5.QtCore import (
    Qt, QEvent, QSize,
    QRect
)
from PyQt5.QtWidgets import (
    QPushButton, QWidget, QLabel,
    QStyleOptionButton, QStyle
)

from utils import ThemeManagerInstance


class _IconCustomButton(QPushButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the button with icon support."""
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

        self.icons = {
            "light": {"default": None, "hover": None, 
                      "pressed": None, "disabled": None},
            "dark": {"default": None, "hover": None, 
                     "pressed": None, "disabled": None}
        }
        self._hover = False
        self._pressed = False

        self.setIconSize(QSize(20, 20))

    def set_icon_paths(self,
                       light_default: str | None = None, light_hover: str | None = None, 
                       light_pressed: str | None = None, light_disabled: str | None = None,
                       dark_default: str | None = None, dark_hover: str | None = None, 
                       dark_pressed: str | None = None, dark_disabled: str | None = None) -> None:
        """
        Sets the icon paths for different states and themes.
        """
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
        # If there is no icon for a specific state, take the default one
        if not icon or icon.isNull():
            icon = self.icons[theme].get("default")

        if icon and not icon.isNull():
            self.setIcon(icon)
        else:
            self.setIcon(QIcon())

    def paintEvent(self, event: QPaintEvent) -> None:
        """Custom paint event to handle icon and text spacing."""
        self.ensurePolished()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        # Clear content to draw background only via style
        original_text = opt.text
        original_icon = opt.icon
        opt.text = ""
        opt.icon = QIcon()

        self.style().drawControl(QStyle.CE_PushButton, opt, painter, self)

        # Restore content
        opt.text = original_text
        opt.icon = original_icon

        # Layout calculations
        spacing = 8
        rect = opt.rect
        
        # Font metrics
        painter.setFont(self.font())
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(opt.text)
        
        icon_size = self.iconSize()
        
        has_text = bool(opt.text)
        
        # Use self.icon() directly to ensure we get the correct icon state
        current_icon = self.icon()
        has_icon = not current_icon.isNull()
        
        total_width = 0
        if has_icon:
            total_width += icon_size.width()
        if has_text:
            total_width += text_width
        if has_icon and has_text:
            total_width += spacing
            
        # Center content
        x = rect.left() + (rect.width() - total_width) // 2
        y_center = rect.top() + rect.height() // 2
        
        # Draw Icon
        if has_icon:
            icon_y = y_center - icon_size.height() // 2
            icon_rect = QRect(x, icon_y, icon_size.width(), icon_size.height())
            
            # Determine mode/state for icon
            mode = QIcon.Disabled if not self.isEnabled() else QIcon.Normal
            state = QIcon.On if self.isChecked() else QIcon.Off
            
            current_icon.paint(painter, icon_rect, Qt.AlignCenter, mode, state)
            
            x += icon_size.width() + spacing
            
        # Draw Text
        if has_text:
            text_rect = QRect(x, rect.top(), text_width, rect.height())
            
            # Use style to draw text to ensure QSS colors (hover, etc.) are applied
            opt.rect = text_rect
            opt.icon = QIcon() # Ensure no icon is drawn by this call
            self.style().drawControl(QStyle.CE_PushButtonLabel, opt, painter, self)

    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
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


class PrimaryButton(_IconCustomButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the primary button."""
        super().__init__(parent=parent)


class SecondaryButton(_IconCustomButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the secondary button."""
        super().__init__(parent=parent)


class TertiaryButton(_IconCustomButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the tertiary button."""
        super().__init__(parent=parent)


class NoFrameButton(_IconCustomButton):
    def __init__(
            self, 
            parent: QWidget | None = None, 
            danger: bool = False
    ) -> None:
        """Initializes the no frame button."""
        super().__init__(parent=parent)
        self.set_danger(danger)

    def set_danger(self, is_danger: bool) -> None:
        self.setProperty("danger", "true" if is_danger else "false")

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.DynamicPropertyChange:
            if event.propertyName() == b"danger":
                self.style().unpolish(self)
                self.style().polish(self)
                self.update()
        super().changeEvent(event)


class TextButton(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the text button."""
        super().__init__(parent=parent)


class ThemeButton(_IconCustomButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the theme button."""
        super().__init__(parent=parent)