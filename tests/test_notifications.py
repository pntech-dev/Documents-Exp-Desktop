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
        mock_toast_instance.destroyed = Mock()
        mock_toast_instance.destroyed.connect = Mock()
        mock_toast_class.return_value = mock_toast_instance
        
        # Call method
        with patch("utils.notifications.notification_service.time.monotonic", return_value=100.0):
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
        mock_toast_instance.destroyed.connect.assert_called_once()
        mock_toast_instance.show_animated.assert_called_once()

    @patch("utils.notifications.notification_service.ThemeManagerInstance")
    @patch("utils.notifications.notification_service.ToastNotification")
    def test_show_toast_deduplicates_burst_identical_messages(self, mock_toast_class, mock_tm):
        service = NotificationService()
        mock_window = Mock(spec=QWidget)
        mock_window.height.return_value = 600
        mock_window.width.return_value = 800
        service.set_main_window(mock_window)

        toast_instance = Mock()
        toast_instance.height.return_value = 80
        toast_instance.width.return_value = 220
        toast_instance.destroyed = Mock()
        toast_instance.destroyed.connect = Mock()
        mock_toast_class.return_value = toast_instance

        with patch("utils.notifications.notification_service.time.monotonic", side_effect=[100.0, 100.2]):
            service.show_toast("info", "Sync", "Done")
            service.show_toast("info", "Sync", "Done")

        mock_toast_class.assert_called_once()

    @patch("utils.notifications.notification_service.ThemeManagerInstance")
    def test_destroyed_toast_is_removed_from_stack(self, mock_tm):
        service = NotificationService()
        service.main_window = Mock(spec=QWidget)

        toast = Mock()
        service.active_toasts = [toast]

        with patch.object(service, "_reposition_toasts") as mock_reposition:
            service._on_toast_destroyed(toast)

        assert toast not in service.active_toasts
        mock_reposition.assert_called_once()

    def test_singleton_behavior(self):
        """Test Singleton pattern."""
        with patch("utils.notifications.notification_service.ThemeManagerInstance"):
            s1 = NotificationService()
            s2 = NotificationService()
            assert s1 is s2

    @patch("utils.notifications.notification_service.ThemeManagerInstance")
    def test_set_main_window_accepts_none_without_crash(self, mock_tm):
        service = NotificationService()
        old_window = Mock(spec=QWidget)
        old_toast = Mock()
        service.main_window = old_window
        service.active_toasts = [old_toast]

        service.set_main_window(None)

        old_window.removeEventFilter.assert_called_once()
        old_toast.close.assert_called_once()
        assert service.main_window is None
        assert service.active_toasts == []
