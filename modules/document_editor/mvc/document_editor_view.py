import json

from pathlib import Path
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QTabWidget, QScrollArea, QFrame

from ui.custom_widgets import (
    NoFrameButton, PrimaryButton, TertiaryButton, FileDropWidget, FileListWidget
)
from utils import ThemeManagerInstance
from utils.app_paths import get_app_root


ROLE_CHECK_STATE = Qt.UserRole + 1


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


    def update_duplicate_page_button_state(self, state: bool) -> None:
        """Updates the duplicate page button state."""
        self.duplicate_button.setEnabled(state)


    def update_delete_button_state(self, state: bool) -> None:
        """Updates the delete page button state."""
        self.delete_page_button.setEnabled(state)


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
        self.headers = ["", "Наименование", "Код", ""]
        self.table_view.set_headers(self.headers)

    def update_pages(self, pages: list[dict]) -> None:
        """Updates the pages table with new items.

        Args:
            pages: A list of dictionaries representing document pages.
        """
        rows = []
        for page in pages:
            rows.append(
                (
                    page.get("id"),
                    page.get("name", ""),
                    page.get("designation", "")
                )
            )
        
        self.table_view.set_rows(rows)

    def get_pages(self) -> list[dict]:
        """Returns the list of pages from the table."""
        pages = []
        model = self.table_view.model()
        for row in range(model.rowCount()):
            item_id = model.item(row, 0).data(Qt.UserRole)

            name = model.item(row, 1).text()
            designation = model.item(row, 2).text()
            
            pages.append({
                "id": item_id,
                "order_index": row,
                "designation": designation,
                "name": name
            })

        return pages

    def add_new_page(self) -> None:
        """Adds a new empty page row at the top and starts editing."""
        model = self.table_view.model()
        
        # 1. Checkbox Column
        check_item = QStandardItem()
        check_item.setData(Qt.Unchecked, ROLE_CHECK_STATE)
        check_item.setEditable(False)
        check_item.setDropEnabled(False)
        check_item.setData(None, Qt.UserRole) 
        
        # 2. Name Column
        name_item = QStandardItem("")
        name_item.setEditable(True)
        name_item.setDropEnabled(False)

        # 3. Designation Column
        designation_item = QStandardItem("")
        designation_item.setEditable(True)
        designation_item.setDropEnabled(False)
        
        # 4. Drag Handle Column
        drag_item = QStandardItem()
        drag_item.setEditable(False)
        drag_item.setDropEnabled(False)
        
        items = [check_item, name_item, designation_item, drag_item]
        
        # Insert at top
        model.insertRow(0, items)
        
        # Scroll to top
        self.table_view.scrollToTop()
        
        # Start editing name column
        index = model.index(0, 1)
        self.table_view.setCurrentIndex(index)
        self.table_view.edit(index)


    def delete_selected_pages(self) -> None:
        """Deletes selected or checked pages from the table."""
        model = self.table_view.model()
        rows_to_delete = set()

        # 1. Get checked rows
        for row in range(model.rowCount()):
            if model.item(row, 0).data(ROLE_CHECK_STATE) == Qt.Checked:
                rows_to_delete.add(row)

        # 2. Get selected rows
        selection_model = self.table_view.selectionModel()
        if selection_model.hasSelection():
            for index in selection_model.selectedRows():
                rows_to_delete.add(index.row())

        # Delete rows in reverse order to maintain indices
        for row in sorted(rows_to_delete, reverse=True):
            model.removeRow(row)
        
        self.table_view.clearSelection()


    def duplicate_selected_pages(self) -> None:
        """Duplicates selected or checked pages."""
        model = self.table_view.model()
        rows_to_duplicate = set()

        # 1. Get checked rows
        for row in range(model.rowCount()):
            if model.item(row, 0).data(ROLE_CHECK_STATE) == Qt.Checked:
                rows_to_duplicate.add(row)

        # 2. Get selected rows
        selection_model = self.table_view.selectionModel()
        if selection_model.hasSelection():
            for index in selection_model.selectedRows():
                rows_to_duplicate.add(index.row())

        # Clear selection before adding new rows
        self.table_view.clearSelection()

        # Duplicate rows in reverse order to maintain indices relative to originals
        for row in sorted(rows_to_duplicate, reverse=True):
            # Get original data
            original_check_state = model.item(row, 0).data(ROLE_CHECK_STATE)
            original_name = model.item(row, 1).text()
            original_designation = model.item(row, 2).text()
            
            # Create new items
            # 1. Checkbox Column
            check_item = QStandardItem()
            check_item.setData(original_check_state, ROLE_CHECK_STATE)
            check_item.setEditable(False)
            check_item.setDropEnabled(False)
            check_item.setData(None, Qt.UserRole) # No ID for new page
            
            # 2. Name Column
            name_item = QStandardItem(original_name)
            name_item.setEditable(True)
            name_item.setDropEnabled(False)

            # 3. Designation Column
            designation_item = QStandardItem(original_designation)
            designation_item.setEditable(True)
            designation_item.setDropEnabled(False)
            
            # 4. Drag Handle Column
            drag_item = QStandardItem()
            drag_item.setEditable(False)
            drag_item.setDropEnabled(False)
            
            items = [check_item, name_item, designation_item, drag_item]
            
            # Insert below the original row
            insert_row = row + 1
            model.insertRow(insert_row, items)

            # Select the new row
            selection_model.select(
                model.index(insert_row, 0), 
                QItemSelectionModel.Select | QItemSelectionModel.Rows
            )


    def has_selection_or_checks(self) -> bool:
        """Checks if any row is selected or any checkbox is checked."""
        if self.table_view.selectionModel().hasSelection():
            return True
            
        model = self.table_view.model()
        for row in range(model.rowCount()):
            if model.item(row, 0).data(ROLE_CHECK_STATE) == Qt.Checked:
                return True
        return False


    def connect_selection_changed(self, handler) -> None:
        """Connects the selection changed signal to a handler."""
        if self.table_view.selectionModel():
            self.table_view.selectionModel().selectionChanged.connect(handler)


    def connect_item_changed(self, handler) -> None:
        """Connects the item changed signal to a handler."""
        self.table_view.model().itemChanged.connect(handler)


    def connect_row_moved(self, handler) -> None:
        """Connects the row moved signal to a handler."""
        self.table_view.rowMoved.connect(handler)


