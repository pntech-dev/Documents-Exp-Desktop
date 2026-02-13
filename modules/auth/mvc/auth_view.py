from PyQt5.QtWidgets import QLineEdit, QCheckBox, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, QPropertyAnimation, QEasingCurve

from ui import AuthWindow_UI
from ui.custom_widgets import SlideLabel
from utils import ThemeManagerInstance
import resources.slides.slides_resources_rc


class AuthPageWidgetGroup:
    """A helper class to group and manage UI widgets for an authentication page.

    This class provides a unified interface for accessing and manipulating a set of
    related widgets (e.g., email, password, buttons) that constitute a single
    authentication form like login, signup, or password reset.

    Attributes:
        email_field (QLineEdit): The input field for the user's email.
        password_field (QLineEdit): The input field for the user's password.
        confirm_password_field (QLineEdit): The input field for password confirmation.
        view_password_checkbox (QCheckBox): The checkbox to toggle password visibility.
        auto_login_checkbox (QCheckBox): The checkbox for the "auto-login" feature.
        submit_button (QPushButton): The primary action button (e.g., "Login", "Sign Up").
        back_button (QPushButton): The button to return to a previous page.
        tertiary_button (QPushButton): A secondary action button (e.g., "No account?").
        forgot_password_button (QPushButton): The button/label to initiate password reset.
    """
    def __init__(
            self,
            email_field: QLineEdit = None,
            password_field: QLineEdit = None,
            confirm_password_field: QLineEdit = None,
            view_password_checkbox: QCheckBox = None,
            auto_login_checkbox: QCheckBox = None,
            submit_button: QPushButton = None,
            back_button: QPushButton = None,
            tertiary_button: QPushButton = None,
            forgot_password_button: QPushButton = None
    ) -> None:
        """Initializes the AuthPageWidgetGroup.

        Args:
            email_field (QLineEdit, optional): The input field for the user's email. Defaults to None.
            password_field (QLineEdit, optional): The input field for the user's password. Defaults to None.
            confirm_password_field (QLineEdit, optional): The input field for password confirmation. Defaults to None.
            view_password_checkbox (QCheckBox, optional): The checkbox to toggle password visibility. Defaults to None.
            auto_login_checkbox (QCheckBox, optional): The checkbox for the "auto-login" feature. Defaults to None.
            submit_button (QPushButton, optional): The primary action button. Defaults to None.
            back_button (QPushButton, optional): The button to return to a previous page. Defaults to None.
            tertiary_button (QPushButton, optional): A secondary action button. Defaults to None.
            forgot_password_button (QPushButton, optional): The button/label to initiate password reset. Defaults to None.
        """
        self.email_field = email_field
        self.password_field = password_field
        self.confirm_password_field = confirm_password_field
        self.view_password_checkbox = view_password_checkbox
        self.auto_login_checkbox = auto_login_checkbox
        self.submit_button = submit_button
        self.back_button = back_button
        self.tertiary_button = tertiary_button
        self.forgot_password_button = forgot_password_button


    """=== Getters ==="""
    def get_email(self) -> str | None:
        """
        Retrieves the text from the email input field.

        Returns:
            str: The email address entered by the user, or None if the field doesn't exist.
        """
        if self.email_field:
            return self.email_field.text()

        return None
    

    def get_password(self) -> str | None:
        """
        Retrieves the text from the password input field.

        Returns:
            str: The password entered by the user, or None if the field doesn't exist.
        """
        if self.password_field:
            return self.password_field.text()
        
        return None
    

    def get_confirm_password(self) -> str | None:
        """
        Retrieves the text from the password confirmation input field.

        Returns:
            str: The confirmation password entered by the user, or None if the field doesn't exist.
        """
        if self.confirm_password_field:
            return self.confirm_password_field.text()

        return None
    

    def get_view_password_state(self) -> bool | None:
        """
        Checks if the 'view password' checkbox is currently checked.

        Returns:
            bool: True if the checkbox is checked, False otherwise, or None if the checkbox doesn't exist.
        """
        if self.view_password_checkbox:
            return self.view_password_checkbox.isChecked()
            
        return None


    def get_auto_login_state(self) -> bool | None:
        """
        Checks if the 'auto-login' checkbox is currently checked.

        Returns:
            bool: True if the checkbox is checked, False otherwise, or None if the checkbox doesn't exist.
        """
        if self.auto_login_checkbox:
            return self.auto_login_checkbox.isChecked()
            
        return None
    


    """=== Setters ==="""
    def set_password_visibility(self, state: bool) -> None:
        """
        Sets the visibility of password characters in the password fields.

        Args:
            state (bool): If True, characters are shown. If False, they are masked.
        """
        mode = QLineEdit.Normal if state else QLineEdit.Password

        if self.password_field:
            self.password_field.setEchoMode(mode)

        if self.confirm_password_field:
            self.confirm_password_field.setEchoMode(mode)

    
    def clear_lineedits(self) -> None:
        """
        Clears the text from all associated line edit fields (email, password, confirm password).
        """
        if self.email_field:
            self.email_field.clear()

        if self.password_field:
            self.password_field.clear()

        if self.confirm_password_field:
            self.confirm_password_field.clear()


    
    """=== Updaters ==="""
    def update_submit_button_state(self, state: bool) -> None:
        """Enables or disables the submit button.

        Args:
            state (bool): True to enable the button, False to disable it.
        """
        if self.submit_button:
            self.submit_button.setEnabled(state)



    """=== Handlers ==="""
    def submit_button_clicked(self, handler) -> None:
        """Connects a handler to the submit button's 'clicked' signal.

        Args:
            handler (callable): The function or method to call when the button is clicked.
        """
        if self.submit_button:
            self.submit_button.clicked.connect(handler)


    def back_button_clicked(self, handler) -> None:
        """Connects a handler to the back button's 'clicked' signal.

        Args:
            handler (callable): The function or method to call when the button is clicked.
        """
        if self.back_button:
            self.back_button.clicked.connect(handler)


    def tertiary_button_clicked(self, handler) -> None:
        """Connects a handler to the tertiary button's 'clicked' signal.

        This button is used for actions like switching between login and sign-up pages.

        Args:
            handler (callable): The function or method to call when the button is clicked.
        """
        if self.tertiary_button:
            self.tertiary_button.clicked.connect(handler)


    def forgot_password_button_clicked(self, handler) -> None:
        """Connects a handler to the 'forgot password' label's 'mousePressEvent'.

        Args:
            handler (callable): The function or method to call when the label is clicked.
        """
        if self.forgot_password_button:
            self.forgot_password_button.mousePressEvent = handler

    
    def view_password_checkbox_state_changed(self, handler) -> None:
        """Connects a handler to the 'view password' checkbox's 'stateChanged' signal.

        Args:
            handler (callable): The function or method to call when the checkbox state changes.
        """
        if self.view_password_checkbox:
            self.view_password_checkbox.stateChanged.connect(handler)


    def email_lineedit_text_changed(self, handler) -> None:
        """Connects a handler to the email field's 'textChanged' signal.

        Args:
            handler (callable): The function or method to call when the text changes.
        """
        if self.email_field:
            self.email_field.textChanged.connect(handler)

    
    def password_lineedit_text_changed(self, handler) -> None:
        """Connects a handler to the password field's 'textChanged' signal.

        Args:
            handler (callable): The function or method to call when the text changes.
        """
        if self.password_field:
            self.password_field.textChanged.connect(handler)


    def confirm_password_lineedit_text_changed(self, handler) -> None:
        """Connects a handler to the confirm password field's 'textChanged' signal.

        Args:
            handler (callable): The function or method to call when the text changes.
        """
        if self.confirm_password_field:
            self.confirm_password_field.textChanged.connect(handler)


