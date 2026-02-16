from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, pyqtProperty, QEvent, QSize
from PyQt5.QtGui import QIcon


class Tag(QFrame):
    """
    Обычный тег для отображения и поиска.
    Поддерживает состояние 'active' для выделения при поиске.
    """
    clicked = pyqtSignal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("Tag")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self._text = text
        
        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 2, 8, 2)
        self._layout.setSpacing(0)

        # Label
        self.label = QLabel(text)
        self.label.setObjectName("tagLabel")
        self.label.setAlignment(Qt.AlignCenter)
        self._layout.addWidget(self.label)

    def text(self) -> str:
        return self._text

    def set_active(self, active: bool) -> None:
        """Устанавливает состояние активности тега (например, при поиске)."""
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        
        # Обновляем стиль метки, если он зависит от родителя
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)


class DeletableTag(QFrame):
    """
    Custom tag widget with text and delete button.
    Delete button icons for different states are set via QSS properties.
    """
    deleteRequested = pyqtSignal()

    def __init__(self, text: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("DeletableTag")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 2, 8, 2)
        self._layout.setSpacing(4)

        # Label
        self.label = QLabel(text)
        self.label.setObjectName("tagLabel")
        self._layout.addWidget(self.label)

        # Close Button
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("tagCloseButton")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setFlat(True)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.deleteRequested.emit)
        self.close_btn.installEventFilter(self)
        self._layout.addWidget(self.close_btn)

        # Icon storage
        self._icon_default = QIcon()
        self._icon_hover = QIcon()
        self._icon_pressed = QIcon()
        self._icon_disabled = QIcon()

        # State tracking
        self._btn_hovered = False
        self._btn_pressed = False

    def setText(self, text: str):
        self.label.setText(text)

    def text(self) -> str:
        return self.label.text()

    # --- QProperties for Icons ---

    def getCloseIconDefault(self) -> QIcon:
        return self._icon_default

    def setCloseIconDefault(self, icon: QIcon):
        self._icon_default = icon
        self._update_icon()

    closeIconDefault = pyqtProperty(QIcon, getCloseIconDefault, setCloseIconDefault)

    def getCloseIconHover(self) -> QIcon:
        return self._icon_hover

    def setCloseIconHover(self, icon: QIcon):
        self._icon_hover = icon
        self._update_icon()

    closeIconHover = pyqtProperty(QIcon, getCloseIconHover, setCloseIconHover)

    def getCloseIconPressed(self) -> QIcon:
        return self._icon_pressed

    def setCloseIconPressed(self, icon: QIcon):
        self._icon_pressed = icon
        self._update_icon()

    closeIconPressed = pyqtProperty(QIcon, getCloseIconPressed, setCloseIconPressed)

    def getCloseIconDisabled(self) -> QIcon:
        return self._icon_disabled

    def setCloseIconDisabled(self, icon: QIcon):
        self._icon_disabled = icon
        self._update_icon()

    closeIconDisabled = pyqtProperty(QIcon, getCloseIconDisabled, setCloseIconDisabled)

    # --- Event Handling & Icon Update ---

    def eventFilter(self, obj, event):
        if obj == self.close_btn:
            if event.type() == QEvent.Enter:
                self._btn_hovered = True
                self._update_icon()
            elif event.type() == QEvent.Leave:
                self._btn_hovered = False
                self._btn_pressed = False
                self._update_icon()
            elif event.type() == QEvent.MouseButtonPress:
                if event.button() == Qt.LeftButton:
                    self._btn_pressed = True
                    self._update_icon()
            elif event.type() == QEvent.MouseButtonRelease:
                if event.button() == Qt.LeftButton:
                    self._btn_pressed = False
                    self._update_icon()
            elif event.type() == QEvent.EnabledChange:
                self._update_icon()
        
        return super().eventFilter(obj, event)

    def _update_icon(self):
        icon = self._icon_default

        if not self.close_btn.isEnabled():
            if not self._icon_disabled.isNull():
                icon = self._icon_disabled
        elif self._btn_pressed:
            if not self._icon_pressed.isNull():
                icon = self._icon_pressed
        elif self._btn_hovered:
            if not self._icon_hover.isNull():
                icon = self._icon_hover
        
        self.close_btn.setIcon(icon)
        self.close_btn.setIconSize(QSize(12, 12))


class FilterTag(QFrame):
    """
    Tag filter with support for two states (selected/not selected).
    When clicked, it changes the state and sends a signal.
    """
    toggled = pyqtSignal(bool, str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("FilterTag")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._text = text
        self._is_selected = False
        
        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(12, 2, 12, 2)
        self._layout.setSpacing(0)

        # Label
        self.label = QLabel(text)
        self.label.setObjectName("filterTagLabel")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._layout.addWidget(self.label)

    def text(self) -> str:
        return self._text

    def is_selected(self) -> bool:
        return self._is_selected

    def set_selected(self, selected: bool) -> None:
        if self._is_selected == selected:
            return
        self._is_selected = selected
        self.setProperty("selected", selected)
        self._repolish()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.set_selected(not self._is_selected)
            self.toggled.emit(self._is_selected, self._text)

    def enterEvent(self, event):
        self.setProperty("hovered", True)
        self._repolish()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setProperty("hovered", False)
        self._repolish()
        super().leaveEvent(event)

    def _repolish(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)
