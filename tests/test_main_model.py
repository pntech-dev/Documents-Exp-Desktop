from unittest.mock import patch

from modules.main.mvc.main_model import MainModel


class TestMainModel:
    def _build_model(self):
        with patch("modules.main.mvc.main_model.load_config", return_value={"base_url": "http://localhost"}), \
             patch("modules.main.mvc.main_model.get_app_data_dir"), \
             patch("modules.main.mvc.main_model.get_local_data_dir"):
            return MainModel(mode="auth")

    def test_get_user_data_normalizes_nested_payload(self):
        model = self._build_model()
        model._get_user_token = lambda: "token"
        model.api.get_user_data = lambda token: {"user": {"id": 7, "email": "u@x.test"}}

        data = model.get_user_data()

        assert data == {"id": 7, "email": "u@x.test"}

    def test_get_full_user_data_normalizes_nested_payload(self):
        model = self._build_model()
        model._get_user_token = lambda: "token"
        model.api.get_user_data = lambda token: {"user": {"id": 3, "username": "Test User"}}

        data = model.get_full_user_data()

        assert data == {"id": 3, "username": "Test User"}

    def test_normalize_user_data_keeps_flat_payload(self):
        flat = {"id": 1, "email": "flat@x.test"}
        assert MainModel._normalize_user_data(flat) == flat