class AuthSlider:
    def __init__(self, slides) -> None:
        self.slides_widget = slides

        for i in range(self.slides_widget.count()):
            page = self.slides_widget.widget(i)
            
            img_label = page.findChild(SlideLabel)
            if img_label:
                img_label.set_svg_paths(
                    light=f":/light/light/slide_{i + 1}.svg",
                    dark=f":/dark/dark/slide_{i + 1}.svg"
                )

        # Setup auto-switch timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._switch_slide)
        self.timer.start(7000)

    def _switch_slide(self) -> None:
        """Switches to the next slide with fade animation."""
        count = self.slides_widget.count()
        if count == 0:
            return
            
        current_index = self.slides_widget.currentIndex()
        next_index = (current_index + 1) % count
        
        current_widget = self.slides_widget.widget(current_index)
        next_widget = self.slides_widget.widget(next_index)
        
        # Fade Out
        self.effect_out = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(self.effect_out)
        
        self.anim_out = QPropertyAnimation(self.effect_out, b"opacity")
        self.anim_out.setDuration(300)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.OutQuad)
        
        self.anim_out.finished.connect(
            lambda: self._on_fade_out_finished(next_index, current_widget, next_widget)
        )
        self.anim_out.start()

    def _on_fade_out_finished(self, next_index, current_widget, next_widget) -> None:
        current_widget.setGraphicsEffect(None)
        self.slides_widget.setCurrentIndex(next_index)
        
        # Fade In
        self.effect_in = QGraphicsOpacityEffect(next_widget)
        self.effect_in.setOpacity(0.0)
        next_widget.setGraphicsEffect(self.effect_in)
        
        self.anim_in = QPropertyAnimation(self.effect_in, b"opacity")
        self.anim_in.setDuration(300)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.InQuad)
        
        self.anim_in.finished.connect(lambda: next_widget.setGraphicsEffect(None))
        self.anim_in.start()


