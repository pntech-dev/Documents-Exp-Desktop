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

        # Setting icon for logo label
        self.ui.logo_label.set_icon_paths(
            light=":/light/logo_light.svg",
            dark=":/dark/logo_dark.svg"
        )

        # Setting icon for create button
        light_create_icon = ":/icons/light/create/create_light.svg"
        dark_create_icon = ":/icons/dark/create/create_dark.svg"

        self.ui.create_pushButton.set_icon_paths(
            # light theme
            light_default=light_create_icon,
            light_hover=light_create_icon,
            light_pressed=light_create_icon,
            light_disabled=light_create_icon,
            
            # dark theme
            dark_default=dark_create_icon,
            dark_hover=dark_create_icon,
            dark_pressed=dark_create_icon,
            dark_disabled=dark_create_icon
        )

        # Setting icon for search filter button
        self.ui.search_filters_pushButton.set_icon_paths(
            # light theme
            light_default=":/icons/light/search_filter/light/default.svg",
            light_hover=":/icons/light/search_filter/light/hover.svg",
            light_pressed=":/icons/light/search_filter/light/clicked.svg",
            light_disabled=":/icons/light/search_filter/light/disabled.svg",
            
            # dark theme
            dark_default=":/icons/dark/search_filter/dark/default.svg",
            dark_hover=":/icons/dark/search_filter/dark/hover.svg",
            dark_pressed=":/icons/dark/search_filter/dark/clicked.svg",
            dark_disabled=":/icons/dark/search_filter/dark/disabled.svg"
        )

        self.sidebar = Sidebar(
            departments_tree=ui.departments_treeView,
            categories_tree=ui.categories_treeView
        )