import yaml

from pathlib import Path

from api.api_client import APIClient



class DocumentEditorModel:
    def __init__(
            self, 
            document_data: dict = None, 
            pages: list[dict] = None
    ) -> None:
        self.document_data = document_data
        self.pages = pages

        self.config_data = self._load_config()

        # API Client Initialization
        self.api = APIClient(base_url=self.config_data.get("base_url", None))

        self.is_document_edited = False

    
    def save_document(self, data: dict) -> None:
        self.api.update_document(
            document_id=self.document_data.get("id"), 
            data=data
        )


    # ====================
    # Model Methods
    # ====================

    
    def _load_config(self) -> dict:
        try:
            config_path = Path(Path.cwd(), "config.yaml")

            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)

            return config
        
        except FileNotFoundError:
            print("Configuration file not found.")
            return {}
        
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            return {}
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {}