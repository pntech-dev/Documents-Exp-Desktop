from ui import MainWindow_UI
from ui.ui_converted.custom_widgets import DeptItem, SidebarBlock


class Sidebar:
    def __init__(
            self,
            departments_tree: SidebarBlock,
            categories_tree: SidebarBlock
            ) -> None:
        self.departments_tree = departments_tree
        self.categories_tree = categories_tree


    def update_departments(self, departments: list[DeptItem]):
        self.departments_tree.set_items(departments, group_title="Отделы", group_icon=None)


    def update_categories(self, categories: list[DeptItem]):
        self.categories_tree.set_items(categories, group_title="Категории", group_icon=None)


class MainView:
    def __init__(self, ui: MainWindow_UI) -> None:
        self.ui = ui

        self.sidebar = Sidebar(
            departments_tree=ui.departments_treeView,
            categories_tree=ui.categories_treeView
        )