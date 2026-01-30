import json
import yaml
import logging

from pathlib import Path
from jinja2 import Template
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ThemeManager(QObject):
    """A universal theme manager for PyQt applications.

    This class handles loading UI configuration, checking theme availability,
    compiling Jinja2 templates to QSS stylesheets, switching between themes,
    and applying the final styles to the QApplication instance.

    Attributes:
        ui_config (dict): The loaded UI configuration from JSON.
        themes (dict[str, str]): A dictionary mapping theme IDs to theme names.
        current_theme_id (str): The ID of the currently active theme.
    """

    themeChanged = pyqtSignal(str)

    def __init__(self) -> None:
        """Initializes the ThemeManager.

        Loads the UI configuration, normalizes theme keys, and sets the default
        theme ID. If the configuration is missing or empty, the manager is
        disabled.
        """
        super().__init__()

        self.ui_config = self._load_ui_config()

        # If the config is empty, we don't do anything.
        if not self.ui_config:
            logger.error("UI configuration is empty. ThemeManager disabled.")
            self.themes = {}
            self.current_theme_id = "0"
            return

        # Normalize the keys to strings
        self.themes: dict[str, str] = {
            str(k): v for k, v in self.ui_config.get("themes", {}).items()
        }

        self.current_theme_id = "0"  # The topic ID as a string

    @property
    def notification_config(self) -> dict:
        """Returns the notification-specific configuration."""
        return self.ui_config.get("notifications", {})

    # ---------------------------
    # PUBLIC API
    # ---------------------------

    def switch_theme(self, theme: int | str | None = None) -> None:
        """Switches the application theme.

        If `theme` is provided, it switches to the specified theme.
        If `theme` is None, it toggles between the default themes ("0" and "1").

        Args:
            theme: The ID of the theme to switch to. Can be an int or a string.
                   If None, toggles between the primary themes.
        """
        try:
            if theme is None:
                self.current_theme_id = "1" if self.current_theme_id == "0" else "0"
            else:
                theme_str = str(theme)
                if theme_str in self.themes:
                    self.current_theme_id = theme_str
                else:
                    logger.error(f"Theme {theme} not found in config.")
                    return

            self._apply_theme()
            
            self.themeChanged.emit(self.current_theme_id)

        except Exception as e:
            logger.error(f"Unexpected error during theme switching: {e}")

    # ---------------------------
    # CONFIG LOADING
    # ---------------------------

    def _load_ui_config(self) -> dict:
        """Loads the UI configuration from YAML and JSON files.

        First, it reads `config.yaml` to find the path to the UI configuration
        file. Then, it loads the specified JSON file.

        Returns:
            A dictionary containing the UI configuration, or an empty dict if
            loading fails at any stage.
        """

        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                base_config = yaml.safe_load(f)

            path = base_config.get("ui_config_path")
            if not path:
                logger.error("ui_config_path not found in config.yaml.")
                return {}

            with open(path, "r", encoding="utf-8") as f:
                ui_config = json.load(f)

            return ui_config or {}

        except FileNotFoundError:
            logger.error("config.yaml or UI config file not found.")
        except yaml.YAMLError as e:
            logger.error(f"YAML parse error: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
        except Exception as e:
            logger.error(f"Unexpected config loading error: {e}")

        return {}

    # ---------------------------
    # THEME APPLY
    # ---------------------------

    def _apply_theme(self) -> None:
        """Applies the current theme's QSS stylesheet to the QApplication.

        Ensures the theme is availabel and its QSS file exists, then reads the
        stylesheet and applies it to the running QApplication instance.
        """

        if not self._validate_theme_availabel():
            return

        theme_name = self.themes[self.current_theme_id]
        themes_path = Path(self.ui_config["paths"]["themes_path"])
        theme_file = themes_path / f"{theme_name}.qss"

        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                style = f.read()

            app = QApplication.instance()
            if not app:
                logger.error("QApplication is not running. Stylesheet not applied.")
                return

            app.setStyleSheet(style)
            logger.info(f"Theme '{theme_name}' applied successfully.")

        except Exception as e:
            logger.error(f"Error applying theme: {e}")

    # ---------------------------
    # VALIDATION
    # ---------------------------

    def _validate_theme_availabel(self) -> bool:
        """Validates that the current theme and its QSS file exist.

        Checks for the theme ID, theme name, and the existence of the themes
        directory. If the QSS file is missing, it attempts to compile all themes
        from their Jinja2 templates.

        Returns:
            True if the theme is valid and the QSS file is availabel (or was
            successfully compiled), False otherwise.
        """

        theme_id = self.current_theme_id
        theme_name = self.themes.get(theme_id)

        if not theme_name:
            logger.error(f"Theme ID '{theme_id}' not found.")
            return False

        themes_path = Path(self.ui_config["paths"]["themes_path"])
        if not themes_path.exists():
            logger.error(f"Themes directory missing: {themes_path}")
            return False

        # If the folder is empty, we try compiling all the themes.
        theme_files = list(themes_path.glob("*.qss"))
        if not theme_files:
            logger.warning("No QSS themes found. Compiling all themes...")
            return self._compile_all_themes()

        # Checking the current QSS
        theme_file = themes_path / f"{theme_name}.qss"
        if not theme_file.exists():
            logger.warning(f"Theme file '{theme_file}' missing. Trying to compile...")
            return self._compile_all_themes()

        return True

    # ---------------------------
    # COMPILATION
    # ---------------------------

    def _compile_all_themes(self) -> bool:
        """Compiles all Jinja2 theme templates into QSS stylesheets.

        Reads all `.j2` files from the templates directory, renders them using
        tokens defined in the UI configuration, and saves the output as
        `.qss` files in the themes directory.

        Returns:
            True if all templates were compiled successfully, False if any
            part of the process fails.
        """

        try:
            t_path = Path(self.ui_config["paths"]["templates_path"])
            if not t_path.exists():
                logger.error(f"Templates folder does not exist: {t_path}")
                return False

            themes_path = Path(self.ui_config["paths"]["themes_path"])
            themes_path.mkdir(parents=True, exist_ok=True)

            templates = list(t_path.glob("*.j2"))
            if not templates:
                logger.error(f"No templates in: {t_path}")
                return False

            for tmpl_path in templates:
                theme_name = tmpl_path.stem
                tokens = self.ui_config["tokens"].get(f"{theme_name}_theme")

                if tokens is None:
                    logger.error(f"No tokens for theme '{theme_name}'. Skipping.")
                    continue

                with open(tmpl_path, "r", encoding="utf-8") as f:
                    template = Template(f.read())

                qss_output = template.render(**tokens)
                out_file = themes_path / f"{theme_name}.qss"

                with open(out_file, "w", encoding="utf-8") as f:
                    f.write(qss_output)

            logger.info("All themes compiled successfully.")
            return True

        except Exception as e:
            logger.error(f"Theme compilation error: {e}")
            return False
        

theme_manager_singleton = ThemeManager()


def ThemeManagerInstance():
    return theme_manager_singleton