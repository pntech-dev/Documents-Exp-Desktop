from PyQt5.QtWidgets import (
    QDialog, 
    QVBoxLayout,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QColor

from ui import EditCategory_UI
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog
from utils.delete_info_modal import DeleteInfoDialog


class EditCategory(BaseModalDialog):
    def __init__(self, parent, current_name: str = None, current_show_for_guest: bool = False):
        super().__init__(parent)
        self.parent_window = parent
        self.current_name = current_name
        self.current_show_for_guest = current_show_for_guest
        self.action = None

        # === Setup UI ===
        self.ui = EditCategory_UI()
        self.ui.setupUi(self)

        self.ui.name_lineEdit.setText(current_name)
        self.ui.guest_show_checkBox.setChecked(current_show_for_guest)

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
        container.setObjectName("editCategoryContainer")

        # Reparent UI frames into container
        self.ui.texts_frame.setParent(container)
        self.ui.name_frame.setParent(container)
        self.ui.guest_show_checkBox.setParent(container)
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
        self.ui.name_lineEdit.textChanged.connect(self._validate_changes)
        self.ui.guest_show_checkBox.stateChanged.connect(self._validate_changes)
        self.ui.accept_pushButton.clicked.connect(self.accept_button_clicked)
        self.ui.cancel_pushButton.clicked.connect(self.cancel_button_clicked)
        self.ui.delete_department_pushButton.clicked.connect(self.delete_button_clicked)

    
    @staticmethod
    def show_dialog(parent=None, current_name="", current_show_for_guest=False):
        """Creates, shows the dialog, and returns the action and entered name."""
        dialog = EditCategory(parent, current_name, current_show_for_guest)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.action, (
                dialog.get_category_name(), 
                dialog.ui.guest_show_checkBox.isChecked()
            )
        
        return None, None
    

    # Handlers
    def _validate_changes(self):
        """Checks if changes were made to enable the save button."""
        text = self.ui.name_lineEdit.text()
        is_name_changed = text != self.current_name
        is_checkbox_changed = self.ui.guest_show_checkBox.isChecked() != self.current_show_for_guest
        
        self.ui.accept_pushButton.setEnabled((
            is_name_changed or is_checkbox_changed
        ) and len(text) > 0)


    def get_category_name(self):
        """Retrieves the category name from the line edit."""
        return self.ui.name_lineEdit.text()


    def accept_button_clicked(self):
        """Handles the 'Accept' button click."""
        self.action = "edit"
        self.accept()


    def cancel_button_clicked(self):
        """Handles the 'Cancel' button click."""
        self.close()

    
    def delete_button_clicked(self):
        """Handles the 'Delete' button click"""
        dialog = DeleteInfoDialog(
            parent=self.parent_window, 
            info_type="category"
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.action = "delete"
            self.accept()
