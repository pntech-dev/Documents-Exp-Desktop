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
        self.view.login_login_page_button_clicked(self.on_login_login_page_button_clicked)
        self.view.guest_login_page_button_clicked(self.on_guest_login_page_button_clicked)
        self.view.create_account_login_page_button_clicked(self.on_create_account_login_page_button_clicked)
        self.view.forgot_password_login_page_button_clicked(self.on_forgot_password_login_page_button_clicked)
        self.view.view_password_login_page_checkbox_state_changed(self.on_view_password_login_page_checkbox_state_changed)
        self.view.email_lineedit_login_page_text_changed(self.on_login_page_lineedits_changed)
        self.view.password_lineedit_login_page_text_changed(self.on_login_page_lineedits_changed)

        # Sign Up page
        self.view.create_account_signup_page_button_clicked(self.on_create_account_signup_page_button_clicked)
        self.view.have_account_signup_page_button_clicked(self.on_have_account_signup_page_button_clicked)
        self.view.view_password_signup_page_checkbox_state_changed(self.on_view_password_signup_page_checkbox_state_changed)
        self.view.email_lineedit_signup_page_text_changed(self.on_signup_page_lineedits_changed)
        self.view.password_lineedit_signup_page_text_changed(self.on_signup_page_lineedits_changed)
        self.view.confirm_password_lineedit_signup_page_text_changed(self.on_signup_page_lineedits_changed)

        # Change password pages
        self.view.confirm_email_button_clicked(self.on_confirm_email_button_clicked)
        self.view.change_password_button_clicked(self.on_change_password_button_clicked)
        self.view.know_password_button_clicked(self.on_do_not_change_password_button_clicked)
        self.view.do_not_change_password_button_clicked(self.on_do_not_change_password_button_clicked)
        self.view.view_password_change_password_checkbox_state_changed(self.on_view_password_change_password_checkbox_state_changed)
        self.view.email_lineedit_change_password_page_text_changed(self.on_email_lineedit_change_password_page_text_changed)
        self.view.password_lineedit_change_password_page_text_changed(self.on_change_password_page_lineedits_changed)
        self.view.confirm_password_lineedit_change_password_page_text_changed(self.on_change_password_page_lineedits_changed)


    def login_user(self, user_data: dict) -> None:
        # Save user data
        auto_login = self.view.get_auto_login_login_page()
        self.model.save_user(user_data=user_data, auto_login=auto_login)

        self.login_successful.emit("auth")


    def signup_user(self, user_data: dict) -> None:
        # Save user data
        auto_login = self.view.get_auto_login_signup_page()
        self.model.save_user(user_data=user_data, auto_login=auto_login)

        self.login_successful.emit("auth")

    
    def check_signup_passwords_match(self) -> bool:
        # Get data from lineedits
        password = self.view.get_password_signup()
        confirm_password = self.view.get_confirm_password_signup()

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
        self.view.change_password_page_cler_lineedits()

    
    def open_email_confirm_modal_window(self, data, email: str) -> None:
        print(data)
        code = EmailConfirmDialog.get_code(parent=self.auth_window)
        
        # Create worker
        self.api_worker = APIWorker(self.model.confirm_email, email=email, code=code)

        self.api_worker.finished.connect(lambda data: self.swith_to_change_password_page(data=data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()

    
    def worker_error(self, exception):
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
        email = self.view.get_email_login()
        password = self.view.get_password_login()

        # Validate email
        if not self._validate_email(email=email):
            return
        
        # Validate password
        if not self._validate_password(password=password):
            return

        # Defining login button state (True if both lineedits has text, else False)
        state = bool(email.strip() and password.strip())

        # Update login button state
        self.view.update_login_button(state=state)


    def on_view_password_login_page_checkbox_state_changed(self):
        state = self.view.get_view_password_login_page_state()
        self.view.set_password_visibalty_login_page(state)


    # Sign Up page
    def on_create_account_signup_page_button_clicked(self) -> None:

        # Get data from lineedits
        email = self.view.get_email_signup()
        password = self.view.get_password_signup()

        # Create worker
        self.api_worker = APIWorker(self.model.signup, email=email, password=password)

        self.api_worker.finished.connect(lambda data: self.signup_user(user_data=data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    def on_have_account_signup_page_button_clicked(self) -> None:
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_signup_page_lineedits_changed(self) -> None:
        # Get texts from lineedits
        email = self.view.get_email_signup()
        password = self.view.get_password_signup()
        confirm_password = self.view.get_confirm_password_signup()
        
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
        self.view.udpate_signup_button(state=state)


    def on_view_password_signup_page_checkbox_state_changed(self):
        state = self.view.get_view_password_signup_page_state()
        self.view.set_password_visibalty_signup_page(state)


    # Change password page
    def on_email_lineedit_change_password_page_text_changed(self) -> None:
        # Get text from lineedit
        email = self.view.get_email_change_password_page()

        # Validate email lineedit
        validate_email_satate = self._validate_email(email=email)

        # Change confirm email button state
        self.view.update_confirm_email_button_state(state=validate_email_satate)


    def on_confirm_email_button_clicked(self) -> None:
        email = self.view.get_email_change_password_page()

        # Create worker
        self.api_worker = APIWorker(self.model.forgot_password, email=email)

        self.api_worker.finished.connect(lambda data: self.open_email_confirm_modal_window(data, email=email))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    def on_do_not_change_password_button_clicked(self) -> None:
        # Switch to login page
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)

        # Clear lineedits
        self.view.change_password_page_cler_lineedits()


    def on_change_password_page_lineedits_changed(self) -> None:
        # Get texts from lineedits
        password = self.view.get_password_change_password_page()
        confirm_password = self.view.get_confirm_password_change_password_page()
        
        # Validate password
        if not self._validate_password(password=password):
            return
        
        # Check password matching
        passwords_match = password == confirm_password

        # Defining signup button state
        state = bool(password.strip() and confirm_password.strip() and passwords_match)

        # Update signup button state
        self.view.update_change_password_button_state(state=state)


    def on_change_password_button_clicked(self) -> None:
        # Get new password
        password = self.view.get_password_change_password_page()

        # Create worker
        self.api_worker = APIWorker(self.model.change_password, password=password)

        self.api_worker.finished.connect(lambda data: self.password_changed(data))
        self.api_worker.error.connect(lambda e: self.worker_error(exception=e))

        self.api_worker.start()


    def on_view_password_change_password_checkbox_state_changed(self):
        state = self.view.get_view_password_change_password_page_state()
        self.view.set_password_visibalty_change_password_page(state)


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