class AuthView:
    """The main View class for the authentication window.

    This class orchestrates the UI components of the authentication module. It
    manages various pages (login, signup, etc.) as widget groups and provides
    methods to interact with them and the overall window (e.g., switching pages,
    handling theme changes).

    Attributes:
        ui (AuthWindow_UI): The UI object generated from Qt Designer.
        theme_manager (ThemeManager): An instance to manage application themes.
        login_page (AuthPageWidgetGroup): Widget group for the login page.
        signup_page (AuthPageWidgetGroup): Widget group for the signup page.
        forgot_page_email_confirm (AuthPageWidgetGroup): Widget group for the password
            reset email confirmation page.
        forgot_page_reset_password (AuthPageWidgetGroup): Widget group for the new
            password entry page.
        pages (dict): A mapping of page names to their corresponding widget objects.
        theme_buttons (list): A list of all theme-switching buttons in the UI.
    """
    def __init__(self, ui: AuthWindow_UI):
        """Initializes the AuthView.

        Args:
            ui (AuthWindow_UI): The UI object generated from Qt Designer.
        """
        self.ui = ui
        self.theme_manager = ThemeManagerInstance()

        # Setting icon for logo label
        self.ui.logo_label.set_icon_paths(
            light=":/light/logo_light.svg",
            dark=":/dark/logo_dark.svg"
        )

        # Setting icon for theme change button
        self.ui.theme_button.set_icon_paths(
            # light theme
            light_default=":/icons/light/light/theme_default.svg",
            light_hover=":/icons/light/light/theme_hover.svg",
            light_pressed=":/icons/light/light/theme_clicked.svg",
            light_disabled=":/icons/light/light/theme_disabled.svg",
            
            # dark theme
            dark_default=":/icons/dark/dark/theme_default.svg",
            dark_hover=":/icons/dark/dark/theme_hover.svg",
            dark_pressed=":/icons/dark/dark/theme_clicked.svg",
            dark_disabled=":/icons/dark/dark/theme_disabled.svg"
        )

        # Setting up icons for password display checkboxes
        self.view_password_checkboxes = [
            self.ui.view_password_checkBox,
            self.ui.view_password_checkBox_2,
            self.ui.view_password_checkBox_3
        ]

        for checkbox in self.view_password_checkboxes:
            checkbox.set_icon_paths(
                # Light theme
                light_unchecked=":/icons/light/light/view_pass_default.svg",
                light_unchecked_hover=":/icons/light/light/view_pass_hover.svg",
                light_unchecked_disabled=":/icons/light/light/view_pass_default_disabled.svg",
                
                light_checked=":/icons/light/light/view_pass_checked.svg",
                light_checked_hover=":/icons/light/light/view_pass_checked_hover.svg",
                light_checked_disabled=":/icons/light/light/view_pass_checked_disabled.svg",
                
                # Dark theme
                dark_unchecked=":/icons/dark/dark/view_pass_default.svg",
                dark_unchecked_hover=":/icons/dark/dark/view_pass_hover.svg",
                dark_unchecked_disabled=":/icons/dark/dark/view_pass_default_disabled.svg",
                
                dark_checked=":/icons/dark/dark/view_pass_checked.svg",
                dark_checked_hover=":/icons/dark/dark/view_pass_checked_hover.svg",
                dark_checked_disabled=":/icons/dark/dark/view_pass_checked_disabled.svg"
            )

        # Setting icon for email lineedits
        mail_lineedits = [
            self.ui.email_lineEdit,
            self.ui.email_lineEdit_2,
            self.ui.email_lineEdit_3,
        ]
        for mail_lineedit in mail_lineedits:
            mail_lineedit.set_icon_paths(
                # light theme
                default_light=":/icons/light/light/mail_default.svg",
                hover_light=":/icons/light/light/mail_hover.svg",
                focus_light=":/icons/light/light/mail_active.svg",
                disabled_light=":/icons/light/light/mail_disabled.svg",

                # dark theme
                default_dark=":/icons/dark/dark/mail_default.svg",
                hover_dark=":/icons/dark/dark/mail_hover.svg",
                focus_dark=":/icons/dark/dark/mail_active.svg",
                disabled_dark=":/icons/dark/dark/mail_disabled.svg"
            )

        # Setting icon for password lineedits
        password_lineedits = [
            self.ui.password_lineEdit,
            self.ui.password_lineEdit_2,
            self.ui.password_lineEdit_3,
            self.ui.password_lineEdit_4,
            self.ui.password_lineEdit_5
        ]
        for password_lineedit in password_lineedits:
            password_lineedit.set_icon_paths(
                # light theme
                default_light=":/icons/light/light/password_default.svg",
                hover_light=":/icons/light/light/password_hover.svg",
                focus_light=":/icons/light/light/password_active.svg",
                disabled_light=":/icons/light/light/password_disabled.svg",

                # dark theme
                default_dark=":/icons/dark/dark/password_default.svg",
                hover_dark=":/icons/dark/dark/password_hover.svg",
                focus_dark=":/icons/dark/dark/password_active.svg",
                disabled_dark=":/icons/dark/dark/password_disabled.svg"
            )

        # Initialize page widget groups
        self.login_page = AuthPageWidgetGroup(
            email_field=self.ui.email_lineEdit,
            password_field=self.ui.password_lineEdit,
            view_password_checkbox=self.ui.view_password_checkBox,
            auto_login_checkbox=self.ui.auto_login_checkBox,
            submit_button=self.ui.login_pushButton,
            back_button=self.ui.guest_pushButton,
            tertiary_button=self.ui.no_account_pushButton,
            forgot_password_button=self.ui.forgot_password_label
        )

        self.signup_page = AuthPageWidgetGroup(
            email_field=self.ui.email_lineEdit_2,
            password_field=self.ui.password_lineEdit_2,
            confirm_password_field=self.ui.password_lineEdit_3,
            view_password_checkbox=self.ui.view_password_checkBox_2,
            auto_login_checkbox=self.ui.auto_login_checkBox_2,
            submit_button=self.ui.create_pushButton,
            back_button=self.ui.have_account_pushButton,
        )

        self.forgot_page_email_confirm = AuthPageWidgetGroup(
            email_field=self.ui.email_lineEdit_3,
            submit_button=self.ui.accept_pushButton,
            back_button=self.ui.have_account_pushButton_2
        )

        self.forgot_page_reset_password = AuthPageWidgetGroup(
            password_field=self.ui.password_lineEdit_4,
            confirm_password_field=self.ui.password_lineEdit_5,
            view_password_checkbox=self.ui.view_password_checkBox_3,
            submit_button=self.ui.change_pushButton,
            back_button=self.ui.have_account_pushButton_3
        )

        # Auth module pages
        self.pages = {
            "login_page": self.ui.login_page,
            "signup_page": self.ui.signup_page,
            "change_password_confirm_page": self.ui.change_password_confirm_page,
            "change_password_change_page": self.ui.change_password_change_page
        }

        # Initialize slides
        self.slides = AuthSlider(slides=self.ui.slider)


    def set_theme(self) -> None:
        """Switches the application's theme.

        Delegates the theme switching logic to the theme manager instance.
        """
        self.theme_manager.switch_theme()


    def switch_page(self, page) -> None:
        """Switches the currently visible page in the stacked widget.

        Args:
            page (QWidget): The page widget to display.
        """
        self.ui.pages.setCurrentWidget(page)


    def theme_switcher_clicked(self, handler) -> None:
        """Connects a handler to all theme-switching buttons.

        Iterates through all registered theme buttons and connects their 'clicked'
        signal to the provided handler.

        Args:
            handler (callable): The function or method to call when any theme
                button is clicked.
        """
        self.ui.theme_button.clicked.connect(handler)