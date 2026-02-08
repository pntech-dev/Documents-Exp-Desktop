import docx
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

        # Constants
        self.APP_DIR = Path.home() / 'AppData' / 'Roaming' / 'Documents Exp'
        self.LOCAL_DIR = Path.home() / 'AppData' / 'Local' / 'Documents Exp'
        self.LOCAL_DIR_LAST_LOGGED = self.LOCAL_DIR / "last_logged.json"

        # API Client Initialization
        self.api = APIClient(base_url=self.config_data.get("base_url", None))

        self.is_document_edited = False

    
    def save_document(self, data: dict) -> None:
        self.api.update_document(
            document_id=self.document_data.get("id"), 
            data=data
        )


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

        if data:
            code = data.get("code", "")
            name = data.get("name", "")
            pages = data.get("pages", [])
        else:
            code = self.document_data.get("code", "")
            name = self.document_data.get("name", "")
            pages = self.pages
            pages.sort(key=lambda x: x.get("order_index", 0))

        doc.add_heading(f"{code} - {name}", 1)

        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'

        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'Наименование'
        hdr_cells[1].text = 'Код'

        for page in pages:
            row_cells = table.add_row().cells
            row_cells[0].text = str(page.get("name", "") or "")
            row_cells[1].text = str(page.get("designation", "") or "")

        full_path = Path(path) / filename
        doc.save(str(full_path))


    def import_from_docx(self, file_path: str) -> list[dict]:
        """Imports pages from a Word document."""
        doc = docx.Document(file_path)
        pages = []

        for table in doc.tables:
            if not table.rows:
                continue
            
            # Check headers in the first row
            headers = [cell.text.strip() for cell in table.rows[0].cells]
            if len(headers) != 2:
                continue
            
            if "Наименование" in headers and "Код" in headers:
                name_index = headers.index("Наименование")
                code_index = headers.index("Код")

                # Iterate over data rows
                for row in table.rows[1:]:
                    cells = row.cells
                    if len(cells) > max(name_index, code_index):
                        pages.append({
                            "id": None, # New page has no ID
                            "name": cells[name_index].text.strip(),
                            "designation": cells[code_index].text.strip()
                        })
                
                # Stop after finding and processing the first valid table
                if pages:
                    break
        
        return pages


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