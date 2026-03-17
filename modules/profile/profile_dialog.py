from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QRegExpValidator
from PyQt5.QtCore import QRegExp

from ui.ui_converted.profile_dialog import Ui_ProfileDialog
from ui.custom_widgets.modal_window import ShadowContainer, BaseModalDialog

class ProfileDialog(BaseModalDialog):
    def __init__(self, parent, user_data: dict, departments: list[dict]):
        super().__init__(parent)
        self.user_data = user_data
        self.departments = departments

        # === Setup UI ===
        self.ui = Ui_ProfileDialog()
        self.ui.setupUi(self)

        # Take layout from UI
        original_layout = self.layout()

        # Create a container widget that will hold the UI and have the shadow
        container = ShadowContainer(self)
        container.setLayout(original_layout)
        container.setObjectName("profileDialogContainer")

        # Reparent UI frames into container
        self.ui.texts_frame.setParent(container)
        self.ui.form_frame.setParent(container)
        self.ui.buttons_frame.setParent(container)

        # === Add single word validators ===
        single_word_validator = QRegExpValidator(QRegExp(r'^\S+$'))
        self.ui.firstname_lineEdit.setValidator(single_word_validator)
        self.ui.lastname_lineEdit.setValidator(single_word_validator)

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

        # === Populate data ===
        self._populate_initial_data()

        # === Connect handlers ===
        self.ui.accept_pushButton.clicked.connect(self.accept)
        self.ui.cancel_pushButton.clicked.connect(self.reject)
        self.ui.firstname_lineEdit.textChanged.connect(self._validate_changes)
        self.ui.lastname_lineEdit.textChanged.connect(self._validate_changes)
        self.ui.department_comboBox.currentIndexChanged.connect(self._validate_changes)

    def _get_original_department_id(self) -> int | None:
        """Robustly determines the original department ID from user_data."""
        dept_id = self.user_data.get("department_id")
        if dept_id is not None:
            return dept_id

        dept_name = self.user_data.get("department")
        if dept_name is not None:
            for dept in self.departments:
                if dept.get("name") == dept_name:
                    return dept.get("id")
        return None

    def _populate_initial_data(self):
        """Fills the widgets with the current user data."""
        parts = self._split_username(self.user_data.get("username"))
        first_name = parts[0] if parts else ""
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        self.ui.firstname_lineEdit.setText(first_name)
        self.ui.lastname_lineEdit.setText(last_name)

        # Populate departments and select the current one
        self.ui.department_comboBox.clear()
        target_dept_id = self._get_original_department_id()
        
        # Add a placeholder for no department
        self.ui.department_comboBox.addItem("Отдел не выбран", user_data=None)
        
        selected_index = 0 # Default to placeholder
        for i, dept in enumerate(self.departments):
            dept_id = dept.get("id")
            self.ui.department_comboBox.addItem(dept.get("name"), user_data=dept_id)
            
            if target_dept_id is not None and str(dept_id) == str(target_dept_id):
                # The index in the combobox is i + 1 because of the placeholder
                selected_index = i + 1
        
        self.ui.department_comboBox.setCurrentIndex(selected_index)

    def _validate_changes(self):
        """Enables the save button only if there are actual changes."""
        is_changed = False
        
        parts = self._split_username(self.user_data.get("username"))
        original_first_name = parts[0] if parts else ""
        original_last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        # Check names
        if self.ui.firstname_lineEdit.text() != original_first_name:
            is_changed = True
        if self.ui.lastname_lineEdit.text() != original_last_name:
            is_changed = True
        
        # Check department with explicit None checks
        selected_dept_id = self.ui.department_comboBox.currentData()
        original_dept_id = self._get_original_department_id()
        
        department_changed = False
        if selected_dept_id is None and original_dept_id is not None:
            department_changed = True
        elif selected_dept_id is not None and original_dept_id is None:
            department_changed = True
        elif selected_dept_id is not None and original_dept_id is not None:
            if str(selected_dept_id) != str(original_dept_id):
                department_changed = True
        
        if department_changed:
            is_changed = True

        self.ui.accept_pushButton.setEnabled(is_changed)

    @staticmethod
    def _split_username(username) -> list[str]:
        """Returns username parts safely even when the source value is None."""
        if username is None:
            return []
        return str(username).split()

    def get_updated_data(self) -> dict:
        """Returns the updated user data from the form."""
        return {
            "username": " ".join([
                self.ui.firstname_lineEdit.text(), 
                self.ui.lastname_lineEdit.text()
            ]),
            "department_id": self.ui.department_comboBox.currentData()
        }

    @staticmethod
    def show_dialog(parent, user_data: dict, departments: list[dict]):
        """Creates, shows the dialog, and returns the updated data if accepted."""
        dialog = ProfileDialog(parent, user_data, departments)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_updated_data()
        return None

