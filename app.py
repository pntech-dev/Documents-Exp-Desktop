import os
import re
import sys
import shutil
import subprocess
import sqlite3 as sql

import config

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from ui.DE_UI import Ui_MainWindow
from settings import SettingsWindow

class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.groups_group.setAlignment(QtCore.Qt.AlignLeft)
        self.ui.tableView.verticalHeader().setVisible(False)
        self.ui.tableView.viewport().installEventFilter(self)

        self.check_program_version(version_label=self.ui.actionsGroup_version)

        self.is_in_group = False
        self.is_mouse_pressed = False
        self.last_mouse_position = None

        # Groups
        self.last_checked_group = None
        self.groups_objects = self.add_groups()
        self.last_checked_group = self.groups_objects[0]
        self.last_checked_group.setChecked(True)

        for radio_button in self.groups_objects:
            radio_button.clicked.connect(lambda _, rb=radio_button: self.group_button_clicked(button=rb))

        # Categories
        self.last_clicked_category = None
        self.categories_objects = self.add_categories(group_name=self.last_checked_group.text())
        if self.categories_objects:
            self.last_clicked_category = self.categories_objects[0]

        for push_button in self.categories_objects:
            push_button.clicked.connect(lambda _, pb=push_button: self.category_button_clicked(button=pb))

        # TableView
        self.slider_value = 0
        self.setup_table_view(headers=["№", "Наименование"])
        self.ui.tableView.doubleClicked.connect(lambda index: self.double_clicked(index))
        self.ui.go_back.clicked.connect(lambda: self.go_back())

        # Search
        self.ui.searchGroup_lineEdit.textChanged.connect(lambda: self.search())
        self.ui.searchGroup_pushButton.clicked.connect(lambda: self.clear_search_line())

        # Settings
        self.ui.actionsGroup_pushButton.clicked.connect(lambda: self.open_settings())

    def open_settings(self):
        settings_window = SettingsWindow()
        settings_window.closed.connect(lambda: self.on_settings_closed())
        self.ui.actionsGroup_pushButton.setEnabled(False)
        settings_window.show()

    def on_settings_closed(self):
        self.ui.actionsGroup_pushButton.setEnabled(True)
        if config.CHANGES:
            # Groups
            self.clear_group(group=self.ui.groups_group, start_index=1)
            self.groups_objects = self.add_groups()
            self.last_checked_group = self.groups_objects[0]
            self.last_checked_group.setChecked(True)

            for radio_button in self.groups_objects:
                radio_button.clicked.connect(lambda _, rb=radio_button: self.group_button_clicked(button=rb))
            
            # Categories
            self.clear_group(group=self.ui.buttons_group)
            self.categories_objects = self.add_categories(group_name=self.last_checked_group.text())
            if self.categories_objects:
                self.last_clicked_category = self.categories_objects[0]

            for push_button in self.categories_objects:
                push_button.clicked.connect(lambda _, pb=push_button: self.category_button_clicked(button=pb))

    def add_groups(self):
        groups = os.listdir(config.CURRENT_PATH_TO_GROUPS)
        groups_objects = []
        if groups:
            for group in groups:
                radio_button = QtWidgets.QRadioButton(text=group)
                groups_objects.append(radio_button)
                self.ui.groups_group.addWidget(radio_button)

        return groups_objects
    
    def add_categories(self, group_name):
        group_path = os.path.join(config.CURRENT_PATH_TO_GROUPS, group_name)
        categories = os.listdir(group_path)
        categories_objects = []
        if categories:
            for category in categories:
                push_button = QtWidgets.QPushButton(text=category[:-3])
                push_button.setFixedHeight(config.CATEGORY_BUTTON_HEIGHT)
                font = QFont("Arial", config.CATEGORY_BUTTON_FONT_SIZE)
                push_button.setFont(font)
                categories_objects.append(push_button)
                self.ui.buttons_group.addWidget(push_button)

        return categories_objects
    
    def clear_group(self, group, start_index=0):
        for i in range(start_index, group.count()):
            item = group.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    layout = item.layout()
                    if layout is not None:
                        self.clear_group(layout)
    
    def group_button_clicked(self, button):
        self.clear_group(group=self.ui.buttons_group)
        self.categories_objects = self.add_categories(group_name=button.text())
        self.last_checked_group = button

        for push_button in self.categories_objects:
            push_button.clicked.connect(lambda _, pb=push_button: self.category_button_clicked(button=pb))
        
    def category_button_clicked(self, button):
        self.last_clicked_category = button
        self.ui.searchGroup_lineEdit.setEnabled(True)

        if len(self.ui.searchGroup_lineEdit.text()) > 0:
            self.search()
        else:
            database_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, self.last_checked_group.text(), self.last_clicked_category.text())}.db"

            label_text = f"Папка:"
            self.ui.label.setText(label_text)
            self.is_document_label = False

            conn = sql.connect(database=database_path)
            cursor = conn.cursor()

            query = f"SELECT name FROM sqlite_master WHERE type='table';"
            cursor.execute(query)
            tables_names = [table[0].split("+") for table in cursor.fetchall()]

            self.update_table_view(data=tables_names)

            cursor.close()
            conn.close()

    def setup_table_view(self, headers):
        self.table_model = QtGui.QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(headers)
        self.ui.tableView.setModel(self.table_model)
        self.ui.tableView.setColumnWidth(0, config.TABLEVIEW_FIRST_COLUMN_WIDTH)
        self.ui.tableView.horizontalHeader().setStretchLastSection(True)
        self.ui.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.ui.tableView.resizeRowsToContents()
        self.ui.tableView.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        if self.last_clicked_category:
            try:
                database_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, self.last_checked_group.text(), self.last_clicked_category.text())}.db"

                conn = sql.connect(database=database_path)
                cursor = conn.cursor()

                query = f"SELECT name FROM sqlite_master WHERE type='table';"
                cursor.execute(query)
                tables_names = [table[0].split("+") for table in cursor.fetchall()]

                self.update_table_view(data=tables_names)

                cursor.close()
                conn.close()
            except:
                pass
        
    def update_table_view(self, data):
        sorted_table = sorted(data, key=lambda table_name: self.extract_numbers(table_name[0]))

        self.table_model.removeRows(0, self.table_model.rowCount())
        for table in sorted_table:
            if len(table) == 2:
                self.table_model.appendRow([QtGui.QStandardItem(table[0]), QtGui.QStandardItem(table[1])])

    def extract_numbers(self, string):
        numbers = re.findall(r'\d+', string)
        return tuple(map(int, numbers))

    def double_clicked(self, index):
        self.slider_value = self.ui.tableView.verticalScrollBar().value()

        row_data = []
        for col in range(self.ui.tableView.model().columnCount()):
            row_data.append(index.sibling(index.row(), col).data())
        
        if self.last_clicked_category:
            try:
                database_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, self.last_checked_group.text(), self.last_clicked_category.text())}.db"

                conn = sql.connect(database=database_path)
                cursor = conn.cursor()

                query = f"SELECT name FROM sqlite_master WHERE type='table';"
                cursor.execute(query)
                tables_names = [table[0] for table in cursor.fetchall()]
                for table_name in tables_names:
                    if row_data[0] == table_name.split("+")[0]:
                        query = f"SELECT * FROM [{table_name}]"
                        cursor.execute(query)
                        table_row_data = [" ".join(i.replace("\n", " ") for i in row) for row in cursor.fetchall()]

                        label_text = f"{self.ui.label.text()[0:9].strip()} {" - ".join(i for i in table_name.split("+"))}"
                        self.ui.label.setText(label_text)
                        self.ui.searchGroup_lineEdit.setEnabled(False)
                            
                if table_row_data:
                    data = []
                    for row in table_row_data:
                        data.append([row_data[0], row])

                    self.update_table_view(data=data)

                cursor.close()
                conn.close()
            except:
                pass

    def search(self):
        if len(self.ui.searchGroup_lineEdit.text()) > 0:
            if self.last_clicked_category:
                try:
                    database_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, self.last_checked_group.text(), self.last_clicked_category.text())}.db"
                    conn = sql.connect(database=database_path)
                    cursor = conn.cursor()

                    search_text = self.ui.searchGroup_lineEdit.text().strip().lower().split()

                    query = f"SELECT name FROM sqlite_master WHERE type='table';"
                    cursor.execute(query)
                    tables_names = [table[0] for table in cursor.fetchall()]
                    
                    data = []
                    for table_name in tables_names:
                        if all(word in table_name.lower() for word in search_text):
                            data.append(table_name.split("+"))

                    for table_name in tables_names:
                        query = f"SELECT * FROM [{table_name}]"
                        cursor.execute(query)
                        table_row_data = [" ".join(i.replace("\n", " ") for i in row) for row in cursor.fetchall()]
                        
                        if table_row_data:
                            self.is_in_group = False
                            for row in table_row_data:
                                if row:
                                    if all(word in row.lower() for word in search_text):
                                        data.append([table_name.split("+")[0], row])
                    
                    self.update_table_view(data=data)

                    cursor.close()
                    conn.close()
                except:
                    pass
        else:
            self.setup_table_view(headers=["№", "Наименование"])

    def clear_search_line(self):
        if self.ui.searchGroup_lineEdit.text():
            self.ui.searchGroup_lineEdit.setText("")

    def go_back(self):
        self.ui.searchGroup_lineEdit.setEnabled(True)

        if len(self.ui.searchGroup_lineEdit.text()) > 0:
            self.search()
        else:
            if self.last_clicked_category:
                try:
                    database_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, self.last_checked_group.text(), self.last_clicked_category.text())}.db"

                    label_text = f"Папка:"
                    self.ui.label.setText(label_text)
                    self.is_document_label = False

                    conn = sql.connect(database=database_path)
                    cursor = conn.cursor()

                    query = f"SELECT name FROM sqlite_master WHERE type='table';"
                    cursor.execute(query)
                    tables_names = [table[0].split("+") for table in cursor.fetchall()]

                    self.update_table_view(data=tables_names)

                    cursor.close()
                    conn.close()

                    QtCore.QTimer.singleShot(0, lambda: self.ui.tableView.verticalScrollBar().setValue(self.slider_value))
                except:
                    self.slider_value = 0
                    self.ui.tableView.verticalScrollBar().setValue(0)
            
    def check_program_version(self, version_label):
        is_version = None
        files = os.listdir(path=config.CURRENT_VERSION_PATH)
        for file in files:
            if "version" in file.strip().lower():
                current_version = file[8:13]
                program_version = version_label.text()[8:]
                
                is_version = False if current_version != program_version else True       
        
        if not is_version:
            message_box = QtWidgets.QMessageBox()
            message_box.setWindowTitle("Обновление")
            message_box.setText("Обнаружена новая версия!\nДля продолжения работы необходимо установить обновление.")

            button_yes = message_box.addButton("Обновить сейчас", QtWidgets.QMessageBox.AcceptRole)
            button_no = message_box.addButton("Закрыть", QtWidgets.QMessageBox.RejectRole)

            message_box.exec()

            if message_box.clickedButton() == button_yes:
                current_directory = os.getcwd()
                updater_path = fr"{current_directory}\updater.exe"

                subprocess.Popen([updater_path, config.CURRENT_VERSION_PATH])
                cleanup_temp_folder()
                sys.exit()
            else:
                cleanup_temp_folder()
                sys.exit()

    def eventFilter(self, source, event):
        if source == self.ui.tableView.viewport():
            if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.LeftButton:
                self.is_mouse_pressed = True
                self.last_mouse_position = event.pos()
                
                self.start_mouse_position = event.pos()
                
                index = self.ui.tableView.indexAt(event.pos())
                if index.isValid():
                    self.ui.tableView.selectRow(index.row())
                
                return True

            elif event.type() == QtCore.QEvent.MouseMove and self.is_mouse_pressed:
                delta = event.pos() - self.start_mouse_position
                
                if abs(delta.y()) > 5:
                    scrollbar = self.ui.tableView.verticalScrollBar()
                    scrollbar.setValue(scrollbar.value() - (event.pos() - self.last_mouse_position).y())
                    self.last_mouse_position = event.pos()
                
                return True

            elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                self.is_mouse_pressed = False
                return True

            elif event.type() == QtCore.QEvent.MouseButtonDblClick and event.button() == QtCore.Qt.LeftButton:
                index = self.ui.tableView.indexAt(event.pos())
                if index.isValid():
                    self.double_clicked(index)
                return True

        return super(MyWindow, self).eventFilter(source, event)

