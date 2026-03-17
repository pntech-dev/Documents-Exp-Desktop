import json
import logging
from pathlib import Path
from typing import Any, Dict

from utils.app_paths import get_app_data_dir

class SettingsManager:
    """
    Manages user-specific application settings.

    This class handles loading, saving, and managing settings for a specific user.
    Settings are stored in a JSON file in the user's profile directory.
    """
    def __init__(self, user_id: int):
        if not isinstance(user_id, int):
            raise TypeError("user_id must be an integer.")

        self.user_id = user_id
        self.settings_dir = get_app_data_dir() / "Profiles"
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir / f"user_settings_{self.user_id}.json"
        
        self.settings = self.load_settings()
        self.logger = logging.getLogger(f"SettingsManager(user_{self.user_id})")

    def get_default_settings(self) -> Dict[str, Any]:
        """
        Returns the default settings for a user.
        """
        return {
            "theme": 1,  # 0 for light, 1 for dark
            "last_seen_whats_new_version": "",
            "search_filters": {
                "include_pages": True,
                "search_by_name": True,
                "search_by_code": True,
                "exact_match": False,
            }
        }

    @staticmethod
    def _normalize_search_filters(filters: Any, default_filters: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes legacy and current search filter schemas to the current format."""
        normalized = dict(default_filters)
        if not isinstance(filters, dict):
            return normalized

        # Legacy schema migration.
        if "search_in_pages" in filters:
            normalized["include_pages"] = bool(filters.get("search_in_pages", normalized["include_pages"]))

        if "search_field" in filters:
            field = str(filters.get("search_field", "")).strip().lower()
            if field == "name":
                normalized["search_by_name"] = True
                normalized["search_by_code"] = False
            elif field == "code":
                normalized["search_by_name"] = False
                normalized["search_by_code"] = True
            elif field == "both":
                normalized["search_by_name"] = True
                normalized["search_by_code"] = True

        if "match_mode" in filters:
            mode = str(filters.get("match_mode", "")).strip().lower()
            normalized["exact_match"] = mode in {"exact", "equals", "strict"}

        # Current schema overrides.
        for key in ("include_pages", "search_by_name", "search_by_code", "exact_match"):
            if key in filters:
                normalized[key] = bool(filters[key])

        return normalized

    def load_settings(self) -> Dict[str, Any]:
        """
        Loads settings from the user's settings file.

        If the file doesn't exist or is invalid, it returns the default settings.
        """
        default_settings = self.get_default_settings()
        if not self.settings_file.exists():
            return default_settings

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                loaded_settings = json.load(f)
             
            # Merge loaded settings with defaults to ensure all keys are present
            settings = default_settings.copy()
            if isinstance(loaded_settings, dict):
                settings.update(loaded_settings)

            settings["search_filters"] = self._normalize_search_filters(
                settings.get("search_filters"),
                default_settings.get("search_filters", {}),
            )
            return settings

        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to load settings file {self.settings_file}: {e}. Using default settings.")
            return default_settings

    def save_settings(self) -> None:
        """Saves the current settings to the user's settings file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except IOError as e:
            self.logger.error(f"Failed to save settings to {self.settings_file}: {e}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a specific setting by key.

        Args:
            key: The key of the setting to retrieve.
            default: The value to return if the key is not found.

        Returns:
            The value of the setting.
        """
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Sets a specific setting and saves it to the file.

        Args:
            key: The key of the setting to set.
            value: The new value for the setting.
        """
        self.settings[key] = value
        self.save_settings()
