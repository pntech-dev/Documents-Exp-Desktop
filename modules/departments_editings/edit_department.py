from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QColor

from ui import EditDepartment_UI
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from utils.delete_info_modal import DeleteInfoDialog



class EditDepartment(BaseModalDialog):
    def __init__(self, parent, current_name: str = None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_name = current_name
        self.action = None

        # === Setup UI ===
        self.ui = EditDepartment_UI()
        self.ui.setupUi(self)

        self.ui.name_lineEdit.setText(current_name)

        # Set the is_danger property to the delete button
        self.ui.delete_department_pushButton.set_danger(is_danger=True)

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
        container.setObjectName("editDepartmentContainer")

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
        self.ui.delete_department_pushButton.clicked.connect(self.delete_button_clicked)

    
    @staticmethod
    def show_dialog(parent=None, current_name=""):
        """Creates, shows the dialog, and returns the action and entered name.

        This static method provides a convenient way to use the dialog. It
        handles the creation, execution, and result retrieval.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
            current_name (str): The current name of the department.

        Returns:
            tuple: (action, name) where action is 'edit', 'delete' or None.
        """
        dialog = EditDepartment(parent, current_name)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.action, dialog.get_department_name()
        
        return None, None
    

    # Handlers
    def name_lineedit_changed(self):
        """Handles text changes in the verification code line edit."""
        text = self.ui.name_lineEdit.text()
        self.ui.accept_pushButton.setEnabled(text != self.current_name)


    def get_department_name(self):
        """Retrieves the department name from the line edit.

        Returns:
            str: The text currently in the verification code line edit.
        """
        return self.ui.name_lineEdit.text()


    def accept_button_clicked(self):
        """Handles the 'Accept' button click.

        Accepts the dialog, causing it to close and return QDialog.Accepted.
        """
        self.action = "edit"
        self.accept()


    def cancel_button_clicked(self):
        """Handles the 'Cancel' button click.

        Closes the dialog, which is equivalent to rejecting it.
        """
        self.close()

    
    def delete_button_clicked(self):
        """Handles the 'Delete' button click"""
        dialog = DeleteInfoDialog(
            parent=self.parent_window, 
            info_type="department"
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.action = "delete"
            self.accept()