import pytest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QWidget
from utils.notifications.notification_service import NotificationService

class TestNotificationService:
    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Resets the singleton state before each test."""
        NotificationService._instances = {}
        yield
        NotificationService._instances = {}

    @patch("utils.notifications.notification_service.ThemeManagerInstance")
    def test_initialization(self, mock_tm):
        """Test service initialization and config loading."""
        # Setup config mock
        mock_tm.notification_config = {"spacing": 15, "toast_duration": 3000}
        
        service = NotificationService()
        
        assert service.SPACING == 15
        assert service.TOAST_DURATION == 3000
        assert service.active_toasts == []

    @patch("utils.notifications.notification_service.ThemeManagerInstance")
    @patch("utils.notifications.notification_service.ToastNotification")
    def test_show_toast(self, mock_toast_class, mock_tm):
        """Test showing a notification."""
        service = NotificationService()
        
        # Mock main window
        mock_window = Mock(spec=QWidget)
        mock_window.height.return_value = 1000
        mock_window.width.return_value = 1000
        service.set_main_window(mock_window)
        
        # Mock created toast
        mock_toast_instance = Mock()
        mock_toast_instance.height.return_value = 100
        mock_toast_instance.width.return_value = 300
        mock_toast_class.return_value = mock_toast_instance
        
        # Call method
        service.show_toast("success", "Title", "Message")
        
        # Verify that ToastNotification was created with correct parameters
        mock_toast_class.assert_called_once_with(
            title="Title",
            message="Message",
            notification_type="success",
            parent=mock_window
        )
        
        # Verify that toast is added to list and shown
        assert mock_toast_instance in service.active_toasts
        mock_toast_instance.show_animated.assert_called_once()

    def test_singleton_behavior(self):
        """Test Singleton pattern."""
        with patch("utils.notifications.notification_service.ThemeManagerInstance"):
            s1 = NotificationService()
            s2 = NotificationService()
            assert s1 is s2