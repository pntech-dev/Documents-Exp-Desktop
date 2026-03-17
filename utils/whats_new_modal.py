from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainterPath, QRegion
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.custom_widgets import PrimaryButton
from ui.custom_widgets.modal_window import BaseModalDialog, ShadowContainer


RELEASE_NOTES = {
    "0.2.4": [
        {
            "title": "Стабильность обновления",
            "items": [
                "Добавлена явная обработка отмены скачивания обновления.",
                "Исправлена очистка состояния менеджера обновления после отмены и ошибок скачивания.",
                "Добавлены проверки для сценариев отмены скачивания и корректного завершения состояния менеджера.",
            ],
        },
    ],
}


class RoundedScrollArea(QFrame):
    """QScrollArea с overlay-скроллбаром и скруглёнными углами."""

    RADIUS = 10
    BAR_WIDTH = 10
    BAR_MARGIN_X = 4   # отступ от правого края
    BAR_MARGIN_Y = 8   # отступ сверху/снизу

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("whatsNewContentFrame")

        # Внутренняя QScrollArea без нативного вертикального скроллбара
        self._scroll = QScrollArea(self)
        self._scroll.setObjectName("whatsNewContentScroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.viewport().setObjectName("whatsNewContentViewport")

        # Overlay-скроллбар поверх контента
        self._bar = QScrollBar(Qt.Vertical, self)
        self._bar.setObjectName("whatsNewScrollBar")

        native = self._scroll.verticalScrollBar()
        native.valueChanged.connect(self._bar.setValue)
        native.rangeChanged.connect(self._sync_range)
        self._bar.valueChanged.connect(native.setValue)

        self._update_mask()

    def setWidget(self, widget):
        self._scroll.setWidget(widget)

    def _sync_range(self, min_val, max_val):
        self._bar.setRange(min_val, max_val)
        self._bar.setPageStep(self._scroll.verticalScrollBar().pageStep())
        self._bar.setVisible(max_val > min_val)

    def _update_mask(self):
        """Пиксельная маска для реального клиппинга дочерних виджетов."""
        path = QPainterPath()
        path.addRoundedRect(0.0, 0.0, float(self.width()), float(self.height()),
                            self.RADIUS, self.RADIUS)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._scroll.setGeometry(self.rect())
        self._bar.setGeometry(
            self.width() - self.BAR_WIDTH - self.BAR_MARGIN_X,
            self.BAR_MARGIN_Y,
            self.BAR_WIDTH,
            self.height() - self.BAR_MARGIN_Y * 2,
        )
        self._update_mask()


class WhatsNewDialog(BaseModalDialog):
    def __init__(self, parent=None, version: str = "", notes: list[str] | None = None):
        super().__init__(parent)
        self.notes = notes or RELEASE_NOTES.get(version, [])

        self.container = ShadowContainer(self)
        self.container.setObjectName("whatsNewContainer")
        self.container.setMinimumWidth(640)
        self.container.setMaximumWidth(720)

        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(28, 28, 28, 28)
        container_layout.setSpacing(18)

        header_frame = QFrame()
        header_frame.setObjectName("whatsNewHeader")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(8)

        badge_label = QLabel(f"Версия {version}")
        badge_label.setObjectName("whatsNewBadge")
        badge_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(badge_label, 0, Qt.AlignLeft)

        title_label = QLabel("Что нового")
        title_label.setObjectName("whatsNewTitle")
        header_layout.addWidget(title_label)

        container_layout.addWidget(header_frame)

        content_frame = RoundedScrollArea()

        content_widget = QWidget()
        content_widget.setObjectName("whatsNewContentWidget")
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 28, 20)
        content_layout.setSpacing(18)

        for section in self.notes:
            section_title = QLabel(section["title"])
            section_title.setObjectName("whatsNewSectionTitle")
            content_layout.addWidget(section_title)

            for note in section["items"]:
                item_row = QWidget()
                item_row.setObjectName("whatsNewItem")
                item_layout = QHBoxLayout(item_row)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setSpacing(12)

                bullet = QLabel("•")
                bullet.setObjectName("whatsNewBullet")
                bullet.setAlignment(Qt.AlignTop)

                note_label = QLabel(note)
                note_label.setObjectName("whatsNewItemText")
                note_label.setWordWrap(True)
                note_label.setTextFormat(Qt.PlainText)

                item_layout.addWidget(bullet, 0, Qt.AlignTop)
                item_layout.addWidget(note_label, 1)
                content_layout.addWidget(item_row)

        content_frame.setWidget(content_widget)
        content_frame.setMinimumHeight(320)
        content_frame.setMaximumHeight(420)
        container_layout.addWidget(content_frame)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.addStretch(1)

        continue_button = PrimaryButton()
        continue_button.setText("Продолжить")
        continue_button.setMinimumHeight(42)
        continue_button.clicked.connect(self.accept)
        action_row.addWidget(continue_button)

        container_layout.addLayout(action_row)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
