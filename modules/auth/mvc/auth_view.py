from utils import ThemeManagerInstance

from ui import AuthWindow_UI

from PyQt5.QtWidgets import QLineEdit, QCheckBox, QPushButton


class AuthPageWidgetGroup:
    def __init__(
            self,
            email_field: QLineEdit = None,
            password_field: QLineEdit = None,
            confirm_password_field: QLineEdit = None,
            view_password_checkbox: QCheckBox = None,
            auto_login_checkbox: QCheckBox = None,
            submit_button: QPushButton = None,
            back_button: QPushButton = None,
            tertiary_button: QPushButton = None,
            forgot_password_button: QPushButton = None
    ) -> None:
        self.email_field = email_field
        self.password_field = password_field
        self.confirm_password_field = confirm_password_field
        self.view_password_checkbox = view_password_checkbox
        self.auto_login_checkbox = auto_login_checkbox
        self.submit_button = submit_button
        self.back_button = back_button
        self.tertiary_button = tertiary_button
        self.forgot_password_button = forgot_password_button


class AuthView:
    def __init__(self, ui: AuthWindow_UI):
        self.ui = ui
        self.theme_manager = ThemeManagerInstance()

        # Auth module pages
        self.pages = {
            "login_page": self.ui.login_page,
            "signup_page": self.ui.signup_page,
            "change_password_confirm_page": self.ui.change_password_confirm_page,
            "change_password_change_page": self.ui.change_password_change_page
        }

        # Theme buttons list
        self.theme_buttons = [
            self.ui.theme_button,
            self.ui.theme_button_2,
            self.ui.theme_button_3,
            self.ui.theme_button_4
        ]

        self.login_page = AuthPageWidgetGroup(
            email_field=self.ui.email_lineEdit,
            password_field=self.ui.password_lineEdit,
            view_password_checkbox=self.ui.view_password_checkBox,
            auto_login_checkbox=self.ui.auto_login_checkBox,
            submit_button=self.ui.login_pushButton,
            back_button=self.ui.guest_pushButton,
            tertiary_button=self.ui.no_account_pushButton,
            forgot_password_button=self.ui.forgot_password_label
        )

        self.signup_page = AuthPageWidgetGroup(
            email_field=self.ui.email_lineEdit_2,
            password_field=self.ui.password_lineEdit_2,
            confirm_password_field=self.ui.password_lineEdit_4,
            view_password_checkbox=self.ui.view_password_checkBox_2,
            auto_login_checkbox=self.ui.auto_login_checkBox_2,
            submit_button=self.ui.create_pushButton,
            back_button=self.ui.have_account_pushButton,
        )

    def set_theme(self) -> None:
        """Set theme"""
        self.theme_manager.switch_theme()


    def switch_page(self, page) -> None:
        """Page switcher"""
        self.ui.pages.setCurrentWidget(page)

    """=== Handlers ==="""

    def theme_switcher_clicked(self, handler) -> None:
        """Switch theme on click theme switcher button"""
        for theme_button in self.theme_buttons:
            theme_button.clicked.connect(handler)


    # Log In page
    def get_view_password_login_page_state(self) -> bool:
        return self.ui.view_password_checkBox.isChecked()


    def set_password_visibality_login_page(self, state) -> None:
        mode = QLineEdit.Normal if state else QLineEdit.Password
        self.ui.password_lineEdit.setEchoMode(mode)
        
        
    def get_email_login(self) -> str:
        return self.ui.email_lineEdit.text()
    

    def get_password_login(self) -> str:
        return self.ui.password_lineEdit.text()
    

    def get_auto_login_login_page(self) -> bool:
        return self.ui.auto_login_checkBox.isChecked()


    def login_login_page_button_clicked(self, handler) -> None:
        self.ui.login_pushButton.clicked.connect(handler)


    def guest_login_page_button_clicked(self, handler) -> None:
        self.ui.guest_pushButton.clicked.connect(handler)


    def create_account_login_page_button_clicked(self, handler) -> None:
        self.ui.no_account_pushButton.clicked.connect(handler)

    
    def forgot_password_login_page_button_clicked(self, handler) -> None:
        self.ui.forgot_password_label.mousePressEvent = handler


    def view_password_login_page_checkbox_state_changed(self, handler) -> None:
        self.ui.view_password_checkBox.stateChanged.connect(handler)


    # Sign Up page
    def get_view_password_signup_page_state(self) -> bool:
        return self.ui.view_password_checkBox_2.isChecked()


    def set_password_visibality_signup_page(self, state) -> None:
        mode = QLineEdit.Normal if state else QLineEdit.Password
        self.ui.password_lineEdit_2.setEchoMode(mode)
        self.ui.password_lineEdit_4.setEchoMode(mode)
    def email_lineedit_login_page_text_changed(self, handler) -> None:
        self.ui.email_lineEdit.textChanged.connect(handler)


    def password_lineedit_login_page_text_changed(self, handler) -> None:
        self.ui.password_lineEdit.textChanged.connect(handler)

    
    def update_login_button(self, state: bool) -> None:
        self.ui.login_pushButton.setEnabled(state)


    # Sign Up page
    def get_email_signup(self) -> str:
        return self.ui.email_lineEdit_2.text()
    

    def get_password_signup(self) -> str:
        return self.ui.password_lineEdit_2.text()
    

    def get_confirm_password_signup(self) -> str:
        return self.ui.password_lineEdit_4.text()
    

    def get_auto_login_signup_page(self) -> bool:
        return self.ui.auto_login_checkBox_2.isChecked()


    def create_account_signup_page_button_clicked(self, handler) -> None:
        self.ui.create_pushButton.clicked.connect(handler)


    def have_account_signup_page_button_clicked(self, handler) -> None:
        self.ui.have_account_pushButton.clicked.connect(handler)

    
    def view_password_signup_page_checkbox_state_changed(self, handler) -> None:
        self.ui.view_password_checkBox_2.stateChanged.connect(handler)


    def update_signup_button(self, state: bool) -> None:
        self.ui.create_pushButton.setEnabled(state)


    def email_lineedit_signup_page_text_changed(self, handler) -> None:
        self.ui.email_lineEdit_2.textChanged.connect(handler)

    
    def password_lineedit_signup_page_text_changed(self, handler) -> None:
        self.ui.password_lineEdit_2.textChanged.connect(handler)


    def confirm_password_lineedit_signup_page_text_changed(self, handler) -> None:
        self.ui.password_lineEdit_4.textChanged.connect(handler)


    # Change password page
    def get_view_password_change_password_page_state(self) -> bool:
        return self.ui.view_password_checkBox_3.isChecked()
    

    def get_email_change_password_page(self) -> str:
        return self.ui.email_lineEdit_3.text()
    

    def get_password_change_password_page(self) -> str:
        return self.ui.password_lineEdit_6.text()
    

    def get_confirm_password_change_password_page(self) -> str:
        return self.ui.password_lineEdit_5.text()
    

    def update_confirm_email_button_state(self, state: bool) -> None:
        self.ui.accept_pushButton.setEnabled(state)

    
    def update_change_password_button_state(self, state: bool) -> None:
        self.ui.change_pushButton.setEnabled(state)


    def set_password_visibality_change_password_page(self, state) -> None:
        mode = QLineEdit.Normal if state else QLineEdit.Password
        self.ui.password_lineEdit_6.setEchoMode(mode)
        self.ui.password_lineEdit_5.setEchoMode(mode)

    
    def change_password_page_clear_lineedits(self) -> None:
        lineedits = [
            self.ui.email_lineEdit_3,
            self.ui.password_lineEdit_6,
            self.ui.password_lineEdit_5
        ]

        for lineedit in lineedits:
            lineedit.clear()


    def confirm_email_button_clicked(self, handler) -> None:
        self.ui.accept_pushButton.clicked.connect(handler)


    def know_password_button_clicked(self, handler) -> None:
        self.ui.have_account_pushButton_2.clicked.connect(handler)


    def email_lineedit_change_password_page_text_changed(self, handler) -> None:
        self.ui.email_lineEdit_3.textChanged.connect(handler)


    def change_password_button_clicked(self, handler) -> None:
        self.ui.change_pushButton.clicked.connect(handler)

    
    def do_not_change_password_button_clicked(self, handler) -> None:
        self.ui.have_account_pushButton_3.clicked.connect(handler)

    
    def view_password_change_password_checkbox_state_changed(self, handler) -> None:
        self.ui.view_password_checkBox_3.stateChanged.connect(handler)


    def password_lineedit_change_password_page_text_changed(self, handler) -> None:
        self.ui.password_lineEdit_6.textChanged.connect(handler)


    def confirm_password_lineedit_change_password_page_text_changed(self, handler) -> None:
        self.ui.password_lineEdit_5.textChanged.connect(handler)