import yaml
import json
import docx
import keyring
import logging

from pathlib import Path

from api.api_client import APIClient


class MainModel:
    def __init__(self) -> None:
        self.config_data = self._load_config()

        # API Client Initialization
        self.api = APIClient(base_url=self.config_data.get("base_url", None))
        
        # Constants
        self.APP_DIR = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp'
        self.LOCAL_DIR = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        self.LOCAL_DIR_LAST_LOGGED = self.LOCAL_DIR / "last_logged.json"

        # Sidebar data
        self.departments = self._get_departments()
        self.current_department_id = self.departments[0]["id"] if self.departments else None
        self.categories = self._get_categories()
        self.current_category_id = self.categories[0]["id"] if self.categories else None

        # Table data
        self.documents = self._get_documents()
        # (x, y): x - id, bool(True, False) if document is page
        self.selected_document = (None, False)



    def get_user_data(self) -> dict | None:
        token = self._get_user_token()

        if not token:
            return None
        
        data = self.api.get_user_data(token)
        
        return data
    

    def get_document_pages(
            self, 
            document_id: int
    ) -> list[dict]:
        pages = self.api.get_document_pages(document_id)
        return pages["pages"]


    def refresh_data(self) -> None:
        """Refreshes the data from the API."""
        self.departments = self._get_departments()
        self.categories = self._get_categories()
        self.documents = self._get_documents()


    def search_data(self, query: str) -> list[dict]:
        """Searches the data based on the provided query."""
        results = []

        if not query:
            return results

        results = self.api.search_data(
            category_id=self.current_category_id, 
            query=query
        )

        return results


    def export_to_docx(
            self, 
            path: str, 
            filename: str, 
            data: dict = None
    ) -> None:
        """Exports the document data to a Word document.

        Args:
            path: The path to save the Word document.
            filename: The name of the Word document.
            data: The document data as a dictionary.
        """
        doc = docx.Document()

        doc.add_heading(f"{data.get('department')} - {data.get('category')}", 1)

        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Код'
        hdr_cells[1].text = 'Наименование'

        for document in data.get("documents", []):
            row_cells = table.add_row().cells
            row_cells[0].text = str(document.get("code", "") or "")
            row_cells[1].text = str(document.get("name", "") or "")

        full_path = Path(path) / filename
        doc.save(str(full_path))


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
        
        
    def _read_json(self, file_path: Path) -> dict | None:
        """Reads and parses a JSON file.

        Args:
            file_path: The path to the JSON file.

        Returns:
            A dictionary with the JSON data or None if the file doesn't exist
            or an error occurs during reading or parsing.
        """
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data
        
        except json.JSONDecodeError:
            logging.error(msg="JSONDecodeError", exc_info=True)
            return None
        
        except Exception as e:
            logging.error(msg=e, exc_info=True)
            return None
        

    def _get_user_token(self) -> str | None:
        last_logged = self._read_json(self.LOCAL_DIR_LAST_LOGGED)

        if not last_logged:
            return None

        user_id = last_logged["user_id"]

        access_token = keyring.get_password(
            service_name="Documents Exp",
            username=f"access_token_{user_id}"
        )

        return access_token
    

    def _get_departments(self) -> list[dict]:
        departments = self.api.get_departments()
        return departments["departments"]


    def _get_categories(self) -> list[dict]:
        categories = self.api.get_categories()
        return categories["categories"]
    

    def _get_documents(self) -> list[dict]:
        documents = self.api.get_documents()
        return documents["documents"]