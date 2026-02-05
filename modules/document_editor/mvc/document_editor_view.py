import json

from pathlib import Path

from ui.custom_widgets import (
    NoFrameButton, PrimaryButton, TertiaryButton
)
from utils import ThemeManagerInstance



class EditorToolBar:
    def __init__(
            self,
            add_page_button: TertiaryButton,
            duplicate_button: NoFrameButton,
            print_button: NoFrameButton,
            import_button: NoFrameButton,
            export_button: NoFrameButton,
            delete_page_button: NoFrameButton,
            icons_config: dict
    ):
        self.add_page_button = add_page_button
        self.duplicate_button = duplicate_button
        self.print_button = print_button
        self.import_button = import_button
        self.export_button = export_button
        self.delete_page_button = delete_page_button
        self.config = icons_config.get("toolbar", {})

        # Set the is_danger property to the delete button
        self.delete_page_button.set_danger(is_danger=True)

        # Setting icon for add page button
        add_page_cfg = self.config.get("add_page", {})
        self.add_page_button.set_icon_paths(
            # light theme
            light_default=add_page_cfg.get("light", {}).get("default"),
            light_hover=add_page_cfg.get("light", {}).get("hover"),
            light_pressed=add_page_cfg.get("light", {}).get("pressed"),
            light_disabled=add_page_cfg.get("light", {}).get("disabled"),

            # dark theme
            dark_default=add_page_cfg.get("dark", {}).get("default"),
            dark_hover=add_page_cfg.get("dark", {}).get("hover"),
            dark_pressed=add_page_cfg.get("dark", {}).get("pressed"),
            dark_disabled=add_page_cfg.get("dark", {}).get("disabled")
        )
        

        # Setting icon for duplicate button
        duplicate_cfg = self.config.get("duplicate", {})
        self.duplicate_button.set_icon_paths(
            # light theme
            light_default=duplicate_cfg.get("light", {}).get("default"),
            light_hover=duplicate_cfg.get("light", {}).get("hover"),
            light_pressed=duplicate_cfg.get("light", {}).get("pressed"),
            light_disabled=duplicate_cfg.get("light", {}).get("disabled"),

            # dark theme
            dark_default=duplicate_cfg.get("dark", {}).get("default"),
            dark_hover=duplicate_cfg.get("dark", {}).get("hover"),
            dark_pressed=duplicate_cfg.get("dark", {}).get("pressed"),
            dark_disabled=duplicate_cfg.get("dark", {}).get("disabled")
        )


        # Setting icon for print button
        print_cfg = self.config.get("print", {})
        self.print_button.set_icon_paths(
            # light theme
            light_default=print_cfg.get("light", {}).get("default"),
            light_hover=print_cfg.get("light", {}).get("hover"),
            light_pressed=print_cfg.get("light", {}).get("pressed"),
            light_disabled=print_cfg.get("light", {}).get("disabled"),

            # dark theme
            dark_default=print_cfg.get("dark", {}).get("default"),
            dark_hover=print_cfg.get("dark", {}).get("hover"), 
            dark_pressed=print_cfg.get("dark", {}).get("pressed"),
            dark_disabled=print_cfg.get("dark", {}).get("disabled")
        )

        # Setting icon for import button
        import_cfg = self.config.get("import", {})
        self.import_button.set_icon_paths(
            # light theme
            light_default=import_cfg.get("light", {}).get("default"),
            light_hover=import_cfg.get("light", {}).get("hover"),
            light_pressed=import_cfg.get("light", {}).get("pressed"),
            light_disabled=import_cfg.get("light", {}).get("disabled"),

            # dark theme
            dark_default=import_cfg.get("dark", {}).get("default"),
            dark_hover=import_cfg.get("dark", {}).get("hover"),
            dark_pressed=import_cfg.get("dark", {}).get("pressed"),
            dark_disabled=import_cfg.get("dark", {}).get("disabled")
        )

        # Setting icon for export button
        export_cfg = self.config.get("export", {})
        self.export_button.set_icon_paths(
            # light theme
            light_default=export_cfg.get("light", {}).get("default"),
            light_hover=export_cfg.get("light", {}).get("hover"),
            light_pressed=export_cfg.get("light", {}).get("pressed"),
            light_disabled=export_cfg.get("light", {}).get("disabled"),

            # dark theme
            dark_default=export_cfg.get("dark", {}).get("default"),
            dark_hover=export_cfg.get("dark", {}).get("hover"), 
            dark_pressed=export_cfg.get("dark", {}).get("pressed"),
            dark_disabled=export_cfg.get("dark", {}).get("disabled")
        )

        # Setting icon for delete page button
        delete_cfg = self.config.get("trash", {})
        self.delete_page_button.set_icon_paths(
            # light theme
            light_default=delete_cfg.get("light", {}).get("default"),
            light_hover=delete_cfg.get("light", {}).get("hover"),
            light_pressed=delete_cfg.get("light", {}).get("pressed"),
            light_disabled=delete_cfg.get("light", {}).get("disabled"),

            # dark theme
            dark_default=delete_cfg.get("dark", {}).get("default"),
            dark_hover=delete_cfg.get("dark", {}).get("hover"),
            dark_pressed=delete_cfg.get("dark", {}).get("pressed"),
            dark_disabled=delete_cfg.get("dark", {}).get("disabled")
        )


    def add_page_button_clicked(self, handler) -> None:
        """Connects the add page button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.add_page_button.clicked.connect(handler)


    def duplicate_button_clicked(self, handler) -> None:
        """Connects the duplicate button click signal to a handler.
        
        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.duplicate_button.clicked.connect(handler)

    
    def print_button_clicked(self, handler) -> None:
        """Connects the print button click signal to a handler.
        
        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.print_button.clicked.connect(handler)


    def import_button_clicked(self, handler) -> None:
        """Connects the import button click signal to a handler.
        
        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.import_button.clicked.connect(handler)


    def export_button_clicked(self, handler) -> None:
        """Connects the export button click signal to a handler.
        
        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.export_button.clicked.connect(handler)


    def delete_page_button_clicked(self, handler) -> None:
        """Connects the delete page button click signal to a handler.
        
        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.delete_page_button.clicked.connect(handler)


