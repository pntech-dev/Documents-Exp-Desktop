import json
from pathlib import Path
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtCore import QEvent, Qt, QObject

from ui import MainWindow_UI
from utils import ThemeManagerInstance
from ui.ui_converted.custom_widgets import (
    SidebarItem,
    SidebarBlock,
    PrimaryButton,
    TertiaryButton,
    ThemeSwitch,
    LogoLabel,
    ProfileIconLabel,
    ThemeAwareMenu
)



class Sidebar:
    """Manages the sidebar logic and updates."""

    def __init__(
            self,
            logo_label: LogoLabel,
            departments_tree: SidebarBlock,
            categories_tree: SidebarBlock,
            profile_icon_label: ProfileIconLabel,
            icons_config: dict
            ) -> None:
        """Initializes the Sidebar manager.

        Args:
            logo_label: The label widget for the application logo.
            departments_tree: The tree view widget for departments.
            categories_tree: The tree view widget for categories.
            profile_icon_label: The custom label widget for the profile icon.
            icons_config: Dictionary containing icon paths configuration.
        """
        
        self.logo_label = logo_label
        self.departments_tree = departments_tree
        self.categories_tree = categories_tree
        self.profile_icon_label = profile_icon_label
        self.config = icons_config

        # Setting icon for logo label
        self.logo_label.set_icon_paths(
            light=self.config.get("logo", {}).get("light"),
            dark=self.config.get("logo", {}).get("dark")
        )

        # Setting default icons for profile
        self.profile_icon_label.set_icon_paths(
            guest_light=self.config.get("profile", {}).get("guest", {}).get("light"),
            guest_dark=self.config.get("profile", {}).get("guest", {}).get("dark"),
            auth_light=self.config.get("profile", {}).get("auth", {}).get("light"),
            auth_dark=self.config.get("profile", {}).get("auth", {}).get("dark")
        )


    def update_departments(self, items: list[SidebarItem]) -> None:
        """Updates the departments tree with new items.

        Args:
            items: A list of SidebarItem objects to populate the tree.
        """
        # The View decides the title and icon, not the Controller
        self.departments_tree.set_items(items, group_title="Отделы", group_icon=None)

    def update_categories(self, items: list[SidebarItem]) -> None:
        """Updates the categories tree with new items.

        Args:
            items: A list of SidebarItem objects to populate the tree.
        """
        # The View decides the title and icon, not the Controller
        self.categories_tree.set_items(items, group_title="Категории", group_icon=None)

    def set_profile_mode(self, mode: str) -> None:
        """Sets the profile mode ('guest' or 'auth').

        Args:
            mode: The mode string, either 'guest' or 'auth'.
        """
        self.profile_icon_label.set_mode(mode)

    def set_user_avatar(self, icon: QIcon | None) -> None:
        """Sets the user's custom avatar.

        Args:
            icon: The QIcon object for the user's avatar, or None to clear.
        """
        self.profile_icon_label.set_custom_avatar(icon)

    def set_ui_visible(self, is_visible: bool) -> None:
        """Enables or disables UI elements visibility.

        Args:
            is_enabled: Boolean indicating whether the UI should be enabled.
        """
        pass


