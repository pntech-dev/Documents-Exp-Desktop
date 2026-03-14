import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from app import Application, APP_VERSION

class TestApplication:
    @pytest.fixture
    def mock_dependencies(self):
        """Mocks all external dependencies of the Application class."""
        with patch("app.QApplication"), \
             patch("app.AuthWindow") as MockAuthWindow, \
             patch("app.MainWindow") as MockMainWindow, \
             patch("app.AuthModel") as MockAuthModel, \
             patch("app.WhatsNewDialog") as MockWhatsNewDialog, \
             patch("app.ThemeManagerInstance"), \
             patch("app.NotificationService"), \
             patch("app.UpdateManager") as MockUpdateManager, \
             patch("app.APIWorker") as MockAPIWorker, \
             patch("app.load_config", return_value={}), \
             patch("app.get_local_data_dir") as mock_get_dir, \
             patch("app.logging"), \
             patch("app.RotatingFileHandler"), \
             patch("app.sys") as mock_sys:
            
            # Mock system calls
            mock_sys.argv = []
            mock_sys.platform = "linux" # Avoid win32 specific calls
            mock_get_dir.return_value = MagicMock()
            
            # Setup AuthModel mock
            auth_model = MockAuthModel.return_value
            auth_model.get_auto_login_state.return_value = False 
            
            yield {
                "AuthWindow": MockAuthWindow,
                "MainWindow": MockMainWindow,
                "AuthModel": auth_model,
                "APIWorker": MockAPIWorker,
                "UpdateManager": MockUpdateManager,
                "WhatsNewDialog": MockWhatsNewDialog,
            }

    def test_init_no_auto_login(self, mock_dependencies):
        """Test initialization when auto-login is disabled."""
        app = Application()
        
        # Should show auth window
        mock_dependencies["AuthWindow"].return_value.show.assert_called_once()
        # Should not attempt auto login (no worker started)
        mock_dependencies["APIWorker"].assert_not_called()

    def test_init_with_auto_login(self, mock_dependencies):
        """Test initialization with auto-login enabled."""
        mock_dependencies["AuthModel"].get_auto_login_state.return_value = True
        
        app = Application()
        
        # Should start verification worker
        mock_dependencies["APIWorker"].assert_called()
        worker = mock_dependencies["APIWorker"].return_value
        worker.start.assert_called_once()

    def test_check_for_updates(self, mock_dependencies):
        """Test that update check is triggered if config has repo."""
        with patch("app.load_config", return_value={"github_repo": "user/repo"}):
            app = Application()
            
            mock_dependencies["UpdateManager"].assert_called_with(APP_VERSION, "user/repo")
            mock_dependencies["UpdateManager"].return_value.check_for_updates.assert_called_with(silent=True)

    def test_token_verified(self, mock_dependencies):
        """Test successful token verification flow."""
        app = Application()
        app.auth_window = Mock() # Simulate open auth window
        auth_window_mock = app.auth_window
        
        app.on_token_verified({})
        
        # Should create and show main window
        mock_dependencies["MainWindow"].assert_called_with(
            mode="auth",
            settings_manager=app.settings_manager
        )
        mock_dependencies["MainWindow"].return_value.showMaximized.assert_called_once()
        # Should close auth window
        auth_window_mock.close.assert_called_once()

    def test_token_verification_failed_connection_error(self, mock_dependencies):
        """Test handling of connection error during verification."""
        app = Application()
        error = requests.exceptions.ConnectionError()
        
        with patch("app.NotificationService") as MockNotify:
            app.on_token_verification_failed(error)
            
            # Should show auth window
            mock_dependencies["AuthWindow"].return_value.show.assert_called()
            # Should show error toast
            MockNotify.return_value.show_toast.assert_called_with(
                notification_type="error",
                title="Ошибка подключения",
                message="Не удалось подключиться к серверу."
            )

    def test_token_verification_failed_refresh(self, mock_dependencies):
        """Test that verification failure triggers token refresh."""
        app = Application()
        error = Exception("Invalid token")
        
        # Reset mock calls from init
        mock_dependencies["APIWorker"].reset_mock()
        
        app.on_token_verification_failed(error)
        
        # Should start refresh worker
        mock_dependencies["APIWorker"].assert_called_with(app.auth_model.refresh_tokens)
        worker = mock_dependencies["APIWorker"].return_value
        worker.start.assert_called_once()

    def test_token_refresh_failed(self, mock_dependencies):
        """Test that refresh failure triggers logout."""
        app = Application()
        error = Exception("Refresh failed")
        
        with patch("app.NotificationService") as MockNotify:
            app.on_token_refresh_failed(error)
            
            app.auth_model.logout.assert_called_once()
            mock_dependencies["AuthWindow"].return_value.show.assert_called()
            MockNotify.return_value.show_toast.assert_called()

    def test_logout_requested(self, mock_dependencies):
        """Test logout request from MainWindow."""
        app = Application()
        app.main_window = Mock()
        main_window_mock = app.main_window
        
        app.on_logout_requested()
        
        main_window_mock.close.assert_called_once()
        assert app.main_window is None
        app.auth_model.logout.assert_called_once()
        mock_dependencies["AuthWindow"].return_value.show.assert_called()

    def test_show_main_window_displays_whats_new_once_for_authorized_user(self, mock_dependencies):
        app = Application()
        app.settings_manager = Mock()
        app.settings_manager.get_setting.return_value = ""

        app.show_main_window(mode="auth")

        mock_dependencies["WhatsNewDialog"].assert_called_once_with(
            parent=app.main_window,
            version=APP_VERSION
        )
        mock_dependencies["WhatsNewDialog"].return_value.exec_.assert_called_once()
        app.settings_manager.set_setting.assert_called_once_with("last_seen_whats_new_version", APP_VERSION)

    def test_show_main_window_skips_whats_new_if_already_seen(self, mock_dependencies):
        app = Application()
        app.settings_manager = Mock()
        app.settings_manager.get_setting.return_value = APP_VERSION

        app.show_main_window(mode="auth")

        mock_dependencies["WhatsNewDialog"].assert_not_called()
        app.settings_manager.set_setting.assert_not_called()

    def test_show_main_window_skips_whats_new_for_guest(self, mock_dependencies):
        app = Application()
        app.settings_manager = Mock()

        app.show_main_window(mode="guest")

        mock_dependencies["WhatsNewDialog"].assert_not_called()