def create_temp_folder():
    is_create = False
    for main_path in config.PATH_TO_GROUPS:
        if not is_create:
            current_directory = os.getcwd()
            number_of_folders = len([folder for folder in os.listdir(current_directory) if folder.startswith("groups")])
            folder_name = f"groups_{number_of_folders}"
            temp_path = os.path.join(current_directory, folder_name)
            main_folder = os.path.join(main_path, "groups")
            if not os.path.exists(temp_path):
                shutil.copytree(main_folder, temp_path)
                config.CURRENT_PATH_TO_GROUPS = temp_path
                is_create = True

def cleanup_temp_folder():
    if os.path.exists(config.CURRENT_PATH_TO_GROUPS):
        shutil.rmtree(config.CURRENT_PATH_TO_GROUPS)

    if os.path.exists(os.path.join(os.getcwd(), "CHANGELOG.txt")):
        os.remove(os.path.join(config.CURRENT_DIRECTORY_PATH, "CHANGELOG.txt"))

def merge_temp_folder():
    for main_path in config.PATH_TO_GROUPS:
        if os.path.exists(main_path):
            with open(f"{config.CURRENT_DIRECTORY_PATH}\\CHANGELOG.txt", "r+", encoding="utf-8") as changelog_file:
                lines = changelog_file.readlines()
                lines = [line.strip().replace("\n", "") for line in lines]

            main_path = os.path.join(main_path, "groups")
            for line in lines:
                line_data = re.findall(r"<(.*?)>", line)

                if "CREATE_GROUP" in line:
                    main_group_path = os.path.join(main_path, line_data[0])
                    if not os.path.exists(main_group_path):
                        os.makedirs(main_group_path, exist_ok=True)

                elif "CREATE_CATEGORY" in line:
                    temp_file_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, line_data[0], line_data[1])}.db"
                    main_file_path = f"{os.path.join(main_path, line_data[0], line_data[1])}.db"
                    if os.path.exists(temp_file_path) and not os.path.exists(main_file_path):
                        shutil.copy(temp_file_path, main_file_path)

                elif "CHANGES_IN_CATEGORY" in line:
                    temp_file_path = f"{os.path.join(config.CURRENT_PATH_TO_GROUPS, line_data[0], line_data[1])}.db"
                    main_file_path = f"{os.path.join(main_path, line_data[0], line_data[1])}.db"
                    if os.path.exists(main_file_path) and os.path.exists(temp_file_path):
                        os.remove(main_file_path)
                        shutil.copy(temp_file_path, main_file_path)

                elif "DELETE_GROUP" in line:
                    main_group_path = os.path.join(main_path, line_data[0])
                    if os.path.exists(main_group_path):
                        shutil.rmtree(main_group_path)

                elif "DELETE_CATEGORY" in line:
                    main_file_path = f"{os.path.join(main_path, line_data[0], line_data[1])}.db"
                    if os.path.exists(main_file_path):
                        os.remove(main_file_path)

if __name__ == "__main__":
    create_temp_folder()

    app = QtWidgets.QApplication([])
    application = MyWindow()
    application.show()
    exit_code = app.exec()

    if config.CHANGES:
        merge_temp_folder()

    cleanup_temp_folder()

    sys.exit(exit_code)