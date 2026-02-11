from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QColor

from ui import EmailConfirm_UI
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog


class EmailConfirmDialog(BaseModalDialog):
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