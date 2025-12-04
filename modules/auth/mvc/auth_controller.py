from .auth_model import AuthModel
from .auth_view import AuthView


class AuthController:
    def __init__(self, model: AuthModel, view: AuthView):
        self.model = model
        self.view = view

        """=== Handlers ==="""
        self.view.theme_switcher_clicked(self.on_theme_switcher_clicked)
        self.view.create_account_button_clicked(self.on_create_account_button_clicked)
        self.view.change_password_button_clicked(self.on_change_password_button_clicked)
        self.view.have_account_create_button_clicked(self.on_have_account_create_button_clicked)
        self.view.have_account_password_button_clicked(self.on_have_account_password_button_clicked)

    """=== Handlers ==="""

    def on_theme_switcher_clicked(self) -> None:
        self.view.set_theme()

    # Login page

    def on_create_account_button_clicked(self) -> None:
        page = self.view.pages.get("signup_page", None)
        if not page is None:
            self.view.switch_page(page=page)

    
    def on_change_password_button_clicked(self, event) -> None:
        page = self.view.pages.get("change_password_confirm_page", None)
        if not page is None:
            self.view.switch_page(page=page)

    # Create account page

    def on_have_account_create_button_clicked(self) -> None:
        page = self.view.pages.get("login_page", None)
        if not page is None:
            self.view.switch_page(page=page)

    # Change password page

    def on_have_account_password_button_clicked(self) -> None:
        page = self.view.pages.get("login_page", None)
        if not page is None:
            self.view.switch_page(page=page)