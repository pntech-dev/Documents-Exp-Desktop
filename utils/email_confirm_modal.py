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

from ui import EmailConfirm_UI


class EmailConfirmDialog(QDialog):
    """A modal dialog for entering a 6-digit email verification code.

    This dialog is designed to be frameless and centered on the screen, with a
    drop shadow and a semi-transparent overlay that darkens the parent window.
    It provides a static method `get_code` for easy instantiation and retrieval
    of the entered code.

    Attributes:
        ui (EmailConfirm_UI): The UI layout and widgets for the dialog.
        overlay (ModalOverlay): The widget used to darken the background.
    """
    def __init__(self, parent=None):
        """Initializes the EmailConfirmDialog.

        Sets up a frameless, transparent window. The actual UI is placed
        within a ShadowContainer to which a QGraphicsDropShadowEffect is
        applied. This avoids rendering issues with applying shadows directly
        to a QDialog. It also sets up input validators and connects widget
        signals to their corresponding handler slots.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
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
            default_light=":/icons/light/light/code_default.svg",
            default_dark=":/icons/dark/dark/code_default.svg",

            hover_light=":/icons/light/light/code_hover.svg",
            hover_dark=":/icons/dark/dark/code_hover.svg",

            focus_light=":/icons/light/light/code_active.svg",
            focus_dark=":/icons/dark/dark/code_active.svg",

            disabled_light=":/icons/light/light/code_disabled.svg",
            disabled_dark=":/icons/dark/dark/code_disabled.svg",
        )


    @staticmethod
    def get_code(parent=None):
        """Creates, shows the dialog, and returns the entered code.

        This static method provides a convenient way to use the dialog. It
        handles the creation, execution, and result retrieval.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.

        Returns:
            str: The 6-digit verification code if the user clicks 'Accept'.
            None: If the user cancels or closes the dialog.
        """
        dialog = EmailConfirmDialog(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_verification_code()
        
        return None


    # Handlers
    def code_lineedit_changed(self):
        """Handles text changes in the verification code line edit.

        Enables the 'Accept' button if and only if the text length is
        exactly 6 characters.
        """
        text = self.ui.verification_code_lineEdit.text()
        self.ui.accept_pushButton.setEnabled(len(text) == 6)


    def accept_button_clicked(self):
        """Handles the 'Accept' button click.

        Accepts the dialog, causing it to close and return QDialog.Accepted.
        """
        self.accept()


    def get_verification_code(self):
        """Retrieves the code from the line edit.

        Returns:
            str: The text currently in the verification code line edit.
        """
        return self.ui.verification_code_lineEdit.text()


    def cancel_button_clicked(self):
        """Handles the 'Cancel' button click.

        Closes the dialog, which is equivalent to rejecting it.
        """
        self.close()


    def accept(self):
        """Overrides the default QDialog.accept() method.

        Ensures the background overlay is closed before calling the parent
        class's accept method.
        """
        if self.overlay:
            self.overlay.close()
            
        super().accept()


    def reject(self):
        """Overrides the default QDialog.reject() method.

        Ensures the background overlay is closed before calling the parent
        class's reject method.
        """
        if self.overlay:
            self.overlay.close()
        super().reject()

    # Center modal on screen
    def showEvent(self, event):
        """Overrides QWidget.showEvent to set up the dialog's appearance.

        Creates the background overlay and triggers the centering logic after
        the dialog is shown, ensuring all geometry calculations are complete.

        Args:
            event (QShowEvent): The show event.
        """
        super().showEvent(event)
        self.create_overlay()
        QTimer.singleShot(0, self.center_on_screen)

    
    def closeEvent(self, event):
        """Overrides QWidget.closeEvent to clean up the overlay.

        Ensures that the background overlay is closed whenever the dialog is
        closed, regardless of whether it was accepted or rejected.

        Args:
            event (QCloseEvent): The close event.
        """
        if self.overlay:
            self.overlay.close()

        super().closeEvent(event)


    def create_overlay(self):
        """Creates and displays the modal overlay.

        If the dialog has a parent, it creates a ModalOverlay instance that
        is a child of the parent window, resizes it to cover the entire
        parent, and shows it.
        """
        if self.parent():
            self.overlay = ModalOverlay(self.parent().window())
            self.overlay.resize(self.parent().window().size())
            self.overlay.show()
            self.overlay.raise_()


    def center_on_screen(self):
        """Calculates and applies the centered position on the screen.

        This method ensures the dialog is perfectly centered on the primary
        monitor's availabel geometry. It's called via a QTimer.singleShot to
        run after the layout has been fully processed.
        """
        self.adjustSize() # Ensure final size with shadow container

        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.center().x() - self.width() // 2
        y = screen.center().y() - self.height() // 2

        self.move(x, y)


    def paintEvent(self, event):
        """Overrides QWidget.paintEvent to do nothing.

        The dialog's background is transparent. All visual content is handled
        by the child ShadowContainer, which has its own background style. This
        prevents painting conflicts.

        Args:
            event (QPaintEvent): The paint event.
        """
        pass


# Shadow
class ShadowContainer(QFrame):
    """A QFrame that serves as the visible background for a custom dialog.

    This container holds the dialog's UI elements. Its primary purpose is to
    provide a surface to which a QGraphicsDropShadowEffect can be applied
    and which can be styled (e.g., with rounded corners) via QSS without
    conflicting with the parent QDialog's properties.
    """
    def __init__(self, parent=None):
        """Initializes the ShadowContainer.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)


# Overlay
class ModalOverlay(QWidget):
    """A semi-transparent widget to darken the background of a modal dialog.

    This widget is placed over the parent window to give focus to the modal
    dialog in front of it.

    Attributes:
        opacity (int): The alpha value (0-255) for the overlay color.
    """
    def __init__(self, parent):
        """Initializes the ModalOverlay.

        Sets window flags to make it a frameless, transparent overlay that
        initially does not interact with mouse events.

        Args:
            parent (QWidget): The parent widget (usually the main window) that
                the overlay will cover.
        """
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.opacity = 100 # (0–255)


    def paintEvent(self, event):
        """Fills the widget with a semi-transparent black color.

        Args:
            event (QPaintEvent): The paint event.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, self.opacity))