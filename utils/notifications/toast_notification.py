from PyQt5.QtWidgets import QFrame, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QRect, Qt, QSize, QEvent

from ui.ui_converted.toast_notification import Ui_ToastNotification
from utils.theme_manager import theme_manager_singleton


class ToastNotification(QFrame, Ui_ToastNotification):
    """A toast notification widget that loads its UI from a .ui file.
    
    This class represents a self-contained toast notification that appears
    with an animation, displays information, and can be closed with an
    animation. It is designed to be managed by the NotificationService.
    The UI is defined in 'toast_notification.ui' and loaded via the
    'Ui_ToastNotification' class.
    """

    def __init__(
            self,
            title: str,
            message: str,
            notification_type: str = "success",
            parent=None
    ):
        """Initializes the toast widget.

        Args:
            title (str): The title of the notification.
            message (str): The message to display.
            notification_type (str): The type of notification (e.g., 'success',
                'info', 'warning', 'error'). This is used for styling.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        # --- Setup UI from .ui file ---
        self.setupUi(self)

        self.notification_container.setAttribute(Qt.WA_StyledBackground, True)

        self.horizontalLayout.removeWidget(self.notify_type_line_frame)
        self.horizontalLayout_2.insertWidget(0, self.notify_type_line_frame)
        
        self.setObjectName("Notification")
        self.setProperty("notificationType", notification_type)

        self.label.setText(title)
        self.description.setText(message)

        # Programmatically set the icon to avoid SVG scaling issues with stylesheets
        theme_name = theme_manager_singleton.themes.get(theme_manager_singleton.current_theme_id, 'light')
        icon_path = f":/icons/{theme_name}/{theme_name}/notification_{notification_type}.svg"
        
        icon = QIcon(icon_path)
        pixmap = icon.pixmap(32, 32)
        
        self.icon_label.clear()
        self.icon_label.setPixmap(pixmap)
        self.icon_label.setFixedSize(32, 32)

        self.close_pushButton.setIconSize(QSize(16, 16))
        self.close_pushButton.clicked.connect(self.close_animated)

        # Loading icons for the close button states
        self._close_icons = {
            "default": QIcon(f":/icons/{theme_name}/{theme_name}/close_default.svg"),
            "hover": QIcon(f":/icons/{theme_name}/{theme_name}/close_hover.svg"),
            "pressed": QIcon(f":/icons/{theme_name}/{theme_name}/close_clicked.svg"),
        }
        self.close_pushButton.setIcon(self._close_icons["default"])
        self.close_pushButton.installEventFilter(self)

        self._set_shadow()
        self.animation = QPropertyAnimation(self, b"geometry")

    def eventFilter(self, watched, event):
        if watched == self.close_pushButton:
            if event.type() == QEvent.Enter:
                self.close_pushButton.setIcon(self._close_icons["hover"])
            elif event.type() == QEvent.Leave:
                self.close_pushButton.setIcon(self._close_icons["default"])
            elif event.type() == QEvent.MouseButtonPress:
                self.close_pushButton.setIcon(self._close_icons["pressed"])
            elif event.type() == QEvent.MouseButtonRelease:
                icon = self._close_icons["hover"] if self.close_pushButton.underMouse() else self._close_icons["default"]
                self.close_pushButton.setIcon(icon)
        return super().eventFilter(watched, event)

    def _set_shadow(self):
        """Sets the shadow effect for the widget."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

    def show_animated(self, position_y: int):
        """Shows the widget with a slide-in animation.

        Args:
            position_y (int): The target vertical position for the widget.
        """
        parent_width = self.parent().width()
        self.adjustSize() 
        
        start_pos = QRect(parent_width, position_y, self.width(), self.height())
        end_pos = QRect(parent_width - self.width() - 10, position_y, self.width(), self.height())

        self.setGeometry(start_pos)
        self.show()

        self.animation.setDuration(300)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

    def update_position(self, target_x, target_y):
        """Updates the position of the notification, adjusting animation if needed."""
        if self.animation.state() == QPropertyAnimation.Running:
            old_end = self.animation.endValue()
            # Calculate deltas
            dx = target_x - old_end.x()
            dy = target_y - old_end.y()
            
            # Update start value
            start_val = self.animation.startValue()
            start_val.translate(dx, dy)
            self.animation.setStartValue(start_val)
            
            # Update end value
            end_val = self.animation.endValue()
            end_val.translate(dx, dy)
            self.animation.setEndValue(end_val)
        else:
            self.move(target_x, target_y)

    def close_animated(self):
        """Closes the widget with a slide-out animation."""
        start_pos = self.geometry()
        end_pos = QRect(self.parent().width(), self.y(), self.width(), self.height())
        
        self.animation.setDuration(300)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setEasingCurve(QEasingCurve.InCubic)
        self.animation.finished.connect(self.close)
        self.animation.start()
