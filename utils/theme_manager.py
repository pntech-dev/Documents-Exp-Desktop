from PyQt5.QtWidgets import QApplication


class ThemeManager:
    def __init__(self) -> None:
        self.default_theme = "light"
        self.current_theme = self.default_theme

        self.themes = {
            "light": "ui/styles/light.qss",
            "dark": "ui/styles/dark.qss",
        }
        
        
    def switch_theme(self, theme: str | None = None) -> None:
        if theme is None:
            if self.current_theme == "light":
                self.current_theme = "dark"
            else:
                self.current_theme = "light"
        else:
            self.current_theme = theme

        self._load_theme()


    def _load_theme(self) -> None:
        theme_file = self.themes.get(self.current_theme)

        if theme_file:
            with open(theme_file, "r", encoding="utf-8") as f:
                style = f.read()
            
            QApplication.instance().setStyleSheet(style)