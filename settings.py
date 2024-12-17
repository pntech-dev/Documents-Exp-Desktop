import config

from settings_lib import *

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from ui.DE_Settings_UI import Ui_MainWindow

class SettingsWindow(QtWidgets.QMainWindow):
    closed = pyqtSignal()

    def __init__(self):
        super(SettingsWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        """Start settings"""
        # Create classes
        tab = Tab()
        add_tab = AddTab(progressBar=self.ui.add_progressBar, tableView=self.ui.deleteLists_tableView)
        delete_tab = DeleteTab(progressBar=self.ui.delete_progressBar, tableView=self.ui.deleteLists_tableView)
        templates_tab = TemplatesTab(progressBar=self.ui.templates_progressBar, tableView=self.ui.templates_tableView)

        # Create group comboboxes
        group_comboboxes = [
            self.ui.addCategory_comboBox,
            self.ui.addLists_comboBox_1,
            self.ui.deleteGroup_comboBox,
            self.ui.deleteCategory_comboBox_1,
            self.ui.deleteLists_comboBox_1
        ]

        groups = tab.get_groups(groups_path=config.CURRENT_PATH_TO_GROUPS)
        tab.create_comboboxes(data=groups, comboboxes=group_comboboxes)

        # Create categorie comboboxes
        categories_comboboxes = {
            self.ui.addLists_comboBox_1:self.ui.addLists_comboBox_2,
            self.ui.deleteCategory_comboBox_1:self.ui.deleteCategory_comboBox_2,
            self.ui.deleteLists_comboBox_1:self.ui.deleteLists_comboBox_2
        }
        tab.create_categories_comboboxes(comboboxes=categories_comboboxes)

        # Create tableViews
        data = tab.get_table_view_data(group=self.ui.deleteLists_comboBox_1.currentText(), categorie=self.ui.deleteLists_comboBox_2.currentText())
        tab.create_table(tableView=self.ui.deleteLists_tableView, headers=["№", "Наименование"], data=data, column_width=70)

        templates_tab.create_templates_tables(tableView=self.ui.templates_tableView, headers=["Название"])

        """Add tab"""
        # Add group
        self.ui.addGroup_lineEdit.textChanged.connect(lambda: add_tab.button_enabler(object=self.ui.addGroup_lineEdit.text(),
                                                                                    button=self.ui.addGroup_pushButton))
        self.ui.addGroup_pushButton.clicked.connect(
            lambda: (
                add_tab.add_group(filename=self.ui.addGroup_lineEdit.text()),
                add_tab.create_comboboxes(data=tab.get_groups(groups_path=config.CURRENT_PATH_TO_GROUPS), comboboxes=group_comboboxes)
            )
        )
        # Add category
        self.ui.addCategory_choice_pushButton.clicked.connect(lambda: add_tab.get_folder(parent=self,
                                                                                        lineEdit=self.ui.addCategory_lineEdit))
        self.ui.addCategory_lineEdit.textChanged.connect(lambda: add_tab.button_enabler(object=self.ui.addCategory_lineEdit.text(),
                                                                                        button=self.ui.addCategory_add_pushButton))
        self.ui.addCategory_add_pushButton.clicked.connect(
            lambda: (
                add_tab.add_categories(group=self.ui.addCategory_comboBox.currentText(), categories_path=self.ui.addCategory_lineEdit.text()),
                add_tab.create_categories_comboboxes(comboboxes=categories_comboboxes),
                tab.create_table(tableView=self.ui.deleteLists_tableView,
                                headers=["№", "Наименование"], 
                                data=tab.get_table_view_data(group=self.ui.deleteLists_comboBox_1.currentText(), 
                                                            categorie=self.ui.deleteLists_comboBox_2.currentText()), 
                                column_width=70)
                )
        )
        
        # Add lists
        self.ui.addLists_choice_pushButton.clicked.connect(lambda: add_tab.get_file(parent=self,
                                                                                    lineEdit=self.ui.addLists_lineEdit))
        self.ui.addLists_comboBox_1.currentTextChanged.connect(lambda: add_tab.create_comboboxes(data=add_tab.get_categories(group=self.ui.addLists_comboBox_1.currentText()),
                                                                                                comboboxes=[self.ui.addLists_comboBox_2]))
        self.ui.addLists_lineEdit.textChanged.connect(lambda: add_tab.button_enabler(object=self.ui.addLists_lineEdit.text(),
                                                                                    button=self.ui.addLists_add_pushButton))
        self.ui.addLists_add_pushButton.clicked.connect(
            lambda: (
                add_tab.add_lists(group=self.ui.addLists_comboBox_1.currentText(), categorie=self.ui.addLists_comboBox_2.currentText(), file_path=self.ui.addLists_lineEdit.text()),
                tab.create_table(tableView=self.ui.deleteLists_tableView,
                                headers=["№", "Наименование"], 
                                data=tab.get_table_view_data(group=self.ui.deleteLists_comboBox_1.currentText(), categorie=self.ui.deleteLists_comboBox_2.currentText()),
                                column_width=70)
                )
            )
        
        """Delete tab"""
        # Delete group
        self.ui.deleteGroup_pushButton.clicked.connect(
            lambda: (
                delete_tab.delete_group(group=self.ui.deleteGroup_comboBox.currentText()),
                delete_tab.create_comboboxes(data=delete_tab.get_groups(groups_path=config.CURRENT_PATH_TO_GROUPS), comboboxes=group_comboboxes)
                )
            )

        # Delete category
        self.ui.deleteCategory_comboBox_1.currentTextChanged.connect(lambda: delete_tab.create_comboboxes(delete_tab.get_categories(group=self.ui.deleteCategory_comboBox_1.currentText()),
                                                                                                        comboboxes=[self.ui.deleteCategory_comboBox_2]))
        self.ui.deleteCategory_pushButton.clicked.connect(
            lambda: (
                delete_tab.delete_categorie(group=self.ui.deleteCategory_comboBox_1.currentText(), categorie=self.ui.deleteCategory_comboBox_2.currentText()),
                delete_tab.create_categories_comboboxes(comboboxes=categories_comboboxes)
                )
            )

        # Delete list
        self.ui.deleteLists_comboBox_1.currentTextChanged.connect(
            lambda: (
                delete_tab.create_comboboxes(delete_tab.get_categories(group=self.ui.deleteLists_comboBox_1.currentText()), comboboxes=[self.ui.deleteLists_comboBox_2]),
                tab.create_table(tableView=self.ui.deleteLists_tableView,
                                headers=["№", "Наименование"], 
                                data=tab.get_table_view_data(group=self.ui.deleteLists_comboBox_1.currentText(), categorie=self.ui.deleteLists_comboBox_2.currentText()),
                                column_width=70)
                )
            )
        self.ui.deleteLists_comboBox_2.currentTextChanged.connect(lambda: tab.create_table(tableView=self.ui.deleteLists_tableView,
                                                                                        headers=["№", "Наименование"], 
                                                                                        data=tab.get_table_view_data(group=self.ui.deleteLists_comboBox_1.currentText(), categorie=self.ui.deleteLists_comboBox_2.currentText()),
                                                                                        column_width=70))
        self.ui.deleteLists_tableView.doubleClicked.connect(lambda index: tab.double_clicked(index, tableView=self.ui.deleteLists_tableView, label=self.ui.deleteLists_lineEdit, text="Выбран перечень:"))
        self.ui.deleteLists_lineEdit.textChanged.connect(lambda: tab.button_enabler(object=self.ui.deleteLists_lineEdit.text(), button=self.ui.deleteLists_pushButton))
        self.ui.deleteLists_pushButton.clicked.connect(
            lambda: (
                delete_tab.delete_list(group=self.ui.deleteLists_comboBox_1.currentText(), 
                                    categorie=self.ui.deleteLists_comboBox_2.currentText(), 
                                    label=self.ui.deleteLists_lineEdit.text()),
                tab.create_table(tableView=self.ui.deleteLists_tableView,
                                headers=["№", "Наименование"], 
                                data=tab.get_table_view_data(group=self.ui.deleteLists_comboBox_1.currentText(), 
                                                            categorie=self.ui.deleteLists_comboBox_2.currentText()), 
                                column_width=70)
                )
            )
        self.ui.deleteLists_search_lineEdit.textChanged.connect(lambda: delete_tab.search(tableView=delete_tab.tableView,
                                                                                        search_text=self.ui.deleteLists_search_lineEdit.text(),
                                                                                        group=self.ui.deleteLists_comboBox_1.currentText(), 
                                                                                        categorie=self.ui.deleteLists_comboBox_2.currentText()))
        
        """Template tab"""
        self.ui.templates_selectPath_pushButton.clicked.connect(lambda: templates_tab.get_folder(parent=self,
                                                                                                lineEdit=self.ui.templates_selectPath_lineEdit))
        self.ui.templates_selectPath_lineEdit.textChanged.connect(lambda: templates_tab.button_enabler(object=self.ui.templates_selectPath_lineEdit.text(),
                                                                                                    button=self.ui.templates_pushButton))
        self.ui.templates_tableView.doubleClicked.connect(lambda index: tab.double_clicked(index, 
                                                                                        tableView=self.ui.templates_tableView, 
                                                                                        label=self.ui.templates_tableView_label_2, 
                                                                                        text="Выбран шаблон:"))
        self.ui.templates_pushButton.clicked.connect(lambda: templates_tab.download(line_edit=self.ui.templates_selectPath_lineEdit.text(),
                                                                                    file_label=self.ui.templates_tableView_label_2.text()))
    
    def closeEvent(self, event):
        self.closed.emit()
        super(SettingsWindow, self).closeEvent(event)