from unittest.mock import MagicMock, patch

from utils.settings_manager import SettingsManager


class TestSettingsManager:
    def test_default_settings_include_whats_new_version(self):
        with patch("utils.settings_manager.get_app_data_dir") as mock_app_dir:
            mock_app_dir.return_value = MagicMock()

            manager = SettingsManager(user_id=1)

            assert manager.get_default_settings()["last_seen_whats_new_version"] == ""