class EditorPagesTable:
    """Manages the pages table logic and updates."""

    def __init__(self, table_view) -> None:
        """Initializes the EditorPagesTable manager.

        Args:
            table_view: The custom table view widget for pages.
        """
        self.table_view = table_view
        
        # Default headers configuration
        self.headers = ["", "Наименование", ""]
        self.table_view.set_headers(self.headers)

    def update_pages(self, pages: list[dict]) -> None:
        """Updates the pages table with new items.

        Args:
            pages: A list of dictionaries representing document pages.
        """
        rows = []
        for id, page in enumerate(pages, start=1):
            rows.append((id, [page.get("name", "")]))
        
        self.table_view.set_rows(rows)



class DocumentEditorView:
    def __init__(self, container):
        # UI Initialization
        from ui import DocumentEditor_UI
        self.ui = DocumentEditor_UI()
        self.ui.setupUi(container)
        container.setObjectName("editorContainer")

        self.theme_manager = ThemeManagerInstance()
        self.ui_config = self._load_ui_config()

        icons_config = self.ui_config.get("icons", {})

        # Set the is_danger property to the delete button
        self.ui.delete_document_pushButton.set_danger(is_danger=True)
        
        # Setting icon for close window button
        close_cfg = icons_config.get("close", {})
        self.ui.close_pushButton.set_icon_paths(
            # Light theme
            light_default=close_cfg.get("light", {}).get("default"),
            light_hover=close_cfg.get("light", {}).get("hover"),
            light_pressed=close_cfg.get("light", {}).get("pressed"),
            light_disabled=close_cfg.get("light", {}).get("disabled"),

            # Dark theme
            dark_default=close_cfg.get("dark", {}).get("default"),
            dark_hover=close_cfg.get("dark", {}).get("hover"),
            dark_pressed=close_cfg.get("dark", {}).get("pressed"),
            dark_disabled=close_cfg.get("dark", {}).get("disabled")
        )

        self.toolbar = EditorToolBar(
            add_page_button=self.ui.add_page_pushButton,
            duplicate_button=self.ui.duplicate_pushButton,
            print_button=self.ui.print_pushButton,
            import_button=self.ui.import_pushButton,
            export_button=self.ui.export_pushButton,
            delete_page_button=self.ui.delete_page_pushButton,
            icons_config=icons_config
        )

        self.pages_table = EditorPagesTable(
            table_view=self.ui.data_tableView
        )


    def _load_ui_config(self) -> dict:
        """Loads the UI configuration from the JSON file.

        Returns:
            A dictionary containing the UI configuration, or an empty dict if loading fails.
        """
        try:
            # Resolve path relative to this file location
            root_dir = Path(__file__).resolve().parents[3]
            config_path = root_dir / "ui" / "ui_config.json"
            
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading UI config: {e}")
            return {}


    # --- public API ---

    def cancel_button_clicked(self, handler) -> None:
        """Connects the cancel button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.ui.close_pushButton.clicked.connect(handler)
        self.ui.cancel_pushButton.clicked.connect(handler)