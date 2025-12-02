from .auth_model import AuthModel
from .auth_view import AuthView


class AuthController:
    def __init__(self, model: AuthModel, view: AuthView):
        self.model = model
        self.view = view

        """=== Handlers ==="""
        self.view.theme_switcher_clicked(self.on_theme_switcher_clicked)


    def on_theme_switcher_clicked(self) -> None:
        self.view.set_theme()