class Navbar:
    """Manages the navigation bar logic and updates."""

    def __init__(
            self,
            search_filters_pushButton: TertiaryButton,
            theme_switch: ThemeSwitch,
            create_pushButton: PrimaryButton,
            icons_config: dict
    ) -> None:
        """Initializes the Navbar manager.

        Args:
            search_filters_pushButton: The button for search filters.
            theme_switch: The custom widget for switching themes.
            create_pushButton: The primary button for creating new items.
            icons_config: Dictionary containing icon paths configuration.
        """
        self.search_filters_pushButton = search_filters_pushButton
        self.theme_switch = theme_switch
        self.create_pushButton = create_pushButton
        self.config = icons_config.get("navbar", {})

        # Setting icon for search filter button
        search_cfg = self.config.get("search_filter", {})
        self.search_filters_pushButton.set_icon_paths(
            # light theme
            light_default=search_cfg.get("light", {}).get("default"),
            light_hover=search_cfg.get("light", {}).get("hover"),
            light_pressed=search_cfg.get("light", {}).get("pressed"),
            light_disabled=search_cfg.get("light", {}).get("disabled"),
            
            # dark theme
            dark_default=search_cfg.get("dark", {}).get("default"),
            dark_hover=search_cfg.get("dark", {}).get("hover"),
            dark_pressed=search_cfg.get("dark", {}).get("pressed"),
            dark_disabled=search_cfg.get("dark", {}).get("disabled")
        )

        # Setting icon for create button
        create_cfg = self.config.get("create", {})
        light_create = create_cfg.get("light")
        dark_create = create_cfg.get("dark")

        self.create_pushButton.set_icon_paths(
            # light theme
            light_default=light_create,
            light_hover=light_create,
            light_pressed=light_create,
            light_disabled=light_create,
            
            # dark theme
            dark_default=dark_create,
            dark_hover=dark_create,
            dark_pressed=dark_create,
            dark_disabled=dark_create
        )

    def set_ui_visible(self, is_visible: bool) -> None:
        """Enables or disables UI elements visibility.

        Args:
            is_enabled: Boolean indicating whether the UI should be enabled.
        """
        self.create_pushButton.setVisible(is_visible)
    
    def theme_switcher_clicked(self, handler) -> None:
        """Connects the theme switcher click signal to a handler.

        Args:
            handler: The callback function to execute when the switch is clicked.
        """
        self.theme_switch.clicked.connect(handler)



