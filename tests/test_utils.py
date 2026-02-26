import json
import pytest
import requests
from pathlib import Path
from unittest.mock import Mock, patch

from utils.fields_validators import FieldValidator
from utils.file_utils import read_json, load_config
from utils.error_messages import get_friendly_error_message
from utils.app_paths import get_app_root, get_app_data_dir, get_local_data_dir



class TestAppPaths:
    APP_NAME = "Documents Exp"

    def test_get_app_root_source(self):
        """Test get_app_root when running from source."""
        root = get_app_root()
        assert isinstance(root, Path)
        assert root.exists()
        assert (root / "utils").exists()


    def test_get_app_root_frozen_meipass(self):
        """Test get_app_root when running as compiled exe (onedir mode)."""
        fake_executable = "/tmp/fake_app/Documents Exp.exe"
        with patch("utils.app_paths.sys") as mock_sys:
            mock_sys.frozen = True
            mock_sys.executable = fake_executable
            assert get_app_root() == Path(fake_executable).parent


    def test_get_app_root_frozen_onedir(self):
        """Test get_app_root when running as PyInstaller onedir."""
        fake_exe = "/opt/app/main_exe"
        with patch("utils.app_paths.sys") as mock_sys:
            mock_sys.mock_add_spec(["frozen", "executable"])
            mock_sys.frozen = True
            mock_sys.executable = fake_exe
            assert get_app_root() == Path("/opt/app")

    @pytest.mark.parametrize(
        "platform, expected_parts", [
            ("win32", ["AppData", "Roaming"]),
            ("darwin", ["Library", "Application Support"]),
            ("linux", [".local", "share"]),
        ]
    )
    def test_get_app_data_dir(self, platform, expected_parts):
        with patch("utils.app_paths.sys") as mock_sys, \
             patch("pathlib.Path.home", return_value=Path("/home/testuser")):
            
            mock_sys.platform = platform
            expected = Path("/home/testuser").joinpath(*expected_parts, self.APP_NAME)
            assert get_app_data_dir() == expected

    @pytest.mark.parametrize(
        "platform, expected_parts", [
            ("win32", ["AppData", "Local"]),
            ("darwin", ["Library", "Caches"]),
            ("linux", [".cache"]),
        ]
    )
    def test_get_local_data_dir(self, platform, expected_parts):
        with patch("utils.app_paths.sys") as mock_sys, \
             patch("pathlib.Path.home", return_value=Path("/home/testuser")):
            
            mock_sys.platform = platform
            expected = Path("/home/testuser").joinpath(*expected_parts, self.APP_NAME)
            assert get_local_data_dir() == expected



class TestRequestExceptions:
    @pytest.mark.parametrize(
            "exception, expected", [
                (requests.exceptions.ConnectionError(), "Не удалось подключиться к серверу. Проверьте соединение или попробуйте позже."),
            ]
    )
    def test_connection_errors(self, exception, expected):
        assert get_friendly_error_message(exception=exception) == expected


    @pytest.mark.parametrize(
            "exception, expected", [
                (requests.exceptions.Timeout(), "Превышено время ожидания ответа от сервера."),
            ]
    )
    def test_timeout_errors(self, exception, expected):
        assert get_friendly_error_message(exception=exception) == expected

    
    @pytest.mark.parametrize(
        "status_code, json_data, expected_part", [
            (400, None, "Некорректный запрос."),
            (401, None, "Ошибка авторизации"),
            (403, {"detail": "Forbidden access"}, "Доступ запрещен: Forbidden access"),
            (404, {"detail": "Not found"}, "Не найдено: Not found"),
            (409, {"detail": "Conflict"}, "Конфликт: Conflict"),
            (409, None, "Конфликт данных"),
            (422, {"detail": "Invalid data"}, "Ошибка валидации: Invalid data"),
            (422, None, "Ошибка проверки данных."),
            (429, None, "Слишком много попыток"),
            (500, None, "Внутренняя ошибка сервера"),
        ]
    )
    def test_http_errors(self, status_code, json_data, expected_part):
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = status_code
        mock_response.json.return_value = json_data if json_data else {}
        
        exception = requests.exceptions.HTTPError(response=mock_response)
        assert expected_part in get_friendly_error_message(exception)



class TestValidators:
    @pytest.mark.parametrize(
            "email_input, expected", [
                ("mail@gmail.com", True),
                ("mailgmail.com", False),
                ("mail@@gmail.com", False),
                ("mail@", False),
                ("@gmail.com", False),
                ("mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail-mail@gmail.com", False),
                (".mail@gmail.com", False),
                ("mail.@gmail.com", False),
                ("ma..il@gmail.com", False),
                ("mail@gmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmailgmail.com", False),
                ("mail@gmailcom", False),
                ("mail@gmail.", False),
                ("mail@.gmail.com", False),
                ("mail@gmail..com", False),
            ]
    )
    def test_email_validator(self, email_input, expected):
        assert FieldValidator.validate_email(email_input) == expected


    @pytest.mark.parametrize(
            "password_input, expected", [
                ("1234567", False),
                ("qwertyui", False),
                ("1qwertyu", False),
                ("1QWERTYU", False),
                ("1Qwertyu", False),
                ("-1Qwerty", True),
            ]
    )
    def test_password_validator(self, password_input, expected):
        assert FieldValidator.validate_password(password_input) == expected

    @pytest.mark.parametrize(
        "password_input, expected_validity", [
            ("-1Qwerty", [True, True, True, True, True]),  # Correct password
            ("1Qwerty", [False, False, True, True, True]), # Too short (7), have not special characters
            ("password", [True, False, False, False, True]), # Have not special characters, digits, upper case letter
            ("PASSWORD", [True, False, False, True, False]), # Have not special characters, digits, lower case letter
            ("12345678", [True, False, True, False, False]), # Have not special characters, letters
            ("!@#$%", [False, True, False, False, False]),   # Too short, only special characters
            ("", [False, False, False, False, False]),       # Empty
        ]
    )
    def test_get_password_validation_status(self, password_input, expected_validity):
        status = FieldValidator.get_password_validation_status(password_input)
        validity = [item["valid"] for item in status]
        assert validity == expected_validity



class TestFileUtils:
    def test_load_config_success(self, tmp_path):
        """Test successful loading of config.yaml."""
        config_content = "base_url: http://test.com"
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content, encoding="utf-8")
        
        with patch("utils.file_utils.get_app_root", return_value=tmp_path):
            config = load_config()
            assert config == {"base_url": "http://test.com"}


    def test_load_config_not_found(self, tmp_path):
        """Test load_config when file does not exist."""
        with patch("utils.file_utils.get_app_root", return_value=tmp_path):
            config = load_config()
            assert config == {}


    def test_load_config_yaml_error(self, tmp_path):
        """Test load_config with invalid YAML content."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: [", encoding="utf-8")
        
        with patch("utils.file_utils.get_app_root", return_value=tmp_path):
            config = load_config()
            assert config == {}


    def test_read_json_success(self, tmp_path):
        """Test successful reading of a JSON file."""
        data = {"key": "value", "number": 123}
        json_file = tmp_path / "test.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")
        
        assert read_json(json_file) == data


    def test_read_json_not_found(self, tmp_path):
        """Test read_json when file does not exist."""
        assert read_json(tmp_path / "non_existent.json") is None


    def test_read_json_decode_error(self, tmp_path):
        """Test read_json with invalid JSON content."""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{invalid json", encoding="utf-8")
        
        assert read_json(json_file) is None
