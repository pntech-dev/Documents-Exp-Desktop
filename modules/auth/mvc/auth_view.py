from utils import ThemeManager

from ui import AuthWindow_UI


class AuthView:
    def __init__(self, ui: AuthWindow_UI):
        self.ui = ui
        self.theme_manager = ThemeManager()

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
        self.ui.fogot_password_label.mousePressEvent = handler


    # Sign Up page
    def get_email_signup(self) -> str:
        return self.ui.email_lineEdit_2.text()
    

    def get_password_signup(self) -> str:
        return self.ui.password_lineEdit_2.text()
    

    def get_auto_login_signup_page(self) -> bool:
        return self.ui.auto_login_checkBox_2.isChecked()


    def create_account_signup_page_button_clicked(self, handler) -> None:
        self.ui.create_pushButton.clicked.connect(handler)


    def have_account_signup_page_button_clicked(self, handler) -> None:
        self.ui.have_account_pushButton.clicked.connect(handler)


    # Change password page
    def confirm_email_button_clicked(self, handler) -> None:
        self.ui.accept_pushButton.clicked.connect(handler)


    def know_password_button_clicked(self, handler) -> None:
        self.ui.have_account_pushButton_2.clicked.connect(handler)


    def change_password_button_clicked(self, handler) -> None:
        self.ui.change_pushButton.clicked.connect(handler)

    
    def do_not_change_password_button_clicked(self, handler) -> None:
        self.ui.have_account_pushButton_3.clicked.connect(handler)