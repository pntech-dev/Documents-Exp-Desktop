from typing import Iterable
from dataclasses import dataclass
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QModelIndex, pyqtProperty, QEvent, QSize
from PyQt5.QtGui import (
    QStandardItem, QColor, QIcon, QStandardItemModel, QPainter, QFont, 
    QFontMetrics, QPalette, QMouseEvent, QResizeEvent, QFocusEvent, QPaintEvent
)
from PyQt5.QtWidgets import (
    QPushButton, QAbstractItemView, QLabel, QCheckBox, QLineEdit, QTreeView, 
    QStyle, QStyledItemDelegate, QWidget, QStyleOptionViewItem, QHBoxLayout,
    QStyleOptionButton
)

from utils import ThemeManagerInstance


"""=== Buttons ==="""

class _IconCustomButton(QPushButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the button with icon support."""
        super().__init__(parent=parent)
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
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        # Clear content to draw background only
        original_text = opt.text
        original_icon = opt.icon
        opt.text = ""
        opt.icon = QIcon()

        painter.save()
        self.style().drawControl(QStyle.CE_PushButton, opt, painter, self)
        painter.restore()

        # Restore content
        opt.text = original_text
        opt.icon = original_icon

        # Layout calculations
        spacing = 8
        rect = opt.rect

        # Font
        painter.setFont(self.font())
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(opt.text)
        
        icon_size = self.iconSize()
        
        current_icon = self.icon()
        has_text = bool(opt.text)
        has_icon = not current_icon.isNull()
        
        total_width = 0
        if has_icon:
            total_width += icon_size.width()
        if has_text:
            total_width += text_width
        if has_icon and has_text:
            total_width += spacing
            
        # Center
        x = rect.left() + (rect.width() - total_width) // 2
        
        # Draw Icon
        if has_icon:
            icon_y = rect.top() + (rect.height() - icon_size.height()) // 2
            pixmap = current_icon.pixmap(icon_size, QIcon.Normal, QIcon.Off)
            painter.drawPixmap(x, icon_y, pixmap)
            x += icon_size.width() + spacing
            
        # Draw Text
        if has_text:
            text_rect = QRect(x, rect.top(), text_width, rect.height())
            
            # Color from palette (handles QSS states)
            color = opt.palette.color(QPalette.ButtonText)
            if not self.isEnabled():
                color = opt.palette.color(QPalette.Disabled, QPalette.ButtonText)
            
            painter.setPen(color)
            painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, opt.text)

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


class ThemeButton(_IconCustomButton):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the theme button."""
        super().__init__(parent=parent)


"""=== Labels ==="""

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


class TextButton(QLabel):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the text button."""
        super().__init__(parent=parent)


"""=== Checkboxes ==="""

class ViewPasswordCheckbox(QCheckBox):
    def __init__(self, parent: QWidget | None = None) -> None:
        """Initializes the view password checkbox."""
        super().__init__(parent=parent)
        self.setCursor(Qt.PointingHandCursor)
        # Hiding the standard checkbox indicator so that only the icon is displayed
        self.setStyleSheet(
            "QCheckBox::indicator { width: 0px; height: 0px; border: none; background: transparent; }"
        )
        
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
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

    def set_icon_paths(self, 
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
                       dark_checked_disabled: str | None = None) -> None:
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


"""=== QLineEdit ==="""

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


"""=== Sidebar Block ==="""

ROLE_ID = Qt.UserRole + 1
ROLE_COUNT = Qt.UserRole + 2
ROLE_DISABLED = Qt.UserRole + 3
ROLE_IS_GROUP = Qt.UserRole + 4


@dataclass
class SidebarItem:
    id: str
    title: str
    count: int = 0
    icon: QIcon | None = None
    disabled: bool = False


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
                option.rect.right() - self.pad_r - badge_w,
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

        # Text (with elide so it doesn't overlap the badge)
        title = str(index.data(Qt.DisplayRole) or "")
        font = QFont(option.font)
        if is_selected and not is_group and not disabled:
            font.setWeight(QFont.Bold)
        painter.setFont(font)
        painter.setPen(text_color)

        text_right = option.rect.right() - self.pad_r - (badge_w + 10 if badge_w else 0)
        text_rect = QRect(x, y, max(0, text_right - x), h)

        fm = QFontMetrics(font)
        elided = fm.elidedText(title, Qt.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, elided)

        painter.restore()


class SidebarBlock(QTreeView):
    """
    QTreeView that can be promoted in Designer.
    Dynamically load items via set_items().
    """
    itemActivatedById = pyqtSignal(str)  # emits id on click/enter

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

        self.clicked.connect(self._on_clicked)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
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

            if it.disabled:
                std.setFlags(Qt.NoItemFlags)
            else:
                std.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            parent_item.appendRow(std)
            self._items_by_id[it.id] = std

        if group_title is not None and expand_group:
            self.expand(self._model.index(0, 0))

        # Automatic selection of the first item
        first_index = None
        if group_title is not None:
            group_idx = self._model.index(0, 0)
            if self._model.rowCount(group_idx) > 0:
                first_index = self._model.index(0, 0, group_idx)
        else:
            if self._model.rowCount() > 0:
                first_index = self._model.index(0, 0)

        if first_index and first_index.isValid():
            self.setCurrentIndex(first_index)
            id_ = first_index.data(ROLE_ID)
            if id_:
                self._active_id = str(id_)
                self.itemActivatedById.emit(str(id_))
            
            # If there is a group, ensure it is visible (didn't scroll out of view due to scrolling to child)
            if group_title is not None:
                self.updateGeometry()
                self.verticalScrollBar().setValue(0)

    def update_count(self, id: str, count: int) -> None:
        """Updates the count badge for a specific item."""
        item = self._items_by_id.get(id)
        if not item:
            return
        item.setData(int(count), ROLE_COUNT)
        # ask view to repaint this row
        idx = item.index()
        self.viewport().update(self.visualRect(idx))

    def set_selected(self, id: str) -> None:
        """Selects an item by its ID."""
        item = self._items_by_id.get(id)
        if not item:
            return
        self.setCurrentIndex(item.index())
        self._active_id = id
        self.scrollTo(item.index(), QAbstractItemView.PositionAtCenter)

    def get_selected_id(self) -> str | None:
        """Returns the ID of the currently selected item."""
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        return idx.data(ROLE_ID)
    
    def _on_theme_changed(self, theme_id: str) -> None:
        """Handles theme change events."""
        self.viewport().update()
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events."""
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid() and index.data(ROLE_IS_GROUP):
                # Intercept click on group: only collapse/expand
                self.setUpdatesEnabled(False)
                if self.isExpanded(index):
                    self.collapse(index)
                else:
                    self.expand(index)
                    # Restore selection if the active item is inside this group
                    if self._active_id:
                        item = self._items_by_id.get(self._active_id)
                        if item:
                            idx = item.index()
                            if idx.isValid() and idx.parent() == index:
                                self.setCurrentIndex(idx)
                self.setUpdatesEnabled(True)
                event.accept()
                return
        super().mousePressEvent(event)

    # ---------- Internal ----------
    def _on_clicked(self, index: QModelIndex) -> None:
        """Handles item click events."""
        id_ = index.data(ROLE_ID)
        if id_:
            self._active_id = str(id_)
            self.itemActivatedById.emit(str(id_))