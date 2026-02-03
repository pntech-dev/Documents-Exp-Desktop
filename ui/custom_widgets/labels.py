from PyQt5.QtGui import (
    QIcon, QPaintEvent, QPainter,
    QPalette
)
from PyQt5.QtCore import (
    QSize, Qt, QRect,
    pyqtProperty
)
from PyQt5.QtWidgets import (
    QLabel, QWidget, QStyle, 
    QStyleOption
)


from utils import ThemeManagerInstance



class LogoLabel(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the logo label."""
        super().__init__(parent=parent)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)

        self.icons = {"light": None, "dark": None}

    def set_icon_paths(self, light: str | None = None, dark: str | None = None) -> None:
        """
        Sets the icon paths for light and dark themes.

        Args:
            light: Path to the icon for light theme.
            dark: Path to the icon for dark theme.
        """
        if light:
            self.icons["light"] = QIcon(light)
        if dark:
            self.icons["dark"] = QIcon(dark)
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Paints the logo icon."""
        super().paintEvent(event)
        theme_id = ThemeManagerInstance().current_theme_id
        theme = "light" if theme_id == "0" else "dark"

        icon = self.icons.get(theme)
        if icon and not icon.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            icon.paint(painter, self.rect(), self.alignment())

    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
        self.update()


class InfoLabel(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the info label."""
        super().__init__(parent=parent)


class IconLabel(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the icon label."""
        super().__init__(parent=parent)
        self._icon = QIcon()
        self._icon_size = QSize(20, 20)
        self._spacing = 8
        self._icon_rotation = 0.0

    def getIcon(self) -> QIcon:
        return self._icon

    def setIcon(self, icon: QIcon) -> None:
        self._icon = icon
        self.updateGeometry()
        self.update()

    icon = pyqtProperty(QIcon, getIcon, setIcon)

    def getIconSize(self) -> QSize:
        return self._icon_size

    def setIconSize(self, size: QSize) -> None:
        self._icon_size = size
        self.updateGeometry()
        self.update()

    iconSize = pyqtProperty(QSize, getIconSize, setIconSize)

    def getIconRotation(self) -> float:
        return self._icon_rotation

    def setIconRotation(self, angle: float) -> None:
        self._icon_rotation = angle
        self.update()

    iconRotation = pyqtProperty(float, getIconRotation, setIconRotation)

    def sizeHint(self) -> QSize:
        sh = super().sizeHint()
        if not self._icon.isNull():
            w = sh.width() + self._icon_size.width() + self._spacing
            h = max(sh.height(), self._icon_size.height())
            return QSize(w, h)
        return sh

    def minimumSizeHint(self) -> QSize:
        msh = super().minimumSizeHint()
        if not self._icon.isNull():
            w = msh.width() + self._icon_size.width() + self._spacing
            h = max(msh.height(), self._icon_size.height())
            return QSize(w, h)
        return msh

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background (supports QSS)
        opt = QStyleOption()
        opt.initFrom(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

        rect = self.contentsRect()
        text = self.text()
        
        has_icon = not self._icon.isNull()
        has_text = bool(text)
        
        content_width = 0
        if has_icon:
            content_width += self._icon_size.width()
        if has_text:
            fm = self.fontMetrics()
            content_width += fm.horizontalAdvance(text)
        if has_icon and has_text:
            content_width += self._spacing
            
        align = self.alignment()
        
        # Calculate starting x
        x = rect.left()
        if align & Qt.AlignHCenter:
            x += (rect.width() - content_width) // 2
        elif align & Qt.AlignRight:
            x += rect.width() - content_width
            
        if has_icon:
            icon_rect = QRect(
                x, 
                rect.top() + (rect.height() - self._icon_size.height()) // 2,
                self._icon_size.width(), 
                self._icon_size.height()
            )
            
            painter.save()
            if self._icon_rotation != 0:
                center = icon_rect.center()
                painter.translate(center)
                painter.rotate(self._icon_rotation)
                painter.translate(-center)

            mode = QIcon.Disabled if not self.isEnabled() else QIcon.Normal
            self._icon.paint(painter, icon_rect, Qt.AlignCenter, mode=mode)
            painter.restore()
            
            x += self._icon_size.width() + self._spacing
            
        if has_text:
            text_rect = QRect(x, rect.top(), rect.width() - (x - rect.left()), rect.height())
            
            color = self.palette().color(QPalette.WindowText)
            if not self.isEnabled():
                color = self.palette().color(QPalette.Disabled, QPalette.WindowText)
            
            painter.setPen(color)
            painter.setFont(self.font())
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, text)


class ProfileIconLabel(IconLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the profile icon label."""
        super().__init__(parent)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
        
        self.icons = {
            "guest": {"light": None, "dark": None},
            "auth": {"light": None, "dark": None}
        }
        self._mode = "guest"
        self._custom_avatar = None
        
        # Default size for profile icon
        self.setIconSize(QSize(48, 48))

    def set_icon_paths(
            self,
            guest_light: str | None = None, guest_dark: str | None = None,
            auth_light: str | None = None, auth_dark: str | None = None
            ) -> None:
                       
        """Sets icon paths for guest and auth modes."""
        if guest_light: self.icons["guest"]["light"] = QIcon(guest_light)
        if guest_dark: self.icons["guest"]["dark"] = QIcon(guest_dark)
        if auth_light: self.icons["auth"]["light"] = QIcon(auth_light)
        if auth_dark: self.icons["auth"]["dark"] = QIcon(auth_dark)
        self._update_icon()

    def set_mode(self, mode: str) -> None:
        """Sets the current mode ('guest' or 'auth')."""
        self._mode = mode
        self._update_icon()

    def set_custom_avatar(self, icon: QIcon | None) -> None:
        """Sets a custom avatar for the authorized user using QIcon."""
        self._custom_avatar = icon
        self._update_icon()

    def _update_icon(self) -> None:
        theme_id = ThemeManagerInstance().current_theme_id
        theme = "light" if theme_id == "0" else "dark"
        
        if self._mode == "auth" and self._custom_avatar and not self._custom_avatar.isNull():
            self.setIcon(self._custom_avatar)
            return

        icon = self.icons.get(self._mode, {}).get(theme)
        if icon and not icon.isNull():
            self.setIcon(icon)

    def _on_theme_changed(self, theme_id: str) -> None:
        self._update_icon()