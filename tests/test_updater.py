import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
from core.updater import GitHubUpdateChecker, UpdateDownloader, UpdateManager



class TestGitHubUpdateChecker:
    @pytest.fixture
    def checker(self):
        # Create an instance, but do not start the thread
        checker = GitHubUpdateChecker("1.0.0", "user/repo")
        # Mock signals to verify their calls
        checker.update_available = Mock()
        checker.no_update = Mock()
        checker.error = Mock()
        return checker

    def test_update_available(self, checker):
        """Test: new version found with exe file."""
        mock_response = {
            "tag_name": "v1.1.0",
            "body": "Fixed bugs",
            "assets": [
                {"name": "source.zip", "browser_download_url": "http://zip", "size": 500},
                {"name": "setup.exe", "browser_download_url": "http://test.com/setup.exe", "size": 1024}
            ]
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response
            
            # Run run() synchronously in the current thread for testing
            checker.run()
            
            # Verify that the update_available signal was called with correct data
            checker.update_available.emit.assert_called_once_with(
                "1.1.0", "http://test.com/setup.exe", "Fixed bugs", 1024
            )

    def test_no_update(self, checker):
        """Test: current version is up to date."""
        mock_response = {
            "tag_name": "v1.0.0",
            "assets": []
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response
            
            checker.run()
            
            checker.no_update.emit.assert_called_once()

    def test_update_version_comparison(self, checker):
        """Test: server version is older than current (e.g., rollback)."""
        checker.current_version = "2.0.0"
        mock_response = {
            "tag_name": "v1.5.0",
            "assets": [{"name": "app.exe", "browser_download_url": "url", "size": 1}]
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response
            
            checker.run()
            
            checker.no_update.emit.assert_called_once()

    def test_error_404(self, checker):
        """Test: repository not found."""
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            
            checker.run()
            
            checker.error.emit.assert_called_once()
            assert "не найден" in checker.error.emit.call_args[0][0]

    def test_no_exe_asset(self, checker):
        """Test: new version exists, but no exe file."""
        mock_response = {
            "tag_name": "v2.0.0",
            "assets": [
                {"name": "source.zip", "browser_download_url": "http://zip", "size": 100}
            ]
        }
        
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response
            
            checker.run()
            
            checker.error.emit.assert_called_once()
            assert "отсутствует" in checker.error.emit.call_args[0][0]


class TestUpdateDownloader:
    def test_download_success(self, tmp_path):
        """Test successful file download."""
        url = "http://test.com/file.exe"
        downloader = UpdateDownloader(url, 10)
        downloader.finished = Mock()
        downloader.progress = Mock()
        downloader.error = Mock()
        
        # Mock requests.get
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.headers = {'content-length': '10'}
            # Simulate data stream (2 chunks of 5 bytes)
            mock_response.iter_content.return_value = [b'12345', b'67890']
            mock_response.raise_for_status = Mock()
            # Support context manager (with requests.get...)
            mock_get.return_value.__enter__.return_value = mock_response
            
            # Mock temporary file creation to write to our test folder
            target_file = tmp_path / "update.exe"
            
            with patch("core.updater.tempfile.mkstemp") as mock_mkstemp, \
                 patch("core.updater.os.close") as mock_close:
                
                # mkstemp returns (file_descriptor, path)
                mock_mkstemp.return_value = (123, str(target_file))
                
                downloader.run()
                
                # Verify that the file is written correctly
                assert target_file.read_bytes() == b'1234567890'
                
                # Verify signals
                downloader.finished.emit.assert_called_once_with(str(target_file))
                # Progress should have been called: 0%, 50%, 100%
                assert downloader.progress.emit.call_count >= 2

    def test_download_error(self):
        """Test network error during download."""
        downloader = UpdateDownloader("http://bad.url")
        downloader.error = Mock()
        
        with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Fail")):
            downloader.run()
            
            downloader.error.emit.assert_called_once()
            assert "Fail" in downloader.error.emit.call_args[0][0]

    def test_download_canceled_emits_signal(self, tmp_path):
        """Stopping download should emit canceled and not emit finished."""
        url = "http://test.com/file.exe"
        downloader = UpdateDownloader(url, 10)
        downloader.finished = Mock()
        downloader.progress = Mock()
        downloader.error = Mock()
        downloader.canceled = Mock()

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.headers = {"content-length": "10"}

            def chunks():
                yield b"12345"
                downloader.stop()
                yield b"67890"

            mock_response.iter_content.return_value = chunks()
            mock_response.raise_for_status = Mock()
            mock_get.return_value.__enter__.return_value = mock_response

            target_file = tmp_path / "update.exe"
            with patch("core.updater.tempfile.mkstemp", return_value=(123, str(target_file))), \
                 patch("core.updater.os.close"):
                downloader.run()

        downloader.canceled.emit.assert_called_once()
        downloader.finished.emit.assert_not_called()


class TestUpdateManager:
    def test_on_download_canceled_cleans_state(self):
        manager = UpdateManager(current_version="0.2.0", repo_name="owner/repo")
        manager.progress_dialog = Mock()
        manager._downloader = Mock()

        with patch("core.updater.NotificationService") as mock_notification_service:
            service_instance = mock_notification_service.return_value
            service_instance.main_window = Mock()

            manager._on_download_canceled()

        manager.progress_dialog.close.assert_called_once()
        assert manager._downloader is None
        service_instance.show_toast.assert_called_once()
