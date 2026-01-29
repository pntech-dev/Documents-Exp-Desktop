from ui import MainWindow_UI
from ui.ui_converted.custom_widgets import SidebarItem, SidebarBlock


class Sidebar:
    def __init__(
            self,
            departments_tree: SidebarBlock,
            categories_tree: SidebarBlock
            ) -> None:
        self.departments_tree = departments_tree
        self.categories_tree = categories_tree


    # def update_departments(self, departments: list[SidebarItem]):
    #     self.departments_tree.set_items(departments, group_title="Отделы", group_icon=None)


    # def update_categories(self, categories: list[SidebarItem]):
    #     self.categories_tree.set_items(categories, group_title="Категории", group_icon=None)


    def update_tree(self, items: list[SidebarItem], group_title: str, group_icon: str = None):
        if not items:
            return
        
        if group_title == "Отделы":
            self.departments_tree.set_items(items, group_title, group_icon)
        
        elif group_title == "Категории":
            self.categories_tree.set_items(items, group_title, group_icon)


class MainView:
    def __init__(self, ui: MainWindow_UI) -> None:
        self.ui = ui

        self.sidebar = Sidebar(
            departments_tree=ui.departments_treeView,
            categories_tree=ui.categories_treeView
        )