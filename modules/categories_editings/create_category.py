from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QColor

from ui import CreateCategory_UI
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog



class CreateCategory(BaseModalDialog):
    def __init__(self, parent):
        super().__init__(parent)

        # === Setup UI ===
        self.ui = CreateCategory_UI()
        self.ui.setupUi(self)

        self.ui.name_lineEdit.set_icon_paths(
            # light theme
            default_light=":/icons/light/light/rename_default.svg",
            hover_light=":/icons/light/light/rename_hover.svg",
            focus_light=":/icons/light/light/rename_active.svg",
            disabled_light=":/icons/light/light/rename_disabled.svg",
            
            # dark theme
            default_dark=":/icons/dark/dark/rename_default.svg",
            hover_dark=":/icons/dark/dark/rename_hover.svg",
            focus_dark=":/icons/dark/dark/rename_active.svg",
            disabled_dark=":/icons/dark/dark/rename_disabled.svg",
        )

        # Take layout from UI
        original_layout = self.layout()

        # Create a container widget that will hold the UI and have the shadow
        container = ShadowContainer(self)
        container.setLayout(original_layout)
        container.setObjectName("createDepartmentContainer")

        # Reparent UI frames into container
        self.ui.texts_frame.setParent(container)
        self.ui.name_frame.setParent(container)
        self.ui.buttons_frame.setParent(container)

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

        # === Connect handlers ===
        self.ui.name_lineEdit.textChanged.connect(self.name_lineedit_changed)
        self.ui.accept_pushButton.clicked.connect(self.accept_button_clicked)
        self.ui.cancel_pushButton.clicked.connect(self.cancel_button_clicked)

    
    @staticmethod
    def get_name(parent=None):
        """Creates, shows the dialog, and returns the entered name.

        This static method provides a convenient way to use the dialog. It
        handles the creation, execution, and result retrieval.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.

        Returns:
            str: The new category name if the user clicks 'Accept'.
            None: If the user cancels or closes the dialog.
        """
        dialog = CreateCategory(parent)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_category_name()
        
        return None
    

    # Handlers
    def name_lineedit_changed(self):
        """Handles text changes in the new category name line edit.

        Enables the 'Accept' button if and only if the text length is
        exactly 6 characters.
        """
        text = self.ui.name_lineEdit.text()
        self.ui.accept_pushButton.setEnabled(len(text) > 0)


    def get_category_name(self):
        """Retrieves the category name from the line edit.

        Returns:
            str: The text currently in the verification code line edit.
        """
        return self.ui.name_lineEdit.text()


    def accept_button_clicked(self):
        """Handles the 'Accept' button click.

        Accepts the dialog, causing it to close and return QDialog.Accepted.
        """
        self.accept()


    def cancel_button_clicked(self):
        """Handles the 'Cancel' button click.

        Closes the dialog, which is equivalent to rejecting it.
        """
        self.close()