class MainView(QObject):
    """Main view class for the application window."""

    def __init__(self, ui: MainWindow_UI) -> None:
        """Initializes the MainView.

        Args:
            ui: The UI object generated by PyQt5 uic.
        """
        super().__init__()
        self.ui = ui
        self.theme_manager = ThemeManagerInstance()
        self.ui_config = self._load_ui_config()

        self.profile_menu = None
        self.user_profile_action = None
        self.settings_action = None
        self.logout_action = None

        # Replacing the standard theme button with a custom switcher
        self._replace_theme_button()
        self._replace_profile_icon_label()

        icons_config = self.ui_config.get("icons", {})

        self.sidebar = Sidebar(
            departments_tree=self.ui.departments_treeView,
            categories_tree=self.ui.categories_treeView,
            logo_label=self.ui.logo_label,
            profile_icon_label=self.ui.profile_icon_label,
            icons_config=icons_config
        )

        self.navbar = Navbar(
            search_filters_pushButton=self.ui.search_filters_pushButton,
            theme_switch=self.ui.theme_pushButton,
            create_pushButton=self.ui.create_pushButton,
            icons_config=icons_config
        )
        
        self._setup_profile_menu()


    def _setup_profile_menu(self) -> None:
        """Configures the profile frame and creates the popup menu."""
        # 1. Make children transparent for mouse events so the frame receives the click
        for child in self.ui.profile_frame.children():
            if isinstance(child, QWidget):
                child.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        # 2. Install event filter on the frame to catch clicks
        self.ui.profile_frame.installEventFilter(self)
        self.ui.profile_frame.setCursor(Qt.PointingHandCursor)

        # 3. Create the menu
        self.profile_menu = ThemeAwareMenu(self.ui.profile_frame)
        self.profile_menu.setObjectName("profile_menu")
        
        # Example actions (Icons should ideally come from config)
        # Using existing icons as placeholders for demonstration
        self.user_profile_action = self.profile_menu.add_theme_action(
            text="Профиль", 
            light_default=":/icons/light/profile/light/profile_default.svg",
            light_hover=":/icons/light/profile/light/profile_hover.svg",
            light_pressed=":/icons/light/profile/light/profile_pressed.svg",
            dark_default=":/icons/dark/profile/dark/profile_default.svg",
            dark_hover=":/icons/dark/profile/dark/profile_hover.svg",
            dark_pressed=":/icons/dark/profile/dark/profile_pressed.svg"
        )
        self.settings_action = self.profile_menu.add_theme_action(
            text="Настройки", 
            light_default=":/icons/light/settings/light/default.svg",
            light_hover=":/icons/light/settings/light/hover.svg",
            light_pressed=":/icons/light/settings/light/pressed.svg",
            dark_default=":/icons/dark/settings/dark/default.svg",
            dark_hover=":/icons/dark/settings/dark/hover.svg",
            dark_pressed=":/icons/dark/settings/dark/pressed.svg"
        )
        self.logout_action = self.profile_menu.add_theme_action(
            text="Выйти", 
            light_default=":/icons/light/exit/light/default.svg",
            light_hover=":/icons/light/exit/light/hover.svg",
            light_pressed=":/icons/light/exit/light/pressed.svg",
            dark_default=":/icons/dark/exit/dark/default.svg",
            dark_hover=":/icons/dark/exit/dark/hover.svg",
            dark_pressed=":/icons/dark/exit/dark/pressed.svg",
            danger_action=True
        )

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if source == self.ui.profile_frame and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                # Show menu aligned to the top-right of the frame
                pos = self.ui.profile_frame.mapToGlobal(self.ui.profile_frame.rect().topRight())
                # Adjust position to open slightly above/inside
                menu_pos = pos
                menu_pos.setY(menu_pos.y() - self.profile_menu.sizeHint().height()) 
                
                # Or standard popup behavior (at mouse position or aligned)
                self.profile_menu.exec_(QMouseEvent(event).globalPos())
                return True
        return super().eventFilter(source, event)


    def _replace_theme_button(self) -> None:
        """Replaces the generated QPushButton with a custom ThemeSwitch widget.

        This method removes the placeholder button from the layout and inserts
        the custom ThemeSwitch widget in its place, preserving the layout index.
        """
        # Getting the parent container and its layout
        parent = self.ui.navbar_actions_frame
        layout = parent.layout()
        
        # We find the old button and its position
        old_button = self.ui.theme_pushButton
        if old_button:
            index = layout.indexOf(old_button)
            layout.removeWidget(old_button)
            old_button.deleteLater()
            
            # Creating and inserting a new switcher in the same place
            self.ui.theme_pushButton = ThemeSwitch(parent)

            # Copying properties from the old button if needed, or setting defaults
            self.ui.theme_pushButton.setMinimumSize(125, 42)
            self.ui.theme_pushButton.setObjectName("themeSwitch")
            
            # Setting the initial state
            is_dark = self.theme_manager.current_theme_id != "0"
            self.ui.theme_pushButton.setChecked(is_dark)
            
            layout.insertWidget(index, self.ui.theme_pushButton)


    def _replace_profile_icon_label(self) -> None:
        """Replaces the generated QLabel with a custom ProfileIconLabel widget.

        This method removes the placeholder label from the layout and inserts
        the custom ProfileIconLabel widget in its place.
        """
        parent = self.ui.profile_frame
        layout = parent.layout()
        
        old_label = self.ui.profile_icon_label
        if old_label:
            index = layout.indexOf(old_label)
            layout.removeWidget(old_label)
            old_label.deleteLater()
            
            self.ui.profile_icon_label = ProfileIconLabel(parent)
            
            # Ensure the object name matches so QSS styles apply correctly
            self.ui.profile_icon_label.setObjectName("profile_icon_label")
            layout.insertWidget(index, self.ui.profile_icon_label)


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

    def set_theme(self) -> None:
        """Switches the application's theme.

        Delegates the theme switching logic to the theme manager instance.
        """
        self.theme_manager.switch_theme()


    def update_departments(self, items: list[SidebarItem]) -> None:
        """Updates the departments tree in the sidebar.

        Args:
            items: List of SidebarItem objects.
        """
        self.sidebar.update_departments(items)


    def update_categories(self, items: list[SidebarItem]) -> None:
        """Updates the categories tree in the sidebar.

        Args:
            items: List of SidebarItem objects.
        """
        self.sidebar.update_categories(items)


    def set_profile_mode(self, mode: str) -> None:
        """Sets the profile mode ('guest' or 'auth')."""
        self.sidebar.set_profile_mode(mode)

        is_visible = True if mode == "auth" else False
        self.navbar.set_ui_visible(is_visible)
        self.sidebar.set_ui_visible(is_visible)


    def connect_theme_switch(self, handler) -> None:
        """Connects the theme switch button signal to a handler.

        Args:
            handler: The callback function.
        """
        self.navbar.theme_switcher_clicked(handler)

    def connect_logout(self, handler) -> None:
        """Connects the logout action to a handler.

        Args:
            handler: The callback function.
        """
        if self.profile_menu:
            self.logout_action.triggered.connect(handler)