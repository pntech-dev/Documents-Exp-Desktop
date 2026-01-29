from dataclasses import dataclass
from typing import Iterable
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QModelIndex, pyqtProperty
from PyQt5.QtWidgets import QPushButton, QAbstractItemView, QLabel, QCheckBox, QLineEdit, QTreeView, QStyle, QStyledItemDelegate
from PyQt5.QtGui import QPixmap,QStandardItem, QColor, QIcon, QStandardItemModel, QPainter, QFont, QFontMetrics, QPalette, QTransform

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


"""=== Labels ==="""

class LogoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)


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
                pix = QPixmap(path)
                if not pix.isNull():
                    self.icons[state][mode] = pix.scaled(
                        self.icon_size, self.icon_size,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )

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
            pix = self.icons["disabled"][theme]
        elif self._focus:
            pix = self.icons["focus"][theme]
        elif self._hover:
            pix = self.icons["hover"][theme]
        else:
            pix = self.icons["default"][theme]

        if pix is None:
            self.icon_label.clear()
        else:
            self.icon_label.setPixmap(pix)


    def _on_theme_changed(self, theme_id):
        self._update_icon()


"""=== Sidebar Block ==="""

ROLE_ID = Qt.UserRole + 1
ROLE_COUNT = Qt.UserRole + 2
ROLE_DISABLED = Qt.UserRole + 3
ROLE_IS_GROUP = Qt.UserRole + 4


@dataclass
class DeptItem:
    id: str
    title: str
    count: int = 0
    icon: QIcon = None
    disabled: bool = False


def _create_color_property(private_name: str) -> pyqtProperty:
    """A factory for creating QColor pyqtProperty."""
    def getter(self) -> QColor:
        return getattr(self, private_name)

    def setter(self, color: QColor) -> None:
        setattr(self, private_name, color)
        self.viewport().update()

    return pyqtProperty(QColor, getter, setter)


def _resolve_view_color(view, attr_name: str) -> QColor | None:
    if view is None:
        return None
    color = getattr(view, attr_name, None)
    if isinstance(color, QColor) and color.isValid():
        return color
    return None


class _DeptDelegate(QStyledItemDelegate):
    """Рисует строку: иконка + текст + badge справа, выбранное красным."""
    def __init__(self, parent=None):
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

    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        sz.setHeight(self.row_h)
        return sz

    def paint(self, painter, option, index):
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

        # Скруглённый фон только для пунктов (не для группы)
        r = option.rect
        if view is not None:
            # Рисуем фон на всю ширину viewport, без клиппинга (убирает артефакты при ресайзе)
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

        # Контент
        x = option.rect.left() + self.pad_l
        y = option.rect.top()
        h = option.rect.height()

        # Текстовые цвета
        # Дефолтный цвет, если ничего не подошло
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

        # Иконка
        icon_rect = QRect(x, y + (h - self.icon_sz) // 2, self.icon_sz, self.icon_sz)
        icon_drawn = False
        if is_group:
            # Берем иконку из свойств виджета (установленных через QSS)
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

                # Badge справа (только для пунктов)
        badge_w = 0
        count = index.data(ROLE_COUNT)
        if (count is not None) and (not is_group):
            count_str = str(int(count))

            # Используем шрифт из опций, меняем только размер
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
            
            # ИСПРАВЛЕННОЕ ЦЕНТРИРОВАНИЕ ТЕКСТА
            # Вычисляем ширину текста
            text_width = fm_b.horizontalAdvance(count_str)
            
            # Получаем метрики шрифта для точного вертикального центрирования
            font_ascent = fm_b.ascent()    # высота от базовой линии до верха символов
            font_descent = fm_b.descent()  # высота от базовой линии до низа символов
            
            # Вычисляем позицию базовой линии для идеального вертикального центрирования
            baseline_y = badge_rect.top() + (badge_rect.height() + font_ascent - font_descent) // 2
            text_x = badge_rect.left() + (badge_rect.width() - text_width) // 2
            
            # Рисуем текст с правильным позиционированием
            painter.drawText(text_x, baseline_y, count_str)

        # Текст (с elide, чтобы не залезал в badge)
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
    QTreeView, который можно promote'нуть в Designer.
    Динамически загружаешь элементы через set_items().
    """
    itemActivatedById = pyqtSignal(str)  # по клику/enter отдаёт id

    def __init__(self, parent=None):
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

        # Мапа id -> item для быстрых апдейтов
        self._items_by_id: dict[str, QStandardItem] = {}
        self._active_id: str | None = None

        self.clicked.connect(self._on_clicked)
        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
        # Инициализация приватных атрибутов для свойств
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

    # Создание свойств через фабрику
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
        return self._group_icon

    @groupIcon.setter
    def groupIcon(self, icon: QIcon) -> None:
        self._group_icon = icon
        self.viewport().update()

    @pyqtProperty(QIcon)
    def groupIconHover(self) -> QIcon:
        return self._group_icon_hover

    @groupIconHover.setter
    def groupIconHover(self, icon: QIcon) -> None:
        self._group_icon_hover = icon
        self.viewport().update()

    # ---------- Public API ----------
    def clear_items(self) -> None:
        self._model.clear()
        self._model.setHorizontalHeaderLabels([""])
        self._items_by_id.clear()
        self._active_id = None

    def set_items(
        self,
        items: Iterable[DeptItem],
        group_title: str | None = None,
        group_icon: QIcon | None = None,
        expand_group: bool = True,
    ) -> None:
        """
        Полностью перезалить список.
        Если group_title задан – делаем одну “группу” сверху.
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

        # Автоматический выбор первого элемента
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
            
            # Если есть группа, убедимся, что она видна (не уехала за пределы из-за скролла к ребенку)
            if group_title is not None:
                self.updateGeometry()
                self.scrollTo(self._model.index(0, 0), QAbstractItemView.PositionAtTop)

    def update_count(self, id: str, count: int) -> None:
        item = self._items_by_id.get(id)
        if not item:
            return
        item.setData(int(count), ROLE_COUNT)
        # попросим view перерисовать эту строку
        idx = item.index()
        self.viewport().update(self.visualRect(idx))

    def set_selected(self, id: str) -> None:
        item = self._items_by_id.get(id)
        if not item:
            return
        self.setCurrentIndex(item.index())
        self._active_id = id
        self.scrollTo(item.index(), QAbstractItemView.PositionAtCenter)

    def get_selected_id(self) -> str | None:
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        return idx.data(ROLE_ID)
    
    def _on_theme_changed(self, theme_id: str) -> None:
        self.viewport().update()
    
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            if index.isValid() and index.data(ROLE_IS_GROUP):
                # Перехватываем клик по группе: только сворачиваем/разворачиваем
                self.setUpdatesEnabled(False)
                if self.isExpanded(index):
                    self.collapse(index)
                else:
                    self.expand(index)
                    # Восстанавливаем выделение, если активный элемент внутри этой группы
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
        id_ = index.data(ROLE_ID)
        if id_:
            self._active_id = str(id_)
            self.itemActivatedById.emit(str(id_))