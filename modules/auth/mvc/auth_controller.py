import string

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject

from .auth_view import AuthView
from .auth_model import AuthModel
from core.worker import APIWorker
from utils.email_confirm_modal import EmailConfirmDialog


class AuthController(QObject):

    login_successful = pyqtSignal(str)

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

        self.main_module_window = None
        self.email_confirm_window = None

        self.api_worker = None # API worker (Thread)


        """=== Handlers ==="""

        self.view.theme_switcher_clicked(self.on_theme_switcher_clicked)

        # Sign In page
        self.view.login_page.submit_button_clicked(self.on_login_login_page_button_clicked)
        self.view.login_page.back_button_clicked(self.on_guest_login_page_button_clicked)
        self.view.login_page.tertiary_button_clicked(self.on_create_account_login_page_button_clicked)
        self.view.login_page.forgot_password_button_clicked(self.on_forgot_password_login_page_button_clicked)
        self.view.login_page.view_password_checkbox_state_changed(self.on_view_password_login_page_checkbox_state_changed)
        self.view.login_page.email_lineedit_text_changed(self.on_login_page_lineedits_changed)
        self.view.login_page.password_lineedit_text_changed(self.on_login_page_lineedits_changed)

        # Sign Up page
        self.view.signup_page.submit_button_clicked(self.on_create_account_signup_page_button_clicked)
        self.view.signup_page.back_button_clicked(self.on_have_account_signup_page_button_clicked)
        self.view.signup_page.view_password_checkbox_state_changed(self.on_view_password_signup_page_checkbox_state_changed)
        self.view.signup_page.email_lineedit_text_changed(self.on_signup_page_lineedits_changed)
        self.view.signup_page.password_lineedit_text_changed(self.on_signup_page_lineedits_changed)
        self.view.signup_page.confirm_password_lineedit_text_changed(self.on_signup_page_lineedits_changed)

        # Change password pages
        self.view.forgot_page_email_confirm.submit_button_clicked(self.on_confirm_email_button_clicked)
        self.view.forgot_page_reset_password.submit_button_clicked(self.on_change_password_button_clicked)
        self.view.forgot_page_email_confirm.back_button_clicked(self.on_do_not_change_password_button_clicked)
        self.view.forgot_page_reset_password.back_button_clicked(self.on_do_not_change_password_button_clicked)
        self.view.forgot_page_reset_password.view_password_checkbox_state_changed(self.on_view_password_change_password_checkbox_state_changed)
        self.view.forgot_page_email_confirm.email_lineedit_text_changed(self.on_email_lineedit_change_password_page_text_changed)
        self.view.forgot_page_reset_password.password_lineedit_text_changed(self.on_change_password_page_lineedits_changed)
        self.view.forgot_page_reset_password.confirm_password_lineedit_text_changed(self.on_change_password_page_lineedits_changed)


    def login_user(self, user_data: dict) -> None:
        # Save user data
        auto_login = self.view.login_page.get_auto_login_state()
        self.model.save_user(user_data=user_data, auto_login=auto_login)

        # Clear lineedits
        self.view.login_page.clear_lineedits()

        self.login_successful.emit("auth")


    def signup_user(self, user_data: dict) -> None:
        # Save user data
        auto_login = self.view.signup_page.get_auto_login_state()
        self.model.save_user(user_data=user_data, auto_login=auto_login)

        # Clear lineedits
        self.view.signup_page.clear_lineedits()

        self.login_successful.emit("auth")

    
    def check_signup_passwords_match(self) -> bool:
        # Get data from lineedits
        password = self.view.signup_page.get_password()
        confirm_password = self.view.signup_page.get_confirm_password()

        return password == confirm_password
    

    def swith_to_change_password_page(self, data: dict) -> None:
        # Save token
        self.model.save_token(token_name="reset_token", token="reset_token", data=data)

        # Switch to change password page
        page = self.view.pages.get("change_password_change_page", None)
        if page:
            self.view.switch_page(page=page)


    def password_changed(self, data: dict) -> None:
        # Switch to login page
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)

        # Clear lineedits
        self.view.forgot_page_reset_password.clear_lineedits()

    
    def open_email_confirm_modal_window(self, data, email: str) -> None:
        print(data)
        code = EmailConfirmDialog.get_code(parent=self.auth_window)
        
        # Create worker
        self.api_worker = APIWorker(
            self.model.reset_password_confirm_email,  
            email=email, 
            code=code
        )

        self.api_worker.finished.connect(lambda data: self.swith_to_change_password_page(data=data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()

    
    def worker_error(self, exception):
        print(exception)


    def signup(self, data: dict, email: str, password: str) -> None:
        print(data)
        code = EmailConfirmDialog.get_code(parent=self.auth_window)

        # Create worker
        self.api_worker = APIWorker(
            self.model.signup, 
            code=code, 
            email=email, 
            password=password
        )

        self.api_worker.finished.connect(lambda data: self.signup_user(user_data=data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    """=== Handlers ==="""

    def on_theme_switcher_clicked(self) -> None:
        self.view.set_theme()


    # Log In page
    def on_login_login_page_button_clicked(self) -> None:
        # Get data from lineedits
        email = self.view.login_page.get_email()
        password = self.view.login_page.get_password()

        # Create worker
        self.api_worker = APIWorker(self.model.login, email=email, password=password)

        self.api_worker.finished.connect(lambda data: self.login_user(user_data=data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()

    
    def on_guest_login_page_button_clicked(self) -> None:
        self.login_successful.emit("guest")


    def on_create_account_login_page_button_clicked(self) -> None:
        page = self.view.pages.get("signup_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_forgot_password_login_page_button_clicked(self, event) -> None:
        page = self.view.pages.get("change_password_confirm_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_login_page_lineedits_changed(self) -> None:
        # Get texts from lineedits
        email = self.view.login_page.get_email()
        password = self.view.login_page.get_password()

        # Validate email
        if not self._validate_email(email=email):
            return
        
        # Validate password
        if not self._validate_password(password=password):
            return

        # Defining login button state (True if both lineedits has text, else False)
        state = bool(email.strip() and password.strip())

        # Update login button state
        self.view.login_page.update_submit_button_state(state=state)


    def on_view_password_login_page_checkbox_state_changed(self):
        state = self.view.login_page.get_view_password_state()
        self.view.login_page.set_password_visibility(state)


    # Sign Up page

    def on_create_account_signup_page_button_clicked(self) -> None:

        # Get data from lineedits
        email = self.view.signup_page.get_email()
        password = self.view.signup_page.get_password()

        # Create email confirm worker
        self.api_worker = APIWorker(self.model.signup_send_code, email=email)

        self.api_worker.finished.connect(lambda data: self.signup(data=data, email=email, password=password))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    def on_have_account_signup_page_button_clicked(self) -> None:
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_signup_page_lineedits_changed(self) -> None:
        # Get texts from lineedits
        email = self.view.signup_page.get_email()
        password = self.view.signup_page.get_password()
        confirm_password = self.view.signup_page.get_confirm_password()
        
        # Validate email
        if not self._validate_email(email=email):
            return
        
        # Validate password
        if not self._validate_password(password=password):
            return

        # Check password matching
        passwords_match = password == confirm_password

        # Defining signup button state
        state = bool(email.strip() and password.strip() and confirm_password.strip() and passwords_match)

        # Update signup button state
        self.view.signup_page.update_submit_button_state(state=state)


    def on_view_password_signup_page_checkbox_state_changed(self):
        state = self.view.signup_page.get_view_password_state()
        self.view.signup_page.set_password_visibility(state)


    # Change password page

    def on_email_lineedit_change_password_page_text_changed(self) -> None:
        # Get text from lineedit
        email = self.view.forgot_page_email_confirm.get_email()

        # Validate email lineedit
        validate_email_satate = self._validate_email(email=email)

        # Change confirm email button state
        self.view.forgot_page_email_confirm.update_submit_button_state(state=validate_email_satate)


    def on_confirm_email_button_clicked(self) -> None:
        email = self.view.forgot_page_email_confirm.get_email()

        # Create worker
        self.api_worker = APIWorker(self.model.request_reset_password, email=email)

        self.api_worker.finished.connect(lambda data: self.open_email_confirm_modal_window(data, email=email))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    def on_do_not_change_password_button_clicked(self) -> None:
        # Switch to login page
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)

        # Clear lineedits
        self.view.change_password_page_clear_lineedits()


    def on_change_password_page_lineedits_changed(self) -> None:
        # Get texts from lineedits
        password = self.view.forgot_page_reset_password.get_password()
        confirm_password = self.view.forgot_page_reset_password.get_confirm_password()
        
        # Validate password
        if not self._validate_password(password=password):
            return
        
        # Check password matching
        passwords_match = password == confirm_password

        # Defining signup button state
        state = bool(password.strip() and confirm_password.strip() and passwords_match)

        # Update signup button state
        self.view.forgot_page_reset_password.update_submit_button_state(state=state)


    def on_change_password_button_clicked(self) -> None:
        # Get new password
        password = self.view.forgot_page_reset_password.get_password()

        # Create worker
        self.api_worker = APIWorker(self.model.reset_password, password=password)

        self.api_worker.finished.connect(lambda data: self.password_changed(data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    def on_view_password_change_password_checkbox_state_changed(self):
        state = self.view.forgot_page_reset_password.get_view_password_state()
        self.view.forgot_page_reset_password.set_password_visibility(state)


    def _validate_email(self, email: str) -> bool:
        """Simple email validation method."""

        if "@" not in email or email.count("@") >= 2:
            return False

        if email.startswith("@") or email.endswith("@"):
            return False

        local_part, domain_part = email.split("@")

        if not local_part or not domain_part:
            return False

        # Local part verification
        if len(local_part) > 64:
            return False

        if local_part.startswith(".") or local_part.endswith("."):
            return False

        if ".." in local_part:
            return False

        # Domain part verification
        if len(domain_part) > 255:
            return False

        if "." not in domain_part:
            return False

        return True
    
    def _validate_password(self, password: str) -> bool:
        """Simple password validation method."""

        # Password length
        if len(password) < 8:
            return False
        
        # Minimum one symbol is digit
        if not any(char.isdigit() for char in password):
            return False
        
        # Minimum one symbol is uppercase
        if not any(char.isupper() for char in password):
            return False
        
        # Minimum one symbol is lowercase
        if not any(char.islower() for char in password):
            return False
        
        # Minimum one symbol is special character
        if not any(char in string.punctuation for char in password):
            return False

        return True