class EditorFilesTab:
    def __init__(self, tab_widget: QTabWidget) -> None:
        self.tab_widget = tab_widget

        # Setup Files Tab Layout
        files_layout = self.tab_widget.layout()
        
        # 1. Drag & Drop Area
        self.file_drop_widget = FileDropWidget(self.tab_widget)
        files_layout.addWidget(self.file_drop_widget)
        
        # 2. Scroll Area for File Widgets
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.scroll_area.setAutoFillBackground(False)
        self.scroll_area.viewport().setAutoFillBackground(False)
        self.scroll_area.setAutoFillBackground(False)
        
        # Container for FileListWidget to allow centering/alignment if needed
        self.file_list = FileListWidget()
        
        self.scroll_area.setWidget(self.file_list)
        files_layout.addWidget(self.scroll_area)


    def connect_drag_drop_area(self, handler) -> None:
        """Connects the drag and drop area to a handler."""
        self.file_drop_widget.clicked.connect(handler)


    def connect_files_dropped(self, handler) -> None:
        """Connects the files dropped signal."""
        self.file_drop_widget.filesDropped.connect(handler)


    def connect_file_deleted(self, handler) -> None:
        """Connects the file deleted signal."""
        self.file_list.fileDeleted.connect(handler)


    def add_file_widget(self, file_data: object) -> None:
        """Adds a file widget to the list."""
        self.file_list.add_file(file_data)


    def remove_file_widget(self, file_identifier: object) -> None:
        """Removes a file widget from the list."""
        self.file_list.remove_file(file_identifier)


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

        # Set the is_danger property to the generate tags and delete button
        self.ui.generate_tags_pushButton.set_danger(is_danger=True)
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

        # Setting icon for generate tags button
        generate_tags_cfg = icons_config.get("stick", {})
        self.ui.generate_tags_pushButton.set_icon_paths(
            # Light theme
            light_default=generate_tags_cfg.get("light", {}).get("default"),
            light_hover=generate_tags_cfg.get("light", {}).get("hover"),
            light_pressed=generate_tags_cfg.get("light", {}).get("pressed"),
            light_disabled=generate_tags_cfg.get("light", {}).get("disabled"),

            # Dark theme
            dark_default=generate_tags_cfg.get("dark", {}).get("default"),
            dark_hover=generate_tags_cfg.get("dark", {}).get("hover"),
            dark_pressed=generate_tags_cfg.get("dark", {}).get("pressed"),
            dark_disabled=generate_tags_cfg.get("dark", {}).get("disabled")
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

        self.files_tab = EditorFilesTab(
            tab_widget=self.ui.files_tab
        )


    def _load_ui_config(self) -> dict:
        """Loads the UI configuration from the JSON file.

        Returns:
            A dictionary containing the UI configuration, or an empty dict if loading fails.
        """
        try:
            config_path = get_app_root() / "ui" / "ui_config.json"
            
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading UI config: {e}")
            return {}


    # --- public API ---

    def add_new_page(self) -> None:
        """Adds a new page to the table."""
        self.pages_table.add_new_page()


    def has_selected_pages(self) -> bool:
        """Checks if any page is selected or checked."""
        return self.pages_table.has_selection_or_checks()


    def delete_selected_pages(self) -> None:
        """Deletes selected or checked pages."""
        self.pages_table.delete_selected_pages()

    
    def duplicate_selected_pages(self) -> None:
        """Duplicates selected or checked pages."""
        self.pages_table.duplicate_selected_pages()


    def get_document_data(self) -> dict:
        data = {
            "code": self.ui.document_code_lineEdit.text(),
            "name": self.ui.document_name_lineEdit.text(),
            "tags": self.ui.tags_lineedit_frame.get_tags(),
            "pages": self.pages_table.get_pages()
        }
        
        return data
    

    def update_generate_button_state(self, state: bool) -> None:
        """Updates the generate tags button state."""
        self.ui.generate_tags_pushButton.setEnabled(state)
    

    def update_duplicate_button_state(self, state: bool) -> None:
        """Updates the duplicate page button state."""
        self.toolbar.update_duplicate_page_button_state(state)


    def update_delete_page_button_state(self, state: bool) -> None:
        """Updates the delete page button state."""
        self.toolbar.update_delete_button_state(state=state)


    def update_save_button_state(self, state: bool) -> None:
        """Updates the save document button state."""
        self.ui.save_pushButton.setEnabled(state)

    
    def set_mode_visibility(self, can_edit: bool, is_creation: bool = False) -> None:
        """Sets the mode visibility."""
        if not can_edit:
            self.ui.title_label.setText("Просмотр документа")
        elif is_creation:
            self.ui.title_label.setText("Создание документа")
            self.ui.save_pushButton.setText("Создать документ")
        else:
            self.ui.title_label.setText("Редактор документа")
            self.ui.save_pushButton.setText("Сохранить изменения")

        self.ui.document_code_lineEdit.setReadOnly(not can_edit)
        self.ui.document_name_lineEdit.setReadOnly(not can_edit)
        self.ui.toolbar_frame.setVisible(can_edit)
        self.ui.buttons_frame.setVisible(can_edit)
        self.ui.delete_document_pushButton.setVisible(not is_creation)

    
    def set_document_tags(self, tags: list[str]) -> None:
        """Sets the document tags.

        Args:
            tags: A list of tags as strings.
        """
        for tag in tags:
            self.ui.tags_lineedit_frame.add_tag(tag)


    def set_document_code(self, code: str) -> None:
        """Sets the document code.

        Args:
            code: The document code as a string.
        """
        self.ui.document_code_lineEdit.setText(code)


    def set_document_name(self, name: str) -> None:
        """Sets the document name.

        Args:
            name: The document name as a string.
        """
        self.ui.document_name_lineEdit.setText(name)


    def code_lineedit_text_changed(self, handler) -> None:
        """Connects the code line edit text changed signal to a handler.

        Args:
            handler: The callback function to execute when the text changes.
        """
        self.ui.document_code_lineEdit.textChanged.connect(handler)


    def name_lineedit_text_changed(self, handler) -> None:
        """Connects the name line edit text changed signal to a handler.

        Args:
            handler: The callback function to execute when the text changes.
        """
        self.ui.document_name_lineEdit.textChanged.connect(handler)


    def tags_lineedit_text_changed(self, handler) -> None:
        """Connects the tags line edit text changed signal to a handler.

        Args:
            handler: The callback function to execute when the text changes.
        """
        self.ui.tags_lineedit_frame.tagsChanged.connect(handler)


    def generate_tags_button_clicked(self, handler) -> None:
        """Connects the generate tags button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.ui.generate_tags_pushButton.clicked.connect(handler)

    
    def toolbar_add_page_button_clicked(self, handler) -> None:
        """Connects the add page button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.toolbar.add_page_button_clicked(handler)


    def toolbar_duplicate_page_button_clicked(self, handler) -> None:
        """Connects the duplicate page button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.toolbar.duplicate_button_clicked(handler)

    
    def toolbar_print_button_clicked(self, handler) -> None:
        """Connects the print button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.toolbar.print_button_clicked(handler)


    def toolbar_import_button_clicked(self, handler) -> None:
        """Connects the import button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.toolbar.import_button_clicked(handler)


    def toolbar_export_button_clicked(self, handler) -> None:
        """Connects the export button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.toolbar.export_button_clicked(handler)

    
    def toolbar_delete_page_button_clicked(self, handler) -> None:
        """Connects the delete page button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.toolbar.delete_page_button_clicked(handler)


    def delete_document_button_clicked(self, handler) -> None:
        """Connects the delete document button click signal to a handler

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.ui.delete_document_pushButton.clicked.connect(handler)

    
    def cancel_button_clicked(self, handler) -> None:
        """Connects the cancel button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.ui.close_pushButton.clicked.connect(handler)
        self.ui.cancel_pushButton.clicked.connect(handler)


    def save_button_clicked(self, handler) -> None:
        """Connects the save button click signal to a handler.

        Args:
            handler: The callback function to execute when the button is clicked.
        """
        self.ui.save_pushButton.clicked.connect(handler)


    def pages_table_selection_changed(self, handler) -> None:
        """Connects the pages table selection changed signal to a handler."""
        self.pages_table.connect_selection_changed(handler)

    
    def pages_table_item_changed(self, handler) -> None:
        """Connects the pages table item changed signal to a handler."""
        self.pages_table.connect_item_changed(handler)


    def pages_table_row_moved(self, handler) -> None:
        """Connects the pages table row moved signal to a handler."""
        self.pages_table.connect_row_moved(handler)

    def file_drop_widget_files_dropped(self, handler) -> None:
        """Connects the files dropped signal."""
        self.files_tab.connect_files_dropped(handler)

    def file_drop_widget_clicked(self, handler) -> None:
        """Connects the file drop widget click signal."""
        self.files_tab.connect_drag_drop_area(handler)

    def file_deleted(self, handler) -> None:
        """Connects the file deleted signal."""
        self.files_tab.connect_file_deleted(handler)

    def add_file_widget(self, file_data: object) -> None:
        self.files_tab.add_file_widget(file_data)

    def remove_file_widget(self, file_identifier: object) -> None:
        self.files_tab.remove_file_widget(file_identifier)