from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QObject

from .auth_view import AuthView
from .auth_model import AuthModel
from core.worker import APIWorker
from utils.fields_validators import FieldValidator
from utils.email_confirm_modal import EmailConfirmDialog


class AuthController(QObject):
    """Orchestrates the authentication UI and logic.

    This controller acts as an intermediary between the authentication view
    (`AuthView`) and the authentication model (`AuthModel`), following the MVC
    pattern. It handles user interactions from the view, such as button clicks
    and text changes, by invoking methods on the model. It initiates
    asynchronous API calls using `APIWorker` for non-blocking operations like
    login, signup, and password reset.

    Signals:
        login_successful (pyqtSignal): Emitted with the login type ('auth' or
            'guest') upon a successful login, signaling the main application to
            proceed.

    Attributes:
        model (AuthModel): The data and business logic component.
        view (AuthView): The UI component for authentication pages.
        auth_window (QMainWindow): The main window containing the auth UI.
        active_workers (set): A set to hold references to running APIWorker
            threads, preventing them from being garbage-collected.
        field_validator (FieldValidator): An instance of the validator for
            input fields like email and password.
    """

    # Successful login signal
    login_successful = pyqtSignal(str)

    def __init__(
            self, 
            model: AuthModel, 
            view: AuthView, 
            window: QMainWindow
    ) -> None:
        """Initializes the AuthController.

        Args:
            model (AuthModel): An instance of the authentication model.
            view (AuthView): An instance of the authentication view.
            window (QMainWindow): The main application window that will host
                the authentication UI.
        """
        super().__init__()
        self.model = model
        self.view = view
        self.auth_window = window

        # Windows
        self.main_module_window = None
        self.email_confirm_window = None

        # Set of active workers
        self.active_workers = set()

        # Initialize field validator
        self.field_validator = FieldValidator()

        # Setup connections
        self._setup_login_connections()
        self._setup_signup_connections()
        self._setup_confirm_email_connections()
        self._setup_reset_password_connections()
        self.view.theme_switcher_clicked(self.on_theme_switcher_clicked)

    
    # ====================
    # Contoller Basic Methods
    # ====================

    
    """=== Login ==="""
    def login_user(self, data: dict) -> None:
        """Handles successful user login.

        This method is called as a success callback after the login API call
        is successfully completed. It saves the user data using the model,
        clears the login form fields, and emits a signal to notify the
        main application to switch to the main module.

        Args:
            data (dict): The user data received from the API upon login.
        """
        # Save user data
        auto_login = self.view.login_page.get_auto_login_state()
        self.model.save_user(user_data=data, auto_login=auto_login)

        # Clear lineedits
        self.view.login_page.clear_lineedits()

        # Switch to main window
        self.login_successful.emit("auth")



    """=== Sign Up ==="""
    def signup_user(self, user_data: dict) -> None:
        """Handles successful user registration.

        This method is called as a success callback after the user has
        successfully signed up and confirmed their email. It saves the new
        user's data, clears the signup form fields, and emits a signal
        to switch to the main application window.

        Args:
            user_data (dict): The user data received from the API upon signup.
        """
        # Save user data
        auto_login = self.view.signup_page.get_auto_login_state()
        self.model.save_user(user_data=user_data, auto_login=auto_login)

        # Clear lineedits
        self.view.signup_page.clear_lineedits()

        # Switch to main window
        self.login_successful.emit("auth")
    

    def signup(self, data: dict, email: str, password: str) -> None:
        """Processes the signup after email verification.

        This method is called after the initial signup request (sending the
        confirmation code) succeeds. It prompts the user to enter the
        verification code via a modal dialog. It then creates and starts a
        worker to finalize the signup process with the provided code.

        Args:
            data (dict): Data from the initial signup request (unused).
            email (str): The user's email address.
            password (str): The user's chosen password.
        """
        print(data)
        code = EmailConfirmDialog.get_code(parent=self.auth_window)

        # Create success callback
        success_cb = lambda data: self.signup_user(user_data=data)

        # Create worker
        self._create_worker(
            method=self.model.signup, 
            success_signal=success_cb, 
            error_signal=self._worker_error, 
            code=code, 
            email=email, 
            password=password
        )


    """=== Reset Password ==="""
    def password_reseted(self, data: dict) -> None:
        """Handles post-password-reset actions.

        This method is called after the user's password has been successfully
        reset. It switches the view back to the login page and clears the
        fields of the password reset form.

        Args:
            data (dict): Data from the password reset API call (unused).
        """
        # Save token
        # Switch to login page
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)

        # Clear lineedits
        self.view.forgot_page_reset_password.clear_lineedits()

        from utils import NotificationService
        NotificationService().show_toast(notification_type="success",
                                         title="Пароль успешно изменён",
                                         message="Ваш пароль успешно изменён!")
        

    def swith_to_reset_password_page(self, data: dict) -> None:
        """Switches to the password reset page after email confirmation.

        This method is called after the user successfully verifies their email
        for a password reset. It saves the necessary reset token and switches
        the UI to the page where the new password can be entered.

        Args:
            data (dict): Data containing the reset token from the API.
        """
        # Save token
        self.model.save_token(token_name="reset_token", token="reset_token", data=data)

        # Switch to change password page
        page = self.view.pages.get("change_password_change_page", None)
        if page:
            self.view.switch_page(page=page)

    
    def open_email_confirm_modal_window(self, data, email: str) -> None:
        """Opens email confirmation dialog for password reset.

        This method is called after a password reset is requested. It opens
        a modal dialog for the user to enter the confirmation code sent to
        their email. It then creates a worker to verify this code.

        Args:
            data (dict): Data from the initial reset request (unused).
            email (str): The email address to which the code was sent.
        """
        print(data)
        code = EmailConfirmDialog.get_code(parent=self.auth_window)

        # Create success callback
        success_cb = lambda data: self.swith_to_reset_password_page(data=data)
        
        # Create worker
        self._create_worker(
            method=self.model.reset_password_confirm_email, 
            success_signal=success_cb, 
            error_signal=self._worker_error, 
            email=email, 
            code=code
        )


    # ====================
    # Contoller Handlers
    # ====================


    """=== Theme ==="""
    def on_theme_switcher_clicked(self) -> None:
        """Handles the theme switcher button click.

        Calls the view's `set_theme` method to toggle between light and dark
        themes for the application.
        """
        self.view.set_theme()



    """=== Login ==="""
    def on_login_page_login_button_clicked(self) -> None:
        """Handles the login button click on the login page.

        Retrieves the email and password from the view, then creates an
        asynchronous worker to perform the login operation via the model.
        """
        # Get data from lineedits
        email = self.view.login_page.get_email()
        password = self.view.login_page.get_password()

        # Create success callback
        success_cb = lambda data: self.login_user(data=data)

        # Create worker
        self._create_worker(
            method=self.model.login, 
            success_signal=success_cb, 
            error_signal=self._worker_error, 
            email=email, 
            password=password
        )

    
    def on_login_page_guest_button_clicked(self) -> None:
        """Handles the 'Continue as Guest' button click.

        Emits the `login_successful` signal with 'guest' as the login type,
        allowing guest access to the application.
        """
        self.login_successful.emit("guest")


    def on_login_page_create_button_clicked(self) -> None:
        """Handles the 'Create Account' button click on the login page.

        Switches the view from the login page to the signup page.
        """
        page = self.view.pages.get("signup_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_login_page_forgot_button_clicked(self, event) -> None:
        """Handles the 'Forgot Password' button click.

        Switches the view to the first page of the password reset flow,
        which prompts the user for their email address.

        Args:
            event: The event object from the button click signal (unused).
        """
        page = self.view.pages.get("change_password_confirm_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_login_page_lineedits_changed(self) -> None:
        """Handles text changes in the login page's input fields.

        Validates the format of the email and password fields. The submit
        button's state is updated to be enabled only if both fields contain
        text and are valid.
        """
        # Get texts from lineedits
        email = self.view.login_page.get_email()
        password = self.view.login_page.get_password()

        # Validate email
        if not self.field_validator.validate_email(email=email):
            return
        
        # Validate password
        if not self.field_validator.validate_password(password=password):
            return

        # Defining login button state (True if both lineedits has text, else False)
        state = bool(email.strip() and password.strip())

        # Update login button state
        self.view.login_page.update_submit_button_state(state=state)


    def on_login_page_view_password_checkbox_state_changed(self):
        """Handles the state change of the 'View Password' checkbox.

        Toggles the visibility of the password text in the login form based on
        the checkbox's state.
        """
        state = self.view.login_page.get_view_password_state()

        self.view.login_page.set_password_visibility(state)



    """=== Signup ==="""
    def on_signup_page_create_button_clicked(self) -> None:
        """Handles the 'Create Account' button click on the signup page.

        Retrieves the email and password from the view, then creates a worker
        to request an email confirmation code from the server.
        """
        # Get data from lineedits
        email = self.view.signup_page.get_email()
        password = self.view.signup_page.get_password()

        # Create success callback
        success_cb = lambda data: self.signup(data=data, email=email, password=password)

        # Create email confirm worker
        self._create_worker(
            method=self.model.signup_send_code, 
            success_signal=success_cb, 
            error_signal=self._worker_error, 
            email=email
        )


    def on_signup_page_have_account_button_clicked(self) -> None:
        """Handles the 'I have an account' button click on the signup page.

        Switches the view from the signup page back to the login page.
        """
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)


    def on_signup_page_lineedits_changed(self) -> None:
        """Handles text changes in the signup page's input fields.

        Validates the email and password fields. The submit button is enabled
        only if all fields are filled, valid, and the password matches the
        confirmation password.
        """
        # Get texts from lineedits
        email = self.view.signup_page.get_email()
        password = self.view.signup_page.get_password()
        confirm_password = self.view.signup_page.get_confirm_password()
        
        # Validate email
        if not self.field_validator.validate_email(email=email):
            return
        
        # Validate password
        if not self.field_validator.validate_password(password=password):
            return

        # Check password matching
        passwords_match = password == confirm_password

        # Defining signup button state
        state = bool(email.strip() and password.strip() and confirm_password.strip() and passwords_match)

        # Update signup button state
        self.view.signup_page.update_submit_button_state(state=state)


    def on_view_password_signup_page_checkbox_state_changed(self):
        """Handles the 'View Password' checkbox state change on the signup page.

        Toggles the visibility of both the password and confirm password
        fields based on the checkbox's state.
        """
        state = self.view.signup_page.get_view_password_state()

        self.view.signup_page.set_password_visibility(state)



    """=== Reset Password ==="""
    def on_confirm_email_page_confirm_button_clicked(self) -> None:
        """Handles the confirm button click for password reset.

        Retrieves the email from the view and creates a worker to request a
        password reset code from the server.
        """
        email = self.view.forgot_page_email_confirm.get_email()

        # Create success callback
        success_cb = lambda data: self.open_email_confirm_modal_window(data=data, email=email)

        # Create worker
        self._create_worker(
            method=self.model.request_reset_password, 
            success_signal=success_cb, 
            error_signal=self._worker_error, 
            email=email
        )

    def on_email_confirm_page_email_lineedit_text_changed(self) -> None:
        """Handles text changes in the email field on the password reset page.

        Validates the email format and enables the submit button only if the
        email is valid.
        """
        # Get text from lineedit
        email = self.view.forgot_page_email_confirm.get_email()

        # Validate email lineedit
        validate_email_satate = self.field_validator.validate_email(email=email)

        # Change confirm email button state
        self.view.forgot_page_email_confirm.update_submit_button_state(state=validate_email_satate)


    def on_reset_password_page_back_button_clicked(self) -> None:
        """Handles the cancel button click during the password reset flow.

        Switches the view back to the login page and clears any input from
        the email confirmation form.
        """
        # Switch to login page
        page = self.view.pages.get("login_page", None)
        if page:
            self.view.switch_page(page=page)

        # Clear lineedits
        self.view.forgot_page_email_confirm.clear_lineedits()


    def on_reset_password_page_lineedits_changed(self) -> None:
        """Handles text changes in the new password and confirm password fields.

        Validates the password fields. The submit button is enabled only if
        both fields are filled, valid, and the passwords match.
        """
        # Get texts from lineedits
        password = self.view.forgot_page_reset_password.get_password()
        confirm_password = self.view.forgot_page_reset_password.get_confirm_password()
        
        # Validate password
        if not self.field_validator.validate_password(password=password):
            return
        
        # Check password matching
        passwords_match = password == confirm_password

        # Defining signup button state
        state = bool(password.strip() and confirm_password.strip() and passwords_match)

        # Update signup button state
        self.view.forgot_page_reset_password.update_submit_button_state(state=state)


    def on_reset_password_page_reset_button_clicked(self) -> None:
        """Handles the final 'Change Password' button click.

        Retrieves the new password from the view and creates a worker to
        submit the new password to the server.
        """
        # Get new password
        password = self.view.forgot_page_reset_password.get_password()

        # Create success callback
        success_cb = lambda data: self.password_reseted(data=data)

        # Create worker
        self._create_worker(
            method=self.model.reset_password, 
            success_signal=success_cb, 
            error_signal=self._worker_error, 
            password=password
        )


    def on_reset_password_view_password_checkbox_state_changed(self):
        """Handles the 'View Password' checkbox on the password change page.

        Toggles the visibility of the new password and confirm password fields
        based on the checkbox's state.
        """
        state = self.view.forgot_page_reset_password.get_view_password_state()
        self.view.forgot_page_reset_password.set_password_visibility(state)


    # ====================
    # Controller methods
    # ====================


    """=== Setup connections ==="""
    def _setup_login_connections(self) -> None:
        """Connects signals from the login page widgets to controller handlers."""
        # Get login page
        login_page = self.view.login_page

        # Connect signals to handlers
        login_page.submit_button_clicked(self.on_login_page_login_button_clicked)
        login_page.back_button_clicked(self.on_login_page_guest_button_clicked)
        login_page.tertiary_button_clicked(self.on_login_page_create_button_clicked)
        login_page.forgot_password_button_clicked(self.on_login_page_forgot_button_clicked)
        login_page.view_password_checkbox_state_changed(self.on_login_page_view_password_checkbox_state_changed)
        login_page.email_lineedit_text_changed(self.on_login_page_lineedits_changed)
        login_page.password_lineedit_text_changed(self.on_login_page_lineedits_changed)


    def _setup_signup_connections(self) -> None:
        """Connects signals from the signup page widgets to controller handlers."""
        # Get signup page
        signup_page = self.view.signup_page

        # Connect signals to handlers
        signup_page.submit_button_clicked(self.on_signup_page_create_button_clicked)
        signup_page.back_button_clicked(self.on_signup_page_have_account_button_clicked)
        signup_page.view_password_checkbox_state_changed(self.on_view_password_signup_page_checkbox_state_changed)
        signup_page.email_lineedit_text_changed(self.on_signup_page_lineedits_changed)
        signup_page.password_lineedit_text_changed(self.on_signup_page_lineedits_changed)
        signup_page.confirm_password_lineedit_text_changed(self.on_signup_page_lineedits_changed)


    def _setup_confirm_email_connections(self) -> None:
        """Connects signals from the email confirmation page to controller handlers."""
        # Get confirm email page
        email_confirm_page = self.view.forgot_page_email_confirm

        # Connect signals to handlers
        email_confirm_page.submit_button_clicked(self.on_confirm_email_page_confirm_button_clicked)
        email_confirm_page.back_button_clicked(self.on_reset_password_page_back_button_clicked)
        email_confirm_page.email_lineedit_text_changed(self.on_email_confirm_page_email_lineedit_text_changed)

    
    def _setup_reset_password_connections(self) -> None:
        """Connects signals from the password reset page to controller handlers."""
        # Get reset password page
        reset_password_page = self.view.forgot_page_reset_password
        
        # Connect signals to handlers
        reset_password_page.submit_button_clicked(self.on_reset_password_page_reset_button_clicked)
        reset_password_page.back_button_clicked(self.on_reset_password_page_back_button_clicked)
        reset_password_page.view_password_checkbox_state_changed(self.on_reset_password_view_password_checkbox_state_changed)
        reset_password_page.password_lineedit_text_changed(self.on_reset_password_page_lineedits_changed)
        reset_password_page.confirm_password_lineedit_text_changed(self.on_reset_password_page_lineedits_changed)

    
    
    """=== API Worker ==="""
    def _create_worker(
        self, 
        method: callable, 
        success_signal: callable, 
        error_signal: callable, 
        **kwargs
    ) -> None:
        """Creates, configures, and starts a new APIWorker thread.

        This factory method encapsulates the creation and management of an
        APIWorker for performing asynchronous API calls. It connects the
        worker's `finished` and `error` signals to the provided callbacks.
        The worker object is added to the `active_workers` set to prevent
        premature garbage collection and is automatically removed upon
        completion.

        Args:
            method (callable): The model's method to be executed in the worker
                thread.
            success_signal (callable): The callback function to execute upon
                successful completion. It receives the data returned by the
                worker.
            error_signal (callable): The callback function to execute when an
                error occurs. It receives the exception object.
            **kwargs: Arbitrary keyword arguments to be passed to the `method`
                when it's called.
        """
        # Create a new APIWorker instance
        worker = APIWorker(method, **kwargs)

        # Connect the worker's signals to the provided success and error signals
        worker.finished.connect(success_signal)
        worker.error.connect(error_signal)

        # Delete the worker from active workers when it finishes
        worker.finished.connect(lambda: self.active_workers.discard(worker))
        worker.error.connect(lambda: self.active_workers.discard(worker))

        # Add the worker to active workers
        self.active_workers.add(worker)

        # Start the worker
        worker.start()
        

    def _worker_error(self, exception: Exception) -> None:
        """Handles errors reported by APIWorker threads.

        This method is connected to the `error` signal of all workers.
        Currently, it prints the exception to the console. For production,
        it should display a user-friendly error message.

        Args:
            exception (Exception): The exception object caught by the worker.
        """
        print(exception)