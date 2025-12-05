from .auth_model import AuthModel
from .auth_view import AuthView

from core.worker import APIWorker

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject


class AuthController(QObject):

    login_successful = pyqtSignal()

    def __init__(
            self, 
            model: AuthModel, 
            view: AuthView, 
            window: QMainWindow
    ) -> None:
        
        super().__init__()
        self.model = model
        self.view = view
        self.auth_window = window

        self.api_worker = None # API worker (Thread)


        """=== Handlers ==="""

        self.view.theme_switcher_clicked(self.on_theme_switcher_clicked)
        
        # Sign In page
        self.view.login_login_page_button_clicked(self.on_login_login_page_button_clicked)
        self.view.guest_login_page_button_clicked(self.on_guest_login_page_button_clicked)
        self.view.create_account_login_page_button_clicked(self.on_create_account_login_page_button_clicked)
        self.view.forgot_password_login_page_button_clicked(self.on_forgot_password_login_page_button_clicked)

        # Sign Up page
        self.view.create_account_signup_page_button_clicked(self.on_create_account_signup_page_button_clicked)
        self.view.have_account_signup_page_button_clicked(self.on_have_account_signup_page_button_clicked)

        # Change password pages
        self.view.confirm_email_button_clicked(self.on_confirm_email_button_clicked)
        self.view.change_password_button_clicked(self.on_change_password_button_clicked)
        self.view.know_password_button_clicked(self.on_do_not_change_password_button_clicked)
        self.view.do_not_change_password_button_clicked(self.on_do_not_change_password_button_clicked)


    def login_user(self, user_data: dict) -> None:
        # Save user data
        auto_login = self.view.get_auto_login()
        self.model.save_user(user_data=user_data, auto_login=auto_login)

        self.login_successful.emit()
        self.auth_window.close()


    def error_login(self, exception):
        print(exception)


    """=== Handlers ==="""

    def on_theme_switcher_clicked(self) -> None:
        self.view.set_theme()


    # Log In page
    def on_login_login_page_button_clicked(self) -> None:

        # Get data from lineedits
        email = self.view.get_email_login()
        password = self.view.get_password_login()

        # Create worker
        self.api_worker = APIWorker(self.model.login, email=email, password=password)

        self.api_worker.finished.connect(lambda data: self.login_user(user_data=data))
        self.api_worker.error.connect(lambda e: self.error_login(exception=e))

        self.api_worker.start()

    
    def on_guest_login_page_button_clicked(self) -> None:
        print("Guest button clicked")


    def on_create_account_login_page_button_clicked(self) -> None:
        page = self.view.pages.get("signup_page", None)
        if page:
            self.view.switch_page(page=page)

    
    def on_forgot_password_login_page_button_clicked(self, event) -> None:
        page = self.view.pages.get("change_password_confirm_page", None)
        if page:
            self.view.switch_page(page=page)


    # Sign Up page
    def on_create_account_signup_page_button_clicked(self) -> None:
        print("Create account button clicked")


    def on_have_account_signup_page_button_clicked(self) -> None:
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)


    # Change password page
    def on_confirm_email_button_clicked(self) -> None:
        page = self.view.pages.get("change_password_change_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_do_not_change_password_button_clicked(self) -> None:
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)

    
    def on_change_password_button_clicked(self) -> None:
        print("Change password button clicked")
