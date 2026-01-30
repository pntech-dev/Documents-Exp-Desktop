from PyQt5.QtCore import QTimer, QObject, QEvent
from PyQt5.QtWidgets import QWidget

from .toast_notification import ToastNotification
from .modal_notification import ModalNotification
from utils.theme_manager import ThemeManagerInstance


class Singleton(type):
    """A metaclass for creating singleton classes."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class WindowResizeFilter(QObject):
    """Event filter to detect main window resize events."""
    def __init__(self, notification_service):
        super().__init__()
        self.notification_service = notification_service

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.notification_service._reposition_toasts()
        return super().eventFilter(obj, event)


class NotificationService(metaclass=Singleton):
    """A singleton service for managing and displaying notifications.

    This service provides a centralized API for showing different types of
    notifications, such as toasts and modals. It manages the lifecycle,
    stacking, and positioning of these notifications relative to the main
    application window.
    """

    def __init__(self):
        """Initializes the NotificationService.
        
        Loads configuration from the ThemeManager and prepares the service.
        """
        config = ThemeManagerInstance().notification_config
        self.SPACING = config.get("spacing", 10)
        self.TOAST_DURATION = config.get("toast_duration", 5000)

        self.main_window: QWidget | None = None
        self.active_toasts = []
        self.resize_filter = WindowResizeFilter(self)

    def set_main_window(self, main_window: QWidget):
        """Sets the main window instance for positioning notifications.

        Args:
            main_window (QWidget): The main window of the application.
        """
        if self.main_window:
            self.main_window.removeEventFilter(self.resize_filter)

        # Clear active toasts from the previous window to prevent positioning issues
        for toast in self.active_toasts:
            toast.close()
        self.active_toasts.clear()

        self.main_window = main_window
        self.main_window.installEventFilter(self.resize_filter)

    def show_toast(
            self,
            notification_type: str,
            title: str,
            message: str
    ):
        """Displays a toast notification.

        Creates, shows, and manages a toast notification that appears at the
        bottom-right of the main window. Toasts are stacked if multiple are
        shown and are automatically dismissed after a configured duration.

        Args:
            notification_type (str): The type of notification, which affects
                styling (e.g., 'success', 'info', 'warning', 'error').
            title (str): The title of the notification.
            message (str): The message body of the notification.
        """
        if not self.main_window:
            print("ERROR: Main window not set for NotificationService.")
            return

        toast = ToastNotification(
            title=title,
            message=message,
            notification_type=notification_type,
            parent=self.main_window
        )

        # Ensure the toast is resized to fit its content before calculating position
        toast.adjustSize()

        # Calculate position
        position_y = self.main_window.height() - toast.height() - self.SPACING
        for active_toast in self.active_toasts:
            position_y -= active_toast.height() + self.SPACING

        self.active_toasts.append(toast)
        toast.show_animated(position_y)

        # Schedule closing
        QTimer.singleShot(self.TOAST_DURATION, lambda: self._close_toast(toast))

    def _close_toast(self, toast_to_close: ToastNotification):
        """Closes a specific toast and triggers repositioning of others.

        Args:
            toast_to_close (ToastNotification): The toast widget to close.
        """
        if toast_to_close in self.active_toasts:
            toast_to_close.close_animated()
            self.active_toasts.remove(toast_to_close)
            self._reposition_toasts()

    def _reposition_toasts(self):
        """Repositions all active toasts, typically after one is closed.
        
        This method recalculates the vertical position of each active toast
        to create a smooth stacking effect when a toast is removed from the
        stack.
        """
        if not self.main_window:
            return

        position_y = self.main_window.height() - self.SPACING
        for toast in self.active_toasts:
            position_y -= toast.height()
            target_x = self.main_window.width() - toast.width() - self.SPACING
            toast.update_position(target_x, position_y)
            position_y -= self.SPACING

    def show_modal(self):
        """Displays a modal notification (dialog).
        
        (Not yet implemented)
        """
        # TODO: Implement modal dialog logic
        pass