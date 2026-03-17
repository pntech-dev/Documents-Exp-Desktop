import json

from unittest.mock import MagicMock, patch

from utils.settings_manager import SettingsManager


class TestSettingsManager:
    def test_default_settings_include_whats_new_version(self):
        with patch("utils.settings_manager.get_app_data_dir") as mock_app_dir:
            mock_app_dir.return_value = MagicMock()

            manager = SettingsManager(user_id=1)

            assert manager.get_default_settings()["last_seen_whats_new_version"] == ""

    def test_default_search_filters_schema(self):
        with patch("utils.settings_manager.get_app_data_dir") as mock_app_dir:
            mock_app_dir.return_value = MagicMock()
            manager = SettingsManager(user_id=1)

            assert manager.get_default_settings()["search_filters"] == {
                "include_pages": True,
                "search_by_name": True,
                "search_by_code": True,
                "exact_match": False,
            }

    def test_load_settings_migrates_legacy_search_filters(self, tmp_path):
        settings_file = tmp_path / "Profiles" / "user_settings_1.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(
            json.dumps(
                {
                    "search_filters": {
                        "search_in_pages": False,
                        "search_field": "code",
                        "match_mode": "exact",
                    }
                }
            ),
            encoding="utf-8",
        )

        with patch("utils.settings_manager.get_app_data_dir", return_value=tmp_path):
            manager = SettingsManager(user_id=1)
            assert manager.get_setting("search_filters") == {
                "include_pages": False,
                "search_by_name": False,
                "search_by_code": True,
                "exact_match": True,
            }

    def test_load_settings_keeps_current_schema(self, tmp_path):
        settings_file = tmp_path / "Profiles" / "user_settings_1.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        settings_file.write_text(
            json.dumps(
                {
                    "search_filters": {
                        "include_pages": False,
                        "search_by_name": True,
                        "search_by_code": False,
                        "exact_match": True,
                    }
                }
            ),
            encoding="utf-8",
        )

        with patch("utils.settings_manager.get_app_data_dir", return_value=tmp_path):
            manager = SettingsManager(user_id=1)
            assert manager.get_setting("search_filters") == {
                "include_pages": False,
                "search_by_name": True,
                "search_by_code": False,
                "exact_match": True,
            }
