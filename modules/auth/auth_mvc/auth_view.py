from utils import ThemeManager

from ui import AuthWindow_UI


class AuthView:
    def __init__(self, ui: AuthWindow_UI):
        self.ui = ui
        self.theme_manager = ThemeManager()

    def set_theme(self) -> None:
        """Set theme"""
        self.theme_manager.switch_theme()
    
    def theme_switcher_clicked(self, handler) -> None:
        """Switch theme on click theme switcher button"""
        self.ui.theme_button.clicked.connect(handler)