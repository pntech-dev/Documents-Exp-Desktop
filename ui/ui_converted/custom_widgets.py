from PyQt5.QtCore import Qt, QRect, pyqtSignal, QModelIndex
from dataclasses import dataclass
from PyQt5.QtGui import QPixmap, QStandardItem, QIcon, QColor, QStandardItemModel, QPainter, QFont, QFontMetrics
from PyQt5.QtWidgets import QPushButton, QAbstractItemView, QLabel, QCheckBox, QLineEdit, QTreeView, QStyle, QStyledItemDelegate

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


class _DeptDelegate(QStyledItemDelegate):
    """Рисует строку: иконка + текст + badge справа, выбранное красным."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.row_h = 44
        self.pad_l = 14
        self.pad_r = 12
        self.icon_sz = 20
        self.gap = 10
        self.badge_pad_x = 10
        self.badge_h = 24
        self.radius = 10

        self.c_hover = QColor(0, 0, 0, 18)
        self.c_sel = QColor("#C43A3A")
        self.c_text = QColor("#1F2937")
        self.c_text_sel = QColor("#FFFFFF")
        self.c_muted = QColor("#9AA0A6")

        self.c_badge_bg = QColor("#F3F4F6")
        self.c_badge_bg_sel = QColor("#FFFFFF")
        self.c_badge_text = QColor("#6B7280")
        self.c_badge_text_sel = QColor("#111827")

    def sizeHint(self, option, index):
        sz = super().sizeHint(option, index)
        sz.setHeight(self.row_h)
        return sz

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)

        is_group = bool(index.data(ROLE_IS_GROUP) or False)
        disabled = bool(index.data(ROLE_DISABLED) or False)
        is_selected = bool(option.state & QStyle.State_Selected)
        is_hover = bool(option.state & QStyle.State_MouseOver)

        # Скруглённый фон только для пунктов (не для группы)
        r = option.rect.adjusted(6, 2, -6, -2)
        if not is_group and not disabled:
            if is_selected:
                painter.setBrush(self.c_sel)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(r, self.radius, self.radius)
            elif is_hover:
                painter.setBrush(self.c_hover)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(r, self.radius, self.radius)

        # Контент
        x = option.rect.left() + self.pad_l
        y = option.rect.top()
        h = option.rect.height()

        # Текстовые цвета
        text_color = (
            self.c_text_sel if (is_selected and not is_group and not disabled)
            else (self.c_muted if disabled else self.c_text)
        )

        # Иконка
        icon = index.data(Qt.DecorationRole)
        if isinstance(icon, QIcon):
            icon_rect = QRect(x, y + (h - self.icon_sz) // 2, self.icon_sz, self.icon_sz)
            mode = QIcon.Disabled if disabled else QIcon.Normal
            icon.paint(painter, icon_rect, Qt.AlignCenter, mode=mode)

        x += self.icon_sz + self.gap

        # Badge справа (только для пунктов)
        badge_w = 0
        count = index.data(ROLE_COUNT)
        if (count is not None) and (not is_group):
            count_str = str(int(count))

            badge_font = QFont(option.font)
            badge_font.setPointSize(max(8, option.font.pointSize() - 1))
            badge_font.setWeight(QFont.DemiBold)

            fm_b = QFontMetrics(badge_font)
            badge_w = max(32, fm_b.horizontalAdvance(count_str) + self.badge_pad_x * 2)

            badge_rect = QRect(
                option.rect.right() - self.pad_r - badge_w,
                y + (h - self.badge_h) // 2,
                badge_w,
                self.badge_h,
            )

            painter.setBrush(self.c_badge_bg_sel if (is_selected and not disabled) else self.c_badge_bg)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(badge_rect, self.badge_h // 2, self.badge_h // 2)

            painter.setFont(badge_font)
            painter.setPen(
                self.c_badge_text_sel if (is_selected and not disabled)
                else (self.c_muted if disabled else self.c_badge_text)
            )
            painter.drawText(badge_rect, Qt.AlignCenter, count_str)

        # Текст (с elide, чтобы не залезал в badge)
        title = str(index.data(Qt.DisplayRole) or "")
        font = QFont(option.font)
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
        self.setIndentation(0)
        self.setRootIsDecorated(False)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setMouseTracking(True)

        self.setItemDelegate(_DeptDelegate(self))

        # Мапа id -> item для быстрых апдейтов
        self._items_by_id: dict[str, QStandardItem] = {}

        self.clicked.connect(self._on_clicked)

    # ---------- Public API ----------
    def clear_items(self) -> None:
        self._model.clear()
        self._model.setHorizontalHeaderLabels([""])
        self._items_by_id.clear()

    def set_items(
        self,
        items: DeptItem,
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
        self.scrollTo(item.index(), QAbstractItemView.PositionAtCenter)

    def get_selected_id(self) -> str | None:
        idx = self.currentIndex()
        if not idx.isValid():
            return None
        return idx.data(ROLE_ID)
    
    # ---------- Internal ----------
    def _on_clicked(self, index: QModelIndex) -> None:
        id_ = index.data(ROLE_ID)
        if id_:
            self.itemActivatedById.emit(str(id_))