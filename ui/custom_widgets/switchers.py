from PyQt5.QtGui import (
    QColor
)
from PyQt5.QtCore import (
    Qt, QEvent, pyqtSignal, 
    QPropertyAnimation, QEasingCurve, pyqtProperty,
)
from PyQt5.QtWidgets import (
    QWidget, QLabel, QGraphicsDropShadowEffect
)

from utils import ThemeManagerInstance



class ThemeSwitch(QWidget):
    clicked = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        ThemeManagerInstance().themeChanged.connect(self._on_theme_changed)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("themeSwitch")

        # Hover should be stable
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        self._checked = False
        self._hovered = False
        self.setProperty("hovered", False)

        self._track = QWidget(self)
        self._track.setObjectName("themeSwitchTrack")
        self._track.setAttribute(Qt.WA_StyledBackground, True)
        self._track.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self._knob = QWidget(self._track)
        self._knob.setObjectName("themeSwitchKnob")
        self._knob.setAttribute(Qt.WA_StyledBackground, True)
        self._knob.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self._label = QLabel(self._track)
        self._label.setObjectName("themeSwitchLabel")
        self._label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self._label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setOffset(0, 0)
        self._shadow.setBlurRadius(10)
        self._knob.setGraphicsEffect(self._shadow)

        self._pad = 12
        self._gap = 16
        self._knob_pos = 0.0

        self.setMinimumSize(125, 42)

        self._anim = QPropertyAnimation(self, b"knobPos", self)
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

        self._update_ui()

    # ---- qproperty for QSS shadow ----
    def getKnobShadowColor(self) -> QColor:
        return self._shadow.color()

    def setKnobShadowColor(self, color: QColor) -> None:
        self._shadow.setColor(color)

    def getKnobShadowBlur(self) -> float:
        return float(self._shadow.blurRadius())

    def setKnobShadowBlur(self, blur: float) -> None:
        self._shadow.setBlurRadius(float(blur))

    knobShadowColor = pyqtProperty(QColor, getKnobShadowColor, setKnobShadowColor)
    knobShadowBlur = pyqtProperty(float, getKnobShadowBlur, setKnobShadowBlur)

    # ---- knob animation property ----
    def getKnobPos(self) -> float:
        return float(self._knob_pos)

    def setKnobPos(self, v: float) -> None:
        self._knob_pos = float(v)
        self._layout()

    knobPos = pyqtProperty(float, getKnobPos, setKnobPos)

    # ---- public API ----
    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, v: bool) -> None:
        if self._checked == v:
            return
        self._checked = v
        self.clicked.emit(v)

        self._anim.stop()
        self._anim.setStartValue(self._knob_pos)
        self._anim.setEndValue(1.0 if v else 0.0)
        self._anim.start()

        self._update_ui()

    # ---- stable hover via hover events ----
    def event(self, e):
        if e.type() == QEvent.HoverEnter:
            self._set_hovered(True)
        elif e.type() == QEvent.HoverLeave:
            self._set_hovered(False)
        return super().event(e)

    def _set_hovered(self, v: bool):
        self._hovered = v
        self.setProperty("hovered", "true" if v else "false")  # <- СТРОКА, не bool
        self._repolish_all()

    def _repolish_all(self):
        for w in (self, self._track, self._knob, self._label):
            w.style().unpolish(w)
            w.style().polish(w)
            w.update()

    # ---- click ----
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            return
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            # Toggle only if released inside the widget
            if self.rect().contains(e.pos()):
                self.setChecked(not self._checked)
            e.accept()
            return
        super().mouseReleaseEvent(e)

    # ---- ui/layout ----
    def _update_ui(self):
        self._label.setText("Тёмная" if self._checked else "Светлая")
        self._label.setAlignment(
            Qt.AlignVCenter | (Qt.AlignLeft if self._checked else Qt.AlignRight)
        )

        # Update properties for QSS styling
        state_str = "true" if self._checked else "false"
        
        self.setProperty("checked", state_str)
        self._track.setProperty("checked", state_str)
        self._knob.setProperty("checked", state_str)

        self._layout()
        self._repolish_all()

    def _on_theme_changed(self, theme_id: str) -> None:
        self._repolish_all()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._layout()

    def _layout(self):
        w, h = self.width(), self.height()
        self._track.setGeometry(0, 0, w, h)

        knob = 24
        y = (h - knob) // 2
        x0 = self._pad
        x1 = w - self._pad - knob
        x = int(x0 + (x1 - x0) * self._knob_pos)
        self._knob.setGeometry(x, y, knob, knob)

        if self._checked:
            lx = self._pad
        else:
            lx = self._pad + knob + self._gap
        lw = max(10, w - knob - self._pad * 2 - self._gap)
        self._label.setGeometry(lx, 0, lw, h)

    def _repolish(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()