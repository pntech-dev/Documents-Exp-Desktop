import json
import yaml
from jinja2 import Template
from PyQt5.QtWidgets import QApplication


class ThemeManager:
    def __init__(self) -> None:
        self.ui_config_data = self._load_config()

        self.default_theme = "light"
        self.current_theme = self.default_theme

        self.themes = {
            "light": "ui/styles/light.qss",
            "dark": "ui/styles/dark.qss"
        }
        
    def switch_theme(self) -> None:
        if self.current_theme == "light":
            self.current_theme = "dark"
        else:
            self.current_theme = "light"

        # self._load_theme()


    # def _load_theme(self) -> None:
        # ui_config = r"ui\ui_config.json"
        # light_jinja2 = r"ui\styles\light.qss.j2"

        # with open(ui_config) as f:
        #     tokens = json.load(f)

        # with open(light_jinja2) as f:
        #     template = Template(f.read())

        # tokens = tokens['tokens']['light_theme']['neutral']
        # qss = template.render(**tokens)

        # light = r"ui/styles/light.qss"

        # with open(light, "w") as out:
        #     out.write(qss)

        # with open(self.themes['light'], "r", encoding="utf-8") as f:
        #         style = f.read()
                
        # QApplication.instance().setStyleSheet(style)

    def _load_config(self) -> dict:
        try:
            # Get UI config path from YAML config file
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)
                ui_config_path = config.get('ui_config_path', None)

            if ui_config_path is None: # If UI config path is not found
                return {}
            
            # Load UI configuration from JSON file
            with open(ui_config_path, 'r') as f:
                ui_config_data = json.load(f)

            if not ui_config_data: # If UI config data is empty
                return {}
            
            return ui_config_data
        
        except FileNotFoundError:
            print("Configuration file not found.")
            return {}
        
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            return {}
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {}