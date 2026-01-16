from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame


class ToastNotification(QFrame):
    """A toast notification widget.
    
    This class represents a self-contained toast notification that appears
    with an animation, displays information, and can be closed with an
    animation. It is designed to be managed by the NotificationService.
    It inherits from QFrame to allow for a styled container with a border-radius.
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
        self.setObjectName("Notification")
        self.setProperty("notificationType", notification_type)

        # --- UI Elements ---
        self.line_frame = QFrame()
        self.line_frame.setObjectName("notify_type_line_frame")

        self.icon_label = QLabel()
        self.icon_label.setObjectName("icon_label")

        self.title_label = QLabel(title)
        self.title_label.setObjectName("label")  # Matches QSS

        self.message_label = QLabel(message)
        self.message_label.setObjectName("description")  # Matches QSS

        self._set_shadow()

        # --- Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 20, 0)  # Margin for shadow
        main_layout.setSpacing(0)

        container_widget = QWidget()  # A container for the content
        container_widget.setObjectName("notification_container")
        container_layout = QHBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 20, 20)
        container_layout.setSpacing(15)

        main_layout.addWidget(container_widget)

        container_layout.addWidget(self.line_frame)
        container_layout.addWidget(self.icon_label, 0, Qt.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.message_label)
        
        container_layout.addLayout(text_layout)

        self.animation = QPropertyAnimation(self, b"geometry")

        # The icon path depends on the theme. This needs to be connected to the ThemeManager.
        # For now, we assume a dark theme as per the j2 file.
        # This logic should be moved or handled by the theme manager.
        icon_path = f":/icons/dark/notification/dark/{notification_type}.svg"
        pixmap = QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(pixmap)

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
        self.adjustSize()  # Ensure widget has the correct size hint
        
        start_pos = QRect(parent_width, position_y, self.width(), self.height())
        end_pos = QRect(parent_width - self.width(), position_y, self.width(), self.height())

        self.setGeometry(start_pos)
        self.show()

        self.animation.setDuration(300)
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()

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
