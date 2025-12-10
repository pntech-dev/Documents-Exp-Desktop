from PyQt5.QtWidgets import (
    QFrame,
    QDialog, 
    QWidget,
    QVBoxLayout,
    QApplication,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIntValidator, QColor, QPainter

from ui.email_confirm import Ui_Dialog as EmailConfirm_UI


class EmailConfirmDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.overlay = None

        # === Window flags ===
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # === Setup UI ===
        self.ui = EmailConfirm_UI()
        self.ui.setupUi(self)

        # Take layout from UI
        original_layout = self.layout()

        # Create a container widget that will hold the UI and have the shadow
        container = ShadowContainer(self)
        container.setLayout(original_layout)
        container.setObjectName("emailConfirmContainer")

        # Reparent UI frames into container
        self.ui.texts_frame.setParent(container)
        self.ui.verification_code_frame.setParent(container)
        self.ui.frame.setParent(container)

        # === Shadow ===
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, int(255 * 0.10)))
        shadow.setOffset(0, 5)
        container.setGraphicsEffect(shadow)

        # === Main layout (holds container with shadow margins) ===
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20) # For shadow space
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # === LineEdit validator ===
        self.ui.verification_code_lineEdit.setValidator(QIntValidator(0, 999999))

        # === Connect handlers ===
        self.ui.verification_code_lineEdit.textChanged.connect(self.code_lineedit_changed)
        self.ui.accept_pushButton.clicked.connect(self.accept_button_clicked)
        self.ui.cancel_pushButton.clicked.connect(self.cancel_button_clicked)

        self.ui.verification_code_lineEdit.set_icon_paths(
            default_light=":/icons/light/input_fields/code/light/default.svg",
            default_dark=":/icons/dark/input_fields/code/dark/default.svg",

            hover_light=":/icons/light/input_fields/code/light/hover.svg",
            hover_dark=":/icons/dark/input_fields/code/dark/hover.svg",

            focus_light=":/icons/light/input_fields/code/light/active.svg",
            focus_dark=":/icons/dark/input_fields/code/dark/active.svg",

            disabled_light=":/icons/light/input_fields/code/light/disabled.svg",
            disabled_dark=":/icons/dark/input_fields/code/dark/disabled.svg",
        )


    @staticmethod
    def get_code(parent=None):
        dialog = EmailConfirmDialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_verification_code()
        
        return None


    # Handlers
    def code_lineedit_changed(self):
        text = self.ui.verification_code_lineEdit.text()
        self.ui.accept_pushButton.setEnabled(len(text) == 6)


    def accept_button_clicked(self):
        self.accept()


    def get_verification_code(self):
        return self.ui.verification_code_lineEdit.text()


    def cancel_button_clicked(self):
        self.close()


    def accept(self):
        if self.overlay:
            self.overlay.close()
            
        super().accept()


    def reject(self):
        if self.overlay:
            self.overlay.close()
        super().reject()

    # Center modal on screen
    def showEvent(self, event):
        """Center the dialog AFTER layout is fully calculated."""
        super().showEvent(event)
        self.create_overlay()
        QTimer.singleShot(0, self.center_on_screen)

    
    def closeEvent(self, event):
        if self.overlay:
            self.overlay.close()

        super().closeEvent(event)


    def create_overlay(self):
        if self.parent():
            self.overlay = ModalOverlay(self.parent().window())
            self.overlay.resize(self.parent().window().size())
            self.overlay.show()
            self.overlay.raise_()


    def center_on_screen(self):
        """Forces layout calculation and centers the window on the screen."""
        self.adjustSize() # Ensure final size with shadow container

        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.center().x() - self.width() // 2
        y = screen.center().y() - self.height() // 2

        self.move(x, y)


    def paintEvent(self, event):
        """All painting is handled by ShadowContainer."""
        pass


# Shadow
class ShadowContainer(QFrame):
    """A QFrame that draws a rounded white background. Used to avoid stylesheet conflicts."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)


# Overlay
class ModalOverlay(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.opacity = 100 # (0–255)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self.opacity))